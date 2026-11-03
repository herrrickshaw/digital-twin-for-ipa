#!/usr/bin/env python3
"""Layer 41 — cross-reference layer 39/40's association/exhibitor rosters
against the twin's existing leads (layer 16) + company DB (layer 32),
flagging genuinely NEW companies not already tracked. Same discipline as
layer 37's filing-sweep cross-reference: word-boundary match via the shared
strong/weak fragment matcher (enrich_company_db_ii_tickers.py), not a guess.

Two source tiers:
  1. RAW-PARSED exhibitor lists (this session's scratch files, re-parsed
     here for a clean name+country extraction): Aero India 2019 foreign
     (160), SEMICON India 2025 (351), AAHAR 2024 Hall 1 foreign (139),
     India ITME 2022 international (148).
  2. HAND-CURATED association rosters (typed into layer 40 from live
     research, short enough to be fully captured there): JAMA (14), ASD
     Europe (51), EFPIA (47), ICMM company members (26), IPIECA (39),
     Cefic Associated Companies (23), worldsteel regular-member sample,
     VDA Manufacturer Group I (21).

Usage: python3 scripts/build_layer41_association_leads_crossref.py
Output: layers/41_association_leads_crossref.json + docs/ASSOCIATION_LEADS_CROSSREF.md
"""
import csv
import datetime as dt
import importlib.util
import json
import os
import re

from twin_common import known_company_names

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "41_association_leads_crossref.json")
OUT_DOC = os.path.join(ROOT, "docs", "ASSOCIATION_LEADS_CROSSREF.md")
# 🔴 session-ephemeral path -- these raw scratch files from the 2026-08-22
# research agents will NOT survive to a future session. Re-run the relevant
# agent (or re-download the PDF directly, URLs are in layer 40) before
# re-running this script later; load_raw_sources() skips any missing file.
SCRATCH = "/private/tmp/claude-501/-Users-umashankar/6ebb536c-0b0a-478d-a20c-1d109cb0ea89/scratchpad"
DB = os.path.join(ROOT, "data", "companies.db")

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

# Hand-curated rosters (short, fully captured in layer 40's research -- not
# re-scraped, just re-typed here for the cross-reference pass).
CURATED = {
    "JAMA": ["Daihatsu Motor", "Hino Motors", "Honda Motor", "Isuzu Motors", "Kawasaki Motors",
             "Mazda Motor", "Mitsubishi Motors", "Mitsubishi Fuso Truck & Bus", "Nissan Motor",
             "Subaru", "Suzuki Motor", "Toyota Motor", "UD Trucks", "Yamaha Motor"],
    "ASD Europe": ["Airbus", "Antonov", "Avio Aero", "BAE Systems", "Czechoslovak Group",
                   "Dassault Aviation", "Diehl", "EME", "Fincantieri", "GKN Aerospace", "Hensoldt",
                   "Indra", "KNDS", "Kongsberg", "Leonardo", "Liebherr", "MBDA", "Naval Group",
                   "Navantia", "Patria", "PGZ", "Rolls-Royce", "Saab", "Safran", "Sopra Steria",
                   "Terma", "Thales", "WB Group"],
    "EFPIA": ["AbbVie", "Almirall", "Amgen", "Astellas", "AstraZeneca", "Bayer", "Biogen",
              "Boehringer Ingelheim", "Bristol Myers Squibb", "Chiesi", "CSL Behring", "CSL Vifor",
              "Daiichi Sankyo", "Gilead", "Grünenthal", "GSK", "Ipsen", "Johnson & Johnson",
              "LEO Pharma", "Eli Lilly", "Lundbeck", "Menarini", "Merck KGaA", "MSD", "Novartis",
              "Novo Nordisk", "Otsuka", "Pfizer", "Pierre Fabre", "Roche", "Sanofi", "Servier",
              "Takeda", "Teva", "UCB", "Bial", "Eisai", "Rovi", "Stallergenes Greer", "AC Immune",
              "AiCuris", "Byondis", "Enyo Pharma", "GenFit", "Idorsia", "Minoryx", "Transgene"],
    "ICMM": ["African Rainbow Minerals", "Alcoa", "Anglo American", "AngloGold Ashanti",
             "Antofagasta Minerals", "Barrick", "BHP", "Boliden", "Codelco", "Freeport-McMoRan",
             "Glencore", "Gold Fields", "Hindustan Zinc", "Hydro", "Ma'aden",
             "Minera San Cristóbal", "Minsur", "MMG", "Newmont", "Orano", "Rio Tinto",
             "Sibanye-Stillwater", "South32", "Sumitomo Metal Mining", "Teck", "Vale"],
    "IPIECA": ["ADNOC", "Aker BP", "Aramco", "BP", "Chevron", "CNOOC", "ConocoPhillips",
               "Ecopetrol", "ENEOS", "Eni", "EOG Resources", "Equinor", "ExxonMobil",
               "Harbour Energy", "INPEX", "Murphy Oil", "OMV", "Occidental Petroleum", "Petrobras",
               "PETRONAS", "PTTEP", "QatarEnergy", "Repsol", "Shell", "Sonangol", "Suncor",
               "TotalEnergies", "Woodside", "Baker Hughes", "Halliburton", "SLB"],
    "Cefic Associated Companies": ["Gujarat Fluorochemicals", "Jubilant Pharmaceuticals",
                                   "Petronas", "Equate Petrochemicals", "Saudi Kayan", "OCP",
                                   "Methanex", "Daicel", "Asahi Kasei", "Adeka", "Tayca",
                                   "Lomon Billions"],
    "worldsteel (sample)": ["ArcelorMittal", "Nippon Steel", "POSCO Holdings", "Tata Steel",
                            "JSW Steel", "Steel Authority of India", "China Baowu Steel Group",
                            "Nucor", "United States Steel", "Cleveland-Cliffs", "Gerdau",
                            "thyssenkrupp Steel Europe", "voestalpine", "JFE Steel",
                            "Hyundai Steel", "Jindal Steel and Power", "Sunflag Iron & Steel",
                            "Saarloha Advanced Materials"],
    "VDA Group I (OEMs)": ["Audi", "Bayerische Motoren Werke", "Brabus", "Daimler Truck",
                           "Dr. Ing. h.c. F. Porsche", "Ford-Werke", "IVECO Deutschland",
                           "MAN Truck & Bus", "Mercedes-Benz", "Opel Automobile", "Stellantis Germany",
                           "TRATON", "Volkswagen"],
}


