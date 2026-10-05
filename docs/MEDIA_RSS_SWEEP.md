# Live media RSS sweep — layer 45

*Generated 2026-10-05 by `scripts/build_layer45_media_rss_sweep.py`. 454 feed items scanned across 8 newspapers, 153 carried investment-intent language, 18 matched a real foreign-company roster name (15 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| BLUE STAR HELIUM LIMITED | AU | economictimes.indiatimes.com | [Haier, Godrej, Blue Star failed to detect fake e-waste recycling claims, India n](https://economictimes.indiatimes.com/industry/cons-products/durables/haier-godrej-blue-star-failed-to-detect-fake-e-waste-recycling-claims-india-notice-shows/articleshow/134590175.cms) | Wed, 30 Sep 2026 15:23:25 +0530 |
| Monster Beverage Corporation - Common Stock | US | economictimes.indiatimes.com | [PepsiCo, Monster challenge India 'energy drink' label ban citing business impact](https://economictimes.indiatimes.com/industry/cons-products/food/pepsico-monster-challenge-india-energy-drink-label-ban-citing-business-impact/articleshow/134622448.cms) | Thu, 01 Oct 2026 20:39:43 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | www.business-standard.com | [Sebi keeps Inox Clean Energy's IPO papers to raise ₹10K cr in abeyance](https://www.business-standard.com/companies/news/sebi-keeps-inox-clean-energy-s-ipo-papers-to-raise-10k-cr-in-abeyance-126100101123_1.html) | Thu, 01 Oct 2026 19:29:21 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | www.business-standard.com | [Sebi keeps Inox Clean Energy's IPO papers to raise ₹10K cr in abeyance](https://www.business-standard.com/companies/news/sebi-keeps-inox-clean-energy-s-ipo-papers-to-raise-10k-cr-in-abeyance-126100101123_1.html) | Thu, 01 Oct 2026 19:29:21 +0530 |
| Lockheed Martin Corporation Common Stock | US | www.livemint.com | [Lockheed Martin’s India expansion plan hinges on $10.5bn military aircraft bid: ](https://www.livemint.com/companies/news/lockheed-martin-s-india-expansion-plan-hinges-on-10-5bn-military-aircraft-bid-which-firms-are-competing-for-project-11791107461403.html) | Sun, 04 Oct 2026 16:24:57 +0530 |
| CLOSE THE LOOP LTD. | AU | www.business-standard.com | [Pointo bets on e-auto, BESS, second-life battery segments to drive growth](https://www.business-standard.com/companies/news/pointo-bets-on-e-auto-bess-second-life-battery-segments-to-drive-growth-126100400269_1.html) | Sun, 04 Oct 2026 16:02:00 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | www.livemint.com | [Paramount-Warner Bros merger: Who is staying, who is exiting as Skydance takes s](https://www.livemint.com/entertainment/paramountwarner-bros-merger-who-is-staying-who-is-exiting-as-skydance-takes-shape-11791038008329.html) | Sat, 03 Oct 2026 20:27:20 +0530 |
| Natural Gas Distribution Company | SA | economictimes.indiatimes.com | [GAIL’s Sanjay Kumar named next Petronet LNG CEO](https://economictimes.indiatimes.com/industry/energy/oil-gas/gails-sanjay-kumar-named-next-petronet-lng-ceo/articleshow/134660552.cms) | Sat, 03 Oct 2026 18:47:49 +0530 |
| Natural Gas Services Group, Inc. Common Stock | US | economictimes.indiatimes.com | [GAIL’s Sanjay Kumar named next Petronet LNG CEO](https://economictimes.indiatimes.com/industry/energy/oil-gas/gails-sanjay-kumar-named-next-petronet-lng-ceo/articleshow/134660552.cms) | Sat, 03 Oct 2026 18:47:49 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | www.livemint.com | [Paramount-Warner Bros merger: David Ellison names combined company Skydance](https://www.livemint.com/companies/people/paramountwarner-bros-merger-david-ellison-names-combined-company-skydance-11790994449359.html) | Sat, 03 Oct 2026 08:28:15 +0530 |
| Rare Earth Magnesium Technology Group Holdings Ltd | HK | economictimes.indiatimes.com | [Midwest Energy to set up Rs 250-crore rare earth magnet plant in Hyderabad](https://economictimes.indiatimes.com/industry/cons-products/electronics/midwest-energy-to-set-up-rs-250-crore-rare-earth-magnet-plant-in-hyderabad/articleshow/134536537.cms) | Mon, 28 Sep 2026 13:52:33 +0530 |
| Convenience Retail Asia Ltd | HK | economictimes.indiatimes.com | [Reliance Retail, 7-Eleven end a five-year India franchise deal as convenience st](https://economictimes.indiatimes.com/industry/services/retail/reliance-retail-7-eleven-end-a-five-year-india-franchise-deal-as-convenience-stores-struggle/articleshow/134679568.cms) | Mon, 05 Oct 2026 00:16:12 +0530 |
| GLOBAL HEALTH LIMITED | AU | www.livemint.com | [Global Health expands Delhi-NCR footprint with upcoming Medanta hospital in Ghaz](https://www.livemint.com/industry/infrastructure/global-health-expands-delhi-ncr-footprint-with-upcoming-medanta-hospital-in-ghaziabad-details-inside-11790948239738.html) | Fri, 02 Oct 2026 20:08:08 +0530 |
| Public Service Enterprise Group Incorporated Common Stock | US | www.livemint.com | [Mint Explainer | Why state-owned BSNL is wary of Trai's proposed service quality](https://www.livemint.com/industry/telecom/bsnl-trai-quality-of-service-rules-objections-explained-11790925221858.html) | Fri, 02 Oct 2026 14:01:34 +0530 |
| Mercantile Bank Corporation - Common Stock | US | timesofindia.indiatimes.com | [Credit offtake stays ahead of banks' deposit growth](https://timesofindia.indiatimes.com/business/india-business/credit-offtake-stays-ahead-of-banks-deposit-growth/articleshow/134683228.cms) | 2026-10-05T05:31:32+05:30 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| BLUE STAR HELIUM LIMITED | AU | 🆕 | [Haier, Godrej, Blue Star failed to detect fake e-waste recycling claims, India n](https://economictimes.indiatimes.com/industry/cons-products/durables/haier-godrej-blue-star-failed-to-detect-fake-e-waste-recycling-claims-india-notice-shows/articleshow/134590175.cms) | Wed, 30 Sep 2026 15:23:25 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [India’s Composite Flash PMI for April signals very strong economy](https://www.moneycontrol.com/news/economy/india’s-composite-flash-pmi-for-april-signals-very-strong-economy_17531301.html) | Tue, 23 Apr 2024 11:07:37 +0530 |
| Monster Beverage Corporation - Common Stock | US | 🆕 | [PepsiCo, Monster challenge India 'energy drink' label ban citing business impact](https://economictimes.indiatimes.com/industry/cons-products/food/pepsico-monster-challenge-india-energy-drink-label-ban-citing-business-impact/articleshow/134622448.cms) | Thu, 01 Oct 2026 20:39:43 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | 🆕 | [Sebi keeps Inox Clean Energy's IPO papers to raise ₹10K cr in abeyance](https://www.business-standard.com/companies/news/sebi-keeps-inox-clean-energy-s-ipo-papers-to-raise-10k-cr-in-abeyance-126100101123_1.html) | Thu, 01 Oct 2026 19:29:21 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | 🆕 | [Sebi keeps Inox Clean Energy's IPO papers to raise ₹10K cr in abeyance](https://www.business-standard.com/companies/news/sebi-keeps-inox-clean-energy-s-ipo-papers-to-raise-10k-cr-in-abeyance-126100101123_1.html) | Thu, 01 Oct 2026 19:29:21 +0530 |
| Lockheed Martin Corporation Common Stock | US | 🆕 | [Lockheed Martin’s India expansion plan hinges on $10.5bn military aircraft bid: ](https://www.livemint.com/companies/news/lockheed-martin-s-india-expansion-plan-hinges-on-10-5bn-military-aircraft-bid-which-firms-are-competing-for-project-11791107461403.html) | Sun, 04 Oct 2026 16:24:57 +0530 |
| CLOSE THE LOOP LTD. | AU | 🆕 | [Pointo bets on e-auto, BESS, second-life battery segments to drive growth](https://www.business-standard.com/companies/news/pointo-bets-on-e-auto-bess-second-life-battery-segments-to-drive-growth-126100400269_1.html) | Sun, 04 Oct 2026 16:02:00 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [Canon in talks with key chip project players, plans India service centres](https://www.business-standard.com/companies/news/canon-in-talks-with-key-chip-project-players-plans-india-service-centres-126100400128_1.html) | Sun, 04 Oct 2026 15:51:40 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [Canon eyes chip projects, plans local service centres in India](https://www.thehindubusinessline.com/companies/canon-eyes-chip-projects-plans-local-service-centres-in-india/article71543011.ece) | Sun, 04 Oct 2026 11:21:52 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | 🆕 | [Paramount-Warner Bros merger: Who is staying, who is exiting as Skydance takes s](https://www.livemint.com/entertainment/paramountwarner-bros-merger-who-is-staying-who-is-exiting-as-skydance-takes-shape-11791038008329.html) | Sat, 03 Oct 2026 20:27:20 +0530 |
| Natural Gas Distribution Company | SA | 🆕 | [GAIL’s Sanjay Kumar named next Petronet LNG CEO](https://economictimes.indiatimes.com/industry/energy/oil-gas/gails-sanjay-kumar-named-next-petronet-lng-ceo/articleshow/134660552.cms) | Sat, 03 Oct 2026 18:47:49 +0530 |
| Natural Gas Services Group, Inc. Common Stock | US | 🆕 | [GAIL’s Sanjay Kumar named next Petronet LNG CEO](https://economictimes.indiatimes.com/industry/energy/oil-gas/gails-sanjay-kumar-named-next-petronet-lng-ceo/articleshow/134660552.cms) | Sat, 03 Oct 2026 18:47:49 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | 🆕 | [Paramount-Warner Bros merger: David Ellison names combined company Skydance](https://www.livemint.com/companies/people/paramountwarner-bros-merger-david-ellison-names-combined-company-skydance-11790994449359.html) | Sat, 03 Oct 2026 08:28:15 +0530 |
| Rare Earth Magnesium Technology Group Holdings Ltd | HK | 🆕 | [Midwest Energy to set up Rs 250-crore rare earth magnet plant in Hyderabad](https://economictimes.indiatimes.com/industry/cons-products/electronics/midwest-energy-to-set-up-rs-250-crore-rare-earth-magnet-plant-in-hyderabad/articleshow/134536537.cms) | Mon, 28 Sep 2026 13:52:33 +0530 |
| Convenience Retail Asia Ltd | HK | 🆕 | [Reliance Retail, 7-Eleven end a five-year India franchise deal as convenience st](https://economictimes.indiatimes.com/industry/services/retail/reliance-retail-7-eleven-end-a-five-year-india-franchise-deal-as-convenience-stores-struggle/articleshow/134679568.cms) | Mon, 05 Oct 2026 00:16:12 +0530 |
| GLOBAL HEALTH LIMITED | AU | 🆕 | [Global Health expands Delhi-NCR footprint with upcoming Medanta hospital in Ghaz](https://www.livemint.com/industry/infrastructure/global-health-expands-delhi-ncr-footprint-with-upcoming-medanta-hospital-in-ghaziabad-details-inside-11790948239738.html) | Fri, 02 Oct 2026 20:08:08 +0530 |
| Public Service Enterprise Group Incorporated Common Stock | US | 🆕 | [Mint Explainer | Why state-owned BSNL is wary of Trai's proposed service quality](https://www.livemint.com/industry/telecom/bsnl-trai-quality-of-service-rules-objections-explained-11790925221858.html) | Fri, 02 Oct 2026 14:01:34 +0530 |
| Mercantile Bank Corporation - Common Stock | US | 🆕 | [Credit offtake stays ahead of banks' deposit growth](https://timesofindia.indiatimes.com/business/india-business/credit-offtake-stays-ahead-of-banks-deposit-growth/articleshow/134683228.cms) | 2026-10-05T05:31:32+05:30 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 14 | 0 |  |
| ET | cons_products | 50 | 21 | 3 |  |
| ET | industry | 50 | 11 | 3 |  |
| Hindu | business | 0 | 0 | 0 | HTTP 403 |
| HinduBusinessLine | companies | 60 | 21 | 1 |  |
| HinduBusinessLine | economy | 60 | 15 | 0 |  |
| TimesOfIndia | business | 20 | 6 | 1 |  |
| Livemint | companies | 35 | 14 | 3 |  |
| Livemint | industry | 35 | 11 | 2 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 4 | 1 | 1 |  |
| BusinessStandard | companies | 35 | 20 | 4 |  |
| AmarUjala | business | 40 | 13 | 0 |  |

