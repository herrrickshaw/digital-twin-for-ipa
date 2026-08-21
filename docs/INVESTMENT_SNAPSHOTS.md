# Investment-announcement snapshots (state summit MOUs + fDi Report)

*Generated 2026-08-09 by `scripts/build_layer36_investment_snapshots.py` -- curated point-in-time data, refreshed manually once a year, not a live scrape. Do not hand-edit the JSON; edit the script's curated tables instead.*

## UPGIS 2023 — named companies (top ~12 of 19,058 total MoUs)

Source: [https://www.iiaonline.in/Uploads/ImportantUpdates/upgis-2023-investment-figures-as-on-11-02-2023-13-02-2023.pdf](https://www.iiaonline.in/Uploads/ImportantUpdates/upgis-2023-investment-figures-as-on-11-02-2023-13-02-2023.pdf), snapshot dated 2023-02-11. Mirrored via an industry association (IIA) -- content is an official government summary; not hosted directly on invest.up.gov.in. Format: PDF with real tables (Top-10/12 Investment Intents, sector-wise top-20, region-wise, 75-district annexure -- district level only past the top ~12).

| Company | Country | MoUs | Sectors | Investment (Rs cr) | Jobs |
|---|---|---|---|---|---|
| Tauschen International Ltd | Hong Kong SAR | 16 | MRO, Manufacturing, Electronics, Textile, EV | 189,849 | 62494 |
| RG Strategies Group | India | 7 | Renewable Energy, EV | 173,031 | — |
| Imperia Innovation Investment / Austin Consulting Group | United States | 2 | Education, Infrastructure | 105,000 | — |
| Causis Group | — | 1 | EV | 100,000 | — |
| Reliance Industries Ltd | India | — | Telecom Infra, MRO | 75,000 | — |
| ABC Cleantech Pvt Ltd | India | — | Renewable Energy (Mirzapur) | 50,000 | — |
| NTPC Ltd | India | 4 | Renewable Energy | 42,280 | — |
| Unicorn Energy | Germany | 2 | Renewable Energy | 41,500 | — |
| GMR Group | India | — | — | 40,000 | — |
| Aditya Birla Group | India | — | — | 25,000 | — |
| Hinduja Group | India | — | — | 25,000 | — |

**Foreign companies**: Tauschen International Ltd, Imperia Innovation Investment / Austin Consulting Group, Unicorn Energy

## fDi Report 2025 — named India greenfield projects

Source: [https://fdiinsights-publications.s3.eu-west-1.amazonaws.com/publications/5000067/documents/The_fDi_Report_2025.pdf](https://fdiinsights-publications.s3.eu-west-1.amazonaws.com/publications/5000067/documents/The_fDi_Report_2025.pdf) (fetched off-domain — fdiintelligence.com itself blocks AI crawlers via robots.txt). Fetched via the S3/ftlocations.com mirror ONLY -- fdiintelligence.com's own robots.txt disallows AI crawlers site-wide (anthropic-ai, Claude-Web, ClaudeBot explicitly named), so this project will not fetch that domain directly. The PDF is the vendor's own freely-distributed publication; next year's edition will have a different publication-ID URL -- find and re-curate manually, once a year.

India 2024 aggregate: **$108.6bn** (+28% YoY), 1017 projects, #1 in APAC, #2 globally.

| Company | Parent countries | Investment | Location | Sector |
|---|---|---|---|---|
| ArcelorMittal Nippon Steel India (AM/NS India) | Luxembourg (ArcelorMittal), Japan (Nippon Steel) | $1.6bn | Rajayyapeta / Nakkapalli Cluster, Andhra Pradesh | Steel |
| Powerchip Technology + Tata Electronics | Taiwan, India | $11.0bn | Dholera, Gujarat | Semiconductors (12-inch wafer fab) |

## Access hazards recorded (not attempted / blocked)

- **vibrantgujarat.com**: 403 to curl/WebFetch (WAF/bot-detection); loads fine in a real browser — any future scrape needs headless-browser fetch, not plain HTTP
- **upgis2023.in**: DEAD -- now a repurposed/parked spam domain — do not link to it; use the iiaonline.in PDF mirror instead
- **invest.up.gov.in/gbc2024/**: 403 "Forbidden: Access is denied" (path-specific WAF) — sibling paths on the same host (upgis-2023/, ground-breaking-ceremony-4-0/) return 200
- **investkarnataka.co.in**: reachable but no consolidated MOU table — "Recent Developments" is per-company press-release PDFs only, high-effort to aggregate

## Sources investigated, not built

- **Vibrant Gujarat**: No consolidated MOU table exists at all; only press aggregates (41,299 projects / Rs 26.33 lakh cr at VGGS 2024) and scattered per-company news mentions. Would need RTI or per-article scraping -- not attempted.
- **Invest Karnataka**: No consolidated MOU table; per-company press-release PDFs only. Not attempted.

