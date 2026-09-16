#!/usr/bin/env python3
"""Layer 48 -- State pharma/medtech/textile/semiconductor cluster registry.

A reference layer answering one recurring question the twin keeps having
to re-derive per-company (layer 47 did it once, by hand, for Telangana):
"is this company's plant in a real, established manufacturing cluster, an
announced park with unofficially-named tenants, or a genuinely empty
announced park?" Catalogues both flavors so future sessions check this
registry instead of re-researching cluster-by-cluster.

Static, hand-verified dataset (same pattern as layers 44/46/47) built from
a targeted research pass, 2026-09-17. Three tiers:

  ESTABLISHED -- real, large, long-operating clusters with named major
  tenants and (where findable) an aggregate scale figure.
  PARK_PARTIAL -- a government-allocated industrial park where official
  Parliament answers say "no allottee names published," but state-level
  press/trade coverage has independently named specific tenant companies
  anyway (a real finding: the non-disclosure stance is informally
  bypassed for some parks, not others).
  PARK_EMPTY -- an announced/approved park with zero confirmed tenants
  found by any source, official or press.

Usage: python3 scripts/build_layer48_state_pharma_clusters.py
Output: layers/48_state_pharma_clusters.json
        + docs/STATE_PHARMA_CLUSTER_REGISTRY.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "48_state_pharma_clusters.json")
OUT_DOC = os.path.join(ROOT, "docs", "STATE_PHARMA_CLUSTER_REGISTRY.md")

CLUSTERS = [
    {
        "name": "Baddi-Barotiwala-Nalagarh (BBN)", "state": "Himachal Pradesh",
        "tier": "ESTABLISHED",
        "scale": "~600-800 active pharma manufacturing units (estimates vary by source); often cited as Asia's largest pharma hub, ~35-45% of India's drug formulations / claimed ~35% of Asia's pharma output",
        "notable_companies": ["Abbott", "Cipla", "Cadila (Zydus)", "GlaxoSmithKline (GSK)", "Glenmark",
                              "Dr Reddy's", "Torrent", "Unichem", "Wockhardt", "Sun Pharma (ex-Ranbaxy sites)"],
        "sources": ["https://bbnda.hp.gov.in/AboutUs.aspx",
                    "https://www.innovexia.com/top-50-pharma-companies-in-baddi-asias-pharma-powerhouse",
                    "https://medellasoftgel.com/himachal-pradesh-pharma-manufacturing-hub/"],
    },
    {
        "name": "Sikkim pharma cluster", "state": "Sikkim", "tier": "ESTABLISHED",
        "scale": "~14 major pharma companies (a smaller, more concentrated cluster than BBN); ~₹2,500 crore cumulative pharma investment cited industry-wide",
        "notable_companies": ["Cipla (Kumrek/Rangpo, operating since 2018, plus Unit-II Rorathang)",
                              "Sun Pharma", "Zydus Healthcare", "Alembic", "Glenmark", "Alkem",
                              "Mankind Pharma", "Macleods"],
        "sources": ["https://www.researchgate.net/publication/376513670_An_Overview_of_Pharmaceutical_Industries_in_Sikkim"],
    },
    {
        "name": "Jawaharlal Nehru Pharma City (JNPC), Parawada", "state": "Andhra Pradesh",
        "tier": "ESTABLISHED",
        "scale": "~120 units within JNPC itself, ~150-250 across greater Vizag; ~38 WHO-approved, ~20 US FDA-approved facilities; >20,000 employed. JNPC alone: 104+ industries on 2,400 acres per APIIC official docs",
        "notable_companies": ["Divi's Laboratories (Unit-II, Chippada, ~350 acres -- world's largest API manufacturing site)",
                              "Aurobindo Pharma", "Hetero Drugs", "Pfizer", "Mylan/Matrix Labs",
                              "Gland Pharma", "Granules India", "Natco Pharma", "Eisai Pharma Technology"],
        "sources": ["https://en.wikipedia.org/wiki/Jawaharlal_Nehru_Pharma_City",
                    "https://apiic.in/wp-content/themes/custom-theme/assets/uploads/ppp/JNPC.pdf",
                    "https://www.divislabs.com/pharmaceutical-company/world-largest-api-manufacturing-facility/"],
    },
    {
        "name": "Ankleshwar chemical/pharma cluster", "state": "Gujarat", "tier": "ESTABLISHED",
        "scale": "~600 chemical units (SIDBI cluster report, the most rigorous source found) within a ~1,200-unit MSME estate; other, less rigorous estimates cite up to 1,500 chemical/pharma units",
        "notable_companies": ["Zydus Cadila / Zydus Lifesciences (API plant, GIDC Phase 1)"],
        "sources": ["https://www.sidbi.in/uploads/posts/Cluster-Profile-Report---Ankleshwar-(Chemical)-Cluster.pdf"],
    },
    {
        "name": "Vapi GIDC industrial estate", "state": "Gujarat", "tier": "ESTABLISHED",
        "scale": "No consolidated hard unit-count found; confirmed active via multiple large listed-company operating plants, long-standing GIDC estate; a major API/bulk-drug satellite of the Ankleshwar cluster",
        "notable_companies": ["Sun Pharmaceutical Industries (Phase-III GIDC, USFDA-inspected Dec 2023)",
                              "Cadila/Zydus", "Lupin", "Megafine (API manufacturer)"],
        "sources": ["https://redica.com/document-store/sites/siteprofile/100003961/sun-pharmaceutical-industries-limited-vapi-india"],
    },
    {
        "name": "Pithampur / Indore SEZ Pharma Zone", "state": "Madhya Pradesh", "tier": "ESTABLISHED",
        "scale": "~300 pharma manufacturing units (largely within Pithampur/Indore SEZ), ~20,000 employed; MP statewide has 280+ pharma units overall, of which this is the largest single concentration. 🚩 No Pfizer facility confirmed here despite that being a common assumption -- only Cipla and Ipca independently verified.",
        "notable_companies": ["Ipca Laboratories (SEZ Pithampur, USFDA-inspected)",
                              "Lupin (Units II & III, Indore SEZ)", "Cipla (Unit-II)", "Glenmark",
                              "Torrent Pharma", "Aurobindo Pharma"],
        "sources": ["https://indoresez.gov.in/Docspdf/ListofunitinIndoreSEZ.pdf"],
    },
    {
        "name": "Hyderabad established pharma clusters (Bollaram/Jinnaram, Nalgonda/Yadadri, Sanath Nagar, Kamareddy, Jeedimetla)",
        "state": "Telangana", "tier": "ESTABLISHED",
        "scale": "10 of 35 layer-46 PLI Bulk Drugs companies confirmed here (see layer 47); no independent aggregate unit-count sourced this session",
        "notable_companies": ["Honour Lab (Bonthapally/Jinnaram)", "Hetero Drugs (multiple units)",
                              "MSN Life Sciences (Kamareddy belt)", "Emmennar Pharma (Sanath Nagar)"],
        "sources": ["layers/47_telangana_pharma_cluster.json"],
    },
    {
        "name": "Hyderabad Pharma City (Mucherla)", "state": "Telangana", "tier": "PARK_EMPTY",
        "scale": "~19,000 acres (TSIIC); 150 of 350+ interested firms secured Phase-1 land per press, but ZERO confirmed actual tenants among 35 researched PLI Bulk Drugs companies (layer 47); build-out politically contested as of 2026 (partial land repurposed to 'Future City')",
        "notable_companies": ["Press names Dr. Reddy's/Aurobindo/Hetero/Laurus Labs/MSN as 'committed' anchors -- none confirmed as actually built there"],
        "sources": ["layers/47_telangana_pharma_cluster.json"],
    },
    {
        "name": "UP Medical Device Park (YEIDA, Greater Noida)", "state": "Uttar Pradesh",
        "tier": "PARK_PARTIAL",
        "scale": "101 units allotted per Parliament answer; Parliament also states 'no allottee names published' -- but state/trade press independently names tenants (see layer 49)",
        "notable_companies": ["Auzein Medical", "Heidelco Medicore", "Q Line Biotech", "Ramsons Group",
                              "Genuince Medica", "Krish Biomedical (first unit inaugurated)"],
        "sources": ["layers/49_medical_devices_parks.json"],
    },
    {
        "name": "MP Medical Device Park (Ujjain)", "state": "Madhya Pradesh", "tier": "PARK_PARTIAL",
        "scale": "74 units allotted per Parliament answer, officially unnamed -- but MPIDC/trade press names tenants across 2023-2025 coverage (see layer 49)",
        "notable_companies": ["Sheba Industries India", "Clinisupplies India", "Medqverse", "HC Lifeline",
                              "Hariva Meditech", "Bioline India"],
        "sources": ["layers/49_medical_devices_parks.json"],
    },
    {
        "name": "TN Medical Device Park (Oragadam/SIPCOT)", "state": "Tamil Nadu", "tier": "PARK_PARTIAL",
        "scale": "35 units allotted per Parliament answer, officially unnamed; 🔴 corrected same day after a deeper research pass -- Polymatech Electronics Ltd confirmed as an allottee via its own press release (99-year lease for additional adjacent land)",
        "notable_companies": ["Polymatech Electronics Ltd"],
        "sources": ["layers/49_medical_devices_parks.json"],
    },
    {
        "name": "Telangana Medical Device Park (Sultanpur, Patancheru)", "state": "Telangana",
        "tier": "PARK_PARTIAL",
        "scale": "A state-run park, NOT one of the 4 nationally-tracked Medical Device Parks -- found only because a PLI Medical Devices beneficiary's official address cites it",
        "notable_companies": ["Majik Medical Solutions Pvt Ltd (Plot M-46, catheter tubing -- the one confirmed case of a PLI Medical Devices company actually sited inside a purpose-built park)"],
        "sources": ["layers/49_medical_devices_parks.json"],
    },
    {
        "name": "HP Medical Device Park (Nalagarh)", "state": "Himachal Pradesh", "tier": "PARK_EMPTY",
        "scale": "Withdrawn by the state government itself, 07.09.2024, despite ₹30cr already released",
        "notable_companies": [],
        "sources": ["docs/PLI_SCHEME_BENEFICIARY_LEADS.md section 5D"],
    },
    {
        "name": "Bulk Drug Parks (HP-Haroli, Gujarat-Jambusar, AP-Nakkapalli)", "state": "multi-state",
        "tier": "PARK_EMPTY",
        "scale": "3 parks approved; AP's own live portal states 'Allotted plots = 0' across 1,793.3 acres -- zero companies allotted land at any of the 3, per the twin's existing section 5E",
        "notable_companies": [],
        "sources": ["docs/PLI_SCHEME_BENEFICIARY_LEADS.md section 5E"],
    },
    {
        "name": "AMTZ (Andhra Pradesh MedTech Zone), Visakhapatnam", "state": "Andhra Pradesh",
        "tier": "ESTABLISHED",
        "scale": "Distinct from the 4 official 'Medical Device Parks' scheme -- a separate, older, genuinely operating medtech manufacturing zone; hosts a real concentration of PLI Medical Devices beneficiaries",
        "notable_companies": ["Varex Imaging (X-ray tubes/detectors)", "Trivitron Healthcare (X-ray/C-arm/USG)",
                              "Innvolution Healthcare (stents/PTCA catheters)"],
        "sources": ["layers/49_medical_devices_parks.json"],
    },
    {
        "name": "PM MITRA Textile Park, Warangal (Kakatiya Mega Textile Park)", "state": "Telangana",
        "tier": "PARK_PARTIAL",
        "scale": "1,350 acres, brownfield; the ONE PM MITRA park with a confirmed, operating, dated tenant of the 7 nationally",
        "notable_companies": ["Evertop Textile & Apparel Complex (Youngone Corporation, Korea) -- "
                              "groundbreaking 2023, commercial production since Oct 2025, also a "
                              "PLI Textiles beneficiary"],
        "sources": ["layers/50_textile_defence_parks.json"],
    },
    {
        "name": "PM MITRA Textile Park, Dhar", "state": "Madhya Pradesh", "tier": "PARK_PARTIAL",
        "scale": "2,158 acres, greenfield; ~91 companies collectively allotted ~1,300 acres per a Sep-2025 state-sourced report",
        "notable_companies": ["Vardhman Textiles (190 acres, ~₹2,000cr -- moderately confirmed, not independently verified against a primary allotment order)",
                              "AB Cotspin India (45 acres)", "Trident Company (180 acres)"],
        "sources": ["layers/50_textile_defence_parks.json"],
    },
    {
        "name": "PM MITRA Textile Parks — 5 remaining (Virudhunagar-TN, Navsari-Gujarat, Kalaburagi-Karnataka, Lucknow-Hardoi-UP, Amravati-Maharashtra)",
        "state": "multi-state", "tier": "PARK_EMPTY",
        "scale": "No named tenant confirmed at any of these 5 sites as of this research pass",
        "notable_companies": [],
        "sources": ["layers/50_textile_defence_parks.json"],
    },
    {
        "name": "Tamil Nadu Defence Industrial Corridor", "state": "Tamil Nadu", "tier": "PARK_PARTIAL",
        "scale": "5 nodes (Chennai/Coimbatore/Hosur/Salem/Tiruchirappalli); 2 confirmed operating foreign-JV facilities",
        "notable_companies": ["LTMMSL (L&T 51% / MBDA France 49%, missile subsystem assembly)",
                              "Merlinhawk Composites (JV w/ Vega Composites, Italy, aerostructures, Shoolagiri)"],
        "sources": ["layers/50_textile_defence_parks.json"],
    },
    {
        "name": "Uttar Pradesh Defence Industrial Corridor", "state": "Uttar Pradesh", "tier": "PARK_EMPTY",
        "scale": "6 nodes (Agra/Aligarh/Chitrakoot/Jhansi/Kanpur/Lucknow); only aggregate MoU figures found (108 MoUs, ~₹12,191cr potential), no foreign-parented tenant confirmed",
        "notable_companies": [],
        "sources": ["layers/50_textile_defence_parks.json"],
    },
    {
        "name": "YEIDA Semiconductor Park (Sector 6)", "state": "Uttar Pradesh", "tier": "PARK_PARTIAL",
        "scale": "500 acres; distinct from Sector 28 (Vama Sundari/Foxconn, the actual ISM-approved unit) and Sector 10 (NXP in talks, R&D not fab)",
        "notable_companies": ["NXP Semiconductors (in talks, Sector 10 — not the Sector 6 park itself)"],
        "sources": ["layers/51_semiconductor_parks.json"],
    },
    {
        "name": "Kochanahalli Semiconductor Park, Mysuru", "state": "Karnataka", "tier": "PARK_PARTIAL",
        "scale": "234 acres total, 140 reserved for the park; none of its tenants are among the 12 nationally ISM-approved units",
        "notable_companies": ["Kaynes Technology (land secured -- a DIFFERENT project from its ISM-approved Sanand, Gujarat unit)",
                              "Wurth Technology", "Silectric Semiconductor Manufacturing (Zoho-backed, ~₹3,425cr)"],
        "sources": ["layers/51_semiconductor_parks.json"],
    },
    {
        "name": "Tamil Nadu Semiconductor Mission 2030 parks (Sulur, Palladam)", "state": "Tamil Nadu",
        "tier": "PARK_EMPTY",
        "scale": "~100 acres each, ~₹500cr mission outlay; 🚩 TN's own government confirmed via a Jul-2026 LS starred question that NO ISM-approved fab/display project has ever been sited in the state, and a widely-reported ~₹80,000cr Taiwanese proposal 'has not been received' by MeitY",
        "notable_companies": [],
        "sources": ["layers/51_semiconductor_parks.json"],
    },
]


def main():
    today = dt.date.today().isoformat()
    by_tier = {}
    for c in CLUSTERS:
        by_tier.setdefault(c["tier"], []).append(c["name"])

    out = {
        "layer": 48, "name": "state_pharma_clusters", "built": today,
        "what": ("Reference registry of India's major state-level manufacturing clusters and "
                 "government-allocated industrial parks -- pharma/medtech (original scope), extended "
                 "2026-09-17 to textiles (PM MITRA), defence (Defence Industrial Corridors), and "
                 "semiconductors (state Semiconductor Parks) as the same cross-reference methodology "
                 "was applied to more schemes. Tiered ESTABLISHED (real, large, operating) / "
                 "PARK_PARTIAL (parks with officially-unnamed but press-confirmed tenants) / "
                 "PARK_EMPTY (announced, zero confirmed tenants by any source). Built so future "
                 "sessions check this registry before re-researching cluster-by-cluster the way "
                 "layer 47 had to for Telangana."),
        "counts_by_tier": {k: len(v) for k, v in by_tier.items()},
        "clusters": CLUSTERS,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# State manufacturing cluster registry — layer 48", "",
         "*(pharma/medtech + textiles + defence + semiconductors)*", "",
         f"*Generated {today} by `scripts/build_layer48_state_pharma_clusters.py`. "
         f"{len(CLUSTERS)} clusters — {out['counts_by_tier'].get('ESTABLISHED',0)} established, "
         f"{out['counts_by_tier'].get('PARK_PARTIAL',0)} park (partially named), "
         f"{out['counts_by_tier'].get('PARK_EMPTY',0)} park (empty). Static hand-verified dataset, "
         "not a live scrape.*", "",
         "## Why this exists", "",
         "Answers a question the twin previously had to re-derive per-company: is this pharma/"
         "medtech company's plant in a real cluster, a park with unofficially-named tenants, or a "
         "genuinely empty announced park? Layer 47 did this by hand for Telangana; this registry "
         "generalizes it nationally so the next session checks here first.", ""]

    for tier, label in [("ESTABLISHED", "Established, real, operating clusters"),
                        ("PARK_PARTIAL", "Parks — officially unnamed, press-confirmed tenants exist"),
                        ("PARK_EMPTY", "Parks — zero confirmed tenants by any source")]:
        L += [f"## {label}", ""]
        for c in CLUSTERS:
            if c["tier"] != tier:
                continue
            L += [f"### {c['name']} ({c['state']})", "",
                 f"**Scale**: {c['scale']}", "",
                 f"**Notable companies**: {', '.join(c['notable_companies']) if c['notable_companies'] else '(none confirmed)'}", ""]

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"{len(CLUSTERS)} clusters ({out['counts_by_tier']}) -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
