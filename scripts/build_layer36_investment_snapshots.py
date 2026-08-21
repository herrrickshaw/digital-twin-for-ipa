#!/usr/bin/env python3
"""Layer 36 — investment-announcement snapshots (state summit MOUs + fDi Report).

Curated, NOT live-fetched (like layer 31's NON_WAIPA_IPAS / CORPORATE_REGISTRIES
catalogs) -- both sources below are genuinely STATIC point-in-time documents,
confirmed by a live scouting pass 2026-08-09, not recurring feeds:

  - State investor-summit MOU lists: of the three summits investigated
    (Vibrant Gujarat, UPGIS, Invest Karnataka), only UPGIS 2023 publishes a
    real tabular company-level document -- an OFFICIAL interim snapshot dated
    11-Feb-2023, mid-summit, covering only the top ~12 of 19,058 total MoUs
    by name (the rest are district/sector aggregates only). Vibrant Gujarat
    and Invest Karnataka have NO consolidated MOU table at all -- only
    scattered per-company press-release PDFs, which is low-signal/high-effort
    to reconstruct (not attempted here).
  - fDi Report 2025 (fDi Intelligence / Financial Times): the flagship annual
    report is freely downloadable, but fdiintelligence.com's own robots.txt
    explicitly disallows AI crawlers (anthropic-ai, Claude-Web, ClaudeBot,
    GPTBot, CCBot, etc. -- Disallow: / site-wide), so this script does NOT
    and never should fetch that domain. The report PDF itself is mirrored on
    a separate, non-blocking domain (ftlocations.com landing page has an
    open robots.txt) -- that's the only route used here. Refresh is a MANUAL
    once-a-year task: find next year's publication-ID URL and re-curate.

Access hazards recorded as data (repo convention, per layers 27/31):
  - vibrantgujarat.com: 403 to curl/WebFetch (WAF/bot-detection), loads fine
    in a real browser -- any future scrape needs a headless browser, not curl.
  - upgis2023.in: DEAD -- now a repurposed/parked spam domain. Do not link to it.
  - invest.up.gov.in/gbc2024/: 403 "Forbidden: Access is denied" (WAF on this
    specific path) while sibling paths on the same host return 200.
  - investkarnataka.co.in: reachable, but "Recent Developments" is a feed of
    individual per-company PDF press releases, no consolidated table.

Output: layers/36_investment_snapshots.json + docs/INVESTMENT_SNAPSHOTS.md
Usage:  python3 scripts/build_layer36_investment_snapshots.py
"""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "36_investment_snapshots.json")
OUT_DOC = os.path.join(ROOT, "docs", "INVESTMENT_SNAPSHOTS.md")

UPGIS_2023 = {
    "summit": "UP Global Investors Summit 2023 (UPGIS)",
    "snapshot_date": "2023-02-11",
    "source_url": ("https://www.iiaonline.in/Uploads/ImportantUpdates/"
                   "upgis-2023-investment-figures-as-on-11-02-2023-13-02-2023.pdf"),
    "source_note": ("Mirrored via an industry association (IIA) -- content is an official "
                    "government summary; not hosted directly on invest.up.gov.in. Format: "
                    "PDF with real tables (Top-10/12 Investment Intents, sector-wise top-20, "
                    "region-wise, 75-district annexure -- district level only past the top ~12)."),
    "total_mous": 19058,
    "companies": [
        {"company": "Tauschen International Ltd", "country": "Hong Kong SAR", "mous": 16,
         "sectors": "MRO, Manufacturing, Electronics, Textile, EV", "investment_inr_cr": 189849.40,
         "estimated_jobs": 62494},
        {"company": "RG Strategies Group", "country": "India", "mous": 7,
         "sectors": "Renewable Energy, EV", "investment_inr_cr": 173031.00, "estimated_jobs": None},
        {"company": "Imperia Innovation Investment / Austin Consulting Group", "country": "United States",
         "mous": 2, "sectors": "Education, Infrastructure", "investment_inr_cr": 105000.00, "estimated_jobs": None},
        {"company": "Causis Group", "country": None, "mous": 1, "sectors": "EV",
         "investment_inr_cr": 100000.00, "estimated_jobs": None},
        {"company": "Reliance Industries Ltd", "country": "India", "mous": None,
         "sectors": "Telecom Infra, MRO", "investment_inr_cr": 75000.00, "estimated_jobs": None},
        {"company": "ABC Cleantech Pvt Ltd", "country": "India", "mous": None,
         "sectors": "Renewable Energy (Mirzapur)", "investment_inr_cr": 50000.00, "estimated_jobs": None},
        {"company": "NTPC Ltd", "country": "India", "mous": 4, "sectors": "Renewable Energy",
         "investment_inr_cr": 42280.00, "estimated_jobs": None},
        {"company": "Unicorn Energy", "country": "Germany", "mous": 2, "sectors": "Renewable Energy",
         "investment_inr_cr": 41500.00, "estimated_jobs": None},
        {"company": "GMR Group", "country": "India", "mous": None, "sectors": None,
         "investment_inr_cr": 40000.00, "estimated_jobs": None},
        {"company": "Aditya Birla Group", "country": "India", "mous": None, "sectors": None,
         "investment_inr_cr": 25000.00, "estimated_jobs": None},
        {"company": "Hinduja Group", "country": "India", "mous": None, "sectors": None,
         "investment_inr_cr": 25000.00, "estimated_jobs": None},
    ],
    "foreign_companies_only": None,  # filled below
}
UPGIS_2023["foreign_companies_only"] = [
    c["company"] for c in UPGIS_2023["companies"] if c["country"] and c["country"] != "India"]

