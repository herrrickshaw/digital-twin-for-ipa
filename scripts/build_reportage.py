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


def quarter_of(datestr):
    y, mth = int(datestr[:4]), int(datestr[5:7])
    return f"{y}Q{(mth - 1) // 3 + 1}"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, date, ministry, title FROM pib_items ORDER BY date").fetchall()
    by_q = defaultdict(lambda: {"mapped": [], "cabinet_other": [], "dropped": 0})
    for prid, date, ministry, title in rows:
        hits = [(s, m) for rx, s, m in COMP if rx.search(title or "")]
        ministry = ministry or "(unattributed)"
        is_cab = ministry.startswith("Cabinet")
        q = quarter_of(date)
        if hits:
            hits = [(refine_pli(s, title), m) for s, m in hits]
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
    write_html(by_q, total)
    write_html_ministry(by_q, total)


MONTHS={m:i+1 for i,m in enumerate(["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"])}
def _extract_date(text):
    """Find the first plausible dd-mm-yyyy / dd Month yyyy / Month-yyyy date in text; return ISO or None."""
    t=text or ""
    m=re.search(r"\b(\d{1,2})[-./](\d{1,2})[-./](20[12]\d)\b", t)
    if m:
        d,mo,y=int(m.group(1)),int(m.group(2)),int(m.group(3))
        if 1<=mo<=12 and 1<=d<=31: return f"{y:04d}-{mo:02d}-{d:02d}"
    m=re.search(r"\b(\d{1,2})[- ]([A-Za-z]{3,9})[- ,]*(20[12]\d)\b", t)
    if m and m.group(2)[:3].lower() in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(2)[:3].lower()]:02d}-{min(int(m.group(1)),28):02d}"
    m=re.search(r"\b([A-Za-z]{3,9})[- ](20[12]\d)\b", t)
    if m and m.group(1)[:3].lower() in MONTHS:
        return f"{int(m.group(2)):04d}-{MONTHS[m.group(1)[:3].lower()]:02d}-15"
    return None


def state_announcements():
    """Dated state-scheme events from layers 12 (policy GR/notification dates) and 18 (funds evidence)."""
    import json as _j, glob as _g
    rows=[]
    for f in _g.glob(os.path.join(ROOT, "layers/12_state_catalog/*.json")):
        if "ocr_extracts" in f: continue
        d=_j.load(open(f))
        for s in d.get("states", []):
            for p in s.get("policies", []):
                blob=" ".join(str(p.get(k,"")) for k in ("name","status","site_notes","what_companies_get"))
                iso=_extract_date(blob)
                if iso and iso>="2017-01-01":
                    rows.append({"date":iso,"state":s["state"].title(),"scheme":p.get("name","")[:110],
                                 "detail":(p.get("status") or p.get("site_notes") or "")[:150],
                                 "url":p.get("site_url","")})
    try:
        mon=_j.load(open(os.path.join(ROOT, "layers/18_state_monitor.json")))
        for s in mon["states"]:
            for sc in s["schemes"]:
                for e in sc.get("funds_evidence", []):
                    iso=_extract_date(str(e.get("date","")))
                    if iso and e.get("figure") and "UNVERIFIED" not in e.get("figure",""):
                        rows.append({"date":iso,"state":s["state"].title(),"scheme":sc["scheme"][:110],
                                     "detail":(e.get("figure","")+" -- "+e.get("fact",""))[:170],
                                     "url":e.get("source_url","")})
    except FileNotFoundError:
        pass
    return rows


