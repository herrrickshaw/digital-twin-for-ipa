#!/usr/bin/env python3
"""Layer 32 enrichment — external news collector (stock-market + FDI news).

Fourth verification channel after clearance register -> rating rationale ->
Invest India tickers: pulls news from the machine's working news APIs and
matches it onto the company DB with the SAME tiered matcher the ticker
enrichment uses (strong / reviewed-promoted / weak).

Sources (keys read from ~/.config/market-secrets/credentials.env — path
referenced only, secrets never committed; missing keys skip that source and
are recorded as data):
  MARKETAUX_KEY     ticker-tagged articles for listed leads (symbols batched)
  ALPHAVANTAGE_KEY  NEWS_SENTIMENT with sentiment scores (tickers batched)
  NEWSAPI_KEY       keyword search: FDI sweep + QUIET-company probes
  NEWSDATA_KEY      keyword search, country=in business stream
  (EODHD news endpoint 404s on this plan — recorded, not called)

Free-tier quotas are tight (NewsAPI/Marketaux ~100 req/day, AlphaVantage 25),
so the collector budgets calls: --max-calls (default 40) hard-caps total HTTP
requests; company-targeted probes cover ONLY the QUIET clearance leads (the
cohort where a news hit changes a verdict).

Tables (companies.db):
  news_articles          one row per collected article (source, query, url…)
  news_company_matches   tiered matches vs companies (fragment kept)

Appends a `news_collection` block to layers/32_company_db.json.
Run AFTER build_company_db.py + enrich_company_db_ii_tickers.py.

Usage: python3 scripts/collect_company_news.py [--max-calls N] [--dry-run]
"""
import argparse
import importlib.util
import json
import os
import sqlite3
import time
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
LAYER = os.path.join(ROOT, "layers", "32_company_db.json")
CRED = os.path.expanduser("~/.config/market-secrets/credentials.env")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# reuse the ticker enrichment's matcher (norm, match_fragments, REVIEWED_WEAK_OK)
_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

FDI_QUERIES = [
    '"FDI" India investment',
    '"greenfield investment" India',
    'India "invests" plant manufacturing crore',
    'India factory expansion investment announcement',
]


def load_keys():
    env = {}
    if os.path.exists(CRED):
        for line in open(CRED):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


