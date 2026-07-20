#!/usr/bin/env python3
"""Leads generation: verified-profitable listed firms x the government's open incentive lanes.

Inputs:
  - focus-sector-investor-map/data/focus_sector_companies_final.csv (147 names,
    yfinance-verified profitable: profit_margin>0 AND roe>0; expansion signal =
    revenue growth >=10% or 1y return >=25%)
  - This repo's instrument layers (curated sector->lane map below, statuses from
    the flat index / sweeps)

Scoring (0-100):
  profitability 40 (margin 20 + roe 20, capped) + expansion 25 + lane openness 25
  (open window in the matched central lane) + state top-up available 10

Output:
  layers/16_leads.json + docs/LEADS.md (generated view -- never hand-edit)

Enrichment (contacts) is a SEPARATE, deliberate step: each lead carries an
`enrichment` block naming the roles to pull from Lusha/Apollo (no API wired here;
the Apollo MCP connector needs claude.ai auth, Lusha has no connector). No personal
data is collected by this script.
"""
import json, os, datetime
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.expanduser("~/focus-sector-investor-map/data/focus_sector_companies_final.csv")

# Curated: FocusSector -> central lanes (with open/closed status from the twin) + state top-up landings
LANES = {
 "Electronics & Semiconductors": {
   "central": [("ECMS", "open -- Rs 40,000cr outlay, FCFS"), ("MPMS", "approved 15-Jul-2026, Rs 62,500cr"),
               ("Semicon 2.0 / ISM 2.0", "approved 15-Jul-2026, Rs 1.27L cr"), ("SPECS", "legacy 25% capex")],
   "states": ["UP (ECMS top-up = equal to central)", "Assam (+40% of ISM capex)", "TN (Semiconductor 2024 + Mission 2030)", "Gujarat (semicon ancillary thrust)"]},
 "Green Energy & Fuels": {
   "central": [("NGHM SIGHT", "electrolyser + GH2/ammonia windows via SECI"), ("BESS VGF via PSDF", "Jul-2025"),
               ("PM-KUSUM / Surya Ghar supply chain", "e-2W E-DRIVE closes 31-Jul-2026"), ("Ethanol/SATAT", "multi-feedstock conversions open")],
   "states": ["Odisha (GH2: 20y power package, uncapped 30% capital)", "Gujarat (green-energy thrust 25-40% eFCI)", "Rajasthan (RIPS boosters)"]},
 "Pharma & Bulk Drugs": {
   "central": [("PLI Pharma / bulk drug parks", "operational"), ("PRIP", "R&D push"), ("TDB Rare Disease CFP", "open")],
   "states": ["Telangana Next-Gen Life Sciences 2026-30 (full stack)", "Himachal (Nalagarh ecosystem)", "Sikkim (legacy hub)"]},
 "Medical Devices": {
   "central": [("PLI Medical Devices + parks", "operational"), ("TDB Medical Devices CFP", "open")],
   "states": ["Telangana LS 2026-30", "TN (structured packages)", "HP medical-device park"]},
 "Aerospace & Defence": {
   "central": [("iDEX/ADITI", "DISC 12 reopen; ADITI to Rs 25cr/project"), ("Make-I/II", "live EOIs: Viraj 03-Aug, TAC 15-Aug"),
               ("SRIJAN/PIL", "assured import-substitution demand"), ("Defence corridors UP/TN", "land + capex")],
   "states": ["Karnataka A&D 2022-27", "UP Defence Corridor (UPEIDA)", "TN aerospace packages"]},
 "Auto, EV & Components": {
   "central": [("PM E-DRIVE", "e-2W claims close 31-Jul-2026; e-3W to 2028; STACKS with PLI-Auto/ACC in scheme terms"),
               ("PLI-Auto / PLI-ACC", "operational")],
   "states": ["TN EV 2023 (20% battery capital subsidy)", "MP EV 2025", "UP EV 2022 + upevsubsidy portal"]},
 "Chemicals & Plastics": {
   "central": [("PCPIR framework", "partial"), ("TDB Chemical CFP", "open"), ("Gujarat thrust-sector chemicals", "25-40% eFCI")],
   "states": ["Gujarat (chemicals thrust)", "Odisha IPR (priority sector)", "Rajasthan RIPS"]},
 "Specialty Steel & Metals": {
   "central": [("PLI Specialty Steel", "operational (AM/NS precedent)"), ("Critical minerals mission / MMDR-2025", "exploration+processing openings")],
   "states": ["Odisha (metals downstream parks, 50% infra to Rs 25cr)", "Chhattisgarh (core-sector stack)", "Jharkhand JIIPP"]},
 "Textiles & Apparel": {
   "central": [("PM MITRA parks", "operational"), ("RoSCTL", "apparel/made-ups rebate (exclusive vs RoDTEP)"), ("Technical textiles mission", "open")],
   "states": ["TN Textile 2025-26 + MMF scheme", "Gujarat Textile 2024", "Maharashtra Textile 2023-28", "UP Textile 2022"]},
 "Food Processing": {
   "central": [("PLI-FPI", "operational"), ("PMKSY", "convergence with AIF 3% subvention"), ("AIF", "portal OPEN, Rs 94,272cr sanctioned"), ("TDB Agriculture CFP", "open")],
   "states": ["AP Food Processing 4.0", "MP (IPP + food parks)", "Jharkhand Food & Feed 2024"]},
 "White Goods & Electricals": {
   "central": [("PLI White Goods", "operational (85->80 attrition noted)"), ("BEE/star-rating demand levers", "standing")],
   "states": ["Standard state stacks (UP/Gujarat/TN capital+SGST menus)"]},
 "Shipbuilding & Marine": {
   "central": [("SBFAS 2.0", "to 31-Mar-2036, 15-25% of vessel cost"), ("Maritime Development Fund", "Rs 25,000cr incl. IIF Rs 5,000cr"),
               ("SbDS", "Rs 19,989cr capacity building"), ("Ports/shipping bills 2024-25", "legal modernisation done")],
   "states": ["Gujarat (shipping-container thrust + scrapping)", "AP/TN coastal packages"]},
}

