"""State fetchers, part 2 (AP, TN, BR, OD, HR, DL, WB)."""
import datetime, html as _html, http.cookiejar, os, re, ssl, sys, time, urllib.error, urllib.parse, urllib.request

from state_sources.net import _get, _get_json



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


# ---------------------------------------------------------------- TN (latest)
_TN_API = "https://dipr.tn.gov.in/dipr_api/v1"
_TN_HEADERS = {"X-App-Key": "dipr", "X-App-Name": "dipr", "Accept": "application/json, text/plain, */*"}
_TN_ENDPOINTS = (
    ("press_release", "pr", "Press Release"),   # rolling ~10-day CM/dept statement wire
    ("press_notes", "pn", "Press Note"),        # full history since 2023, minister press-meet notes
)


def fetch_tamil_nadu():
    """Tamil Nadu: dipr.tn.gov.in's public press-release page is a static HTML
    shell whose table is filled client-side from a JSON API. The API 404s with
    {"success":0,"message":"APP Key Missing"} unless two static headers
    (X-App-Key/X-App-Name: dipr -- applied to every page request via a global
    $.ajaxSetup(), not real auth) are sent, found by reading assets/js/global.js.
    Pulls both press_release (rolling ~10-day window) and press_notes (full
    2023-> history) endpoints; title is derived from the PDF filename since
    there's no separate title field."""
    rows = []
    for endpoint, prefix, category in _TN_ENDPOINTS:
        url = f"{_TN_API}/general/pressReleases/{endpoint}"
        try:
            d = _get_json(url, timeout=30, headers=_TN_HEADERS)
        except Exception as e:
            print(f"TN {endpoint}: FETCH FAILED ({e})", file=sys.stderr)
            continue
        if d.get("success") != 1:
            print(f"TN {endpoint}: unexpected response ({d.get('message')})", file=sys.stderr)
            continue
        for x in d.get("data") or []:
            date = (x.get("pr_date") or x.get("uploaded_date") or "")[:10]
            fname = (x.get("press_name") or "").strip()
            title = re.sub(r"\.pdf$", "", fname, flags=re.I)
            title = re.sub(r"[_\s]+", " ", title).strip(" -")
            title = _html.unescape(title)
            file_path = x.get("press_file_name") or ""
            if not title or not x.get("id") or not file_path:
                continue
            url_full = _TN_API + urllib.parse.quote(urllib.parse.unquote(file_path))
            rows.append({
                "newsid": f"{prefix}{x['id']}", "date": date, "title": title,
                "category": category, "keywords": "", "url": url_full,
            })
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- BR (latest)
_BR_ROW = re.compile(
    r'<td class="text-center">(?P<sr>\d+)</td>\s*'
    r'<td>(?P<prno>\d+)</td>\s*'
    r'<td>(?P<subject>.*?)</td>\s*'
    r'<td class="text-center">(?P<date>\d{2}/\d{2}/\d{4})</td>.*?'
    r"downloadFile\('(?P<path>[^']+)'",
    re.S)
_BR_CSRF = re.compile(r'<meta name="_csrf" content="([^"]+)"')
_BR_RESOLVED = re.compile(r"window\.open\('\./?(cache/[^']+)'")

_BR_BASE = "https://state.bihar.gov.in/prdbihar/"
_BR_PRESS_PAGE = _BR_BASE + "SectionInformation.html?editForm&rowId=8931"  # IPRD PRESS RELEASE (current year)
_BR_DOWNLOAD_EP = _BR_BASE + "SectionInformation.html?Download"