def render_states():
    """State-level incentives section from layers/18_state_monitor.json + instrument counts from layer 12."""
    import html as _h, json as _j, glob as _g
    try:
        mon = _j.load(open(os.path.join(ROOT, "layers/18_state_monitor.json")))
    except FileNotFoundError:
        return "<p>(state monitor layer not built)</p>"
    counts = {}
    for f in _g.glob(os.path.join(ROOT, "layers/12_state_catalog/*.json")):
        d = _j.load(open(f))
        for s in d.get("states", []):
            counts[s["state"].upper()] = len(s.get("policies", []))
    parts = ['<div style="background:var(--accent-soft);border-radius:8px;padding:12px 16px;margin-bottom:18px;'
             'font-family:-apple-system,sans-serif;font-size:.85rem;">'
             + "".join(f"<p style='margin:4px 0'>{_h.escape(h)}</p>" for h in mon.get("headline_findings", []))
             + "</div>"]
    for st in mon["states"]:
        n = counts.get(st["state"].upper(), "")
        parts.append(f'<section class="q"><h2>{_h.escape(st["state"].title())} '
                     f'<span class="n">&middot; {n} catalogued instruments</span></h2>')
        for sc in st["schemes"]:
            arrears = any("arrear" in (e.get("fact","")+sc.get("status_2025_26","")).lower() or "pending" in e.get("fact","").lower()
                          for e in sc.get("funds_evidence", []))
            flag = ' <span class="chip" style="background:#7a2e2e22;color:var(--warn);">arrears signal</span>' if arrears else ""
            parts.append(f'<div class="row" data-q="state" data-s="{_h.escape(sc["scheme"][:60], quote=True)}" data-m="State governments" data-st="{_h.escape(st["state"].title(), quote=True)}">'
                         f'<div class="top"><span class="chip">{_h.escape(sc["scheme"][:80])}</span>{flag}</div>'
                         f'<div class="title" style="font-size:.88rem;color:var(--muted);">{_h.escape(sc.get("status_2025_26","")[:260])}</div>')
            for e in sc.get("funds_evidence", [])[:4]:
                fig = _h.escape(e.get("figure",""))
                fact = _h.escape(e.get("fact","")[:200])
                url = e.get("source_url","")
                src = _h.escape(e.get("source_type",""))
                link = f' <a href="{url}" target="_blank" rel="noopener" class="prid">[{src}]</a>' if url and url.startswith("http") else f' <span class="prid">[{src}]</span>'
                parts.append(f'<div style="font-size:.85rem;margin:5px 0 0;"><b>{fig}</b> — {fact}{link}</div>')
            arts = sc.get("news_articles", [])
            if arts:
                parts.append('<div style="font-size:.78rem;color:var(--muted);margin-top:6px;font-family:-apple-system,sans-serif;">News: '
                             + " · ".join(f'<a href="{a["url"]}" target="_blank" rel="noopener" style="color:var(--accent)">{_h.escape(a["outlet"])} ({_h.escape(str(a.get("date",""))[:10])})</a>'
                                          for a in arts[:3] if a.get("url","").startswith("http")) + "</div>")
            parts.append("</div>")
        parts.append("</section>")
    return "\n".join(parts)


