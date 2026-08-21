#!/usr/bin/env python3
"""cninfo (巨潮资讯网) India-sweep -- China A-share filing discovery, sibling to
build_edgar_india_sweep.py and build_dart_india_sweep.py.

Unlike DART, cninfo DOES have a real full-text search API: POST
cninfo.com.cn/new/hisAnnouncement/query, tabName=fulltext, no key, JSON
response -- confirmed live 2026-08-09, 200 OK. Architecturally this is
clone-EDGAR-easy, not clone-DART-medium.

BUT two things make raw output unreliable, both confirmed live:
  1. Precision hazard -- NOT a Korean-style verb homonym but a SUBSTRING
     collision: 印度尼西亚 ("Indonesia") starts with 印度 ("India"). Worse,
     cninfo's search is NOT exact-phrase like EDGAR's efts.sec.gov -- it's
     tokenized/fuzzy, so querying "在印度投资" (invest in India) returned 19
     hits of which the TOP 3 were Indonesia-only announcements (CATL/宁德时代,
     蔚蓝锂芯, 上海凤凰 -- all Indonesia battery/subsidiary projects) whose
     titles don't contain "在印度投资" as a literal substring at all. Every
     result is filtered locally: title must contain 印度 NOT immediately
     followed by 尼西亚 (regex `印度(?!尼西亚)`).
  2. Actionability -- these are Mainland China A-share (SSE/SZSE) listed
     companies. This twin's own build_target_leads.py already treats China
     as a SEPARATE Press Note 3 watch-list, not an outreach-target pool.
     🔴 PN3 was AMENDED 10-Mar-2026 (Cabinet, PIB PRID=2237806; gazetted as
     Press Note 2 of 2026 ~15-Mar-2026) -- it no longer routes ALL Chinese
     FDI through government approval: non-controlling stakes <=10% are now
     automatic-route, and 5 specified manufacturing sectors (capital goods,
     electronic capital goods, electronic components, polysilicon,
     ingot-wafer) get a 60-day government-route fast-track IF majority
     control stays with resident Indian citizens/entities. These 86 hits
     are wholly-owned-subsidiary establishments (设立子公司) -- controlling
     by construction -- so they fall OUTSIDE both relaxed lanes and the
     watch-list placement stands; see layers/16_leads.json's
     china_pn3_policy_update for the full reconstruction. Matches here are
     written to the SAME watch-list bucket, never mixed into actionable
     new-lead output.

Response gives title/secCode/secName/PDF path only, NOT a body-text snippet
(announcementContent was empty in live testing) -- so this v1 filters on
TITLE text only. A title that doesn't mention India even when the body does
will be missed; downloading and grepping each matching PDF (like the DART
sweep's document.xml step) would close that gap but isn't built here.

Usage: python3 scripts/build_cninfo_india_sweep.py [--max-pages-per-phrase 3]
Output: layers/16_enrichment/cninfo_india_sweep.json
"""
import argparse
import datetime as dt
import json
import os
import re
import time
import urllib.parse

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "16_enrichment", "cninfo_india_sweep.json")

QUERY_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")
HEADERS = {"User-Agent": UA,
           "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
           "Content-Type": "application/x-www-form-urlencoded"}

INTENT_PHRASES = ["印度设立", "印度建厂", "印度投资设立子公司", "印度子公司",
                  "印度工厂", "在印度投资", "印度产能", "印度基地"]

# 印度尼西亚 (Indonesia) starts with 印度 (India) -- exclude that collision.
INDIA_HIT_RE = re.compile(r"印度(?!尼西亚)")


def query_page(phrase: str, page: int) -> dict:
    r = requests.post(QUERY_URL, headers=HEADERS, data={
        "tabName": "fulltext", "searchkey": phrase, "column": "szse",
        "pageNum": page, "pageSize": 30,
    }, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages-per-phrase", type=int, default=3)
    args = ap.parse_args()

    seen_ids = set()
    hits, excluded_indonesia = [], 0

    for phrase in INTENT_PHRASES:
        page = 1
        while page <= args.max_pages_per_phrase:
            try:
                d = query_page(phrase, page)
            except Exception as e:
                print(f"  {phrase} page {page}: ERROR {type(e).__name__}: {e}")
                break
            anns = d.get("announcements") or []
            if not anns:
                break
            for a in anns:
                aid = a.get("announcementId")
                title = a.get("announcementTitle") or ""
                if not INDIA_HIT_RE.search(title):
                    excluded_indonesia += 1
                    continue
                if aid in seen_ids:
                    continue
                seen_ids.add(aid)
                hits.append({
                    "company": a.get("secName"), "sec_code": a.get("secCode"),
                    "title": title, "matched_phrase": phrase,
                    "pdf_url": ("http://static.cninfo.com.cn/" + a["adjunctUrl"]
                               if a.get("adjunctUrl") else None),
                    "announcement_time": a.get("announcementTime"),
                })
            total = d.get("totalAnnouncement", 0)
            if page * 30 >= total:
                break
            page += 1
            time.sleep(0.4)
        time.sleep(0.4)

    out = {"layer": "16_enrichment/cninfo_india_sweep", "built": dt.date.today().isoformat(),
           "method": ("cninfo.com.cn full-text search (keyless, real API, confirmed live -- "
                      "NOT exact-phrase, tokenized/fuzzy, so every hit is title-filtered for "
                      "genuine 印度 mentions excluding the 印度尼西亚/Indonesia substring collision). "
                      "Title-only filter -- body text (PDF) not downloaded/verified in this v1."),
           "china_pn3_note": ("Press Note 3 (2020) requires government approval for land-border-"
                              "country FDI; AMENDED 10-Mar-2026 (Cabinet, PIB PRID=2237806; "
                              "gazetted as Press Note 2 of 2026 ~15-Mar-2026) -- <=10% "
                              "non-controlling stakes now automatic-route, and 5 manufacturing "
                              "sectors (capital goods, electronic capital goods, electronic "
                              "components, polysilicon, ingot-wafer) get a 60-day government-route "
                              "fast-track if majority control stays Indian. These hits are "
                              "controlling wholly-owned-subsidiary establishments (设立子公司), "
                              "outside both relaxed lanes -- watch-list placement stands, matching "
                              "build_target_leads.py's existing china_pn3_watchlist convention. "
                              "Full policy detail: layers/16_leads.json china_pn3_policy_update."),
           "excluded_indonesia_false_positives": excluded_indonesia,
           "count": len(hits), "china_pn3_watchlist": hits}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"genuine India hits: {len(hits)} | excluded as Indonesia false-positives: {excluded_indonesia} -> {OUT}")
    for h in hits[:15]:
        print(f"  {h['company']} ({h['sec_code']}) -- {h['title']}")


if __name__ == "__main__":
    main()
