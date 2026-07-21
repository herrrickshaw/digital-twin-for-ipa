#!/usr/bin/env python3
"""Foreign-investor targeting shortlist: leads layer filtered to non-India companies
with VERIFIED India/APAC intent, ranked for outreach.

Input:  layers/16_leads.json (263 leads; annual-report deep-dives for non-US names,
        SEC 10-K mention mining for US names)
Output: layers/16_target_shortlist.json + docs/TARGET_LEADS.md (generated -- never hand-edit)

Targeting score = lead_score (profitability/expansion/open-lane, 0-100)
                + India-intent bonus:
    non-US:  HIGH +30, MEDIUM +15  (LOW/NONE excluded from the shortlist)
    US 10-K: min(india_mentions,20)*1.5, +5 if mentions trending up YoY
             tier HIGH if >=8 mentions (or >=5 and rising), MEDIUM if >=4

China leads are listed separately: Press Note 3 (2020) routes ALL their FDI through
government approval, so they are watch-list counterparties, not outreach targets.

Interest levels reflect what each company's own latest report says about India --
absence of India language (e.g. TSMC: zero) is recorded, not imputed.
"""
import datetime, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def classify(l):
    """Return (tier, bonus, evidence) or None if not shortlistable."""
    ia = l.get("india_apac_interest") or {}
    if "level" in ia:                                   # annual-report deep-dive
        ev = (ia.get("evidence") or [""])[0]
        if ia["level"] == "HIGH":
            return "HIGH", 30, ev
        if ia["level"] == "MEDIUM":
            return "MEDIUM", 15, ev
        return None
    if ia:                                              # US 10-K mention mining
        m, tr = ia.get("india_mentions") or 0, ia.get("india_trend_yoy") or 0
        ev = (ia.get("investment_sentences") or ia.get("india_sentences") or [""])[0]
        bonus = min(m, 20) * 1.5 + (5 if tr > 0 else 0)
        if m >= 8 or (m >= 5 and tr > 0):
            return "HIGH", bonus, ev
        if m >= 4:
            return "MEDIUM", bonus, ev
    return None


def open_lane(l):
    for c in l["central_lanes"]:
        s = c["status"].lower()
        if any(k in s for k in ("open", "approved", "live", "closes")):
            return f'{c["instrument"]} ({c["status"]})'
    return "; ".join(c["instrument"] for c in l["central_lanes"][:2]) or "(no mapped lane)"


def main():
    src = json.load(open(os.path.join(ROOT, "layers/16_leads.json")))
    targets, pn3 = [], []
    for l in src["leads"]:
        if l["country"] == "India":
            continue
        c = classify(l)
        if not c:
            continue
        tier, bonus, ev = c
        row = {
            "company": l["company"], "ticker": l["ticker"], "country": l["country"],
            "sector": l["sector"], "tier": tier,
            "target_score": round(l["lead_score"] + bonus, 1),
            "evidence": ev[:220], "why_now": open_lane(l),
            "state_landings": l["state_landings"][:3],
            "roles_to_approach": l["enrichment"]["roles_to_pull"],
        }
        (pn3 if l["country"] == "China" else targets).append(row)
    targets.sort(key=lambda r: (r["tier"] != "HIGH", -r["target_score"]))
    pn3.sort(key=lambda r: -r["target_score"])

    out = {"layer": "target_shortlist", "built": datetime.date.today().isoformat(),
           "method": ("foreign leads only; targeting score = lead_score + verified India-intent bonus "
                      "(annual-report level or 10-K mention weight); China separated under Press Note 3"),
           "source": "layers/16_leads.json", "count": len(targets), "china_pn3_count": len(pn3),
           "targets": targets, "china_pn3_watchlist": pn3}
    json.dump(out, open(os.path.join(ROOT, "layers/16_target_shortlist.json"), "w"), indent=1)

    t1 = [r for r in targets if r["tier"] == "HIGH"]
    t2 = [r for r in targets if r["tier"] == "MEDIUM"]
    L = ["# Target leads — foreign companies with verified India intent", "",
         f"*Generated {datetime.date.today().isoformat()} by `scripts/build_target_leads.py` from "
         f"`layers/16_leads.json` — do not hand-edit. {len(t1)} priority + {len(t2)} warm targets across "
         f"{len({r['country'] for r in targets})} countries; {len(pn3)} China names held on the Press Note 3 "
         "watch-list. Evidence quotes are from each company's own latest annual report / 10-K. "
         "Contact enrichment (Lusha/Apollo) remains a separate, deliberate step — no personal data here.*", "",
         "## Tier 1 — priority targets (stated India intent)", ""]
    for i, r in enumerate(t1, 1):
        L += [f"**{i}. {r['company']}** ({r['ticker']}, {r['country']}) — {r['sector']} — score {r['target_score']}",
              f"- Evidence: {r['evidence']}",
              f"- Why now: {r['why_now']}",
              f"- Landing states: {'; '.join(r['state_landings'])}",
              f"- Approach: {', '.join(r['roles_to_approach'][:3])}", ""]
    L += ["## Tier 2 — warm (APAC-committed, India-adjacent)", "",
          "| Score | Company | Country | Sector | Why now |", "|---|---|---|---|---|"]
    for r in t2:
        L.append(f"| {r['target_score']} | {r['company'][:38]} | {r['country']} | {r['sector'][:28]} | "
                 f"{r['why_now'][:70].replace('|','/')} |")
    L += ["", "## China — Press Note 3 watch-list (not outreach targets)", "",
          "> " + src.get("china_pn3_note", "")[:500], ""]
    for r in pn3:
        L.append(f"- **{r['company']}** ({r['sector']}, score {r['target_score']}) — {r['evidence'][:160]}")
    open(os.path.join(ROOT, "docs/TARGET_LEADS.md"), "w").write("\n".join(L) + "\n")
    print(f"targets: {len(t1)} HIGH + {len(t2)} MEDIUM + {len(pn3)} PN3 -> layers/16_target_shortlist.json + docs/TARGET_LEADS.md")
    for r in targets[:10]:
        print(f"  {r['target_score']:>6}  {r['company'][:40]:40} {r['country'][:14]:14} {r['sector']}")


if __name__ == "__main__":
    main()