def write_html(by_q, total):
    """Emit docs/reportage.html -- house-style page; list pre-rendered (works without JS), filters via JS."""
    import html as _h
    st_by_q = {}
    for r in state_announcements():
        st_by_q.setdefault(quarter_of(r["date"]), []).append(r)
    parts = []
    all_qs = sorted(set(list(by_q.keys()) + list(st_by_q.keys())), reverse=True)
    for q in all_qs:
        rows = by_q[q]["mapped"] if q in by_q else []
        strows = sorted(st_by_q.get(q, []), key=lambda r: r["date"])
        if not rows and not strows:
            continue
        n = len(rows) + len(strows)
        parts.append(f'<section class="q" data-q="{q}"><h2>{q} <span class="n">&middot; {n} announcement{"s" if n>1 else ""} ({len(strows)} state)</span></h2>')
        for date, prid, ministry, title, hits in rows:
            scheme = "; ".join(s for s, _ in hits)
            chips = "".join(f'<span class="chip">{_h.escape(s)}</span>' for s, _ in hits)
            parts.append(
                f'<div class="row" data-q="{q}" data-s="{_h.escape(scheme, quote=True)}" data-m="{_h.escape(ministry, quote=True)}" data-st="Central">'
                f'<div class="top"><span class="date">{date}</span>{chips}<span class="min">{_h.escape(ministry)}</span></div>'
                f'<div class="title"><a href="https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}" target="_blank" rel="noopener">'
                f'{_h.escape((title or "")[:160])}</a> <span class="prid">PRID {prid}</span></div></div>')
        for r in strows:
            link = (f'<a href="{r["url"]}" target="_blank" rel="noopener">' if r.get("url","").startswith("http") else "<span>")
            close = "</a>" if r.get("url","").startswith("http") else "</span>"
            parts.append(
                f'<div class="row" style="border-left-color:var(--warn);" data-q="{q}" '
                f'data-s="{_h.escape(r["scheme"][:60], quote=True)}" data-m="{_h.escape(r["state"], quote=True)}" data-st="{_h.escape(r["state"], quote=True)}">'
                f'<div class="top"><span class="date">{r["date"]}</span>'
                f'<span class="chip" style="background:#8a5a1222;color:var(--warn);">STATE · {_h.escape(r["state"])}</span>'
                f'<span class="min">{_h.escape(r["scheme"][:80])}</span></div>'
                f'<div class="title" style="font-size:.9rem;">{link}{_h.escape(r["detail"])}{close}</div></div>')
        parts.append("</section>")
    tpl = open(os.path.join(ROOT, "docs/_reportage_template.html")).read()
    html_out = tpl.replace("__ROWS__", "\n".join(parts)).replace("__STATES__", render_states()).replace("__TOTAL__", str(total)).replace(
        "__NQ__", str(len(by_q))).replace("__GEN__", datetime.date.today().isoformat()).replace("__POLICY__", render_policy_annex())
    path = os.path.join(ROOT, "docs/reportage.html")
    open(path, "w").write(html_out)
    print(f"reportage html: {sum(len(v['mapped']) for v in by_q.values())} rows pre-rendered -> {path}")


