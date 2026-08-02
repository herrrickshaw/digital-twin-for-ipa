#!/usr/bin/env python3
"""Historical backfill for the state-news register (one-shot, resumable).

Pulls the full archives of the two sources that actually serve history:
  MP -- mpinfo.org Todaynews API, day-addressable; archive starts ~2020-04
        (probed 2026-08-02: 2020-03-15 empty, 2020-06-15 populated)
  MH -- mahasamvad.in WordPress REST; oldest post 2019-09-18 (~25.7k posts)

UP/GJ/KA only expose their latest releases -- no archive to backfill.

Rows are inserted WITHOUT translation (bulk); run the signal pass afterwards:
  python3 scripts/backfill_state_news.py            # collect archives
  python3 scripts/backfill_state_news.py --translate-signal
The signal pass machine-translates only rows whose native title carries
investment/project/regulation language (SIGNAL_NATIVE below), which is what the
quarterly state view reads. Progress is checkpointed in backfill_log -- rerun to
resume after an interruption.
"""
import argparse, datetime, os, re, sqlite3, sys, time, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect_state_news import (DB, ensure_db, fetch_mp, fetch_rajasthan,
                                translate_en, _is_english, _get_json)

MP_START = datetime.date(2020, 3, 1)
MH_OLDEST = "2019-09-18"

# Devanagari (Hindi/Marathi) + Latin investment/project/regulation signal terms.
# Hindi: nivesh/udyog/crore/pariyojana/yojana/niti/manzoori/swikriti/udghatan/
# shilanyas/lokarpan/samjhauta/MoU/factory/plant/rojgar-package...
# Marathi: guntavnuk/prakalp/dhoran/karkhana/koti/manjuri/bhoomipujan/udyog...
SIGNAL_NATIVE = re.compile(
    r"निवेश|गुंतवणूक|उद्योग|उद्योजक|औद्योगिक|करोड़|कोटी|करोड|परियोजना|प्रकल्प|"
    r"योजना|नीति|धोरण|मंजूरी|मंजुरी|स्वीकृति|स्वीकृत|उद्घाटन|उदघाटन|शिलान्यास|"
    r"भूमिपूजन|भूमि.?पूजन|लोकार्पण|समझौता|सामंजस्य|एमओयू|MoU|MOU|कारखाना|संयंत्र|"
    r"प्लांट|निर्यात|रोजगार|रोज़गार|अधिनियम|विधेयक|अध्यादेश|संशोधन|नियम|कैबिनेट|"
    r"मंत्रि.?परिषद|मंत्रिमंडळ|सेमीकंडक्टर|सौर|इथेनॉल|टेक्सटाइल|वस्त्रोद्योग|"
    r"invest|industr|crore|project|policy|regulat|cabinet|semiconductor|solar|"
    r"MSME|एमएसएमई|स्टार्टअप|डेटा सेंटर|लॉजिस्टिक", re.I)


def backfill_mp(con):
    today = datetime.date.today()
    done = {r[0] for r in con.execute("select chunk from backfill_log where state='MP'")}
    days = [MP_START + datetime.timedelta(days=i) for i in range((today - MP_START).days + 1)]
    todo = [d for d in days if d.isoformat() not in done]
    print(f"MP: {len(todo)} days to fetch ({len(days) - len(todo)} already logged)")
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for k, day in enumerate(todo):
        try:
            rows = fetch_mp(day)
        except Exception as e:
            print(f"MP {day}: FETCH FAILED ({e}) -- will retry on next run", file=sys.stderr)
            time.sleep(3)
            continue
        with con:
            for r in rows:
                con.execute(
                    "insert or ignore into state_news(state,newsid,date,title,title_en,category,keywords,url,fetched_at)"
                    " values('MP',?,?,?,?,?,?,?,?)",
                    (r["newsid"], r["date"], r["title"],
                     r["title"] if _is_english(r["title"]) else None,
                     r["category"], r["keywords"], r["url"], now))
            con.execute("insert or ignore into backfill_log(state,chunk,fetched_at,n) values('MP',?,?,?)",
                        (day.isoformat(), now, len(rows)))
        if k % 50 == 0:
            print(f"MP progress: {k}/{len(todo)} days ({day}, {len(rows)} rows)", flush=True)
        time.sleep(0.25)


