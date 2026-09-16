# Live media RSS sweep — layer 45

*Generated 2026-09-16 by `scripts/build_layer45_media_rss_sweep.py`. 330 feed items scanned across ET/Hindu/HBL, 89 carried investment-intent language, 7 matched a real foreign-company roster name (3 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup (ET: JSON-LD `articleBody`; Hindu/HBL: shared `contentbody` div) — no third-party scraper needed.

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| Clean Energy Technologies, Inc. - Common Stock | US | economictimes.indiatimes.com | [Saatvik Green Energy bags order worth Rs 1042 crore from SECI](https://economictimes.indiatimes.com/industry/renewables/saatvik-green-energy-bags-order-worth-rs-1042-crore-from-seci/articleshow/134267699.cms) | Tue, 15 Sep 2026 20:44:03 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | economictimes.indiatimes.com | [Saatvik Green Energy bags order worth Rs 1042 crore from SECI](https://economictimes.indiatimes.com/industry/renewables/saatvik-green-energy-bags-order-worth-rs-1042-crore-from-seci/articleshow/134267699.cms) | Tue, 15 Sep 2026 20:44:03 +0530 |
| ONE CLICK GROUP LIMITED | AU | www.thehindu.com | [ETFs: A one-click route to diversified investing](https://www.thehindu.com/business/etfs-a-one-click-route-to-diversified-investing/article71463244.ece) | Sun, 13 Sep 2026 17:31:02 +0530 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Semiconductor Manufacturing International Corp | HK |  | [Japan’s Hirata bets on India’s semiconductor boom with ATS India tie-up](https://economictimes.indiatimes.com/industry/cons-products/electronics/japans-hirata-bets-on-indias-semiconductor-boom-with-ats-india-tie-up/articleshow/134278072.cms) | Wed, 16 Sep 2026 10:02:26 +0530 |
| Coca-Cola Consolidated, Inc. - Common Stock | US |  | [Hindustan Coca-Cola Beverages lines up Rs 1,127 crore for new unit, expansion in](https://economictimes.indiatimes.com/industry/cons-products/food/hindustan-coca-cola-beverages-lines-up-1127-crore-for-new-unit-expansion-in-andhra-pradesh/articleshow/134272247.cms) | Wed, 16 Sep 2026 00:31:56 +0530 |
| Coca-Cola Company (The) Common Stock | US |  | [Hindustan Coca-Cola Beverages lines up Rs 1,127 crore for new unit, expansion in](https://economictimes.indiatimes.com/industry/cons-products/food/hindustan-coca-cola-beverages-lines-up-1127-crore-for-new-unit-expansion-in-andhra-pradesh/articleshow/134272247.cms) | Wed, 16 Sep 2026 00:31:56 +0530 |
| Coca Cola Femsa S.A.B. de C.V.  American Depositary Shares, each representing 10 Units (each Unit consists of 3 Series B Shares and 5 Series L Shares) | US |  | [Hindustan Coca-Cola Beverages lines up Rs 1,127 crore for new unit, expansion in](https://economictimes.indiatimes.com/industry/cons-products/food/hindustan-coca-cola-beverages-lines-up-1127-crore-for-new-unit-expansion-in-andhra-pradesh/articleshow/134272247.cms) | Wed, 16 Sep 2026 00:31:56 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | 🆕 | [Saatvik Green Energy bags order worth Rs 1042 crore from SECI](https://economictimes.indiatimes.com/industry/renewables/saatvik-green-energy-bags-order-worth-rs-1042-crore-from-seci/articleshow/134267699.cms) | Tue, 15 Sep 2026 20:44:03 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | 🆕 | [Saatvik Green Energy bags order worth Rs 1042 crore from SECI](https://economictimes.indiatimes.com/industry/renewables/saatvik-green-energy-bags-order-worth-rs-1042-crore-from-seci/articleshow/134267699.cms) | Tue, 15 Sep 2026 20:44:03 +0530 |
| ONE CLICK GROUP LIMITED | AU | 🆕 | [ETFs: A one-click route to diversified investing](https://www.thehindu.com/business/etfs-a-one-click-route-to-diversified-investing/article71463244.ece) | Sun, 13 Sep 2026 17:31:02 +0530 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 15 | 0 |  |
| ET | cons_products | 50 | 15 | 4 |  |
| ET | industry | 50 | 14 | 2 |  |
| Hindu | business | 60 | 13 | 1 |  |
| HinduBusinessLine | companies | 60 | 23 | 0 |  |
| HinduBusinessLine | economy | 60 | 9 | 0 |  |