def write_html_ministry(by_q, total):
    """Emit docs/reportage_ministry.html -- MINISTRY-WISE companion view (owning ministry
    per the twin's scheme map; Cabinet/CCEA rows file under their line ministry), rows
    time-stamped with the release date, newest first. Pre-rendered (works without JS),
    filters (quarter/scheme/ministry/state/search) via JS. Does NOT replace the
    quarter-wise docs/reportage.html -- both are built every run."""
    import html as _h
    # flatten central rows, keyed by the scheme's owning ministry from the twin map
    by_min = defaultdict(list)
    for q, d in by_q.items():
        for date, prid, ministry, title, hits in d["mapped"]:
            owner = hits[0][1] if hits else "various"
            by_min[owner].append((date, q, prid, ministry, title, hits))
    parts = []
    for owner in sorted(by_min, key=lambda k: (-len(by_min[k]), k)):
        rows = sorted(by_min[owner], reverse=True)  # newest first
        latest = rows[0][0]
        parts.append(f'<section class="q" data-min="{_h.escape(owner, quote=True)}">'
                     f'<h2>{_h.escape(owner)} <span class="n">&middot; {len(rows)} announcement{"s" if len(rows)>1 else ""}'
                     f' &middot; latest {latest}</span></h2>')
        for date, q, prid, ministry, title, hits in rows:
            scheme = "; ".join(s for s, _ in hits)
            chips = "".join(f'<span class="chip">{_h.escape(s)}</span>' for s, _ in hits)
            parts.append(
                f'<div class="row" data-q="{q}" data-s="{_h.escape(scheme, quote=True)}" data-m="{_h.escape(owner, quote=True)}" data-st="Central">'
                f'<div class="top"><span class="date">{date}</span>{chips}<span class="min">register: {_h.escape(ministry)}</span></div>'
                f'<div class="title"><a href="https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}" target="_blank" rel="noopener">'
                f'{_h.escape((title or "")[:160])}</a> <span class="prid">PRID {prid}</span></div></div>')
        parts.append("</section>")
    # dated state-scheme events: one section, grouped visually by state chips, newest first
    strows = sorted(state_announcements(), key=lambda r: r["date"], reverse=True)
    if strows:
        parts.append(f'<section class="q" data-min="State governments"><h2>State governments '
                     f'<span class="n">&middot; {len(strows)} dated scheme events &middot; latest {strows[0]["date"]}</span></h2>')
        for r in strows:
            link = (f'<a href="{r["url"]}" target="_blank" rel="noopener">' if r.get("url","").startswith("http") else "<span>")
            close = "</a>" if r.get("url","").startswith("http") else "</span>"
            parts.append(
                f'<div class="row" style="border-left-color:var(--warn);" data-q="{quarter_of(r["date"])}" '
                f'data-s="{_h.escape(r["scheme"][:60], quote=True)}" data-m="State governments" data-st="{_h.escape(r["state"], quote=True)}">'
                f'<div class="top"><span class="date">{r["date"]}</span>'
                f'<span class="chip" style="background:#8a5a1222;color:var(--warn);">STATE · {_h.escape(r["state"])}</span>'
                f'<span class="min">{_h.escape(r["scheme"][:80])}</span></div>'
                f'<div class="title" style="font-size:.9rem;">{link}{_h.escape(r["detail"])}{close}</div></div>')
        parts.append("</section>")
    tpl = open(os.path.join(ROOT, "docs/_reportage_ministry_template.html")).read()
    html_out = tpl.replace("__ROWS__", "\n".join(parts)).replace("__STATES__", render_states()).replace("__TOTAL__", str(total)).replace(
        "__NQ__", str(len(by_min))).replace("__GEN__", datetime.date.today().isoformat()).replace("__POLICY__", render_policy_annex())
    path = os.path.join(ROOT, "docs/reportage_ministry.html")
    open(path, "w").write(html_out)
    print(f"reportage ministry html: {sum(len(v) for v in by_min.values())} central rows + {len(strows)} state rows "
          f"across {len(by_min)} ministries -> {path}")




