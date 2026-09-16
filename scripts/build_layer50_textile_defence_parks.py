#!/usr/bin/env python3
"""Layer 50 -- PM MITRA textile parks + Defence Industrial Corridors cross-reference.

Extends the layer 46/47/49 pattern to two more scheme/park pairs flagged
in docs/PLI_SCHEME_BENEFICIARY_LEADS.md as unresolved: 7B ("PM MITRA parks
(7): zero anchor-tenant names in any government document -- all
circulating names are news-only") and 7E (defence indigenisation, "3
confirmed JVs, everything else undisclosed").

Static, hand-verified dataset (same pattern as layers 44/46/47/49), built
2026-09-17 from a targeted research pass.

KEY FINDING 1 -- the cleanest dual-beneficiary case found across this
whole line of research: Youngone Corporation (Korea), via its Indian
subsidiary Evertop Textile & Apparel Complex Pvt Ltd, is SIMULTANEOUSLY
(a) a named PLI Textiles beneficiary and (b) the confirmed, operating
anchor tenant of the Kakatiya Mega Textile Park, Warangal, Telangana --
groundbreaking 17.06.2023, commercial production confirmed by press as of
Oct 2025. This resolves the "zero anchor-tenant names" claim for at least
one of the 7 PM MITRA parks with hard, dated, multi-sourced evidence.

KEY FINDING 2 -- Vardhman Textiles at Dhar, MP is moderately confirmed
(190 acres, ~Rs 2,000cr, named in a Sep-2025 state-government-sourced
report) but NOT independently verified against a primary PIB/Ministry of
Textiles allotment order. Welspun is NOT confirmed as a tenant at any of
the 7 parks -- the twin's prior skepticism holds for that name specifically.

KEY FINDING 3 -- Tamil Nadu's Defence Industrial Corridor has two real,
operating (not MoU-stage) foreign-JV facilities: LTMMSL (L&T 51% / MBDA
France 49%, missile subsystem assembly) and Merlinhawk Composites (JV
with Vega Composites, Italy, aerostructures at Shoolagiri). Uttar
Pradesh's corridor remains opaque -- no foreign-parented tenant found,
consistent with the twin's existing note on defence-sector non-disclosure.

Usage: python3 scripts/build_layer50_textile_defence_parks.py
Output: layers/50_textile_defence_parks.json
        + docs/TEXTILE_DEFENCE_PARKS_CROSSREF.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "50_textile_defence_parks.json")
OUT_DOC = os.path.join(ROOT, "docs", "TEXTILE_DEFENCE_PARKS_CROSSREF.md")

PM_MITRA_PARKS = [
    {"state": "Tamil Nadu", "site": "Virudhunagar (E. Kumaralingapuram)", "type": "Greenfield",
     "size": "1,052 acres", "named_tenants": [], "tier": "PARK_EMPTY"},
    {"state": "Telangana", "site": "Warangal (Kakatiya Mega Textile Park)", "type": "Brownfield",
     "size": "1,350 acres", "tier": "PARK_PARTIAL",
     "named_tenants": ["Evertop Textile & Apparel Complex Pvt Ltd (Youngone Corporation, Korea) -- "
                       "groundbreaking 17.06.2023, ~Rs 900cr+, 290 acres, 11 factories; commercial "
                       "production confirmed Oct 2025, exporting T-shirts, ~90% local women workforce. "
                       "ALSO a named PLI Textiles beneficiary -- the one clean dual-scheme case found."]},
    {"state": "Gujarat", "site": "Navsari (Vansi-Borsi village)", "type": "Greenfield",
     "size": "462 hectares", "named_tenants": [], "tier": "PARK_EMPTY"},
    {"state": "Karnataka", "site": "Kalaburagi", "type": "Greenfield",
     "size": "DPR cleared, no size found", "named_tenants": [], "tier": "PARK_EMPTY"},
    {"state": "Madhya Pradesh", "site": "Dhar (Bhainsola village)", "type": "Greenfield",
     "size": "2,158 acres", "tier": "PARK_PARTIAL",
     "named_tenants": ["Vardhman Textiles (190 acres, ~Rs 2,000cr -- named in a Sep-2025 "
                       "state-government-sourced report; NOT independently verified against a "
                       "primary PIB/Ministry of Textiles allotment order)",
                       "AB Cotspin India (45 acres, ~Rs 1,300cr)",
                       "Trident Company (180 acres, ~Rs 4,881cr)",
                       "(part of a reported '91 prominent companies' collectively allotted ~1,300 acres)"]},
    {"state": "Uttar Pradesh", "site": "Lucknow-Hardoi (730 ac Lucknow + 270 ac Hardoi)", "type": "Greenfield",
     "size": "1,000 acres", "named_tenants": [], "tier": "PARK_EMPTY"},
    {"state": "Maharashtra", "site": "Amravati", "type": "Brownfield",
     "size": "1,020 acres", "named_tenants": [], "tier": "PARK_EMPTY"},
]

# Corrected foreign-parented PLI Textiles roster: the twin's PLI_SCHEME_
# BENEFICIARY_LEADS.md 7B previously named 5; research found the real
# count is 7 (Evertop/Youngone and Avgol/Teejay were missing).
PLI_TEXTILES_FOREIGN = [
    {"company": "Evertop Textile & Apparel Complex Pvt Ltd (Youngone Corporation)", "country": "South Korea",
     "plant_location": "Kakatiya Mega Textile Park, Warangal, Telangana",
     "in_pm_mitra_park": True, "note": "The one confirmed dual PLI-textiles + PM-MITRA-tenant case"},
    {"company": "Kimberly Clark India", "country": "United States",
     "plant_location": "Sanaswadi/Pune (Maharashtra), Sricity (Andhra Pradesh)", "in_pm_mitra_park": False, "note": None},
    {"company": "Autoliv India", "country": "Sweden",
     "plant_location": "Bengaluru, Mysuru, Badli, Cheyyar, Pune", "in_pm_mitra_park": False, "note": None},
    {"company": "Toray International India", "country": "Japan",
     "plant_location": "Chennai, Chittoor (AP), Mumbai (HQ)", "in_pm_mitra_park": False, "note": None},
    {"company": "Rane TRW Steering Systems (JV, now Rane/ZF)", "country": "Germany/United States",
     "plant_location": "Trichy, Guduvanchery, Pudukkottai, Chengalpattu (TN, not Virudhunagar), Rudrapur (Uttarakhand)",
     "in_pm_mitra_park": False, "note": None},
    {"company": "HS Hyosung India / HS Hyosung Advanced Materials", "country": "South Korea",
     "plant_location": "Aurangabad (AURIC complex), Nagpur/Butibori, Pune -- all Maharashtra, not Amravati",
     "in_pm_mitra_park": False, "note": None},
    {"company": "Avgol India", "country": "Israel (Indorama Ventures-owned)", "plant_location": "not resolved this pass",
     "in_pm_mitra_park": False, "note": "Newly identified in this pass; location not yet researched"},
    {"company": "Teejay India", "country": "Sri Lanka", "plant_location": "not resolved this pass",
     "in_pm_mitra_park": False, "note": "Newly identified in this pass; location not yet researched"},
]

DEFENCE_CORRIDORS = [
    {
        "corridor": "Tamil Nadu Defence Industrial Corridor",
        "nodes": ["Chennai", "Coimbatore", "Hosur", "Salem", "Tiruchirappalli"],
        "tier": "PARK_PARTIAL",
        "named_tenants": [
            "LTMMSL (L&T 51% / MBDA, France, 49%) -- operating missile-subsystem assembly, integration and testing facility, not MoU-stage",
            "Merlinhawk Composites (JV, Merlinhawk Aerospace India + Vega Composites, Italy) -- advanced-composites aerostructures facility at Shoolagiri",
        ],
        "note": "Two real, hardware-on-the-ground foreign JVs -- past the MoU stage, unlike most of the defence sector's disclosure pattern.",
    },
    {
        "corridor": "Uttar Pradesh Defence Industrial Corridor",
        "nodes": ["Agra", "Aligarh", "Chitrakoot", "Jhansi", "Kanpur", "Lucknow"],
        "tier": "PARK_EMPTY",
        "named_tenants": [],
        "note": "Not found -- search surfaced only aggregate MoU figures (108 MoUs, ~Rs 12,191cr potential investment; ~Rs 50,000cr in MoUs at a 2020 Defence Expo), no specific foreign-parented company confirmed as actually operating. Consistent with the twin's existing note on defence-sector opacity (section 7E).",
    },
]


def main():
    today = dt.date.today().isoformat()
    pm_mitra_partial = [p for p in PM_MITRA_PARKS if p["tier"] == "PARK_PARTIAL"]

    out = {
        "layer": 50, "name": "textile_defence_parks", "built": today,
        "what": ("Cross-references PLI Textiles' foreign-parented beneficiaries against the 7 PM "
                 "MITRA mega textile parks, and separately researches foreign-JV tenancy in India's "
                 "2 Defence Industrial Corridors -- both flagged as unresolved in "
                 "docs/PLI_SCHEME_BENEFICIARY_LEADS.md sections 7B and 7E. Static hand-verified "
                 "dataset, same pattern as layers 44/46/47/49."),
        "pm_mitra_parks": PM_MITRA_PARKS,
        "pm_mitra_parks_with_named_tenants": len(pm_mitra_partial),
        "pm_mitra_parks_total": len(PM_MITRA_PARKS),
        "pli_textiles_foreign_corrected_roster": PLI_TEXTILES_FOREIGN,
        "pli_textiles_foreign_correction_note": ("docs/PLI_SCHEME_BENEFICIARY_LEADS.md 7B previously "
                                                 "named 5 foreign-parented PLI Textiles companies; the "
                                                 "real count is 7 -- Evertop/Youngone and Avgol/Teejay "
                                                 "were missing."),
        "finding_youngone_dual_beneficiary": {
            "note": ("Evertop Textile & Apparel Complex (Youngone Corporation, Korea) is SIMULTANEOUSLY "
                     "a named PLI Textiles beneficiary AND the confirmed, operating anchor tenant of "
                     "the Warangal PM MITRA park -- groundbreaking 2023, commercial production "
                     "confirmed Oct 2025. The cleanest dual-scheme case found across this entire line "
                     "of cross-reference work (layers 47/49/50)."),
        },
        "welspun_not_confirmed": True,
        "defence_industrial_corridors": DEFENCE_CORRIDORS,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# PM MITRA + Defence Corridors cross-reference — layer 50", "",
         f"*Generated {today} by `scripts/build_layer50_textile_defence_parks.py`. "
         f"{len(pm_mitra_partial)} of {len(PM_MITRA_PARKS)} PM MITRA parks have a confirmed named "
         "tenant; 1 of 2 Defence Industrial Corridors has confirmed foreign-JV tenants. Static "
         "hand-verified dataset.*", "",
         "## Headline finding: Youngone/Evertop, the cleanest dual-beneficiary case yet", "",
         out["finding_youngone_dual_beneficiary"]["note"], "", "",
         "## PM MITRA — 7 parks", "",
         "| State | Site | Type | Size | Tier | Named tenants |", "|---|---|---|---|---|---|"]
    for p in PM_MITRA_PARKS:
        tenants = "; ".join(p["named_tenants"]) if p["named_tenants"] else "(none found)"
        L.append(f"| {p['state']} | {p['site']} | {p['type']} | {p['size']} | {p['tier']} | {tenants} |")
    L.append("")

    L += ["## PLI Textiles — corrected foreign-parented roster (7, not 5)", "",
         "| Company | Country | Plant Location | In a PM MITRA park? | Note |",
         "|---|---|---|---|---|"]
    for c in PLI_TEXTILES_FOREIGN:
        L.append(f"| {c['company']} | {c['country']} | {c['plant_location']} | "
                 f"{'✅ YES' if c['in_pm_mitra_park'] else ''} | {c['note'] or ''} |")
    L.append("")
    L.append("**Welspun**: not confirmed as a tenant at any of the 7 PM MITRA parks — the twin's prior skepticism holds for this name specifically.")
    L.append("")

    L += ["## Defence Industrial Corridors", ""]
    for c in DEFENCE_CORRIDORS:
        L += [f"### {c['corridor']} — {c['tier']}", "",
             f"**Nodes**: {', '.join(c['nodes'])}", "",
             f"**Named tenants**: {'; '.join(c['named_tenants']) if c['named_tenants'] else '(none found)'}", "",
             c["note"], ""]

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"{len(pm_mitra_partial)}/{len(PM_MITRA_PARKS)} PM MITRA parks with named tenants, "
          f"1/2 defence corridors with foreign-JV tenants -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
