#!/usr/bin/env python3
"""Regenerate docs/SCHEME_CATALOGUE.md from layers/13_flat_instrument_index.json.

Run after any catalog layer changes (or via `refresh_twin.py catalogue`).
The catalogue is a generated view -- edit the layer JSONs, never this file's output.
"""
import json, os, datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idx = json.load(open(os.path.join(ROOT, "layers/13_flat_instrument_index.json")))

by_entity = defaultdict(list)
for r in idx["instruments"]:
    by_entity[(r.get("tier", "?"), r.get("offering_entity", "?"))].append(r)


def status_flag(r):
    s = " ".join(str(r.get(k, "")) for k in ("status", "application_status", "what_companies_get")).lower()
    if "oversubscribed" in s:
        return "🔴 CLOSED-OVERSUBSCRIBED"
    if any(w in s for w in ("lapsed", "superseded", "discontinued")):
        return "⚫ lapsed/superseded"
    if "closed" in s:
        return "🔒 closed"
    if any(w in s for w in ("open", "live", "active", "in force", "operative")):
        return "🟢 open/active"
    return "▫ unspecified"


lines = [
    "# Scheme Catalogue",
    "",
    f"*Generated {datetime.date.today().isoformat()} from `layers/13_flat_instrument_index.json` "
    f"({idx['count']} instruments). Regenerate with `python3 scripts/build_catalogue.py` -- do not edit by hand.*",
    "",
]

for tier, title in (("central", "Central government"), ("state", "States & UTs")):
    entities = sorted(k for k in by_entity if k[0] == tier)
    n = sum(len(by_entity[k]) for k in entities)
    lines += [f"## {title} ({n} instruments)", ""]
    for key in entities:
        rows = by_entity[key]
        lines += [f"### {key[1]}", "", "| Instrument | Type | Status | What companies get |", "|---|---|---|---|"]
        for r in rows:
            name = (r.get("instrument") or "?").replace("|", "/")
            typ = (r.get("instrument_type") or "").replace("|", "/")
            what = (r.get("what_companies_get") or r.get("site_notes") or "").replace("|", "/")
            if len(what) > 220:
                what = what[:217] + "..."
            lines.append(f"| {name} | {typ} | {status_flag(r)} | {what} |")
        lines.append("")

out = os.path.join(ROOT, "docs/SCHEME_CATALOGUE.md")
open(out, "w").write("\n".join(lines))
print(f"catalogue: {idx['count']} instruments -> {out}")
