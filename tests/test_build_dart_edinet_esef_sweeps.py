"""DART / EDINET / ESEF-XBRL India-intent sweeps (HTTP faked, credentials are throw-away test values)."""
import datetime as dt
import io
import json
import zipfile

import pytest
import requests

from _fakes import FakeResp
from conftest import load_script


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    import time
    monkeypatch.setattr(time, "sleep", lambda *a: None)


def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for n, data in files.items():
            z.writestr(n, data)
    return buf.getvalue()


# ----------------------------------------------------------------------- DART
@pytest.fixture
def dart(fake_repo, tmp_path):
    m = load_script("build_dart_india_sweep", fake_repo)
    creds = tmp_path / "creds.env"
    m.CREDS = str(creds)
    m.OUT = str(fake_repo / "layers/16_enrichment/dart.json")
    return m, creds, fake_repo


def test_dart_load_key_variants(dart):
    m, creds, _ = dart
    with pytest.raises(SystemExit, match="credentials file not found"):
        m.load_dart_key()
    creds.write_text("OTHER=1\nDART_KEY=<paste>\n")
    with pytest.raises(SystemExit, match="missing or placeholder"):
        m.load_dart_key()
    creds.write_text("DART_KEY=your-key-here\n")
    with pytest.raises(SystemExit):
        m.load_dart_key()
    creds.write_text("DART_KEY=\n")
    with pytest.raises(SystemExit):
        m.load_dart_key()
    creds.write_text("A=1\nDART_KEY=test-value-123\n")
    assert m.load_dart_key() == "test-value-123"
    creds.write_text("DART_KEY=a=b\n")
    assert m.load_dart_key() == "a=b"           # split on first '=' only


def test_dart_find_hits_intent_business_and_homonym(dart):
    m, *_ = dart
    text = "당사는 인도 진출을 추진. 인도 수출 증가. 인도하다 인도되었다 인도한 인도받은 인도함 인도해. 인도 시장"
    h = m.find_hits(text)
    assert [x["phrase"] for x in h["intent"]] == ["인도 진출"]
    assert sorted(x["phrase"] for x in h["business"]) == ["인도 수출", "인도 시장"]
    assert h["excluded_delivery_verb"] == 6        # 인도하/되/한/받/함/해
    assert "인도 진출" in h["intent"][0]["snippet"]
    assert m.find_hits("nothing") == {"intent": [], "business": [], "excluded_delivery_verb": 0}


def test_dart_find_hits_snippet_window_and_newlines(dart):
    m, *_ = dart
    text = "a" * 30 + "인도 투자" + "b\nb" * 10
    s = m.find_hits(text)["intent"][0]["snippet"]
    assert s.startswith("a" * 20 + "인도 투자") and "\n" not in s
    assert len(s) == 20 + len("인도 투자") + 20


def _chunk_get(pages):
    calls = []

    def get(url, params=None, timeout=None):
        calls.append(dict(params))
        return FakeResp(jsonobj=pages(params))
    return get, calls


def test_dart_list_chunk_pagination_and_statuses(dart, monkeypatch, capsys):
    m, *_ = dart

    def pages(p):
        return {"status": "000", "total_page": 2, "list": [{"rcept_no": f"r{p['page_no']}"}]}
    get, calls = _chunk_get(pages)
    monkeypatch.setattr(requests, "get", get)
    got = m.list_filings_chunk("K", "20260101", "20260301", "Y")
    assert [f["rcept_no"] for f in got] == ["r1", "r2"] and [c["page_no"] for c in calls] == [1, 2]
    assert calls[0]["pblntf_detail_ty"] == "A001" and calls[0]["corp_cls"] == "Y" and calls[0]["page_count"] == 100
    # 013 -> no data, silently empty; other statuses reported on stderr
    get, _ = _chunk_get(lambda p: {"status": "013"})
    monkeypatch.setattr(requests, "get", get)
    assert m.list_filings_chunk("K", "a", "b", "Y") == []
    assert capsys.readouterr().err == ""
    get, _ = _chunk_get(lambda p: {"status": "100", "message": "too wide"})
    monkeypatch.setattr(requests, "get", get)
    assert m.list_filings_chunk("K", "a", "b", "K") == []
    assert "list.json error 100: too wide (range a..b)" in capsys.readouterr().err


