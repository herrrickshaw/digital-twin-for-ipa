#!/usr/bin/env python3
"""Layer 24 — leads mined from the PARIVESH clearance registers, news-verified.

A NEW lead-generation channel, and a stronger one than announcement-scanning:
a company with a LIVE environmental/forest clearance filing is not merely
talking about investing -- it has paid fees, filed EIA paperwork and put a
site on record. The register is the intent; the news check tells us which of
these verified investors are in the public limelight and which are QUIET.

Pipeline (all 2025-26 filings, live statuses only):
  EC register (majorClearanceType=1, 113,981 rows) -> manufacturing activities
  only (metallurgy, cement, chemicals, pharma API, pesticides, fertilizer,
  petrochemicals...) -> corporate proponents (persons and govt agencies
  stripped) -> dedup against the 321 companies already in layers/16_leads.json
  -> top filers + foreign-linked FC filers (Jio-bp, Nayara/Rosneft, HMEL)
  -> 3-agent public-news sweep -> ANNOUNCED / PARTIALLY_VISIBLE / QUIET.

Inputs (scratchpad): clearance_lead_shortlist.json, news_batch{1,2,3}.json
Output: layers/24_clearance_leads.json
"""
import datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = ("/private/tmp/claude-501/-Users-umashankar/"
           "0c3e9924-9f05-4396-80c8-81c306920b86/scratchpad")


def norm(name):
    n = name.lower()
    # canonicalise legal-suffix variants so 'JSW Steel Ltd' == 'Jsw Steel Limited'
    n = re.sub(r"\b(limited|ltd\.?|private|pvt\.?|llp|the)\b", "", n)
    n = re.sub(r"\(.*?\)", "", n)  # drop parentheticals like '(Adani group)'
    return re.sub(r"[^a-z0-9]", "", n)[:24]


def main():
    short = json.load(open(os.path.join(SCRATCH, "clearance_lead_shortlist.json")))
    news = {}
    for f in ("news_batch1.json", "news_batch2.json", "news_batch3.json"):
        p = os.path.join(SCRATCH, f)
        if os.path.exists(p):
            for r in json.load(open(p)):
                news[norm(r["company"])] = r

    leads, unmatched = [], []
    for s in short:
        n = news.get(norm(s["company"]))
        if n is None:  # fuzzy: try containment either way
            for k, v in news.items():
                if k[:12] in norm(s["company"]) or norm(s["company"])[:12] in k:
                    n = v
                    break
        rec = {
            "company": s["company"],
            "clearance_evidence": {
                "filings_2025_26": s["filings"],
                "activities": s.get("activities", {}),
                "states": s.get("states", {}),
                "latest_filing": s["latest_filing"],
                "register": s.get("source", "EC register"),
            },
        }
        if s.get("note"):
            rec["note"] = s["note"]
        if n:
            rec["news_verdict"] = n.get("verdict")
            rec["news_summary"] = n.get("news_summary")
            rec["match_with_filings"] = n.get("match_with_filings")
            rec["best_source_url"] = n.get("best_source_url")
            if n.get("announced_capex_rs_cr"):
                rec["announced_capex_rs_cr"] = n["announced_capex_rs_cr"]
        else:
            rec["news_verdict"] = "UNCHECKED"
            unmatched.append(s["company"])
        leads.append(rec)

    counts = {}
    for r in leads:
        counts[r["news_verdict"]] = counts.get(r["news_verdict"], 0) + 1
    out = {
        "layer": 24,
        "name": "clearance_register_leads",
        "built": datetime.date.today().isoformat(),
        "method": ("PARIVESH EC/FC registers (2025-26 filings, live statuses, manufacturing "
                   "activities, corporate proponents only, deduped against layer 16's 321 leads) "
                   "-> public-news sweep -> visibility verdict. A clearance filing is stronger "
                   "evidence of intent than an announcement: fees paid, EIA filed, site on record."),
        "why_quiet_matters": ("QUIET = verified investment intent with NO public announcement -- "
                              "the same below-radar category the PIB-visibility work found most "
                              "valuable for investment-promotion targeting."),
        "verdict_counts": counts,
        "leads": leads,
        "unmatched_in_news_sweep": unmatched,
        "candidate_pool": {"ec_corporate_filers_2025_26": 1445,
                           "after_dedup_vs_layer16": 1723,
                           "note": ("shortlist is the TOP of a 1,445-company pool of live corporate "
                                    "industrial filers -- the pool file (scratchpad ec_lead_candidates.json) "
                                    "supports deeper batches")},
    }
    p = os.path.join(ROOT, "layers/24_clearance_leads.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"layer 24: {len(leads)} leads | verdicts {counts} | unmatched {len(unmatched)}")


if __name__ == "__main__":
    main()
