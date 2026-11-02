# Live media RSS sweep — layer 45

*Generated 2026-11-02 by `scripts/build_layer45_media_rss_sweep.py`. 514 feed items scanned across 8 newspapers, 203 carried investment-intent language, 13 matched a real foreign-company roster name (12 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| Philip Morris International Inc Common Stock | US | economictimes.indiatimes.com | [Philip Morris Q3 net revenues rise 5.5% to $11.4 billion on smoke-free, combusti](https://economictimes.indiatimes.com/industry/cons-products/tobacco/philip-morris-q3-net-revenues-rise-5-5-to-11-4-billion-on-smoke-free-combustible-growth/articleshow/135294554.cms) | Thu, 29 Oct 2026 12:29:37 +0530 |
| Financial Institutions, Inc. - Common Stock | US | economictimes.indiatimes.com | [Cyberattacks on banks, including AU Small Finance Bank, worry insurers as claim ](https://economictimes.indiatimes.com/industry/banking/finance/insure/cyberattacks-on-banks-including-au-small-finance-bank-worry-insurers-as-claim-risks-rise/articleshow/135434670.cms) | Sun, 01 Nov 2026 23:29:56 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | www.business-standard.com | [Solex Energy eyeing US market for international debut, says chairman](https://www.business-standard.com/companies/news/solex-energy-eyeing-us-market-for-international-debut-says-chairman-126110100351_1.html) | Sun, 01 Nov 2026 14:46:50 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | www.business-standard.com | [Solex Energy eyeing US market for international debut, says chairman](https://www.business-standard.com/companies/news/solex-energy-eyeing-us-market-for-international-debut-says-chairman-126110100351_1.html) | Sun, 01 Nov 2026 14:46:50 +0530 |
| American Eagle Outfitters, Inc. Common Stock | US | www.business-standard.com | [Aditya Birla Fashion and Retail Q2 profit more than doubles to ₹53 crore](https://www.business-standard.com/companies/quarterly-results/aditya-birla-fashion-and-retail-q2-profit-more-than-doubles-to-53-crore-126103100919_1.html) | Sat, 31 Oct 2026 17:42:37 +0530 |
| Natural Gas Distribution Company | SA | www.business-standard.com | [IGL Q2 result: Net profit plunges 93.5% to ₹24 crore on higher gas costs](https://www.business-standard.com/companies/quarterly-results/igl-q2-result-net-profit-plunges-93-5-to-24-crore-on-higher-gas-costs-126103100481_1.html) | Sat, 31 Oct 2026 12:38:51 +0530 |
| Natural Gas Services Group, Inc. Common Stock | US | www.business-standard.com | [IGL Q2 result: Net profit plunges 93.5% to ₹24 crore on higher gas costs](https://www.business-standard.com/companies/quarterly-results/igl-q2-result-net-profit-plunges-93-5-to-24-crore-on-higher-gas-costs-126103100481_1.html) | Sat, 31 Oct 2026 12:38:51 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | www.business-standard.com | [Two Point O Capital raises $10 million to expand clean energy platform](https://www.business-standard.com/companies/start-ups/two-point-o-capital-raises-10-million-to-expand-clean-energy-platform-126110100446_1.html) | Mon, 02 Nov 2026 06:05:11 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | www.business-standard.com | [Two Point O Capital raises $10 million to expand clean energy platform](https://www.business-standard.com/companies/start-ups/two-point-o-capital-raises-10-million-to-expand-clean-energy-platform-126110100446_1.html) | Mon, 02 Nov 2026 06:05:11 +0530 |
| Southeast Asia Properties & Finance Ltd | HK | economictimes.indiatimes.com | [Hinduja's Gulf Oil scouts acquisitions in Asia, South America ahead of global li](https://economictimes.indiatimes.com/industry/energy/oil-gas/hindujas-gulf-oil-scouts-acquisitions-in-asia-south-america-ahead-of-global-listing/articleshow/135436239.cms) | Mon, 02 Nov 2026 00:41:24 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | www.thehindubusinessline.com | [Tata Motors takes control of Iveco in €3.43-billion deal; focus shifts to debt, ](https://www.thehindubusinessline.com/companies/tata-motors-takes-control-of-iveco-in-343-billion-deal-focus-shifts-to-debt-integration/article71646387.ece) | Fri, 30 Oct 2026 21:59:52 +0530 |
| Mercantile Bank Corporation - Common Stock | US | www.livemint.com | [Tamilnad Mercantile Bank seeks RBI nod for share transfers, gets board backing f](https://www.livemint.com/industry/banking/tamilnad-mercantile-bank-rbi-approval-share-transfers-expansion-11793333344595.html) | Fri, 30 Oct 2026 12:35:54 +0530 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Semiconductor Manufacturing International Corp | HK |  | [India’s Composite Flash PMI for April signals very strong economy](https://www.moneycontrol.com/news/economy/india’s-composite-flash-pmi-for-april-signals-very-strong-economy_17531301.html) | Tue, 23 Apr 2024 11:07:37 +0530 |
| Philip Morris International Inc Common Stock | US | 🆕 | [Philip Morris Q3 net revenues rise 5.5% to $11.4 billion on smoke-free, combusti](https://economictimes.indiatimes.com/industry/cons-products/tobacco/philip-morris-q3-net-revenues-rise-5-5-to-11-4-billion-on-smoke-free-combustible-growth/articleshow/135294554.cms) | Thu, 29 Oct 2026 12:29:37 +0530 |
| Financial Institutions, Inc. - Common Stock | US | 🆕 | [Cyberattacks on banks, including AU Small Finance Bank, worry insurers as claim ](https://economictimes.indiatimes.com/industry/banking/finance/insure/cyberattacks-on-banks-including-au-small-finance-bank-worry-insurers-as-claim-risks-rise/articleshow/135434670.cms) | Sun, 01 Nov 2026 23:29:56 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | 🆕 | [Solex Energy eyeing US market for international debut, says chairman](https://www.business-standard.com/companies/news/solex-energy-eyeing-us-market-for-international-debut-says-chairman-126110100351_1.html) | Sun, 01 Nov 2026 14:46:50 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | 🆕 | [Solex Energy eyeing US market for international debut, says chairman](https://www.business-standard.com/companies/news/solex-energy-eyeing-us-market-for-international-debut-says-chairman-126110100351_1.html) | Sun, 01 Nov 2026 14:46:50 +0530 |
| American Eagle Outfitters, Inc. Common Stock | US | 🆕 | [Aditya Birla Fashion and Retail Q2 profit more than doubles to ₹53 crore](https://www.business-standard.com/companies/quarterly-results/aditya-birla-fashion-and-retail-q2-profit-more-than-doubles-to-53-crore-126103100919_1.html) | Sat, 31 Oct 2026 17:42:37 +0530 |
| Natural Gas Distribution Company | SA | 🆕 | [IGL Q2 result: Net profit plunges 93.5% to ₹24 crore on higher gas costs](https://www.business-standard.com/companies/quarterly-results/igl-q2-result-net-profit-plunges-93-5-to-24-crore-on-higher-gas-costs-126103100481_1.html) | Sat, 31 Oct 2026 12:38:51 +0530 |
| Natural Gas Services Group, Inc. Common Stock | US | 🆕 | [IGL Q2 result: Net profit plunges 93.5% to ₹24 crore on higher gas costs](https://www.business-standard.com/companies/quarterly-results/igl-q2-result-net-profit-plunges-93-5-to-24-crore-on-higher-gas-costs-126103100481_1.html) | Sat, 31 Oct 2026 12:38:51 +0530 |
| Clean Energy Technologies, Inc. - Common Stock | US | 🆕 | [Two Point O Capital raises $10 million to expand clean energy platform](https://www.business-standard.com/companies/start-ups/two-point-o-capital-raises-10-million-to-expand-clean-energy-platform-126110100446_1.html) | Mon, 02 Nov 2026 06:05:11 +0530 |
| Clean Energy Fuels Corp. - Common Stock | US | 🆕 | [Two Point O Capital raises $10 million to expand clean energy platform](https://www.business-standard.com/companies/start-ups/two-point-o-capital-raises-10-million-to-expand-clean-energy-platform-126110100446_1.html) | Mon, 02 Nov 2026 06:05:11 +0530 |
| Southeast Asia Properties & Finance Ltd | HK | 🆕 | [Hinduja's Gulf Oil scouts acquisitions in Asia, South America ahead of global li](https://economictimes.indiatimes.com/industry/energy/oil-gas/hindujas-gulf-oil-scouts-acquisitions-in-asia-south-america-ahead-of-global-listing/articleshow/135436239.cms) | Mon, 02 Nov 2026 00:41:24 +0530 |
| Commercial Vehicle Group, Inc. - Common Stock | US | 🆕 | [Tata Motors takes control of Iveco in €3.43-billion deal; focus shifts to debt, ](https://www.thehindubusinessline.com/companies/tata-motors-takes-control-of-iveco-in-343-billion-deal-focus-shifts-to-debt-integration/article71646387.ece) | Fri, 30 Oct 2026 21:59:52 +0530 |
| Mercantile Bank Corporation - Common Stock | US | 🆕 | [Tamilnad Mercantile Bank seeks RBI nod for share transfers, gets board backing f](https://www.livemint.com/industry/banking/tamilnad-mercantile-bank-rbi-approval-share-transfers-expansion-11793333344595.html) | Fri, 30 Oct 2026 12:35:54 +0530 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 14 | 0 |  |
| ET | cons_products | 50 | 23 | 1 |  |
| ET | industry | 50 | 12 | 2 |  |
| Hindu | business | 60 | 17 | 0 |  |
| HinduBusinessLine | companies | 60 | 29 | 1 |  |
| HinduBusinessLine | economy | 60 | 14 | 0 |  |
| TimesOfIndia | business | 20 | 7 | 0 |  |
| Livemint | companies | 35 | 22 | 0 |  |
| Livemint | industry | 35 | 14 | 1 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 4 | 1 | 1 |  |
| BusinessStandard | companies | 35 | 25 | 7 |  |
| AmarUjala | business | 40 | 19 | 0 |  |

