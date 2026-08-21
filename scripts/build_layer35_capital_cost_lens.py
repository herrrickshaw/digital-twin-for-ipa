#!/usr/bin/env python3
"""Layer 35 — capital-cost arbitrage lens.

Prioritizes which foreign markets to sweep for NEW India-inbound leads, using
policy-rate gap vs India as one signal among several. Source table: the
author's own "Cheaper than India, on paper" analysis (masaladeutsch, 2026-08-03,
raising-green-debt-globally-rec-euroyen.html, section 5a-i) — 25 economies
with a policy rate below India's repo rate, 13 flagged with capital-market
depth sufficient for institutional issuance.

Important scope note (why this ISN'T a mechanical re-application of that
post's conclusion): the blog's finding is that covered-interest-parity (CIP)
hedging cancels most of the apparent rate advantage for a CROSS-BORDER BOND
INVESTOR who must hedge back to a reference currency to compare like-for-like
yields. That cancellation does NOT transfer to a multinational funding REAL
CAPEX (a factory, a plant) from a foreign parent's balance sheet: FDI returns
are equity-like and routinely left unhedged as ordinary MNC practice, so the
parent's cheaper domestic WACC survives as a genuine (if partial, and not
sole) driver of hurdle rates and expansion appetite. The rate gap is kept
here as ONE prioritization signal, not a scored certainty.

Cross-references LIVE (local reads, no network):
  - layers/16_leads.json          -- current per-country lead coverage (thin
                                      coverage = under-sampled, not "no good
                                      companies exist there")
  - layers/31_ipa_source_network.json -- which of these countries already
                                      have a catalogued IPA data source vs a
                                      gap layer 31 should add next

Output: layers/35_capital_cost_arbitrage_lens.json + docs/CAPITAL_COST_ARBITRAGE.md
Usage:  python3 scripts/build_layer35_capital_cost_lens.py
"""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "35_capital_cost_arbitrage_lens.json")
OUT_DOC = os.path.join(ROOT, "docs", "CAPITAL_COST_ARBITRAGE.md")

SOURCE_POST = {
    "title": ("Raising Green Debt Globally: The REC EuroYen Playbook, the CBI "
              "Stamp, and Every Avenue an Indian Issuer Actually Has"),
    "url": "https://masaladeutsch.blogspot.com/2026/08/raising-green-debt-globally-rec-euroyen.html",
    "section": "5a-i. Cheaper than India, on paper — and why most of it is unreachable",
    "published": "2026-08-03",
}

INDIA_POLICY_RATE = {"rate_pct": 5.25, "instrument": "RBI repo rate",
                      "as_of": "2026-08 (blog snapshot; repo rate moves on MPC "
                                "cadence -- re-verify against rbi.org.in before "
                                "citing in anything dated later)"}

