#!/usr/bin/env python3
"""Layer 25 — cross-repo linkages: land availability + currently-open incentives.

Joins the twin's own scheme monitor (layer 17) with industrial-land-availability
data produced by the sibling repo `india-trade-sector-policy-recommendations`
(IILB vacant-land aggregates), and records how the twin links to the wider repo
constellation. Output: layers/25_land_incentive_linkages.json.

Re-run any time; it reads layer 17 locally and the land data from GitHub raw
(so it stays current with the policy repo's dated pulls).
"""
import json
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "layers"
OWNER = "herrrickshaw"
POLICY_REPO = "india-trade-sector-policy-recommendations"
IILB_FILE = "data/iilb_industrial_land_2026-07-22.json"

# How the twin links to the wider repo constellation (data + insights flowing in).
RELATED_REPOS = [
    {"repo": POLICY_REPO, "provides": "Industrial land availability (IILB vacant "
     "developed-park land, 37 states) + pending-IEM demand match + supply/demand "
     "scenarios", "links_to_layer": "25 (this), 05 decade report card",
     "direction": "data-in"},
    {"repo": "agri-commodity-tracker", "provides": "FCI depot / storage "
     "footprint (478 depots, 5 zones) — physical agri-logistics infrastructure "
     "behind Food Processing & AIF incentives", "links_to_layer": "02 catalog "
     "(FPI), 17 scheme monitor (AIF)", "direction": "data-in"},
    {"repo": "india-trade-tracker", "provides": "DGFT EIDB chapter-wise "
     "export/import flows — reveals which incentivized sectors are import-heavy "
     "(substitution targets) vs export-strong", "links_to_layer": "16 target "
     "shortlist (China PN3 substitution), 06 investor map", "direction": "data-in"},
    {"repo": "focus-sector-investor-map", "provides": "Global company pools per "
     "incentivized sector", "links_to_layer": "06 investor map, 07 pairings",
     "direction": "sibling"},
    {"repo": "discom-debt-and-revenue-models", "provides": "State DISCOM "
     "financial health — power-cost/reliability context for siting decisions "
     "under RDSS", "links_to_layer": "17 scheme monitor (RDSS)", "direction": "data-in"},
    {"repo": "india-trade-data-analysis", "provides": "Descriptive trade "
     "baselines feeding sector prioritisation", "links_to_layer": "05, 06",
     "direction": "sibling"},
]

# State land-bank portals that hold UNDEVELOPED land beyond the central IILB
# (from reference: industrial-land-bank-access). Machine-readable availability.
STATE_LANDBANK_SOURCES = {
    "Odisha": "gis.investodisha.gov.in ArcGIS REST (open, per-parcel geometry)",
    "Uttar Pradesh": "eservices.onlineupsida.com PropertyHub (all plots + price)",
    "Andhra Pradesh": "kpi.apiic.in VacantPlots.jsp (zone→park→plot)",
    "Telangana": "tgiic.telangana.gov.in/PMVacantPlots",
    "Rajasthan": "riico.rajasthan.gov.in/undevelopedland.aspx",
    "Tamil Nadu": "sipcotweb.tn.gov.in (genuine site; sipcot.com/.in are parked)",
    "West Bengal": "silpasathi.wb.gov.in (login/PDF-gated)",
}


def fetch_iilb():
    url = f"https://raw.githubusercontent.com/{OWNER}/{POLICY_REPO}/HEAD/{IILB_FILE}"
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.load(r)
    sa = d["state_aggregates"]
    rows = sa if isinstance(sa, list) else list(sa.values())
    rows = [r for r in rows if r.get("available_area")]
    rows.sort(key=lambda x: -x["available_area"])
    return d.get("coverage"), d.get("note"), rows


def open_incentives():
    m = json.load(open(LAYERS / "17_scheme_monitor.json"))
    OPEN_WORDS = ("open", "operational", "ongoing", "rolling", "tranches",
                  "fcfs", "round-1")
    out = []
    for e in m["entries"]:
        w = (e["monitor"].get("window") or "").lower()
        # truly closed = oversubscribed/stopped/discontinued (a plain closing
        # DATE just means date-limited but still open now). Order matters.
        if any(k in w for k in ("oversubscribed", "stopped", "discontinued")):
            status = "CLOSED"
        elif any(k in w for k in OPEN_WORDS):
            status = "OPEN"
        elif "clos" in w:                       # a future closing date is named
            status = "CLOSING-SOON"
        else:
            status = "PENDING/OTHER"
        out.append({
            "scheme": e["scheme"], "ministry": e["ministry"],
            "tier": e.get("tier"), "status": status,
            "window": e["monitor"].get("window"),
            "funds_allocated": e["monitor"].get("funds_allocated"),
            "last_verified": e["monitor"].get("last_verified"),
        })
    return out


def build():
    coverage, note, land = fetch_iilb()
    top_land = [{"state": r["state"], "available_vacant_ha": r["available_area"],
                 "parks": r["parks"]} for r in land[:15]]
    incentives = open_incentives()
    open_now = [i for i in incentives if i["status"] in ("OPEN", "CLOSING-SOON")]

    # the join insight: land-rich states × sector-agnostic open central incentives
    land_rich = [r["state"].title() for r in land[:6]]
    layer = {
        "layer": 25,
        "title": "Land availability + currently-open incentives (cross-repo linkage)",
        "built": date.today().isoformat(),
        "purpose": "Give an investor the two operational facts the earlier "
                   "layers implied but never joined: WHERE developed industrial "
                   "land is actually vacant, and WHICH incentive windows are open "
                   "right now — plus the repos each fact is sourced from.",
        "related_repositories": RELATED_REPOS,
        "land_availability": {
            "source_repo": POLICY_REPO,
            "source_dataset": IILB_FILE,
            "coverage": coverage,
            "definition": note,
            "top_states_by_vacant_developed_land": top_land,
            "state_landbank_portals_for_undeveloped_land": STATE_LANDBANK_SOURCES,
            "caveat": "Central IILB counts VACANT developed-park land only; "
                      "states hold larger undeveloped banks (portals listed). "
                      "Per-parcel geometry only from Odisha ArcGIS.",
        },
        "open_incentives": {
            "as_of": date.today().isoformat(),
            "source_layer": "17_scheme_monitor.json (PIB daily + PRS refreshed)",
            "open_or_closing_count": len(open_now),
            "windows": incentives,
        },
        "linked_insight": {
            "statement": "A company eligible for a sector-agnostic open central "
                         "incentive (Semicon/ISM 2.0, ECMS, ELI, RDI, AIF) can "
                         "site in the land-rich states without a land constraint; "
                         "heavy-industry pipelines face the deficit flagged in "
                         f"{POLICY_REPO}'s supply/demand scenarios.",
            "land_rich_states": land_rich,
            "open_central_windows": [i["scheme"] for i in open_now
                                     if i["tier"] == "central"],
            "cross_ref": "See india-trade-sector-policy-recommendations "
                         "land_supply_demand_scenarios for the land-intensity "
                         "swing factor.",
        },
    }
    out = LAYERS / "25_land_incentive_linkages.json"
    out.write_text(json.dumps(layer, indent=1, ensure_ascii=False))
    print(f"layer 25 written: {len(top_land)} land states, "
          f"{len(open_now)} open/closing incentive windows -> {out}")


if __name__ == "__main__":
    build()
