#!/usr/bin/env python3
"""Quarterly reportage: key announcements from the PIB register mapped to scheme + ministry.

Source: the policy repo's PIB SQL register (122k+ releases, 2017 -> today, refreshed
daily by the cron 'pib' job). "Key" = Cabinet/CCEA approvals plus line-ministry
releases whose titles hit the twin's scheme-keyword map. Every line carries its PRID
(clickable), ministry, and the scheme(s) it maps to.

Output: docs/REPORTAGE.md (generated view -- never hand-edit). Per quarter:
scheme-mapped announcements first, then unmapped Cabinet approvals, with an honest
"not shown" count when a quarter is capped.

Rerun after every PIB refresh worth reporting:  python3 scripts/build_reportage.py
"""
import datetime, os, re, sqlite3
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.expanduser("~/india-trade-sector-policy-recommendations/data/pib_index.sqlite")
CAP_PER_QUARTER = 30

# scheme-keyword map: regex (case-insensitive) -> (scheme label, owning ministry per the twin)
SCHEMES = [
 (r"\bPLI\b|production[- ]linked", "PLI (family)", "sectoral ministry / DPIIT"),
 (r"semicon|\bISM\b|fab\b|display fab|OSAT|ATMP", "India Semiconductor Mission / Semicon", "MeitY"),
 (r"\bECMS\b|electronics component", "ECMS", "MeitY"),
 (r"\bMPMS\b|mobile phone manufacturing scheme", "MPMS (LSEM successor)", "MeitY"),
 (r"\bSPECS\b", "SPECS", "MeitY"),
 (r"green hydrogen|electrolyser|electrolyzer|green ammonia|\bSIGHT\b", "NGHM / SIGHT", "MNRE"),
 (r"\bKUSUM\b", "PM-KUSUM", "MNRE"),
 (r"surya ghar|rooftop solar", "PM Surya Ghar", "MNRE"),
 (r"\bALMM\b|solar (module|cell) manufactur", "Solar PLI / ALMM", "MNRE"),
 (r"\bFAME\b|E-?DRIVE|electric mobility|\bEMPS\b", "FAME / PM E-DRIVE", "Heavy Industries"),
 (r"advanced chemistry cell|\bACC\b.{0,20}(battery|storage)", "PLI-ACC", "Heavy Industries"),
 (r"battery energy storage|\bBESS\b", "BESS VGF (PSDF)", "Power"),
 (r"\bRDSS\b|distribution sector scheme", "RDSS", "Power"),
 (r"ethanol", "EBP / ethanol interest subvention", "MoPNG / DFPD"),
 (r"\bSATAT\b|compressed bio.?gas|\bCBG\b", "SATAT / CBG", "MoPNG"),
 (r"coal gasification", "Coal gasification incentives", "Coal"),
 (r"critical mineral|\bKABIL\b|rare earth", "Critical Minerals Mission / RE magnet scheme", "Mines"),
 (r"specialty steel", "PLI Specialty Steel", "Steel"),
 (r"\bUNNATI\b|north.?east.{0,15}industriali[sz]", "UNNATI 2024 (ex NEIDS)", "DPIIT"),
 (r"\bNIPU\b|urea.{0,25}(policy|plant)|new investment policy.{0,10}urea", "NIP/NIPU urea investment policy", "Fertilizers"),
 (r"nutrient based subsidy|\bNBS\b|\bDAP\b.{0,20}subsid", "NBS fertilizer subsidy", "Fertilizers"),
 (r"\bPMFME\b|micro food processing", "PMFME", "MoFPI"),
 (r"\bPMKSY\b|kisan sampada", "PMKSY", "MoFPI"),
 (r"food processing.{0,20}(PLI|incentive)|\bPLISFPI\b", "PLI-FPI", "MoFPI"),
 (r"agriculture infrastructure fund|\bAIF\b", "Agriculture Infrastructure Fund", "Agriculture"),
 (r"\bAHIDF\b|animal husbandry infrastructure", "AHIDF", "DAHD"),
 (r"\bPMMSY\b|matsya sampada", "PMMSY", "Fisheries"),
 (r"textile.{0,25}(PLI|park|MITRA)|\bMITRA\b|man.?made fib|technical textile", "PM MITRA / textiles PLI", "Textiles"),
 (r"\bRoSCTL\b", "RoSCTL", "Textiles"),
 (r"\bRoDTEP\b", "RoDTEP", "Commerce"),
 (r"\bSEZ\b", "SEZ framework", "Commerce"),
 (r"medical device|bulk drug|pharmaceutical.{0,20}(PLI|park|incentive)|\bPRIP\b", "Pharma/medical-devices incentives", "Pharmaceuticals"),
 (r"\biDEX\b|\bADITI\b|defence.{0,15}innovation", "iDEX / ADITI", "Defence"),
 (r"defence.{0,20}corridor|positive indigeni[sz]ation|\bSRIJAN\b", "Defence corridors / indigenisation", "Defence"),
 (r"shipbuilding|\bSBFAS\b|maritime development fund|\bSbDS\b", "Shipbuilding package", "Ports & Shipping"),
 (r"gati shakti.{0,15}(cargo|terminal)|\bGCT\b", "Gati Shakti Cargo Terminals", "Railways"),
 (r"vehicle scrapp|\bRVSF\b", "Vehicle Scrapping / RVSF", "MoRTH"),
 (r"\bELI\b|employment linked incentive", "ELI", "Labour/EPFO"),
 (r"\bPM-?SETU\b|ITI upgradation", "PM-SETU", "MSDE"),
 (r"\bNAPS\b|apprenticeship promotion", "NAPS", "MSDE"),
 (r"\bRDI\b.{0,20}(scheme|fund)|research development and innovation scheme", "RDI Scheme", "DST/ANRF"),
 (r"\bBioE3\b", "BioE3", "DBT"),
 (r"urban challenge fund|\bUCF\b", "Urban Challenge Fund", "MoHUA"),
 (r"e-?bus sewa", "PM-eBus Sewa", "MoHUA"),
 (r"\bPMAY\b|awas yojana", "PMAY (U/G)", "MoHUA / Rural Dev"),
 (r"jal jeevan|\bJJM\b", "Jal Jeevan Mission", "Jal Shakti"),
 (r"namami gange", "Namami Gange (HAM)", "Jal Shakti"),
 (r"bharatnet", "BharatNet", "DoT"),
 (r"telecom.{0,20}PLI", "Telecom PLI", "DoT"),
 (r"space (policy|sector|reform)|IN-SPACe|\bNSIL\b", "Space reforms / IN-SPACe", "DoS"),
 (r"nuclear|\bSMR\b|bharat small reactor", "Nuclear opening / BSR / SHANTI", "DAE"),
 (r"green credit", "Green Credit Programme", "MoEFCC"),
 (r"\bEPR\b|extended producer", "EPR certificate markets", "MoEFCC/CPCB"),
 (r"\bDAP-?2020\b|make.{0,4}(i|ii) categor", "Make-I/II (DAP-2020)", "Defence"),
 (r"interest subvention", "Interest subvention schemes (various)", "various"),
 (r"viability gap|\bVGF\b", "VGF schemes", "DEA"),
 (r"\bNIDHI\b|startup india seed|fund of funds", "Startup funding schemes", "DST/DPIIT"),
 (r"\bPM-?DevINE\b|\bNESIDS\b", "PM-DevINE / NESIDS", "MDoNER"),
 (r"jan vishwas", "Jan Vishwas (decriminalisation)", "DPIIT"),
 (r"national manufacturing mission", "National Manufacturing Mission", "DPIIT"),
]
COMP = [(re.compile(p, re.I), s, m) for p, s, m in SCHEMES]
# generic incentive-language filter for line-ministry releases
GENERIC = re.compile(r"cabinet approv|incentive|subsid|scheme launch|\bVGF\b|outlay|crore package", re.I)