def test_dart_list_chunk_defaults_single_page(dart, monkeypatch):
    m, *_ = dart
    get, calls = _chunk_get(lambda p: {"status": "000", "list": [{"rcept_no": "x"}]})
    monkeypatch.setattr(requests, "get", get)
    assert len(m.list_filings_chunk("K", "a", "b", "Y")) == 1 and len(calls) == 1


def test_dart_list_filings_chunks_90_day_windows(dart, monkeypatch):
    m, *_ = dart
    seen = []
    monkeypatch.setattr(m, "list_filings_chunk", lambda k, b, e, c: (seen.append((b, e, c)), [{"x": b}])[1])
    got = m.list_filings("K", "20260101", "20260630", "K")
    # 181 days -> 90 + 90 + 1
    assert seen == [("20260101", "20260331", "K"), ("20260401", "20260629", "K"), ("20260630", "20260630", "K")]
    assert len(got) == 3
    seen.clear()
    m.list_filings("K", "20260101", "20260101", "Y")
    assert seen == [("20260101", "20260101", "Y")]
    seen.clear()
    assert m.list_filings("K", "20260301", "20260101", "Y") == [] and seen == []   # start after stop


def test_dart_sweep_filing(dart, monkeypatch):
    m, *_ = dart
    z = make_zip({"a.xml": "인도 진출 계획".encode(), "b.xml": "인도 수출 및 인도하다".encode(),
                  "bad.xml": b"\xff\xfe nothing"})
    seen = []
    monkeypatch.setattr(requests, "get", lambda url, params=None, timeout=None: (seen.append((url, params, timeout)), FakeResp(z))[1])
    r = m.sweep_filing("K", "2026R1")
    assert len(r["intent"]) == 1 and len(r["business"]) == 1 and r["excluded_delivery_verb"] == 1
    assert seen[0][1]["rcept_no"] == "2026R1" and seen[0][2] == 60
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(b"x", status=500))
    with pytest.raises(requests.HTTPError):
        m.sweep_filing("K", "r")


def _dart_main(m, root, argv):
    return load_script("build_dart_india_sweep", root, argv=argv, run_name="__main__",
                       globals_override=None)


def test_dart_main_flow(dart, monkeypatch, capsys, tmp_path):
    m, creds, root = dart
    creds.write_text("DART_KEY=test-value\n")
    out = root / "layers/16_enrichment/dart.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"results": [{"rcept_no": "OLD", "hits": {}}]}))
    monkeypatch.setattr(m, "CREDS", str(creds))
    monkeypatch.setattr(m, "OUT", str(out))
    filings = [{"rcept_no": "OLD", "corp_name": "o", "stock_code": "1"},
               {"rcept_no": "N1", "corp_name": "Intent Co", "stock_code": "2"},
               {"rcept_no": "N2", "corp_name": "Biz Co", "stock_code": "3"},
               {"rcept_no": "N3", "corp_name": "Err Co", "stock_code": "4"},
               {"rcept_no": "N4", "corp_name": "Beyond Cap", "stock_code": "5"}]
    monkeypatch.setattr(m, "list_filings", lambda k, b, e, c: filings)
    sweeps = {"N1": {"intent": [{"phrase": "인도 진출", "snippet": "S1"}], "business": [], "excluded_delivery_verb": 0},
              "N2": {"intent": [], "business": [{"phrase": "인도 수출", "snippet": "S2"}], "excluded_delivery_verb": 0}}

    def fake_sweep(k, r):
        if r == "N3":
            raise ValueError("bad zip")
        return sweeps[r]
    monkeypatch.setattr(m, "sweep_filing", fake_sweep)
    monkeypatch.setattr("sys.argv", ["x", "--since", "2026-01-01", "--until", "2026-02-01", "--max-filings", "3"])
    m.main()
    data = json.load(open(out))
    assert data["count"] == 4
    by = {r["rcept_no"]: r for r in data["results"]}
    assert set(by) == {"OLD", "N1", "N2", "N3"}          # N4 beyond --max-filings
    assert by["N3"]["hits"] == {"error": "ValueError: bad zip"}
    assert by["N1"]["swept"] == dt.date.today().isoformat()
    text = capsys.readouterr().out
    assert "filings in range (Y, 2026-01-01..2026-02-01): 5" in text
    assert "already swept (prior runs): 1 | unswept: 4 | sweeping this run: 3" in text
    assert "[1/3] NEW-LEAD (INTENT): Intent Co (2) -- S1" in text
    assert "[2/3] NEW-LEAD (business-only): Biz Co (3) -- S2" in text
    assert "new leads (intent or business hit): 2" in text and "cumulative filings tracked: 4" in text
    assert data["corpus_note"].endswith("corp_cls=Y")