def _scratch_file(*parts):
    """Path under the (session-ephemeral) SCRATCH dir if the file exists, else None."""
    p = os.path.join(SCRATCH, *parts)
    return p if os.path.exists(p) else None


def _repo_file(*parts):
    """Path under data/trade_fairs/ if the file exists, else None."""
    p = os.path.join(ROOT, "data", "trade_fairs", *parts)
    return p if os.path.exists(p) else None


def _load_aero_india():
    p = _scratch_file("pdfs", "aeroindia2019_foreign.txt")
    if not p:
        return None
    out = []
    for l in open(p):
        m = re.match(r"\s*\d+\s+(.+?)\s{2,}([A-Z][A-Z .]+)\s*$", l)
        if m:
            out.append({"company": m.group(1).strip().rstrip("*").strip(),
                        "country": m.group(2).strip().title()})
    return "Aero India 2019 (foreign exhibitors)", out


def _load_semicon():
    p = _scratch_file("semicon_india_2025_names.txt")
    if not p:
        return None
    return "SEMICON India 2025", [{"company": l.strip(), "country": None} for l in open(p) if l.strip()]


def _load_aahar():
    p = _scratch_file("pdfs", "aahar2024.txt")
    if not p:
        return None
    # 🔴 fixed: the stop marker is "HALL 2 GROUND FLOOR", NOT "HALL NO. 2"
    # (that exact string never recurs) -- first version silently swallowed
    # every subsequent hall (1,577 "Hall 1" rows instead of ~139), caught
    # by a sanity-check against the scouting agent's own reported count.
    out, in_hall1 = [], False
    for l in open(p):
        if "HALL NO. 1" in l:
            in_hall1 = True
            continue
        if in_hall1 and re.match(r"\s*HALL\s+2\b", l):
            break
        m = re.match(r"\s*\d+\s+(.+?)\s{2,}\S", l)
        if in_hall1 and m:
            out.append({"company": m.group(1).strip(), "country": None})
    return "AAHAR 2024 (Hall 1, foreign participation)", out


def _load_itme():
    p = _scratch_file("textile_pdfs", "india_itme_2022_exhibitors.txt")
    if not p:
        return None
    NOISE = {"EMBROIDERY,", "PROCESSING", "SPINNING", "WEAVING", "DIGITAL PRINTING",
             "KNITTING,", "GARMENTING"}
    out = []
    for l in open(p):
        if l.startswith("INTERNATIONAL"):
            rest = l[len("INTERNATIONAL"):].strip()
            name = re.split(r"\s{2,}", rest)[0].strip()
            if name and name not in NOISE and len(name) > 2:
                out.append({"company": name, "country": None})
    return "India ITME 2022 (international exhibitors)", out


# -- Railways sector: durable repo data (data/trade_fairs/railways/), not
# ephemeral scratch -- these survive to future sessions.
def _load_innotrans():
    p = _repo_file("railways", "innotrans_2026_exhibitors.csv")
    if not p:
        return None
    with open(p) as f:
        return "InnoTrans 2026 (all exhibitors)", [
            {"company": r["company"], "country": r["country"]} for r in csv.DictReader(f)]


