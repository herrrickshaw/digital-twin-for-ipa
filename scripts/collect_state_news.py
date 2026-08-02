#!/usr/bin/env python3
"""State-government news wire -> data/registers/state_news.sqlite.

Counterpart to the central PIB register: pulls daily press releases from state
information-department sites into one dedup'd register so the reportage views can
show state-level scheme/investment announcements next to PIB ones. Non-English
titles are machine-translated into title_en (free Google gtx endpoint, best-effort)
so the central scheme-keyword map can read them.

Sources (extensible via SOURCES; two modes):
  mode "daily"  -- fetch(day) called per day going back --days
  mode "latest" -- fetch() called once, returns the site's latest N releases

  MP  -- mpinfo.org (Madhya Pradesh Jansampark). AngularJS front-end over an open
         GET JSON API: /HomePageWebservice.asmx/Todaynews?strloc=32
         &fontname=fontenglish&publishdate=MM/DD/YYYY (fontenglish=English subset,
         Mangal=full Hindi wire -- we pull BOTH and dedup, translating the Hindi).
         newsid is char-shifted +0x80 ("²°²¶..." -> "20260731N409").
  UP  -- information.up.gov.in. Plain ASP.NET tables of Hindi titles + dated PDF
         links: cm_press_release_details.aspx (CM wire) and
         other_press_release_details.aspx (departments). Latest ~30 rows each.
  GJ  -- gujaratinformation.gujarat.gov.in. POST /BindDepartmentPressRealese with
         an antiforgery token + session cookie from /Department-Releases;
         PressLangId=1 English, 2 Gujarati (latest 15 each; merged on pressId,
         English preferred).

Usage:  python3 scripts/collect_state_news.py [--days 14] [--state MP] [--no-translate]
Rerun daily (idempotent -- INSERT OR IGNORE on (state, newsid)).
"""
import argparse, datetime, html as _html, http.cookiejar, json, os, re, sqlite3, ssl, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data/registers/state_news.sqlite")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def _get(url, timeout=45, opener=None, data=None, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs)
    op = opener.open if opener else urllib.request.urlopen
    try:
        with op(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        # several Indian govt sites serve incomplete cert chains that curl's CA
        # bundle tolerates but Python rejects -- retry unverified (public,
        # read-only data; no credentials ever sent on these requests)
        if not isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError):
            raise
        print(f"warning: broken cert chain, retrying unverified: {url.split('/')[2]}", file=sys.stderr)
        ctx = ssl._create_unverified_context()
        if opener:
            raise  # cookie-carrying openers keep strict TLS
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read().decode("utf-8", "replace")


def _get_json(url, **kw):
    return json.loads(_get(url, **kw))


# ---------------------------------------------------------------- translation
_TRANSLATE_FAILS = 0


