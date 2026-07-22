#!/usr/bin/env python3
"""Layer 30 — trade-deficit & import-substitution map.

Links the twin's incentive catalogue to India's trade deficit: the sectors where
India runs the largest import bills are the import-substitution investment thesis
that PLI-type incentives exist to serve. This layer joins the import-dependency /
policy-gap analysis from the sibling repo
`india-trade-sector-policy-recommendations` (HS-chapter import value + policy
coverage, from TRADESTAT/DGCI&S) with the twin's open-incentive lanes, so each
deficit chapter is tagged with whether an incentive actually addresses it.

Trade-deficit clauses (the analytical framing this layer encodes):
  1. A large, growing import bill in a chapter is an import-substitution
     opportunity ONLY where a policy lever is sized to it — otherwise it is a
     policy GAP, not an opportunity.
  2. Process-trade chapters (import-to-re-export, e.g. gems & jewellery) are NOT
     substitution targets — trade facilitation is the relevant lever, not PLI.
  3. Structural-import chapters (crude oil, edible oils, fertilisers) cannot be
     fully substituted by industrial policy — the realistic lever is efficiency
     / alternative feedstock, not a domestic-manufacturing PLI.
  4. The bilateral deficit is concentrated (China alone ~ -$112bn) — Press Note 3
     screening + the target shortlist (layer 16) route substitution demand toward
     specific source countries.

Output: layers/30_trade_deficit_map.json. Pulls the matrix live from the repo.
"""
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "layers"
OWNER = "herrrickshaw"
POLICY_REPO = "india-trade-sector-policy-recommendations"
MATRIX_FILE = "data/import_dependency_policy_gap_analysis_2026-07-18.json"
COUNTRY_FILE = "data/country_trade_deficit_and_policy_history_2026-07-18.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# HS chapter -> twin incentive lane (which open incentive, if any, targets it)
HS_TO_INCENTIVE = {
    "27": "Coal gasification + NGHM SIGHT (partial — no crude-oil substitution)",
    "85": "Semicon/ISM 2.0 + ECMS + PLI IT Hardware (strong coverage)",
    "84": "PLI capital goods (partial)",
    "29": "PLI bulk drugs / chemicals (partial)",
    "72": "PLI Specialty Steel (partial)",
    "90": "PLI medical devices (partial)",
    "39": None, "15": None, "31": None, "28": None, "88": None, "71": None,
}
# chapters that are structural or process-trade, not manufacturing-substitutable
NON_SUBSTITUTABLE = {"27": "structural (crude/energy)",
                     "71": "process-trade (import-to-re-export)",
                     "15": "structural (edible-oil deficit)",
                     "31": "structural (fertiliser feedstock)"}


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=30) as r:
        return json.load(r)


def build():
    base = f"https://raw.githubusercontent.com/{OWNER}/{POLICY_REPO}/HEAD/"
    matrix = get_json(base + MATRIX_FILE)["matrix"]
    country = get_json(base + COUNTRY_FILE)["country_balances"]

    rows = []
    for m in matrix:
        hs = m["hs"]
        val = re.search(r"\$([\d.]+)\s*bn", m.get("value", ""))
        rows.append({
            "hs_chapter": hs, "sector": m["name"],
            "import_usd_bn": float(val.group(1)) if val else None,
            "import_note": m.get("value"), "growth": m.get("growth"),
            "policy_coverage": m.get("coverage"),   # strong|partial|gap|na
            "twin_incentive_lane": HS_TO_INCENTIVE.get(hs),
            "substitution_type": NON_SUBSTITUTABLE.get(hs, "manufacturing-substitutable"),
            "gap_note": m.get("note"),
        })
    # policy gaps = large imports with weak/no coverage that ARE substitutable
    gaps = [r for r in rows if r["policy_coverage"] in ("gap", "na", "partial")
            and r["substitution_type"] == "manufacturing-substitutable"]
    top_deficit_countries = [
        {"country": c["name"], "code": c["code"],
         "balance_usd_bn": round(c["balance"] / 1000, 1)}
        for c in sorted(country, key=lambda x: x["balance"])[:8]]

    layer = {
        "layer": 30,
        "title": "Trade-deficit & import-substitution map",
        "built": date.today().isoformat(),
        "purpose": "Link the twin's incentives to India's trade deficit: which "
                   "large import chapters an incentive actually addresses "
                   "(opportunity) versus where the deficit is uncovered (policy "
                   "gap) or not substitutable by industrial policy.",
        "source": {"repo": POLICY_REPO,
                   "url": f"https://github.com/{OWNER}/{POLICY_REPO}",
                   "datasets": [MATRIX_FILE, COUNTRY_FILE],
                   "origin": "TRADESTAT / DGCI&S HS-chapter trade, 2018-19→2025-26"},
        "trade_deficit_clauses": [
            "A large/growing import chapter is an import-substitution opportunity "
            "ONLY where a policy lever is sized to it; otherwise it is a policy "
            "GAP, not an opportunity.",
            "Process-trade chapters (gems & jewellery) are trade-facilitation "
            "cases, not PLI substitution targets.",
            "Structural imports (crude oil, edible oils, fertilisers) are not "
            "fully substitutable by manufacturing policy — the lever is "
            "efficiency / alternative feedstock.",
            "The bilateral deficit is concentrated (China ~ -$112bn); Press "
            "Note 3 screening + the target shortlist (layer 16) route "
            "substitution demand toward specific source countries.",
        ],
        "import_dependency_matrix": rows,
        "policy_gaps": [{"hs": r["hs_chapter"], "sector": r["sector"],
                         "import_usd_bn": r["import_usd_bn"],
                         "coverage": r["policy_coverage"], "note": r["gap_note"]}
                        for r in gaps],
        "top_deficit_countries": top_deficit_countries,
        "linkage": {
            "to_layer_16": "Import-substitution demand + China PN3 screening feed "
                           "the target shortlist's substitution watchlist.",
            "to_layer_17_25": "Deficit chapters with strong coverage (electronics "
                              "HS85) map to open incentives; gap chapters flag "
                              "where the incentive catalogue is silent.",
            "to_layer_26": "Substitutable-deficit sectors are where NIP/PLI "
                           "capacity projects have the clearest demand rationale.",
            "cross_repo": f"Full sector×country strategy, PLI-coverage scorecard "
                          f"and FDI pitch live in {POLICY_REPO}.",
        },
    }
    out = LAYERS / "30_trade_deficit_map.json"
    out.write_text(json.dumps(layer, indent=1, ensure_ascii=False))
    print(f"layer 30: {len(rows)} import chapters, {len(gaps)} substitutable "
          f"policy gaps, top deficit country {top_deficit_countries[0]['country']} "
          f"(${top_deficit_countries[0]['balance_usd_bn']}bn) -> {out}")


if __name__ == "__main__":
    build()
