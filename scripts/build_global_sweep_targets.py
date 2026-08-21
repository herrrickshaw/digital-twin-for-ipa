#!/usr/bin/env python3
"""Global sweep targets -- consolidates every NEW discovery-source sweep built
2026-08-09 (EDGAR pre-existing; DART/cninfo/Oslo NewsWeb/EDINET/ESEF new) into
one target list of companies with offices or announced India interest, cross-
checked against the twin's existing leads (layer 16) and company DB (layer 32)
so only genuinely NEW names are flagged as such.

Deliberately NOT merged into layers/16_target_shortlist.json -- that file has
its own defined method/schema (static-catalog + EDGAR mention-mining). This is
a separate, clearly-provenanced product for the 2026-08 filing-sweep expansion,
matching the project's provenance-first convention (company_sources keeps
every source record verbatim).

Tiers:
  TIER 1 -- controlling establishment (subsidiary/branch/office opened) --
    highest-confidence, ready for outreach.
  TIER 2 -- market presence / business activity (contracts, distribution,
    market commentary) -- real relationship, lower priority than TIER 1.
  CHINA WATCHLIST -- separate, NOT mixed into TIER 1/2, per build_target_leads.py's
    existing Press Note 3 convention (amended 2026-03 but still gates
    controlling-stake establishments like these).

Usage: python3 scripts/build_global_sweep_targets.py
Output: layers/37_global_sweep_targets.json + docs/GLOBAL_SWEEP_TARGETS.md
"""
import datetime as dt
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "37_global_sweep_targets.json")
OUT_DOC = os.path.join(ROOT, "docs", "GLOBAL_SWEEP_TARGETS.md")
DB = os.path.join(ROOT, "data", "companies.db")


def load(rel):
    p = os.path.join(ROOT, rel)
    return json.load(open(p)) if os.path.exists(p) else None


def known_names():
    """Company names already in the twin (layer 16 leads + layer 32 DB), normalized."""
    names = set()
    leads = load("layers/16_leads.json")
    if leads:
        for l in leads["leads"]:
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


def is_new(name, known):
    return name.strip().lower() not in known


DART_INTENT_MARKERS = ("법인 설립", "진출", "현지법인")