class Budget:
    def __init__(self, cap):
        self.cap, self.used = cap, 0

    def take(self):
        if self.used >= self.cap:
            return False
        self.used += 1
        return True


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-calls", type=int, default=40)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    env = load_keys()
    budget = Budget(args.max_calls)
    today = date.today().isoformat()

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS news_articles (
            art_id    INTEGER PRIMARY KEY,
            source    TEXT,          -- marketaux | alphavantage | newsapi | newsdata
            query     TEXT,          -- the query/symbols that fetched it
            title     TEXT, description TEXT, url TEXT UNIQUE,
            published TEXT, sentiment TEXT,
            fetched   TEXT
        );
        CREATE TABLE IF NOT EXISTS news_company_matches (
            art_id     INTEGER REFERENCES news_articles(art_id),
            company_id INTEGER REFERENCES companies(company_id),
            matched_fragment TEXT, match_quality TEXT,
            company_visibility TEXT,
            UNIQUE(art_id, company_id)
        );
        """
    )

    skipped, called = [], {}

    def store(source, query, arts):
        n = 0
        for a in arts:
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO news_articles"
                    "(source,query,title,description,url,published,sentiment,fetched)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (source, query, a.get("title"), a.get("description"),
                     a.get("url"), a.get("published"), a.get("sentiment"), today))
                n += cur.rowcount
            except sqlite3.Error:
                pass
        called[source] = called.get(source, 0) + 1
        return n

    # ---- 1) FDI keyword sweep (NewsAPI + Newsdata) ---------------------------
    new_arts = 0
    if env.get("NEWSAPI_KEY"):
        for q in FDI_QUERIES:
            if not budget.take():
                break
            try:
                d = get_json("https://newsapi.org/v2/everything?"
                             + urllib.parse.urlencode(
                                 {"q": q, "language": "en", "sortBy": "publishedAt",
                                  "pageSize": 50, "apiKey": env["NEWSAPI_KEY"]}))
                new_arts += store("newsapi", q, [
                    {"title": a.get("title"), "description": a.get("description"),
                     "url": a.get("url"), "published": a.get("publishedAt")}
                    for a in d.get("articles", [])])
            except Exception as e:
                skipped.append(f"newsapi {q}: {type(e).__name__}")
    else:
        skipped.append("newsapi: no key")

    if env.get("NEWSDATA_KEY"):
        for q in ("FDI investment", "stock market"):
            if not budget.take():
                break
            try:
                d = get_json("https://newsdata.io/api/1/latest?"
                             + urllib.parse.urlencode(
                                 {"apikey": env["NEWSDATA_KEY"], "q": q,
                                  "country": "in", "category": "business",
                                  "language": "en"}))
                new_arts += store("newsdata", q, [
                    {"title": a.get("title"), "description": a.get("description"),
                     "url": a.get("link"), "published": a.get("pubDate")}
                    for a in d.get("results", [])])
            except Exception as e:
                skipped.append(f"newsdata {q}: {type(e).__name__}")
    else:
        skipped.append("newsdata: no key")

    # ---- 2) ticker-tagged news for listed leads (Marketaux + AlphaVantage) ---
    cur.execute("""SELECT company_id, name, ticker FROM companies
                    WHERE ticker IS NOT NULL AND ticker != ''
                      AND company_id IN (SELECT company_id FROM lead_scores)
                    ORDER BY (SELECT MAX(score) FROM lead_scores l
                              WHERE l.company_id=companies.company_id) DESC
                    LIMIT 60""")
    listed = cur.fetchall()
    tickers = [t for _, _, t in listed]
    if env.get("MARKETAUX_KEY") and tickers:
        for i in range(0, min(len(tickers), 30), 3):   # 3 symbols/call on free tier
            if not budget.take():
                break
            syms = ",".join(tickers[i:i+3])
            try:
                d = get_json("https://api.marketaux.com/v1/news/all?"
                             + urllib.parse.urlencode(
                                 {"symbols": syms, "limit": 3, "language": "en",
                                  "api_token": env["MARKETAUX_KEY"]}))
                new_arts += store("marketaux", syms, [
                    {"title": a.get("title"), "description": a.get("description"),
                     "url": a.get("url"), "published": a.get("published_at")}
                    for a in d.get("data", [])])
            except Exception as e:
                skipped.append(f"marketaux {syms}: {type(e).__name__}")
            time.sleep(0.6)
    if env.get("ALPHAVANTAGE_KEY") and tickers:
        # AV free tier: 25 req/day — ONE batched call with US-listed tickers only
        us = [t for t in tickers if "." not in t][:8]
        if us and budget.take():
            try:
                d = get_json("https://www.alphavantage.co/query?"
                             + urllib.parse.urlencode(
                                 {"function": "NEWS_SENTIMENT",
                                  "tickers": ",".join(us), "limit": 50,
                                  "apikey": env["ALPHAVANTAGE_KEY"]}))
                new_arts += store("alphavantage", ",".join(us), [
                    {"title": a.get("title"), "description": a.get("summary"),
                     "url": a.get("url"), "published": a.get("time_published"),
                     "sentiment": a.get("overall_sentiment_label")}
                    for a in d.get("feed", [])])
            except Exception as e:
                skipped.append(f"alphavantage: {type(e).__name__}")

    # ---- 3) QUIET-company probes (NewsAPI, exact-phrase) ---------------------
    cur.execute("""SELECT c.company_id, c.name FROM companies c
                    JOIN clearance_activity a USING (company_id)
                   WHERE a.visibility_verdict='QUIET'""")
    quiet = cur.fetchall()
    if env.get("NEWSAPI_KEY"):
        for cid, name in quiet:
            if not budget.take():
                break
            q = f'"{norm(name)}"'
            try:
                d = get_json("https://newsapi.org/v2/everything?"
                             + urllib.parse.urlencode(
                                 {"q": q, "pageSize": 5,
                                  "apiKey": env["NEWSAPI_KEY"]}))
                new_arts += store("newsapi", q, [
                    {"title": a.get("title"), "description": a.get("description"),
                     "url": a.get("url"), "published": a.get("publishedAt")}
                    for a in d.get("articles", [])])
            except Exception as e:
                skipped.append(f"newsapi quiet {name}: {type(e).__name__}")
    con.commit()

    # ---- 4) tiered matching over collected articles --------------------------
    cur.execute("""SELECT c.company_id, c.name,
                          (SELECT visibility_verdict FROM clearance_activity a
                            WHERE a.company_id=c.company_id
                              AND a.visibility_verdict IS NOT NULL LIMIT 1)
                     FROM companies c""")
    companies = [(cid, name, vis, norm(name)) for cid, name, vis in cur.fetchall()]
    cur.execute("SELECT art_id, COALESCE(title,'') || ' ' || COALESCE(description,'')"
                " FROM news_articles")
    arts = [(aid, " " + norm(t) + " ") for aid, t in cur.fetchall()]
    n_match = 0
    for cid, name, vis, nn in companies:
        for frag, quality in match_fragments(nn):
            hits = [aid for aid, ntext in arts if f" {frag} " in ntext]
            if hits:
                for aid in hits:
                    cur.execute("INSERT OR IGNORE INTO news_company_matches"
                                " VALUES (?,?,?,?,?)", (aid, cid, frag, quality, vis))
                    n_match += cur.rowcount
                break
    con.commit()

    # exception hits: QUIET/PARTIALLY_VISIBLE with strong-tier news
    rows = cur.execute("""
        SELECT DISTINCT c.name, m.company_visibility, n.source, n.title, n.url
          FROM news_company_matches m
          JOIN companies c USING (company_id)
          JOIN news_articles n ON n.art_id = m.art_id
         WHERE m.company_visibility IN ('QUIET','PARTIALLY_VISIBLE')
           AND m.match_quality IN ('strong','reviewed-promoted')
           AND n.fetched = ?""", (today,)).fetchall()
    exceptions = [{"company": r[0], "verdict": r[1], "source": r[2],
                   "title": r[3], "url": r[4]} for r in rows]

    n_arts = cur.execute("SELECT COUNT(*) FROM news_articles").fetchone()[0]
    summary = {
        "ran": today,
        "what": ("External news collection (Marketaux ticker-tagged, AlphaVantage "
                 "sentiment, NewsAPI/Newsdata keyword FDI sweep + QUIET-company "
                 "probes) matched onto the company DB with the shared tiered "
                 "matcher; keys read from ~/.config/market-secrets/credentials.env"),
        "api_calls_used": budget.used, "calls_by_source": called,
        "articles_total": n_arts, "new_articles": new_arts,
        "match_rows_added": n_match,
        "exception_news_hits": exceptions[:25],
        "sources_skipped_or_errors": skipped,
        "quota_note": ("free tiers: NewsAPI/Marketaux ~100 req/day, AlphaVantage 25 "
                       "— weekly cadence keeps usage well inside quotas; EODHD news "
                       "endpoint not in plan (404), not called"),
    }
    layer = json.load(open(LAYER))
    layer["news_collection"] = summary
    if not args.dry_run:
        with open(LAYER, "w") as f:
            json.dump(layer, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("exception_news_hits",)}, indent=1)[:1200])
    print("exception hits:", len(exceptions))
    for e in exceptions[:8]:
        print(f"  [{e['verdict']}] {e['company']} <- {e['source']}: {e['title'][:70]}")
    con.close()


if __name__ == "__main__":
    main()
