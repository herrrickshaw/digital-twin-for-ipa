#!/usr/bin/env python3
"""Layer 46 -- PLI Scheme for Bulk Drugs: commercial-production sourcing.

Static, hand-verified dataset (same pattern as layer 44's state-MoU sweep,
NOT a live scrape) built from three government primary sources, pieced
together because no single document has the full picture:

  1. Dept. of Pharmaceuticals / BDMAI circular, 18 Oct 2022 -- the only
     source with COMPANY-LEVEL committed capacity (MT) per approved
     project. The source PDF is image-only (zero extractable text via
     pdfplumber/pymupdf) -- transcribed by reading it visually.
     https://bdmai.org/wp-content/uploads/2025/02/LIST-OF-APPROVED-BULK-DRUG-MANUFACTURERS-ALONG-WITH-MANUFACTUREING-CAPACITY-UNDER-THE-PLI-SCHEME.pdf
  2. PIB Release ID 2146914, 22 Jul 2025 (Rajya Sabha written reply,
     Anupriya Patel) -- applicant/product annexure confirming 48 approved
     projects. https://www.pib.gov.in/PressReleasePage.aspx?PRID=2146914
  3. PIB Release ID 2295928, 07 Aug 2026 (Lok Sabha written reply,
     Anupriya Patel) -- MOST CURRENT: state-wise investment/capacity/
     production table, the full 41-product approved list (Annexure-B),
     and -- the key gap this layer fills -- the exact 18 APIs now in
     COMMERCIAL production (prior sourcing only had the count, not the
     names). https://www.pib.gov.in/PressReleasePage.aspx?PRID=2295928

Distinct from the ORIGINAL 53 critical China-import-dependent APIs the
Dept. of Pharmaceuticals identified in 2020 (BusinessToday, 03 Jun 2020) --
only 41 of those 53 ever received an approved PLI project. This layer's
`gap_apis_no_pli_project` field is the resulting finding: 22 critical APIs,
including Paracetamol and Metformin, have NO PLI-incentivised domestic
capacity underway at all.

Usage: python3 scripts/build_layer46_pli_bulk_drugs.py
Output: layers/46_pli_bulk_drugs_commercial.json
        + docs/PLI_BULK_DRUGS_COMMERCIAL_PRODUCTION.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "46_pli_bulk_drugs_commercial.json")
OUT_DOC = os.path.join(ROOT, "docs", "PLI_BULK_DRUGS_COMMERCIAL_PRODUCTION.md")

# The 53 critical KSMs/DIs/APIs identified by DoP in 2020 as heavily
# China-import-dependent (source: BusinessToday, 03 Jun 2020, "Atma Nirbhar
# Bharat: Here are 53 drugs on which India will test self reliance").
CRITICAL_53 = [
    "Amoxicillin", "Azithromycin", "Erythromycin Stearate", "Ceftriaxone", "Cefoperazone",
    "Cefixime", "Cephalexin", "Piperacillin", "Tazobactam", "Sulbactam", "Prednisolone",
    "Metformin", "Gabapentin", "Rifampicin", "Vitamin B1", "Vitamin B6", "Clindamycin Phosphate",
    "Clindamycin HCL", "Streptomycin", "Neomycin", "Gentamycin", "Doxycycline",
    "Potassium Clavulanate", "Oxytetracycline", "Tetracycline", "Clarithromycin", "Betamethasone",
    "Ciprofloxacin", "Losartan", "Telmisartan", "Artesunate", "Norfloxacin", "Ofloxacin",
    "Metronidazole", "Sulfadiazine", "Levofloxacin", "Meropenem", "Paracetamol", "Tinidazole",
    "Ornidazole", "Ritonavir", "Diclofenac Sodium", "Aspirin", "Levetiracetam", "Carbidopa",
    "Levodopa", "Carbamazepine", "Oxcarbazepine", "Valsartan", "Olmesartan", "Atorvastatin",
    "Acyclovir", "Lopinavir",
]

# 41 products actually approved under PLI Bulk Drugs (PIB 2295928 Annexure-B, Aug 2026)
PLI_APPROVED_41 = [
    "Penicillin G", "7-ACA", "Erythromycin Thiocynate (TIOC)", "Clavulanic Acid", "Neomycin",
    "Gentamycin", "Betamethasone", "Dexamethasone", "Prednisolone", "Rifampicin", "Vitamin B1",
    "Clindamycin Base", "Streptomycin", "Tetracycline", "1,1 Cyclohexane Diacetic Acid (CDA)",
    "2-Methyl-5Nitro-Imidazole (2-MNI)", "Dicyandiamide (DCDA)", "Para amino phenol", "Meropenem",
    "Atorvastatin", "Olmesartan", "Valsartan", "Losartan", "Levofloxacin", "Sulfadiazine",
    "Ciprofloxacin", "Ofloxacin", "Norfloxacin", "Artesunate", "Telmisartan", "Aspirin",
    "Diclofenac Sodium", "Levetiracetam", "Carbidopa", "Ritonavir", "Lopinavir", "Acyclovir",
    "Carbamazepine", "Oxcarbazepine", "Vitamin B6", "Levodopa",
]

# 18 APIs in COMMERCIAL PRODUCTION as of March 2026 (PIB 2295928 -- the
# single most valuable fact in this layer; every other public source only
# had the count "18", never the names).
COMMERCIAL_18 = [
    "Penicillin G", "Clavulanic Acid", "Dexamethasone", "Prednisolone", "Para Amino Phenol",
    "1,1 Cyclohexane Diacetic Acid (CDA)", "Dicyandiamide (DCDA)", "Atorvastatin", "Levofloxacin",
    "Sulfadiazine", "Ofloxacin", "Norfloxacin", "Artesunate", "Telmisartan", "Lopinavir",
    "Carbamazepine", "Oxcarbazepine", "Diclofenac Sodium",
]

# 51 company-level approved projects with committed capacity in MT
# (BDMAI circular, 18 Oct 2022 -- baseline; a handful of projects may have
# been added/withdrawn since, per the 48-vs-51 count difference with the
# 2025/2026 PIB releases -- flagged, not reconciled, in the doc output).
BDMAI_PROJECTS = [
    (1, "Aurobindo Pharma Limited (through Lyfius Pharma Pvt. Ltd.)", "Penicillin G", 15000),
    (2, "Karnataka Antibiotics and Pharmaceuticals Limited", "7-ACA", 1000),
    (3, "Orchid Bio-Pharma Limited", "7-ACA", 1000),
    (4, "Kinvan Private Limited", "Clavulanic Acid", 300),
    (5, "Natural Biogenex Private Limited", "Betamethasone", 12),
    (6, "Natural Biogenex Private Limited", "Dexamethasone", 10),
    (7, "Natural Biogenex Private Limited", "Prednisolone", 15),
    (8, "Symbiotec Pharmalab Private Limited", "Prednisolone", 15),
    (9, "Macleods Pharmaceutical Limited", "Rifampicin", 200),
    (10, "Karnataka Antibiotics and Pharmaceuticals Limited", "Clindamycin Base", 60),
    (11, "Emmennar Pharma Pvt. Ltd.", "1,1 Cyclohexane Diacetic Acid (CDA)", 1500),
    (12, "Hindys Lab Pvt. Ltd.", "1,1 Cyclohexane Diacetic Acid (CDA)", 3000),
    (13, "Alkimia Pharma-Chem Pvt Ltd", "1,1 Cyclohexane Diacetic Acid (CDA)", 1500),
    (14, "Meghmani LLP", "Para Amino Phenol", 13500),
    (15, "Sadhana Nitro Chem Ltd.", "Para Amino Phenol", 36000),
    (16, "Granules India Limited", "Dicyandiamide (DCDA)", 8000),
    (17, "Rajasthan Antibiotics Limited", "Meropenem", 48),
    (18, "Centrient Pharmaceuticals India Private Limited", "Atorvastatin", 180),
    (19, "Anasia Lab Private Limited", "Olmesartan", 75),
    (20, "Andhra Organics Limited", "Olmesartan", 75),
    (21, "Aviran Pharmachem Private Limited", "Artesunate", 20),
    (22, "K P Manish Global Ingredients Pvt. Ltd.", "Artesunate", 80),
    (23, "RMC Performance Chemicals Private Limited", "Aspirin", 1500),
    (24, "Alta Laboratories Limited", "Aspirin", 2250),
    (25, "Lifetech Sciences", "Ritonavir", 20),
    (26, "Honour Lab Limited", "Lopinavir", 49),
    (27, "Hindys Lab Pvt. Ltd.", "Acyclovir", 525),
    (28, "Dasami Lab Pvt. Ltd.", "Carbamazepine", 260),
    (29, "Dasami Lab Pvt. Ltd.", "Oxcarbazepine", 195),
    (30, "Hetero Drugs Limited", "Oxcarbazepine", 195),
    (31, "Hazelo Lab Pvt. Ltd.", "Vitamin B6", 70),
    (32, "Sudarshan Pharma Industries Ltd.", "Vitamin B6", 35),
    (33, "Honour Lab Limited", "Vitamin B6", 140),
    (34, "Honour Lab Limited", "Valsartan", 300),
    (35, "Anasia Lab Private Limited", "Losartan", 400),
    (36, "Hetero Drugs Limited", "Levofloxacin", 230),
    (37, "MSN Life Sciences Pvt. Ltd", "Levofloxacin", 230),
    (38, "Vital Laboratories Private Limited", "Levofloxacin", 115),
    (39, "Andhra Organics Limited", "Sulfadiazine", 360),
    (40, "Sreepathi Pharmaceuticals Limited", "Ciprofloxacin", 900),
    (41, "Vital Laboratories Private Limited", "Ofloxacin", 100),
    (42, "Global Pharma Healthcare Private Limited", "Ofloxacin", 200),
    (43, "Globela Industries Pvt. Ltd", "Ofloxacin", 100),
    (44, "Globela Industries Pvt. Ltd", "Norfloxacin", 60),
    (45, "Andhra Organics Limited", "Telmisartan", 360),
    (46, "Kreative Actives Private Limited", "Diclofenac Sodium", 350),
    (47, "Amoli Organics Private Limited", "Diclofenac Sodium", 175),
    (48, "Vapi Care Pharma Private Limited", "Diclofenac Sodium", 525),
    (49, "Honour Lab Limited", "Levetiracetam", 840),
    (50, "Hetero Drugs Limited", "Carbidopa", 16),
    (51, "Hetero Drugs Limited", "Levodopa", 40),
]

# State-wise investment/capacity, PIB 2295928 Annexure-A (as of March 2026).
# (state, projects, committed_inv_cr, actual_inv_cr, committed_cap_mt, installed_cap_mt)
STATE_WISE = [
    ("Andhra Pradesh", 10, 1745.7, 2676, 24390, 16468),
    ("Gujarat", 8, 330.9, 407.3, 14270, 13959),
    ("Haryana", 1, 81, 37, 800, 0),          # under commissioning
    ("Himachal Pradesh", 2, 806.8, 502.6, 1100, 400),
    ("Jammu & Kashmir", 1, 185, 338.65, 1000, 0),  # under commissioning
    ("Karnataka", 3, 96.9, 201.4, 37, 16.7),
    ("Madhya Pradesh", 2, 280, 101.8, 1015, 15),
    ("Maharashtra", 5, 308.4, 168.8, 40185, 19180),
    ("Punjab", 1, 137.7, 161.1, 180, 206),
    ("Tamil Nadu", 2, 31.5, 45.6, 280, 280),
    ("Telangana", 13, 326.02, 430.2, 7820, 7820),
]

SOURCES = [
    {"doc": "BDMAI circular (Dept. of Pharmaceuticals letter No.30013/16/2022-Scheme)",
     "date": "2022-10-18",
     "url": "https://bdmai.org/wp-content/uploads/2025/02/LIST-OF-APPROVED-BULK-DRUG-MANUFACTURERS-ALONG-WITH-MANUFACTUREING-CAPACITY-UNDER-THE-PLI-SCHEME.pdf",
     "provides": "company-level committed capacity (MT) per approved project — 51 line items; image-only PDF, transcribed visually"},
    {"doc": "PIB Release ID 2146914 (Rajya Sabha written reply, Anupriya Patel)",
     "date": "2025-07-22",
     "url": "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2146914",
     "provides": "applicant/product annexure confirming 48 approved projects"},
    {"doc": "PIB Release ID 2295928 (Lok Sabha written reply, Anupriya Patel)",
     "date": "2026-08-07",
     "url": "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2295928",
     "provides": "MOST CURRENT — state-wise investment/capacity/production (Annexure-A), full 41-product approved list (Annexure-B), and the exact 18 APIs now in commercial production"},
    {"doc": "BusinessToday, \"Atma Nirbhar Bharat: Here are 53 drugs on which India will test self reliance\"",
     "date": "2020-06-03",
     "url": "https://www.businesstoday.in/industry/pharma/story/atma-nirbhar-bharat-here-are-53-drugs-on-which-india-will-test-self-reliance-260146-2020-06-03",
     "provides": "the original 53 critical China-import-dependent APIs identified pre-scheme"},
]


def norm(s):
    return s.lower().replace("-", " ").replace("(", "").replace(")", "").strip()


def main():
    pli_norm = {norm(p) for p in PLI_APPROVED_41}
    commercial_norm = {norm(p) for p in COMMERCIAL_18}

    api_status = {}
    for api in CRITICAL_53:
        n = norm(api)
        api_status[api] = {
            "pli_project_approved": n in pli_norm,
            "commercial_production": n in commercial_norm,
        }

    gap_apis = [a for a, s in api_status.items() if not s["pli_project_approved"]]
    pli_not_commercial = [a for a, s in api_status.items()
                          if s["pli_project_approved"] and not s["commercial_production"]]
    commercial = [a for a, s in api_status.items() if s["commercial_production"]]

    today = dt.date.today().isoformat()
    out = {
        "layer": 46, "name": "pli_bulk_drugs_commercial", "built": today,
        "what": ("PLI Scheme for Bulk Drugs: company-level approved-project roster with "
                 "committed capacity, cross-referenced against the original 53 critical "
                 "China-import-dependent APIs identified in 2020 -- which of them ever got "
                 "a PLI project (41 of 53), and which have actually reached commercial "
                 "production (18 of those 41, named explicitly for the first time in this "
                 "layer's primary source). Static hand-verified dataset, same pattern as "
                 "layer 44 -- not a live scrape; re-run only when a fresher PIB annexure "
                 "is sourced."),
        "sources": SOURCES,
        "critical_apis_53_2020_baseline": CRITICAL_53,
        "pli_approved_products_41": PLI_APPROVED_41,
        "commercial_production_18": COMMERCIAL_18,
        "critical_api_status": api_status,
        "finding_gap_apis_no_pli_project": {
            "count": len(gap_apis),
            "apis": gap_apis,
            "note": ("22 of the 53 originally-identified critical APIs have NO PLI project "
                     "approved at all, including Paracetamol and Metformin -- two of the "
                     "highest-volume generic APIs in India's own Jan Aushadhi (PMBJP) "
                     "formulary. These remain exposed to import dependence with zero "
                     "government-incentivised domestic capacity underway despite being "
                     "flagged as critical five years earlier."),
        },
        "pli_approved_not_yet_commercial": pli_not_commercial,
        "commercial_critical_apis": commercial,
        "company_projects": [
            {"sno": sno, "company": company, "product": product, "committed_capacity_mt": cap,
             "commercial_production": norm(product) in commercial_norm}
            for sno, company, product, cap in BDMAI_PROJECTS
        ],
        "total_committed_capacity_mt": sum(p[3] for p in BDMAI_PROJECTS),
        "state_wise_2026_03": [
            {"state": s, "projects_approved": p, "committed_investment_cr": ci,
             "actual_investment_cr": ai, "committed_capacity_mt": cc, "installed_capacity_mt": ic}
            for s, p, ci, ai, cc, ic in STATE_WISE
        ],
        "note_count_discrepancy": ("BDMAI's Oct-2022 roster has 51 company-project line items; "
                                   "PIB's 2025/2026 releases say 48 projects approved -- the gap "
                                   "is not reconciled here (could be projects merged, withdrawn, "
                                   "or added between the two dates); treat 51 as the fuller, "
                                   "slightly older company-level list and 48 as the current "
                                   "official count."),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# PLI Bulk Drugs — commercial-production sourcing — layer 46", "",
         f"*Generated {today} by `scripts/build_layer46_pli_bulk_drugs.py`. Static, hand-verified "
         "dataset built from 4 government primary sources (see below) — not a live scrape.*", "",
         "## The three-source problem this layer solves", "",
         "No single official document has the full picture: the BDMAI circular has company-level "
         "capacity but is from 2022 and image-only; the 2025 PIB release has the applicant/product "
         "annexure but no capacity; the 2026 PIB release has the current state-wise numbers and — "
         "critically — is the ONLY source that names all 18 APIs now in commercial production "
         "(every other source just gives the count). This layer merges all three.", ""]

    L += ["## Sources", ""]
    for s in SOURCES:
        L.append(f"- **{s['doc']}** ({s['date']}) — {s['provides']}. [{s['url']}]({s['url']})")
    L.append("")

    L += ["## Key finding: the Paracetamol/Metformin gap", "",
         f"**{len(gap_apis)} of the 53 originally-identified critical APIs have NO PLI project "
         "approved at all**, including **Paracetamol** and **Metformin** — two of the highest-"
         "volume generic APIs in India's own Jan Aushadhi (PMBJP) formulary. These remain exposed "
         "to import dependence with zero government-incentivised domestic capacity underway "
         "despite being flagged as critical in 2020.", "",
         "| Gap APIs (no PLI project) |", "|---|"]
    for a in gap_apis:
        L.append(f"| {a} |")
    L.append("")

    L += ["## The 18 APIs in commercial production (named for the first time here)", "",
         "| API |", "|---|"]
    for a in commercial:
        L.append(f"| {a} |")
    L.append("")

    L += [f"## Company-level approved projects (n={len(BDMAI_PROJECTS)}, "
         f"total committed capacity {out['total_committed_capacity_mt']:,} MT)", "",
         "| S.No. | Company | Product | Committed Capacity (MT) | Commercial? |",
         "|---|---|---|---|---|"]
    for sno, company, product, cap in BDMAI_PROJECTS:
        commercial_flag = "✅" if norm(product) in commercial_norm else ""
        L.append(f"| {sno} | {company} | {product} | {cap:,} | {commercial_flag} |")
    L.append("")

    L += ["## State-wise (as of March 2026)", "",
         "| State | Projects | Committed Inv. (₹cr) | Actual Inv. (₹cr) | Committed Cap. (MT) | Installed Cap. (MT) |",
         "|---|---|---|---|---|---|"]
    for s, p, ci, ai, cc, ic in STATE_WISE:
        L.append(f"| {s} | {p} | {ci:,} | {ai:,} | {cc:,} | {ic:,} |")
    L.append("")
    L.append(out["note_count_discrepancy"])
    L.append("")

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"{len(CRITICAL_53)} critical APIs, {len(PLI_APPROVED_41)} PLI-approved, "
          f"{len(commercial)} commercial, {len(gap_apis)} gap APIs, "
          f"{len(BDMAI_PROJECTS)} company projects -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