def quarter_of(datestr):
    y, mth = int(datestr[:4]), int(datestr[5:7])
    return f"{y}Q{(mth - 1) // 3 + 1}"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, date, ministry, title FROM pib_items WHERE ministry IN "
        "('Cabinet','Cabinet Committee on Economic Affairs (CCEA)') OR title LIKE '%scheme%' "
        "OR title LIKE '%incentive%' OR title LIKE '%PLI%' ORDER BY date").fetchall()
    by_q = defaultdict(lambda: {"mapped": [], "cabinet_other": [], "dropped": 0})
    for prid, date, ministry, title in rows:
        hits = [(s, m) for rx, s, m in COMP if rx.search(title or "")]
        ministry = ministry or "(unattributed)"
        is_cab = ministry.startswith("Cabinet")
        q = quarter_of(date)
        if hits:
            by_q[q]["mapped"].append((date, prid, ministry, title, hits[:2]))
        elif is_cab and GENERIC.search(title or ""):
            by_q[q]["cabinet_other"].append((date, prid, ministry, title))

    lines = ["# Quarterly Reportage — key announcements × scheme × ministry", "",
             f"*Generated {datetime.date.today().isoformat()} by `scripts/build_reportage.py` from the PIB register "
             "(122k+ releases, refreshed daily). Every row links its PRID. Scheme mapping is keyword-based — "
             "treat as an index into the register, not a substitute for reading the release.*", ""]
    total = 0
    for q in sorted(by_q, reverse=True):
        d = by_q[q]
        n = len(d["mapped"])
        total += n
        lines += [f"## {q} — {n} scheme-mapped announcements", "",
                  "| Date | Scheme | Ministry (register) | Announcement | PRID |", "|---|---|---|---|---|"]
        shown = 0
        for date, prid, ministry, title, hits in d["mapped"]:
            if shown >= CAP_PER_QUARTER:
                break
            scheme = "; ".join(s for s, _ in hits)
            url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"
            lines.append(f"| {date} | **{scheme}** | {ministry} | {(title or '')[:120].replace('|','/')} | [{prid}]({url}) |")
            shown += 1
        if n > CAP_PER_QUARTER:
            lines.append(f"| … | | | *{n - CAP_PER_QUARTER} further scheme-mapped rows not shown (cap {CAP_PER_QUARTER}) — query the register* | |")
        oth = d["cabinet_other"]
        if oth:
            lines += ["", f"<details><summary>Other Cabinet/CCEA approvals this quarter ({len(oth)})</summary>", ""]
            for date, prid, ministry, title in oth[:15]:
                url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"
                lines.append(f"- {date} · {(title or '')[:130]} · [{prid}]({url})")
            if len(oth) > 15:
                lines.append(f"- … {len(oth) - 15} more")
            lines += ["", "</details>"]
        lines.append("")
    out = os.path.join(ROOT, "docs/REPORTAGE.md")
    open(out, "w").write("\n".join(lines))
    print(f"reportage: {total} scheme-mapped announcements across {len(by_q)} quarters -> {out}")


if __name__ == "__main__":
    main()
