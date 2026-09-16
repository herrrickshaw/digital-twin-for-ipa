#!/usr/bin/env python3
"""Layer 47 -- Telangana/Hyderabad pharma cluster cross-reference.

Takes layer 46's 35 PLI Bulk Drugs companies and answers a geography
question layer 46 doesn't: which of them actually manufacture their
PLI-approved product in Telangana, and specifically, is any of it in the
much-publicized "Hyderabad Pharma City" (HPC) mega-project near Mucherla?

Static, hand-verified dataset (same pattern as layers 44/46) built from a
targeted per-company plant-location research pass (34 of 35 companies
resolved; company-website/about-us pages, MCA/Zaubacorp registered-office
data, and trade-press plant-inauguration coverage -- not a single official
list, because none exists in machine-readable form).

KEY FINDING: Hyderabad Pharma City (TSIIC, ~19,000 acres, Mucherla,
Rangareddy district) is repeatedly reported in the press as having
"committed" anchor tenants including Dr. Reddy's, Aurobindo Pharma, Hetero
Drugs, Laurus Labs and MSN Pharmaceuticals (~50-acre plots each) -- but
NONE of this layer's 35 resolved companies has their PLI-scheme plant
actually sited there. Aurobindo's PLI project (via Lyfius Pharma) is in
Kakinada SEZ, Andhra Pradesh; Hetero's and MSN's PLI plants are in
Telangana's OLDER established clusters (Bonthapally/Jinnaram, Jeedimetla,
Kamareddy), not Mucherla. Reconciles with a live 2026 political dispute:
the state government has been repurposing part of the Mucherla land into
a "Future City" (AI/skills/health hub), which the opposition calls "a
real estate venture" -- i.e. Pharma City's actual build-out remains
contested, not a settled industrial park with tenants moving in.

Usage: python3 scripts/build_layer47_telangana_pharma_cluster.py
Output: layers/47_telangana_pharma_cluster.json
        + docs/TELANGANA_PHARMA_CLUSTER_CROSSREF.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER46 = os.path.join(ROOT, "layers", "46_pli_bulk_drugs_commercial.json")
OUT_JSON = os.path.join(ROOT, "layers", "47_telangana_pharma_cluster.json")
OUT_DOC = os.path.join(ROOT, "docs", "TELANGANA_PHARMA_CLUSTER_CROSSREF.md")

# (company, state, plant_location, cluster, confidence, note)
# cluster values used for Telangana rows only; None elsewhere.
LOCATIONS = [
    ("Emmennar Pharma Pvt. Ltd.", "Telangana", "Sanath Nagar Industrial Estate, Hyderabad",
     "Sanath Nagar (established)", "HIGH", None),
    ("Hindys Lab Pvt. Ltd.", "Telangana", "Veliminedu, Chityal, Nalgonda district",
     "Nalgonda cluster", "HIGH", None),
    ("Alkimia Pharma-Chem Pvt Ltd", "Telangana", "Chiragpally, Zaheerabad, Sangareddy district",
     "Sangareddy corridor, near Pashamylaram", "HIGH", None),
    ("Anasia Lab Private Limited", "Telangana", "Dothi Gudem, B. Pochampally mandal, Nalgonda",
     "Nalgonda cluster", "HIGH", None),
    ("Honour Lab Limited", "Telangana", "Bonthapally, Jinnaram Mandal, Sangareddy district",
     "Bollaram/Jinnaram belt (established)", "HIGH", None),
    ("Dasami Lab Pvt. Ltd.", "Telangana", "Veliminedu, Chityal, Nalgonda",
     "Nalgonda cluster", "HIGH", None),
    ("Hetero Drugs Limited", "Telangana",
     "Bonthapally / Jeedimetla / Polepally-Jadcherla units (exact unit per-product not confirmed)",
     "Multiple established clusters", "MEDIUM",
     "Publicly 'committed' to Hyderabad Pharma City per press, but PLI-scheme plant sites are all in older established clusters, not Mucherla."),
    ("Hazelo Lab Pvt. Ltd.", "Telangana", "Dothi Gudem, B. Pochampally, Yadadri Bhuvanagiri district",
     "Nalgonda/Yadadri cluster", "HIGH", None),
    ("MSN Life Sciences Pvt. Ltd", "Telangana", "Chegunta / Kamareddy (reg. office Sanath Nagar)",
     "Kamareddy belt", "HIGH",
     "MSN group publicly 'committed' to Hyderabad Pharma City per press, but this PLI entity's plant is in the Kamareddy belt, not Mucherla."),
    ("Sreepathi Pharmaceuticals Limited", "Telangana",
     "Hyderabad (reg. office Jubilee Hills; a Chintal, Hyderabad facility also cited)",
     "Hyderabad city / Chintal (Jeedimetla-adjacent)", "MEDIUM", None),
    ("Granules India Limited", "Andhra Pradesh", "Kakinada, Andhra Pradesh", None, "MEDIUM",
     "Telangana-HEADQUARTERED (Hyderabad) but this PLI product (DCDA) is sited at the Kakinada, AP facility, not in Telangana."),
    ("Kreative Actives Private Limited", "Andhra Pradesh", "Rambilli, Visakhapatnam district", None, "HIGH",
     "Registered office Hyderabad, but manufacturing plant for Diclofenac Sodium is in Rambilli, AP, not Telangana."),
    ("Aurobindo Pharma Limited (through Lyfius Pharma Pvt. Ltd.)", "Andhra Pradesh",
     "Kakinada SEZ, Thondangi Mandal, Kakinada district", None, "HIGH",
     "Aurobindo is publicly 'committed' to Hyderabad Pharma City per press, but this PLI project (Penicillin G) is in Kakinada SEZ, AP."),
    ("Andhra Organics Limited", "Andhra Pradesh", "Pydibhimavaram, Ranasthalam, Srikakulam district", None, "HIGH", None),
    ("Macleods Pharmaceutical Limited", "Gujarat", "Daman (UT)/Sarigam border belt (exact PLI unit not pinned down)", None, "MEDIUM", None),
    ("Meghmani LLP", "Gujarat", "Dahej, Bharuch district", None, "HIGH", None),
    ("Aviran Pharmachem Private Limited", "Gujarat", "Saduthala, Kanoda, Mehsana district", None, "HIGH", None),
    ("Globela Industries Pvt. Ltd", "Gujarat", "Saykha, Vagra, Bharuch district", None, "HIGH", None),
    ("Vital Laboratories Private Limited", "Gujarat", "Phase III GIDC, Vapi", None, "HIGH", None),
    ("Amoli Organics Private Limited", "Gujarat", "GIDC, Vapi", None, "HIGH", None),
    ("Vapi Care Pharma Private Limited", "Gujarat",
     "Vapi (Unit 1); a Unit 2 exists in Baddi, HP -- which unit makes Diclofenac Sodium not confirmed",
     None, "MEDIUM", None),
    ("Sadhana Nitro Chem Ltd.", "Maharashtra", "Roha MIDC, Raigad district", None, "HIGH", None),
    ("RMC Performance Chemicals Private Limited", "Maharashtra", "MIDC, Jalgaon", None, "HIGH", None),
    ("Alta Laboratories Limited", "Maharashtra", "Khopoli, Raigad district", None, "MEDIUM",
     "Long-standing site; not confirmed as the specific PLI unit."),
    ("Sudarshan Pharma Industries Ltd.", "Maharashtra", "Mahad, Raigad district", None, "MEDIUM-HIGH", None),
    ("Karnataka Antibiotics and Pharmaceuticals Limited", "Madhya Pradesh",
     "DMIC Vikram Udyogpuri, Ujjain (HQ remains Peenya, Bengaluru)", None, "HIGH", None),
    ("Symbiotec Pharmalab Private Limited", "Madhya Pradesh", "Rau, Indore", None, "HIGH", None),
    ("Natural Biogenex Private Limited", "Karnataka", "KIADB Industrial Area, Vasanthanarsapura, Tumkur", None, "HIGH", None),
    ("K P Manish Global Ingredients Pvt. Ltd.", "Tamil Nadu", "Kawman Pharma plant, Cuddalore (HQ Chennai)", None, "MEDIUM", None),
    ("Global Pharma Healthcare Private Limited", "Tamil Nadu", "Alathur pharma industrial estate, near Chennai", None, "HIGH", None),
    ("Centrient Pharmaceuticals India Private Limited", "Punjab", "Toansa", None, "HIGH", None),
    ("Rajasthan Antibiotics Limited", "Rajasthan", "Bhiwadi", None, "MEDIUM",
     "Plant confirmed; PLI-specific tie-in for Meropenem not separately verified."),
    ("Kinvan Private Limited", "Himachal Pradesh", "Plassara Industrial Area, Nalagarh", None, "HIGH", None),
    ("Orchid Bio-Pharma Limited", "Jammu & Kashmir", "Village Gadadhar, Kathua district", None, "HIGH", None),
    ("Lifetech Sciences", None, None, None, None, "NOT FOUND -- no plant address or reliable company profile located after reasonable search; multiple unrelated 'Lifetech' entities surfaced instead."),
]

# Publicly reported (press, not an official machine-readable roster) as
# "committed"/anchor tenants of Hyderabad Pharma City (Mucherla) -- NONE
# of these have their PLI-scheme plant confirmed there (see LOCATIONS
# above); kept separate because this is company-level reputation, not a
# per-product fact.
HPC_ANCHOR_TENANTS_REPORTED = [
    "Dr. Reddy's Laboratories", "Aurobindo Pharma", "Hetero Drugs", "Laurus Labs",
    "MSN Pharmaceuticals", "Biocon", "Novartis",
]


def main():
    layer46 = json.load(open(LAYER46))
    known_companies = {p["company"] for p in layer46["company_projects"]}

    loc_by_company = {l[0]: l for l in LOCATIONS}
    unresolved = known_companies - set(loc_by_company)

    rows = []
    for company, state, plant, cluster, confidence, note in LOCATIONS:
        rows.append({
            "company": company, "state": state, "plant_location": plant,
            "telangana_cluster": cluster, "confidence": confidence, "note": note,
            "in_hyderabad_pharma_city_mucherla": False,  # true for zero rows -- see finding below
        })

    telangana_rows = [r for r in rows if r["state"] == "Telangana"]
    hq_telangana_plant_elsewhere = [r for r in rows if r["note"] and "HEADQUARTERED" in (r["note"] or "").upper()
                                     or (r["note"] and "Telangana" in r["note"] and r["state"] != "Telangana")]
    by_state = {}
    for r in rows:
        if r["state"]:
            by_state.setdefault(r["state"], []).append(r["company"])

    today = dt.date.today().isoformat()
    out = {
        "layer": 47, "name": "telangana_pharma_cluster", "built": today,
        "what": ("Cross-references layer 46's 35 PLI Bulk Drugs companies against actual plant "
                 "geography, to answer specifically: how much of this national scheme sits in "
                 "Telangana, and is any of it in the publicized Hyderabad Pharma City (Mucherla) "
                 "mega-project. Static hand-verified dataset (34 of 35 companies resolved), same "
                 "pattern as layers 44/46 -- not a live scrape."),
        "input_layer": "46_pli_bulk_drugs_commercial",
        "companies_resolved": len(LOCATIONS) - 1,  # minus Lifetech Sciences (not found)
        "companies_not_found": ["Lifetech Sciences"],
        "companies_by_state": by_state,
        "telangana_companies": [r["company"] for r in telangana_rows],
        "telangana_company_count": len(telangana_rows),
        "finding_hyderabad_pharma_city": {
            "companies_confirmed_at_mucherla_hpc": 0,
            "hpc_anchor_tenants_reported_in_press": HPC_ANCHOR_TENANTS_REPORTED,
            "note": ("Press repeatedly names Dr. Reddy's, Aurobindo Pharma, Hetero Drugs, Laurus "
                     "Labs, MSN Pharmaceuticals (~50-acre plots each), plus Biocon and Novartis, as "
                     "'committed' to Hyderabad Pharma City (TSIIC, ~19,000 acres, Mucherla, Rangareddy "
                     "district; 150 of 350+ interested firms secured Phase-1 land). But ZERO of this "
                     "layer's 35 resolved PLI Bulk Drugs companies has their actual plant there. "
                     "Aurobindo's PLI project (via Lyfius Pharma) is in Kakinada SEZ, Andhra Pradesh; "
                     "Hetero's and MSN's PLI plants are in Telangana's OLDER established clusters "
                     "(Bonthapally/Jinnaram, Jeedimetla, Kamareddy), not Mucherla. 'Committed to "
                     "Pharma City' and 'this specific product's actual current plant' are two "
                     "different facts, same trap as the twin's 'MoU graveyard' pattern (layer 44)."),
            "context_political_dispute": ("As of 2026, the state government has been repurposing part "
                                          "of the Mucherla land into a 'Future City' (AI/skills/health "
                                          "hub) -- the opposition BRS publicly calls this 'a real "
                                          "estate venture.' Pharma City's actual build-out status is "
                                          "politically contested, not a settled industrial park with "
                                          "tenants moving in."),
            "no_official_machine_readable_tenant_list": True,
        },
        "flagged_hq_vs_plant_mismatches": [
            {"company": r["company"], "hq_state": "Telangana", "plant_state": r["state"], "note": r["note"]}
            for r in rows if r["note"] and "HEADQUARTERED" in (r["note"] or "").upper()
        ],
        "company_locations": rows,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# Telangana/Hyderabad pharma cluster cross-reference — layer 47", "",
         f"*Generated {today} by `scripts/build_layer47_telangana_pharma_cluster.py`. "
         f"{out['companies_resolved']} of {len(known_companies)} layer-46 companies resolved to a plant location "
         f"({len(telangana_rows)} in Telangana); 1 not found (Lifetech Sciences). Static "
         "hand-verified dataset, not a live scrape.*", "",
         "## Headline finding: Hyderabad Pharma City has zero confirmed PLI Bulk Drugs tenants", "",
         "Press repeatedly names **Dr. Reddy's, Aurobindo Pharma, Hetero Drugs, Laurus Labs, "
         "MSN Pharmaceuticals** (plus Biocon, Novartis) as \"committed\" anchor tenants of "
         "Hyderabad Pharma City (TSIIC, ~19,000 acres near Mucherla, Rangareddy district; 150 of "
         "350+ interested firms secured Phase-1 land, ~50-acre plots each). **None of this layer's "
         "35 resolved companies has their actual PLI-scheme plant there.** Aurobindo's PLI project "
         "(via Lyfius Pharma) is in Kakinada SEZ, Andhra Pradesh. Hetero's and MSN's PLI plants sit "
         "in Telangana's older established clusters — not Mucherla.", "",
         "**Context**: as of 2026 the state government has been repurposing part of the Mucherla "
         "land into a \"Future City\" (AI/skills/health hub) — the opposition calls this \"a real "
         "estate venture.\" Pharma City's build-out remains politically contested, not a settled "
         "industrial park with tenants moving in. No official machine-readable tenant list exists.", ""]

    L += ["## Telangana companies (established clusters — not Pharma City)", "",
         "| Company | Plant Location | Cluster | Confidence | Note |",
         "|---|---|---|---|---|"]
    for r in telangana_rows:
        L.append(f"| {r['company']} | {r['plant_location']} | {r['telangana_cluster']} | "
                 f"{r['confidence']} | {r['note'] or ''} |")
    L.append("")

    L += ["## HQ-Telangana but plant elsewhere (flagged exceptions)", "",
         "| Company | Actual Plant State | Location | Note |", "|---|---|---|---|"]
    for r in rows:
        if r["note"] and "HEADQUARTERED" in (r["note"] or "").upper():
            L.append(f"| {r['company']} | {r['state']} | {r['plant_location']} | {r['note']} |")
    L.append("")

    L += ["## All other companies by state", "", "| State | Companies |", "|---|---|"]
    for state, companies in sorted(by_state.items(), key=lambda kv: -len(kv[1])):
        if state == "Telangana":
            continue
        L.append(f"| {state} | {', '.join(companies)} |")
    L.append("")
    L.append("**Not found**: Lifetech Sciences (Ritonavir) — no plant address or reliable company profile located.")
    L.append("")

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"{out['companies_resolved']}/{len(known_companies)} resolved, {len(telangana_rows)} in Telangana, "
          f"0 confirmed at Hyderabad Pharma City -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
