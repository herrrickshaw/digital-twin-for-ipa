import datetime
import json
import sqlite3
import ssl
import sys
import time
import urllib.error

import pytest

from conftest import load_script

TODAY = datetime.date.today().isoformat()


@pytest.fixture
def csn(fake_repo, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    mod = load_script("collect_state_news", fake_repo)
    mod._TRANSLATE_FAILS = 0
    return mod


def feed(csn, monkeypatch, mapping, default=""):
    """Serve _get from {url-substring: body}; record calls."""
    calls = []

    def get(url, timeout=45, opener=None, data=None, headers=None):
        calls.append({"url": url, "data": data, "headers": headers, "opener": opener})
        for k, v in mapping.items():
            if k in url:
                if isinstance(v, Exception):
                    raise v
                return v
        return default

    monkeypatch.setattr(csn, "_get", get)
    return calls


# ------------------------------------------------------------------ _get
class _Resp:
    def __init__(self, b):
        self.b = b

    def read(self):
        return self.b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_get_decodes_and_sends_headers(csn, monkeypatch):
    seen = {}

    def urlopen(req, timeout, context=None):
        seen.update(h=dict(req.header_items()), t=timeout, data=req.data)
        return _Resp(b"ab\xffc")

    monkeypatch.setattr(csn.urllib.request, "urlopen", urlopen)
    assert csn._get("http://x/y", timeout=3, data=b"d", headers={"X-A": "1"}) == "ab�c"
    assert seen["h"]["User-agent"] == csn.UA and seen["h"]["X-a"] == "1"
    assert seen["t"] == 3 and seen["data"] == b"d"


def test_get_uses_opener_when_given(csn):
    class Op:
        def open(self, req, timeout):
            return _Resp(b"via-opener")

    assert csn._get("http://x", opener=Op()) == "via-opener"


def test_get_retries_unverified_on_cert_error(csn, monkeypatch, capsys):
    calls = []
    cert = urllib.error.URLError(ssl.SSLCertVerificationError("bad"))

    def urlopen(req, timeout, context=None):
        calls.append(context)
        if context is None:
            raise cert
        return _Resp(b"ok")

    monkeypatch.setattr(csn.urllib.request, "urlopen", urlopen)
    assert csn._get("https://h.example/p") == "ok"
    assert calls[0] is None and calls[1] is not None
    assert "broken cert chain" in capsys.readouterr().err


def test_get_cert_error_with_opener_reraises(csn):
    class Op:
        def open(self, req, timeout):
            raise urllib.error.URLError(ssl.SSLCertVerificationError("bad"))

    with pytest.raises(urllib.error.URLError):
        csn._get("https://h/p", opener=Op())


@pytest.mark.xfail(strict=True, raises=ModuleNotFoundError,
                   reason="collect_state_news.py:126-127 `except ImportError: raise` re-raises the ImportError, "
                          "masking the original URLError the caller should see when scrapling is not installed")
def test_get_other_urlerror_without_scrapling_reraises(csn, monkeypatch):
    def urlopen(req, timeout, context=None):
        raise urllib.error.URLError("handshake")

    monkeypatch.setattr(csn.urllib.request, "urlopen", urlopen)
    monkeypatch.setitem(sys.modules, "scrapling", None)
    monkeypatch.setitem(sys.modules, "scrapling.fetchers", None)
    with pytest.raises(urllib.error.URLError):
        csn._get("https://h/p")


def test_get_falls_back_to_scrapling(csn, monkeypatch, capsys):
    def urlopen(req, timeout, context=None):
        raise urllib.error.URLError("handshake")

    class F:
        @staticmethod
        def get(url, timeout, headers):
            class R:
                body = b"scrap\xff"
            return R()

    import types
    fetchers = types.ModuleType("scrapling.fetchers")
    fetchers.Fetcher = F
    pkg = types.ModuleType("scrapling")
    monkeypatch.setitem(sys.modules, "scrapling", pkg)
    monkeypatch.setitem(sys.modules, "scrapling.fetchers", fetchers)
    monkeypatch.setattr(csn.urllib.request, "urlopen", urlopen)
    assert csn._get("https://h/p") == "scrap�"
    assert "retrying via scrapling: h" in capsys.readouterr().err


def test_get_post_or_opener_never_uses_scrapling(csn, monkeypatch):
    def urlopen(req, timeout, context=None):
        raise urllib.error.URLError("handshake")

    monkeypatch.setattr(csn.urllib.request, "urlopen", urlopen)
    with pytest.raises(urllib.error.URLError):
        csn._get("https://h/p", data=b"x")


def test_get_json(csn, monkeypatch):
    monkeypatch.setattr(csn, "_get", lambda url, **kw: '{"a": [1]}')
    assert csn._get_json("u") == {"a": [1]}


# ------------------------------------------------------------------ translation
def test_translate_en_joins_segments_and_truncates_query(csn, monkeypatch):
    seen = {}

    def gj(url, timeout):
        seen["url"] = url
        return [[["Hello ", "x"], None, ["", "skip"], ["world", "y"]]]

    monkeypatch.setattr(csn, "_get_json", gj)
    assert csn.translate_en("नमस्ते" * 400) == "Hello world"
    import urllib.parse as up
    q = up.parse_qs(up.urlparse(seen["url"]).query)["q"][0]
    assert len(q) == 900


def test_translate_en_empty_inputs_and_empty_result(csn, monkeypatch):
    assert csn.translate_en("") is None and csn.translate_en(None) is None
    monkeypatch.setattr(csn, "_get_json", lambda url, timeout: [[["", "x"]]])
    assert csn.translate_en("abc") is None
    assert csn._TRANSLATE_FAILS == 0


def test_translate_breaker_trips_after_five_failures(csn, monkeypatch):
    n = []

    def boom(url, timeout):
        n.append(1)
        raise OSError

    monkeypatch.setattr(csn, "_get_json", boom)
    for _ in range(8):
        assert csn.translate_en("x") is None
    assert len(n) == 5 and csn._TRANSLATE_FAILS == 5


@pytest.mark.parametrize("s,ok", [("plain", True), ("", True), (None, True),
                                  ("café", True), ("ԯ", True), ("԰", False),
                                  ("नम", False)])
def test_is_english(csn, s, ok):
    assert csn._is_english(s) is ok


def test_decode_mp_newsid(csn):
    enc = "".join(chr(ord(c) + 0x80) for c in "20260731N409")
    assert csn._decode_mp_newsid(enc) == "20260731N409"
    assert csn._decode_mp_newsid("plain") == "plain"
    assert csn._decode_mp_newsid(None) == ""


def test_decode_mp_newsid_exact_boundary(csn):
    assert csn._decode_mp_newsid(chr(0x80)) == "\x00"
    assert csn._decode_mp_newsid(chr(0x7f)) == chr(0x7f)


# ------------------------------------------------------------------ MP
def test_fetch_mp_dedup_across_fonts(csn, monkeypatch):
    enc = lambda s: "".join(chr(ord(c) + 0x80) for c in s)
    en = [{"newsid": enc("20260801N409"), "NewsTitle": " Title  one ", "Description": " cat ", "KeyWords": " kw "},
          {"newsid": enc("20260801N410"), "NewsTitle": "", "Description": "x"},
          {"newsid": "", "NewsTitle": "no id"}]
    hi = [{"newsid": enc("20260801N409"), "NewsTitle": "same id hindi"},
          {"newsid": enc("20260801N411"), "NewsTitle": "Other", "KeyWords": None}]
    urls = []

    def gj(url, **kw):
        urls.append(url)
        return en if "fontenglish" in url else hi

    monkeypatch.setattr(csn, "_get_json", gj)
    rows = csn.fetch_mp(datetime.date(2026, 8, 1))
    assert [r["newsid"] for r in rows] == ["20260801N409", "20260801N411"]
    assert rows[0] == {"newsid": "20260801N409", "date": "2026-08-01", "title": "Title one",
                       "category": "cat", "keywords": "kw",
                       "url": rows[0]["url"]}
    assert rows[0]["url"].startswith("https://www.mpinfo.org/Home/TodaysNews#%20kw%20-")
    assert rows[1]["url"].startswith("https://www.mpinfo.org/Home/TodaysNews#Other-")
    assert "publishdate=08%2F01%2F2026" in urls[0] and len(urls) == 2


# ------------------------------------------------------------------ UP
UP_PAGE = ("<table><tr><td>1</td><td> <b>CM</b> meets  investors </td><td>05/Aug/2026 ...</td>"
           "<td><a href='/pdfs/a1.pdf'>x</a></td></tr>"
           "<tr><td>2</td><td>Bad month</td><td>05/Xyz/2026</td><td><a href='/pdfs/a2.pdf'>x</a></td></tr>"
           "<tr><td>3</td><td>  <i></i> </td><td>06/Aug/2026</td><td><a href='/pdfs/a3.pdf'>x</a></td></tr>"
           "<tr><td>4</td><td>Dept item</td><td>7/sep/2026</td><td><a href='/pdfs/a4'>x</a></td></tr></table>")


def test_fetch_up(csn, monkeypatch, capsys):
    calls = feed(csn, monkeypatch, {"cm_press": UP_PAGE, "other_press": OSError("x")})
    rows = csn.fetch_up()
    assert rows == [{"newsid": "a1.pdf", "date": "2026-08-05", "title": "CM meets investors",
                     "category": "CM press", "keywords": "",
                     "url": "https://information.up.gov.in/pdfs/a1.pdf"},
                    {"newsid": "a4", "date": "2026-09-07", "title": "Dept item",
                     "category": "CM press", "keywords": "",
                     "url": "https://information.up.gov.in/pdfs/a4"}]
    assert "other_press_release_details.aspx: FETCH FAILED" in capsys.readouterr().err
    assert len(calls) == 2


# ------------------------------------------------------------------ GJ
def test_fetch_gujarat(csn, monkeypatch):
    page = '<input name="AntiforgeryFieldname" type="hidden" value="TOK"/>'
    eng = [{"pressId": 1, "pressTitle": " Eng  title ", "pressReleaseDate": "2026-08-01T10:00",
            "depName": " Dept  A ", "metaTitle": " " + "m" * 300},
           {"pressId": None, "pressTitle": "no id"},
           {"pressId": 3, "pressTitle": "   "}]
    guj = [{"pressId": 1, "pressTitle": "Gujarati dup"},
           {"pressId": 2, "pressTitle": "Guj only", "createdDate": "2026-07-30T00:00"}]
    calls = []

    def get(url, timeout=45, opener=None, data=None, headers=None):
        calls.append((url, data))
        if url.endswith("Department-Releases"):
            return page
        return json.dumps(eng if b"PressLangId=1" in data else guj)

    monkeypatch.setattr(csn, "_get", get)
    rows = csn.fetch_gujarat()
    assert [r["newsid"] for r in rows] == ["1", "2"]
    assert rows[0]["title"] == "Eng title" and rows[0]["date"] == "2026-08-01"
    assert rows[0]["category"] == "Dept A" and len(rows[0]["keywords"]) == 200
    assert rows[1]["date"] == "2026-07-30" and rows[1]["category"] == ""
    assert rows[1]["url"].endswith("#press-2")
    assert b"AntiforgeryFieldname=TOK" in calls[1][1]


def test_fetch_gujarat_missing_token(csn, monkeypatch):
    feed(csn, monkeypatch, {"Department-Releases": "<html>"})
    with pytest.raises(RuntimeError, match="antiforgery"):
        csn.fetch_gujarat()


# ------------------------------------------------------------------ WordPress style: MH, GA
def _wp(n, start=0):
    return [{"id": start + i, "date": "2026-08-0%dT01:02" % (1 + i % 9),
             "link": "" if i == 0 else f"https://w/{start + i}",
             "title": {"rendered": " T&amp;%d <b>x</b> " % i if i != 1 else "  "}} for i in range(n)]


@pytest.mark.parametrize("fn,cat,prefix", [("fetch_mh", "DGIPR wire", "https://mahasamvad.in/"),
                                           ("fetch_goa", "DIP wire", "")])
def test_wordpress_fetchers_paging(csn, monkeypatch, fn, cat, prefix):
    pages = {1: _wp(100), 2: _wp(3, start=1000)}
    seen = []

    def gj(url, **kw):
        import urllib.parse as up
        p = int(up.parse_qs(up.urlparse(url).query)["page"][0])
        seen.append(p)
        return pages[p]

    monkeypatch.setattr(csn, "_get_json", gj)
    rows = getattr(csn, fn)()
    assert seen == [1, 2]
    assert len(rows) == 100 - 1 + 3 - 1   # blank title dropped on each page
    assert rows[0]["title"] == "T&0 x" and rows[0]["category"] == cat
    assert rows[0]["date"] == "2026-08-01"
    assert rows[0]["url"] == (prefix + "0/" if prefix else "")


@pytest.mark.parametrize("fn", ["fetch_mh", "fetch_goa"])
def test_wordpress_fetchers_stop_on_short_page_and_error(csn, monkeypatch, fn, capsys):
    n = []
    monkeypatch.setattr(csn, "_get_json", lambda url, **kw: n.append(1) or _wp(5))
    assert len(getattr(csn, fn)()) == 4 and len(n) == 1
    monkeypatch.setattr(csn, "_get_json", lambda url, **kw: (_ for _ in ()).throw(OSError("dead")))
    assert getattr(csn, fn)() == []
    assert "page 1: FETCH FAILED (dead)" in capsys.readouterr().err


# ------------------------------------------------------------------ KA
def test_fetch_ka(csn, monkeypatch):
    h = ('<a href="https://cm.karnataka.gov.in/500/cm-inaugurates-new-industrial-park-in-tumakuru/en">'
         '<a href="https://cm.karnataka.gov.in/500/cm-inaugurates-new-industrial-park-in-tumakuru/kn">'
         '<a href="https://cm.karnataka.gov.in/399/this-slug-is-long-enough-but-id-too-low/en">'
         '<a href="https://cm.karnataka.gov.in/400/short-slug/en">'
         '<a href="https://cm.karnataka.gov.in/401/exactly-twenty-five-chars/kn">'
         '<a href="https://cm.karnataka.gov.in/402/twenty-four-chars-aaaaaa/kn">')
    feed(csn, monkeypatch, {"karnataka": h})
    rows = csn.fetch_ka()
    assert [r["newsid"] for r in rows] == ["500", "401"]
    assert rows[0]["title"] == "Cm inaugurates new industrial park in tumakuru"
    assert rows[0]["date"] == TODAY and rows[0]["category"] == "CM office"
    assert rows[1]["title"] == "Exactly twenty five chars"   # slug len 25 passes the >=25 floor


# ------------------------------------------------------------------ RJ
def test_fetch_rajasthan(csn, monkeypatch):
    payload = {"Data": {"Data": [
        {"Id": 7, "PressreleaseDate": "2026-08-03T00:00", "Description": "<p>नमस्ते  <b>दुनिया</b></p>",
         "PDFUrl": "http://pdf/7", "DepartmentTitle": " Dept ", "KeyWords": "k" * 300},
        {"Id": 8, "Description": "<p></p>"},
        {"Id": 9, "PressreleaseDate": "2026-08-04", "Description": "x" * 250},
    ]}}
    calls = feed(csn, monkeypatch, {"rajasthan": json.dumps(payload)})
    rows = csn.fetch_rajasthan(page_size=5, page=2)
    body = json.loads(calls[0]["data"])
    assert body["PageSize"] == 5 and body["Page"] == 2
    assert len(rows) == 2
    assert rows[0] == {"newsid": "7", "date": "2026-08-03", "title": "नमस्ते दुनिया", "category": "Dept",
                       "keywords": "k" * 200, "url": "http://pdf/7"}
    assert len(rows[1]["title"]) == 200 and rows[1]["category"] == "DIPR wire"
    assert rows[1]["url"] == "https://dipr.rajasthan.gov.in/pages/press-release-list/0"
    feed(csn, monkeypatch, {"rajasthan": json.dumps({"Data": None})})
    assert csn.fetch_rajasthan() == []


# ------------------------------------------------------------------ simple HTML scrapers
def test_fetch_punjab(csn, monkeypatch):
    item = lambda slug, title, d: (f'<a href="/en/press-releases/{slug}"><p>{title}</p></a> x '
                                   f'<i class="icofont-ui-calendar"></i>{d}')
    h = (item("one", "Minister *launches*  scheme", "August 5, 2026") + item("one", "dup slug title", "August 6, 2026")
         + item("two", "Bad date format title", "Smarch 5, 2026") + item("three", "short", "August 7, 2026"))
    feed(csn, monkeypatch, {"punjab": h})
    rows = csn.fetch_punjab()
    assert rows == [{"newsid": "one", "date": "2026-08-05", "title": "Minister launches scheme",
                     "category": "HQ press", "keywords": "",
                     "url": "https://ipr.punjab.gov.in/en/press-releases/one"}]


def test_fetch_mizoram(csn, monkeypatch):
    h = ('<a href="/post/abc-1" class="x" title="Mizoram CM launches new scheme">..Dated: 5<sup>th</sup> Aug 26 '
         '<a href="/post/abc-2" title="Another long enough title here">..Dated: 12<sup>th</sup> Foo 26')
    calls = feed(csn, monkeypatch, {"mizoram": h})
    rows = csn.fetch_mizoram()
    assert len(calls) == 2  # two pages
    assert rows[0] == {"newsid": "abc-1", "date": "2026-08-05", "title": "Mizoram CM launches new scheme",
                       "category": "DIPR English", "keywords": "",
                       "url": "https://dipr.mizoram.gov.in/post/abc-1"}
    assert len(rows) == 2  # bad-month row dropped (once per page)


def test_fetch_nagaland(csn, monkeypatch):
    h = ('<h2 class="entry-title x"> <a href="/naga/a-1" t>GOVT ANNOUNCES NEW SCHEME</a> </h2> '
         '<time datetime="Aug 5 2026">'
         '<h2 class="entry-title"><a href="/naga/b-2">Mixed Case Title Stays</a></h2> <time datetime="Bad 5 2026">'
         '<h2 class="entry-title"><a href="/naga/c-3">Lower  Case &amp; Fine</a></h2> <time datetime="Sep 1 2026">')
    calls = feed(csn, monkeypatch, {"nagaland": h})
    rows = csn.fetch_nagaland()
    assert len(calls) == 4
    first = rows[0]
    assert first["title"] == "Govt Announces New Scheme" and first["date"] == "2026-08-05"
    assert first["newsid"] == "naga/a-1"
    assert rows[1]["title"] == "Lower  Case & Fine" and rows[1]["date"] == "2026-09-01"
    assert len(rows) == 8


def test_fetch_sikkim(csn, monkeypatch):
    h = ('<h2 class="text-lg font-semibold">Sikkim press note one</h2> <p class="t">Published on: 5 Aug 2026</p>'
         ' <a href="/press_releases/GUID1_x.pdf">'
         '<h2 class="text-lg font-semibold">Duplicate guid</h2> <p>Published on: 6 Aug 2026</p> <a href="/press_releases/GUID1_y.pdf">'
         '<h2 class="text-lg font-semibold">Bad date row</h2> <p>Published on: 6 Foo 2026</p> <a href="/press_releases/GUID2_y.pdf">')
    calls = feed(csn, monkeypatch, {"sikkim": h})
    rows = csn.fetch_sikkim()
    assert len(calls) == 3
    assert rows == [{"newsid": "GUID1", "date": "2026-08-05", "title": "Sikkim press note one",
                     "category": "IPR", "keywords": "",
                     "url": "https://ipr.sikkim.gov.in/press_releases/GUID1_x.pdf"}]


def test_fetch_chandigarh_and_dd(csn, monkeypatch):
    ch = ('<tr> <td>1</td> <td><a href="https://chandigarh.gov.in/cadmin//uploads/n1.pdf" t> Public  notice </a></td>'
          '<td> </td> <td> 05/08/2026')
    feed(csn, monkeypatch, {"chandigarh": ch})
    assert csn.fetch_chandigarh() == [{"newsid": "n1", "date": "2026-08-05", "title": "Public notice",
                                       "category": "Administration", "keywords": "",
                                       "url": "https://chandigarh.gov.in/cadmin//uploads/n1.pdf"}]
    feed(csn, monkeypatch, {"chandigarh": ch.replace("<td> </td>", "<td> Dept   X </td>")})
    assert csn.fetch_chandigarh()[0]["category"] == "Dept X"
    dd = ('<td role="rowheader" a>Daman  update</td> <td> 01/09/2026</td> x href="https://cdnbbsr.s3waas.gov.in/f/doc.v2.pdf"')
    calls = feed(csn, monkeypatch, {"ddd.gov.in": dd})
    rows = csn.fetch_dnh_dd()
    assert len(calls) == 2 and calls[1]["url"].endswith("latest-updates/page/2/")
    assert rows[0] == {"newsid": "doc", "date": "2026-09-01", "title": "Daman update",
                       "category": "Latest updates", "keywords": "",
                       "url": "https://cdnbbsr.s3waas.gov.in/f/doc.v2.pdf"}


def test_fetch_kerala(csn, monkeypatch):
    h = ('<time datetime="2026-08-05T10:00" x>..<div class="post-title"> <a href="/index.php/ml/pr/123" t>Title &amp; one</a>')
    calls = feed(csn, monkeypatch, {"kerala": h})
    rows = csn.fetch_kerala()
    assert len(calls) == 3
    assert rows[0] == {"newsid": "123", "date": "2026-08-05", "title": "Title & one", "category": "PRD",
                       "keywords": "", "url": "https://prd.kerala.gov.in/ml/pr/123"}


RSS_TS = ("<rss><item><title><![CDATA[ Telangana CM &amp; team ]]></title><link>https://t/2026/08/some-Slug_1/</link>"
          "<pubDate>Wed, 05 Aug 2026 10:00:00 +0000</pubDate></item>"
          "<item><title>Odd date</title><link>https://t/2026/07/odd-one/</link><pubDate>garbage</pubDate></item>"
          "<item><title>No path date</title><link>https://t/x/nodate/</link><pubDate>garbage</pubDate></item>"
          "<item><title></title><link>https://t/empty/</link><pubDate>Wed, 05 Aug 2026</pubDate></item></rss>")


def test_fetch_telangana(csn, monkeypatch):
    feed(csn, monkeypatch, {"telangana": RSS_TS})
    rows = csn.fetch_telangana()
    assert [(r["newsid"], r["date"]) for r in rows] == [
        ("some-slug1", "2026-08-05"), ("odd-one", "2026-07-01"), ("nodate", TODAY)]
    assert rows[0]["title"] == "Telangana CM & team"


def test_fetch_assam(csn, monkeypatch):
    def row(t, u):
        return f'<tr><td>{t}</td><td>x</td><td><a class="file-default" href="{u}">d</a></td></tr>'
    h = (row("Release dated 05/08/2026 CM", "http://a/f1.pdf") + row("Held on 7 August, 2026 event", "http://a/f2.pdf")
         + row("Short year 1.2.26 here", "http://a/f3.pdf") + row("No date at all", "http://a/f4.pdf")
         + row("Bad month 5/13/2026", "http://a/f5.pdf") + row("Big day 45/08/2026", "http://a/f6.pdf")
         + row("<b> </b>", "http://a/f7.pdf"))
    feed(csn, monkeypatch, {"assam": h})
    rows = {r["newsid"]: r for r in csn.fetch_assam()}
    assert rows["f1.pdf"]["date"] == "2026-08-05"
    assert rows["f2.pdf"]["date"] == "2026-08-07"
    assert rows["f3.pdf"]["date"] == "2026-02-01"
    assert rows["f4.pdf"]["date"] == TODAY
    assert rows["f5.pdf"]["date"] == TODAY
    assert rows["f6.pdf"]["date"] == "2026-08-31"   # day clamped to 31
    assert "f7.pdf" not in rows and rows["f1.pdf"]["category"] == "DIPR"


def test_fetch_ap(csn, monkeypatch, capsys):
    good = {"dataList": [{"id": 1, "title": " A  title ", "from": "2026-08-05T00:00", "url": "http://u"},
                         {"id": 2, "title": "img", "from": "2026-08-06", "imageBase64": "data:x"},
                         {"id": 3, "title": "fallback", "from": "2026-08-07"},
                         {"id": 4, "title": "", "from": "2026-08-07"},
                         {"id": 5, "title": "nodate", "from": ""}]}

    def gj(url, **kw):
        if url.endswith("ApNewsLatestAnnouncements"):
            return good
        raise OSError("down")

    monkeypatch.setattr(csn, "_get_json", gj)
    rows = csn.fetch_ap()
    assert [(r["newsid"], r["url"], r["category"]) for r in rows] == [
        ("ApNewsLatestAnnouncements-1", "http://u", "News wire"),
        ("ApNewsLatestAnnouncements-2", "data:x", "News wire"),
        ("ApNewsLatestAnnouncements-3", "https://www.ap.gov.in/", "News wire")]
    assert rows[0]["title"] == "A title" and rows[0]["date"] == "2026-08-05"
    assert "ApNewsAnnouncements: FETCH FAILED (down)" in capsys.readouterr().err


def test_fetch_tamil_nadu(csn, monkeypatch, capsys):
    pr = {"success": 1, "data": [
        {"id": 5, "pr_date": "2026-08-05T00:00", "press_name": " CM_statement-on  roads.PDF ", "press_file_name": "/files/a b.pdf"},
        {"id": 6, "uploaded_date": "2026-08-06", "press_name": "x.pdf", "press_file_name": "/f%20x.pdf"},
        {"id": 7, "press_name": "", "press_file_name": "/f.pdf"},
        {"id": 0, "press_name": "noid.pdf", "press_file_name": "/f.pdf"},
        {"id": 8, "press_name": "nofile.pdf", "press_file_name": ""}]}
    seen = []

    def gj(url, timeout, headers):
        seen.append((url, headers))
        if url.endswith("press_release"):
            return pr
        return {"success": 0, "message": "APP Key Missing"}

    monkeypatch.setattr(csn, "_get_json", gj)
    rows = csn.fetch_tamil_nadu()
    assert [r["newsid"] for r in rows] == ["pr5", "pr6"]
    assert rows[0]["title"] == "CM statement-on roads" and rows[0]["date"] == "2026-08-05"
    assert rows[0]["url"] == "https://dipr.tn.gov.in/dipr_api/v1/files/a%20b.pdf"
    assert rows[1]["url"].endswith("/f%20x.pdf") and rows[1]["date"] == "2026-08-06"
    assert seen[0][1]["X-App-Key"] == "dipr"
    assert "unexpected response (APP Key Missing)" in capsys.readouterr().err

    def gj2(url, timeout, headers):
        raise OSError("tn down")

    monkeypatch.setattr(csn, "_get_json", gj2)
    assert csn.fetch_tamil_nadu() == []
    assert "press_release: FETCH FAILED (tn down)" in capsys.readouterr().err


BR_PAGE = ('<meta name="_csrf" content="CSRF1">'
           '<td class="text-center">1</td> <td>101</td> <td> विषय  एक </td> <td class="text-center">05/08/2026</td> x downloadFile(\'p1\')'
           '<td class="text-center">2</td> <td>102</td> <td>second</td> <td class="text-center">06/08/2026</td> x downloadFile(\'p2\')'
           '<td class="text-center">3</td> <td>103</td> <td>  </td> <td class="text-center">07/08/2026</td> x downloadFile(\'p3\')')


def test_fetch_bihar(csn, monkeypatch, capsys):
    calls = []

    def get(url, timeout=45, opener=None, data=None, headers=None):
        calls.append((url, data))
        if url.endswith("prdbihar/"):
            return ""
        if "editForm" in url:
            return BR_PAGE
        if b"downloadLink=p1" in data:
            return "<script>window.open('./cache/a b/x.pdf')</script>"
        if b"downloadLink=p2" in data:
            raise OSError("resolve boom")
        return ""

    monkeypatch.setattr(csn, "_get", get)
    rows = csn.fetch_bihar()
    assert [r["newsid"] for r in rows] == ["PR101", "PR102"]
    assert rows[0]["url"] == "https://state.bihar.gov.in/prdbihar/cache/a%20b/x.pdf"
    assert rows[0]["date"] == "2026-08-05" and rows[0]["title"] == "विषय एक"
    assert rows[1]["url"].endswith("#PR102")
    assert b"_csrf=CSRF1" in calls[2][1]
    assert "PR102: resolve failed (resolve boom)" in capsys.readouterr().err


def test_fetch_bihar_limit_and_no_csrf(csn, monkeypatch):
    def get(url, timeout=45, opener=None, data=None, headers=None):
        return BR_PAGE if "editForm" in url else ""

    monkeypatch.setattr(csn, "_get", get)
    assert [r["newsid"] for r in csn.fetch_bihar(limit=1)] == ["PR101"]
    assert csn.fetch_bihar(limit=0) == []
    monkeypatch.setattr(csn, "_get", lambda *a, **k: "no token")
    with pytest.raises(RuntimeError, match="csrf"):
        csn.fetch_bihar()


def test_fetch_odisha(csn, monkeypatch):
    def it(path, title, d):
        return (f'<a href="{path}" x class="text-decoration-none"> <h2 c>{title}</h2> </a> '
                f'<div class="date mb-2 text-muted small"> <i c></i> {d} </div>')
    h = (it("/en/latest-news/n-1", "CM  reviews &amp; plans", "05 Aug, 2026") + it("/en/latest-news/n-1", "dup", "05 Aug, 2026")
         + it("/en/latest-news/n-2", "bad date", "5 Foo, 2026"))
    calls = feed(csn, monkeypatch, {"odisha": h})
    rows = csn.fetch_odisha()
    assert len(calls) == 3
    assert rows == [{"newsid": "n-1", "date": "2026-08-05", "title": "CM reviews & plans", "category": "CMO wire",
                     "keywords": "", "url": "https://cm.odisha.gov.in/en/latest-news/n-1"}]


def test_fetch_haryana(csn, monkeypatch):
    h = ('href="https://prms.prharyana.gov.in/press-release/11" class="a-size"> *Haryana CM <b>meets</b>  team* </a>'
         'href="https://prms.prharyana.gov.in/press-release/11" class="a-size">dup</a>'
         'href="https://prms.prharyana.gov.in/press-release/12" class="a-size"> ** </a>')
    feed(csn, monkeypatch, {"prharyana": h})
    assert csn.fetch_haryana() == [{"newsid": "11", "date": TODAY, "title": "Haryana CM meets team",
                                    "category": "PRMS", "keywords": "",
                                    "url": "https://prms.prharyana.gov.in/press-release/11"}]


def test_fetch_delhi(csn, monkeypatch):
    def it(title, d, url):
        return (f'<div class="tab-title"> {title} <div> <div class="tab-date">Date : {d} x href="{url}"')
    h = it("Notice  one", "05-08-2026", "/files/n1.pdf") + it("   ", "06-08-2026", "/files/n2.pdf") + it("Root", "07-08-2026", "/")
    feed(csn, monkeypatch, {"delhi.gov.in": h})
    rows = csn.fetch_delhi()
    assert rows[0] == {"newsid": "n1.pdf", "date": "2026-08-05", "title": "Notice one",
                       "category": "GNCTD Notifications", "keywords": "",
                       "url": "https://delhi.gov.in/files/n1.pdf"}
    assert len(rows) == 2 and rows[1]["newsid"].startswith("2026-08-07-")


def test_fetch_west_bengal(csn, monkeypatch, capsys):
    def row(href, title, d):
        return f'<tr> <td><a href="{href}" t>{title}</a></td> <td>{d}</td>'
    h = row("docs/a.pdf", "Notice  A", "05-08-2026") + row("docs/a.pdf", "dup", "06-08-2026") + row("/", "Root", "07-08-2026") + row("docs/b.pdf", " ", "08-08-2026")
    calls = feed(csn, monkeypatch, {"notice.php": h, "govt-order.php": OSError("wb down")})
    rows = csn.fetch_west_bengal()
    assert rows[0] == {"newsid": "a.pdf", "date": "2026-08-05", "title": "Notice A", "category": "Notice",
                       "keywords": "", "url": "https://icad.wb.gov.in/docs/a.pdf"}
    assert rows[1]["newsid"].startswith("2026-08-07-") and len(rows) == 2
    assert "govt-order.php: FETCH FAILED (wb down)" in capsys.readouterr().err
    assert len(calls) == 2


def test_sources_registry(csn):
    assert len(csn.SOURCES) == 23
    assert csn.SOURCES["MP"]["mode"] == "daily"
    assert all(s["mode"] == "latest" for c, s in csn.SOURCES.items() if c != "MP")
    assert all(callable(s["fetch"]) for s in csn.SOURCES.values())


# ------------------------------------------------------------------ db + main
def test_ensure_db_creates_and_migrates(csn, fake_repo):
    con = csn.ensure_db()
    cols = [r[1] for r in con.execute("pragma table_info(state_news)")]
    assert "title_en" in cols
    con.close()
    # legacy table without title_en gets the column added
    import os
    os.remove(csn.DB)
    legacy = sqlite3.connect(csn.DB)
    legacy.execute("create table state_news(state text not null, newsid text not null, date text not null,"
                   " title text not null, category text, keywords text, url text, fetched_at text not null,"
                   " primary key(state, newsid))")
    legacy.commit()
    legacy.close()
    con = csn.ensure_db()
    assert "title_en" in [r[1] for r in con.execute("pragma table_info(state_news)")]
    assert con.execute("pragma index_list(state_news)").fetchall()


def _row(nid, title, date="2026-08-05"):
    return {"newsid": nid, "date": date, "title": title, "category": "c", "keywords": "k", "url": "u"}


def test_main_inserts_dedups_translates_and_backfills(csn, monkeypatch, capsys):
    pre = csn.ensure_db()
    pre.execute("insert into state_news(state,newsid,date,title,fetched_at) values('XX','old','2026-01-01','नम','t')")
    pre.execute("insert into state_news(state,newsid,date,title,fetched_at) values('XX','old2','2026-01-01','english','t')")
    pre.commit()
    pre.close()
    batches = {"MP": [[_row("a", "English one")], [_row("b", "हिन्दी")]],
               "UP": [[_row("a", "English one"), _row("a", "English one")]]}
    csn.SOURCES = {
        "MP": {"state": "S1", "mode": "daily", "fetch": lambda day, it=iter(batches["MP"]): next(it)},
        "UP": {"state": "S2", "mode": "latest", "fetch": lambda: batches["UP"][0]},
        "ZZ": {"state": "S3", "mode": "latest", "fetch": lambda: (_ for _ in ()).throw(OSError("src down"))},
    }
    monkeypatch.setattr(csn, "translate_en", lambda t: "translated:" + t[:1] if t else None)
    monkeypatch.setattr(sys, "argv", ["x", "--days", "2"])
    csn.main()
    out = capsys.readouterr()
    con = sqlite3.connect(csn.DB)
    got = {(s, n): te for s, n, te in con.execute("select state,newsid,title_en from state_news")}
    assert got[("MP", "a")] == "English one"
    assert got[("MP", "b")] == "translated:ह"
    assert got[("UP", "a")] == "English one"
    assert got[("XX", "old")] == "translated:न"       # backfill
    assert got[("XX", "old2")] == "english"                 # english backfill w/o translation
    assert "MP (S1): fetched 2, 2 new (1 machine-translated) -> 2 total in register" in out.out
    assert "UP (S2): fetched 2, 1 new (0 machine-translated) -> 1 total" in out.out
    assert "ZZ: FETCH FAILED (src down)" in out.err
    assert "backfill: 2/2 rows gained title_en" in out.out


def test_main_state_filter_no_translate_and_daily_error(csn, monkeypatch, capsys):
    def boom(day):
        raise OSError("daily down")

    csn.SOURCES = {"MP": {"state": "S1", "mode": "daily", "fetch": boom},
                   "UP": {"state": "S2", "mode": "latest", "fetch": lambda: [_row("n", "हि")]}}
    monkeypatch.setattr(csn, "translate_en", lambda t: pytest.fail("translation must be skipped"))
    monkeypatch.setattr(sys, "argv", ["x", "--state", "mp", "--days", "3"])
    csn.main()
    err = capsys.readouterr().err
    assert err.count("FETCH FAILED (daily down)") == 3

    monkeypatch.setattr(sys, "argv", ["x", "--state", "up", "--no-translate"])
    csn.main()
    con = sqlite3.connect(csn.DB)
    assert con.execute("select title_en from state_news where state='UP'").fetchall() == [(None,)]
    assert "backfill" not in capsys.readouterr().out


def test_run_as_script(fake_repo, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["x", "--state", "nonexistent", "--no-translate"])
    load_script("collect_state_news", fake_repo, run_name="__main__")
    assert (fake_repo / "data" / "registers" / "state_news.sqlite").exists()
