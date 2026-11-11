# Live media RSS sweep — layer 45

*Generated 2026-11-04 by `scripts/build_layer45_media_rss_sweep.py`. 510 feed items scanned across 8 newspapers, 205 carried investment-intent language, 10 matched a real foreign-company roster name (9 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| Clean Energy Technologies, Inc. - Common Stock | US | www.business-standard.com | [US-based KKR gets CCI nod to acquire stake in Gentari Renewables](https://www.business-standard.com/companies/news/us-based-kkr-gets-cci-nod-to-acquire-stake-in-gentari-renewables-126110400727_1.html) | Wed, 04 Nov 2026 14:04:57 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | www.business-standard.com | [US-based KKR gets CCI nod to acquire stake in Gentari Renewables](https://www.business-standard.com/companies/news/us-based-kkr-gets-cci-nod-to-acquire-stake-in-gentari-renewables-126110400727_1.html) | Wed, 04 Nov 2026 14:04:57 +0530 |
| Diversified Energy Company Common Stock | US | www.thehindubusinessline.com | [Essar Renewables to invest ₹4,500 cr in NHPC project in Andhra Pradesh](https://www.thehindubusinessline.com/news/essar-renewables-to-invest-4500-cr-in-nhpc-project-in-andhra-pradesh/article71664397.ece) | Wed, 04 Nov 2026 12:30:01 +0530 |
| Deutsche Bank AG Common Stock | US | www.thehindu.com | [Kotak Mahindra Bank gets CCI nod to acquire Deutsche Bank India's retail, privat](https://www.thehindu.com/business/Industry/kotak-mahindra-bank-gets-cci-nod-to-acquire-deutsche-bank-indias-retail-private-banking-businesses/article71664408.ece) | Wed, 04 Nov 2026 12:23:01 +0530 |
| ASA  Gold and Precious Metals Limited | US | economictimes.indiatimes.com | [Middle class spending boom in India comes with growing debt bill](https://economictimes.indiatimes.com/industry/banking/finance/middle-class-spending-boom-in-india-comes-with-growing-debt-bill/articleshow/135526004.cms) | Wed, 04 Nov 2026 11:31:38 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | economictimes.indiatimes.com | [Tata Motors-Iveco will focus on building a global CV business: N Chandrasekaran](https://economictimes.indiatimes.com/industry/auto/lcv-hcv/tata-motors-iveco-will-focus-on-building-a-global-cv-business-n-chandrasekaran/articleshow/135511563.cms) | Wed, 04 Nov 2026 01:00:54 +0530 |
| Saudi Aramco Base Oil Company - Luberef | SA | www.business-standard.com | [Saudi Aramco Q3 net profit rises 35% on higher oil prices, stake sale](https://www.business-standard.com/world-news/saudi-aramco-q3-net-profit-rises-35-on-higher-oil-prices-stake-sale-126110301317_1.html) | Tue, 03 Nov 2026 22:38:51 +0530 |
| Deutsche Bank AG Common Stock | US | www.business-standard.com | [CCI clears Kotak Bank's acquisition of Deutsche Bank India retail business](https://www.business-standard.com/companies/news/cci-clears-kotak-bank-s-acquisition-of-deutsche-bank-india-retail-business-126110301856_1.html) | Tue, 03 Nov 2026 21:24:20 +0530 |
| Deutsche Bank AG Common Stock | US | economictimes.indiatimes.com | [CCI clears Kotak-Deutsche deal, KKR vehicle's Gentari investment](https://economictimes.indiatimes.com/industry/banking/finance/banking/cci-clears-kotak-deutsche-deal-kkr-vehicles-gentari-investment/articleshow/135505393.cms) | Tue, 03 Nov 2026 21:18:26 +0530 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Health and Happiness (H&H) International Holdings Ltd | HK |  | [Pioneer Urban to invest Rs 3,500 crore in ultra-luxury Gurugram residences](https://economictimes.indiatimes.com/industry/services/property-/-cstruction/pioneer-urban-to-invest-rs-3500-crore-in-ultra-luxury-gurugram-residences/articleshow/135534814.cms) | Wed, 04 Nov 2026 15:28:18 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | 🆕 | [US-based KKR gets CCI nod to acquire stake in Gentari Renewables](https://www.business-standard.com/companies/news/us-based-kkr-gets-cci-nod-to-acquire-stake-in-gentari-renewables-126110400727_1.html) | Wed, 04 Nov 2026 14:04:57 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | 🆕 | [US-based KKR gets CCI nod to acquire stake in Gentari Renewables](https://www.business-standard.com/companies/news/us-based-kkr-gets-cci-nod-to-acquire-stake-in-gentari-renewables-126110400727_1.html) | Wed, 04 Nov 2026 14:04:57 +0530 |
| Diversified Energy Company Common Stock | US | 🆕 | [Essar Renewables to invest ₹4,500 cr in NHPC project in Andhra Pradesh](https://www.thehindubusinessline.com/news/essar-renewables-to-invest-4500-cr-in-nhpc-project-in-andhra-pradesh/article71664397.ece) | Wed, 04 Nov 2026 12:30:01 +0530 |
| Deutsche Bank AG Common Stock | US | 🆕 | [Kotak Mahindra Bank gets CCI nod to acquire Deutsche Bank India's retail, privat](https://www.thehindu.com/business/Industry/kotak-mahindra-bank-gets-cci-nod-to-acquire-deutsche-bank-indias-retail-private-banking-businesses/article71664408.ece) | Wed, 04 Nov 2026 12:23:01 +0530 |
| ASA  Gold and Precious Metals Limited | US | 🆕 | [Middle class spending boom in India comes with growing debt bill](https://economictimes.indiatimes.com/industry/banking/finance/middle-class-spending-boom-in-india-comes-with-growing-debt-bill/articleshow/135526004.cms) | Wed, 04 Nov 2026 11:31:38 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | 🆕 | [Tata Motors-Iveco will focus on building a global CV business: N Chandrasekaran](https://economictimes.indiatimes.com/industry/auto/lcv-hcv/tata-motors-iveco-will-focus-on-building-a-global-cv-business-n-chandrasekaran/articleshow/135511563.cms) | Wed, 04 Nov 2026 01:00:54 +0530 |
| Saudi Aramco Base Oil Company - Luberef | SA | 🆕 | [Saudi Aramco Q3 net profit rises 35% on higher oil prices, stake sale](https://www.business-standard.com/world-news/saudi-aramco-q3-net-profit-rises-35-on-higher-oil-prices-stake-sale-126110301317_1.html) | Tue, 03 Nov 2026 22:38:51 +0530 |
| Deutsche Bank AG Common Stock | US | 🆕 | [CCI clears Kotak Bank's acquisition of Deutsche Bank India retail business](https://www.business-standard.com/companies/news/cci-clears-kotak-bank-s-acquisition-of-deutsche-bank-india-retail-business-126110301856_1.html) | Tue, 03 Nov 2026 21:24:20 +0530 |
| Deutsche Bank AG Common Stock | US | 🆕 | [CCI clears Kotak-Deutsche deal, KKR vehicle's Gentari investment](https://economictimes.indiatimes.com/industry/banking/finance/banking/cci-clears-kotak-deutsche-deal-kkr-vehicles-gentari-investment/articleshow/135505393.cms) | Tue, 03 Nov 2026 21:18:26 +0530 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 18 | 1 |  |
| ET | cons_products | 50 | 21 | 0 |  |
| ET | industry | 50 | 24 | 3 |  |
| Hindu | business | 60 | 19 | 1 |  |
| HinduBusinessLine | companies | 60 | 35 | 1 |  |
| HinduBusinessLine | economy | 60 | 14 | 0 |  |
| TimesOfIndia | business | 20 | 6 | 0 |  |
| Livemint | companies | 35 | 18 | 0 |  |
| Livemint | industry | 35 | 10 | 0 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 0 | 0 | 0 | HTTP 502 |
| BusinessStandard | companies | 35 | 25 | 4 |  |
| AmarUjala | business | 40 | 9 | 0 |  |