# Curated from the source post's table. deep_capital_market = the post's
# "Issuance Feasibility: Yes" flag (institutional-depth offshore bond market)
# -- kept here as a proxy for developed/liquid capital markets generally, NOT
# recomputed. "Euro area" from the original table is expanded to its member
# states already present in the twin's country vocabulary (layer 16/31),
# since the twin tracks countries, not currency blocs.
RATE_TABLE = [
    {"economy": "Switzerland", "rate_pct": 0.00, "deep_capital_market": True},
    {"economy": "Japan", "rate_pct": 1.00, "deep_capital_market": True},
    {"economy": "Thailand", "rate_pct": 1.00, "deep_capital_market": False},
    {"economy": "Sweden", "rate_pct": 1.75, "deep_capital_market": True},
    {"economy": "Denmark", "rate_pct": 1.85, "deep_capital_market": True},
    {"economy": "Canada", "rate_pct": 2.25, "deep_capital_market": True},
    {"economy": "Morocco", "rate_pct": 2.25, "deep_capital_market": False},
    {"economy": "Germany", "rate_pct": 2.25, "deep_capital_market": True, "note": "Euro area member"},
    {"economy": "France", "rate_pct": 2.25, "deep_capital_market": True, "note": "Euro area member"},
    {"economy": "Netherlands", "rate_pct": 2.25, "deep_capital_market": True, "note": "Euro area member"},
    {"economy": "Italy", "rate_pct": 2.25, "deep_capital_market": True, "note": "Euro area member"},
    {"economy": "South Korea", "rate_pct": 2.50, "deep_capital_market": True},
    {"economy": "New Zealand", "rate_pct": 2.50, "deep_capital_market": False},
    {"economy": "Malaysia", "rate_pct": 2.75, "deep_capital_market": False},
    {"economy": "China", "rate_pct": 3.00, "deep_capital_market": True},
    {"economy": "Kuwait", "rate_pct": 3.50, "deep_capital_market": False},
    {"economy": "United States", "rate_pct": 3.62, "deep_capital_market": True},
    {"economy": "Czechia", "rate_pct": 3.75, "deep_capital_market": False},
    {"economy": "United Kingdom", "rate_pct": 3.75, "deep_capital_market": True},
    {"economy": "Israel", "rate_pct": 3.75, "deep_capital_market": False},
    {"economy": "Poland", "rate_pct": 3.75, "deep_capital_market": False},
    {"economy": "Hong Kong", "rate_pct": 4.00, "deep_capital_market": True},
    {"economy": "North Macedonia", "rate_pct": 4.25, "deep_capital_market": False},
    {"economy": "Norway", "rate_pct": 4.25, "deep_capital_market": True},
    {"economy": "Peru", "rate_pct": 4.25, "deep_capital_market": False},
    {"economy": "Saudi Arabia", "rate_pct": 4.25, "deep_capital_market": False},
    {"economy": "Australia", "rate_pct": 4.35, "deep_capital_market": True},
    {"economy": "Chile", "rate_pct": 4.50, "deep_capital_market": False},
]

# Country-name normalization: twin leads use "South Korea", "Hong Kong" (bare);
# layer 31 non_waipa_ipas/country_ipas use "Korea, Rep." / "Hong Kong" -- keep
# a small alias map rather than forcing one spelling everywhere.
LEADS_COUNTRY_ALIAS = {"South Korea": "South Korea", "Hong Kong": "Hong Kong"}


def load_json(rel):
    path = os.path.join(ROOT, rel)
    return json.load(open(path)) if os.path.exists(path) else None


