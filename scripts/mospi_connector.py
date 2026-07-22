#!/usr/bin/env python3
"""MoSPI connector — the official India statistics data sources.

Ministry of Statistics & Programme Implementation (MoSPI) publishes India's
authoritative macro and survey statistics through the eSankhyiki portal and the
`api.mospi.gov.in` API. This connector enumerates the 25 datasets available via
MoSPI, tags each for investment relevance, links it to the twin layer it informs,
and documents how to pull the actual data (official API + the 4-step workflow).

It is the macro-economic backdrop the incentive/land/project layers lacked:
inflation (CPI/WPI), growth (NAS/GDP), industry (IIP/ASI), jobs (PLFS),
external sector (RBI), renewable capacity (MNRE), establishments (EC).

Access routes to the data itself:
  1. Official API — base https://api.mospi.gov.in/api/esankhyiki/ ; per-dataset
     endpoints (e.g. /api/nas/..., /api/plfs/...) with dataset-specific params.
     Portal + viz: https://esankhyiki.mospi.gov.in/viz/<dataset>. Swagger:
     https://esankhyiki.mospi.gov.in/EC/swagger-ui/index.html .
  2. MoSPI MCP connector (session tool) — the clean interface: list_datasets ->
     get_indicators(dataset) -> get_metadata(dataset, indicator) ->
     get_data(dataset, filters). Filter codes are arbitrary and per-dataset;
     they must come from get_metadata, never guessed.

🔴 Known quirks (verified 2026-07): RBI forex series lags ~13 months (prefer
rbi.org.in WSSView scrape); WPI/IIP prints with large jumps need cross-check;
NAS getNasIndicatorList intermittently 500s (falls back to bundled definitions).

Output: layers/29_mospi_data_sources.json (run build_layer29 to regenerate).
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "layers"

API_BASE = "https://api.mospi.gov.in/api/esankhyiki/"
PORTAL = "https://esankhyiki.mospi.gov.in"

# relevance: core = direct investment signal; sector = maps to a twin sector;
# context = social/structural backdrop.
CATALOG = [
    ("NAS", "National Accounts Statistics", "GDP, GVA, growth, savings, capital "
     "formation, trade — 22 annual + 11 quarterly macro aggregates", "core",
     "Decade report card (L05) macro backdrop; GDP growth frames the pipeline"),
    ("CPI", "Consumer Price Index", "Retail inflation, 600+ items, base 2024; "
     "state + all-India", "core", "Cost-of-living context for siting; food/fuel "
     "inflation feeds AIF/FPI relevance"),
    ("WPI", "Wholesale Price Index", "Producer/wholesale inflation, 1000+ items, "
     "5 levels", "core", "Input-cost signal for manufacturing sectors (L26)"),
    ("IIP", "Index of Industrial Production", "Industrial output — manufacturing, "
     "mining, electricity; use-based classes", "core", "Electronic Mfg & "
     "manufacturing sector momentum (L26); pairs with ASI"),
    ("PLFS", "Periodic Labour Force Survey", "Jobs, unemployment, wages, LFPR/WPR; "
     "annual/quarterly/monthly", "core", "Labour-codes watchlist (L28); talent/"
     "wage context for siting"),
    ("RBI", "RBI Statistics", "Foreign trade by country/commodity, BoP, forex "
     "reserves, exchange rates (155 currencies), external debt", "core",
     "External-sector context; complements india-trade-tracker EIDB flows"),
    ("ASI", "Annual Survey of Industries", "Factory-sector financials — capital, "
     "wages, GVA, fuel, profitability by NIC", "sector", "Factory economics "
     "behind manufacturing incentives (L17/26)"),
    ("MNRE", "Renewable Energy (MNRE)", "State-wise monthly installed RE capacity "
     "(MW): solar/wind/hydro/bio, rooftop, KUSUM", "sector", "NGHM SIGHT & RE "
     "incentives (L17/25); Electricity Generation pipeline (L26)"),
    ("ENERGY", "Energy Statistics", "Energy balance — supply/consumption by "
     "commodity & sector (KToE/PJ)", "sector", "Energy-cost & fuel-mix context "
     "for Oil&Gas/Power sectors (L26)"),
    ("EC", "Economic Census", "District-wise establishment & worker counts (EC4-6)",
     "sector", "Where enterprises already cluster — siting demand signal"),
    ("ASUSE", "Annual Survey of Unincorporated Enterprises", "Informal/MSME "
     "sector — counts, GVA, digital adoption, registration", "sector",
     "MSME base behind ease-of-business reforms (L28)"),
    ("HCES", "Household Consumption Expenditure Survey", "MPCE, food/non-food, "
     "Gini inequality across 12 fractiles", "context", "Demand-side consumption "
     "context (Consumer Goods/Retail sectors)"),
    ("AISHE", "All India Survey on Higher Education", "Universities, colleges, "
     "enrolment, GER, PTR", "context", "Talent-pool depth for tech/GCC entrants"),
    ("UDISE", "UDISE+ (School Education)", "46 indicators — schools, enrolment, "
     "dropout, teachers, infrastructure", "context", "Education-sector NIP "
     "projects (L26); human-capital base"),
    ("NFHS", "National Family Health Survey", "Health & demographics — fertility, "
     "mortality, nutrition, NCDs", "context", "Healthcare-sector demand (L26 "
     "1,153 opportunities)"),
    ("GENDER", "Gender Statistics", "147 indicators — health, education, labour, "
     "leadership, crime", "context", "Workforce-diversity & ESG context"),
    ("ENVSTATS", "Environment Statistics", "124 indicators — climate, water, "
     "forests, pollution, waste, disasters", "context", "ESG/climate-risk "
     "screening for siting"),
    ("CPIALRL", "CPI Agricultural/Rural Labourers", "Rural inflation for AL/RL "
     "worker categories", "context", "Rural cost-of-living (agri sectors)"),
    ("TUS", "Time Use Survey", "Time allocation — paid/unpaid/care work by group",
     "context", "Care-economy & informal-labour context"),
    ("NSS77", "NSS 77th — Land, Livestock & AIDIS", "Agri households, land "
     "ownership, farm income, household debt/assets", "sector", "Agri-sector & "
     "rural-asset base (FPI/AIF)"),
    ("NSS78", "NSS 78th — Living Conditions", "Water, sanitation, digital "
     "connectivity, migration, assets", "context", "Infrastructure-gap context"),
    ("NSS79", "NSS 79th — CAMS + AYUSH", "Education, health expenditure, digital "
     "literacy, financial inclusion", "context", "Digital-readiness & health-"
     "spend context"),
    ("NSS75E", "NSS 75th — Education", "Literacy, attainment, GAR/NAR, education "
     "expenditure", "context", "Human-capital detail"),
    ("NSS76", "NSS 76th — Disability + Housing/Water", "Disability prevalence; "
     "drinking water, housing quality, sanitation", "context", "Social-"
     "infrastructure base"),
    ("NSS80", "NSS 80th — Telecom + Education", "Mobile/internet usage, digital "
     "literacy, e-commerce, school expenditure", "context", "Digital-economy "
     "adoption (Telecom/IT sectors)"),
]

# Real indicator structure for flagship datasets (pulled from the MoSPI API).
FLAGSHIP_INDICATORS = {
    "NAS": ["Gross Value Added", "Gross Domestic Product", "GDP Growth Rate",
            "GVA Growth Rate", "Gross Fixed Capital Formation",
            "Private Final Consumption Expenditure", "Gross National Income",
            "Gross Saving", "Export of Goods and Services",
            "Import of Goods and Services"],
    "PLFS": ["LFPR — Labour Force Participation Rate", "WPR — Worker Population "
             "Ratio", "UR — Unemployment Rate", "Avg regular wage/salary earnings",
             "Avg casual-labour daily earnings", "Avg self-employment earnings"],
    "MNRE": ["Solar Power (MW)", "Wind Power (MW)", "Hydro Power (MW)",
             "Bio Power (MW)", "Total Renewable Power (MW)"],
}


def build_layer():
    rows = []
    for code, name, desc, rel, link in CATALOG:
        rows.append({
            "dataset": code, "name": name, "coverage": desc,
            "relevance": rel, "twin_link": link,
            "viz_url": f"{PORTAL}/viz/{code.lower()}",
            "flagship_indicators": FLAGSHIP_INDICATORS.get(code),
        })
    by_rel = {r: sum(1 for x in rows if x["relevance"] == r)
              for r in ("core", "sector", "context")}
    layer = {
        "layer": 29,
        "title": "MoSPI macro-statistics data sources (connector)",
        "built": date.today().isoformat(),
        "purpose": "The official India macro/statistics backdrop the twin lacked "
                   "— 25 MoSPI datasets, each tagged for investment relevance and "
                   "linked to the twin layer it informs.",
        "source": {
            "authority": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "portal": PORTAL, "api_base": API_BASE,
            "swagger": f"{PORTAL}/EC/swagger-ui/index.html",
            "access_routes": [
                "Official API: api.mospi.gov.in/api/<dataset>/... with "
                "dataset-specific params (see swagger); viz at /viz/<dataset>.",
                "MoSPI MCP connector (session tool): list_datasets -> "
                "get_indicators -> get_metadata -> get_data. Filter codes are "
                "arbitrary and per-dataset; take them from get_metadata.",
            ],
            "quirks": [
                "RBI forex series lags ~13 months — prefer rbi.org.in WSSView "
                "scrape for current reserves.",
                "WPI/IIP prints with large jumps need cross-check vs press release.",
                "NAS getNasIndicatorList intermittently 500s (bundled fallback).",
            ],
        },
        "counts": {"datasets": len(rows), **{f"{k}_relevance": v
                                             for k, v in by_rel.items()}},
        "data_sources": rows,
        "linkage": {
            "macro_backdrop": "NAS/CPI/WPI/IIP/PLFS/RBI give the growth, "
                              "inflation, industry, jobs and external-sector "
                              "context that frames every incentive/land/project "
                              "decision in layers 05/17/25/26.",
            "sector_specific": "ASI, MNRE, ENERGY, EC, ASUSE map to specific twin "
                               "sectors (factory economics, renewable capacity, "
                               "establishment clusters, MSME base).",
            "cross_repo": "RBI trade series complements india-trade-tracker EIDB "
                          "flows; CPI/WPI complement agri-commodity-tracker.",
        },
    }
    out = LAYERS / "29_mospi_data_sources.json"
    out.write_text(json.dumps(layer, indent=1, ensure_ascii=False))
    print(f"layer 29: {len(rows)} MoSPI data sources "
          f"({by_rel['core']} core / {by_rel['sector']} sector / "
          f"{by_rel['context']} context) -> {out}")
    return layer


if __name__ == "__main__":
    build_layer()
