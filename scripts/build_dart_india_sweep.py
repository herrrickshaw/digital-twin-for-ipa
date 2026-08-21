#!/usr/bin/env python3
"""Korea DART India-sweep -- a non-US filing discovery channel, sibling to
build_edgar_india_sweep.py (NOT a new top-level numbered layer -- like the
EDGAR sweep, this feeds layers/16_enrichment/ and the layer-16/32 shortlist,
same tier as collect_company_news.py's "4th verification channel").

Why this exists: build_edgar_india_sweep.py finds NEW India-intent leads by
full-text-searching SEC EDGAR (efts.sec.gov) with a narrow exact-phrase list.
DART (Korea's disclosure system, opendart.fss.or.kr) has NO equivalent
full-text search API -- confirmed live 2026-08-09 (scouting agent + verified
here): `list.json` only returns filing METADATA (corp/date/report type),
`document.xml` returns the filing's raw XML, and the phrase search has to
happen locally after download. So this is a "list -> download -> grep"
script, not a search-API sweep -- architecturally different from EDGAR, not
a clone.

Live-verified 2026-08-09:
  - list.json(pblntf_ty=A, pblntf_detail_ty=A001, corp_cls=Y) = 953 KOSPI
    annual business reports (사업보고서) for Q1-2026 filing season alone.
  - document.xml for one real filing (Dasco, 다스코, corp_code 00353878)
    contained a genuine hit: "인도 뭄바이 교량 강재방호책 공급계약" (India
    Mumbai bridge steel-guardrail supply contract) -- an existing Indian
    business relationship, not from any list this twin already had.
  - Same filing also proved the PRECISION HAZARD: "인도" (India) is a
    homonym of the verb stem 인도- ("to hand over/deliver") -- "재화가
    구매자에게 인도되는 시점" (point at which goods are delivered to the
    buyer) matched bare "인도" twice with zero India relevance. Every hit
    is regex-filtered to exclude 인도 immediately followed by a delivery-verb
    conjugation (되/하/한/받/함/해) before being counted.

Corpus/effort (per scouting agent + this rebuild): ~953 KOSPI + ~1,998
KOSDAQ A001 filings/year (~2,951 total, essentially the whole listed
universe files once/year). KOSPI-only first pass keeps a full sweep to
~1GB of zip downloads/year -- tractable as an overnight batch, NOT
something to run synchronously in one sitting. This script is incremental
and rate-limited; run it with --max-filings to bound any one sitting.

Japan EDINET companion: see build_edinet_india_sweep.py -- an earlier scouting
pass wrongly concluded EDINET_API_KEY was invalid (it tested a bare
`Subscription-Key` HTTP header, which does 401); the CORRECT auth is either
`?Subscription-Key=<key>` as a query param or the `Ocp-Apim-Subscription-Key`
header, both confirmed live 2026-08-09 (742 real filings returned for
2026-08-07). EDINET has no full-text search either, same list -> download ->
grep shape as this DART script -- but CSV export (type=5) is available per
filing, smaller/cleaner than PDF.

Usage:
    build_dart_india_sweep.py --since 2026-01-01 --max-filings 40
    build_dart_india_sweep.py --since 2026-01-01 --corp-cls Y --max-filings 0  # 0 = unbounded, run via cron/background

Output: layers/16_enrichment/dart_india_sweep.json (cumulative, deduped on
rcept_no) -- same location convention as the EDGAR sweep's edgar_india_sweep.json.
"""
from __future__ import annotations

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
OUT = os.path.join(ROOT, "layers", "16_enrichment", "dart_india_sweep.json")
CREDS = os.path.expanduser("~/.config/market-secrets/credentials.env")

LIST_URL = "https://opendart.fss.or.kr/api/list.json"
DOC_URL = "https://opendart.fss.or.kr/api/document.xml"

# Investment-intent phrases (new capex / facility / subsidiary / expansion) --
# scored HIGH, mirrors EDGAR sweep's PHRASES precision-over-recall stance.
INTENT_PHRASES = [
    "인도 진출", "인도에 진출", "인도 투자", "인도에 투자", "인도 법인",
    "인도 공장", "인도 생산기지", "인도 신설", "인도 확장", "인도 현지법인",
    "인도 자회사", "인도 지사", "인도 사업 확대",
]
# Existing-business phrases (supply/export/sales already happening) --
# scored lower: real signal of an India relationship, but not new-investment intent.
BUSINESS_PHRASES = [
    "인도 수출", "인도 공급", "인도 판매", "인도 매출", "인도 시장",
    "인도 지역", "인도 고객",
]
ALL_PHRASES = INTENT_PHRASES + BUSINESS_PHRASES

# Exclude 인도 immediately followed by a conjugated form of 인도하다
# ("to hand over/deliver") -- the homonym false-positive proven live above.
DELIVERY_VERB_RE = re.compile(r"인도(?:되|하|한|받|함|해)")


def load_dart_key() -> str:
    if not os.path.exists(CREDS):
        sys.exit(f"credentials file not found: {CREDS}")
    for line in open(CREDS):
        if line.startswith("DART_KEY="):
            key = line.strip().split("=", 1)[1]
            if key and not key.startswith("<") and "your" not in key.lower():
                return key
    sys.exit("DART_KEY missing or placeholder in credentials.env")