def translate_en(text):
    """Best-effort machine translation to English via the free gtx endpoint.
    Returns None on failure or when disabled; trips a breaker after 5 failures."""
    global _TRANSLATE_FAILS
    if _TRANSLATE_FAILS >= 5 or not text:
        return None
    try:
        url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
            {"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text[:900]})
        d = _get_json(url, timeout=20)
        out = "".join(seg[0] for seg in d[0] if seg and seg[0]).strip()
        time.sleep(0.3)
        return out or None
    except Exception:
        _TRANSLATE_FAILS += 1
        return None


def _is_english(s):
    return all(ord(c) < 0x530 for c in s or "")


# ---------------------------------------------------------------- MP (daily)
def _decode_mp_newsid(raw):
    """mpinfo obfuscates newsid by adding 0x80 to each ASCII char."""
    try:
        return "".join(chr(ord(c) - 0x80) if ord(c) >= 0x80 else c for c in raw or "")
    except Exception:
        return raw or ""


def fetch_mp(day):
    """Madhya Pradesh: one day's releases -- English subset plus full Hindi wire."""
    rows, seen = [], set()
    for font in ("fontenglish", "Mangal"):
        ds = day.strftime("%m/%d/%Y")  # API only accepts MM/DD/YYYY
        url = ("https://www.mpinfo.org/HomePageWebservice.asmx/Todaynews?"
               + urllib.parse.urlencode({"strloc": 32, "fontname": font, "publishdate": ds}))
        for x in _get_json(url):
            raw_id = x.get("newsid", "")
            nid = _decode_mp_newsid(raw_id)
            # English + Hindi feeds share the numeric id; keep one row per id
            key = nid.split("N")[-1] if "N" in nid else nid
            title = re.sub(r"\s+", " ", x.get("NewsTitle") or "").strip()
            if not title or not nid or key in seen:
                continue
            seen.add(key)
            anchor = urllib.parse.quote(f"{x.get('KeyWords') or title}-{raw_id}")
            rows.append({
                "newsid": nid, "date": day.isoformat(), "title": title,
                "category": (x.get("Description") or "").strip(),
                "keywords": (x.get("KeyWords") or "").strip(),
                "url": f"https://www.mpinfo.org/Home/TodaysNews#{anchor}",
            })
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- UP (latest)
_UP_MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
_UP_ROW = re.compile(
    r"<tr>\s*<td>\d+\s*</td>\s*<td>(?P<title>.*?)</td>\s*<td>\s*(?P<d>\d{1,2})/(?P<mon>[A-Za-z]{3})/(?P<y>20\d\d)"
    r".*?href='(?P<pdf>[^']+)'", re.S)


def fetch_up():
    """Uttar Pradesh: latest rows from the CM and departmental press tables."""
    base = "https://information.up.gov.in/"
    rows = []
    for page, cat in (("cm_press_release_details.aspx", "CM press"),
                      ("other_press_release_details.aspx", "Departments")):
        try:
            h = _get(base + page, timeout=90)
        except Exception as e:
            print(f"UP {page}: FETCH FAILED ({e})", file=sys.stderr)
            continue
        for m in _UP_ROW.finditer(h):
            mon = _UP_MONTHS.get(m.group("mon")[:3].title())
            if not mon:
                continue
            date = f"{int(m.group('y')):04d}-{mon:02d}-{int(m.group('d')):02d}"
            title = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", m.group("title")))).strip()
            pdf = urllib.parse.urljoin(base, m.group("pdf").strip())
            if not title:
                continue
            # no stable id on the site -> derive from the PDF filename
            rows.append({"newsid": os.path.basename(urllib.parse.urlparse(pdf).path)[:120] or f"{date}-{hash(title) & 0xffffffff:x}",
                         "date": date, "title": title, "category": cat, "keywords": "", "url": pdf})
        time.sleep(0.5)
    return rows


# ---------------------------------------------------------------- GJ (latest)
def fetch_gujarat():
    """Gujarat: latest releases via the Department-Releases JSON backend.
    English (PressLangId=1) preferred; Gujarati (2) fills the gaps."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    page = _get("https://gujaratinformation.gujarat.gov.in/Department-Releases", opener=opener)
    m = re.search(r'name="AntiforgeryFieldname"[^>]*value="([^"]+)"', page)
    if not m:
        raise RuntimeError("antiforgery token not found")
    token = m.group(1)
    by_press = {}
    for lang in (1, 2):
        data = urllib.parse.urlencode({"PressLangId": lang, "AntiforgeryFieldname": token}).encode()
        items = json.loads(_get("https://gujaratinformation.gujarat.gov.in/BindDepartmentPressRealese",
                                opener=opener, data=data,
                                headers={"Content-Type": "application/x-www-form-urlencoded"}))
        for x in items:
            pid = x.get("pressId")
            if pid is None or (pid in by_press and lang == 2):
                continue  # English row already captured
            title = re.sub(r"\s+", " ", x.get("pressTitle") or "").strip()
            if not title:
                continue
            date = (x.get("pressReleaseDate") or x.get("createdDate") or "")[:10]
            by_press[pid] = {
                "newsid": str(pid), "date": date, "title": title,
                "category": re.sub(r"\s+", " ", x.get("depName") or "").strip(),
                "keywords": (x.get("metaTitle") or "").strip()[:200],
                "url": f"https://gujaratinformation.gujarat.gov.in/Department-Releases#press-{pid}",
            }
        time.sleep(0.5)
    return list(by_press.values())


# ---------------------------------------------------------------- MH (latest)
def fetch_mh():
    """Maharashtra: DGIPR's mahasamvad.in wire is stock WordPress -- the REST API
    returns the full Marathi feed with real publish dates."""
    rows = []
    for page in (1, 2):  # 2 x 100 newest posts covers well over a month
        url = ("https://mahasamvad.in/wp-json/wp/v2/posts?"
               + urllib.parse.urlencode({"per_page": 100, "page": page, "_fields": "id,date,link,title,categories"}))
        try:
            posts = _get_json(url)
        except Exception as e:
            print(f"MH page {page}: FETCH FAILED ({e})", file=sys.stderr)
            break
        for x in posts:
            title = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", x["title"]["rendered"]))).strip()
            if not title:
                continue
            rows.append({"newsid": str(x["id"]), "date": (x.get("date") or "")[:10],
                         "title": title, "category": "DGIPR wire", "keywords": "",
                         "url": x.get("link") or f"https://mahasamvad.in/{x['id']}/"})
        if len(posts) < 100:
            break
        time.sleep(0.5)
    return rows


# ---------------------------------------------------------------- KA (latest)
_KA_ITEM = re.compile(r'href="(https://cm\.karnataka\.gov\.in/(\d+)/([^"]+)/(?:kn|en))"')


def fetch_ka():
    """Karnataka: DIPR's sites are static PDF shelves, but cm.karnataka.gov.in's
    homepage lists the CM office wire -- sequential item ids with English slugs.
    Item pages carry no publish date, so new items are stamped with collection
    date (the homepage only surfaces recent releases)."""
    h = _get("https://cm.karnataka.gov.in/", timeout=60)
    today = datetime.date.today().isoformat()
    rows, seen = [], set()
    for m in _KA_ITEM.finditer(h):
        iid, slug = m.group(2), m.group(3)
        # skip nav/static pages (about-cm, contact-us, download, ...) -- the wire
        # ids are high and slugs are long sentence-like headlines
        if iid in seen or int(iid) < 400 or len(slug) < 25:
            continue
        seen.add(iid)
        title = re.sub(r"\s+", " ", urllib.parse.unquote(slug).replace("-", " ")).strip().capitalize()
        rows.append({"newsid": iid, "date": today, "title": title, "category": "CM office",
                     "keywords": "", "url": m.group(1)})
    return rows


# ---------------------------------------------------------------- GA (latest)
def fetch_goa():
    """Goa: dip.goa.gov.in is stock WordPress -- REST API, mixed English/Marathi."""
    rows = []
    for page in (1, 2):
        url = ("https://dip.goa.gov.in/wp-json/wp/v2/posts?"
               + urllib.parse.urlencode({"per_page": 100, "page": page, "_fields": "id,date,link,title"}))
        try:
            posts = _get_json(url)
        except Exception as e:
            print(f"GA page {page}: FETCH FAILED ({e})", file=sys.stderr)
            break
        for x in posts:
            title = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", x["title"]["rendered"]))).strip()
            if title:
                rows.append({"newsid": str(x["id"]), "date": (x.get("date") or "")[:10],
                             "title": title, "category": "DIP wire", "keywords": "",
                             "url": x.get("link") or ""})
        if len(posts) < 100:
            break
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- RJ (latest)
def fetch_rajasthan(page_size=100, page=1):
    """Rajasthan: DIPR's Angular portal is backed by an open POST JSON API
    (73k+ dated releases). No title field -- derive one from the Description
    HTML body (Hindi). Detail links aren't stable; prefer the row's PDF.
    Paged (date desc) -- backfill_state_news.py walks the full archive."""
    body = json.dumps({"PageSize": page_size, "Page": page, "OrderBy": "PressreleaseDate",
                       "OrderByAsc": 0, "IsBase64File": False, "DepartmentCode": 0}).encode()
    d = json.loads(_get("https://dipr.rajasthan.gov.in/webapi/PublicPortal/DepartmentWebsite/GetDIPRPressReleaseByFilter",
                        data=body, headers={"Content-Type": "application/json"}))
    rows = []
    for x in (d.get("Data") or {}).get("Data", []):
        text = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", x.get("Description") or ""))).strip()
        if not text:
            continue
        url = x.get("PDFUrl") or "https://dipr.rajasthan.gov.in/pages/press-release-list/0"
        rows.append({"newsid": str(x.get("Id")), "date": (x.get("PressreleaseDate") or "")[:10],
                     "title": text[:200], "category": (x.get("DepartmentTitle") or "DIPR wire").strip(),
                     "keywords": (x.get("KeyWords") or "")[:200], "url": url})
    return rows


# ---------------------------------------------------------------- PB (latest)
_PB_ITEM = re.compile(
    r'href="(/en/press-releases/[^"]+)"><p>([^<]{10,250})</p></a>.*?icofont-ui-calendar"></i>([A-Za-z]+ \d{1,2}, 20\d\d)', re.S)


def fetch_punjab():
    """Punjab: ipr.punjab.gov.in English HQ press list, server-rendered HTML."""
    h = _get("https://ipr.punjab.gov.in/en/press-releases/hq-press-releases/", timeout=60)
    rows, seen = [], set()
    for m in _PB_ITEM.finditer(h):
        path, title, ds = m.groups()
        try:
            date = datetime.datetime.strptime(ds, "%B %d, %Y").date().isoformat()
        except ValueError:
            continue
        slug = path.rstrip("/").rsplit("/", 1)[-1][:120]
        if slug in seen:
            continue
        seen.add(slug)
        rows.append({"newsid": slug, "date": date, "title": re.sub(r"[*\s]+", " ", title).strip(),
                     "category": "HQ press", "keywords": "",
                     "url": "https://ipr.punjab.gov.in" + path})
    return rows


# ---------------------------------------------------------------- MZ (latest)
_MZ_ITEM = re.compile(
    r'<a href="(/post/[^"]+)"[^>]*title="([^"]{10,250})".*?Dated:\s*(\d{1,2})<sup>[a-z]{2}</sup>\s+([A-Za-z]{3})\s+(\d{2})\b', re.S)


def fetch_mizoram():
    """Mizoram: DIPR English press-release category, server-rendered HTML."""
    rows = []
    for page in (1, 2):
        h = _get(f"https://dipr.mizoram.gov.in/category/english-press-releases?page={page}", timeout=45)
        for m in _MZ_ITEM.finditer(h):
            path, title, dd, mon, yy = m.groups()
            mth = _UP_MONTHS.get(mon.title())
            if not mth:
                continue
            date = f"20{yy}-{mth:02d}-{int(dd):02d}"
            rows.append({"newsid": path.rsplit("/", 1)[-1][:120], "date": date,
                         "title": _html.unescape(title).strip(), "category": "DIPR English",
                         "keywords": "", "url": "https://dipr.mizoram.gov.in" + path})
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- NL (latest)
_NL_ITEM = re.compile(
    r'<h2 class="entry-title[^"]*">\s*<a href="(/[^"]+)"[^>]*>([^<]{10,250})</a>\s*</h2>.*?<time datetime="([A-Za-z]{3} \d{1,2} 20\d\d)"', re.S)


def fetch_nagaland():
    """Nagaland: IPR /naga-news Drupal view, server-rendered, 6 items/page."""
    rows = []
    for page in range(4):  # 0-based; 4 pages = 24 newest items
        h = _get(f"https://ipr.nagaland.gov.in/naga-news?page={page}", timeout=45)
        for m in _NL_ITEM.finditer(h):
            path, title, ds = m.groups()
            try:
                date = datetime.datetime.strptime(ds, "%b %d %Y").date().isoformat()
            except ValueError:
                continue
            rows.append({"newsid": path.strip("/")[:120], "date": date,
                         "title": _html.unescape(title).strip().title() if title.isupper() else _html.unescape(title).strip(),
                         "category": "Naga News", "keywords": "",
                         "url": "https://ipr.nagaland.gov.in" + path})
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- SK (latest)
_SK_ITEM = re.compile(
    r'<h2 class="text-lg font-semibold">([^<]{5,250})</h2>\s*<p[^>]*>Published on:\s*(\d{1,2} [A-Za-z]{3} 20\d\d)</p>.*?href="(/press_releases/[^"]+)"', re.S)


def fetch_sikkim():
    """Sikkim: IPR ASP.NET Core press list; dedupe on the PDF GUID (slugs repeat)."""
    rows, seen = [], set()
    for page in (1, 2, 3):
        h = _get(f"https://ipr.sikkim.gov.in/Home/PressReleasesList?page={page}", timeout=45)
        for m in _SK_ITEM.finditer(h):
            title, ds, pdf = m.groups()
            guid = pdf.split("/")[-1].split("_")[0][:60]
            if guid in seen:
                continue
            seen.add(guid)
            try:
                date = datetime.datetime.strptime(ds, "%d %b %Y").date().isoformat()
            except ValueError:
                continue
            rows.append({"newsid": guid, "date": date, "title": _html.unescape(title).strip(),
                         "category": "IPR", "keywords": "",
                         "url": "https://ipr.sikkim.gov.in" + urllib.parse.quote(pdf)})
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- CH (latest)
_CH_ROW = re.compile(
    r'<tr>\s*<td>\d+</td>\s*<td><a href="(https://chandigarh\.gov\.in/cadmin//uploads/[^"]+)"[^>]*>\s*([^<]{5,250})</a></td>\s*<td>([^<]*)</td>\s*<td>\s*(\d{2}/\d{2}/20\d\d)', re.S)


def fetch_chandigarh():
    """Chandigarh UT: /public-notice press table, all rows in one response."""
    h = _get("https://chandigarh.gov.in/public-notice", timeout=45)
    rows = []
    for m in _CH_ROW.finditer(h):
        pdf, title, dept, ds = m.groups()
        d, mth, y = ds.split("/")
        rows.append({"newsid": pdf.rsplit("/", 1)[-1].split(".")[0][:80],
                     "date": f"{y}-{mth}-{d}", "title": re.sub(r"\s+", " ", _html.unescape(title)).strip(),
                     "category": re.sub(r"\s+", " ", dept).strip() or "Administration",
                     "keywords": "", "url": pdf})
    return rows


# ---------------------------------------------------------------- DD (latest)
_DD_ROW = re.compile(
    r'<td role="rowheader"[^>]*>([^<]{5,250})</td>\s*<td>\s*(\d{2}/\d{2}/20\d\d)</td>.*?href="(https://cdnbbsr\.s3waas\.gov\.in/[^"]+)"', re.S)


def fetch_dnh_dd():
    """Dadra NH & Daman Diu UT: latest-updates document category (S3WaaS table)."""
    rows = []
    for page in ("", "page/2/"):
        h = _get(f"https://ddd.gov.in/document-category/latest-updates/{page}", timeout=45)
        for m in _DD_ROW.finditer(h):
            title, ds, pdf = m.groups()
            d, mth, y = ds.split("/")
            rows.append({"newsid": pdf.rsplit("/", 1)[-1].split(".")[0][:80],
                         "date": f"{y}-{mth}-{d}", "title": re.sub(r"\s+", " ", _html.unescape(title)).strip(),
                         "category": "Latest updates", "keywords": "", "url": pdf})
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- KL (latest)
_KL_ITEM = re.compile(
    r'<time datetime="(20\d\d-\d\d-\d\d)T[^"]*"[^>]*>.*?<div class="post-title">\s*<a href="([^"]+)"[^>]*>([^<]{5,300})</a>', re.S)


def fetch_kerala():
    """Kerala: PRD Drupal press-release view (Malayalam titles). Bare ?page=N is
    ignored unless the full exposed-filter query string is present."""
    rows = []
    for page in range(3):
        h = _get(f"https://prd.kerala.gov.in/ml/pressrelease?tid=All&field_date_value=&page={page}", timeout=45)
        for m in _KL_ITEM.finditer(h):
            date, path, title = m.groups()
            path = path.replace("/index.php", "")
            nid = path.rstrip("/").rsplit("/", 1)[-1][:60]
            rows.append({"newsid": nid, "date": date, "title": _html.unescape(title).strip(),
                         "category": "PRD", "keywords": "",
                         "url": "https://prd.kerala.gov.in" + path})
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- TS (latest)
_TS_RSS = re.compile(r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>", re.S)


def fetch_telangana():
    """Telangana: ipr.telangana.gov.in is a stale static site; the live wire is
    the state portal's WordPress RSS (REST API is auth-blocked)."""
    h = _get("https://www.telangana.gov.in/category/news/press-releases/feed/", timeout=45)
    rows = []
    for m in _TS_RSS.finditer(h):
        title, link, pd = (re.sub(r"<!\[CDATA\[|\]\]>", "", g).strip() for g in m.groups())
        try:
            date = datetime.datetime.strptime(pd[:16].strip(), "%a, %d %b %Y").date().isoformat()
        except ValueError:
            m2 = re.search(r"/(20\d\d)/(\d\d)/", link)
            date = f"{m2.group(1)}-{m2.group(2)}-01" if m2 else datetime.date.today().isoformat()
        nid = re.sub(r"[^a-z0-9%-]", "", urllib.parse.urlparse(link).path.rstrip("/").rsplit("/", 1)[-1].lower())[:110]
        if title and nid:
            rows.append({"newsid": nid, "date": date, "title": _html.unescape(title),
                         "category": "State portal", "keywords": "", "url": link})
    return rows


# ---------------------------------------------------------------- AS (latest)
_AS_ROW = re.compile(r'<tr><td>(.*?)</td><td>.*?</td><td><a class="file-default" href="([^"]+)"', re.S)


def fetch_assam():
    """Assam: DIPR's curated current list (~14 rows, no date column -- dates are
    regex-extracted from the title text in whatever format the operator used)."""
    h = _get("https://dipr.assam.gov.in/portlets/press-release", timeout=45)
    rows = []
    for m in _AS_ROW.finditer(h):
        title = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()
        url = m.group(2)
        dm = (re.search(r"\b(\d{1,2})[/.](\d{1,2})[/.](20\d\d|\d\d)\b", title)
              or re.search(r"\b(\d{1,2})\s+([A-Za-z]+),?\s+(20\d\d)\b", title))
        date = None
        if dm:
            a, b, y = dm.groups()
            y = int(y) + (2000 if int(y) < 100 else 0)
            mth = int(b) if b.isdigit() else _UP_MONTHS.get(b[:3].title())
            if mth and 1 <= mth <= 12:
                date = f"{y:04d}-{mth:02d}-{min(int(a), 31):02d}"
        if not title:
            continue
        rows.append({"newsid": url.rsplit("/", 1)[-1][:120],
                     "date": date or datetime.date.today().isoformat(),
                     "title": title, "category": "DIPR", "keywords": "", "url": url})
    return rows


# ---------------------------------------------------------------- AP (latest)
def fetch_ap():
    """Andhra Pradesh: the official state portal (ap.gov.in, plain Angular REST
    API at /api/api/) publishes both curated announcements and a news-clipping
    wire, no auth. NOTE: ipr.ap.gov.in (a *different* AP site) gates its API
    behind an RSA+AES-GCM+HMAC request-signing scheme that is a deliberate
    anti-automation mechanism -- deliberately NOT implemented here; this
    fetcher uses the legitimate open endpoint instead."""
    rows = []
    for endpoint, category in (("ApNewsLatestAnnouncements", "News wire"),
                               ("ApNewsAnnouncements", "Announcements")):
        try:
            d = _get_json(f"https://www.ap.gov.in/api/api/{endpoint}", timeout=30)
        except Exception as e:
            print(f"AP {endpoint}: FETCH FAILED ({e})", file=sys.stderr)
            continue
        for x in d.get("dataList") or []:
            title = re.sub(r"\s+", " ", x.get("title") or "").strip()
            date = (x.get("from") or "")[:10]
            if not title or not date:
                continue
            url = x.get("url") or x.get("imageBase64") or "https://www.ap.gov.in/"
            rows.append({"newsid": f"{endpoint}-{x.get('id')}", "date": date,
                         "title": title, "category": category, "keywords": "", "url": url})
    return rows


SOURCES = {
    "MP": {"state": "Madhya Pradesh", "mode": "daily", "fetch": fetch_mp},
    "AP": {"state": "Andhra Pradesh", "mode": "latest", "fetch": fetch_ap},
    "UP": {"state": "Uttar Pradesh", "mode": "latest", "fetch": fetch_up},
    "GJ": {"state": "Gujarat", "mode": "latest", "fetch": fetch_gujarat},
    "MH": {"state": "Maharashtra", "mode": "latest", "fetch": fetch_mh},
    "KA": {"state": "Karnataka", "mode": "latest", "fetch": fetch_ka},
    "GA": {"state": "Goa", "mode": "latest", "fetch": fetch_goa},
    "RJ": {"state": "Rajasthan", "mode": "latest", "fetch": fetch_rajasthan},
    "PB": {"state": "Punjab", "mode": "latest", "fetch": fetch_punjab},
    "MZ": {"state": "Mizoram", "mode": "latest", "fetch": fetch_mizoram},
    "NL": {"state": "Nagaland", "mode": "latest", "fetch": fetch_nagaland},
    "SK": {"state": "Sikkim", "mode": "latest", "fetch": fetch_sikkim},
    "CH": {"state": "Chandigarh", "mode": "latest", "fetch": fetch_chandigarh},
    "DD": {"state": "DNH & Daman-Diu", "mode": "latest", "fetch": fetch_dnh_dd},
    "KL": {"state": "Kerala", "mode": "latest", "fetch": fetch_kerala},
    "TS": {"state": "Telangana", "mode": "latest", "fetch": fetch_telangana},
    "AS": {"state": "Assam", "mode": "latest", "fetch": fetch_assam},
    # Dead ends (probed 2026-08-02, see docs/STATE_SOURCES.md): CG WAF-blocks
    # curl; OD archive stale since 2023; WB page stale + North-Bengal-only;
    # UK stale since mid-2025; AP ipr.ap.gov.in needs an RSA+AES-GCM+HMAC
    # handshake (protocol documented in STATE_SOURCES.md — needs `cryptography`,
    # deliberately out of scope for this stdlib-only collector).
}


def ensure_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB, timeout=60)
    con.execute("pragma journal_mode=DELETE")
    con.execute("pragma busy_timeout=60000")  # collector + signal pass may overlap
    con.execute("""create table if not exists state_news(
        state text not null, newsid text not null, date text not null,
        title text not null, category text, keywords text, url text,
        fetched_at text not null, primary key(state, newsid))""")
    cols = [r[1] for r in con.execute("pragma table_info(state_news)")]
    if "title_en" not in cols:
        con.execute("alter table state_news add column title_en text")
    con.execute("create index if not exists ix_state_news_date on state_news(date)")
    return con


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14, help="lookback for daily-mode sources")
    ap.add_argument("--state", default=None, help="restrict to one source code (e.g. MP)")
    ap.add_argument("--no-translate", action="store_true", help="skip machine translation")
    a = ap.parse_args()
    con = ensure_db()
    today = datetime.date.today()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for code, src in SOURCES.items():
        if a.state and code != a.state.upper():
            continue
        batches = []
        if src["mode"] == "daily":
            for back in range(a.days):
                day = today - datetime.timedelta(days=back)
                try:
                    batches.append(src["fetch"](day))
                except Exception as e:
                    print(f"{code} {day}: FETCH FAILED ({e})", file=sys.stderr)
                time.sleep(0.4)
        else:
            try:
                batches.append(src["fetch"]())
            except Exception as e:
                print(f"{code}: FETCH FAILED ({e})", file=sys.stderr)
        total = new = translated = 0
        for rows in batches:
            total += len(rows)
            for r in rows:
                exists = con.execute("select 1 from state_news where state=? and newsid=?",
                                     (code, r["newsid"])).fetchone()
                if exists:
                    continue
                title_en = r["title"] if _is_english(r["title"]) else None
                if title_en is None and not a.no_translate:
                    title_en = translate_en(r["title"])
                    translated += bool(title_en)
                with con:
                    con.execute(
                        "insert or ignore into state_news(state,newsid,date,title,title_en,category,keywords,url,fetched_at)"
                        " values(?,?,?,?,?,?,?,?,?)",
                        (code, r["newsid"], r["date"], r["title"], title_en,
                         r["category"], r["keywords"], r["url"], now))
                    new += 1
        n_all = con.execute("select count(*) from state_news where state=?", (code,)).fetchone()[0]
        print(f"{code} ({src['state']}): fetched {total}, {new} new ({translated} machine-translated) -> {n_all} total in register")
    # backfill translations for rows collected before title_en existed
    if not a.no_translate:
        back = con.execute("select state, newsid, title from state_news where title_en is null").fetchall()
        done = 0
        for state, nid, title in back:
            t = title if _is_english(title) else translate_en(title)
            if t:
                with con:
                    con.execute("update state_news set title_en=? where state=? and newsid=?", (t, state, nid))
                done += 1
        if back:
            print(f"backfill: {done}/{len(back)} rows gained title_en")


if __name__ == "__main__":
    main()
