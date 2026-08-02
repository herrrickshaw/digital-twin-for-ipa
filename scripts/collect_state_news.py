#!/usr/bin/env python3
"""State-government news wire -> data/registers/state_news.sqlite.

Counterpart to the central PIB register: pulls daily press releases from state
information-department sites and stores them in one dedup'd register so the
reportage views can show state-level scheme announcements next to PIB ones.

Sources (extensible via SOURCES):
  MP  -- mpinfo.org (Madhya Pradesh Jansampark). AngularJS front-end, but the
         backing webservice is an open GET JSON API:
           /HomePageWebservice.asmx/Todaynews?strloc=32&fontname=fontenglish
                                             &publishdate=MM/DD/YYYY
         fontname=fontenglish -> English releases, Mangal -> Hindi. The newsid
         field is char-shifted by +0x80 ("²°²¶..." -> "20260731N409"); decoded
         id keeps the publish date. Deep link = /Home/TodaysNews#<KeyWords>-<raw id>.

Usage:  python3 scripts/collect_state_news.py [--days 14] [--state MP]
Rerun daily (idempotent -- INSERT OR IGNORE on (state, newsid)).
"""
import argparse, datetime, json, os, re, sqlite3, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data/registers/state_news.sqlite")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def _get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _decode_mp_newsid(raw):
    """mpinfo obfuscates newsid by adding 0x80 to each ASCII char."""
    try:
        return "".join(chr(ord(c) - 0x80) if ord(c) >= 0x80 else c for c in raw or "")
    except Exception:
        return raw or ""


def fetch_mp(day):
    """Madhya Pradesh: one day's English releases from the Todaynews webservice."""
    ds = day.strftime("%m/%d/%Y")  # API only accepts MM/DD/YYYY
    url = ("https://www.mpinfo.org/HomePageWebservice.asmx/Todaynews?"
           + urllib.parse.urlencode({"strloc": 32, "fontname": "fontenglish", "publishdate": ds}))
    rows = []
    for x in _get_json(url):
        raw_id = x.get("newsid", "")
        nid = _decode_mp_newsid(raw_id)
        title = re.sub(r"\s+", " ", x.get("NewsTitle") or "").strip()
        if not title or not nid:
            continue
        anchor = urllib.parse.quote(f"{x.get('KeyWords') or title}-{raw_id}")
        rows.append({
            "newsid": nid,
            "date": day.isoformat(),
            "title": title,
            "category": (x.get("Description") or "").strip(),
            "keywords": (x.get("KeyWords") or "").strip(),
            "url": f"https://www.mpinfo.org/Home/TodaysNews#{anchor}",
        })
    return rows


SOURCES = {
    "MP": {"state": "Madhya Pradesh", "fetch": fetch_mp},
    # add more states here: {"state": ..., "fetch": callable(day) -> [row dicts]}
}


def ensure_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("pragma journal_mode=DELETE")
    con.execute("""create table if not exists state_news(
        state text not null, newsid text not null, date text not null,
        title text not null, category text, keywords text, url text,
        fetched_at text not null, primary key(state, newsid))""")
    con.execute("create index if not exists ix_state_news_date on state_news(date)")
    return con


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14, help="how many days back to (re)fetch")
    ap.add_argument("--state", default=None, help="restrict to one source code (e.g. MP)")
    a = ap.parse_args()
    con = ensure_db()
    today = datetime.date.today()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for code, src in SOURCES.items():
        if a.state and code != a.state.upper():
            continue
        total = new = 0
        for back in range(a.days):
            day = today - datetime.timedelta(days=back)
            try:
                rows = src["fetch"](day)
            except Exception as e:
                print(f"{code} {day}: FETCH FAILED ({e})", file=sys.stderr)
                continue
            total += len(rows)
            with con:
                for r in rows:
                    cur = con.execute(
                        "insert or ignore into state_news(state,newsid,date,title,category,keywords,url,fetched_at)"
                        " values(?,?,?,?,?,?,?,?)",
                        (code, r["newsid"], r["date"], r["title"], r["category"], r["keywords"], r["url"], now))
                    new += cur.rowcount
            time.sleep(0.4)  # be polite to the state server
        n_all = con.execute("select count(*) from state_news where state=?", (code,)).fetchone()[0]
        print(f"{code} ({src['state']}): fetched {total} rows over {a.days}d, {new} new -> {n_all} total in register")


if __name__ == "__main__":
    main()
