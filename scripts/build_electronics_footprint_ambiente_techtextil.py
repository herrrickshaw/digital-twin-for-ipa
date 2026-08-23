#!/usr/bin/env python3
"""Cross-references the Ambiente + Techtextil exhibitor rosters (layer 40)
against the twin's known Electronics & Semiconductors sector universe, to
see whether either fair has any real footprint in that sector.

Two source tiers for "known electronics & semiconductor company":
  1. data/companies.db, sector IN ('Electronics & Semiconductors',
     'Semiconductors', 'Semicon equipment', 'Semicon materials & gases')
  2. layers/16_enrichment/electronics_semiconductors_sector_expansion.json
     (filing-derived, SEC 10-K/8-K sweep, market_entry_or_investment +
     business_activity tiers)

Two passes per fair:
  A. DIRECT MATCH -- exact company overlap via the same word-boundary
     strong/weak fragment matcher used everywhere else in this twin. A
     hit here means a company the twin ALREADY tracks as electronics/
     semiconductor is ALSO exhibiting at Ambiente or Techtextil.
  B. KEYWORD SCAN -- exhibitor names containing electronics/semiconductor
     or smart-textile/e-textile terms, for companies NOT already tracked.
     This is a lower-confidence, exploratory signal only (a company named
     "XYZ Electronics" could be a lamp maker, not a semiconductor firm) --
     reported separately and never merged into the direct-match count.

Usage: python3 scripts/build_electronics_footprint_ambiente_techtextil.py
Output: layers/16_enrichment/ambiente_techtextil_electronics_footprint.json
"""
import csv
import datetime as dt
import importlib.util
import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "16_enrichment", "ambiente_techtextil_electronics_footprint.json")
DB = os.path.join(ROOT, "data", "companies.db")

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

ELECTRONICS_SECTORS = ("Electronics & Semiconductors", "Semiconductors",
                       "Semicon equipment", "Semicon materials & gases")

FAIRS = {
    "Ambiente 2027": os.path.join(ROOT, "data", "trade_fairs", "messe_frankfurt", "ambiente_exhibitors.csv"),
    "Techtextil 2027": os.path.join(ROOT, "data", "trade_fairs", "messe_frankfurt", "techtextil_exhibitors.csv"),
}

# Lower-confidence keyword signals -- deliberately separate from the direct
# DB/filing match. "Electronics"/"Electronic" alone is too generic (lamps,
# appliances) so it's included but flagged as the weakest signal.
# "IC" must stay case-sensitive (upper) -- case-insensitive matched Turkish
# "Ic" in "... Ic ve Dis Ticaret ..." (domestic/foreign trade boilerplate),
# a real false positive caught on the first run against Ambiente/Techtextil.
KEYWORD_RE = re.compile(
    r"\b(Semiconductor|Semicon|Micro ?chip|Integrated Circuit|Sensor(s)?|"
    r"Circuit(s)?|LED|Smart Home|IoT|Wearable(s)?|Conductive (Fiber|Fibre|Yarn|Textile)|"
    r"E-Textile|Smart Textile|Fiber Optic|Photonic|Electronic(s)?)\b", re.I)
KEYWORD_IC_RE = re.compile(r"\bIC\b")


def known_electronics_companies():
    names = set()
    if os.path.exists(DB):
        con = sqlite3.connect(DB)
        qmarks = ",".join("?" for _ in ELECTRONICS_SECTORS)
        for (n,) in con.execute(f"SELECT name FROM companies WHERE sector IN ({qmarks})", ELECTRONICS_SECTORS):
            if n:
                names.add(n.strip())
        con.close()

    p = os.path.join(ROOT, "layers", "16_enrichment", "electronics_semiconductors_sector_expansion.json")
    if os.path.exists(p):
        d = json.load(open(p))
        for tier in ("market_entry_or_investment", "business_activity", "exit_or_divestment"):
            for e in d.get(tier, []):
                c = e.get("company", "")
                # strip trailing "(NasdaqGS:SMCI)"-style ticker annotation
                c = re.sub(r"\s*\([^)]*:[^)]*\)\s*$", "", c).strip()
                if c:
                    names.add(c)
    return names


def main():
    known = known_electronics_companies()
    print(f"known electronics/semiconductor companies loaded: {len(known)}")

    results = {}
    for fair, path in FAIRS.items():
        if not os.path.exists(path):
            print(f"  {fair}: SKIPPED, file not found at {path}")
            continue
        with open(path) as f:
            exhibitors = list(csv.DictReader(f))

        direct_hits = []
        for r in exhibitors:
            name = r.get("name")
            if not name:
                continue
            n = norm(name)
            frags = match_fragments(n)
            strong = [fr for fr, q in frags if q == "strong"]
            if not strong:
                continue
            for kn in known:
                if any(re.search(rf"\b{re.escape(fr)}\b", norm(kn)) for fr in strong):
                    direct_hits.append({"exhibitor": name, "country": r.get("country_label"),
                                        "matched_known_company": kn})
                    break

        keyword_hits = []
        matched_names = {h["exhibitor"] for h in direct_hits}
        for r in exhibitors:
            name = r.get("name")
            if not name or name in matched_names:
                continue
            m = KEYWORD_RE.search(name) or KEYWORD_IC_RE.search(name)
            if m:
                keyword_hits.append({"exhibitor": name, "country": r.get("country_label"),
                                     "matched_term": m.group(0)})

        results[fair] = {
            "total_exhibitors": len(exhibitors),
            "direct_match_count": len(direct_hits),
            "direct_matches": direct_hits,
            "keyword_signal_count": len(keyword_hits),
            "keyword_signals_sample": keyword_hits[:40],
            "keyword_signals_truncated": max(0, len(keyword_hits) - 40),
        }
        print(f"  {fair}: {len(exhibitors)} exhibitors, {len(direct_hits)} direct electronics/semiconductor "
              f"matches, {len(keyword_hits)} lower-confidence keyword signals")

    out = {
        "built": dt.date.today().isoformat(),
        "what": ("Cross-references the Ambiente + Techtextil exhibitor rosters against the twin's "
                "known Electronics & Semiconductors universe (companies.db sector tags + the filing-"
                "derived electronics_semiconductors_sector_expansion.json). Direct matches use the "
                "same word-boundary fragment matcher as layer 41. Keyword signals are a separate, "
                "lower-confidence pass over UNMATCHED exhibitor names -- not a claim those companies "
                "are actually electronics/semiconductor firms, just a worth-a-look list."),
        "known_electronics_company_count": len(known),
        "results": results,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"\nWrote {OUT_JSON}")


if __name__ == "__main__":
    main()