def fetch_bihar(limit=30):
    """Bihar: IPRD's state.bihar.gov.in/prdbihar Java/Undertow portal. The
    'IPRD PRESS RELEASE 2026' section (rowId=8931) is a plain HTML table
    (Hindi subjects, PR No, dd/mm/yyyy date) covering the whole year --
    only the newest `limit` rows are kept per run. Each row's PDF is behind
    a JS-triggered POST (CSRF token + session cookie) whose response embeds
    the real cache/ path via window.open(); resolved here with one extra
    POST + one extra GET per row so the stored url is a genuine, directly
    fetchable PDF rather than a JS-only trigger."""
    # state.bihar.gov.in serves an incomplete cert chain (confirmed via
    # `curl -k` -- not a TLS-fingerprint block like telangana.gov.in). The
    # shared _get() deliberately does NOT retry-unverified for opener-based
    # (session/cookie) calls, so build the unverified context into the
    # opener itself here rather than relying on _get()'s fallback path.
    cj = http.cookiejar.CookieJar()
    ctx = ssl._create_unverified_context()
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(cj))
    # bootstrap: the home page must be hit first to get a session cookie --
    # requesting SectionInformation.html cold 302s back to CitizenHome.html
    _get(_BR_BASE, timeout=45, opener=opener)
    page = _get(_BR_PRESS_PAGE, timeout=45, opener=opener)
    m = _BR_CSRF.search(page)
    if not m:
        raise RuntimeError("bihar: csrf token not found on press-release page")
    csrf = m.group(1)

    rows = []
    for rm in list(_BR_ROW.finditer(page))[:limit]:
        prno = rm.group("prno")
        subject = re.sub(r"\s+", " ", _html.unescape(rm.group("subject"))).strip()
        d, mth, y = rm.group("date").split("/")
        date = f"{y}-{mth}-{d}"
        path = rm.group("path")
        if not subject:
            continue

        # resolve the real PDF url: POST the download trigger, then parse
        # the tiny JS-redirect response for the actual cache/ path
        url = _BR_PRESS_PAGE + f"#PR{prno}"  # fallback if resolution fails
        try:
            body = urllib.parse.urlencode({"downloadLink": path, "_csrf": csrf}).encode()
            resolved = _get(_BR_DOWNLOAD_EP, timeout=30, opener=opener, data=body,
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
            rm2 = _BR_RESOLVED.search(resolved)
            if rm2:
                url = _BR_BASE + urllib.parse.quote(rm2.group(1))
        except Exception as e:
            print(f"BR PR{prno}: resolve failed ({e}), using page anchor", file=sys.stderr)
        time.sleep(0.2)

        rows.append({
            "newsid": f"PR{prno}", "date": date, "title": subject,
            "category": "IPRD press release", "keywords": "", "url": url,
        })
    return rows


# ---------------------------------------------------------------- OD (latest)
_OD_ITEM = re.compile(
    r'<a href="(/en/latest-news/[^"]+)"[^>]*class="text-decoration-none">\s*<h2[^>]*>(.*?)</h2>\s*</a>\s*'
    r'<div class="date mb-2 text-muted small">\s*<i[^>]*></i>\s*([A-Za-z0-9, ]+?)\s*</div>', re.S)


def fetch_odisha():
    """Odisha: CM office's live English wire, plain GET-paginated Drupal view.
    IPR department's own site (inpr.odisha.gov.in) has no live press-release
    feed -- its "News" view is empty and its "News Archives" table is dated
    administrative notices/tenders, stalest at ~9 months old. cm.odisha.gov.in
    is a Drupal 9/10 (theme "unee") site with a genuinely live English wire at
    /en/news-updates. Titles are server-side trimmed by the Views formatter
    (ends in "…" past ~100 chars); full title lives at the detail page's
    <title> but is not fetched per-item to keep this one request per page."""
    rows, seen = [], set()
    for page in range(3):  # 0-based; 3 pages comfortably covers the last ~2-3 weeks
        h = _get(f"https://cm.odisha.gov.in/en/news-updates?page={page}", timeout=45)
        for m in _OD_ITEM.finditer(h):
            path, title, ds = m.groups()
            nid = path.rstrip("/").rsplit("/", 1)[-1][:120]
            if nid in seen:
                continue
            seen.add(nid)
            try:
                date = datetime.datetime.strptime(ds.strip(), "%d %b, %Y").date().isoformat()
            except ValueError:
                continue
            rows.append({"newsid": nid, "date": date,
                         "title": re.sub(r"\s+", " ", _html.unescape(title)).strip(),
                         "category": "CMO wire", "keywords": "",
                         "url": "https://cm.odisha.gov.in" + path})
        time.sleep(0.4)
    return rows


# ---------------------------------------------------------------- HR (latest)
_HR_ITEM = re.compile(
    r'href="https://prms\.prharyana\.gov\.in/press-release/(\d+)"\s+class="a-size">(.*?)</a>', re.S)


def fetch_haryana():
    """Haryana: PRMS (Press Release Management System) English-filtered listing
    -- ~100 latest titles, server-rendered HTML, no date on the list page.
    Detail pages do carry a real "Posted On" date but are ~7MB/~35-40s each
    (confirmed live), so -- like fetch_ka() -- rows are stamped with the
    collection date instead of one detail-page fetch per row."""
    h = _get("https://prms.prharyana.gov.in/press-release/?Language=English", timeout=45)
    today = datetime.date.today().isoformat()
    rows, seen = [], set()
    for m in _HR_ITEM.finditer(h):
        nid, raw_title = m.groups()
        if nid in seen:
            continue
        seen.add(nid)
        title = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", raw_title))).strip()
        title = title.strip("*").strip()
        if not title:
            continue
        rows.append({
            "newsid": nid, "date": today, "title": title, "category": "PRMS",
            "keywords": "", "url": f"https://prms.prharyana.gov.in/press-release/{nid}",
        })
    return rows


# ---------------------------------------------------------------- DL (latest)
_DL_ITEM = re.compile(
    r'<div class="tab-title">\s*(?P<title>.*?)\s*<div>\s*<div class="tab-date">Date\s*:\s*'
    r'(?P<d>\d{2})-(?P<m>\d{2})-(?P<y>\d{4}).*?href="(?P<url>[^"]+)"', re.S)


def fetch_delhi():
    """Delhi (NCT): GNCTD notice-board notifications (Drupal list, dated PDFs).
    The proper DIP press-release wire (publicity.delhi.gov.in/press-releases) is
    dead -- frozen on May-2017 content behind a stale "changed" timestamp -- so
    this uses the parent delhi.gov.in portal's live Notifications view instead.
    Weaker source than MP/UP/GJ: only ~7 rows, skews administrative
    (empanelment notices, compliance circulars) rather than a curated
    scheme-announcement wire -- kept because it's the only genuinely live,
    dated, official GNCTD content found matching this collector's model."""
    base = "https://delhi.gov.in"
    h = _get(base + "/notice-board/notifications", timeout=45)
    rows = []
    for m in _DL_ITEM.finditer(h):
        title = re.sub(r"\s+", " ", _html.unescape(m.group("title"))).strip()
        if not title:
            continue
        date = f"{m.group('y')}-{m.group('m')}-{m.group('d')}"
        url = urllib.parse.urljoin(base, m.group("url").strip())
        newsid = os.path.basename(urllib.parse.urlparse(url).path)[:120] or f"{date}-{hash(title) & 0xffffffff:x}"
        rows.append({
            "newsid": newsid, "date": date, "title": title,
            "category": "GNCTD Notifications", "keywords": "", "url": url,
        })
    return rows


# ---------------------------------------------------------------- WB (latest)
_WB_ROW = re.compile(
    r'<tr>\s*<td><a href="(?P<href>[^"]+)"[^>]*>(?P<title>[^<]{1,300})</a></td>\s*'
    r'<td>(?P<d>\d{2})-(?P<m>\d{2})-(?P<y>\d{4})</td>', re.S)


def fetch_west_bengal():
    """West Bengal: icad.wb.gov.in (I&CA Dept) Notice + Govt Order boards --
    plain server-rendered HTML tables, no auth/JS. wb.gov.in's own media-center
    feed has been dead since 2023, and cm.wb.gov.in/wbcmo.gov.in are simply
    unreachable (confirmed 2026-08-24, both time out while every other
    .gov.in source connects fine -- looks like a genuinely down server, not a
    TLS/geo block). Weaker source than MP/UP/GJ: admin Notice/GO board, not a
    curated scheme/investment wire -- content skews toward recruitment
    notices, transfer orders and departmental circulars, with occasional
    cultural-scheme items."""
    base = "https://icad.wb.gov.in/"
    rows, seen = [], set()
    for page, cat in (("notice.php", "Notice"), ("govt-order.php", "Government Order")):
        try:
            h = _get(base + page, timeout=45)
        except Exception as e:
            print(f"WB {page}: FETCH FAILED ({e})", file=sys.stderr)
            continue
        for m in _WB_ROW.finditer(h):
            title = re.sub(r"\s+", " ", _html.unescape(m.group("title"))).strip()
            if not title:
                continue
            date = f"{m.group('y')}-{m.group('m')}-{m.group('d')}"
            href = urllib.parse.urljoin(base, m.group("href").strip())
            nid = os.path.basename(urllib.parse.urlparse(href).path)[:120] or f"{date}-{hash(title) & 0xffffffff:x}"
            if nid in seen:
                continue
            seen.add(nid)
            rows.append({"newsid": nid, "date": date, "title": title,
                         "category": cat, "keywords": "", "url": href})
        time.sleep(0.4)
    return rows
