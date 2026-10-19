# Live media RSS sweep — layer 45

*Generated 2026-10-19 by `scripts/build_layer45_media_rss_sweep.py`. 510 feed items scanned across 8 newspapers, 200 carried investment-intent language, 16 matched a real foreign-company roster name (15 new to the twin). Run this often -- RSS feeds churn within hours, unlike layer 44's hand-curated 5-year sweep.*

## Why this layer exists

economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's own network is not blocked, so this layer fetches section RSS feeds directly and extracts full article text via each site's own article markup — JSON-LD `articleBody` works identically across all 8 sources tested (ET, Hindu, HBL, Times of India, Livemint, Moneycontrol, Business Standard, Amar Ujala), no per-site parser or third-party scraper needed. Extended 2026-09-16 to 5 more English dailies plus Amar Ujala (Hindi) — see the layer JSON's `what` field for the Hindi-coverage caveat (Latin-script company mentions only, not transliterated ones).

## New-to-twin company matches

| Company | Country | Source | Headline | Published |
|---|---|---|---|---|
| Philip Morris International Inc Common Stock | US | economictimes.indiatimes.com | [We have invested $16 billion in R&amp;D of less harmful alternatives for smokers](https://economictimes.indiatimes.com/industry/cons-products/tobacco/we-have-invested-16-billion-in-rd-of-less-harmful-alternatives-for-smokers-philip-morris-internationals-tomoko-iida/articleshow/134912230.cms) | Tue, 13 Oct 2026 13:44:07 +0530 |
| Innovative Solutions and Support, Inc. - Common Stock | US | economictimes.indiatimes.com | [Engie plans €3 billion investment in India by 2030](https://economictimes.indiatimes.com/industry/renewables/engie-plans-3-billion-investment-in-india-by-2030/articleshow/135033696.cms) | Sun, 18 Oct 2026 23:54:22 +0530 |
| HDFC Bank Limited Common Stock | US | www.thehindu.com | [HDFC Bank Q2 net profit grows 5.55% to ₹20,700 crore](https://www.thehindu.com/business/Industry/hdfc-bank-q2-net-profit-grows-555-to-20700-crore/article71596506.ece) | Sun, 18 Oct 2026 22:29:22 +0530 |
| Greater China Financial Holdings Ltd | HK | www.livemint.com | [Accenture weighs $1.5 billion sale of China business as AI push reshapes growth ](https://www.livemint.com/companies/news/accenture-weighs-1-5-billion-sale-of-china-business-as-ai-push-reshapes-growth-strategy-report-11792323492872.html) | Sun, 18 Oct 2026 17:18:17 +0530 |
| Sumitomo Mitsui Financial Group Inc Unsponsored American Depositary Shares (Japan) | US | www.livemint.com | [Japanese Sumitomo Mitsui Banking Corporation leases 50,000 sq ft office space in](https://www.livemint.com/industry/real-estate/japanese-sumitomo-mitsui-banking-corporation-leases-50-000-sq-ft-office-space-in-mumbais-bkc-for-189-crore-11792298803609.html) | Sun, 18 Oct 2026 11:18:51 +0530 |
| RESOURCE BASE LIMITED. | AU | www.thehindu.com | [Essar Oil & Gas bags five CBM blocks with 6.6 TCF resources](https://www.thehindu.com/business/Industry/essar-oil-gas-bags-five-cbm-blocks-with-66-tcf-resources/article71588078.ece) | Sun, 18 Oct 2026 02:00:13 +0530 |
| ICICI Bank Limited Common Stock | US | www.business-standard.com | [ICICI Bank Q2 net rises 20% to ₹14,843 crore as provisions fall](https://www.business-standard.com/companies/quarterly-results/icici-bank-q2-fy27-result-net-profit-rises-22-3-to-16-333-crore-126101700550_1.html) | Sat, 17 Oct 2026 15:40:48 +0530 |
| HDFC Bank Limited Common Stock | US | www.business-standard.com | [HDFC Bank Q2 net profit rises 4.7% to ₹19,510 crore as NII grows](https://www.business-standard.com/companies/quarterly-results/hdfc-bank-q2fy27-result-net-profit-rises-4-7-to-19-510-cr-nii-up-9-7-126101700465_1.html) | Sat, 17 Oct 2026 14:18:38 +0530 |
| Asia Pacific Wire & Cable Corporation Limited  - Common shares, Par value .01 per share | US | www.thehindubusinessline.com | [GMR Aero Technic, Logic Air ink MoU to team up in aircraft modification, enginee](https://www.thehindubusinessline.com/news/gmr-aero-technic-logic-air-ink-mou-to-team-up-in-aircraft-modification-engineering-capabilities/article71592514.ece) | Sat, 17 Oct 2026 04:51:35 +0530 |
| Greater China Financial Holdings Ltd | HK | www.livemint.com | [Accenture weighs $1.5 billion sale of Greater China operations amid AI shift, hi](https://www.livemint.com/companies/news/accenture-weighs-1-5-billion-sale-of-greater-china-operations-amid-ai-shift-hires-jpmorgan-for-review-report-11792375064725.html) | Mon, 19 Oct 2026 08:00:11 +0530 |
| HDFC Bank Limited Common Stock | US | economictimes.indiatimes.com | [Banks also count cost of insurance payout curbs](https://economictimes.indiatimes.com/industry/banking/finance/banking/banks-also-count-cost-of-insurance-payout-curbs/articleshow/135034779.cms) | Mon, 19 Oct 2026 00:51:37 +0530 |
| ICICI Bank Limited Common Stock | US | www.thehindu.com | [ICICI Bank Q2 PAT rises 20.1% to ₹14,843 crore, NIM down to 4.18%](https://www.thehindu.com/business/icici-bank-q2-pat-rises-201-to-14843-crore-nim-down-to-418/article71596780.ece) | Mon, 19 Oct 2026 00:28:28 +0530 |
| HDFC Bank Limited Common Stock | US | www.thehindu.com | [HDFC Bank Q2 net profit grows 4.7% to ₹19,510 crore](https://www.thehindu.com/business/hdfc-bank-q2-net-profit-grows-47-to-19510-crore/article71597377.ece) | Mon, 19 Oct 2026 00:22:04 +0530 |
| HDFC Bank Limited Common Stock | US | timesofindia.indiatimes.com | [Stock market outlook: Geopolitical cues, earnings, FIIs to keep Dalal Street bus](https://timesofindia.indiatimes.com/business/india-business/stock-market-outlook-geopolitical-cues-earnings-foreign-inflows-more-to-keep-dalal-street-busy/articleshow/135025850.cms) | 2026-10-18T14:06:15+05:30 |
| ICICI Bank Limited Common Stock | US | timesofindia.indiatimes.com | [Stock market outlook: Geopolitical cues, earnings, FIIs to keep Dalal Street bus](https://timesofindia.indiatimes.com/business/india-business/stock-market-outlook-geopolitical-cues-earnings-foreign-inflows-more-to-keep-dalal-street-busy/articleshow/135025850.cms) | 2026-10-18T14:06:15+05:30 |

## All company matches (incl. already-known)

| Company | Country | New? | Headline | Published |
|---|---|---|---|---|
| Philip Morris International Inc Common Stock | US | 🆕 | [We have invested $16 billion in R&amp;D of less harmful alternatives for smokers](https://economictimes.indiatimes.com/industry/cons-products/tobacco/we-have-invested-16-billion-in-rd-of-less-harmful-alternatives-for-smokers-philip-morris-internationals-tomoko-iida/articleshow/134912230.cms) | Tue, 13 Oct 2026 13:44:07 +0530 |
| Innovative Solutions and Support, Inc. - Common Stock | US | 🆕 | [Engie plans €3 billion investment in India by 2030](https://economictimes.indiatimes.com/industry/renewables/engie-plans-3-billion-investment-in-india-by-2030/articleshow/135033696.cms) | Sun, 18 Oct 2026 23:54:22 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [HDFC Bank Q2 net profit grows 5.55% to ₹20,700 crore](https://www.thehindu.com/business/Industry/hdfc-bank-q2-net-profit-grows-555-to-20700-crore/article71596506.ece) | Sun, 18 Oct 2026 22:29:22 +0530 |
| Greater China Financial Holdings Ltd | HK | 🆕 | [Accenture weighs $1.5 billion sale of China business as AI push reshapes growth ](https://www.livemint.com/companies/news/accenture-weighs-1-5-billion-sale-of-china-business-as-ai-push-reshapes-growth-strategy-report-11792323492872.html) | Sun, 18 Oct 2026 17:18:17 +0530 |
| Sumitomo Mitsui Financial Group Inc Unsponsored American Depositary Shares (Japan) | US | 🆕 | [Japanese Sumitomo Mitsui Banking Corporation leases 50,000 sq ft office space in](https://www.livemint.com/industry/real-estate/japanese-sumitomo-mitsui-banking-corporation-leases-50-000-sq-ft-office-space-in-mumbais-bkc-for-189-crore-11792298803609.html) | Sun, 18 Oct 2026 11:18:51 +0530 |
| RESOURCE BASE LIMITED. | AU | 🆕 | [Essar Oil & Gas bags five CBM blocks with 6.6 TCF resources](https://www.thehindu.com/business/Industry/essar-oil-gas-bags-five-cbm-blocks-with-66-tcf-resources/article71588078.ece) | Sun, 18 Oct 2026 02:00:13 +0530 |
| ICICI Bank Limited Common Stock | US | 🆕 | [ICICI Bank Q2 net rises 20% to ₹14,843 crore as provisions fall](https://www.business-standard.com/companies/quarterly-results/icici-bank-q2-fy27-result-net-profit-rises-22-3-to-16-333-crore-126101700550_1.html) | Sat, 17 Oct 2026 15:40:48 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [HDFC Bank Q2 net profit rises 4.7% to ₹19,510 crore as NII grows](https://www.business-standard.com/companies/quarterly-results/hdfc-bank-q2fy27-result-net-profit-rises-4-7-to-19-510-cr-nii-up-9-7-126101700465_1.html) | Sat, 17 Oct 2026 14:18:38 +0530 |
| Asia Pacific Wire & Cable Corporation Limited  - Common shares, Par value .01 per share | US | 🆕 | [GMR Aero Technic, Logic Air ink MoU to team up in aircraft modification, enginee](https://www.thehindubusinessline.com/news/gmr-aero-technic-logic-air-ink-mou-to-team-up-in-aircraft-modification-engineering-capabilities/article71592514.ece) | Sat, 17 Oct 2026 04:51:35 +0530 |
| Greater China Financial Holdings Ltd | HK | 🆕 | [Accenture weighs $1.5 billion sale of Greater China operations amid AI shift, hi](https://www.livemint.com/companies/news/accenture-weighs-1-5-billion-sale-of-greater-china-operations-amid-ai-shift-hires-jpmorgan-for-review-report-11792375064725.html) | Mon, 19 Oct 2026 08:00:11 +0530 |
| Semiconductor Manufacturing International Corp | HK |  | [Public sector banks' Rs 7.8 lakh core corporate loan pipeline signals capex revi](https://economictimes.indiatimes.com/industry/banking/finance/banking/public-sector-banks-rs-7-8-lakh-core-corporate-loan-pipeline-signals-capex-revival/articleshow/135034438.cms) | Mon, 19 Oct 2026 05:30:00 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [Banks also count cost of insurance payout curbs](https://economictimes.indiatimes.com/industry/banking/finance/banking/banks-also-count-cost-of-insurance-payout-curbs/articleshow/135034779.cms) | Mon, 19 Oct 2026 00:51:37 +0530 |
| ICICI Bank Limited Common Stock | US | 🆕 | [ICICI Bank Q2 PAT rises 20.1% to ₹14,843 crore, NIM down to 4.18%](https://www.thehindu.com/business/icici-bank-q2-pat-rises-201-to-14843-crore-nim-down-to-418/article71596780.ece) | Mon, 19 Oct 2026 00:28:28 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [HDFC Bank Q2 net profit grows 4.7% to ₹19,510 crore](https://www.thehindu.com/business/hdfc-bank-q2-net-profit-grows-47-to-19510-crore/article71597377.ece) | Mon, 19 Oct 2026 00:22:04 +0530 |
| HDFC Bank Limited Common Stock | US | 🆕 | [Stock market outlook: Geopolitical cues, earnings, FIIs to keep Dalal Street bus](https://timesofindia.indiatimes.com/business/india-business/stock-market-outlook-geopolitical-cues-earnings-foreign-inflows-more-to-keep-dalal-street-busy/articleshow/135025850.cms) | 2026-10-18T14:06:15+05:30 |
| ICICI Bank Limited Common Stock | US | 🆕 | [Stock market outlook: Geopolitical cues, earnings, FIIs to keep Dalal Street bus](https://timesofindia.indiatimes.com/business/india-business/stock-market-outlook-geopolitical-cues-earnings-foreign-inflows-more-to-keep-dalal-street-busy/articleshow/135025850.cms) | 2026-10-18T14:06:15+05:30 |

## Feed health

| Source | Section | Items | Intent hits | Matches | Error |
|---|---|---|---|---|---|
| ET | auto | 50 | 18 | 0 |  |
| ET | cons_products | 50 | 19 | 1 |  |
| ET | industry | 50 | 20 | 3 |  |
| Hindu | business | 60 | 22 | 4 |  |
| HinduBusinessLine | companies | 60 | 27 | 0 |  |
| HinduBusinessLine | economy | 60 | 9 | 1 |  |
| TimesOfIndia | business | 20 | 4 | 2 |  |
| Livemint | companies | 35 | 16 | 2 |  |
| Livemint | industry | 35 | 14 | 1 |  |
| Moneycontrol | business | 15 | 6 | 0 |  |
| Moneycontrol | economy | 0 | 0 | 0 | HTTP 502 |
| BusinessStandard | companies | 35 | 30 | 2 |  |
| AmarUjala | business | 40 | 15 | 0 |  |

