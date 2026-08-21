#!/usr/bin/env python3
"""Country-linked FDI news sweep -- "look in the stock markets of the layer-35
priority countries and link it to companies announcing India interest."

Two things layer 35 (capital-cost arbitrage lens) could not do on its own:
  1. It scored "twin_lead_coverage" as a bare count (e.g. Switzerland: 3
     leads) with NO DENOMINATOR -- 3 out of how many real listed companies?
     This script answers that from data ALREADY ON DISK: the sibling
     global-stock-screener repo's per-market ticker rosters
     (~/repos/global-stock-screener/data/global_universe/<CC>.csv), no new
     scraping needed. Real denominators: Switzerland 192 listed names,
     Sweden 564, Denmark 104, Germany 449, Canada 2091, China 2895, UK 854,
     Hong Kong 2792 -- Netherlands/Italy/France/Norway have no dedicated
     file, only the thinner EU.csv bucket filtered by exchange (Euronext
     Amsterdam/Borsa Italiana/Euronext Paris/Oslo Bors).
  2. It had no live discovery mechanism for these 12 markets (unlike EDGAR
     for the US or the new DART sweep for Korea). This script adds one using
     NewsAPI's boolean full-text search (the one already-keyed source that
     supports free-text country+intent queries, unlike Marketaux/
     AlphaVantage which are ticker-lookup-only) -- ONE query per priority
     country, matched back against that country's REAL roster (not NER,
     not fuzzy guessing) using the SAME strong/weak fragment matcher
     enrich_company_db_ii_tickers.py already uses, so a hit only counts if
     the actual listed company's name (not a bare country name or generic
     word) appears in the article.

Scope: the 12 countries layers/35_capital_cost_arbitrage_lens.json flagged
as sweep_priority (deep capital market AND thin/no-source coverage) --
NOT all 28 in the rate table. Running this against all 28 would mean
also querying the shallow/excluded markets (Thailand, Morocco, Kuwait...)
that layer 35 already found not worth prioritizing, and would burn far
more of NewsAPI's ~100-call/day free-tier budget for no better signal.

Usage: python3 scripts/build_country_fdi_news_sweep.py [--max-calls 15] [--dry-run]
Output: layers/16_enrichment/country_fdi_news_sweep.json
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED = os.path.expanduser("~/.config/market-secrets/credentials.env")
UNIV_DIR = os.path.expanduser("~/repos/global-stock-screener/data/global_universe")
OUT = os.path.join(ROOT, "layers", "16_enrichment", "country_fdi_news_sweep.json")
ARCHIVE = os.path.join(ROOT, "state", "news_articles.jsonl")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

# economy -> roster source. Dedicated per-country file preferred; Netherlands/
# Italy/France/Norway fall back to the pan-European EU.csv bucket filtered by
# exchange (thinner: index-constituent-level, not the full listed universe).
ROSTERS = {
    "Switzerland": {"file": "CH.csv"},
    "Sweden": {"file": "SE.csv"},
    "Denmark": {"file": "DK.csv"},
    "Canada": {"file": "CA.csv"},
    "Germany": {"file": "DE.csv"},
    "China": {"file": "CN.csv"},
    "United Kingdom": {"file": "UK.csv"},
    "Hong Kong": {"file": "HK.csv"},
    "Netherlands": {"file": "EU.csv", "exchange": "Euronext Amsterdam"},
    "Italy": {"file": "EU.csv", "exchange": "Borsa Italiana"},
    "France": {"file": "EU.csv", "exchange": "Euronext Paris"},
    "Norway": {"file": "EU.csv", "exchange": "Oslo Bors"},
}

INDIA_INTENT_QUERY = ('("invest in India" OR "investment in India" OR "India expansion" OR '
                       '"India plant" OR "India facility" OR "enters India" OR "India subsidiary" '
                       'OR "manufacturing in India")')


def load_key():
    if os.path.exists(CRED):
        for line in open(CRED):
            if line.startswith("NEWSAPI_KEY="):
                v = line.strip().split("=", 1)[1]
                if v and not v.startswith("<") and "your" not in v.lower():
                    return v
    return None


def load_roster(economy):
    spec = ROSTERS[economy]
    path = os.path.join(UNIV_DIR, spec["file"])
    if not os.path.exists(path):
        return []
    import csv
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            if "exchange" in spec and r.get("exchange") != spec["exchange"]:
                continue
            rows.append({"name": r["name"], "ticker": r["yf_ticker"], "exchange": r["exchange"]})
    return rows


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def load_leads_tickers():
    p = os.path.join(ROOT, "layers", "16_leads.json")
    if not os.path.exists(p):
        return set()
    return {l["ticker"] for l in json.load(open(p))["leads"] if l.get("ticker")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-calls", type=int, default=15)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    key = load_key()
    if not key and not args.dry_run:
        sys.exit("NEWSAPI_KEY missing/placeholder -- run --dry-run to test roster loading only")

    known_tickers = load_leads_tickers()
    today = date.today().isoformat()

    results = {}
    calls_used = 0
    for economy in ROSTERS:
        roster = load_roster(economy)
        roster_index = [(norm(r["name"]), r) for r in roster]
        row = {"economy": economy, "roster_source": ROSTERS[economy]["file"],
               "roster_size": len(roster), "matches": [], "articles_fetched": 0}

        if not args.dry_run and calls_used < args.max_calls:
            q = f'"{economy}" AND {INDIA_INTENT_QUERY}'
            try:
                d = get_json("https://newsapi.org/v2/everything?" + urllib.parse.urlencode(
                    {"q": q, "language": "en", "sortBy": "publishedAt", "pageSize": 50,
                     "apiKey": key}))
                calls_used += 1
                articles = d.get("articles", [])
                row["articles_fetched"] = len(articles)
                for a in articles:
                    text = norm((a.get("title") or "") + " " + (a.get("description") or ""))
                    for rn, r in roster_index:
                        frags = match_fragments(rn)
                        # word-boundary match, not raw substring: raw `in` let a
                        # 2-char orphaned-possessive fragment ("people s", from
                        # "People's" -> "people"+"s" after apostrophe-stripping)
                        # false-match inside "the people SAID" -- found live
                        # 2026-08-09 (People's Insurance Group of China vs. an
                        # unrelated Tata/China-curbs article). \b...\b rejects it.
                        hit = next((q for frag, q in frags
                                    if re.search(rf"\b{re.escape(frag)}\b", text)), None)
                        if hit:
                            quality = hit
                            row["matches"].append({
                                "company": r["name"], "ticker": r["ticker"], "exchange": r["exchange"],
                                "match_quality": quality,
                                "already_in_twin_leads": r["ticker"] in known_tickers,
                                "article_title": a.get("title"), "article_url": a.get("url"),
                                "published": a.get("publishedAt"),
                            })
                    if os.path.exists(os.path.dirname(ARCHIVE)):
                        with open(ARCHIVE, "a") as f:
                            f.write(json.dumps({"source": "newsapi_country_sweep", "query": q,
                                                "title": a.get("title"), "description": a.get("description"),
                                                "url": a.get("url"), "published": a.get("publishedAt"),
                                                "collected": today}) + "\n")
            except Exception as e:
                row["error"] = f"{type(e).__name__}: {e}"
            time.sleep(0.5)
        results[economy] = row

    new_leads = [m for row in results.values() for m in row["matches"]
                 if not m["already_in_twin_leads"] and m["match_quality"] == "strong"]

    out = {"layer": "16_enrichment/country_fdi_news_sweep", "built": today,
           "method": ("NewsAPI boolean query per priority country (from layer 35's "
                      "sweep_priority list), matched against each country's REAL stock-market "
                      "roster (global-stock-screener/data/global_universe/*.csv) using the "
                      "strong/weak fragment matcher from enrich_company_db_ii_tickers.py -- "
                      "only 'strong' (full-name or first-two-token) matches count as new leads"),
           "calls_used": calls_used, "countries": results,
           "new_leads_strong_match": new_leads}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

    for economy, row in results.items():
        print(f"{economy:16} roster={row['roster_size']:>5} articles={row['articles_fetched']:>3} "
              f"matches={len(row['matches']):>3}"
              + (f" ERROR:{row['error']}" if "error" in row else ""))
    print(f"\ncalls used: {calls_used}/{args.max_calls} | NEW strong-match leads not in twin: {len(new_leads)}")
    for l in new_leads:
        print(f"  NEW-LEAD: {l['company']} ({l['ticker']}, {l['exchange']}) -- {l['article_title']}")


if __name__ == "__main__":
    main()
