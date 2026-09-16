#!/usr/bin/env python3
"""Layer 49 -- PLI Medical Devices roster + Medical Device Parks occupancy.

Extends the layer 46/47 pattern (PLI Bulk Drugs vs Telangana clusters) to
the PLI Medical Devices scheme and its dedicated infrastructure grant --
the Medical Device Parks -- to test the same question: do the national
scheme's approved companies actually sit inside the government's own
purpose-built parks for that sector?

Static, hand-verified dataset (same pattern as layers 44/46/47), built
2026-09-17 from: pharma-dept.gov.in's official 22.03.2023 approved-
applicant PDF (confirms the 6 companies later dropped from 32->27), plus
company-level plant-location research for company website/press coverage
(20 of the current ~27 resolved; ~7 slots added after the 2023 snapshot
remain unidentified -- no newer official list found), plus a fresh press
sweep of the 3 live Medical Device Parks.

KEY FINDING 1 (corrects docs/PLI_SCHEME_BENEFICIARY_LEADS.md 5D, which
said "no company/allottee names published for any live park"): that is
Parliament's official non-disclosure LINE, but it is informally bypassed
for 2 of the 3 parks -- UP-YEIDA and MP-Ujjain both have specific tenant
companies named in state-authority press releases and trade coverage
(Operon Strategist, Medical Buyer, Swarajya, Daily Jagran). TN-Oragadam
remains the one park where the non-disclosure genuinely holds -- no
source, official or press, names a single confirmed in-park tenant.

KEY FINDING 2: none of the resolved PLI Medical Devices companies are
located inside any of the 3 parks. The PLI scheme's approved-applicant
universe and each park's tenant universe are two non-overlapping company
sets -- the same "committed ≠ built there" pattern layer 47 found for
Hyderabad Pharma City, and the same "two separate schemes, don't conflate
them" pattern the twin already documents for PLI Bulk Drugs vs Bulk Drug
Parks (section 5B/5E).

Usage: python3 scripts/build_layer49_medical_devices_parks.py
Output: layers/49_medical_devices_parks.json
        + docs/MEDICAL_DEVICES_PARKS_CROSSREF.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "49_medical_devices_parks.json")
OUT_DOC = os.path.join(ROOT, "docs", "MEDICAL_DEVICES_PARKS_CROSSREF.md")

# (company, product/segment, state, city/location, status, confidence)
# status: approved | dropped
PLI_MED_DEVICES = [
    ("Philips Global Business Services LLP", "MRI Coils", "Maharashtra", "Pune", "approved", "HIGH"),
    ("Siemens Healthcare Pvt Ltd", "CT/MRI", "Karnataka", "Bengaluru", "approved", "HIGH"),
    ("Wipro GE Healthcare", "CT/Cath Lab/USG + anaesthesia/monitoring", "Karnataka",
     "Whitefield/Kadugodi (EPIP Phase 2, Hoodi Village), Bengaluru", "approved", "HIGH"),
    ("GE BE Pvt Ltd", "PET Detector", "Karnataka", "Bengaluru", "approved", "MEDIUM-HIGH"),
    ("Varex Imaging Manufacturing India", "X-ray tubes / flat panel detectors (2 approvals)",
     "Maharashtra / Andhra Pradesh", "Pune/Talegaon Dabhade + AMTZ Visakhapatnam", "approved", "MEDIUM"),
    ("Nipro India Corporation", "Dialyzers", "Maharashtra", "Satara", "approved", "MEDIUM"),
    ("Omron Healthcare Manufacturing India", "BP monitors", "Tamil Nadu", "(state only, not Oragadam-confirmed)", "approved", "MEDIUM"),
    ("Meril group (4 entities: Healthcare, Life Sciences, Endo Surgery, Medical Innovations)",
     "Implants/stents/heart valves/surgical mesh/lithotripsy", "Gujarat", "Vapi", "approved", "HIGH"),
    ("Panacea Medical Technologies Pvt Ltd", "Linear Accelerator (LINAC), Rotational Cobalt Machine",
     "Karnataka", "Malur Industrial Area, Kolar district", "approved", "HIGH"),
    ("Allengers Medical Systems Ltd (AMSL)",
     "CT/MRI/USG/X-Ray/Cath Lab/PET/SPECT/Mammography/C-Arm", "Punjab", "Mohali (Derabassi)/Chandigarh",
     "approved", "HIGH"),
    ("BPL Medical Technologies Pvt Ltd (project 1: surgical X-ray/C-arm)",
     "Surgical X-ray, C-arm", "Karnataka",
     "Anekal Taluk, Bangalore", "approved", "HIGH"),
    ("Poly Medicure Ltd",
     "Dialyzer, dialysis machine, peritoneal dialysis kits, fistula, blood line", "Haryana",
     "Faridabad (+ Haridwar, Jaipur)", "approved", "HIGH"),
    ("Allied Medical Ltd", "Anaesthesia workstations, ventilators, AEDs, defibrillators",
     "Rajasthan", "Karoli, Alwar", "approved", "HIGH"),
    ("Deck Mount Electronics Ltd", "Oxygen concentrator",
     "Haryana", "Gurugram", "approved", "HIGH"),
    ("Microtek New Technologies Pvt Ltd", "Oxygen concentrators", "Himachal Pradesh",
     "Village Kattha, Baddi, Solan district", "approved", "HIGH"),
    ("Innvolution Healthcare Pvt Ltd", "Stents, PTCA catheter", "Rajasthan / Andhra Pradesh",
     "Sanganer, Jaipur + AMTZ, Visakhapatnam", "approved", "HIGH"),
    ("Envision Scientific Pvt Ltd", "Stents, PTCA balloon catheter", "Gujarat", "Surat SEZ, Sachin", "approved", "HIGH"),
    ("Motherson Health and Medical System Ltd", "X-ray tube components (housings, anode/cathode parts)",
     "Tamil Nadu", "Sojitz Motherson Industrial Park, Kanchipuram", "approved", "HIGH"),
    ("Majik Medical Solutions Pvt Ltd", "Cardiovascular/neurovascular catheter tubing", "Telangana",
     "Plot M-46, Medical Device Park, Sultanpur, Patancheru, Hyderabad", "approved", "HIGH"),
    ("Syrma Johari Medtech Ltd", "Not specified (2 line entries)", "Rajasthan",
     "G-582-584, EPIP Boranada, Jodhpur", "approved", "HIGH"),
    ("BPL Medical Technologies Pvt Ltd (project 2: patient monitoring/AED/ECG)", "Patient monitoring, AED, ECG",
     "Karnataka", "Anekal Taluk, Bangalore", "approved", "HIGH"),
    ("Trivitron Healthcare Pvt Ltd", "X-ray, C-arm, mammography, ultrasonography",
     "Maharashtra / Andhra Pradesh", "Raigad + AMTZ Campus, Visakhapatnam", "approved", "HIGH"),
    ("Allengers OEM Pvt Ltd (AOPL)", None, None, None, "status_unclear", None),
    ("Sahajanand Medical Technologies Pvt Ltd (SMTPL)", None, None, None, "status_unclear", None),
    ("Bio India Interventional Technologies Pvt Ltd", None, None, None, "status_unclear", None),
    ("Indovasive Pvt Ltd", None, None, None, "dropped", None),
    ("Neurovasive Pvt Ltd", None, None, None, "dropped", None),
]
# 🔴 CORRECTION found via a second, more authoritative research pass, same
# day: the official PIB PRID=2204598 (16 Dec 2025, Rajya Sabha Annexure A --
# addresses + investment through Sep 2025) is MORE CURRENT than the "6
# dropped" list an earlier pass cross-checked against an undated
# pharma-dept.gov.in PDF. That official Dec-2025 annexure explicitly
# INCLUDES Trivitron Healthcare as approved (Raigad, Maharashtra + AMTZ
# Visakhapatnam) and gives BPL Medical Technologies a 2nd project (Anekal
# Taluk, Bangalore). Three others (Allengers OEM, Sahajanand Medical Tech,
# Bio India Interventional) appear on an undated DoP PDF but NOT in the
# Dec-2025 annexure -- status genuinely unclear (rescinded? lapsed? just
# not yet reporting investment?), marked "status_unclear" rather than
# forced into "approved" or "dropped". Only Indovasive and Neurovasive are
# confirmed dropped with no ambiguity. Government sources disagree with
# each other here -- not silently reconciled, both readings are kept.

MEDICAL_DEVICE_PARKS = [
    {
        "park": "UP Medical Device Park", "state": "Uttar Pradesh", "location": "YEIDA, Sector 28, Greater Noida",
        "units_allotted_official": 101, "tier": "PARK_PARTIAL",
        "named_tenants_press": ["Auzein Medical Pvt Ltd (orthopaedic implants, ₹18.15cr)",
                                "Heidelco Medicore Pvt Ltd (AED/oxygen concentrators, ₹24cr)",
                                "Q Line Biotech", "Ramsons Group (anaesthesia needles/kits, ₹15cr)",
                                "Genuince Medica Pvt Ltd (anaesthesia workstations, ₹18.5cr)",
                                "Krish Biomedical (first unit inaugurated; blood-testing/preservation equipment, ₹6cr)"],
        "note": "Parliament says 'no allottee names published' -- effectively bypassed by YEIDA press coverage and trade media naming specific companies with investment figures.",
    },
    {
        "park": "MP Medical Device Park", "state": "Madhya Pradesh", "location": "Ujjain",
        "units_allotted_official": 74, "tier": "PARK_PARTIAL",
        "named_tenants_press": ["Sheba Industries India Pvt Ltd", "Clinisupplies India Pvt Ltd (catheters)",
                                "Medqverse Pvt Ltd (radiotherapy/cancer devices, ₹100cr)",
                                "VRM Molecular and Nuclear Medicines Pvt Ltd",
                                "HC Lifeline (syringes/cannula)", "KRM Healthcare (diagnostic kits)",
                                "Microgen Healthcare (infection control/wound care/orthopaedic implants)",
                                "Maple Technologies (women's healthcare devices)",
                                "Shreeji Polymers Medical Devices (insulin delivery/spray pumps)",
                                "Bioline India (blood collection/bags)",
                                "Technoplast Packaging Pvt Ltd (₹62cr)", "Hariva Meditech (₹200cr)"],
        "note": "Same bypass as YEIDA -- MPIDC/trade press (Operon Strategist, Medical Buyer, DrugsControl) repeatedly names specific allottees with investment amounts and product lines across 2023-2025 coverage.",
    },
    {
        "park": "TN Medical Device Park", "state": "Tamil Nadu", "location": "Oragadam, SIPCOT (Kancheepuram district)",
        "units_allotted_official": 35, "tier": "PARK_PARTIAL",
        "named_tenants_press": ["Polymatech Electronics Ltd (executed a 99-year lease for additional land, adjacent to its existing Oragadam facility)"],
        "note": "🔴 CORRECTED same day: an earlier research pass found this park genuinely empty; a second, deeper pass found Polymatech Electronics confirmed as an allottee via a company press release. Reclassified PARK_EMPTY -> PARK_PARTIAL. No other individual allottees found named for this specific park.",
    },
    {
        "park": "HP Medical Device Park", "state": "Himachal Pradesh", "location": "Nalagarh",
        "units_allotted_official": 0, "tier": "PARK_EMPTY",
        "named_tenants_press": [],
        "note": "Withdrawn by the state government itself, 07.09.2024, despite ₹30cr already released.",
    },
    {
        "park": "Telangana Medical Device Park", "state": "Telangana", "location": "Sultanpur, Patancheru, Hyderabad",
        "units_allotted_official": None, "tier": "PARK_PARTIAL",
        "named_tenants_press": ["Majik Medical Solutions Pvt Ltd (Plot M-46, cardiovascular/neurovascular catheter tubing -- also a PLI Medical Devices beneficiary, see below)"],
        "note": "🔴 NOT one of the 4 nationally-tracked Medical Device Parks (UP/MP/TN/HP-withdrawn) -- a separate STATE-run park, found only because a PLI-approved company's official address happens to cite it. This is the ONE confirmed case in this layer of a PLI Medical Devices company actually sited inside a purpose-built medical device park.",
    },
]

# Explicit per-company location vs the named parks, for companies checked
# during this research pass. Two rounds of research produced overlapping
# but not identical findings; both are folded in here.
PLI_COMPANY_PARK_CHECK = [
    {"company": "Majik Medical Solutions Pvt Ltd",
     "finding": "🔴 THE ONE CONFIRMED OVERLAP: Plot M-46, Medical Device Park, Sultanpur, Patancheru, Hyderabad -- an actual PLI Medical Devices beneficiary sited inside a purpose-built park, just not one of the 4 nationally-tracked ones (UP/MP/TN/HP)."},
    {"company": "Varex Imaging Manufacturing India, Trivitron Healthcare, Innvolution Healthcare",
     "finding": "All three have a facility inside the AMTZ (Andhra Pradesh MedTech Zone) campus, Visakhapatnam -- a real concentration of PLI Medical Devices manufacturing, but AMTZ is a separate, older, established medtech zone (see layer 48), not one of the 4 tracked Medical Device Parks."},
    {"company": "Wipro GE Healthcare", "finding": "Whitefield/Kadugodi, Bengaluru -- not Oragadam/Sriperumbudur"},
    {"company": "Omron Healthcare Manufacturing India", "finding": "Fresh MoU with Guidance TN (CM Stalin's Japan visit) for a TN investment, but no source confirms this is sited inside Oragadam specifically -- treat as unconfirmed/likely separate SIPCOT site"},
    {"company": "Meril group", "finding": "Vapi, Gujarat -- consistent with its known India base, not in any of the 5 tracked parks"},
    {"company": "Nipro India Corporation, Siemens Healthcare Pvt Ltd, GE BE Pvt Ltd, Philips Global Business Services LLP",
     "finding": "No evidence found placing any of these inside a named park; exact site not conclusively pinned down for Nipro/Siemens specifically"},
]


def main():
    today = dt.date.today().isoformat()
    approved = [c for c in PLI_MED_DEVICES if c[4] == "approved"]
    dropped = [c for c in PLI_MED_DEVICES if c[4] == "dropped"]
    status_unclear = [c for c in PLI_MED_DEVICES if c[4] == "status_unclear"]

    out = {
        "layer": 49, "name": "medical_devices_parks", "built": today,
        "what": ("PLI Medical Devices approved-company roster cross-referenced against actual "
                 "tenant occupancy at 5 government-run medical device parks (4 nationally-tracked "
                 "+ 1 Telangana state park found only via a company address). Two research passes "
                 "same day, second more authoritative (an official Dec-2025 Rajya Sabha annexure) "
                 "-- corrections from pass 1 to pass 2 are flagged inline rather than silently "
                 "overwritten. Static hand-verified dataset, same pattern as layers 44/46/47."),
        "sources": [
            {"doc": "PIB PRID=2204598 (16 Dec 2025, Rajya Sabha Annexure A -- addresses + investment through Sep 2025)",
             "url": "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2204598",
             "provides": "MOST AUTHORITATIVE -- 28 approved projects/24 entities with addresses; supersedes the 2023 PDF and the 27-count headline for company-level detail"},
            {"doc": "pharma-dept.gov.in official approved-applicants PDF (as on 22.03.2023, revised)",
             "url": "https://pharma-dept.gov.in/sites/default/files/Revised%20list%20of%20applicant%20-%20PLI%20for%20Medical%20Devices%20(as%20on%2022.03.2023)_0.pdf",
             "provides": "originally used to identify dropped companies; PARTIALLY SUPERSEDED -- see status_unclear entries"},
            {"doc": "LS USQ 1001, 24.07.2026 (filed under 'High Precision Medical Instruments')",
             "provides": "8 companies with disbursement figures (already in docs 5C)"},
            {"doc": "State-authority press + trade media (Operon Strategist, Medical Buyer, Swarajya, Daily Jagran, DrugsControl, CXOToday)",
             "provides": "the named park tenants no official source discloses"},
        ],
        "pli_medical_devices_approved": [
            {"company": c[0], "product": c[1], "state": c[2], "location": c[3], "confidence": c[5]}
            for c in approved
        ],
        "pli_medical_devices_dropped_confirmed": [c[0] for c in dropped],
        "pli_medical_devices_status_unclear": {
            "companies": [c[0] for c in status_unclear],
            "note": ("Appear on the undated pharma-dept.gov.in PDF as approved, but do NOT appear "
                     "in the more current Dec-2025 Rajya Sabha annexure. Could mean rescinded, "
                     "lapsed, or simply not yet reporting investment as of Sep 2025 -- not resolved "
                     "either way here."),
        },
        "total_approved_resolved": len(approved),
        "total_approved_official_count_note": ("28 approved PROJECTS across 24 distinct legal "
                                                "entities per the Dec-2025 annexure (some entities "
                                                "-- Meril, Varex, Syrma Johari, BPL -- have 2 "
                                                "separate approved projects each), reconciling the "
                                                "'27' vs '28' figures different press summaries cite."),
        "medical_device_parks": MEDICAL_DEVICE_PARKS,
        "finding_1_parliament_disclosure_bypassed": {
            "note": ("docs/PLI_SCHEME_BENEFICIARY_LEADS.md section 5D previously stated 'no company/"
                     "allottee names published for any live park' -- true as an official Parliament "
                     "position, but state-authority press and trade media independently name "
                     "specific tenants for 3 of the 4 nationally-tracked parks (YEIDA, Ujjain, and "
                     "-- corrected after a deeper pass -- Oragadam too, via Polymatech Electronics). "
                     "Only HP-Nalagarh has zero tenants, because it was withdrawn outright."),
        },
        "finding_2_one_confirmed_overlap": {
            "companies_confirmed_inside_a_park": 1,
            "checks_performed": PLI_COMPANY_PARK_CHECK,
            "note": ("Exactly ONE PLI Medical Devices company (Majik Medical Solutions) is confirmed "
                     "sited inside a purpose-built medical device park -- but a STATE-run Telangana "
                     "park (Sultanpur, Patancheru) not one of the 4 nationally-tracked ones. None of "
                     "the resolved companies are inside UP-YEIDA, MP-Ujjain, TN-Oragadam or the "
                     "withdrawn HP-Nalagarh. Separately, 3 companies (Varex, Trivitron, Innvolution) "
                     "cluster at AMTZ Visakhapatnam -- a real concentration, but AMTZ is an older "
                     "established medtech zone (layer 48), not a 'Medical Device Park' scheme site. "
                     "Overall: still overwhelmingly the same 'committed elsewhere ≠ built in the "
                     "purpose-built park' pattern layer 47 found for Hyderabad Pharma City -- just "
                     "not a perfect zero this time."),
        },
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# PLI Medical Devices roster + parks cross-reference — layer 49", "",
         f"*Generated {today} by `scripts/build_layer49_medical_devices_parks.py`. "
         f"{len(approved)} approved PLI Medical Devices projects resolved with plant location "
         f"(28 approved projects/24 entities officially, per the Dec-2025 Rajya Sabha annexure); "
         f"{len(dropped)} confirmed dropped; {len(status_unclear)} status-unclear (on an older "
         "list, absent from the newer one). Static hand-verified dataset, two research passes.*", "",
         "## Finding 1 — corrects docs/PLI_SCHEME_BENEFICIARY_LEADS.md 5D", "",
         out["finding_1_parliament_disclosure_bypassed"]["note"], "",
         "## Finding 2 — one confirmed overlap, not zero (corrected same day)", "",
         out["finding_2_one_confirmed_overlap"]["note"], "", "",
         "## PLI Medical Devices — approved (resolved)", "",
         "| Company | Product | State | Location | Confidence |", "|---|---|---|---|---|"]
    for c in out["pli_medical_devices_approved"]:
        L.append(f"| {c['company']} | {c['product']} | {c['state']} | {c['location']} | {c['confidence']} |")
    L.append("")
    L.append(f"**Confirmed dropped**: {', '.join(out['pli_medical_devices_dropped_confirmed']) or '(none)'}")
    L.append("")
    L.append(f"**Status unclear** (older list only): {', '.join(out['pli_medical_devices_status_unclear']['companies'])}")
    L.append("")
    L.append(out["pli_medical_devices_status_unclear"]["note"])
    L.append("")
    L.append(out["total_approved_official_count_note"])
    L.append("")

    L += ["## Medical Device Parks — actual tenant occupancy", ""]
    for p in MEDICAL_DEVICE_PARKS:
        units = p['units_allotted_official'] if p['units_allotted_official'] is not None else "not applicable (state-run, not one of the 4 nationally-tracked parks)"
        L += [f"### {p['park']} ({p['state']}, {p['location']}) — {p['tier']}", "",
             f"**Units allotted (official)**: {units}", "",
             f"**Named tenants (press, not official)**: "
             f"{'; '.join(p['named_tenants_press']) if p['named_tenants_press'] else '(none found)'}", "",
             p["note"], ""]

    L += ["## PLI company vs park location checks performed", "",
         "| Company | Finding |", "|---|---|"]
    for c in PLI_COMPANY_PARK_CHECK:
        L.append(f"| {c['company']} | {c['finding']} |")
    L.append("")

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"{len(approved)} approved projects resolved, {len(dropped)} dropped, "
          f"{len(status_unclear)} status-unclear, 3/4 national parks have press-named tenants, "
          f"1 confirmed PLI-company/park overlap (Telangana state park) -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