def test_dart_main_unbounded_and_kosdaq(dart, monkeypatch):
    m, creds, root = dart
    creds.write_text("DART_KEY=test-value\n")
    seen = {}
    monkeypatch.setattr(m, "list_filings", lambda k, b, e, c: (seen.update(b=b, e=e, c=c),
                                                               [{"rcept_no": f"r{i}"} for i in range(60)])[1])
    monkeypatch.setattr(m, "sweep_filing", lambda k, r: {"intent": [], "business": [], "excluded_delivery_verb": 0})
    monkeypatch.setattr("sys.argv", ["x", "--since", "2026-03-04", "--until", "2026-03-09",
                                     "--corp-cls", "K", "--max-filings", "0"])
    m.main()
    assert (seen["b"], seen["e"], seen["c"]) == ("20260304", "20260309", "K")
    assert json.load(open(m.OUT))["count"] == 60       # 0 = unbounded


def test_dart_default_max_filings_is_40(dart, monkeypatch):
    m, creds, root = dart
    creds.write_text("DART_KEY=test-value\n")
    monkeypatch.setattr(m, "list_filings", lambda *a: [{"rcept_no": f"r{i}"} for i in range(60)])
    monkeypatch.setattr(m, "sweep_filing", lambda k, r: {"intent": [], "business": []})
    monkeypatch.setattr("sys.argv", ["x"])
    m.main()
    assert json.load(open(m.OUT))["count"] == 40


# --------------------------------------------------------------------- EDINET
@pytest.fixture
def edinet(fake_repo, tmp_path):
    m = load_script("build_edinet_india_sweep", fake_repo)
    creds = tmp_path / "e.env"
    m.CREDS = str(creds)
    m.OUT = str(fake_repo / "layers/16_enrichment/edinet.json")
    return m, creds, fake_repo


def test_edinet_load_key(edinet):
    m, creds, _ = edinet
    with pytest.raises(SystemExit, match="EDINET_API_KEY missing"):
        m.load_key()
    creds.write_text("EDINET_API_KEY=<your key>\n")
    with pytest.raises(SystemExit):
        m.load_key()
    creds.write_text("EDINET_API_KEY=Your-Key\n")
    with pytest.raises(SystemExit):
        m.load_key()
    creds.write_text("EDINET_API_KEY=\n")
    with pytest.raises(SystemExit):
        m.load_key()
    creds.write_text("EDINET_API_KEY=testval\n")
    assert m.load_key() == "testval"


def test_edinet_api_get_and_list_day(edinet, monkeypatch):
    m, *_ = edinet
    seen = []

    def get(url, params=None, timeout=None):
        seen.append((url, params, timeout))
        return FakeResp(jsonobj={"results": [{"docID": "D1"}]}) if "documents.json" in url else FakeResp(b"RAW")
    monkeypatch.setattr(requests, "get", get)
    assert m.list_day("KEY", "2026-03-02") == [{"docID": "D1"}]
    assert seen[0][0].endswith("/documents.json")
    assert seen[0][1] == {"date": "2026-03-02", "type": "2", "Subscription-Key": "KEY"} and seen[0][2] == 30
    assert m.api_get("documents/D1", "KEY", {"type": "5"}, expect_json=False) == b"RAW"
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(jsonobj={"results": None}))
    assert m.list_day("K", "d") == []
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(b"", status=401))
    with pytest.raises(requests.HTTPError):
        m.api_get("x", "K", {})


def test_edinet_find_hits_and_sweep_doc(edinet, monkeypatch):
    m, *_ = edinet
    assert [h["phrase"] for h in m.find_hits("当社はインド進出とインド工場")] == ["インド進出", "インド工場"]
    assert m.find_hits("インドネシア") == []
    z = make_zip({"a.csv": "インド市場".encode("utf-16-le"), "skip.txt": "インド進出".encode("utf-16-le"),
                  "b.csv": "なし".encode("utf-16-le")})
    monkeypatch.setattr(m, "api_get", lambda path, key, params, expect_json=True: z)
    hits = m.sweep_doc("K", "D")
    assert [h["phrase"] for h in hits] == ["インド市場"]