ENRICH_ROLES = ["CFO", "Head of Corporate Development / M&A", "VP Strategy / New Markets",
                "India Country Head (if exists)", "Head of Government Affairs"]


def build():
    df = pd.read_csv(SRC)
    leads = []
    for _, r in df.iterrows():
        lane = LANES.get(r.FocusSector, {"central": [], "states": []})
        open_lane = any(k in s.lower() for _, s in lane["central"] for k in ("open", "approved", "live", "operational"))
        score = (min(float(r.profit_margin or 0), 0.25) / 0.25 * 20 +
                 min(float(r.roe or 0), 0.30) / 0.30 * 20 +
                 (25 if bool(r.expansion_signal) else 0) +
                 (25 if open_lane else 10) +
                 (10 if lane["states"] else 0))
        leads.append({
            "company": r.Name, "ticker": r.Symbol, "market": r.Market, "country": r.Country,
            "sector": r.FocusSector, "region": r.Region,
            "profitability": {"margin": round(float(r.profit_margin), 4) if pd.notna(r.profit_margin) else None,
                               "roe": round(float(r.roe), 4) if pd.notna(r.roe) else None,
                               "revenue_growth": round(float(r.revenue_growth), 4) if pd.notna(r.revenue_growth) else None},
            "expansion_signal": bool(r.expansion_signal),
            "lead_score": round(score, 1),
            "central_lanes": [{"instrument": n, "status": s} for n, s in lane["central"]],
            "state_landings": lane["states"],
            "enrichment": {"status": "PENDING", "provider": "Lusha or Apollo (Apollo MCP connector available but unauthenticated; Lusha has no connector -- manual export)",
                            "roles_to_pull": ENRICH_ROLES},
        })
    leads.sort(key=lambda x: -x["lead_score"])
    out = {"layer": "leads_generation", "built": datetime.date.today().isoformat(),
           "method": "yfinance-verified profitable (margin>0 AND roe>0) x curated open-lane map; score = profitability 40 + expansion 25 + open central lane 25 + state top-up 10. Contact enrichment is a separate deliberate step (no personal data collected here).",
           "source": "focus-sector-investor-map/data/focus_sector_companies_final.csv (147 verified names from the 19,795-company catalog)",
           "count": len(leads), "leads": leads}
    json.dump(out, open(os.path.join(ROOT, "layers/16_leads.json"), "w"), indent=1)

    lines = ["# Leads — profitable firms × open government lanes", "",
             f"*Generated {datetime.date.today().isoformat()} by `scripts/build_leads.py` — do not hand-edit. "
             "Contact enrichment (Lusha/Apollo) is a separate step; no personal data here.*", ""]
    for sector in df.FocusSector.unique():
        sec = [l for l in leads if l["sector"] == sector]
        lanes = LANES.get(sector, {})
        lines += [f"## {sector} ({len(sec)} leads)", "",
                  "**Lanes**: " + "; ".join(f"{n} ({s})" for n, s in lanes.get("central", [])), "",
                  "**State landings**: " + "; ".join(lanes.get("states", [])), "",
                  "| Score | Company | Ticker | Country | Margin | ROE | Growth | Expanding |", "|---|---|---|---|---|---|---|---|"]
        for l in sec[:8]:
            p = l["profitability"]
            lines.append(f"| {l['lead_score']} | {l['company']} | {l['ticker']} | {l['country']} | "
                         f"{p['margin']:.1%} | {p['roe']:.1%} | {(p['revenue_growth'] if p['revenue_growth'] is not None else 0):.1%} | {'✅' if l['expansion_signal'] else ''} |")
        lines.append("")
    open(os.path.join(ROOT, "docs/LEADS.md"), "w").write("\n".join(lines))
    print(f"leads: {len(leads)} -> layers/16_leads.json + docs/LEADS.md | top: "
          + ", ".join(f"{l['company']} ({l['lead_score']})" for l in leads[:3]))


if __name__ == "__main__":
    build()
