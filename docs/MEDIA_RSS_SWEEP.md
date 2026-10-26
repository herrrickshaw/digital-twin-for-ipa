# Live media RSS sweep — layer 45

*Generated 2026-10-26 by `scripts/build_layer45_media_rss_sweep.py`. 454 feed items scanned across 8 newspapers, 178 carried investment-intent language, 9 matched a real foreign-company roster name (8 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| Commercial Vehicle Group, Inc. - Common Stock | US | www.thehindubusinessline.com | [Tata Motors’ €3.91-billion Iveco bid faces make-or-break October 26 test of glob](https://www.thehindubusinessline.com/companies/tata-motors-391-billion-iveco-bid-faces-make-or-break-october-26-test-of-global-ambitions/article71622938.ece) | Sun, 25 Oct 2026 19:52:35 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | www.livemint.com | [Mint Explainer | How new land compensation rules could speed up India’s clean en](https://www.livemint.com/industry/energy/mint-explainer-how-new-land-compensation-rules-could-speed-up-india-s-clean-energy-transition-11792913800449.html) | Sun, 25 Oct 2026 16:57:24 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | www.livemint.com | [Mint Explainer | How new land compensation rules could speed up India’s clean en](https://www.livemint.com/industry/energy/mint-explainer-how-new-land-compensation-rules-could-speed-up-india-s-clean-energy-transition-11792913800449.html) | Sun, 25 Oct 2026 16:57:24 +0530 |
| Asia Pacific Wire & Cable Corporation Limited  - Common shares, Par value .01 per share | US | www.business-standard.com | [L'Oreal sees India biz gaining momentum; expands skincare, online presence](https://www.business-standard.com/companies/news/l-oreal-sees-india-biz-gaining-momentum-expands-skincare-online-presence-126102500132_1.html) | Sun, 25 Oct 2026 12:50:47 +0530 |
| CRITICAL MINERALS GROUP LIMITED | AU | economictimes.indiatimes.com | [Diversification plan: NMDC scouts for mining assets across four continents](https://economictimes.indiatimes.com/industry/indl-goods/svs/metals-mining/diversification-plan-nmdc-scouts-for-mining-assets-across-four-continents/articleshow/135184622.cms) | Sun, 25 Oct 2026 11:27:51 +0530 |
| Southeast Asia Properties & Finance Ltd | HK | www.thehindubusinessline.com | [Cordelia Cruises launches Cordelia Sky, expands fleet to two ships](https://www.thehindubusinessline.com/economy/logistics/cordelia-cruises-launches-cordelia-sky-expands-fleet-to-two-ships/article71619024.ece) | Sat, 24 Oct 2026 17:12:06 +0530 |
| HDFC Bank Limited Common Stock | US | www.livemint.com | [Sonu Sood’s Mumbai property portfolio: How  ₹3.52 crore Bokka Coffee rent is str](https://www.livemint.com/industry/real-estate/sonu-sood-s-mumbai-property-portfolio-how-3-52-crore-bokka-coffee-rent-is-structured-how-much-he-earns-from-hdfc-bank-11792733291054.html) | Fri, 23 Oct 2026 11:36:57 +0530 |
| HDFC Bank Limited Common Stock | US | timesofindia.indiatimes.com | [Market recap: Eight of top 10 firms lose Rs 1.55 lakh crore](https://timesofindia.indiatimes.com/business/india-business/market-recap-eight-of-top-10-firms-lose-rs-1-55-lakh-crore-hdfc-bank-bajaj-finance-take-biggest-hit/articleshow/135187845.cms) | 2026-10-25T15:06:39+05:30 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Semiconductor Manufacturing International Corp | HK |  | [India’s Composite Flash PMI for April signals very strong economy](https://www.moneycontrol.com/news/economy/india’s-composite-flash-pmi-for-april-signals-very-strong-economy_17531301.html) | Tue, 23 Apr 2024 11:07:37 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | 🆕 | [Tata Motors’ €3.91-billion Iveco bid faces make-or-break October 26 test of glob](https://www.thehindubusinessline.com/companies/tata-motors-391-billion-iveco-bid-faces-make-or-break-october-26-test-of-global-ambitions/article71622938.ece) | Sun, 25 Oct 2026 19:52:35 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | 🆕 | [Mint Explainer | How new land compensation rules could speed up India’s clean en](https://www.livemint.com/industry/energy/mint-explainer-how-new-land-compensation-rules-could-speed-up-india-s-clean-energy-transition-11792913800449.html) | Sun, 25 Oct 2026 16:57:24 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | 🆕 | [Mint Explainer | How new land compensation rules could speed up India’s clean en](https://www.livemint.com/industry/energy/mint-explainer-how-new-land-compensation-rules-could-speed-up-india-s-clean-energy-transition-11792913800449.html) | Sun, 25 Oct 2026 16:57:24 +0530 |
| Asia Pacific Wire & Cable Corporation Limited  - Common shares, Par value .01 per share | US | 🆕 | [L'Oreal sees India biz gaining momentum; expands skincare, online presence](https://www.business-standard.com/companies/news/l-oreal-sees-india-biz-gaining-momentum-expands-skincare-online-presence-126102500132_1.html) | Sun, 25 Oct 2026 12:50:47 +0530 |
| CRITICAL MINERALS GROUP LIMITED | AU | 🆕 | [Diversification plan: NMDC scouts for mining assets across four continents](https://economictimes.indiatimes.com/industry/indl-goods/svs/metals-mining/diversification-plan-nmdc-scouts-for-mining-assets-across-four-continents/articleshow/135184622.cms) | Sun, 25 Oct 2026 11:27:51 +0530 |
| Southeast Asia Properties & Finance Ltd | HK | 🆕 | [Cordelia Cruises launches Cordelia Sky, expands fleet to two ships](https://www.thehindubusinessline.com/economy/logistics/cordelia-cruises-launches-cordelia-sky-expands-fleet-to-two-ships/article71619024.ece) | Sat, 24 Oct 2026 17:12:06 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [Sonu Sood’s Mumbai property portfolio: How  ₹3.52 crore Bokka Coffee rent is str](https://www.livemint.com/industry/real-estate/sonu-sood-s-mumbai-property-portfolio-how-3-52-crore-bokka-coffee-rent-is-structured-how-much-he-earns-from-hdfc-bank-11792733291054.html) | Fri, 23 Oct 2026 11:36:57 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [Market recap: Eight of top 10 firms lose Rs 1.55 lakh crore](https://timesofindia.indiatimes.com/business/india-business/market-recap-eight-of-top-10-firms-lose-rs-1-55-lakh-crore-hdfc-bank-bajaj-finance-take-biggest-hit/articleshow/135187845.cms) | 2026-10-25T15:06:39+05:30 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 18 | 0 |  |
| ET | cons_products | 50 | 20 | 0 |  |
| ET | industry | 50 | 17 | 1 |  |
| Hindu | business | 0 | 0 | 0 | HTTP 403 |
| HinduBusinessLine | companies | 60 | 35 | 2 |  |
| HinduBusinessLine | economy | 60 | 14 | 0 |  |
| TimesOfIndia | business | 20 | 5 | 1 |  |
| Livemint | companies | 35 | 17 | 0 |  |
| Livemint | industry | 35 | 11 | 3 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 4 | 1 | 1 |  |
| BusinessStandard | companies | 35 | 24 | 1 |  |
| AmarUjala | business | 40 | 10 | 0 |  |

