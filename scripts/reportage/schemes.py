"""Scheme-keyword map, vetoes and PLI sector refinement over PIB titles."""
import re

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
 (r"critical mineral|\bKABIL\b|\bNCMM\b", "National Critical Mineral Mission", "Mines"),
 (r"rare earth|permanent magnet scheme", "Rare Earth Magnet scheme", "Heavy Industries/Mines"),
 (r"dhan-?dhaanya|\bPMDDKY\b", "PM Dhan-Dhaanya Krishi Yojana", "Agriculture"),
 (r"aatmanirbharta in pulses|pulses mission|national pulses", "Mission for Aatmanirbharta in Pulses", "Agriculture"),
 (r"dairy development|\bNPDD\b|gokul mission", "NPDD / Rashtriya Gokul Mission", "DAHD"),
 (r"export promotion mission|niryat protsahan|niryat disha|\bRELIEF\b.{0,30}export", "Export Promotion Mission", "Commerce"),
 (r"\bBHAVYA\b|audyogik vikas yojna|plug.?and.?play industrial park", "BHAVYA industrial parks", "DPIIT"),
 (r"\bUDAN\b|regional connectivity scheme|\bRCS\b", "UDAN / RCS (VGF)", "Civil Aviation"),
 (r"fund of funds|\bFFS\b|startup india seed", "Startup FoF / seed funding", "DPIIT"),
 (r"IndiaAI|india ai mission", "IndiaAI Mission (subsidized compute)", "MeitY"),
 (r"bioenergy|waste.?to.?energy|biomass programme", "National Bioenergy Programme", "MNRE"),
 (r"nuclear energy mission", "Nuclear Energy Mission (SMR)", "DAE/Finance"),
 (r"national manufacturing mission", "National Manufacturing Mission", "DPIIT"),
 (r"\bSASCI\b|challenge mode.{0,25}destinat|iconic tourist", "SASCI tourism challenge-mode", "Tourism/DEA"),
 (r"gig worker|e-?shram", "Gig-worker coverage (PM-JAY/e-Shram)", "Labour/Health"),
 (r"vishwakarma", "PM Vishwakarma", "MSME"),
 (r"\bPRIP\b", "PRIP (pharma-medtech R&D)", "Pharmaceuticals"),
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
 (r"\bNIDHI\b", "NIDHI (DST startups)", "DST"),
 (r"\bPM-?DevINE\b|\bNESIDS\b", "PM-DevINE / NESIDS", "MDoNER"),
 (r"jan vishwas", "Jan Vishwas (decriminalisation)", "DPIIT"),
 (r"mutual credit guarantee|\bMCGS\b", "MCGS-MSME credit guarantee", "Finance (DFS)"),
 (r"credit guarantee scheme for startups|\bCGSS\b", "CGSS (startups)", "DPIIT"),
 (r"\bECLGS\b|emergency credit line", "ECLGS", "Finance"),
 (r"BHIM|UPI.{0,25}incentive", "UPI incentive scheme", "MeitY"),
 (r"\bSHAKTI\b.{0,60}(coal|koyala)|(coal|koyala).{0,60}\bSHAKTI\b", "SHAKTI coal allocation", "Coal"),
 (r"\bADEETIE\b|energy.?efficien.{0,30}MSME", "ADEETIE (EE interest subsidy)", "Power/BEE"),
 (r"\bSPMEPCI\b|electric passenger car", "SPMEPCI (EV import-duty scheme)", "Heavy Industries"),
 (r"diamond imprest", "Diamond Imprest Authorisation", "Commerce"),
 (r"price stabili[sz]ation fund|\bATF\b.{0,30}(fund|support)", "ATF/price stabilisation funds", "Civil Aviation/DEA"),
 (r"scheme for investment promotion", "Scheme for Investment Promotion", "DPIIT"),
 (r"skill india programme", "Skill India Programme (incl. PM-NAPS)", "MSDE"),
]
COMP = [(re.compile(p, re.I), s, m) for p, s, m in SCHEMES]

# Keyword vetoes: same token, different programme. A scheme match is dropped when the
# title also matches the veto below. These are the acronym collisions the register
# actually contains -- IIT (ISM) Dhanbad is a mining school, not the semiconductor
# mission; Sanchar/Paryatan/Nyaya/Monument Mitra are unrelated to PM MITRA textile
# parks; "AIF" in a CCI combination order is an Alternative Investment Fund, not the
# Agriculture Infrastructure Fund; Krishi Unnati Mela (and the judoka Unnati Sharma)
# are not UNNATI 2024. Verified against the full register 4-Aug-2026: 4,066 -> 4,034 rows.
EXCLUDE = {
 "India Semiconductor Mission / Semicon": r"IIT\s*[(\-]?\s*ISM|\bISM\b[\s,)]*Dhanbad",
 "PM MITRA / textiles PLI": r"(sanchar|nyaya|monument|paryatan|sahakar|food safety|swachh|vidyut|van|krishi|kisan|vigyan)\s*mitra",
 "Agriculture Infrastructure Fund": r"alternative investment fund|\bAIF\b\s*(scheme|management)|CCI approves",
 "UNNATI 2024 (ex NEIDS)": r"krishi unnati|\bUnnati\s+[A-Z][a-z]+",
}
EXC = {k: re.compile(v, re.I) for k, v in EXCLUDE.items()}

def _vetoed(label, title):
    rx = EXC.get(label)
    return bool(rx and rx.search(title or ""))

def scheme_hits(title, with_ministry=False):
    """Scheme labels for a title, minus acronym-collision false positives."""
    if with_ministry:
        return [(s, m) for rx, s, m in COMP
                if rx.search(title or "") and not _vetoed(s, title)]
    return [refine_pli(s, title) for rx, s, m in COMP
            if rx.search(title or "") and not _vetoed(s, title)]

# PLI sector split: refine the generic "PLI (family)" label using title sector cues
PLI_SECTORS = [
 (re.compile(r"auto|automobile", re.I), "PLI — Auto & Components"),
 (re.compile(r"white goods|air condition|\bLED\b", re.I), "PLI — White Goods"),
 (re.compile(r"drone", re.I), "PLI — Drones"),
 (re.compile(r"textile|MMF|man.?made", re.I), "PLI — Textiles"),
 (re.compile(r"pharma|drug|medical device|API|KSM", re.I), "PLI — Pharma/MedDev"),
 (re.compile(r"food", re.I), "PLI — Food Processing"),
 (re.compile(r"steel", re.I), "PLI — Specialty Steel"),
 (re.compile(r"telecom", re.I), "PLI — Telecom"),
 (re.compile(r"IT hardware|laptop|server", re.I), "PLI — IT Hardware"),
 (re.compile(r"solar|module", re.I), "PLI — Solar Modules"),
 (re.compile(r"electronics|mobile|smartphone", re.I), "PLI — Electronics/LSEM"),
 (re.compile(r"battery|advanced chemistry|\bACC\b", re.I), "PLI — ACC Battery"),
]
def refine_pli(label, title):
    if label != "PLI (family)":
        return label
    for rx, sub in PLI_SECTORS:
        if rx.search(title or ""):
            return sub
    return "PLI (general)"
# generic incentive-language filter for line-ministry releases
GENERIC = re.compile(r"cabinet approv|incentive|subsid|scheme launch|\bVGF\b|outlay|crore package", re.I)
