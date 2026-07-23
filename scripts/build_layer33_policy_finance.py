#!/usr/bin/env python3
"""Layer 33 — policy-finance extensions: fisheries · state-excise bottling fees ·
import/export duties · India Exim Bank.

Four analysis blocks the twin lacked, researched 2026-07-23 (4-agent sweep,
every claim carrying its source URL + the HTTP status actually observed from
this machine; access failures recorded as data). Each block names the layer-32
companies it touches — policy without a company linkage is just prose.

Live on build:
  - Exim LOC spreadsheet links re-scraped from /lines-of-credit (the .xlsx
    URLs carry upload-month paths and move every quarterly refresh)
  - liveness stamps on the key portals

Usage:  python3 scripts/build_layer33_policy_finance.py [--no-live]
Output: layers/33_policy_finance_extensions.json
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "33_policy_finance_extensions.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout)


def status(url):
    try:
        return get(url).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR:{type(e).__name__}"


def scrape_exim_loc_links():
    """The LOC xlsx URLs move quarterly — always re-scrape the listing page."""
    html = get("https://www.eximbankindia.in/lines-of-credit",
               timeout=40).read().decode("utf-8", "replace")
    return sorted(set(re.findall(
        r'href="(/sites/default/files/[^"]+\.xlsx)"', html)))


FISHERIES = {
    "what": ("Central fisheries incentive stack + export machinery — the twin's "
             "catalog had PMMSY name-checks only; this is the funded picture"),
    "pmmsy": {
        "outlay": "Rs 20,050 cr FY21-25, extended to FY26 on existing design",
        "approved": ("Rs 21,394.88 cr projects (central share Rs 9,510.89 cr) "
                     "per Rajya Sabha reply 22-Jul-2026"),
        "portal": {"url": "https://pmmsy.dof.gov.in/", "http_status": 200},
        "traceability": "National Framework on Traceability in Fisheries 2025 released",
        "unconfirmed": ("'Rs 2,500 cr Budget 2026-27 allocation' appears only on "
                        "unofficial guide sites — NOT verified, do not cite"),
    },
    "pm_mkssy": {
        "what": ("Central-sector sub-scheme Rs 6,000+ cr FY24-27 (FINAL YEAR "
                 "now): NFDP registration, aquaculture insurance incentive "
                 "(<=4 ha), credit facilitation, performance grants to "
                 "micro/small units"),
        "apply_via": [{"url": "https://nfdp.dof.gov.in/", "http_status": 200},
                      {"url": "https://www.myscheme.gov.in/schemes/pm-mkssy-1a",
                       "http_status": 200}],
        "blocked": "pmmkssy.dof.gov.in TCP-refused from this machine (000)",
    },
    "fidf": {
        "corpus": "Rs 7,522.48 cr, extended to 2025-26",
        "terms": ("interest subvention up to 3% pa, NLE rate floor 5%, 12-yr "
                  "tenure incl. 2-yr moratorium; NLEs = NABARD, NCDC, all "
                  "scheduled banks"),
        "status_mar_2026": ("228 projects approved Rs 5,559.54 cr; Rs 1,600.56 cr "
                            "disbursed. TN largest user (108 projects, "
                            "Rs 2,169.03 cr), then MH, GJ"),
        "portal": {"url": "https://fidf.in/home/", "http_status": 200,
                   "note": "fidf.dof.gov.in is NXDOMAIN — fidf.in is real"},
    },
    "mpeda": {
        "exports_fy26": ("RECORD: 19,72,018 t, Rs 73,890.46 cr (USD 8.46 bn); "
                         "frozen shrimp 66.52% of USD earnings; US shipments "
                         "FELL 19.51% by volume on tariffs, diverted to "
                         "China/EU/SE-Asia"),
        "exports_fy25": "16,98,170 t, USD 7.45 bn; shrimp 69.46%",
        "access": ("mpeda.gov.in 200 but WordPress pretty-URLs 404 — use "
                   "?page_id=438; stats PDF-only; exporter registry scrapeable "
                   "at e-mpeda.nic.in ASP.NET pages (200); rgca.org.in DNS "
                   "SERVFAIL from this machine"),
    },
    "us_tariff": {
        "stack": ("CVD 5.63-5.87% + AD 0-2.49% (Oct-2024 finals) + IEEPA "
                  "reciprocal tariff that peaked ~50% in Aug-2025 (~58% "
                  "effective) then CUT TO 18% by the Feb-2026 US-India deal "
                  "(AD/CVD remain on top); 'India Shrimp Tariff Act' 40% bill "
                  "still only proposed"),
        "impact": ("FY26 US volumes -19.5% (CRISIL had projected 15-18%); "
                   "record diversion kept total exports at all-time high"),
    },
    "state_policies": [
        {"state": "Odisha", "policy": "Fisheries Policy 2015 (PDF verified 200)",
         "note": "+ Food & Seafood Processing = IPR-2022 Priority Sector (20% uncapped capital-subsidy stack, layer 33 x state-policy doc link)"},
        {"state": "Tamil Nadu", "policy": "Dept Policy Notes; largest FIDF borrower (108 projects)"},
        {"state": "Andhra Pradesh", "policy": "2015-vintage policy; largest PMMSY user (~Rs 2,398.72 cr); interest subsidy incl. FEED/SEED manufacturers + aqua power tariff"},
        {"state": "Kerala", "policy": "Dept schemes page verified"},
        {"state": "Gujarat", "policy": "Commissioner-of-Fisheries assistance schemes (hatcheries, shrimp farms)"},
    ],
    "investment_angles": [
        "Feed mills: FIDF-eligible (3% subvention) + PMMSY 40/60% capital assistance",
        "Processing: FIDF funded 18 plant expansions Rs 345.89 cr; MPEDA TDSVMP Rs 118.10 cr to 89 units; PM-MKSSY grants for quality systems",
        "Cold chain: routed through FIDF/PMMSY, NOT the Agriculture Infrastructure Fund (AIF is agri-produce; fisheries has its own fund)",
    ],
    "db_linkage": ("Foreign lead: Charoen Pokphand Foods (Thailand, layer 16) — "
                   "world-scale shrimp-feed player with India aquaculture ops = "
                   "the FIDF feed-mill lane's natural user. No EC-filer seafood "
                   "processors in the clearance pool (the 'marine' hits are "
                   "pigment/aero false positives) — a gap worth watching"),
}

EXCISE_BOTTLING = {
    "what": ("State-excise fee stack on distilleries/bottlers — the cost side "
             "of the twin's E20 ethanol cohort (14+ EC-filing distilleries) "
             "and alco-bev leads"),
    "fee_stack": ("4-6 levies on the same litre, re-set annually: activity "
                  "license fees (capacity-slabbed) + BOTTLING FEE per BL/case "
                  "+ excise duty (the big one) + inter-state export/import "
                  "fees + cesses (e.g. Punjab cow-welfare Rs 1.5/PL)"),
    "primary_sourced_rates": {
        "Rajasthan": {"bottling_fee": "IMFL Rs 4/BL · CL/ENA-RML Rs 5/BL · beer Rs 3/BL (w.e.f. 1-4-2022, still current under 2025-29 policy)",
                      "duty": "Rs 310-370/LPL + 75% of EDP",
                      "source": "excise.rajasthan.gov.in/Downloads/RSED/PDF/NewLicanseFee.pdf (200, clean text layer — best machine-readable fee schedule in India; note 'Licanse' filename typo)"},
    },
    "verified_but_rate_unpublished": {
        "Uttar Pradesh": ("2026-27: CL basic licence Rs 32/BL MGQ + Rs 273/BL retail "
                          "privilege; CLB 4 paise/200ml; NEW 75% single-distillery "
                          "brand-supply cap (volume risk to large CL suppliers); "
                          "IMFL per-BL bottling rate NOT primary-verifiable "
                          "(indiacode PDF host connection-refused)"),
        "Madhya Pradesh": "composite structure; duty Rs 414-2,682/PL slabs; Hindi-filename PDFs, worst machine-readability",
        "Karnataka": "17 AED slabs (hiked 16-40% in 2023, more since); beer 195% floor; bottling rate under 1967 Rules unpublished",
        "Punjab": "policy PDF not discoverable on portal; fee facts via MoPNG letter + press",
        "Delhi": "old regime frozen at 2022-23 terms to Mar-2026; import-fee market, no distillery base",
    },
    "legal_shift": {
        "case": "State of UP v. Lalta Prasad Vaish, SC 9-judge bench, 23-Oct-2024 (8:1)",
        "holding": ("'intoxicating liquor' (Entry 8, List II) COVERS industrial/"
                    "denatured alcohol — overrules Synthetics & Chemicals 1990; "
                    "states can now regulate and levy fees on the ENA/denatured "
                    "stream that feeds BOTH potable and fuel output"),
        "consequence": ("regulatory-fee creep is now the structural risk for "
                        "fuel-ethanol economics — Punjab's Rs 1/BL ethanol "
                        "regulatory fee (Policy 2025-26 Para 29) is the first "
                        "mover; MoPNG formally asked for rollback (8-Apr-2025); "
                        "Haryana + HP flagged with similar levies"),
    },
    "ethanol_treatment": ("fuel ethanol bears NO bottling fee/potable duty (5% "
                          "GST instead) but pays licence/renewal/capacity/"
                          "supervision/transport-pass fees — and post-Lalta-"
                          "Prasad, whatever states invent next"),
    "recent_shocks": [
        "Maharashtra Jun-2025: IMFL retail +~50%, duty to ~4.5x mfg cost, new MML category (UNSP/Pernod/Allied Blenders exposure)",
        "Punjab Apr-2025: Rs 1/BL ethanol fee + 'substantial' licence hikes (MoPNG rollback demand)",
        "Karnataka 2025-26: beer AED to 195%/Rs 130 floor; UBL petitions",
        "UP Feb-2026: MGQ +4-8%, 75% brand cap, MRP rounding",
    ],
    "db_linkage": ("E20 ethanol cohort in layer 32 (policy_program='Ethanol "
                   "Blending Programme E20'): Kamakhya Biofuels, Bannari Amman "
                   "Sugars, RSLD Biofuels (HIGH-RISK regrade), Bapuna Spirits, "
                   "Mowa, Keyaan, Atharv, Inamdar + potable-side Pernod Ricard "
                   "India, Allied Blenders, Amur Spirits. The Lalta-Prasad fee "
                   "risk applies to ALL of them; the Maharashtra duty shock "
                   "hits the potable names"),
    "access": ("all 6 state excise dept sites reachable; dead: upexciseportal.in, "
               "legacy rajexcise.gov.in, indiacode PDF host; NO state publishes "
               "CSV/JSON — PDF extraction, refresh annually Feb-Mar"),
}

CUSTOMS_DUTIES = {
    "what": ("Import/export duty posture per twin focus sector, post "
             "Union Budget 2026-27 (Feb-2026) — the tariff half of the "
             "duty x incentive stacks layer 30 maps"),
    "sector_posture": {
        "semiconductors_electronics": ("fab/display machinery duty-free; mobile "
                                       "components 2.5%->NIL (Feb-2026); phones 15% BCD; "
                                       "Semicon Mission 2.0 Rs 40,000 cr funded"),
        "ev_batteries": ("li-ion cell capital goods BCD-exempt EXTENDED + expanded "
                         "to BESS (~85 machinery categories + 35 EV-battery capital "
                         "goods); critical minerals NIL (cobalt powder, li-ion "
                         "scrap); 🔴 exemption end-date CONFLICT in sources — "
                         "Mar-2028 vs 31-Mar-2029 — resolve from the Feb-2026 "
                         "customs notification before citing"),
        "solar": ("cells 20% BCD + 7.5% AIDC, modules 20% + 20% AIDC (Feb-2025 "
                  "restructure of 25/40% — AIDC escapes FTA concessions); "
                  "sodium antimonate (solar glass input) 7.5%->NIL Feb-2026"),
        "steel": ("12% SAFEGUARD (not BCD) on flat products 21-Apr-2025, stepping "
                  "11.5% (Apr-2026) -> 11% (to Apr-2028), definitive notification "
                  "31-Dec-2025; NO export duty since Nov-2022"),
        "chemicals_apis": ("KOH 0->7.5% (protective); naphtha + alpha-pinene "
                           "exemptions LAPSED; 17 cancer drugs BCD-exempt; "
                           "Rs 600 cr for 3 chemical parks"),
        "textiles": "input BCD cuts + export-obligation window 6->12 months",
        "seafood": "duty-free input entitlement RAISED 1%->3% of prior-year FOB",
    },
    "export_duties_in_force": [
        "iron ore lumps/fines >=58% Fe: 30% (unchanged since Nov-2022)",
        "parboiled rice: 10% (halved from 20%)",
        "NOT in force: steel (since Nov-2022), onion (removed Apr-2026), molasses (removed pro-ethanol), low-grade-ore proposal DEFERRED; sugar = quantity ban to Sep-2026, not a duty",
    ],
    "duty_incentive_stacks": [
        "Solar triple lock: BCD+AIDC wall + ALMM demand restriction + PLI supply subsidy; input duty then removed to fix inversion",
        "Mobile ladder: 15% finished > sub-assembly > components NIL + MPMS Rs 62,500 cr (Jul-2026; 2.25-5% + 1.5% domestic-sourcing bonus)",
        "ACC full stack: PLI-ACC + duty-free capex to Mar-2028 + NIL feedstock + critical-minerals-processing equipment exemption",
    ],
    "lookup_routes": {
        "working": {
            "WITS (World Bank)": "200 — API + bulk India schedules (lags current year)",
            "ICEGATE CIP duty calculator": "foservices.icegate.gov.in/cip/ 200 — SPA, endpoints need browser-devtools discovery (blind POST 405)",
            "taxinformation.cbic.gov.in": "200, backing REST API exists but 401 anonymous",
        },
        "blocked_from_this_machine": ["indiantradeportal.in 403 (the canonical FTA-rate lookup)",
                                      "macmap.org 403", "old.cbic.gov.in 000",
                                      "tariffdata.wto.org 000", "content.dgft.gov.in PDFs 403"],
    },
    "ftas_in_force": "UAE CEPA (2022) · Australia ECTA (2022) · EFTA TEPA (1-Oct-2025, 3/5/7/10-yr phase-outs)",
    "db_linkage": ("Feeds layer 30 (trade-deficit map): the safeguard explains "
                   "steel-import-chapter policy coverage; the li-ion/BESS "
                   "machinery exemption underwrites the ACC/ESS clearance "
                   "filers; seafood input entitlement ties to the MPEDA "
                   "exporter base in the fisheries block"),
}

EXIM_BANK = {
    "what": ("India Exim Bank as financing channel + structured data source — "
             "fully open site, no bot-blocking, no API"),
    "loc_xlsx": {
        "note": ("THE machine-readable asset: three quarterly .xlsx files "
                 "(GOI LOC Statistics 298 rows ~USD 25.49bn/61 countries; "
                 "Operative LOCs 238 project-level rows; Pipeline). Direct "
                 "curl, no auth. Parse from the ENGLISH header row (row 6 — "
                 "row 5 is Hindi); watch INR-denominated text rows (Seychelles "
                 "INR 1,250 cr); FILTER OUT Purpose ~ FITL/Restructuring "
                 "(Ghana/Zambia/SL debt treatments, not new money)"),
        "current_links_scraped_on_build": [],  # filled live
        "official_cumulative": "307 LOCs, USD 27.25bn, 63 countries (FY26 results)",
    },
    "programs": {
        "Ubharte Sitaare": ("Rs 250 cr AIF (+greenshoe); Rs 2,111 cr deployed "
                            "to 106 entities as of 2026-03-31; turnover <= "
                            "Rs 500 cr, export-oriented, tech-differentiated — "
                            "the 106 list is a verified export-champion "
                            "cross-match target for layer 32"),
        "BC-NEIA": "buyer's credit to sovereign buyers, up to 85% of contract, non-recourse to exporter",
        "EOU term loans": "project/expansion finance; eligibility exports >= 20% of turnover",
        "Overseas Investment Finance": "equity/loans into Indian companies' foreign JV/WOS, 5-7 yr",
    },
    "research": ("WP-155 NE-states export landscape (Jun-2026), WP-154 trade "
                 "competitiveness, WP-153 LAC footprint, medical-devices study "
                 "2026; 5 PDF economic trackers + quarterly ELI export forecast"),
    "financials_fy26": ("loan book Rs 2,07,779 cr (+11.9%), PAT Rs 4,273 cr "
                        "(+31.7%), GNPA 0.57%, net NPA 0.01%, CRAR 26.39%"),
    "db_linkage": ("(a) EOU 20%-export test = screen for export-oriented "
                   "clearance leads; (b) LOC xlsx = 'engineered exports' "
                   "series for layer 30; (c) eprocure.eximbankindia.in = early "
                   "signal of Indian EPC winners on LOC projects; (d) weak "
                   "inbound-FDI signal by design (outbound instruments)"),
}


def main():
    live = "--no-live" not in sys.argv
    if live:
        try:
            links = scrape_exim_loc_links()
            EXIM_BANK["loc_xlsx"]["current_links_scraped_on_build"] = [
                "https://www.eximbankindia.in" + l for l in links]
        except Exception as e:
            EXIM_BANK["loc_xlsx"]["current_links_scraped_on_build"] = [
                f"SCRAPE FAILED: {type(e).__name__}"]
    checked = {}
    if live:
        for u in ("https://pmmsy.dof.gov.in/", "https://fidf.in/home/",
                  "https://mpeda.gov.in/?page_id=438",
                  "https://excise.rajasthan.gov.in/",
                  "https://excise.up.gov.in/",
                  "https://www.eximbankindia.in/lines-of-credit",
                  "https://wits.worldbank.org/",
                  "https://foservices.icegate.gov.in/cip/"):
            checked[u] = status(u)

    layer = {
        "layer": 33,
        "name": "policy_finance_extensions",
        "built": date.today().isoformat(),
        "what": ("Fisheries incentive stack, state-excise bottling-fee economics, "
                 "import/export duty posture, and India Exim Bank — four analysis "
                 "blocks with per-claim sources, HTTP-verified access routes, and "
                 "explicit layer-32 company linkages. Research sweep 2026-07-23."),
        "fisheries": FISHERIES,
        "excise_bottling": EXCISE_BOTTLING,
        "customs_duties": CUSTOMS_DUTIES,
        "exim_bank": EXIM_BANK,
        "url_liveness": checked,
        "refresh_guidance": {
            "annual_feb_mar": "state excise policies (UP/MP/Punjab) + Union Budget duty changes",
            "quarterly": "Exim LOC xlsx (links re-scraped by this script)",
            "on_event": "US tariff moves (Feb-2026 deal at 18%; shrimp bill pending), Lalta-Prasad fee creep by more states",
            "open_conflict": "li-ion machinery exemption end-date (Mar-2028 vs Mar-2029) — resolve from Feb-2026 customs notification",
        },
    }
    with open(OUT, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    print("loc links scraped:", len(EXIM_BANK["loc_xlsx"]["current_links_scraped_on_build"]),
          "| urls checked:", len(checked))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