def backfill_mh(con):
    done = {r[0] for r in con.execute("select chunk from backfill_log where state='MH'")}
    now = datetime.datetime.now().isoformat(timespec="seconds")
    page = 1
    while True:
        chunk = f"page-{page}"
        if chunk in done:
            page += 1
            continue
        url = ("https://mahasamvad.in/wp-json/wp/v2/posts?"
               + urllib.parse.urlencode({"per_page": 100, "page": page,
                                         "_fields": "id,date,link,title"}))
        try:
            posts = _get_json(url, timeout=60)
        except Exception as e:
            if "400" in str(e):  # past the last page
                break
            print(f"MH page {page}: FETCH FAILED ({e}) -- will retry on next run", file=sys.stderr)
            time.sleep(5)
            continue
        if not posts:
            break
        with con:
            for x in posts:
                title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x["title"]["rendered"])).strip()
                if not title:
                    continue
                con.execute(
                    "insert or ignore into state_news(state,newsid,date,title,title_en,category,keywords,url,fetched_at)"
                    " values('MH',?,?,?,?,?,?,?,?)",
                    (str(x["id"]), (x.get("date") or "")[:10], title,
                     title if _is_english(title) else None,
                     "DGIPR wire", "", x.get("link") or "", now))
            con.execute("insert or ignore into backfill_log(state,chunk,fetched_at,n) values('MH',?,?,?)",
                        (chunk, now, len(posts)))
        if page % 20 == 0:
            print(f"MH progress: page {page} ({posts[-1]['date'][:10]})", flush=True)
        if len(posts) < 100:
            break
        page += 1
        time.sleep(0.4)


def backfill_rj(con):
    """Rajasthan: page the full DIPR archive (73k+ rows, date desc, ~200/page).
    ~1 GB transfer total; only date+derived-title+PDF link are kept."""
    done = {r[0] for r in con.execute("select chunk from backfill_log where state='RJ'")}
    now = datetime.datetime.now().isoformat(timespec="seconds")
    page, empty = 1, 0
    while empty < 2:
        chunk = f"page-{page}"
        if chunk in done:
            page += 1
            continue
        try:
            rows = fetch_rajasthan(page_size=200, page=page)
        except Exception as e:
            print(f"RJ page {page}: FETCH FAILED ({e}) -- will retry on next run", file=sys.stderr)
            time.sleep(5)
            continue
        if not rows:
            empty += 1
            page += 1
            continue
        empty = 0
        with con:
            for r in rows:
                con.execute(
                    "insert or ignore into state_news(state,newsid,date,title,title_en,category,keywords,url,fetched_at)"
                    " values('RJ',?,?,?,?,?,?,?,?)",
                    (r["newsid"], r["date"], r["title"],
                     r["title"] if _is_english(r["title"]) else None,
                     r["category"], r["keywords"], r["url"], now))
            con.execute("insert or ignore into backfill_log(state,chunk,fetched_at,n) values('RJ',?,?,?)",
                        (chunk, now, len(rows)))
        if page % 25 == 0:
            print(f"RJ progress: page {page} ({rows[-1]['date']})", flush=True)
        page += 1
        time.sleep(0.6)


def translate_signal(con, limit=None, batch=100):
    """Translate only rows whose native title carries signal language.

    Colibri-style streaming: rows are cursored out of SQLite in small batches
    and committed per batch -- the working set in RAM is one batch, never the
    ~80k-row backlog. Resumable by construction (title_en is null = todo), so
    it can run niced in the background or capped per run with --limit."""
    done = fails = skipped = 0
    stop = False
    while not stop:
        # fresh bounded query per batch -- translated rows leave the predicate,
        # so OFFSET only has to step over accumulated non-signal rows
        rows = con.execute(
            "select state, newsid, title from state_news where title_en is null"
            " order by date desc, state, newsid limit ? offset ?", (batch, skipped)).fetchall()
        if not rows:
            break
        pending = []
        for state, nid, title in rows:
            if not SIGNAL_NATIVE.search(title or ""):
                skipped += 1
                continue
            t = translate_en(title)
            if t:
                pending.append((t, state, nid))
                done += 1
            else:
                fails += 1
                skipped += 1  # leave it native this run; rerun retries
            if (limit and done + fails >= limit) or fails >= 5:
                if fails >= 5:
                    print("translation breaker tripped -- rerun later to resume", file=sys.stderr)
                stop = True
                break
        if pending:
            with con:
                con.executemany("update state_news set title_en=? where state=? and newsid=?", pending)
        if done and done % 500 < len(pending):
            print(f"signal pass progress: {done} translated so far", flush=True)
    print(f"signal pass: {done} translated, {fails} failures this run "
          f"(rerun resumes automatically; untranslated non-signal rows stay native)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translate-signal", action="store_true", help="run only the signal translation pass")
    ap.add_argument("--limit", type=int, default=None, help="cap signal translations this run")
    a = ap.parse_args()
    con = ensure_db()
    con.execute("""create table if not exists backfill_log(
        state text not null, chunk text not null, fetched_at text, n integer,
        primary key(state, chunk))""")
    if a.translate_signal:
        translate_signal(con, a.limit)
        return
    backfill_mh(con)
    backfill_mp(con)
    backfill_rj(con)
    print("archives collected; now run:  python3 scripts/backfill_state_news.py --translate-signal")


if __name__ == "__main__":
    main()