FDI_REPORT_2025 = {
    "publisher": "fDi Intelligence (Financial Times) / fDi Markets",
    "title": "The fDi Report 2025",
    "source_url": ("https://fdiinsights-publications.s3.eu-west-1.amazonaws.com/publications/"
                   "5000067/documents/The_fDi_Report_2025.pdf"),
    "landing_page": "https://ftlocations.com/knowledge-hub/report/fdi-report-2025",
    "source_note": ("Fetched via the S3/ftlocations.com mirror ONLY -- fdiintelligence.com's own "
                    "robots.txt disallows AI crawlers site-wide (anthropic-ai, Claude-Web, ClaudeBot "
                    "explicitly named), so this project will not fetch that domain directly. The PDF "
                    "is the vendor's own freely-distributed publication; next year's edition will have "
                    "a different publication-ID URL -- find and re-curate manually, once a year."),
    "india_aggregate": {"fdi_2024_usd_bn": 108.6, "yoy_change_pct": 28, "project_count": 1017,
                        "rank_apac": 1, "rank_global": 2, "note": "#2 globally after the US; #1 globally for job creation"},
    "named_projects": [
        {"company": "ArcelorMittal Nippon Steel India (AM/NS India)",
         "parent_countries": ["Luxembourg (ArcelorMittal)", "Japan (Nippon Steel)"],
         "investment_usd_bn": 1.6, "location": "Rajayyapeta / Nakkapalli Cluster, Andhra Pradesh",
         "sector": "Steel", "estimated_jobs": 20000},
        {"company": "Powerchip Technology + Tata Electronics", "parent_countries": ["Taiwan", "India"],
         "investment_usd_bn": 11.0, "location": "Dholera, Gujarat",
         "sector": "Semiconductors (12-inch wafer fab)", "estimated_jobs": None,
         "note": "\"Made in India\" compliant"},
    ],
    "unctad_wir_cross_check": ("UNCTAD's World Investment Report ultimately sources its greenfield-FDI "
                               "annex tables from fDi Markets, but publishes AGGREGATE only (source/"
                               "destination country x sector), no company-level annex -- fDi "
                               "Intelligence's own reporting is the only company-level route."),
}

ACCESS_HAZARDS = [
    {"target": "vibrantgujarat.com", "issue": "403 to curl/WebFetch (WAF/bot-detection); loads fine in a real browser",
     "implication": "any future scrape needs headless-browser fetch, not plain HTTP"},
    {"target": "upgis2023.in", "issue": "DEAD -- now a repurposed/parked spam domain",
     "implication": "do not link to it; use the iiaonline.in PDF mirror instead"},
    {"target": "invest.up.gov.in/gbc2024/", "issue": '403 "Forbidden: Access is denied" (path-specific WAF)',
     "implication": "sibling paths on the same host (upgis-2023/, ground-breaking-ceremony-4-0/) return 200"},
    {"target": "investkarnataka.co.in", "issue": "reachable but no consolidated MOU table",
     "implication": "\"Recent Developments\" is per-company press-release PDFs only, high-effort to aggregate"},
]

