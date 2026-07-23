#!/usr/bin/env python3
"""Fisheries re-query of the PARIVESH EC register (layer 33 follow-up).

The layer-24 pool showed ZERO seafood EC-filers. This re-query settles whether
that is a query gap or structural. Route discovered 2026-07-23:

  - the PUBLIC MIS dashboard API is OPEN (no auth):
      GET https://parivesh.nic.in/admin_api/dashboard/getProposals
          ?fromDate&toDate&status=Received|Granted&is_state=true|false&page&size
    (ledger/advanceSearch + globalSearch are 401 token-gated; the dashboard
    drill-down is the anonymous surface)
  - activity taxonomy: POST parivesh_api/activity/action/getAll -> 46 EC
    activities. STRUCTURAL FINDING: the EIA-2006 schedule has NO fisheries /
    aquaculture / seafood-processing category — closest touchpoints are
    7(e) Ports/harbors (fishing harbours) and 7(c) industrial estates
    (aqua/food parks). Seafood processing is regulated via state PCB
    consent (CTE/CTO) + CAA registration, NOT central EC.

This script sweeps Received+Granted × central+state proposals for a date
window and greps project names for fisheries terms, writing findings into the
layer 33 fisheries block (requery_2026_07 key).

Usage: python3 scripts/parivesh_fisheries_requery.py [--from 2025-01-01] [--to today]
"""
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER = os.path.join(ROOT, "layers", "33_policy_finance_extensions.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
BASE = "https://parivesh.nic.in/admin_api/dashboard/getProposals"

TERMS = re.compile(
    r"fish|seafood|sea food|shrimp|prawn|aqua ?cultur|hatcher|surimi|"
    r"maricultur|molluscs?|crustacean", re.I)
HARBOUR = re.compile(r"harbou?r", re.I)


def fetch(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=40).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", default="2025-01-01")
    ap.add_argument("--to", dest="to", default=date.today().isoformat())
    ap.add_argument("--size", type=int, default=500)
    args = ap.parse_args()

    # 🔴 the API IGNORES page/size — every call returns the COMPLETE result
    # set for the window/status (this is layer 08's "one API call"). Fetch
    # ONCE per combination and dedupe by proposal_no; never loop pages.
    hits, harbour_hits = [], []
    seen = set()
    scanned = 0
    for status in ("Received", "Granted"):
        for is_state in ("false", "true"):
            try:
                d = fetch({"fromDate": args.frm, "toDate": args.to,
                           "status": status, "is_state": is_state})
            except Exception as e:
                print(f"  fetch error {status}/{is_state}: {type(e).__name__}")
                continue
            rows = d.get("data") or []
            fresh = 0
            for r in rows:
                pno = r.get("proposal_no")
                key = (pno, status)
                if key in seen:
                    continue
                seen.add(key)
                fresh += 1
                name = r.get("project_name") or ""
                act = r.get("activity_name") or ""
                rec = {"project": name[:120], "activity": act,
                       "state": r.get("state_name"), "proposal_no": pno,
                       "status": status,
                       "authority": "state" if is_state == "true" else "central",
                       "investment_cost": r.get("investment_cost")}
                if TERMS.search(name):
                    hits.append(rec)
                elif HARBOUR.search(name) and "Ports" in act:
                    harbour_hits.append(rec)
            scanned += fresh
            print(f"  {status}/{'state' if is_state=='true' else 'central'}: "
                  f"{len(rows)} rows, {fresh} unique")
            time.sleep(1)

    result = {
        "ran": date.today().isoformat(),
        "window": f"{args.frm}..{args.to}",
        "rows_scanned": scanned,
        "route": ("OPEN public MIS dashboard API admin_api/dashboard/getProposals "
                  "(ledger/globalSearch are 401); activity taxonomy via "
                  "parivesh_api/activity/action/getAll"),
        "structural_finding": ("EIA-2006 schedule (46 EC activities) has NO "
                               "fisheries/aquaculture/seafood category — seafood "
                               "processing sits under state-PCB consent + CAA, not "
                               "central EC. The layer-24 zero is STRUCTURAL, not a "
                               "query gap."),
        "name_term_hits": hits,
        "fishing_harbour_hits_7e": harbour_hits,
    }
    layer = json.load(open(LAYER))
    layer["fisheries"]["requery_2026_07"] = result
    with open(LAYER, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    print(f"\nscanned {scanned} | term hits {len(hits)} | harbour hits {len(harbour_hits)}")
    for h in hits[:20]:
        print(f"  [{h['status']}/{h['authority']}] {h['project'][:70]} | {h['activity'][:40]} | {h['state']}")
    for h in harbour_hits[:10]:
        print(f"  HARBOUR: {h['project'][:70]} | {h['state']}")


if __name__ == "__main__":
    main()
