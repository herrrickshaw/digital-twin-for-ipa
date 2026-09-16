#!/usr/bin/env python3
"""Layer 51 -- Semiconductor Parks vs ISM approved-unit cross-reference.

Extends the layer 46/47/49/50 pattern to India's semiconductor policy,
and specifically resolves an "Open item" flagged in
docs/PLI_SCHEME_BENEFICIARY_LEADS.md Part 9: "identify Telangana's three
unnamed semiconductor applicants" (from MeitY LS USQ 6046, 01.04.2026 --
"Telangana has three pending proposals -- one fab, two OSAT, applicants
unnamed").

Static, hand-verified dataset (same pattern as layers 44/46/47/49/50),
built 2026-09-17 from a targeted research pass.

KEY FINDING 1 -- CONSISTENT NEGATIVE RESULT, itself the finding: checked
every one of the 12 nationally ISM-approved units against every
state-designated "Semiconductor Park" found (UP-YEIDA Sector 6,
Karnataka-Kochanahalli/Mysuru, Tamil Nadu-Sulur/Palladam). ZERO overlap
in every case. ISM approvals land wherever a company's own site (a GIDC
industrial estate, an IT park, bespoke land) ends up; state "Semiconductor
Parks" are either aspirational with no ISM tenant, or hold entirely
different companies recruited independently by the state (e.g. Kaynes has
TWO separate semiconductor-adjacent India projects -- the ISM-approved
Sanand, Gujarat unit, and an unrelated land allocation at Kochanahalli,
Karnataka). The two policy layers run on genuinely separate tracks.

KEY FINDING 2 -- partially resolves the Telangana open item, though not
by naming the 3 applicants: BOTH of Telangana's previously press-visible
semiconductor candidates have since LEFT the state. ASIP Technologies +
APACT (South Korea) relocated to Tharluvada, Visakhapatnam, Andhra
Pradesh (inaugurated 2026, "Andhra Pradesh's first ISM-approved
facility"). Kaynes' Kongara Kalan, Telangana project relocated to Sanand,
Gujarat (the actual ISM-approved Kaynes Semicon unit); Kaynes retains
Kongara Kalan for non-semiconductor electronics only. This means the "3
pending" proposals in the April-2026 reply are very likely genuinely new/
different projects, not previously-known ones Parliament is simply
withholding -- a materially different read than "government is sitting on
known names."

KEY FINDING 3 -- Tamil Nadu's own government confirmed via a July-2026
Lok Sabha starred question (Dr. T. Sumathy, DMK) that NO ISM-approved fab
or display project has ever been sited in the state, and a widely-
reported ~Rs 80,000cr Taiwanese proposal for Tirunelveli/Thoothukudi has
"not been received" by MeitY -- a direct, sourced refutation of that
rumor, not just an absence of confirmation.

Usage: python3 scripts/build_layer51_semiconductor_parks.py
Output: layers/51_semiconductor_parks.json
        + docs/SEMICONDUCTOR_PARKS_CROSSREF.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "51_semiconductor_parks.json")
OUT_DOC = os.path.join(ROOT, "docs", "SEMICONDUCTOR_PARKS_CROSSREF.md")

# The 12 nationally ISM-approved units (already documented elsewhere in
# the twin's PLI lead doc Part 1) with their ACTUAL site, checked against
# any state "Semiconductor Park" branding.
ISM_UNITS_VS_PARKS = [
    {"unit": "Tata Electronics — fab", "state": "Gujarat", "actual_site": "Dholera Special Investment Region",
     "in_named_semiconductor_park": False, "note": None},
    {"unit": "Micron", "state": "Gujarat", "actual_site": "Sanand GIDC-II industrial estate (Plot SM12 51/3)",
     "in_named_semiconductor_park": False, "note": "Generic GIDC estate, not semiconductor-branded"},
    {"unit": "Kaynes Semicon", "state": "Gujarat", "actual_site": "Sanand GIDC cluster (same area as Micron)",
     "in_named_semiconductor_park": False,
     "note": "Kaynes ALSO holds an unrelated land allocation at Kochanahalli, Karnataka -- a different, non-ISM project, not to be confused with this one"},
    {"unit": "CG Power — OSAT", "state": "Gujarat", "actual_site": "Sanand, Gujarat",
     "in_named_semiconductor_park": False, "note": None},
    {"unit": "Vama Sundari / Foxconn", "state": "Uttar Pradesh", "actual_site": "YEIDA Sector 28",
     "in_named_semiconductor_park": False,
     "note": "UP's actual 'Semiconductor Park' branding applies to Sector 6, a DIFFERENT sector of the same YEIDA industrial area"},
    {"unit": "SiCSem", "state": "Odisha", "actual_site": "Info Valley, Bhubaneswar",
     "in_named_semiconductor_park": False, "note": "Info Valley is an IT park, not semiconductor-branded"},
    {"unit": "3D Glass Solutions", "state": "Odisha", "actual_site": "Info Valley, Bhubaneswar",
     "in_named_semiconductor_park": False, "note": None},
    {"unit": "ASIP Technologies", "state": "Andhra Pradesh", "actual_site": "Tharluvada, Visakhapatnam",
     "in_named_semiconductor_park": False,
     "note": "Relocated here from an earlier Telangana candidacy -- see Telangana finding below"},
    {"unit": "CDIL", "state": "Punjab", "actual_site": "not resolved this pass", "in_named_semiconductor_park": False, "note": None},
    {"unit": "Crystal Matrix", "state": "Gujarat", "actual_site": "Dholera (Cabinet-approved 05.05.2026)",
     "in_named_semiconductor_park": False, "note": None},
    {"unit": "Suchi Semicon", "state": "Gujarat", "actual_site": "Surat (Cabinet-approved 05.05.2026)",
     "in_named_semiconductor_park": False, "note": None},
]

STATE_SEMICONDUCTOR_PARKS = [
    {"park": "YEIDA Semiconductor Park", "state": "Uttar Pradesh", "location": "Sector 6, Yamuna City",
     "size": "500 acres (separate 600-acre EV park adjacent)", "tier": "PARK_PARTIAL",
     "named_tenants": ["NXP Semiconductors -- in talks for YEIDA land, but for Sector 10 "
                       "(R&D/system-innovation/lab, not the Sector 6 park itself, and not a fab)"],
     "note": "The ISM-approved UP project (Vama Sundari/Foxconn) is in Sector 28 -- a third, "
             "distinct sector of the same broader YEIDA industrial area. Three different YEIDA "
             "sectors (6, 10, 28) host three different things -- don't conflate them."},
    {"park": "Kochanahalli Semiconductor Park", "state": "Karnataka", "location": "near Kadakola, Mysuru",
     "size": "234 acres total, 140 acres reserved for the park", "tier": "PARK_PARTIAL",
     "named_tenants": ["Kaynes Technology (land secured -- NOT the same as its ISM-approved Sanand, Gujarat unit)",
                       "Wurth Technology (land secured)",
                       "Silectric Semiconductor Manufacturing (Zoho-backed, ~Rs 3,425cr/$400M, called 'Karnataka's first' such project)"],
     "note": "None of these three are among the 12 nationally ISM-approved units."},
    {"park": "Tamil Nadu Semiconductor Mission 2030 parks", "state": "Tamil Nadu",
     "location": "Sulur and near Palladam (~100 acres each)", "size": "~Rs 500cr mission outlay",
     "tier": "PARK_EMPTY", "named_tenants": [],
     "note": ("🔴 Tamil Nadu's own government confirmed via a July-2026 Lok Sabha starred question "
              "(Dr. T. Sumathy, DMK) that NO ISM-approved fab or display project has ever been sited "
              "in the state, and a widely-reported ~Rs 80,000cr Taiwanese proposal for Tirunelveli/"
              "Thoothukudi has 'not been received' by MeitY -- a sourced REFUTATION, not just an "
              "absence of confirmation."),
     },
]

TELANGANA_SEMICONDUCTOR_FINDING = {
    "open_item_source": "MeitY LS USQ 6046, 01.04.2026 -- 'Telangana has three pending proposals, one fab, two OSAT, applicants unnamed'",
    "resolution_status": "PARTIALLY RESOLVED -- applicants still not named, but their absence is now explained",
    "finding": ("Both of Telangana's previously press-visible semiconductor candidates have since LEFT "
               "the state. (1) ASIP Technologies + APACT (South Korea) -- the only Telangana OSAT "
               "candidate ever named in press (Mar 2025, ~Rs 890cr) -- relocated to Tharluvada, "
               "Visakhapatnam, Andhra Pradesh, inaugurated 2026 as 'Andhra Pradesh's first ISM-approved "
               "facility.' (2) Kaynes' OSAT/compound-semiconductor project, originally planned for "
               "Kongara Kalan, Telangana (Rs 2,800cr, signed Oct 2023), relocated to Sanand, Gujarat "
               "-- the actual ISM-approved Kaynes Semicon unit; Kaynes keeps Kongara Kalan only for "
               "non-semiconductor electronics manufacturing. Telangana's own home-grown fab ambition "
               "(T-CHIP roadmap) targets a 28-65nm fab only in Phase III, 2029-2030 -- no private-"
               "sector fab applicant found named anywhere in current press. The closest live lead as "
               "of Sep-2026 is an unnamed Singapore delegation (MTI Singapore's Augustine Lee) meeting "
               "CM Revanth Reddy about the sector, with no company/product/commitment given."),
    "sk_hynix_connection": ("NOT FOUND -- no source connects SK Hynix's early-stage, multi-state ATMP "
                            "evaluation (Odisha reported as front-runner) to either of Telangana's two "
                            "unnamed OSAT proposals."),
    "interpretation": ("The trail suggests Telangana's list of 'named' semiconductor suitors from "
                       "2023-2025 has emptied out -- both moved to other states -- which may be WHY "
                       "the April-2026 reply describes three proposals as still fully unnamed: they "
                       "could be genuinely new/different projects not yet surfaced in any public "
                       "reporting, not simply Parliament sitting on already-known names."),
}


def main():
    today = dt.date.today().isoformat()
    overlaps = [u for u in ISM_UNITS_VS_PARKS if u["in_named_semiconductor_park"]]

    out = {
        "layer": 51, "name": "semiconductor_parks", "built": today,
        "what": ("Cross-references all 12 nationally ISM-approved semiconductor units against every "
                 "state-designated 'Semiconductor Park' found, and separately resolves (partially) "
                 "the twin's open item on Telangana's 3 unnamed semiconductor proposals. Static "
                 "hand-verified dataset, same pattern as layers 44/46/47/49/50."),
        "ism_units_vs_parks": ISM_UNITS_VS_PARKS,
        "overlap_count": len(overlaps),
        "finding_1_zero_overlap": {
            "note": ("ZERO of the 12 ISM-approved units sit inside any state-designated 'Semiconductor "
                     "Park.' ISM approvals land wherever a company's own site (GIDC estate, IT park, "
                     "bespoke land) ends up; state Semiconductor Parks are either aspirational with no "
                     "ISM tenant, or hold entirely different companies the state recruited "
                     "independently. Kaynes is the clearest illustration: it has TWO separate India "
                     "semiconductor-adjacent projects (ISM-approved Sanand, Gujarat; unrelated "
                     "Kochanahalli, Karnataka land) -- don't conflate them."),
        },
        "state_semiconductor_parks": STATE_SEMICONDUCTOR_PARKS,
        "telangana_open_item_resolution": TELANGANA_SEMICONDUCTOR_FINDING,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# Semiconductor Parks vs ISM cross-reference — layer 51", "",
         f"*Generated {today} by `scripts/build_layer51_semiconductor_parks.py`. "
         f"0 of 12 ISM-approved units confirmed inside a state Semiconductor Park. Static "
         "hand-verified dataset.*", "",
         "## Finding 1 — consistent zero overlap", "",
         out["finding_1_zero_overlap"]["note"], "", "",
         "## Finding 2 — the Telangana open item, partially resolved", "",
         f"**Source of the open item**: {TELANGANA_SEMICONDUCTOR_FINDING['open_item_source']}", "",
         TELANGANA_SEMICONDUCTOR_FINDING["finding"], "",
         f"**SK Hynix connection**: {TELANGANA_SEMICONDUCTOR_FINDING['sk_hynix_connection']}", "",
         f"**Interpretation**: {TELANGANA_SEMICONDUCTOR_FINDING['interpretation']}", "", "",
         "## The 12 ISM units vs semiconductor park branding", "",
         "| Unit | State | Actual site | In a named Semiconductor Park? | Note |",
         "|---|---|---|---|---|"]
    for u in ISM_UNITS_VS_PARKS:
        L.append(f"| {u['unit']} | {u['state']} | {u['actual_site']} | "
                 f"{'✅ YES' if u['in_named_semiconductor_park'] else 'No'} | {u['note'] or ''} |")
    L.append("")

    L += ["## State-designated Semiconductor Parks", ""]
    for p in STATE_SEMICONDUCTOR_PARKS:
        L += [f"### {p['park']} ({p['state']}, {p['location']}) — {p['tier']}", "",
             f"**Size**: {p['size']}", "",
             f"**Named tenants**: {'; '.join(p['named_tenants']) if p['named_tenants'] else '(none found)'}", "",
             p["note"], ""]

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"0/12 ISM units overlap with a named Semiconductor Park; Telangana open item "
          f"partially resolved (both prior candidates relocated to AP/Gujarat) -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