def test_edinet_main(edinet, monkeypatch, capsys):
    m, creds, root = edinet
    creds.write_text("EDINET_API_KEY=testval\n")
    out = root / "layers/16_enrichment/edinet.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"results": [{"doc_id": "SEEN", "hits": []}]}))
    days = []
    corp = lambda i, **kw: {"docID": i, "ordinanceCode": "010", "docTypeCode": "120", "csvFlag": "1",
                            "filerName": f"F{i}", "secCode": "1", "docDescription": "d", **kw}

    def list_day(key, day):
        days.append(day)
        if len(days) == 1:
            return [corp("SEEN"), corp("A"), corp("B"),
                    corp("X1", ordinanceCode="020"), corp("X2", docTypeCode="999"), corp("X3", csvFlag="0")]
        if len(days) == 2:
            raise RuntimeError("down")
        return [corp("C")]
    monkeypatch.setattr(m, "list_day", list_day)

    def sweep(key, doc):
        if doc == "B":
            raise ValueError("zip")
        return [{"phrase": "インド進出", "snippet": "s"}] if doc == "A" else []
    monkeypatch.setattr(m, "sweep_doc", sweep)
    monkeypatch.setattr("sys.argv", ["x", "--days", "3", "--max-filings", "100", "--checkpoint-every", "2"])
    m.main()
    assert len(days) == 3
    assert all(dt.date.fromisoformat(d).weekday() < 5 for d in days)
    assert days == sorted(days, reverse=True)       # walks backwards from yesterday
    assert dt.date.fromisoformat(days[0]) < dt.date.today()
    data = json.load(open(out))
    by = {r["doc_id"]: r for r in data["results"]}
    assert set(by) == {"SEEN", "A", "B", "C"}
    assert by["A"]["hits"][0]["phrase"] == "インド進出" and by["A"]["filer"] == "FA"
    assert by["B"]["error"] == "ValueError: zip" and by["B"]["hits"] == []
    assert by["C"]["date"] == days[2]
    assert data["count"] == 4
    cap = capsys.readouterr()
    assert "NEW-LEAD: FA (1) -- インド進出: ...s..." in cap.out
    assert f"{days[0]}: 6 total, 3 corp annual/half-year/quarterly" in cap.out
    assert f"{days[1]}: list error RuntimeError: down" in cap.err
    assert "with India-intent hits: 1" in cap.out


def test_edinet_max_filings_stops_scan(edinet, monkeypatch):
    m, creds, root = edinet
    creds.write_text("EDINET_API_KEY=testval\n")
    docs = [{"docID": f"D{i}", "ordinanceCode": "010", "docTypeCode": "160", "csvFlag": "1"} for i in range(5)]
    calls = {"list": 0}
    monkeypatch.setattr(m, "list_day", lambda k, d: (calls.__setitem__("list", calls["list"] + 1), docs)[1])
    monkeypatch.setattr(m, "sweep_doc", lambda k, d: [])
    monkeypatch.setattr("sys.argv", ["x", "--days", "10", "--max-filings", "2"])
    m.main()
    assert calls["list"] == 1 and json.load(open(m.OUT))["count"] == 2


# ------------------------------------------------------------------------ ESEF
@pytest.fixture
def esef(fake_repo):
    m = load_script("build_esef_xbrl_india_sweep", fake_repo)
    m.OUT = str(fake_repo / "layers/16_enrichment/esef.json")
    return m, fake_repo


def test_esef_strip_html_and_find_hits(esef):
    m, _ = esef
    html = "<html><script>var x='expansion in India'</script><style>.a{}</style><p>Hello</p>\n  <b>World</b></html>"
    assert m.strip_html(html).strip() == "Hello World"
    hits = m.find_hits("We plan EXPANSION IN INDIA soon, and also invest in India.")
    assert [h["phrase"] for h in hits] == ["expansion in India", "invest in India"]
    assert hits[0]["snippet"].lower().startswith("we plan expansion in india")
    assert m.find_hits("nothing here") == []
    long = "x" * 100 + "plant in India" + "y" * 100
    s = m.find_hits(long)[0]["snippet"]
    assert s == long[60:100 + 60]


