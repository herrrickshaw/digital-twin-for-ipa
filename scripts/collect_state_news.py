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
import argparse, datetime, html as _html, http.cookiejar, json, os, re, sqlite3, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data/registers/state_news.sqlite")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def _get(url, timeout=45, opener=None, data=None, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs)
    op = opener.open if opener else urllib.request.urlopen
    with op(req, timeout=timeout) as r:
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


SOURCES = {
    "MP": {"state": "Madhya Pradesh", "mode": "daily", "fetch": fetch_mp},
    "UP": {"state": "Uttar Pradesh", "mode": "latest", "fetch": fetch_up},
    "GJ": {"state": "Gujarat", "mode": "latest", "fetch": fetch_gujarat},
    # Candidate next states (probed 2026-08-02, see docs/STATE_SOURCES.md):
    # MH mahasamvad.in / dgipr.maharashtra.gov.in, KA karnatakavarthe.org,
    # RJ dipr.rajasthan.gov.in, TS ipr.telangana.gov.in, AS dipr.assam.gov.in,
    # WB wb.gov.in/press-release.aspx
}


def ensure_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("pragma journal_mode=DELETE")
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