def render_policy_annex():
    """Annex: clearance-register policy findings + the source cross-verification
    matrix (layer 24c). Injected into both reportage variants via __POLICY__.

    The point of the matrix: no committed company name rests on a single source.
    EC/FC counts are ground-truthed direct from the raw PARIVESH registers and
    are deliberately BROADER (all years/statuses) than the 2025-26 lead subset."""
    import html as _h
    import json, os
    p = os.path.join(ROOT, "layers/24c_cross_verification.json")
    if not os.path.exists(p):
        return ""
    d = json.load(open(p))
    rows = []
    for r in sorted(d["companies"], key=lambda r: -( (r.get("ec_register") or {}).get("filings",0) + (r.get("fc_register") or {}).get("filings",0) )):
        ec = (r.get("ec_register") or {}).get("filings")
        fc = (r.get("fc_register") or {}).get("filings")
        pib = (r.get("pib_headlines") or {}).get("headlines")
        def cell(v, cls="y"):
            return f'<td class="cv {cls}">{v}</td>' if v else '<td class="cv n">—</td>'
        nv = r.get("news_verdict") or ""
        nvc = {"ANNOUNCED":"y","PARTIALLY_VISIBLE":"p","QUIET":"q"}.get(nv,"n")
        ib = r.get("ibef")   # True / False / None(=not checked)
        ibcell = ('<td class="cv y">✓</td>' if ib is True
                  else '<td class="cv n">—</td>' if ib is False
                  else '<td class="cv" style="opacity:.3">·</td>')
        rows.append(
            f'<tr><td class="cn">{_h.escape(r["company"])}</td>'
            + cell(ec) + cell(fc)
            + cell(pib)
            + cell("✓" if r.get("iem_partB_sample") else None)
            + cell("✓" if r.get("state_govt_announcement") else None)
            + cell("✓" if r.get("pli_ebp_register") else None)
            + cell("✓" if r.get("credit_rating_public") else None)
            + ibcell
            + f'<td class="cv {nvc}">{nv.replace("_"," ").title() or "—"}</td></tr>')
    return f"""
<section id="policy-annex" style="max-width:1100px;margin:40px auto 20px;padding:0 20px;">
<h2 style="font-family:Georgia,serif;font-weight:500;">Annex — what the clearance registers add (policy findings)</h2>
<div style="font-size:.92rem;max-width:80ch;line-height:1.55;">
<p><b>1. Half of India's live industrial EC pipeline is chemicals.</b> Of 1,384 live corporate industrial
filers beyond the verified leads, 51% file under synthetic-organic-chemicals — the China import-substitution
story is already the dominant physical activity in the clearance register, mostly self-funded and mostly
unannounced.</p>
<p><b>2. The API localisation wave is running outside PLI.</b> The only confirmed KSM/API-PLI beneficiary
in the 98 verified leads (Orchid Pharma, ₹600 cr 7-ACA) carries the cohort's worst execution profile
(land delays, downgrade), while IOL, Farmson, Anthem, Aarti, Piramal and Virupaksha localise the same
China-dependent chains self-funded. Land assembly, not incentive size, is the binding constraint.</p>
<p><b>3. Verified foreign capex is visible in the registers before the press.</b> Lanxess (DE), Pernod
Ricard (FR, ₹1,785 cr Nagpur), HS Hyosung (KR, ~₹3,000 cr cumulative), Kansai Nerolac (JP), Sumitomo (JP,
via TruAlt), plus SRF's Odisha filings fronting the ₹10,000 cr pledge.</p>
<p><b>4. Cross-verification: no name rests on one source.</b> All 41 headline companies ground-truth in the
raw PARIVESH registers; only 17 have <i>ever</i> appeared in a PIB headline — the registers see ~2.4× more
of these investors than PIB headlines do. IEM Part-B company data is held for only two sample months, so
absence there is weak evidence.</p>
<p><b>5. Rating darkness is a screening signal.</b> Withdrawn or issuer-not-cooperating credit ratings
cluster around exactly the companies expanding quietly — Farmson (CARE withdrawn 2023, world's largest
paracetamol maker), RSL/RSLD (CARE withdrawn 2025 after disclosing SEBI/IT/ED promoter litigations),
Bodal (CRISIL withdrawn), D&nbsp;R&nbsp;Coats and Matangi (non-cooperating, Matangi the same quarter it
filed ECs), Sandhya (non-cooperating). Announcement darkness and rating darkness travel together:
a live clearance filing plus a dead rating is itself a below-radar-expansion screen — and where the
last rationale exists, it often carries the only adverse disclosures (litigations, guarantees) no
other public source records.</p>
<p><b>6. IBEF promotes the themes, misses the executors.</b> The Commerce-Ministry trust's coverage actively
champions all four policy narratives — specialty-chem import substitution, API/KSM PLI, E20 ethanol, MMF PLI —
with the exact framing this analysis uses. But its company coverage tracks <i>listing status</i>, not
clearance activity: 20 of 37 checked names have zero IBEF footprint, including marquee FDI stories (Hyosung's
$100M spandex plant, Pernod Ricard's ₹1,785 cr distillery) and every quiet builder. The quasi-official
promotion channel validates the macro thesis while missing the specific companies executing it — the
clearance register is the earlier, more complete signal.</p></div>
<style>
#policy-annex table{{border-collapse:collapse;width:100%;font-size:.78rem}}
#policy-annex th{{font-size:.62rem;text-transform:uppercase;letter-spacing:.05em;text-align:left;padding:5px 7px;border-bottom:1px solid var(--rule,#ccc);opacity:.7}}
#policy-annex td{{padding:4px 7px;border-bottom:1px solid var(--rule,#e3e3dc)}}
#policy-annex td.cn{{white-space:nowrap;font-weight:600}}
#policy-annex td.cv{{text-align:center;font-variant-numeric:tabular-nums}}
#policy-annex td.cv.n{{opacity:.35}} #policy-annex td.cv.y{{color:#2f7d4f}} #policy-annex td.cv.p{{color:#8a5a12}} #policy-annex td.cv.q{{color:#a5402c;font-weight:600}}
#policy-annex .scroll{{overflow-x:auto}}
</style>
<div class="scroll"><table>
<thead><tr><th>Company</th><th>EC register<br>(all-time filings)</th><th>Forest reg.</th><th>PIB headlines<br>(2017-26)</th>
<th>IEM Part-B<br>(2-mo sample)</th><th>State-govt<br>announcement</th><th>PLI / EBP<br>register</th><th>Public credit<br>rating</th><th>IBEF<br>coverage</th><th>News verdict</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p style="font-size:.72rem;opacity:.65;max-width:86ch;">EC/Forest counts are ground-truthed from the raw PARIVESH
registers (all years, statuses, activities) and are deliberately broader than the 2025-26 live-manufacturing
subset used for lead scoring. PIB is a title-only index — annexure PDFs are a known blind spot. "Quiet" = live
clearance filings with zero press. Sources &amp; data: layers/24_clearance_leads.json · 24b_pool_policy_triage.json ·
24c_cross_verification.json. Generated {datetime.date.today().isoformat()}.</p>
{render_up_ethanol()}
</section>"""




