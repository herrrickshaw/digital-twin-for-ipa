#!/usr/bin/env python3
"""Sector-primary news sweep -- "pick this sector by sector and evaluate this
country by country for all companies." One NewsAPI query PER SECTOR (13
sectors, matching the twin's existing focus-sector taxonomy in
build_leads.py's LANES dict), each query OR-combining sector-specific
India-investment phrases. Country breakdown comes from matching each hit's
company mention against REAL stock-market rosters for 24 countries
(global-stock-screener/data/global_universe/*.csv) -- not query-time country
restriction, which would have meant 13 sectors x ~20 countries = 260+ calls,
far past NewsAPI's free-tier budget. This design gets full sector x country
coverage in 13 calls.

Same discipline as build_country_fdi_news_sweep.py: a hit only counts as a
company match if an ACTUAL roster company name appears in the article
(word-boundary matched via the shared strong/weak fragment matcher), not
guessed from article prose -- avoids fabricating company identities.

Usage: python3 scripts/build_sector_news_sweep.py [--max-calls 13]
Output: layers/16_enrichment/sector_news_sweep.json
"""
import argparse
import csv
import importlib.util
import json
import os
import re
import sys
import time
import urllib.parse

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED = os.path.expanduser("~/.config/market-secrets/credentials.env")
UNIV_DIR = os.path.expanduser("~/repos/global-stock-screener/data/global_universe")
OUT = os.path.join(ROOT, "layers", "16_enrichment", "sector_news_sweep.json")
ARCHIVE = os.path.join(ROOT, "state", "news_articles.jsonl")

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

# All dedicated per-country roster files except India itself (we want
# FOREIGN companies with India interest, not Indian companies).
ROSTER_COUNTRIES = ["AU", "BR", "CA", "CH", "CN", "DE", "DK", "FI", "HK", "ID",
                    "IL", "JP", "KR", "MX", "MY", "SA", "SE", "SG", "TH", "TW", "UK", "US", "ZA"]

# Sector -> India-investment intent phrases, matching build_leads.py's LANES sectors.
# 🔴 REDESIGNED 2026-08-21, twice. V1 mixed a quoted phrase with a trailing
# BARE word (e.g. '"green hydrogen India" investment') -- NewsAPI parsed the
# unquoted word as its own broad OR-term, matching near-random finance
# articles (Charter Communications/Cox merger, unrelated bank-hiring news,
# four unrelated Saudi companies on one Ashtead Technology story). V2 fixed
# the quoting but used long 5-6 word exact phrases ("solar plant in India")
# -- verified live: 0 results, too rare to appear verbatim in real headlines.
# V3 (current): broad sector-keyword OR-group AND India at the API layer
# (guarantees real recall), with precision enforced LOCALLY in two stages --
# INTENT_KEYWORDS must also appear in the matched article text (not just a
# company name), on top of the existing roster word-boundary company match.
SECTOR_QUERIES = {
    "Electronics & Semiconductors": '(semiconductor OR chip OR "electronics manufacturing" OR wafer) AND India',
    "Green Energy & Fuels": '(solar OR "green hydrogen" OR "renewable energy" OR battery) AND India',
    "Pharma & Bulk Drugs": '(pharmaceutical OR "bulk drug" OR "active pharmaceutical ingredient") AND India',
    "Medical Devices": '"medical device" AND India',
    "Aerospace & Defence": '(defence OR defense OR aerospace) AND India',
    "Auto, EV & Components": '("electric vehicle" OR automotive OR "auto components") AND India',
    "Chemicals & Plastics": '(chemical OR petrochemical OR "specialty chemicals") AND India',
    "Specialty Steel & Metals": '(steel OR "specialty steel" OR metals) AND India',
    "Textiles & Apparel": '(textile OR apparel OR garment) AND India',
    "Food Processing": '"food processing" AND India',
    "White Goods & Electricals": '("white goods" OR electricals OR appliance) AND India',
    "Shipbuilding & Marine": '(shipbuilding OR shipyard) AND India',
}
INTENT_KEYWORDS = re.compile(
    r"\b(invest\w*|expan\w*|new (plant|facility|factory)|manufactur\w*|"
    r"establish\w*|subsidiary|joint venture)\b", re.I)


