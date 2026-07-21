#!/usr/bin/env python3
"""Fold trade-press verification into the PIB visibility map (layer 19).

The PIB match answers "does the government headline this company?". It cannot
answer "is the company actually doing anything in India?" -- for that we went to
the trade press. Merging the two produces the classification that is actually
useful for targeting:

    HEADLINED        PIB names it in an investment release -- already courted
    STATE_PUBLICISED real activity, publicised by a STATE government or a
                     minister in person, but absent from PIB headlines
    QUIET_INVESTOR   real, dated, sourced India activity and no government
                     publicity found at all  <-- the outreach list
    BLOCKED_PN3      Chinese-domiciled; activity is refusal/exit/Indianisation
                     under Press Note 3, not inbound investment
    NO_ACTIVITY      verified intent in the annual report, but no dated India
                     activity in the 3-year window (intent has not converted)
    DIRECTION_INBOUND the traceable flow runs India->company, not company->India

CORRECTIONS ARE APPLIED, NOT HIDDEN. Where the news check proved a "BELOW_RADAR"
label wrong -- Cameco's CAD 2.6bn DAE contract was signed with the PM present,
Ma'aden's was minister-fronted on state TV -- the record keeps the original PIB
result, the correction, and the reason, because the PIB register indexes titles
only and that limit is exactly what these cases expose.
"""
import datetime, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = ("/private/tmp/claude-501/-Users-umashankar/"
           "0c3e9924-9f05-4396-80c8-81c306920b86/scratchpad")
NEWS = ["news_below_radar_eu.json", "news_below_radar_asia.json", "news_below_radar_row.json"]

# Corrections established by the news check, with the evidence that forced them.
CORRECTIONS = {
    "Cameco": ("HEADLINED", "PIB title match missed it: the CAD 2.6bn / 22M-lb uranium "
               "contract with the Dept of Atomic Energy was signed at a Delhi event attended "
               "by the PM and the Canadian PM -- publicised, just not in a PIB headline"),
    "Ma'aden": ("HEADLINED", "minister-fronted (signed during J.P. Nadda's Saudi visit, "
                "carried by DD News, the state broadcaster); also offtake, not Indian capex"),
}
PN3 = {"BYD", "Luxshare", "Hikvision", "Haier", "Midea", "SAIC"}


def classify(c):
    name = c["company"]
    for key, (verdict, why) in CORRECTIONS.items():
        if key.lower() in name.lower():
            return verdict, why
    act = (c.get("activity_type") or "").lower()
    note = (c.get("govt_visibility_note") or "") + " " + (c.get("summary_line") or "")
    if any(p.lower() in name.lower() for p in PN3):
        return "BLOCKED_PN3", c.get("summary_line", "")[:300]
    if act in ("none", ""):
        return "NO_ACTIVITY", c.get("summary_line", "")[:300]
    if act == "bid":
        return "NO_ACTIVITY", "campaign/bid only, not a committed investment: " + c.get("summary_line", "")[:240]
    if "inbound" in note.lower() or "wrong direction" in note.lower():
        return "DIRECTION_INBOUND", c.get("summary_line", "")[:300]
    # State publicity must be ASSERTED, not merely mentioned. The researchers write
    # "No minister or state government publicity found" -- a naive keyword scan reads
    # that as publicity and inverts the finding, so match a government actor bound to
    # an action verb, and let an explicit negation veto it.
    g = c.get("govt_visibility_note", "") or ""
    negated = re.search(r"\b(no|zero|not)\s+(\w+\s+){0,3}"
                        r"(minister|ministerial|state|government|pib|publicity)", g, re.I)
    asserted = re.search(r"(chief minister|\bCM\b|minister|state government|"
                         r"[A-Z][a-z]+ (Pradesh|Nadu|government))\s+(\w+\s+){0,4}"
                         r"(attended|approved|publicis|inaugurat|announced|fronted|witness|"
                         r"laid|handed|allotted)", g, re.I) or g.strip().startswith("FLAG:")
    if asserted and not (negated and not g.strip().startswith("FLAG:")):
        return "STATE_PUBLICISED", g[:300]
    return "QUIET_INVESTOR", c.get("summary_line", "")[:300]


def main():
    vis = json.load(open(os.path.join(ROOT, "layers/19_pib_visibility.json")))
    by_name = {r["company"]: r for r in vis["all"]}

    merged, missing = [], []
    for f in NEWS:
        path = os.path.join(SCRATCH, f)
        if not os.path.exists(path):
            missing.append(f)
            continue
        for c in json.load(open(path))["companies"]:
            verdict, why = classify(c)
            # link back to the lead record by loose name match
            lead = next((r for k, r in by_name.items()
                         if k.lower().startswith(c["company"].split()[0].lower())), None)
            merged.append({
                "company": c["company"], "country": c.get("country"),
                "sector": (lead or {}).get("sector"),
                "india_intent": (lead or {}).get("india_intent"),
                "pib_visibility": (lead or {}).get("visibility", "UNKNOWN"),
                "pib_investment_hits_3y": (lead or {}).get("pib_investment_hits_3y", 0),
                "verdict": verdict, "verdict_basis": why,
                "activity_type": c.get("activity_type"),
                "india_news": c.get("india_news", []),
                "govt_visibility_note": c.get("govt_visibility_note", ""),
                "summary": c.get("summary_line", ""),
            })

    order = ["QUIET_INVESTOR", "STATE_PUBLICISED", "HEADLINED", "BLOCKED_PN3",
             "DIRECTION_INBOUND", "NO_ACTIVITY"]
    merged.sort(key=lambda r: (order.index(r["verdict"]) if r["verdict"] in order else 9,
                               -len(r["india_news"])))
    counts = {}
    for r in merged:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    doc = {"layer": "visibility_news_verified", "built": datetime.date.today().isoformat(),
           "window": vis["window"],
           "method": ("PIB headline match (layer 19) x trade-press verification of India activity. "
                      "Verdicts reconcile the two: a company absent from PIB headlines may still be "
                      "loudly publicised by a state government, blocked under Press Note 3, or simply "
                      "inactive -- only the residue is a genuine quiet investor."),
           "corrections_applied": [{"company": k, "to": v[0], "reason": v[1]}
                                   for k, v in CORRECTIONS.items()],
           "counts": counts, "companies": merged}
    if missing:
        doc["clusters_missing"] = missing
    json.dump(doc, open(os.path.join(ROOT, "layers/20_visibility_verified.json"), "w"), indent=1)

    print(f"merged {len(merged)} companies" + (f" (MISSING: {missing})" if missing else ""))
    for k in order:
        if counts.get(k):
            print(f"  {k:<18} {counts[k]}")
    print("\nQUIET INVESTORS (real activity, no government publicity found):")
    for r in merged:
        if r["verdict"] == "QUIET_INVESTOR":
            n = r["india_news"][0] if r["india_news"] else {}
            print(f"  {r['company'][:30]:30} {str(r['country'])[:12]:12} {str(n.get('date'))[:10]} "
                  f"{str(n.get('headline'))[:60]}")
    return doc


if __name__ == "__main__":
    main()