def render_up_ethanol():
    """Case study injected under the policy annex: UP ethanol, register x news
    (layer 24d). UP is the EBP's #1 state -- the table shows every significant
    live 5(g) filer with its news-verified project detail."""
    import html as _h
    import json, os
    p = os.path.join(ROOT, "layers/24d_up_ethanol.json")
    if not os.path.exists(p):
        return ""
    d = json.load(open(p))
    ra = d["register_aggregates"]
    rows = "".join(
        f'<tr><td class="cn">{_h.escape(r["company"])}</td>'
        f'<td>{_h.escape(r["district"])}</td>'
        f'<td>{_h.escape(r["capacity"])}</td>'
        f'<td>{_h.escape(r["feedstock"])}</td>'
        f'<td class="cv">{("&#8377;" + format(round(r["capex_rs_cr"]), ",") + " cr") if r["capex_rs_cr"] else "—"}</td>'
        f'<td class="cv {"q" if "QUIET" in r["status"] else "y"}">{_h.escape(r["status"])}</td>'
        f'<td style="font-size:.72rem;opacity:.8">{_h.escape(r["note"])}</td></tr>'
        for r in d["companies"])
    return f"""
<h3 style="font-family:Georgia,serif;font-weight:500;margin-top:30px;">Case study — Uttar Pradesh ethanol: the register × the news</h3>
<div style="font-size:.9rem;max-width:82ch;line-height:1.5;">
<p>{_h.escape(d["up_context"])}</p>
<p>The PARIVESH register holds <b>{ra["up_5g_proposals_total"]} UP distillery (5(g)) proposals</b> —
<b>{ra["live"]} live</b> across <b>{ra["unique_companies"]} companies</b>. The {len(d["companies"])} most
significant, register-verified and news-checked:</p></div>
<div class="scroll"><table>
<thead><tr><th>Company</th><th>District</th><th>Capacity / project</th><th>Feedstock</th><th>Capex</th><th>Status</th><th>Note</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p style="font-size:.72rem;opacity:.65;max-width:86ch;">Register side = PARIVESH EC 5(g) filings (all years; live = granted
+ in-process). News side = 2024-26 sweep. Notables: Karimganj's UP-vs-Assam location discrepancy resolved (Moradabad);
TQN "Retails" verified as a genuine &#8377;224 cr ethanol proponent; Modi Illva is potable malt, not EBP — feedstock
disambiguation applied. Data: layers/24d_up_ethanol.json.</p>"""


if __name__ == "__main__":
    main()
