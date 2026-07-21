#!/usr/bin/env python3
"""Merge staged annual-report sweep clusters into layers/16_leads.json.

Each cluster file (scratchpad/apac_*.json) holds companies whose latest annual
report was mined for India/APAC investment language, graded HIGH/MEDIUM/LOW/NONE
with verbatim evidence. This script folds new clusters into the leads layer using
the SAME scoring as the original build (profitability 40 + expansion 25 + open
central lane 25 + state top-up 10), then leaves rendering to build_leads.py
--render and build_target_leads.py.

Companies already in the layer (matched on ticker, else name) are skipped, so a
re-run is idempotent. Unprofitable names a cluster deliberately excluded stay
excluded -- they live in the cluster file's own excluded_* block, not here.

    python3 scripts/merge_cluster_leads.py                 # merge all clusters
    python3 scripts/merge_cluster_leads.py --only apac_asean.json
    python3 scripts/merge_cluster_leads.py --dry-run
"""
import argparse, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = ("/private/tmp/claude-501/-Users-umashankar/"
           "0c3e9924-9f05-4396-80c8-81c306920b86/scratchpad")
LEADS = os.path.join(ROOT, "layers/16_leads.json")

# clusters added in this round (the earlier ones are already merged into the layer)
NEW_CLUSTERS = ["apac_asean.json", "apac_gulf_mena.json", "apac_latam.json",
                "apac_europe_tail.json", "apac_tr_nz.json"]


def lanes_for(sector, build_leads_lanes):
    return build_leads_lanes.get(sector, {"central": [], "states": []})


def score(company, lane):
    """Same formula as build_leads.build(): profitability 40 + expansion 25 +
    open lane 25 (else 10) + state top-up 10. Missing profitability scores 0 for
    that component rather than dropping the lead (cluster files mark UNVERIFIED
    where an exchange has no yfinance coverage)."""
    p = company.get("profitability") or {}
    margin, roe = p.get("margin"), p.get("roe")
    open_lane = any(k in s.lower() for _, s in lane["central"]
                    for k in ("open", "approved", "live", "operational", "closes"))
    return round(
        (min(float(margin), 0.25) / 0.25 * 20 if isinstance(margin, (int, float)) else 0)
        + (min(float(roe), 0.30) / 0.30 * 20 if isinstance(roe, (int, float)) else 0)
        + (25 if company.get("expansion_signal") else 0)
        + (25 if open_lane else 10)
        + (10 if lane["states"] else 0), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", help="cluster filename(s) to merge")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from build_leads import LANES, ENRICH_ROLES

    idx = json.load(open(LEADS))
    seen_t = {(l.get("ticker") or "").upper() for l in idx["leads"]}
    seen_n = {l["company"].strip().lower() for l in idx["leads"]}

    wanted = args.only or NEW_CLUSTERS
    added, skipped, missing = [], [], []
    for name in wanted:
        path = os.path.join(SCRATCH, name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        cluster = json.load(open(path))
        for c in cluster.get("companies", []):
            tick, cname = (c.get("ticker") or "").upper(), c["company"].strip().lower()
            if (tick and tick in seen_t) or cname in seen_n:
                skipped.append(c["company"])
                continue
            lane = lanes_for(c.get("sector", ""), LANES)
            lead = {
                "company": c["company"], "ticker": c.get("ticker"),
                "market": c.get("market"), "country": c.get("country"),
                "sector": c.get("sector"), "region": c.get("region", "Foreign"),
                "profitability": c.get("profitability") or {},
                "expansion_signal": bool(c.get("expansion_signal")),
                "lead_score": score(c, lane),
                "central_lanes": [{"instrument": n, "status": s} for n, s in lane["central"]],
                "state_landings": lane["states"],
                "enrichment": {"status": "PENDING",
                               "provider": "Lusha or Apollo (Apollo MCP connector unauthenticated)",
                               "roles_to_pull": ENRICH_ROLES},
                "india_apac_interest": c.get("india_apac_interest") or {},
                "source_cluster": cluster.get("cluster", name.replace(".json", "")),
            }
            if c.get("notes"):
                lead["notes"] = c["notes"]
            idx["leads"].append(lead)
            seen_t.add(tick); seen_n.add(cname)
            added.append(lead)

    idx["leads"].sort(key=lambda x: -x["lead_score"])
    idx["count"] = len(idx["leads"])
    idx["clusters_merged"] = sorted(set(idx.get("clusters_merged", []))
                                    | {l["source_cluster"] for l in added})
    if not args.dry_run:
        json.dump(idx, open(LEADS, "w"), indent=1)

    print(f"merged {len(added)} new leads (skipped {len(skipped)} already present)"
          f" -> {idx['count']} total{' [DRY RUN]' if args.dry_run else ''}")
    if missing:
        print("  MISSING cluster files (not merged):", ", ".join(missing))
    for l in sorted(added, key=lambda x: -x["lead_score"])[:12]:
        lvl = (l["india_apac_interest"] or {}).get("level", "?")
        print(f"  {l['lead_score']:>6}  {lvl:<7} {l['company'][:38]:38} {l['country']}")


if __name__ == "__main__":
    main()
