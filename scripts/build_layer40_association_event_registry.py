#!/usr/bin/env python3
"""Layer 40 — association + trade-fair event registry, for ONGOING MONITORING.

Different purpose from layer 39 (a one-time textile-sector membership
snapshot): this is a durable SourceRoute-style registry (same convention as
layer 15's portal directory: URL + access method + liveness, not raw data)
that says WHERE to re-check for updated member/exhibitor lists, and WHEN
(next event edition), so a future refresh knows what to re-fetch rather than
starting research from zero. Two linked record types:

  - `associations`: one row per trade body -- sector, country scope, member
    directory URL + access method (public HTML / PDF / JS-search / paywalled
    / login-gated), member count, which events its members are known to
    exhibit at.
  - `events`: one row per trade fair -- sector, frequency, last known
    edition (with exhibitor-list URL if found), next edition if known,
    which associations' members were cross-validated as exhibitors.

The India-fair-exhibitor-list pattern (proven on India ITME 2022: 148
international exhibitors, directly cross-validating Swiss/German/Italian/
Japanese association membership) is the highest-value discovery type in
this registry -- an exhibitor list is a REVEALED PREFERENCE signal (a
company paid to be physically present in the Indian market), stronger than
a bare association-membership record.

Usage: python3 scripts/build_layer40_association_event_registry.py
Output: layers/40_association_event_registry.json + docs/ASSOCIATION_EVENT_REGISTRY.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "40_association_event_registry.json")
OUT_DOC = os.path.join(ROOT, "docs", "ASSOCIATION_EVENT_REGISTRY.md")

from layer40_data import ASSOCIATIONS, EVENTS  # noqa: E402  (tables live in scripts/layer40_data/)


def main():
    layer = {
        "layer": 40, "name": "association_event_registry", "built": dt.date.today().isoformat(),
        "what": ("Durable monitoring registry (SourceRoute-style, matching layer 15's portal "
                "directory convention) of trade associations and their linked events -- WHERE to "
                "re-check for updated member/exhibitor lists and WHEN, not a full data snapshot "
                "itself (layer 39 holds the actual Textiles membership data this registry points "
                "to; other sectors' full company lists live in each research pass's own scratch "
                "files, referenced here by URL/count/sample rather than re-embedded in full)."),
        "associations": ASSOCIATIONS, "events": EVENTS,
        "coverage_note": ("Extended 2026-08-22 across all twin focus sectors: Electronics & "
                          "Semiconductors, White Goods & Electricals, Auto/EV & Components, Pharma "
                          "& Bulk Drugs, Medical Devices, Green Energy & Fuels, Chemicals & "
                          "Plastics, Aerospace & Defence, Specialty Steel & Metals, Shipbuilding & "
                          "Marine, Food Processing -- plus Mining and Oil & Gas (not yet formal "
                          "twin focus sectors, added per explicit request). "
                          f"{len(ASSOCIATIONS)} associations, {len(EVENTS)} events tracked. "
                          "Highest-value pattern confirmed repeatedly: an India-domestic trade "
                          "fair's exhibitor list is a stronger signal than bare association "
                          "membership (revealed preference -- paid to physically exhibit in India) "
                          "-- India ITME, SEMICON India, ELECRAMA, Medical Fair India, ChemTECH "
                          "World Expo, Auto Expo Components, Aero India, AAHAR, and IMME all "
                          "produced real country-tagged rosters this pass."),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)

    L = ["# Association + event registry — for ongoing monitoring", "",
         f"*Generated {layer['built']} by `scripts/build_layer40_association_event_registry.py`. "
         "Durable registry (URL + access method + recheck cadence), not a data snapshot -- see "
         "`docs/TEXTILE_ASSOCIATIONS.md` (layer 39) for the actual textile membership data this "
         "registry points to.*", "",
         "## Associations", "",
         "| Association | Sector | Scope | Members | Access | Linked events | Recheck |",
         "|---|---|---|---|---|---|---|"]
    for a in ASSOCIATIONS:
        L.append(f"| {a['name']} | {a['sector']} | {a['scope']} | {a['member_count'] or '—'} | "
                 f"{a['access_method'][:60]} | {', '.join(a['linked_events']) or '—'} | "
                 f"{a['recheck_recommended']} |")
    L += ["", "## Events", "", "| Event | Sector | Frequency | Last edition | Next edition | Value |",
          "|---|---|---|---|---|---|"]
    for e in EVENTS:
        last = f"{e['last_edition'].get('year')} ({e['last_edition'].get('location', '?')})" if e.get("last_edition") else "—"
        nxt = f"{e['next_edition'].get('year')} {e['next_edition'].get('dates', '')}" if e.get("next_edition") else "TBD"
        L.append(f"| {e['name']} | {e['sector']} | {e.get('frequency', '—')} | {last} | {nxt} | {e['value'][:70]} |")
    L += ["", "## Coverage note", "", layer["coverage_note"], ""]
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"associations: {len(ASSOCIATIONS)} | events: {len(EVENTS)} -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
