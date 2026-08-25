#!/usr/bin/env python3
"""Layer 44 — 5-year state-MoU sweep (2021-2026).

Distinct from layer 42 (revealed events, ~18-month window, actually-verified
investment/JV/plant actions) and layer 16's state_landings (policy-eligible,
scheme-design only). This layer sits at the "MoU signed" stage — a specific,
dated, individually-named-company agreement with a state government at an
investor summit or roadshow. India's state investor summits are notorious
for headline MoU totals that don't convert to real investment (the
"MoU graveyard" phenomenon, documented per-state in each file's
negative_notes) -- so every record here carries a `follow_through_status`,
verified separately from the MoU signing itself, wherever findable.

12 parallel subagents covered 12 states/state-pairs' major investor summits
over 2021-2026: Gujarat, Uttar Pradesh, Tamil Nadu, Maharashtra, Karnataka,
Odisha, Rajasthan, Madhya Pradesh, West Bengal, Andhra Pradesh + Telangana,
Punjab + Haryana. Every entry required an actually-opened, actually-read
source naming the specific company -- summit-total press figures were never
used as data points. Non-foreign (India-headquartered) companies were
excluded even when large/prominent in press coverage.

Usage: python3 scripts/build_layer44_state_mou_5yr_sweep.py
Output: layers/44_state_mou_5yr_sweep.json + docs/STATE_MOU_5YR_SWEEP.md
"""
import datetime as dt
import importlib.util
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_DIR = os.path.join(ROOT, "data", "news_sweeps", "state_mou_5yr_2026_08")
OUT_JSON = os.path.join(ROOT, "layers", "44_state_mou_5yr_sweep.json")
OUT_DOC = os.path.join(ROOT, "docs", "STATE_MOU_5YR_SWEEP.md")

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments


def known_names():
    import sqlite3
    names = set()
    leads_path = os.path.join(ROOT, "layers", "16_leads.json")
    if os.path.exists(leads_path):
        for l in json.load(open(leads_path))["leads"]:
            names.add(l["company"].strip().lower())
    db = os.path.join(ROOT, "data", "companies.db")
    if os.path.exists(db):
        con = sqlite3.connect(db)
        for (n,) in con.execute("SELECT name FROM companies"):
            if n:
                names.add(n.strip().lower())
        con.close()
    return names


_STATUS_CANON = ["operational", "under construction", "publicly stalled/withdrawn", "no follow-up news found"]


def canon_status(raw):
    """Several agents appended explanatory detail directly onto the enum value
    instead of using a separate field (e.g. 'operational -- plant inaugurated
    ...'). Bucket by known-prefix match so aggregation stays clean; the raw,
    full-detail string is preserved untouched in each record's own field."""
    raw = (raw or "").strip().lower()
    for c in _STATUS_CANON:
        if raw.startswith(c):
            return c
    return "no follow-up news found"


def is_new(name, known):
    n = norm(name)
    if not n:
        return False
    frags = match_fragments(n)
    strong = [f for f, q in frags if q == "strong"]
    if not strong:
        return False
    for kn in known:
        knn = norm(kn)
        if any(re.search(rf"\b{re.escape(f)}\b", knn) for f in strong):
            return False
    return True


def load_all():
    """Normalize every file's mous to a flat list, each tagged with its state."""
    rows = []
    files_meta = []
    for fname in sorted(os.listdir(SWEEP_DIR)):
        if not fname.endswith(".json"):
            continue
        d = json.load(open(os.path.join(SWEEP_DIR, fname)))
        default_state = d.get("state")
        for m in d.get("mous", []):
            m = dict(m)
            m["state"] = m.get("state") or default_state
            m["source_file"] = fname
            rows.append(m)
        files_meta.append({"file": fname, "states": d.get("states") or [d.get("state")],
                           "summits_covered": d.get("summits_covered", []),
                           "method": d.get("method"), "negative_notes": d.get("negative_notes", [])})
    return rows, files_meta


