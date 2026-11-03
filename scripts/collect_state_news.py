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
  TN  -- dipr.tn.gov.in (Tamil Nadu DIPR). The public press-release page is a
         static HTML shell (press-release1.html) whose table is populated by
         client-side JS calling a JSON API: GET /dipr_api/v1/general/
         pressReleases/{press_release,press_notes}. The API 404s with
         {"success":0,"message":"APP Key Missing"} unless two static headers
         (X-App-Key: dipr, X-App-Name: dipr -- applied to every request via
         global $.ajaxSetup(), not a real auth scheme) are sent; discovered by
         reading assets/js/global.js and assets/js/apiConfig.js off the page.
         press_release returns a rolling ~10-day window (CM/dept statements,
         PDF links); press_notes returns the full history since 2023 (minister
         press-meet notes). newsid = "{endpoint prefix}{id}" to keep the two
         tables' id spaces from colliding.
  BR  -- state.bihar.gov.in/prdbihar (IPRD portal, Java/Undertow backend).
         Latest rows scraped from the "IPRD PRESS RELEASE 2026"
         SectionInformation.html?rowId=8931 HTML table (Hindi subjects, PR
         No, date, per-row JS-triggered PDF download). Session cookie is
         required first (home page bootstrap), then each row's download is
         resolved via a POST to SectionInformation.html?Download carrying a
         CSRF token, whose response JS redirects to the real cache/ PDF path
         -- same two-step pattern as GJ's antiforgery flow, plus one extra
         POST+GET per row to land on the actual PDF url. Site serves an
         incomplete cert chain -- since this flow needs a cookie-carrying
         opener, the opener itself is built with an unverified SSL context
         rather than relying on _get()'s no-opener-only unverified-retry.
  OD  -- cm.odisha.gov.in (Chief Minister's Office). IPR department's own site
         (inpr.odisha.gov.in) has no live press-release feed -- its "News"
         view is empty and its "News Archives" table is dated administrative
         notices/tenders, stalest at ~9 months old. The CM's office site is a
         Drupal 9/10 (theme "unee") site with a genuinely live English wire at
         /en/news-updates -- plain GET-paginated (?page=N), no AJAX/JS needed.
  HR  -- prms.prharyana.gov.in (Press Release Management System, Directorate
         of Information Public Relations & Languages). The public listing
         GET /press-release/?Language=English server-renders ~100 latest
         English titles. Detail pages carry a real "Posted On" date but are
         ~7MB/~35-40s each, so -- like KA -- items are stamped with the
         collection date instead.
  DL  -- Delhi (NCT). The real target -- DIP's own wire, publicity.delhi.gov.in
         /press-releases -- is CONFIRMED DEAD (frozen on May-2017 content
         behind a stale "changed" timestamp). Falls back to delhi.gov.in
         /notice-board/notifications: same GNCTD Drupal family, genuinely
         dated PDF notices, but only ~7 rows and administrative in flavour
         (empanelment notices, compliance circulars) rather than a curated
         scheme-announcement wire like MP/UP/GJ -- weaker source, kept
         because it's the only genuinely live official GNCTD content found.
  WB  -- icad.wb.gov.in (Information & Cultural Affairs Dept). No dedicated
         press-release feed exists (wb.gov.in's media-center-latest-news.aspx
         is dead since 2023; cm.wb.gov.in/wbcmo.gov.in are simply unreachable
         -- confirmed 2026-08-24, both time out while every other .gov.in
         source connects fine, so this looks like a genuinely down server).
         The department's own Notice board (notice.php) and Govt Order board
         (govt-order.php) are current instead -- plain HTML tables, but
         admin-flavoured (recruitment/transfer/circulars) rather than a
         scheme-announcement wire, same caveat as DL.

Some govt sites intermittently fail the TLS handshake itself against Python's
default fingerprint (confirmed on TS and WB, different failure modes each
time) -- not a cert problem, plain urllib has no retry path for it. _get()
falls back to Scrapling's Fetcher (curl_cffi, real-browser TLS fingerprint)
for plain GETs when this happens; `pip install scrapling[fetchers]` into
scripts/requirements-state-news.txt's venv if setting this up fresh.

Usage:  python3 scripts/collect_state_news.py [--days 14] [--state MP] [--no-translate]
Rerun daily (idempotent -- INSERT OR IGNORE on (state, newsid)).
"""
import argparse, datetime, os, sqlite3, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data/registers/state_news.sqlite")

# Fetchers live in scripts/state_sources/; re-exported so `from collect_state_news import fetch_mp, ...` still works.
from state_sources.net import UA, _decode_mp_newsid, _get, _get_json, _is_english, translate_en  # noqa: E402,F401
from state_sources.fetchers_a import (  # noqa: E402,F401
    fetch_assam, fetch_chandigarh, fetch_dnh_dd, fetch_goa, fetch_gujarat, fetch_ka, fetch_kerala, fetch_mh,
    fetch_mizoram, fetch_mp, fetch_nagaland, fetch_punjab, fetch_rajasthan, fetch_sikkim, fetch_telangana, fetch_up)
from state_sources.fetchers_b import (  # noqa: E402,F401
    fetch_ap, fetch_bihar, fetch_delhi, fetch_haryana, fetch_odisha, fetch_tamil_nadu, fetch_west_bengal)


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
    "TN": {"state": "Tamil Nadu", "mode": "latest", "fetch": fetch_tamil_nadu},
    "BR": {"state": "Bihar", "mode": "latest", "fetch": fetch_bihar},
    "OD": {"state": "Odisha", "mode": "latest", "fetch": fetch_odisha},
    "HR": {"state": "Haryana", "mode": "latest", "fetch": fetch_haryana},
    "DL": {"state": "Delhi (NCT)", "mode": "latest", "fetch": fetch_delhi},
    "WB": {"state": "West Bengal", "mode": "latest", "fetch": fetch_west_bengal},
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
