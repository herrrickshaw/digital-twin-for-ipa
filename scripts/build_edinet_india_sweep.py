#!/usr/bin/env python3
"""EDINET India-sweep -- Japan filing discovery, sibling to build_dart_india_sweep.py.

CORRECTION (2026-08-09): an earlier scouting pass concluded EDINET_API_KEY
was invalid/needed re-registration, testing only a bare `Subscription-Key`
HTTP header (which does 401 -- confirmed). The CORRECT auth, confirmed live
by hand: `?Subscription-Key=<key>` as a query PARAM, or the
`Ocp-Apim-Subscription-Key` HEADER -- both return real data (742 filings for
2026-08-07, 552 for 2026-03-31). The key was never broken.

EDINET has no full-text search (same architecture gap as DART): this is a
list -> download -> grep sweep. Two differences from DART:
  1. documents.json only accepts a SINGLE date, not a range -- this script
     loops one API call per calendar day.
  2. Each filing offers a CSV export (type=5, XBRL_TO_CSV/*.csv, UTF-16LE)
     alongside PDF/XBRL -- smaller and cleaner to grep than DART's raw XML
     dump. Filtered to ordinanceCode=="010" (corporate filers under the
     Financial Instruments and Exchange Act, i.e. real companies) and
     docTypeCode in {120 (annual securities report), 140 (quarterly), 160
     (half-year)} -- excludes investment-trust/fund filings (ordinanceCode
     "030"), which dominate the raw daily list and are not the target.

Precision hazard (confirmed live, same class as DART's 인도/인도하다 and
cninfo's 印度/印度尼西亚): インド (India) is a literal substring of
インドネシア (Indonesia) in Japanese too -- first live test hit was
"...インドネシア市場向けには..." (for the Indonesia market). Unlike cninfo's
bare-keyword search, this script searches for multi-character COMPOUND
phrases only ("インド市場" India-market, "インド進出" India-entry, etc) --
none of these appear as a literal substring of any インドネシア+suffix
combination (インドネシア市場 does not contain "インド市場" contiguously),
so the collision is avoided by phrase construction, not a separate filter.

Usage: python3 scripts/build_edinet_india_sweep.py --days 10 --max-filings 0
Output: layers/16_enrichment/edinet_india_sweep.json (cumulative, deduped on docID)
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import time
import zipfile

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "16_enrichment", "edinet_india_sweep.json")
CREDS = os.path.expanduser("~/.config/market-secrets/credentials.env")
API = "https://api.edinet-fsa.go.jp/api/v2"

CORP_DOC_TYPES = {"120", "140", "160"}  # annual / quarterly / half-year securities reports
INTENT_PHRASES = ["インド進出", "インドに進出", "インド投資", "インドに投資", "インド法人",
                  "インド工場", "インド生産", "インド新設", "インド拡大", "インド現地法人",
                  "インド子会社", "インド市場", "インド事業"]

def load_key() -> str:
    if os.path.exists(CREDS):
        for line in open(CREDS):
            if line.startswith("EDINET_API_KEY="):
                v = line.strip().split("=", 1)[1]
                if v and not v.startswith("<") and "your" not in v.lower():
                    return v
    sys.exit("EDINET_API_KEY missing/placeholder in credentials.env")


def api_get(path: str, key: str, params: dict, expect_json=True):
    r = requests.get(f"{API}/{path}", params={**params, "Subscription-Key": key}, timeout=30)
    r.raise_for_status()
    return r.json() if expect_json else r.content


def list_day(key: str, date: str) -> list:
    d = api_get("documents.json", key, {"date": date, "type": "2"})
    return d.get("results") or []


def find_hits(text: str) -> list:
    hits = []
    for phrase in INTENT_PHRASES:
        for m in re.finditer(re.escape(phrase), text):
            snippet = text[max(0, m.start() - 20):m.end() + 20].replace("\n", " ")
            hits.append({"phrase": phrase, "snippet": snippet})
    return hits


def sweep_doc(key: str, doc_id: str) -> list:
    content = api_get(f"documents/{doc_id}", key, {"type": "5"}, expect_json=False)
    hits = []
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        for name in z.namelist():
            if not name.endswith(".csv"):
                continue
            try:
                text = z.read(name).decode("utf-16-le", "replace")
            except Exception:
                continue
            hits += find_hits(text)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=10, help="business days back from today to scan")
    ap.add_argument("--max-filings", type=int, default=100)
    ap.add_argument("--checkpoint-every", type=int, default=15)
    args = ap.parse_args()

    key = load_key()
    prior = {}
    if os.path.exists(OUT):
        prior = {r["doc_id"]: r for r in json.load(open(OUT))["results"]}

    def save():
        out = {"layer": "16_enrichment/edinet_india_sweep", "built": dt.date.today().isoformat(),
               "method": ("EDINET documents.json (per-day list, no full-text search) -> type=5 "
                          "CSV export -> UTF-16LE decode -> local regex sweep, excluding the "
                          "インド/インドネシア (India/Indonesia) substring collision. Corrected "
                          "2026-08-09: EDINET_API_KEY is valid -- auth via query param or "
                          "Ocp-Apim-Subscription-Key header, NOT a bare Subscription-Key header."),
               "count": len(prior), "results": list(prior.values())}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

    # walk back from today, business days only (Sat/Sun skipped -- EDINET filings are business-day)
    day = dt.date.today() - dt.timedelta(days=1)
    scanned_days, total_swept, since_checkpoint = 0, 0, 0
    while scanned_days < args.days and total_swept < args.max_filings:
        if day.weekday() < 5:  # Mon-Fri
            try:
                docs = list_day(key, day.isoformat())
            except Exception as e:
                print(f"  {day}: list error {type(e).__name__}: {e}", file=sys.stderr)
                docs = []
            corp_docs = [d for d in docs if d.get("ordinanceCode") == "010"
                        and d.get("docTypeCode") in CORP_DOC_TYPES and d.get("csvFlag") == "1"]
            print(f"  {day}: {len(docs)} total, {len(corp_docs)} corp annual/half-year/quarterly")
            for d in corp_docs:
                if total_swept >= args.max_filings:
                    break
                doc_id = d["docID"]
                total_swept += 1
                if doc_id in prior:
                    continue
                row = {"doc_id": doc_id, "filer": d.get("filerName"), "sec_code": d.get("secCode"),
                       "doc_type": d.get("docTypeCode"), "description": d.get("docDescription"),
                       "date": day.isoformat(), "hits": [], "swept": dt.date.today().isoformat()}
                try:
                    row["hits"] = sweep_doc(key, doc_id)
                except Exception as e:
                    row["error"] = f"{type(e).__name__}: {e}"
                if row["hits"]:
                    print(f"    NEW-LEAD: {row['filer']} ({row['sec_code']}) -- "
                          f"{row['hits'][0]['phrase']}: ...{row['hits'][0]['snippet']}...")
                prior[doc_id] = row
                since_checkpoint += 1
                if since_checkpoint >= args.checkpoint_every:
                    save()
                    since_checkpoint = 0
                time.sleep(0.3)
            scanned_days += 1
        day -= dt.timedelta(days=1)

    save()
    hits = [r for r in prior.values() if r.get("hits")]
    print(f"\ncumulative filings tracked: {len(prior)} | with India-intent hits: {len(hits)} -> {OUT}")


if __name__ == "__main__":
    main()