def _load_iree():
    p = _repo_file("railways", "iree_2025_key_exhibitors.json")
    if not p:
        return None
    entries = json.load(open(p))
    # foreign/foreign-parent only, excluding rows flagged as likely parser
    # merge-artifacts (two company names concatenated) -- see that file's
    # README for the full origin_flag heuristic and its caveats
    return "IREE 2025 (foreign / foreign-parent, clean subset)", [
        {"company": e["company"], "country": None} for e in entries
        if e.get("origin_flag", "").startswith("FOREIGN") and not e.get("possible_merge_artifact")]


# -- Messe Frankfurt / Messe Düsseldorf: durable repo data, "name" column.
# MF files carry a "country_label" column; Düsseldorf (vis-platform) files
# carry "country" instead -- using the wrong key silently yields None, so
# each entry below is tagged with which column its file actually has.
MESSE_FILES = [
    ("Light + Building 2026 (Messe Frankfurt)", "messe_frankfurt", "lightbuilding_exhibitors.csv", "country_label"),
    ("ISH 2027 (Messe Frankfurt)", "messe_frankfurt", "ish_exhibitors.csv", "country_label"),
    ("Heimtextil 2027 (Messe Frankfurt)", "messe_frankfurt", "heimtextil_exhibitors.csv", "country_label"),
    ("Ambiente 2027 (Messe Frankfurt)", "messe_frankfurt", "ambiente_exhibitors.csv", "country_label"),
    ("Techtextil 2027 (Messe Frankfurt)", "messe_frankfurt", "techtextil_exhibitors.csv", "country_label"),
    ("interpack 2026 (Messe Düsseldorf)", "messe_duesseldorf", "interpack_exhibitors.csv", "country"),
    ("EuroShop 2026 (Messe Düsseldorf)", "messe_duesseldorf", "euroshop_exhibitors.csv", "country"),
    ("wire & Tube Düsseldorf 2026 (Messe Düsseldorf)", "messe_duesseldorf", "wire_dusseldorf_exhibitors.csv", "country"),
    ("boot 2027 (Messe Düsseldorf)", "messe_duesseldorf", "boot_exhibitors.csv", "country"),
    ("drupa (Messe Düsseldorf)", "messe_duesseldorf", "drupa_exhibitors.csv", "country"),
    ("glasstec 2026 (Messe Düsseldorf)", "messe_duesseldorf", "glasstec_exhibitors.csv", "country"),
    ("A+A 2027 (Messe Düsseldorf)", "messe_duesseldorf", "a_a_exhibitors.csv", "country"),
    ("Caravan Salon 2026 (Messe Düsseldorf)", "messe_duesseldorf", "caravan_salon_exhibitors.csv", "country"),
]


def _load_messe():
    """-> list of (label, rows) for every Messe file present."""
    found = []
    for label, subdir, fname, country_col in MESSE_FILES:
        p = _repo_file(subdir, fname)
        if p:
            with open(p) as f:
                found.append((label, [{"company": r["name"], "country": r.get(country_col)}
                                      for r in csv.DictReader(f) if r.get("name")]))
    return found


# -- India-domestic events, deep-dived 2026-08-22 (Delhi/Mumbai gap-scan follow-up).
# ACETECH is deliberately excluded here: it produced a verified-zero roster
# (see layer 40), not a company list -- nothing to cross-reference.
def _load_iijs():
    p = _repo_file("india_domestic", "iijs", "iijs_participants.json")
    if not p:
        return None
    entries = json.load(open(p))
    return "IIJS Bharat 2026 (foreign-flagged subset)", [
        {"company": e["name"], "country": e.get("country_or_origin")}
        for e in entries if e.get("origin_flag") == "FOREIGN"]


def _load_convergence():
    p = _repo_file("india_domestic", "convergence_india", "convergence_india_participants_foreign_only.json")
    if not p:
        return None
    entries = json.load(open(p))
    entries = entries.get("participants", entries) if isinstance(entries, dict) else entries
    return "Convergence India 2026 (foreign-flagged subset)", [
        {"company": e["name"], "country": e.get("country_origin")} for e in entries]


def _load_iitf():
    p = _repo_file("india_domestic", "iitf", "iitf_participants.json")
    if not p:
        return None
    cle = json.load(open(p)).get("company_level_exhibitors", {})
    return "IITF 2025 (International Pavilion, company-level)", [
        {"company": e["name"], "country": e.get("country_origin")} for e in cle.get("records", [])]


def _load_cement_expo():
    p = _repo_file("india_domestic", "cement_expo", "cement_expo_participants.json")
    if not p:
        return None
    d = json.load(open(p))
    return "Cement Expo 2023 (foreign / foreign-parent)", [
        {"company": e["name"], "country": None} for e in d.get("participants", [])
        if str(e.get("origin_flag", "")).startswith(("FOREIGN",))]


