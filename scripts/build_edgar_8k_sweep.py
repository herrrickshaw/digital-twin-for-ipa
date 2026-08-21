#!/usr/bin/env python3
"""build_edgar_8k_sweep.py — SEC EDGAR full-text sweep of 8-K material-event
filings for FRESH India-intent, sibling to build_edgar_india_sweep.py (which
covers annual reports: 10-K/20-F).

Why a separate script, not a FORMS-list extension of the annual-report sweep:
8-Ks are filed within 4 business days of a material event (plant openings,
JVs, executive appointments for a new region, etc.) -- much fresher than an
annual report's once-a-year cadence, and this project's own EDGAR precision
lesson ("high precision over recall") applies just as much here, so it gets
its own cumulative output rather than being merged into the annual-report
file's different cadence/consumption pattern (that one feeds the Monday
shortlist rebuild specifically).

Live-verified 2026-08-21: `"expansion in India" forms=8-K` returns 6 hits for
2026 alone -- a real, fresh, keyless, high-precision source, same efts.sec.gov
API and PHRASES as the annual-report sweep.

Output: layers/16_enrichment/edgar_8k_sweep.json (cumulative, deduped on
accession number).

    build_edgar_8k_sweep.py                # incremental (last 200 days)
    build_edgar_8k_sweep.py --since 2025-01-01
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
OUT = os.path.join(ROOT, "layers", "16_enrichment", "edgar_8k_sweep.json")

API = "https://efts.sec.gov/LATEST/search-index"
UA = {"User-Agent": "digital-twin-for-ipa research umashankartd1991@gmail.com"}
FORMS = "8-K"
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
    "India expansion",
    "subsidiary in India",
    "joint venture in India",
]


def classify(company: str) -> str:
    up = company.upper()
    if any(k in up for k in (" FUND", " L.P.", " LP)", "PARTNERS FUND",
                             "STRATEGIES L.P", "ACCESS FUND")):
        return "pe_fund"
    return "foreign_operator"


def search(phrase: str, start: str, end: str) -> list[dict]:
    hits, frm = [], 0
    while True:
        j = None
        for attempt in range(3):
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
        if not batch or frm >= min(total, 100):
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
                "adsh": adsh, "company": names[0] if names else "?",
                "form": ",".join(src.get("root_forms") or []) or src.get("file_type", ""),
                "file_date": src.get("file_date"), "phrases": [],
            })
            if p not in e["phrases"]:
                e["phrases"].append(p)
            e["segment"] = classify(e["company"])
        time.sleep(0.5)
    print(f"  window {start}..{end}: {len(found)} 8-K filings across {len(PHRASES)} phrases")

    merged = {**old, **found}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {"layer": "edgar_8k_sweep", "built": dt.date.today().isoformat(),
              "method": f"EDGAR FTS exact-phrase sweep, forms {FORMS} (material-event "
                        "filings, fresher than annual reports); cumulative, deduped on accession",
              "filings": sorted(merged.values(), key=lambda e: e.get("file_date") or "", reverse=True)}
    tmp = OUT + ".tmp"
    json.dump(payload, open(tmp, "w"), indent=1)
    os.replace(tmp, OUT)
    print(f"  wrote {os.path.relpath(OUT, ROOT)} ({len(merged)} cumulative)")
    for e in sorted(found.values(), key=lambda x: x.get("file_date") or "", reverse=True):
        print(f"  NEW-LEAD [{e.get('segment', '?')}] {e['file_date']} {e['company']} — "
              f"{', '.join(e['phrases'][:3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