def list_filings_chunk(key: str, bgn_de: str, end_de: str, corp_cls: str) -> list[dict]:
    filings, page = [], 1
    while True:
        r = requests.get(LIST_URL, params={
            "crtfc_key": key, "bgn_de": bgn_de, "end_de": end_de,
            "pblntf_ty": "A", "pblntf_detail_ty": "A001",
            "corp_cls": corp_cls, "page_no": page, "page_count": 100,
        }, timeout=30)
        data = r.json()
        status = data.get("status")
        if status == "013":
            break  # documented: no results for this range
        if status != "000":
            print(f"  list.json error {status}: {data.get('message')} (range {bgn_de}..{end_de})",
                  file=sys.stderr)
            break
        filings.extend(data.get("list", []))
        if page >= int(data.get("total_page", 1)):
            break
        page += 1
        time.sleep(0.3)
    return filings


def list_filings(key: str, bgn_de: str, end_de: str, corp_cls: str) -> list[dict]:
    # 🔴 DART live-verified 2026-08-09: without a corp_code filter, bgn_de..end_de
    # is capped at 3 months ("corp_code가 없는 경우 검색기간은 3개월만 가능합니다") --
    # a wider window returns status 100, not more data. Chunk into <=90-day windows.
    start = dt.datetime.strptime(bgn_de, "%Y%m%d").date()
    stop = dt.datetime.strptime(end_de, "%Y%m%d").date()
    filings = []
    cursor = start
    while cursor <= stop:
        chunk_end = min(cursor + dt.timedelta(days=89), stop)
        filings += list_filings_chunk(key, cursor.strftime("%Y%m%d"),
                                       chunk_end.strftime("%Y%m%d"), corp_cls)
        cursor = chunk_end + dt.timedelta(days=1)
    return filings


def find_hits(text: str) -> dict:
    hits = {"intent": [], "business": [], "excluded_delivery_verb": 0}
    for phrase in ALL_PHRASES:
        for m in re.finditer(re.escape(phrase), text):
            snippet = text[max(0, m.start() - 20):m.end() + 20].replace("\n", " ")
            (hits["intent"] if phrase in INTENT_PHRASES else hits["business"]).append(
                {"phrase": phrase, "snippet": snippet})
    for m in re.finditer("인도", text):
        if DELIVERY_VERB_RE.match(text[m.start():m.start() + 6]):
            hits["excluded_delivery_verb"] += 1
    return hits


def sweep_filing(key: str, rcept_no: str) -> dict:
    r = requests.get(DOC_URL, params={"crtfc_key": key, "rcept_no": rcept_no}, timeout=60)
    r.raise_for_status()
    combined = {"intent": [], "business": [], "excluded_delivery_verb": 0}
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for name in z.namelist():
            try:
                text = z.read(name).decode("utf-8", "replace")
            except Exception:
                continue
            h = find_hits(text)
            combined["intent"] += h["intent"]
            combined["business"] += h["business"]
            combined["excluded_delivery_verb"] += h["excluded_delivery_verb"]
    return combined


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=(dt.date.today() - dt.timedelta(days=200)).isoformat())
    ap.add_argument("--until", default=dt.date.today().isoformat())
    ap.add_argument("--corp-cls", default="Y", choices=["Y", "K"],
                     help="Y=KOSPI (953/yr), K=KOSDAQ (~2,000/yr). One at a time -- run twice for both.")
    ap.add_argument("--max-filings", type=int, default=40,
                     help="0 = unbounded (background/cron use only -- do not run unbounded interactively)")
    args = ap.parse_args()

    key = load_dart_key()
    bgn, end = args.since.replace("-", ""), args.until.replace("-", "")

    filings = list_filings(key, bgn, end, args.corp_cls)
    print(f"filings in range ({args.corp_cls}, {args.since}..{args.until}): {len(filings)}")

    prior = {}
    if os.path.exists(OUT):
        prior = {r["rcept_no"]: r for r in json.load(open(OUT))["results"]}

    already_swept = [f for f in filings if f["rcept_no"] in prior]
    unswept = [f for f in filings if f["rcept_no"] not in prior]
    todo = unswept[: args.max_filings] if args.max_filings else unswept
    print(f"already swept (prior runs): {len(already_swept)} | unswept: {len(unswept)} "
          f"| sweeping this run: {len(todo)}")

    new_leads = []
    for i, f in enumerate(todo, 1):
        try:
            hits = sweep_filing(key, f["rcept_no"])
        except Exception as e:
            hits = {"error": f"{type(e).__name__}: {e}"}
        row = {**f, "hits": hits, "swept": dt.date.today().isoformat()}
        prior[f["rcept_no"]] = row
        if hits.get("intent") or hits.get("business"):
            new_leads.append(row)
            tier = "INTENT" if hits.get("intent") else "business-only"
            print(f"  [{i}/{len(todo)}] NEW-LEAD ({tier}): {f['corp_name']} ({f['stock_code']}) "
                  f"-- {(hits.get('intent') or hits.get('business'))[0]['snippet']}")
        time.sleep(0.3)  # be polite to a free government API

    out = {"layer": "16_enrichment/dart_india_sweep", "built": dt.date.today().isoformat(),
           "method": ("list.json -> document.xml -> local regex sweep (no DART full-text search "
                      "API exists, confirmed 2026-08-09); phrases in INTENT_PHRASES/BUSINESS_PHRASES; "
                      "인도 hits immediately followed by a delivery-verb conjugation are excluded "
                      "(homonym: 인도하다 = 'to hand over')"),
           "corpus_note": "~953 KOSPI + ~1,998 KOSDAQ A001 filings/year; this run scoped to corp_cls="
                          + args.corp_cls,
           "count": len(prior), "results": list(prior.values())}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"swept this run: {len(todo)} | new leads (intent or business hit): {len(new_leads)} "
          f"| cumulative filings tracked: {len(prior)} -> {OUT}")


if __name__ == "__main__":
    main()
