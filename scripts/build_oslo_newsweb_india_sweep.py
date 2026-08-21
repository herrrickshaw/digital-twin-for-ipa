#!/usr/bin/env python3
"""Oslo Bors NewsWeb India-sweep -- Norway filing discovery, sibling to
build_edgar_india_sweep.py. Genuinely clone-EDGAR-easy: Euronext's Oslo Bors
NewsWeb has a real no-auth JSON REST API (found via network trace, confirmed
live 2026-08-09): GET api3.oslo.oslobors.no/v1/newsreader/list?messageTitle=
<term>&fromDate=&toDate= -- server-side TITLE search (not full body text like
EDGAR, but titles on this feed are descriptive press-release/regulatory-
announcement titles, not boilerplate). 158 "India" hits over 2015-2026,
`overflow: false` confirming no truncation -- small enough to fetch in one
call, no pagination needed.

Unlike EDGAR/DART/cninfo, this needs LOCAL classification, not phrase
filtering -- the API already narrows to titles containing "India", but mixes
genuine market-entry signals with unrelated hits: exits/divestments (e.g.
"BW LPG exits investment in Confidence Petroleum India"), and business-
activity hits (contract wins, distribution deals) that are real but not
FDI-establishment signals. Classified into three tiers locally.

Usage: python3 scripts/build_oslo_newsweb_india_sweep.py
Output: layers/16_enrichment/oslo_newsweb_india_sweep.json
"""
import datetime as dt
import json
import os
import re

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "16_enrichment", "oslo_newsweb_india_sweep.json")
API = "https://api3.oslo.oslobors.no/v1/newsreader/list"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126"

EXIT_RE = re.compile(r"\b(exit|divest|disposal|sold|sale of|ceases?|ceasing|terminat\w*|withdraw\w*)\b", re.I)
ENTRY_RE = re.compile(
    r"\b(entry into|enters|expansion|establish|subsidiary|initial public offering|"
    r"\bipo\b|new facility|new plant|manufacturing|invests?\b|investment in)\b", re.I)


def classify(title: str) -> str:
    if EXIT_RE.search(title):
        return "exit_or_divestment"
    if ENTRY_RE.search(title):
        return "market_entry_or_investment"
    return "business_activity"


def main():
    r = requests.get(API, params={"messageTitle": "India", "fromDate": "2015-01-01",
                                   "toDate": dt.date.today().isoformat()},
                     headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    d = r.json()
    msgs = d["data"]["messages"]
    overflow = d["data"]["overflow"]

    rows = []
    for m in msgs:
        rows.append({
            "issuer": m.get("issuerName"), "issuer_sign": m.get("issuerSign"),
            "title": m.get("title"), "published": m.get("publishedTime"),
            "tier": classify(m.get("title") or ""),
            "category": (m.get("category") or [{}])[0].get("category_en"),
            "message_id": m.get("messageId"),
        })

    entry = [r for r in rows if r["tier"] == "market_entry_or_investment"]
    business = [r for r in rows if r["tier"] == "business_activity"]
    exits = [r for r in rows if r["tier"] == "exit_or_divestment"]

    out = {"layer": "16_enrichment/oslo_newsweb_india_sweep", "built": dt.date.today().isoformat(),
           "method": ("Oslo Bors NewsWeb API, server-side title search for 'India', "
                      "2015-2026, no auth. overflow=" + str(overflow) + " (no truncation). "
                      "Classified locally into market_entry_or_investment / business_activity / "
                      "exit_or_divestment -- API narrows by keyword, this script narrows by intent."),
           "total_india_titles": len(rows), "market_entry_or_investment": entry,
           "business_activity": business, "exit_or_divestment": exits}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"total: {len(rows)} | market_entry/investment: {len(entry)} | "
          f"business_activity: {len(business)} | exit/divestment: {len(exits)} -> {OUT}")
    for e in entry:
        print(f"  ENTRY: {e['issuer']} -- {e['title']}")


if __name__ == "__main__":
    main()