def load_key():
    if os.path.exists(CRED):
        for line in open(CRED):
            if line.startswith("NEWSAPI_KEY="):
                v = line.strip().split("=", 1)[1]
                if v and not v.startswith("<") and "your" not in v.lower():
                    return v
    sys.exit("NEWSAPI_KEY missing/placeholder")


def load_all_rosters():
    rosters = {}
    for cc in ROSTER_COUNTRIES:
        path = os.path.join(UNIV_DIR, f"{cc}.csv")
        if not os.path.exists(path):
            continue
        rows = []
        with open(path) as f:
            for r in csv.DictReader(f):
                rows.append({"name": r["name"], "ticker": r["yf_ticker"], "exchange": r["exchange"], "country": cc})
        rosters[cc] = rows
    return rosters


def get_json(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-calls", type=int, default=13)
    args = ap.parse_args()

    key = load_key()
    rosters = load_all_rosters()
    roster_index = [(norm(r["name"]), r) for rows in rosters.values() for r in rows]
    print(f"loaded {len(roster_index)} companies across {len(rosters)} country rosters")

    today = __import__("datetime").date.today().isoformat()
    results = {}
    calls = 0
    for sector, q in SECTOR_QUERIES.items():
        if calls >= args.max_calls:
            break
        row = {"sector": sector, "query": q, "articles_fetched": 0, "matches": [], "excluded_no_intent": 0}
        try:
            d = get_json("https://newsapi.org/v2/everything?" + urllib.parse.urlencode(
                {"q": q, "language": "en", "sortBy": "publishedAt", "pageSize": 50, "apiKey": key}))
            calls += 1
            articles = d.get("articles", [])
            row["articles_fetched"] = len(articles)
            for a in articles:
                text = norm((a.get("title") or "") + " " + (a.get("description") or ""))
                raw_text = (a.get("title") or "") + " " + (a.get("description") or "")
                if not INTENT_KEYWORDS.search(raw_text):
                    row["excluded_no_intent"] += 1
                    continue
                for rn, r in roster_index:
                    frags = match_fragments(rn)
                    hit = next((qlt for frag, qlt in frags
                               if re.search(rf"\b{re.escape(frag)}\b", text)), None)
                    if hit:
                        row["matches"].append({"company": r["name"], "ticker": r["ticker"],
                                              "country": r["country"], "match_quality": hit,
                                              "article_title": a.get("title"),
                                              "article_url": a.get("url"),
                                              "published": a.get("publishedAt")})
                if os.path.exists(os.path.dirname(ARCHIVE)):
                    with open(ARCHIVE, "a") as f:
                        f.write(json.dumps({"source": "sector_news_sweep", "query": f"[{sector}] {q}",
                                           "title": a.get("title"), "description": a.get("description"),
                                           "url": a.get("url"), "published": a.get("publishedAt"),
                                           "collected": today}) + "\n")
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
        results[sector] = row
        print(f"[{sector}] articles={row['articles_fetched']} matches={len(row['matches'])}"
              + (f" ERROR:{row['error']}" if "error" in row else ""))
        for m in row["matches"]:
            print(f"    {m['company']} ({m['ticker']}, {m['country']}) [{m['match_quality']}] -- {m['article_title']}")
        time.sleep(0.5)

    all_matches = [m for row in results.values() for m in row["matches"] if m["match_quality"] == "strong"]
    out = {"layer": "16_enrichment/sector_news_sweep", "built": today,
           "method": ("One NewsAPI query per twin focus-sector (OR-combined India-investment "
                      "phrases), matched against REAL 23-country stock-market rosters using the "
                      "strong/weak fragment matcher -- country breakdown comes from roster "
                      "matching, not query-time restriction, to stay within free-tier quota."),
           "calls_used": calls, "sectors": results, "strong_matches_all_sectors": all_matches}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"\ncalls used: {calls} | strong matches across all sectors: {len(all_matches)} -> {OUT}")


if __name__ == "__main__":
    main()