def main():
    known = known_names()
    tier1, tier2 = [], []

    dart = load("layers/16_enrichment/dart_india_sweep.json")
    if dart:
        seen_dart = set()
        for r in dart["results"]:
            h = r.get("hits", {})
            hits = h.get("intent") or h.get("business")
            if not hits or r["corp_name"] in seen_dart:
                continue
            seen_dart.add(r["corp_name"])
            row = {"company": r["corp_name"], "country": "South Korea", "ticker": r["stock_code"],
                   "source": "DART (Korea)", "signal": hits[0]["snippet"].strip()[:150],
                   "new_to_twin": is_new(r["corp_name"], known)}
            (tier1 if h.get("intent") else tier2).append(row)

    oslo = load("layers/16_enrichment/oslo_newsweb_india_sweep.json")
    if oslo:
        for r in oslo["market_entry_or_investment"]:
            tier1.append({"company": r["issuer"], "country": "Norway", "ticker": r["issuer_sign"],
                          "source": "Oslo Bors NewsWeb", "signal": r["title"],
                          "new_to_twin": is_new(r["issuer"], known)})
        for r in oslo["business_activity"][:0]:  # business_activity is 143 rows, mostly noise -- not included in v1
            pass

    edinet = load("layers/16_enrichment/edinet_india_sweep.json")
    if edinet:
        for r in edinet["results"]:
            if r.get("hits"):
                tier2.append({"company": r["filer"], "country": "Japan", "ticker": r["sec_code"],
                              "source": "EDINET", "signal": r["hits"][0]["snippet"].strip()[:150],
                              "new_to_twin": is_new(r["filer"], known)})

    # 🔴 2026-08-21: discovered via `git log` that a SEPARATE Claude Code session
    # (2026-08-12, outside this conversation's awareness) already built a
    # Switzerland sweep (SIX Equity Issuer News, richer than Oslo's title-only
    # feed) and an Electronics & Semiconductors sector-wide expansion, and
    # wrote docs/INTEGRATED_TARGET_DECISION.md synthesizing them against the
    # PLI beneficiary roster. That session explicitly left layers 35-37 and
    # this session's sweep scripts untouched ("committed in isolation from
    # unrelated in-progress work") -- folding its real results in here now.
    switzerland = load("layers/16_enrichment/switzerland_india_sweep.json")
    if switzerland:
        for r in switzerland["market_entry_or_investment"]:
            tier1.append({"company": r["company"], "country": "Switzerland", "ticker": r.get("ticker"),
                          "source": "SIX Equity Issuer News (2026-08-12 session)",
                          "signal": r.get("title", "")[:150], "new_to_twin": is_new(r["company"], known)})

    electronics = load("layers/16_enrichment/electronics_semiconductors_sector_expansion.json")
    if electronics:
        for r in electronics["market_entry_or_investment"]:
            tier1.append({"company": r["company"], "country": r.get("country") or "United States",
                          "ticker": None, "source": "Sector expansion: Electronics & Semiconductors "
                          "(2026-08-12 session, SEC 10-K mining)",
                          "signal": "confirmed India market-entry/investment disclosure",
                          "new_to_twin": is_new(r["company"], known)})

    edgar_8k = load("layers/16_enrichment/edgar_8k_sweep.json")
    if edgar_8k:
        for e in edgar_8k["filings"]:
            if e.get("segment") == "india_domiciled":
                continue
            tier1.append({"company": e["company"], "country": "United States (8-K filer)",
                          "ticker": None, "source": "EDGAR 8-K",
                          "signal": f"{e['file_date']} -- {', '.join(e['phrases'][:2])}",
                          "new_to_twin": is_new(e["company"], known)})

    esef = load("layers/16_enrichment/esef_xbrl_india_sweep.json")
    ESEF_COUNTRY_NAMES = {"GB": "United Kingdom", "FR": "France", "IT": "Italy", "NL": "Netherlands"}
    if esef:
        for r in esef["results"]:
            if r.get("hits") and r.get("entity", {}).get("name"):
                tier2.append({"company": r["entity"]["name"], "country": ESEF_COUNTRY_NAMES.get(r["country"], r["country"]),
                              "ticker": r["entity"].get("lei"), "source": "ESEF (xbrl.org)",
                              "signal": r["hits"][0]["snippet"].strip()[:150],
                              "new_to_twin": is_new(r["entity"]["name"], known)})

    cninfo = load("layers/16_enrichment/cninfo_india_sweep.json")
    china_watchlist = []
    if cninfo:
        for r in cninfo["china_pn3_watchlist"]:
            china_watchlist.append({"company": r["company"], "country": "China", "ticker": r["sec_code"],
                                    "source": "cninfo", "signal": r["title"],
                                    "new_to_twin": is_new(r["company"], known)})

    tier1_new = [r for r in tier1 if r["new_to_twin"]]
    tier2_new = [r for r in tier2 if r["new_to_twin"]]
    china_new = [r for r in china_watchlist if r["new_to_twin"]]

    out = {"layer": 37, "name": "global_sweep_targets", "built": dt.date.today().isoformat(),
           "what": ("Consolidated target list from the 2026-08 filing-sweep expansion (DART/"
                    "cninfo/Oslo NewsWeb/EDINET/ESEF) -- companies with offices or announced "
                    "India interest, cross-checked against the twin's existing leads/company DB."),
           "sources_covered": ["DART (Korea, COMPLETE -- full KOSPI+KOSDAQ sweep, 6,096 filings)",
                               "Oslo Bors NewsWeb (Norway, complete, 2015-2026)",
                               "EDINET (Japan, partial -- 430 filings, 30-day window)",
                               "cninfo (China, PN3 watch-list only)",
                               "ESEF xbrl.org (UK/FR/IT/NL) -- near-complete, ~1,200 filings",
                               "EDGAR 8-K (US, COMPLETE -- 22 filings, 2026 YTD, material-event "
                               "filings fresher than annual reports)"],
           "note": ("Snapshot, not final -- textile-specific and sector-primary news re-sweeps "
                    "were tried and found low-yield/low-precision respectively (see "
                    "layers/38_textile_sector_targets.json and session notes); re-run "
                    "this script once it completes for the full count."),
           "tier1_controlling_establishment": {"count": len(tier1), "new_to_twin": len(tier1_new), "all": tier1},
           "tier2_market_presence": {"count": len(tier2), "new_to_twin": len(tier2_new), "all": tier2},
           "china_pn3_watchlist": {"count": len(china_watchlist), "new_to_twin": len(china_new), "all": china_watchlist}}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# Global sweep targets — companies with offices or announced India interest", "",
         f"*Generated {out['built']} by `scripts/build_global_sweep_targets.py` from the 2026-08 "
         "filing-sweep expansion. Snapshot, not final — DART full sweep still running, EDINET/ESEF "
         "only lightly tested so far.*", "",
         f"## Tier 1 — controlling establishment ({len(tier1)} total, {len(tier1_new)} new to twin)", "",
         "| Company | Country | Ticker | Source | Signal |", "|---|---|---|---|---|"]
    for r in tier1:
        flag = " 🆕" if r["new_to_twin"] else ""
        L.append(f"| {r['company']}{flag} | {r['country']} | {r['ticker'] or '—'} | {r['source']} | {r['signal'][:100]} |")
    L += ["", f"## Tier 2 — market presence / business activity ({len(tier2)} total, {len(tier2_new)} new to twin)", "",
          "| Company | Country | Ticker | Source | Signal |", "|---|---|---|---|---|"]
    for r in tier2:
        flag = " 🆕" if r["new_to_twin"] else ""
        L.append(f"| {r['company']}{flag} | {r['country']} | {r['ticker'] or '—'} | {r['source']} | {r['signal'][:100]} |")
    L += ["", f"## China — Press Note 3 watch-list, NOT outreach targets ({len(china_watchlist)} total, {len(china_new)} new to twin)", "",
          "See `layers/16_leads.json` china_pn3_policy_update for the 2026-03 amendment detail. "
          "Full list in the JSON output (86 rows) — first 15 shown here:", "",
          "| Company | Ticker | Signal |", "|---|---|---|"]
    for r in china_watchlist[:15]:
        L.append(f"| {r['company']} | {r['ticker'] or '—'} | {r['signal'][:100]} |")
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"Tier 1: {len(tier1)} ({len(tier1_new)} new) | Tier 2: {len(tier2)} ({len(tier2_new)} new) | "
          f"China watch-list: {len(china_watchlist)} ({len(china_new)} new) -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