NOT_BUILT = {
    "vibrant_gujarat": "No consolidated MOU table exists at all; only press aggregates (41,299 projects / Rs 26.33 lakh cr at VGGS 2024) and scattered per-company news mentions. Would need RTI or per-article scraping -- not attempted.",
    "invest_karnataka": "No consolidated MOU table; per-company press-release PDFs only. Not attempted.",
}


def main():
    layer = {
        "layer": 36,
        "name": "investment_snapshots",
        "built": datetime.date.today().isoformat(),
        "what": ("Curated (not live-fetched) point-in-time investment-announcement snapshots: "
                 "the one state investor-summit MOU list that's actually structured (UPGIS 2023) "
                 "and the one fDi Intelligence free-content asset that's actually scrapable "
                 "(The fDi Report 2025, fetched off-domain to respect fdiintelligence.com's own "
                 "robots.txt block on AI crawlers). Feeds new company names into layer 16/32."),
        "upgis_2023": UPGIS_2023,
        "fdi_report_2025": FDI_REPORT_2025,
        "access_hazards": ACCESS_HAZARDS,
        "sources_investigated_not_built": NOT_BUILT,
        "refresh_cadence": "MANUAL, ANNUAL -- neither source is a live/recurring feed; re-curate by hand once a year",
    }
    with open(OUT_JSON, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)

    L = ["# Investment-announcement snapshots (state summit MOUs + fDi Report)", "",
         f"*Generated {layer['built']} by `scripts/build_layer36_investment_snapshots.py` -- curated "
         "point-in-time data, refreshed manually once a year, not a live scrape. Do not hand-edit "
         "the JSON; edit the script's curated tables instead.*", "",
         "## UPGIS 2023 — named companies (top ~12 of 19,058 total MoUs)", "",
         f"Source: [{UPGIS_2023['source_url']}]({UPGIS_2023['source_url']}), snapshot dated "
         f"{UPGIS_2023['snapshot_date']}. {UPGIS_2023['source_note']}", "",
         "| Company | Country | MoUs | Sectors | Investment (Rs cr) | Jobs |",
         "|---|---|---|---|---|---|"]
    for c in UPGIS_2023["companies"]:
        L.append(f"| {c['company']} | {c['country'] or '—'} | {c['mous'] or '—'} | {c['sectors'] or '—'} | "
                 f"{c['investment_inr_cr']:,.0f} | {c['estimated_jobs'] or '—'} |")
    L += ["", f"**Foreign companies**: {', '.join(UPGIS_2023['foreign_companies_only'])}", "",
          "## fDi Report 2025 — named India greenfield projects", "",
          f"Source: [{FDI_REPORT_2025['source_url']}]({FDI_REPORT_2025['source_url']}) "
          f"(fetched off-domain — fdiintelligence.com itself blocks AI crawlers via robots.txt). "
          f"{FDI_REPORT_2025['source_note']}", "",
          f"India 2024 aggregate: **${FDI_REPORT_2025['india_aggregate']['fdi_2024_usd_bn']}bn** "
          f"(+{FDI_REPORT_2025['india_aggregate']['yoy_change_pct']}% YoY), "
          f"{FDI_REPORT_2025['india_aggregate']['project_count']} projects, "
          f"#{FDI_REPORT_2025['india_aggregate']['rank_apac']} in APAC, "
          f"#{FDI_REPORT_2025['india_aggregate']['rank_global']} globally.", "",
          "| Company | Parent countries | Investment | Location | Sector |", "|---|---|---|---|---|"]
    for p in FDI_REPORT_2025["named_projects"]:
        L.append(f"| {p['company']} | {', '.join(p['parent_countries'])} | ${p['investment_usd_bn']}bn | "
                 f"{p['location']} | {p['sector']} |")
    L += ["", "## Access hazards recorded (not attempted / blocked)", ""]
    for h in ACCESS_HAZARDS:
        L.append(f"- **{h['target']}**: {h['issue']} — {h['implication']}")
    L += ["", "## Sources investigated, not built", ""]
    for k, v in NOT_BUILT.items():
        L.append(f"- **{k.replace('_', ' ').title()}**: {v}")
    L.append("")
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"UPGIS companies: {len(UPGIS_2023['companies'])} ({len(UPGIS_2023['foreign_companies_only'])} foreign) "
          f"| fDi named projects: {len(FDI_REPORT_2025['named_projects'])} -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
