#!/usr/bin/env python3
"""
build_edgar_india_sweep.py — SEC EDGAR full-text sweep for FRESH India-intent
in annual reports (10-K, 10-K/A, 20-F).

Why: the target shortlist (layers/16_target_shortlist.json) weights India
intent stated in a company's own annual report — the highest-commitment public
signal. The twin previously learned this at rebuild cadence; this sweep
catches newly-FILED intent within days, via EDGAR's full-text search API
(efts.sec.gov, covers 2001+, no key needed, UA header required).

Phrase set is deliberately narrow (exact quoted phrases): high precision over
recall — one true positive beats fifty "operations in India" boilerplates.
20-F matters as much as 10-K: it is the annual report of FOREIGN private
issuers (the "global companies investing in India from global markets" set).

Output: layers/16_enrichment/edgar_india_sweep.json  (cumulative, deduped on
accession number) — consumed by the Monday shortlist rebuild; new CIKs not in
the shortlist print as NEW-LEAD lines for the alert mail.

    build_edgar_india_sweep.py                # incremental (last 200 days)
    build_edgar_india_sweep.py --since 2025-01-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "16_enrichment", "edgar_india_sweep.json")
SHORTLIST = os.path.join(ROOT, "layers", "16_target_shortlist.json")

API = "https://efts.sec.gov/LATEST/search-index"
UA = {"User-Agent": "digital-twin-for-ipa research umashankartd1991@gmail.com"}
# 🔴 never add "10-K/A" here: the slash poisons EDGAR's comma-list form
# filter and the whole query silently returns 0 hits (found 2026-07-23)
FORMS = "10-K,20-F"
PHRASES = [
    "expansion in India",
    "expand in India",
    "invest in India",
    "investment in India",
    "investments in India",
    "new facility in India",
    "manufacturing facility in India",
    "manufacturing in India",
    "production capacity in India",
    "growing demand in India",
    "India expansion",
]


# segmentation: a global operator planning Indian capacity is a different lead
# from an India-domiciled ADR filer describing itself, or a PE fund vehicle
# disclosing India exposure — all three are useful, in different playbooks
INDIA_DOMICILED_CIKS = {
    "0001103838",  # ICICI Bank
    "0001144967",  # HDFC Bank
    "0001123799",  # Wipro
    "0001094324",  # Sify
    "0001495153",  # MakeMyTrip
    "0001516899",  # Yatra
    "0001848763",  # ReNew Energy
    "0001854275",  # Zoomcar
    "0001868640",  # Roadzen
    "0001427570",  # Vyome
    "0001973368",  # SRIVARU
    "0001816319",  # Lytus
}


def classify(company: str) -> str:
    if any(cik in company for cik in INDIA_DOMICILED_CIKS):
        return "india_domiciled"
    up = company.upper()
    if any(k in up for k in (" FUND", " L.P.", " LP)", "PARTNERS FUND",
                             "STRATEGIES L.P", "ACCESS FUND")):
        return "pe_fund"
    return "foreign_operator"


def search(phrase: str, start: str, end: str) -> list[dict]:
    hits, frm = [], 0
    while True:
        j = None
        for attempt in range(3):  # EDGAR FTS throws transient 500s
            try:
                r = requests.get(API, params={
                    "q": f'"{phrase}"', "forms": FORMS, "dateRange": "custom",
                    "startdt": start, "enddt": end, "from": frm}, headers=UA,
                    timeout=30)
                r.raise_for_status()
                j = r.json()
                break
            except Exception as e:
                if attempt == 2:
                    print(f"  {phrase!r}: FAILED {type(e).__name__}: {str(e)[:60]}")
                    return hits
                time.sleep(2 * (attempt + 1))
        batch = j.get("hits", {}).get("hits", [])
        hits.extend(batch)
        total = j.get("hits", {}).get("total", {}).get("value", 0)
        frm += len(batch)
        if not batch or frm >= min(total, 100):  # cap per phrase — precision set
            break
        time.sleep(0.5)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    a = ap.parse_args()
    start = a.since or (dt.date.today() - dt.timedelta(days=200)).isoformat()
    end = dt.date.today().isoformat()

    old = {}
    if os.path.exists(OUT):
        old = {e["adsh"]: e for e in json.load(open(OUT)).get("filings", [])}

    found = {}
    for p in PHRASES:
        for h in search(p, start, end):
            src = h.get("_source", {})
            adsh = src.get("adsh") or h.get("_id", "")
            names = src.get("display_names") or []
            e = found.setdefault(adsh, {
                "adsh": adsh,
                "company": names[0] if names else "?",
                "form": ",".join(src.get("root_forms") or []) or src.get("file_type", ""),
                "file_date": src.get("file_date"),
                "phrases": [],
                "url": ("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
                        f"&filenum=&type=&dateb=&owner=include&count=40&search_text="),
            })
            if p not in e["phrases"]:
                e["phrases"].append(p)
            e["segment"] = classify(e["company"])
        time.sleep(0.5)
    print(f"  window {start}..{end}: {len(found)} filings across "
          f"{len(PHRASES)} phrases")

    merged = {**old, **found}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        "layer": "edgar_india_sweep",
        "built": dt.date.today().isoformat(),
        "method": f"EDGAR FTS exact-phrase sweep, forms {FORMS}; cumulative, "
                  "deduped on accession; consumed by shortlist rebuild",
        "filings": sorted(merged.values(),
                          key=lambda e: e.get("file_date") or "", reverse=True),
    }
    tmp = OUT + ".tmp"
    json.dump(payload, open(tmp, "w"), indent=1)
    os.replace(tmp, OUT)
    print(f"  wrote {os.path.relpath(OUT, ROOT)} ({len(merged)} cumulative)")

    # surface leads not already on the shortlist (for the alert mail)
    if os.path.exists(SHORTLIST):
        sl = json.load(open(SHORTLIST))
        known = {t["company"].upper()[:20] for t in sl.get("targets", [])}
        for e in sorted(found.values(), key=lambda x: x.get("file_date") or "",
                        reverse=True):
            comp = str(e["company"]).upper()
            if e.get("segment") == "india_domiciled":
                continue  # ADR self-description, not an inbound-FDI lead
            if not any(k in comp for k in known):
                print(f"  NEW-LEAD [{e.get('segment', '?')}] {e['file_date']} "
                      f"{e['form']:<6} {e['company']} — "
                      f"{', '.join(e['phrases'][:3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