def main():
    leads = load_json("layers/16_leads.json")
    ipa_net = load_json("layers/31_ipa_source_network.json")

    lead_country_counts = {}
    if leads:
        for l in leads["leads"]:
            lead_country_counts[l["country"]] = lead_country_counts.get(l["country"], 0) + 1

    ipa_covered_countries = set()
    if ipa_net:
        for i in ipa_net["global"]["country_ipas"]:
            ipa_covered_countries.add(i["country"])
        for i in ipa_net["non_waipa_ipas"]:
            if i.get("url"):
                ipa_covered_countries.add(i["country"])

    rows = []
    for r in RATE_TABLE:
        econ = r["economy"]
        gap = round(INDIA_POLICY_RATE["rate_pct"] - r["rate_pct"], 2)
        coverage = lead_country_counts.get(LEADS_COUNTRY_ALIAS.get(econ, econ), 0)
        row = {
            "economy": econ,
            "policy_rate_pct": r["rate_pct"],
            "gap_vs_india_pts": gap,
            "deep_capital_market": r["deep_capital_market"],
            "note": r.get("note"),
            "twin_lead_coverage": coverage,
            "coverage_flag": ("THIN" if coverage <= 3 else
                               "MODERATE" if coverage <= 8 else "COVERED"),
            "ipa_source_catalogued": econ in ipa_covered_countries,
        }
        rows.append(row)

    # Sweep-priority: real economy (deep_capital_market) AND (thin lead
    # coverage OR no catalogued IPA source yet) -- these are the markets where
    # a new source would plausibly surface names the static catalog missed,
    # not the markets that are merely "cheap on paper" (Thailand/Morocco/
    # Kuwait/Peru/N.Macedonia -- excluded, matching the source post's own
    # "unreachable" finding, for the unrelated reason of thin capital-market
    # depth correlating with weaker corporate-disclosure infrastructure too).
    priority = [r for r in rows if r["deep_capital_market"]
                and (r["coverage_flag"] != "COVERED" or not r["ipa_source_catalogued"])]
    priority.sort(key=lambda r: (-r["gap_vs_india_pts"], r["twin_lead_coverage"]))

    excluded_shallow = [r["economy"] for r in rows if not r["deep_capital_market"]]

    layer = {
        "layer": 35,
        "name": "capital_cost_arbitrage_lens",
        "built": datetime.date.today().isoformat(),
        "what": ("Prioritizes which foreign markets to build NEW company-discovery "
                 "sweeps for (layers 36+), using policy-rate gap vs India as one "
                 "signal alongside existing twin coverage. Source: the author's own "
                 "cross-border debt-issuance research, repurposed here for a "
                 "different question (equity/capex expansion propensity, not bond "
                 "arbitrage) -- see 'analysis_scope_note'."),
        "source_post": SOURCE_POST,
        "india_policy_rate": INDIA_POLICY_RATE,
        "analysis_scope_note": (
            "The source post's core finding -- 'covered interest parity means the "
            "currency with the lower policy rate carries the more expensive hedge, "
            "and the two very nearly cancel' -- applies to a cross-border BOND "
            "investor who must hedge back to a reference currency for a like-for-like "
            "yield comparison. It does not mechanically transfer to a multinational "
            "funding real capex in India from a foreign parent's balance sheet: FDI "
            "returns are equity-like and ordinarily left unhedged (translation risk "
            "is routine MNC practice), so the parent's cheaper domestic cost of "
            "capital survives as a genuine, if partial, driver of hurdle rates and "
            "expansion appetite. Treated here as ONE prioritization signal, not a "
            "scored certainty -- deep_capital_market is a market-depth proxy carried "
            "verbatim from the source post's bond-market context, and correlates with "
            "(but does not prove) an FDI-relevant developed economy."),
        "rate_table": rows,
        "excluded_shallow_markets": excluded_shallow,
        "sweep_priority": priority,
        "feeds": {
            "layer_36_non_us_filing_sweeps": [r["economy"] for r in priority],
            "layer_31_ipa_source_network_gaps": [
                r["economy"] for r in priority if not r["ipa_source_catalogued"]],
        },
    }
    with open(OUT_JSON, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)

    L = ["# Capital-cost arbitrage lens — which foreign markets to sweep next", "",
         f"*Generated {layer['built']} by `scripts/build_layer35_capital_cost_lens.py` from "
         f"[{SOURCE_POST['title']}]({SOURCE_POST['url']}), {SOURCE_POST['section']}. "
         "Do not hand-edit.*", "",
         f"India policy rate: **{INDIA_POLICY_RATE['rate_pct']}%** ({INDIA_POLICY_RATE['instrument']}, "
         f"{INDIA_POLICY_RATE['as_of']}).", "",
         "## Scope note", "", layer["analysis_scope_note"], "",
         "## Sweep-priority markets (deep capital market + thin twin coverage or no IPA source yet)", "",
         "| Economy | Rate | Gap vs India | Lead coverage | IPA source? |",
         "|---|---|---|---|---|"]
    for r in priority:
        L.append(f"| {r['economy']} | {r['policy_rate_pct']}% | {r['gap_vs_india_pts']} pts | "
                 f"{r['twin_lead_coverage']} leads ({r['coverage_flag']}) | "
                 f"{'yes' if r['ipa_source_catalogued'] else 'GAP'} |")
    L += ["", "## Full rate table (25 economies below India's repo rate)", "",
          "| Economy | Rate | Gap | Deep capital mkt | Lead coverage | IPA source |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['economy']} | {r['policy_rate_pct']}% | {r['gap_vs_india_pts']} | "
                 f"{'yes' if r['deep_capital_market'] else 'no'} | {r['twin_lead_coverage']} | "
                 f"{'yes' if r['ipa_source_catalogued'] else 'no'} |")
    L += ["", f"**Excluded as shallow markets** (low rate but insufficient capital-market depth, "
          f"per the source post): {', '.join(excluded_shallow)}.", ""]
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"rows: {len(rows)} | sweep-priority: {len(priority)} -> {OUT_JSON} + {OUT_DOC}")
    for r in priority:
        print(f"  {r['gap_vs_india_pts']:>5}pt  {r['economy']:16} coverage={r['twin_lead_coverage']:>3} "
              f"({r['coverage_flag']:8}) ipa_source={'yes' if r['ipa_source_catalogued'] else 'GAP'}")


if __name__ == "__main__":
    main()
