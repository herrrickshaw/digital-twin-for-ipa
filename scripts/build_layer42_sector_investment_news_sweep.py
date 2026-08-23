#!/usr/bin/env python3
"""Layer 42 — consolidates the 12-sector India-investment news sweep
(data/news_sweeps/india_investment_sector_sweep_2026_08/, one file per the
twin's 12 core PLI-derived sectors) and cross-references every finding
against the twin's existing leads (layer 16) + company DB (layer 32),
using the same word-boundary strong/weak fragment matcher as layers 37/41.

This sweep replaces the earlier country-linked and sector-primary NewsAPI
sweeps, both of which were proven unreliable at scale (false positives from
bulk keyword search) and had their outputs discarded entirely. This pass
used 12 parallel subagents doing live WebSearch + WebFetch discovery, with
a hard rule: every finding had to be verified by actually opening and
reading the source article, not just a search-result snippet. Each sector
file also documents its own negative_notes -- real candidates checked and
explicitly ruled out, not silently dropped.

Usage: python3 scripts/build_layer42_sector_investment_news_sweep.py
Output: layers/42_sector_investment_news_sweep.json + docs/SECTOR_INVESTMENT_NEWS_SWEEP.md
"""
import datetime as dt
import importlib.util
import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_DIR = os.path.join(ROOT, "data", "news_sweeps", "india_investment_sector_sweep_2026_08")
OUT_JSON = os.path.join(ROOT, "layers", "42_sector_investment_news_sweep.json")
OUT_DOC = os.path.join(ROOT, "docs", "SECTOR_INVESTMENT_NEWS_SWEEP.md")
DB = os.path.join(ROOT, "data", "companies.db")

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments


def known_names():
    names = set()
    leads_path = os.path.join(ROOT, "layers", "16_leads.json")
    if os.path.exists(leads_path):
        for l in json.load(open(leads_path))["leads"]:
            names.add(l["company"].strip().lower())
    if os.path.exists(DB):
        con = sqlite3.connect(DB)
        for (n,) in con.execute("SELECT name FROM companies"):
            if n:
                names.add(n.strip().lower())
        con.close()
    return names


def is_new(name, known):
    n = norm(name)
    if not n:
        return False
    frags = match_fragments(n)
    strong = [f for f, q in frags if q == "strong"]
    if not strong:
        return False
    for known_name in known:
        kn = norm(known_name)
        if any(re.search(rf"\b{re.escape(f)}\b", kn) for f in strong):
            return False
    return True


def main():
    known = known_names()
    print(f"known company names loaded: {len(known)}")

    sectors = {}
    total_findings = total_new = 0
    conf_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for fname in sorted(os.listdir(SWEEP_DIR)):
        if not fname.endswith(".json"):
            continue
        d = json.load(open(os.path.join(SWEEP_DIR, fname)))
        sector = d.get("sector", fname)
        findings = d.get("findings", [])
        for f in findings:
            f["new_to_twin"] = is_new(f["company"], known)
            conf_counts[f.get("confidence", "MEDIUM")] = conf_counts.get(f.get("confidence", "MEDIUM"), 0) + 1
        new_count = sum(1 for f in findings if f["new_to_twin"])
        total_findings += len(findings)
        total_new += new_count
        sectors[sector] = {
            "source_file": fname,
            "total_findings": len(findings),
            "new_to_twin": new_count,
            "findings": findings,
            "negative_notes": d.get("negative_notes", []),
            "method": d.get("method"),
        }
        print(f"  {sector}: {len(findings)} findings, {new_count} new to twin")

    out = {
        "layer": 42, "name": "sector_investment_news_sweep",
        "built": dt.date.today().isoformat(),
        "what": ("12-sector India-investment news sweep (one subagent per the twin's core "
                "PLI-derived sectors), replacing the earlier NewsAPI-based sweeps that were "
                "proven unreliable at scale. Every finding here was verified by opening and "
                "reading the actual source article/press release, not a search snippet. "
                "new_to_twin flags companies not already in layer 16 leads or the company DB, "
                "via the same word-boundary fragment matcher used in layers 37/41."),
        "known_company_count": len(known),
        "total_findings": total_findings,
        "total_new_to_twin": total_new,
        "confidence_breakdown": conf_counts,
        "sectors": sectors,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# Sector-wise India investment news sweep — layer 42", "",
         f"*Generated {out['built']} by `scripts/build_layer42_sector_investment_news_sweep.py`. "
         f"{total_findings} verified findings across 12 sectors, checked against {len(known)} "
         f"known company names. **{total_new} new to the twin.** Confidence: "
         f"{conf_counts.get('HIGH', 0)} HIGH, {conf_counts.get('MEDIUM', 0)} MEDIUM, "
         f"{conf_counts.get('LOW', 0)} LOW.*", ""]
    for sector, r in sectors.items():
        L += [f"## {sector} ({r['new_to_twin']} new of {r['total_findings']})", ""]
        if r["findings"]:
            L += ["| Company | Country | Confidence | New? | Signal | Source |", "|---|---|---|---|---|---|"]
            for f in r["findings"]:
                sig = (f.get("signal") or "")[:140].replace("|", "/")
                L.append(f"| {f['company']} | {f.get('country_of_headquarters', '—')} | "
                        f"{f.get('confidence', '—')} | {'🆕' if f['new_to_twin'] else ''} | {sig}... | "
                        f"[link]({f.get('source_url', '')}) |")
        else:
            L.append("*(none found)*")
        if r["negative_notes"]:
            L += ["", f"<details><summary>{len(r['negative_notes'])} negative/ruled-out leads (click to expand)</summary>", ""]
            for n in r["negative_notes"]:
                L.append(f"- {n}" if isinstance(n, str) else f"- {json.dumps(n, ensure_ascii=False)}")
            L += ["", "</details>"]
        L.append("")
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"\nTOTAL findings: {total_findings} ({total_new} new to twin) -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
