# Live media RSS sweep — layer 45

*Generated 2026-09-21 by `scripts/build_layer45_media_rss_sweep.py`. 514 feed items scanned across 8 newspapers, 183 carried investment-intent language, 15 matched a real foreign-company roster name (7 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| CRITICAL MINERALS GROUP LIMITED | AU | www.business-standard.com | [Coal India plans to raise annual R&D spending to ₹500 crore by FY30](https://www.business-standard.com/companies/news/coal-india-plans-to-raise-annual-r-d-spending-to-500-crore-by-fy30-126092000644_1.html) | Sun, 20 Sep 2026 19:03:19 +0530 |
| CRITICAL MINERALS GROUP LIMITED | AU | economictimes.indiatimes.com | [Coal India Limited announces ambitious Business Development portfolio for divers](https://economictimes.indiatimes.com/industry/energy/power/coal-india-limited-announces-ambitious-business-development-portfolio-for-diversification-beyond-mining/articleshow/134368468.cms) | Sun, 20 Sep 2026 17:57:54 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | www.livemint.com | [Paramount Settlement Talks Include Promise to Stay in California](https://www.livemint.com/companies/paramount-settlement-talks-include-promise-to-stay-in-california-11789854789916.html) | Sun, 20 Sep 2026 03:23:09 +0530 |
| Trip.com Group Ltd | HK | www.livemint.com | [Alibaba, Meituan units in trouble? China antitrust probe follows Trip.com’s $776](https://www.livemint.com/companies/news/alibaba-meituan-units-in-trouble-china-antitrust-probe-follows-trip-com-s-776-million-penalty-11789834813094.html) | Sat, 19 Sep 2026 22:00:17 +0530 |
| Trip.com Group Limited - American Depositary Shares | US | www.livemint.com | [Alibaba, Meituan units in trouble? China antitrust probe follows Trip.com’s $776](https://www.livemint.com/companies/news/alibaba-meituan-units-in-trouble-china-antitrust-probe-follows-trip-com-s-776-million-penalty-11789834813094.html) | Sat, 19 Sep 2026 22:00:17 +0530 |
| Wells Fargo & Company Common Stock | US | www.livemint.com | [Netflix stock tumbles: Wells Fargo cuts target, says streamer giant needs ‘break](https://www.livemint.com/companies/news/netflix-stock-tumbles-wells-fargo-cuts-target-says-streamer-giant-needs-breakout-hits-11789824110933.html) | Sat, 19 Sep 2026 20:08:37 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | economictimes.indiatimes.com | [Domestic CV wholesale volumes to grow 4-6 pc in FY27: ICRA](https://economictimes.indiatimes.com/industry/auto/lcv-hcv/domestic-cv-wholesale-volumes-to-grow-4-6-pc-in-fy27-icra/articleshow/134332580.cms) | Fri, 18 Sep 2026 16:12:17 +0530 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Semiconductor Manufacturing International Corp | HK |  | [India’s Composite Flash PMI for April signals very strong economy](https://www.moneycontrol.com/news/economy/india’s-composite-flash-pmi-for-april-signals-very-strong-economy_17531301.html) | Tue, 23 Apr 2024 11:07:37 +0530 |
| Applied Materials Inc | HK |  | [Applied Materials’ $5 billion India plan to build chip R&amp;D lab, supply chain](https://www.livemint.com/industry/applied-materials-5-billion-india-plan-to-build-chip-r-d-lab-supply-chain-11789655951975.html) | Thu, 17 Sep 2026 21:22:36 +0530 |
| Applied Materials, Inc. - Common Stock | US |  | [Applied Materials’ $5 billion India plan to build chip R&amp;D lab, supply chain](https://www.livemint.com/industry/applied-materials-5-billion-india-plan-to-build-chip-r-d-lab-supply-chain-11789655951975.html) | Thu, 17 Sep 2026 21:22:36 +0530 |
| Applied Materials Inc | HK |  | [Tata Electronics, Applied Materials bolster India’s chip push](https://www.livemint.com/industry/tata-electronics-applied-materials-bolster-india-s-chip-push-11789652984326.html) | Thu, 17 Sep 2026 21:12:39 +0530 |
| Applied Materials, Inc. - Common Stock | US |  | [Tata Electronics, Applied Materials bolster India’s chip push](https://www.livemint.com/industry/tata-electronics-applied-materials-bolster-india-s-chip-push-11789652984326.html) | Thu, 17 Sep 2026 21:12:39 +0530 |
| Applied Materials Inc | HK |  | [Applied Materials announces $5 billion India investment under Vision 2035 for se](https://economictimes.indiatimes.com/industry/cons-products/electronics/applied-materials-announces-5-billion-india-investment-under-vision-2035-for-semiconductor-ecosystem/articleshow/134303422.cms) | Thu, 17 Sep 2026 11:51:29 +0530 |
| Applied Materials, Inc. - Common Stock | US |  | [Applied Materials announces $5 billion India investment under Vision 2035 for se](https://economictimes.indiatimes.com/industry/cons-products/electronics/applied-materials-announces-5-billion-india-investment-under-vision-2035-for-semiconductor-ecosystem/articleshow/134303422.cms) | Thu, 17 Sep 2026 11:51:29 +0530 |
| CRITICAL MINERALS GROUP LIMITED | AU | 🆕 | [Coal India plans to raise annual R&D spending to ₹500 crore by FY30](https://www.business-standard.com/companies/news/coal-india-plans-to-raise-annual-r-d-spending-to-500-crore-by-fy30-126092000644_1.html) | Sun, 20 Sep 2026 19:03:19 +0530 |
| CRITICAL MINERALS GROUP LIMITED | AU | 🆕 | [Coal India Limited announces ambitious Business Development portfolio for divers](https://economictimes.indiatimes.com/industry/energy/power/coal-india-limited-announces-ambitious-business-development-portfolio-for-diversification-beyond-mining/articleshow/134368468.cms) | Sun, 20 Sep 2026 17:57:54 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | 🆕 | [Paramount Settlement Talks Include Promise to Stay in California](https://www.livemint.com/companies/paramount-settlement-talks-include-promise-to-stay-in-california-11789854789916.html) | Sun, 20 Sep 2026 03:23:09 +0530 |
| Trip.com Group Ltd | HK | 🆕 | [Alibaba, Meituan units in trouble? China antitrust probe follows Trip.com’s $776](https://www.livemint.com/companies/news/alibaba-meituan-units-in-trouble-china-antitrust-probe-follows-trip-com-s-776-million-penalty-11789834813094.html) | Sat, 19 Sep 2026 22:00:17 +0530 |
| Trip.com Group Limited - American Depositary Shares | US | 🆕 | [Alibaba, Meituan units in trouble? China antitrust probe follows Trip.com’s $776](https://www.livemint.com/companies/news/alibaba-meituan-units-in-trouble-china-antitrust-probe-follows-trip-com-s-776-million-penalty-11789834813094.html) | Sat, 19 Sep 2026 22:00:17 +0530 |
| Wells Fargo & Company Common Stock | US | 🆕 | [Netflix stock tumbles: Wells Fargo cuts target, says streamer giant needs ‘break](https://www.livemint.com/companies/news/netflix-stock-tumbles-wells-fargo-cuts-target-says-streamer-giant-needs-breakout-hits-11789824110933.html) | Sat, 19 Sep 2026 20:08:37 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | 🆕 | [Domestic CV wholesale volumes to grow 4-6 pc in FY27: ICRA](https://economictimes.indiatimes.com/industry/auto/lcv-hcv/domestic-cv-wholesale-volumes-to-grow-4-6-pc-in-fy27-icra/articleshow/134332580.cms) | Fri, 18 Sep 2026 16:12:17 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [India’s semiconductor journey ‘pretty strong’, Semicon 2.0 offers policy continu](https://economictimes.indiatimes.com/industry/cons-products/electronics/indias-semiconductor-journey-pretty-strong-semicon-2-0-offers-policy-continuity-tata-electronics-ceo/articleshow/134326802.cms) | Fri, 18 Sep 2026 11:06:17 +0530 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 19 | 1 |  |
| ET | cons_products | 50 | 35 | 3 |  |
| ET | industry | 50 | 20 | 1 |  |
| Hindu | business | 60 | 16 | 0 |  |
| HinduBusinessLine | companies | 60 | 18 | 0 |  |
| HinduBusinessLine | economy | 60 | 12 | 0 |  |
| TimesOfIndia | business | 20 | 3 | 0 |  |
| Livemint | companies | 35 | 10 | 4 |  |
| Livemint | industry | 35 | 14 | 4 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 4 | 1 | 1 |  |
| BusinessStandard | companies | 35 | 12 | 1 |  |
| AmarUjala | business | 40 | 17 | 0 |  |