def test_esef_get_json_headers(esef, monkeypatch):
    m, _ = esef
    seen = []
    monkeypatch.setattr(requests, "get", lambda url, params=None, headers=None, timeout=None:
                        (seen.append((url, params, headers, timeout)), FakeResp(jsonobj={"ok": 1}))[1])
    assert m.get_json("http://u", {"a": 1}) == {"ok": 1}
    assert seen[0][2]["Accept"] == "application/vnd.api+json" and seen[0][3] == 30


def _filing(fxo, report_url="/r/%s.html", lei="LEI1", period="2025-12-31"):
    return {"attributes": {"fxo_id": fxo, "report_url": (report_url % fxo) if report_url else None,
                           "period_end": period},
            "relationships": {"entity": {"links": {"related": f"/api/entities/{lei}"}}}}


def test_esef_main(esef, monkeypatch, capsys):
    m, root = esef
    out = root / "layers/16_enrichment/esef.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"results": [{"fxo_id": "SEEN"}]}))
    list_calls = []

    def get_json(url, params=None):
        list_calls.append((url, params))
        if "/api/entities/" in url:
            if url.endswith("LEI2"):
                raise RuntimeError("entity down")
            return {"data": {"attributes": {"name": "Ent One"}}}
        if params:  # first page
            return {"data": [_filing("SEEN"), _filing("F1"), _filing("F2", report_url=None),
                             _filing("F3", lei="LEI2"), _filing("F4"), _filing("F5")],
                    "links": {"next": "https://filings.xbrl.org/api/filings?page=2"}}
        return {"data": [_filing("F6")], "links": {}}
    monkeypatch.setattr(m, "get_json", get_json)

    def fake_get(url, headers=None, timeout=None):
        if url.endswith("F1.html") or url.endswith("F3.html"):
            return FakeResp("<p>We announce expansion in India next year</p>")
        if url.endswith("F4.html"):
            raise RuntimeError("fetch fail")
        return FakeResp("<p>nothing</p>")
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr("sys.argv", ["x", "--countries", "GB", "--max-filings-per-country", "5",
                                     "--checkpoint-every", "1"])
    m.main()
    data = json.load(open(out))
    by = {r["fxo_id"]: r for r in data["results"]}
    assert set(by) == {"SEEN", "F1", "F2", "F3", "F4"}          # cap of 5 includes SEEN, F5/F6 beyond cap
    assert by["F1"]["entity"] == {"lei": "LEI1", "name": "Ent One"}
    assert by["F1"]["hits"][0]["phrase"] == "expansion in India"
    assert by["F2"]["skipped"].startswith("no report_url") and by["F2"]["hits"] == []
    assert by["F3"]["entity"] == {"lei": "LEI2", "name": None}
    assert by["F4"]["error"] == "RuntimeError: fetch fail" and by["F4"]["entity"] is None
    assert list_calls[0][1] == {"filter[country]": "GB", "page[size]": 50}
    assert len([c for c in list_calls if "entities" in c[0]]) == 2
    out_text = capsys.readouterr().out
    assert "NEW-LEAD (GB): Ent One (LEI1) -- expansion in India" in out_text
    assert "GB: fetched 5" in out_text and "with India-intent hits: 2" in out_text


def test_esef_pagination_follows_next_link_and_list_error(esef, monkeypatch, capsys):
    m, root = esef
    pages = []

    def get_json(url, params=None):
        pages.append((url, params))
        if "country" in str(params) and params["filter[country]"] == "FR":
            raise RuntimeError("list down")
        if params:
            return {"data": [_filing("P1")], "links": {"next": "NEXT"}}
        return {"data": [_filing("P2")], "links": {}}
    monkeypatch.setattr(m, "get_json", get_json)
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp("<p>x</p>"))
    monkeypatch.setattr("sys.argv", ["x", "--countries", "GB,FR"])
    m.main()
    assert pages[1] == ("NEXT", None)            # next link carries its own params
    data = json.load(open(m.OUT))
    assert {r["fxo_id"] for r in data["results"]} == {"P1", "P2"}
    cap = capsys.readouterr()
    assert "FR: list error RuntimeError: list down" in cap.err
    assert "FR: fetched 0" in cap.out
