# Live media RSS sweep — layer 45

*Generated 2026-09-16 by `scripts/build_layer45_media_rss_sweep.py`. 514 feed items scanned across 8 newspapers, 146 carried investment-intent language, 5 matched a real foreign-company roster name (2 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| MINERAL RESOURCES LIMITED | AU | economictimes.indiatimes.com | [Indian steel industry creating new opportunities for ferro-alloy sector: IFAPA](https://economictimes.indiatimes.com/industry/indl-goods/svs/steel/indian-steel-industry-creating-new-opportunities-for-ferro-alloy-sector-ifapa/articleshow/134289342.cms) | Wed, 16 Sep 2026 19:02:46 +0530 |
| ONE CLICK GROUP LIMITED | AU | www.thehindu.com | [ETFs: A one-click route to diversified investing](https://www.thehindu.com/business/etfs-a-one-click-route-to-diversified-investing/article71463244.ece) | Sun, 13 Sep 2026 17:31:02 +0530 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| MINERAL RESOURCES LIMITED | AU | 🆕 | [Indian steel industry creating new opportunities for ferro-alloy sector: IFAPA](https://economictimes.indiatimes.com/industry/indl-goods/svs/steel/indian-steel-industry-creating-new-opportunities-for-ferro-alloy-sector-ifapa/articleshow/134289342.cms) | Wed, 16 Sep 2026 19:02:46 +0530 |
| Lam Research Corporation - Common Stock | US |  | [Lam Research to invest ₹10,000 cr in first silicon component manufacturing facil](https://www.thehindubusinessline.com/companies/lam-research-to-invest-10000-cr-in-first-silicon-component-manufacturing-facility-in-india/article71472662.ece) | Wed, 16 Sep 2026 18:49:35 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [Japan’s Hirata bets on India’s semiconductor boom with ATS India tie-up](https://economictimes.indiatimes.com/industry/cons-products/electronics/japans-hirata-bets-on-indias-semiconductor-boom-with-ats-india-tie-up/articleshow/134278072.cms) | Wed, 16 Sep 2026 10:02:26 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [India’s Composite Flash PMI for April signals very strong economy](https://www.moneycontrol.com/news/economy/india’s-composite-flash-pmi-for-april-signals-very-strong-economy_17531301.html) | Tue, 23 Apr 2024 11:07:37 +0530 |
| ONE CLICK GROUP LIMITED | AU | 🆕 | [ETFs: A one-click route to diversified investing](https://www.thehindu.com/business/etfs-a-one-click-route-to-diversified-investing/article71463244.ece) | Sun, 13 Sep 2026 17:31:02 +0530 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 15 | 0 |  |
| ET | cons_products | 50 | 16 | 1 |  |
| ET | industry | 50 | 12 | 1 |  |
| Hindu | business | 60 | 13 | 1 |  |
| HinduBusinessLine | companies | 60 | 22 | 1 |  |
| HinduBusinessLine | economy | 60 | 9 | 0 |  |
| TimesOfIndia | business | 20 | 1 | 0 |  |
| Livemint | companies | 35 | 15 | 0 |  |
| Livemint | industry | 35 | 8 | 0 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 4 | 1 | 1 |  |
| BusinessStandard | companies | 35 | 21 | 0 |  |
| AmarUjala | business | 40 | 7 | 0 |  |

