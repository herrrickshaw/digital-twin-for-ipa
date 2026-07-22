#!/usr/bin/env python3
"""Layer 26 — investment-project pipeline: IIG / NIP + PM Gati Shakti.

Links the twin's incentive catalogue to the actual government-listed project
pipeline an investor can plug into, sourced from the **India Investment Grid**
(indiaindustriallandbank's sibling portal, DPIIT/Invest India) — the public
window onto the **National Infrastructure Pipeline (NIP)**, which is the same
project set PM Gati Shakti coordinates.

Data:
 - Sector-wise NIP opportunity counts across 42 IIG sectors (12,385 projects) —
   scraped once from IIG's d3 India-Overview chart (see SECTOR_SEED); the sector
   `id` is IIG's own filter key for deeper per-sector pulls.
 - Flagship projects pulled LIVE from IIG's rawData endpoint (curl-able HTML
   fragment, parsed here) — project id, name, USD value.
 - Mapping from IIG sectors to the twin's incentivized-sector lanes.

Gati Shakti note: pmgatishakti.gov.in / the GIS master-plan portal are
login-gated (state/ministry SSO) and return 404/timeout to anonymous clients,
so NIP-via-IIG is the machine-readable public surface for the same pipeline.

Output: layers/26_project_pipeline.json.  Re-run any time.
"""
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "layers"
SEED = ROOT / "layers" / "26_iig_sector_seed.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "Referer": "https://www.indiainvestmentgrid.gov.in/opportunities/nip-projects"}
RAWDATA = ("https://www.indiainvestmentgrid.gov.in/opportunities/"
           "nip-projects?rawData=true&page=0")

# IIG sector -> twin incentive lane (which central instrument(s) it maps to)
SECTOR_TO_INCENTIVE = {
    "Electronic Manufacturing": "Semicon/ISM 2.0, ECMS, IT Hardware PLI",
    "Roads & Highways": "PM Gati Shakti / NIP (MoRTH); Bharatmala",
    "Railways": "PM Gati Shakti / NIP (Railways); Dedicated Freight Corridors",
    "Food Processing & Agriculture": "PLI-FPI, Agriculture Infrastructure Fund",
    "Food Processing": "PLI-FPI, AIF",
    "Electricity Generation": "NGHM SIGHT, RE bids (SECI)",
    "Transmission & Distribution": "RDSS",
    "Energy Storage": "PLI-ACC batteries",
    "Textiles": "PLI-Textiles, PM MITRA parks",
    "Textiles & Apparel": "PLI-Textiles, PM MITRA parks",
    "Pharma, Biotech & Lifesciences": "PLI-Pharma, Bulk Drug Parks",
    "Steel": "PLI-Specialty Steel",
    "Automotive": "PLI-Auto & Auto Components, PM E-DRIVE",
    "Shipping": "Shipbuilding package (SBFAS 2.0)",
    "Logistics Infrastructure": "PM Gati Shakti National Logistics Policy",
    "Waste & Water": "Jal Jeevan Mission, AMRUT (MoHUA/Jal Shakti)",
    "Coal": "Coal gasification incentives",
    "Oil & Gas": "MoPNG city-gas / refinery incentives",
    "Telecommunication": "BharatNet, PLI-Telecom",
    "Defence": "Defence corridors, iDEX",
}


def fetch_flagship_projects():
    req = urllib.request.Request(RAWDATA, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    projects, seen = [], set()
    for m in re.finditer(
            r'href="/opportunities/nip-project/(\d+)"(.*?)'
            r'(?=href="/opportunities/nip-project/|\Z)', html, re.DOTALL):
        pid, block = m.group(1), m.group(2)
        if pid in seen:
            continue
        name = re.search(r'card-main-project-title[^>]*title="([^"]+)"', block)
        # value span carries its own unit ("bn" | "mn") — normalise to USD bn
        vu = re.search(r'data-counter-value="([\d.]+)"[^>]*>[\d.]+</span>\s*'
                       r'<span>\s*(bn|mn|cr)\s*</span>', block, re.IGNORECASE)
        if not name:
            continue
        seen.add(pid)
        usd_bn = None
        if vu:
            v, unit = float(vu.group(1)), vu.group(2).lower()
            usd_bn = round(v if unit == "bn" else v / 1000, 4)  # mn -> bn
        projects.append({
            "project_id": pid,
            "name": name.group(1).strip(),
            "value_usd_bn": usd_bn,
            "url": f"https://www.indiainvestmentgrid.gov.in/opportunities/"
                   f"nip-project/{pid}",
        })
    return projects


def build():
    sectors = json.loads(SEED.read_text())
    for s in sectors:
        s["opportunities"] = int(s.pop("value"))
        s["iig_filter_id"] = s.pop("id")
        s["twin_incentive_lane"] = SECTOR_TO_INCENTIVE.get(s["name"].strip())
    sectors.sort(key=lambda x: -x["opportunities"])
    total = sum(s["opportunities"] for s in sectors)
    flagship = fetch_flagship_projects()

    layer = {
        "layer": 26,
        "title": "Investment-project pipeline — IIG / NIP + PM Gati Shakti",
        "built": date.today().isoformat(),
        "purpose": "Link the twin's incentive catalogue to the actual "
                   "government-listed project pipeline investors can enter, "
                   "from the India Investment Grid (public window onto the "
                   "National Infrastructure Pipeline / PM Gati Shakti).",
        "source": {
            "portal": "India Investment Grid (indiaindustriallandbank sibling; "
                      "DPIIT / Invest India, run by TCS)",
            "url": "https://www.indiainvestmentgrid.gov.in",
            "pipeline": "National Infrastructure Pipeline (NIP) — the project "
                        "set PM Gati Shakti coordinates",
            "access": {
                "sector_aggregates": "d3 chart on /analytics/india-overview "
                    "(scraped to 26_iig_sector_seed.json; sector id = IIG "
                    "filter key)",
                "flagship_projects": "GET /opportunities/nip-projects?"
                    "rawData=true&page=N (HTML fragment, parsed live)",
                "gati_shakti_portal": "pmgatishakti.gov.in / GIS master plan = "
                    "login-gated (state/ministry SSO), 404/timeout to anon — "
                    "IIG is the public surface for the same pipeline",
            },
        },
        "pipeline_totals": {
            "sectors": len(sectors),
            "total_nip_opportunities": total,
            "headline_sector_values_usd_bn": {
                "Roads & Highways": 314.21, "Waste & Water": 76.36,
                "Healthcare": 33.0},
        },
        "sectors": sectors,
        "flagship_projects": flagship,
        "linkage": {
            "to_layer_25": "Projects need land (layer 25 IILB vacant land) and "
                           "open incentives (layer 25 scheme monitor) — together "
                           "layers 25+26 give WHERE + WHAT-INCENTIVE + WHICH-"
                           "PROJECT for a siting decision.",
            "to_layer_02_17": "twin_incentive_lane maps each IIG sector to the "
                              "central instrument(s) that fund projects in it.",
            "cross_repo": "IIG's own footer links the Industrial Information "
                          "System (= IILB land bank used in layer 25) and the "
                          "Project Monitoring Group — land, projects and "
                          "incentives are one system.",
        },
    }
    out = LAYERS / "26_project_pipeline.json"
    out.write_text(json.dumps(layer, indent=1, ensure_ascii=False))
    print(f"layer 26: {len(sectors)} sectors / {total:,} NIP opportunities, "
          f"{len(flagship)} flagship projects -> {out}")


if __name__ == "__main__":
    build()