def _load_mobile_congress():
    p = _repo_file("india_domestic", "india_mobile_congress", "india_mobile_congress_participants.json")
    if not p:
        return None
    d = json.load(open(p))
    return "India Mobile Congress 2025 (named foreign companies, lower-confidence)", [
        {"company": e["name"], "country": e.get("country_origin")}
        for e in d.get("participants", []) if str(e.get("flag_basis", "")).startswith("FOREIGN")]


# Loaders in output order; each returns (label, rows), None when its file is absent, or (for
# _load_messe) a list of such pairs. A new roster source needs one function and one entry here.
RAW_LOADERS = [_load_aero_india, _load_semicon, _load_aahar, _load_itme, _load_innotrans, _load_iree,
               _load_messe, _load_iijs, _load_convergence, _load_iitf, _load_cement_expo, _load_mobile_congress]


def load_raw_sources():
    rows = {}
    for loader in RAW_LOADERS:
        res = loader()
        if not res:
            continue
        for label, entries in (res if isinstance(res, list) else [res]):
            rows[label] = entries
    return rows


def known_names():
    """Lower-cased names already in the twin (layer 16 leads + companies.db)."""
    return known_company_names(ROOT, tolerate_db_errors=True)


# diplomatic/trade-promotion bodies, not investable companies -- exclude
# from "new lead" flags (the twin already tracks these separately in layer 31)
NON_COMPANY_RE = re.compile(
    r"\b(EMBASSY|HIGH COMMISSION|CONSULATE|TRADE (COMMISSION|COMMISSIONER)|"
    r"CHAMBER OF COMMERCE|TRADE (&|AND) INVESTMENT|INVESTMENT (&|AND) TRADE|"
    r"GOVERNMENT TRADE|TRADE PROMOTION|EXPORT (COUNCIL|PROMOTION))\b", re.I)


def is_new(name, known):
    if NON_COMPANY_RE.search(name):
        return False
    n = norm(name)
    if not n:
        return False
    frags = match_fragments(n)
    strong = [f for f, q in frags if q == "strong"]
    if not strong:
        return False  # too generic/short a name to judge either way
    for known_name in known:
        kn = norm(known_name)
        if any(re.search(rf"\b{re.escape(f)}\b", kn) for f in strong):
            return False
    return True


def main():
    known = known_names()
    print(f"known company names loaded: {len(known)}")

    results = {}
    for source, entries in load_raw_sources().items():
        seen, new_flagged = set(), []
        for e in entries:
            c = e["company"]
            if c in seen or len(c) < 4:
                continue
            seen.add(c)
            if is_new(c, known):
                new_flagged.append(e)
        results[source] = {"total_entries": len(entries), "unique": len(seen),
                           "new_to_twin": len(new_flagged), "flagged": new_flagged}
        print(f"  {source}: {len(entries)} total, {len(new_flagged)} flagged new")

    for assoc, names in CURATED.items():
        new_flagged = [{"company": c, "country": None} for c in names if is_new(c, known)]
        results[f"[curated] {assoc}"] = {"total_entries": len(names), "unique": len(names),
                                         "new_to_twin": len(new_flagged), "flagged": new_flagged}
        print(f"  [curated] {assoc}: {len(names)} total, {len(new_flagged)} flagged new")

    total_new = sum(r["new_to_twin"] for r in results.values())
    out = {"layer": 41, "name": "association_leads_crossref", "built": dt.date.today().isoformat(),
           "what": ("Cross-references layer 39/40's association/exhibitor rosters against the "
                    "twin's existing leads (layer 16, 263+ companies) and company DB (layer 32, "
                    "1,785+ companies) using the shared strong/weak fragment matcher -- flags "
                    "companies NOT already tracked. Word-boundary matched, not a guess."),
           "known_company_count": len(known), "total_new_flagged": total_new, "sources": results}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# Association/exhibitor leads — cross-referenced against existing twin data", "",
         f"*Generated {out['built']} by `scripts/build_layer41_association_leads_crossref.py`. "
         f"Checked against {len(known)} known company names (layer 16 + layer 32). "
         f"**{total_new} new companies flagged** across all sources.*", ""]
    for source, r in results.items():
        L += [f"## {source} ({r['new_to_twin']} new of {r['unique']} unique)", ""]
        if r["flagged"]:
            L += ["| Company | Country |", "|---|---|"]
            for e in r["flagged"][:60]:
                L.append(f"| {e['company']} | {e['country'] or '—'} |")
            if len(r["flagged"]) > 60:
                L.append(f"| ...+{len(r['flagged']) - 60} more | — |")
        else:
            L.append("*(none flagged)*")
        L.append("")
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"\nTOTAL new companies flagged: {total_new} -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
