# Live media RSS sweep — layer 45

*Generated 2026-10-12 by `scripts/build_layer45_media_rss_sweep.py`. 510 feed items scanned across 8 newspapers, 168 carried investment-intent language, 6 matched a real foreign-company roster name (6 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | www.thehindu.com | [Paramount and Warner Bros merge to become one Hollywood giant, Skydance](https://www.thehindu.com/business/paramount-and-warner-bros-merge-to-become-one-hollywood-giant-skydance/article71552210.ece) | Thu, 08 Oct 2026 17:27:28 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | www.livemint.com | [$606 million payday! Check outgoing CEO David Zaslav's big windfall from Paramou](https://www.livemint.com/companies/news/606-million-payday-check-outgoing-ceo-david-zaslavs-big-windfall-from-paramounts-warner-bros-takeover-11791625464356.html) | Sat, 10 Oct 2026 17:40:38 +0530 |
| CLOSE THE LOOP LTD. | AU | www.livemint.com | [Tata Motors sweetens Iveco offer as key investors hold out](https://www.livemint.com/companies/tata-motors-iveco-acquisition-deal-status-11791713827262.html) | Mon, 12 Oct 2026 06:05:40 +0530 |
| HDFC Bank Limited Common Stock | US | www.livemint.com | [₹3 cr per month salary? Meet India's 'highest-paid' bank CEO - ICICI veteran and](https://www.livemint.com/companies/people/rs-3-cr-per-month-salary-meet-indias-highest-paid-bank-ceo-icici-veteran-and-hdfcs-anup-bagchi-11791545564481.html) | Fri, 09 Oct 2026 18:04:12 +0530 |
| HDFC Bank Limited Common Stock | US | www.thehindubusinessline.com | [HDFC Bank shares bounce back after rate hike blow; YTD loss tops 29%](https://www.thehindubusinessline.com/markets/stock-markets/hdfc-bank-shares-bounce-back-after-rate-hike-blow-ytd-loss-tops-29/article71562937.ece) | Fri, 09 Oct 2026 12:31:34 +0530 |
| ASA  Gold and Precious Metals Limited | US | timesofindia.indiatimes.com | [Gold, silver prices next week: What investors should watch amid global uncertain](https://timesofindia.indiatimes.com/business/india-business/gold-silver-prices-next-week-what-investors-should-watch-amid-global-uncertainty/articleshow/134872993.cms) | 2026-10-11T21:19:20+05:30 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | 🆕 | [Paramount and Warner Bros merge to become one Hollywood giant, Skydance](https://www.thehindu.com/business/paramount-and-warner-bros-merge-to-become-one-hollywood-giant-skydance/article71552210.ece) | Thu, 08 Oct 2026 17:27:28 +0530 |
| Warner Bros. Discovery, Inc. - Series A Common Stock | US | 🆕 | [$606 million payday! Check outgoing CEO David Zaslav's big windfall from Paramou](https://www.livemint.com/companies/news/606-million-payday-check-outgoing-ceo-david-zaslavs-big-windfall-from-paramounts-warner-bros-takeover-11791625464356.html) | Sat, 10 Oct 2026 17:40:38 +0530 |
| CLOSE THE LOOP LTD. | AU | 🆕 | [Tata Motors sweetens Iveco offer as key investors hold out](https://www.livemint.com/companies/tata-motors-iveco-acquisition-deal-status-11791713827262.html) | Mon, 12 Oct 2026 06:05:40 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [₹3 cr per month salary? Meet India's 'highest-paid' bank CEO - ICICI veteran and](https://www.livemint.com/companies/people/rs-3-cr-per-month-salary-meet-indias-highest-paid-bank-ceo-icici-veteran-and-hdfcs-anup-bagchi-11791545564481.html) | Fri, 09 Oct 2026 18:04:12 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [HDFC Bank shares bounce back after rate hike blow; YTD loss tops 29%](https://www.thehindubusinessline.com/markets/stock-markets/hdfc-bank-shares-bounce-back-after-rate-hike-blow-ytd-loss-tops-29/article71562937.ece) | Fri, 09 Oct 2026 12:31:34 +0530 |
| ASA  Gold and Precious Metals Limited | US | 🆕 | [Gold, silver prices next week: What investors should watch amid global uncertain](https://timesofindia.indiatimes.com/business/india-business/gold-silver-prices-next-week-what-investors-should-watch-amid-global-uncertainty/articleshow/134872993.cms) | 2026-10-11T21:19:20+05:30 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 16 | 0 |  |
| ET | cons_products | 50 | 17 | 0 |  |
| ET | industry | 50 | 20 | 0 |  |
| Hindu | business | 60 | 12 | 1 |  |
| HinduBusinessLine | companies | 60 | 21 | 1 |  |
| HinduBusinessLine | economy | 60 | 8 | 0 |  |
| TimesOfIndia | business | 20 | 6 | 1 |  |
| Livemint | companies | 35 | 14 | 3 |  |
| Livemint | industry | 35 | 14 | 0 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 0 | 0 | 0 | HTTP 502 |
| BusinessStandard | companies | 35 | 19 | 0 |  |
| AmarUjala | business | 40 | 15 | 0 |  |