def main():
    known = known_names()
    rows, files_meta = load_all()
    print(f"known company names loaded: {len(known)}")
    print(f"total MoU records: {len(rows)}")

    for r in rows:
        r["new_to_twin"] = is_new(r["company"], known)

    conf_counts = defaultdict(int)
    follow_counts = defaultdict(int)
    state_counts = defaultdict(lambda: {"mous": [], "conf": defaultdict(int), "follow": defaultdict(int)})
    for r in rows:
        conf_counts[r.get("confidence", "MEDIUM")] += 1
        follow_counts[canon_status(r.get("follow_through_status"))] += 1
        st = r.get("state") or "Unknown"
        state_counts[st]["mous"].append(r)
        state_counts[st]["conf"][r.get("confidence", "MEDIUM")] += 1
        state_counts[st]["follow"][canon_status(r.get("follow_through_status"))] += 1

    new_count = sum(1 for r in rows if r["new_to_twin"])

    by_state = {}
    for st, d in sorted(state_counts.items(), key=lambda kv: -len(kv[1]["mous"])):
        by_state[st] = {
            "mou_count": len(d["mous"]),
            "new_to_twin": sum(1 for m in d["mous"] if m["new_to_twin"]),
            "confidence_breakdown": dict(d["conf"]),
            "follow_through_breakdown": dict(d["follow"]),
            "mous": d["mous"],
        }

    out = {
        "layer": 44, "name": "state_mou_5yr_sweep",
        "built": dt.date.today().isoformat(),
        "what": ("5-year (2021-2026) state investor-summit MoU sweep, 12 states/state-pairs via "
                "parallel subagents. Distinct from layer 42 (revealed, verified investment EVENTS) "
                "and layer 16 (policy-eligible scheme data) -- this is the intermediate 'MoU signed' "
                "stage, with follow_through_status tracked per record since Indian state MoUs are "
                "well-documented to frequently not convert to real investment."),
        "known_company_count": len(known),
        "total_mous": len(rows),
        "total_new_to_twin": new_count,
        "confidence_breakdown": dict(conf_counts),
        "follow_through_breakdown": dict(follow_counts),
        "by_state": by_state,
        "sweep_files_meta": files_meta,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    graveyard_pct = round(100 * follow_counts.get("no follow-up news found", 0) / max(len(rows), 1))
    L = ["# 5-year state MoU sweep (2021-2026) — layer 44", "",
         f"*Generated {out['built']} by `scripts/build_layer44_state_mou_5yr_sweep.py`. "
         f"{len(rows)} verified foreign-company MoUs across {len(by_state)} states, checked against "
         f"{len(known)} known company names. **{new_count} new to the twin.** "
         f"Confidence: {conf_counts.get('HIGH',0)} HIGH, {conf_counts.get('MEDIUM',0)} MEDIUM, "
         f"{conf_counts.get('LOW',0)} LOW. "
         f"**{graveyard_pct}% of all MoUs have no follow-up news found** since signing — the "
         "quantified 'MoU graveyard' rate across this sweep.*", "",
         "## Methodology", "",
         "Every record required an actually-opened, actually-read source naming the specific "
         "company — summit-total press figures (often in lakh crores, covering hundreds/thousands "
         "of MoUs) were never used as data points, only individually verified companies. "
         "India-headquartered companies were excluded even when large/prominent in the same press "
         "coverage. `follow_through_status` is tracked separately from the MoU signing itself: "
         "`operational` / `under construction` (real progress confirmed), `publicly stalled/withdrawn`, "
         "or `no follow-up news found` (the honest default for most MoUs — absence of coverage, not "
         "evidence of failure, but also not evidence of success).", ""]

    L += ["## Follow-through breakdown (all states)", "",
         "| Status | Count | % |", "|---|---|---|"]
    for status, cnt in sorted(follow_counts.items(), key=lambda kv: -kv[1]):
        L.append(f"| {status} | {cnt} | {round(100*cnt/len(rows))}% |")
    L.append("")

    L += ["## By state", "", "| State | MoUs | New to twin | HIGH conf | Operational/Under construction | No follow-up |",
         "|---|---|---|---|---|---|"]
    for st, d in by_state.items():
        op = d["follow_through_breakdown"].get("operational", 0) + d["follow_through_breakdown"].get("under construction", 0)
        nf = d["follow_through_breakdown"].get("no follow-up news found", 0)
        L.append(f"| {st} | {d['mou_count']} | {d['new_to_twin']} | {d['confidence_breakdown'].get('HIGH',0)} | {op} | {nf} |")
    L.append("")

    for st, d in by_state.items():
        L += [f"## {st} ({d['mou_count']} MoUs)", "",
             "| Company | Country | Sector | Investment | MoU date | Status | Confidence |",
             "|---|---|---|---|---|---|---|"]
        for m in sorted(d["mous"], key=lambda r: r.get("mou_date") or ""):
            sig = (m.get("sector") or "")[:60].replace("|", "/")
            inv = (m.get("proposed_investment") or "")[:60].replace("|", "/")
            new = " 🆕" if m["new_to_twin"] else ""
            L.append(f"| {m['company']}{new} | {m.get('country_of_headquarters','—')} | {sig} | {inv} | "
                     f"{m.get('mou_date','—')} | {m.get('follow_through_status','—')} | {m.get('confidence','—')} |")
        L.append("")

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"\n{len(rows)} MoUs ({new_count} new), {graveyard_pct}% no-follow-up -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
