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
import sqlite3

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


def load_raw_sources():
    rows = {}

    p = os.path.join(SCRATCH, "pdfs", "aeroindia2019_foreign.txt")
    if os.path.exists(p):
        out = []
        for l in open(p):
            m = re.match(r"\s*\d+\s+(.+?)\s{2,}([A-Z][A-Z .]+)\s*$", l)
            if m:
                out.append({"company": m.group(1).strip().rstrip("*").strip(),
                           "country": m.group(2).strip().title()})
        rows["Aero India 2019 (foreign exhibitors)"] = out

    p = os.path.join(SCRATCH, "semicon_india_2025_names.txt")
    if os.path.exists(p):
        rows["SEMICON India 2025"] = [{"company": l.strip(), "country": None}
                                      for l in open(p) if l.strip()]

    p = os.path.join(SCRATCH, "pdfs", "aahar2024.txt")
    if os.path.exists(p):
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
        rows["AAHAR 2024 (Hall 1, foreign participation)"] = out

    p = os.path.join(SCRATCH, "textile_pdfs", "india_itme_2022_exhibitors.txt")
    if os.path.exists(p):
        NOISE = {"EMBROIDERY,", "PROCESSING", "SPINNING", "WEAVING", "DIGITAL PRINTING",
                "KNITTING,", "GARMENTING"}
        out = []
        for l in open(p):
            if l.startswith("INTERNATIONAL"):
                rest = l[len("INTERNATIONAL"):].strip()
                name = re.split(r"\s{2,}", rest)[0].strip()
                if name and name not in NOISE and len(name) > 2:
                    out.append({"company": name, "country": None})
        rows["India ITME 2022 (international exhibitors)"] = out

    # -- Railways sector: durable repo data (data/trade_fairs/railways/), not
    # ephemeral scratch -- these survive to future sessions.
    p = os.path.join(ROOT, "data", "trade_fairs", "railways", "innotrans_2026_exhibitors.csv")
    if os.path.exists(p):
        with open(p) as f:
            rows["InnoTrans 2026 (all exhibitors)"] = [
                {"company": r["company"], "country": r["country"]} for r in csv.DictReader(f)]

    p = os.path.join(ROOT, "data", "trade_fairs", "railways", "iree_2025_key_exhibitors.json")
    if os.path.exists(p):
        entries = json.load(open(p))
        # foreign/foreign-parent only, excluding rows flagged as likely parser
        # merge-artifacts (two company names concatenated) -- see that file's
        # README for the full origin_flag heuristic and its caveats
        rows["IREE 2025 (foreign / foreign-parent, clean subset)"] = [
            {"company": e["company"], "country": None} for e in entries
            if e.get("origin_flag", "").startswith("FOREIGN") and not e.get("possible_merge_artifact")]

    # -- Messe Frankfurt / Messe Düsseldorf: durable repo data, "name" column
    MESSE_FILES = [
        ("Light + Building 2026 (Messe Frankfurt)", "messe_frankfurt", "lightbuilding_exhibitors.csv"),
        ("ISH 2027 (Messe Frankfurt)", "messe_frankfurt", "ish_exhibitors.csv"),
        ("Heimtextil 2027 (Messe Frankfurt)", "messe_frankfurt", "heimtextil_exhibitors.csv"),
        ("interpack 2026 (Messe Düsseldorf)", "messe_duesseldorf", "interpack_exhibitors.csv"),
        ("EuroShop 2026 (Messe Düsseldorf)", "messe_duesseldorf", "euroshop_exhibitors.csv"),
        ("wire & Tube Düsseldorf 2026 (Messe Düsseldorf)", "messe_duesseldorf", "wire_dusseldorf_exhibitors.csv"),
    ]
    for label, subdir, fname in MESSE_FILES:
        p = os.path.join(ROOT, "data", "trade_fairs", subdir, fname)
        if os.path.exists(p):
            with open(p) as f:
                rows[label] = [{"company": r["name"], "country": r.get("country_label")}
                               for r in csv.DictReader(f) if r.get("name")]

    return rows


def known_names():
    names = set()
    leads_path = os.path.join(ROOT, "layers", "16_leads.json")
    if os.path.exists(leads_path):
        for l in json.load(open(leads_path))["leads"]:
            names.add(l["company"].strip().lower())
    if os.path.exists(DB):
        try:
            con = sqlite3.connect(DB)
            for (n,) in con.execute("SELECT name FROM companies"):
                if n:
                    names.add(n.strip().lower())
            con.close()
        except sqlite3.Error:
            pass
    return names


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
