# digital-twin-for-ipa

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/herrrickshaw/digital-twin-for-ipa/blob/main/notebooks/twin_quickstart.ipynb)

A machine-readable **digital twin of India's Investment Promotion Apparatus** — the full set of central-government entities, the incentive instruments each one actually offers companies, how the instruments interlink (stack / exclude / converge / feed), what the budget record says about delivery, and how an investor navigates the system.

Every layer is a JSON file. Every claim is tagged with how it was verified (`verified_on_site`, PIB PRIDs, portal URLs) and access failures are recorded as data, not skipped.

## Layers

| Layer | File | Contents |
|---|---|---|
| 01 | `layers/01_ministries_master.json` | All **86 entities** in the PIB register (2017–2026, 122,141 releases) with per-entity sweep verdicts: HAS-INCENTIVES / THIN / N/A / SUPERSEDED |
| 02 | `layers/02_incentive_catalog_v1.json` | Catalog v1 — the 16 heavyweight ministries, site-verified (DPIIT, MeitY, Heavy Industries, Textiles, Steel, MNRE, MoPNG, Coal, Mines, Pharma, FPI, MSME, Commerce, DoT, Fisheries/AHD, Ports) |
| 03 | `layers/03_scheme_registry.json` | Scheme registry: launch dates, application windows, applicant counts, closures (displayed corrections, never silent) |
| 04 | `layers/04_investor_workflow.json` | The investor path: sector → scheme → NSWS → ministry connect → sanction (8 steps) |
| 05 | `layers/05_decade_report_card.json` | 2014–2026 graded: which instrument designs paid, open windows, ministries to approach |
| 06 | `layers/06_investor_map.json` | Global company pools per incentivized sector (19,795 companies, 107 countries) |
| 07 | `layers/07_investor_pairings.json` | Foreign investors ↔ initiatives, PRID-cited; stalled cases retained |
| 08 | `layers/08_refresh_blueprint.json` | Quarterly refresh blueprint (TOGAF layers × modern data architecture) |
| 09 | `layers/09_catalog_v2/` | **Catalog v2 — the full-government sweep** (the other 70 entities), one cluster file per agent sweep |
| 10 | `layers/10_interlinkages.json` | **Scheme interlinkage graph**: 23 edges (stacks / excludes / boundary / feeds / converges) + 11 clarity checks against explainer sources. Anchor: MeitY PLI FAQ Clause 3.6 (the legal basis for PLI + state stacking) |
| 11 | `layers/11_prs_budget_layer.json` | **PRS Legislative Research overlay**: Demand-for-Grants utilization findings (12 ministries), 22-bill legislative track, and PRS's own coverage gaps |
| 12 | `layers/12_state_catalog/` | **State catalog** — state-government incentive schemes verified on state single-window / industries-department sites, one cluster file per sweep |
| 00 | `layers/00_data_model.json` | **Canonical data model** — nine entity types every sweep maps into (Instrument, ApplicationWindow, InterlinkageEdge, SourceRoute…) |
| 13 | `layers/13_flat_instrument_index.json` | **Flat instrument index** — all 312 instruments (195 central + 117 state) normalized to one schema |
| 14 | `layers/14_update_engine.json` | **Auto-update engine** — per-source refresh design (PIB daily, NSWS/RBI/UNNATI weekly, quarterly sweeps; Orbis-upgrade path for company data). Flow diagram: [docs/DATA_MODEL.md](docs/DATA_MODEL.md) |
| 15 | `layers/15_directory.json` | **Portal directory** — 64 verified portals (27 central + 37 state) + 12 known-bad domains; human version: [docs/DIRECTORY.md](docs/DIRECTORY.md) |
| 17 | `layers/17_scheme_monitor.json` | **Scheme performance monitor** — per-scheme schema mapped to the owning ministry: funds allocated/disbursed, utilization, applicants, window, **arrears**, refresh source (15 central schemes seeded) |
| 18 | `layers/18_state_monitor.json` | **State incentive monitor** — 15 states' status + funds evidence from public records (disbursals vs approvals vs MoUs; the arrears divide: TG/AP/PB/J&K vs MP/RJ; transparency divide: RJ/GJ publish, MH/KA don't) |
| 16 | `layers/16_leads.json` | **Leads generation** — **263 leads across 26 countries**: 147 yfinance-verified-profitable US/India firms (US leads carry SEC 10-K India/APAC mention-mining with YoY trend) + 116 annual-report deep-dive leads from 19 more countries (JP/KR/CN/UK/AU + DACH/NL, France/South-EU/Nordics, TW/HK/SG, CA/BR/ZA/Saudi/Israel) with quoted evidence, yfinance tickers, and per-region policy context (PN3, TEPA, SHANTI, ECTA); view: [docs/LEADS.md](docs/LEADS.md). Companion: [docs/PLI_SCHEME_BENEFICIARY_LEADS.md](docs/PLI_SCHEME_BENEFICIARY_LEADS.md) — hand-researched government-approval evidence (9 schemes, Parliament Q&A + PIB sourced) for the *other* half of the picture this layer's disclosure-mining structurally can't see: companies approved for scheme money without ever saying so in a filing, and schemes with zero current participants. [docs/INTEGRATED_TARGET_DECISION.md](docs/INTEGRATED_TARGET_DECISION.md) cross-references the two by hand into a tiered target list. |
| 25 | `layers/25_land_incentive_linkages.json` | **Land availability × open incentives (cross-repo linkage)** — joins the twin's scheme monitor with industrial-land data from sibling repos: the two operational facts an investor needs — WHERE developed land is vacant (IILB 37-state, 125,602 vacant plots) and WHICH windows are open right now (10 open central incentives). Built by `scripts/build_layer25_linkages.py` |
| 26 | `layers/26_project_pipeline.json` | **Investment-project pipeline — IIG / NIP + PM Gati Shakti** — the actual government-listed projects an investor can enter, from the [India Investment Grid](https://www.indiainvestmentgrid.gov.in) (public window onto the National Infrastructure Pipeline, the set PM Gati Shakti coordinates): **12,385 NIP opportunities across 42 sectors** + flagship projects (live), each sector mapped to its twin incentive lane. Built by `scripts/build_layer26_projects.py` |
| 27 | `layers/27_entry_facilitators.json` | **Market-entry facilitators in India** — the trade-promotion agencies & bilateral chambers that host events and B2B matchmaking to bring foreign firms into India, plus the **Indian apex industry bodies** (FICCI, CII, NASSCOM, ASSOCHAM) that co-host them (**31 bodies, 21 countries**): GTAI + Indo-German Chamber (AHK/IGCC), Swissnex + S-GE, UKIBC, JETRO, KOTRA, Business France + IFCCI, ITA/ICE, USIBC + AMCHAM, EBTC and more. 11 verified events calendars; URLs liveness-checked on build. Built by `scripts/build_layer27_entry_facilitators.py` |
| 28 | `layers/28_policy_watchlist.json` | **Policy watchlist — policies in discussion / in the pipeline** — the forward-looking counterpart to layer 17: NEW policy drafted, tabled or debated but not yet in force. **962 PRS bills** (live), **33 active investment-relevant bills (2024+)** mapped to twin sectors — Income Tax Bill 2025, Securities Markets Code, IBC & Banking amendments, Draft Electricity Amendment 2025, Nuclear Energy Bill, Indian Ports/Shipping bills, Jan Vishwas, labour codes — plus Drishti IAS policy editorials. Sources: PRS + Drishti IAS (live), Lok Sabha (API), 🔴 Rajya Sabha blocked. Built by `scripts/build_layer28_policy_watchlist.py` |
| 29 | `layers/29_mospi_data_sources.json` | **MoSPI macro-statistics connector** — the official India macro/statistics backdrop the twin lacked: **25 MoSPI datasets** (6 core macro · 6 sector · 13 context), each tagged for investment relevance and linked to the twin layer it informs — NAS (GDP), CPI/WPI (inflation), IIP (industrial output), PLFS (jobs), RBI (external sector), MNRE (renewable capacity), ASI, EC. Documents the official API (`api.mospi.gov.in`) + eSankhyiki portal + MCP-connector 4-step workflow. Built by `scripts/mospi_connector.py` |
| 31 | `layers/31_ipa_source_network.json` | **IPA source network** — the data sources of the investment-promotion world itself: **WAIPA member directory live-scraped on build (138 IPAs, 112 countries** incl. Invest India, Invest Telangana, MIDC; every member website liveness-swept — 107 live), 10 non-WAIPA IPAs covering the top India FDI-source jurisdictions WAIPA misses (SelectUSA, EDB Singapore, NFIA, GTAI, InvestHK, InvesTaiwan…), WAIPA-World Bank IPA survey PDFs, Invest India's scrapeable surfaces (no JSON API — sitemap w/ 41 sector + 36 state pages, static S3 PDF archive, company-announcement tickers, ODOP, winding-down SIRU), **NDAP API access pattern** (`loadqa.ndapapi.com` backend + Origin header; 6,784 datasets; 12 investment-relevant ids), NITI state indices (EPI/III/SDG/FHI/SECI) + GVC reports, and the data.gov.in DPIIT **IEM datasets that work with the public sample key**. Access failures recorded as data (unctad.org 403 — but investmentpolicy.unctad.org works; oecd.org 403). Built by `scripts/build_layer31_ipa_sources.py` |
| 32 | `layers/32_company_db.json` + `data/companies.db` | **Company database** — every company the twin has touched (**1,785 unique**, deduped on normalized-name+country) consolidated from seven layers into one queryable SQLite DB: 321 foreign leads · 136 shortlist targets · 98 clearance leads (82 credit-rated via the layer-24 CARE/CRISIL/ICRA channel) · 1,371 EC-filer pool · alias checks · pairings. `company_sources` keeps every source record verbatim (provenance per row); `company_card` view = one row per company. Built by `scripts/build_company_db.py`. **Enrichment**: `scripts/enrich_company_db_ii_tickers.py` scrapes the Invest India sector-page announcement tickers (439 items across 41 sectors) into `ii_announcements`/`ii_company_matches` and validates the exception cohort — tiered matching (strong challenges verdicts, weak is review-only after 'Reliance Bp Mobility' swallowed Reliance Industries stories and 'Galaxy Dyestuff' matched Samsung Galaxy); first run: 41 companies matched, and Nayara Energy's QUIET-side verdict CHALLENGED — the national IPA itself carries its 400-petrol-pump rollout, corroborating the CARE rationale's DODO buildout |
| 33 | `layers/33_policy_finance_extensions.json` | **Policy-finance extensions** — four analysis blocks with per-claim sources + HTTP-verified access + layer-32 company linkages: **fisheries** (PMMSY ₹21,395 cr approved / PM-MKSSY final year / FIDF 3% subvention, TN largest user / MPEDA record FY26 exports $8.46bn w/ US −19.5% on tariffs → 18% post-deal), **state-excise bottling fees** (4-6-levy fee stack; Rajasthan the only primary-sourced per-BL rate; 🔑 SC *Lalta Prasad Vaish* 9-judge ruling lets states tax industrial alcohol — structural fee-creep risk for the E20 ethanol cohort; Punjab ₹1/BL first mover, MoPNG rollback demand; Maharashtra +50% duty shock), **customs duties** (Feb-2026 posture per sector; steel 12% safeguard stepping to Apr-2028; solar BCD+AIDC; 3 duty×incentive stacks; WITS/ICEGATE-CIP working lookup routes, indiantradeportal 403), **India Exim Bank** (LOC .xlsx links live-scraped each build — 298 LOCs $25.5bn structured; Ubharte Sitaare 106 export champions; EOU 20%-export screen), and **CBG/GOBARdhan FCO fertiliser route** (Schedule VIII "Organic Carbon Enhancer" lets CBG plants sell FOM/LFOM as notified fertiliser — NPK floor cut 5%→1.2%; clause-22(c) bulk-sale notifications I–VII authorise named plants to sell direct to farmers 3 yrs; MDA ₹1,500/MT, 120 plants on iFMS, sales 56k→16.7 lakh MT in 2 yrs; **119 plant-authorisations across notifications I–VII**, Reliance group 12 + Adani + PSUs HPCL/GAIL/NDDB). Built by `scripts/build_layer33_policy_finance.py` |
| 34 | `layers/34_stressed_assets.json` + `stressed_assets` view | **Stressed/distressed assets** — consolidates three previously-scattered sources: (1) company-level rating/litigation distress flags from the layer-32 DB as a `stressed_assets` SQLite view (11 flagged: 4 rating-darkness/issuer-not-cooperating, 2 watch-negative incl. Nayara, 1 downgrade, 1 promoter-litigation regrade RSLD, 3 sub-IG BB+-and-below via a grade parser that excludes upgrades), (2) national distressed-LAND supply channels + 7 named liquidation assets pulled live from the policy-recs repo (IBC 1,436 ongoing liquidations, closed-PSU/NLMC ~3,400 acres, GIDC ~1,800 ha resumed, ARC/SARFAESI), (3) the **Dunlop India** litigation case map (wound-up manufacturer, TN Ambattur 60.86 ac + WB Kings Court 50%, lead judgment 17-Mar-2026). Real registers (IBBI/NLMC/SARFAESI) named with routes. Docs: [docs/STRESSED_ASSETS.md](docs/STRESSED_ASSETS.md). Built by `scripts/build_layer34_stressed_assets.py` |
| 30 | `layers/30_trade_deficit_map.json` | **Trade-deficit & import-substitution map** — links incentives to India's trade deficit: which large import chapters an open incentive actually addresses vs where the deficit is a **policy gap**. From [india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations) — 12 import chapters (Mineral fuels $203bn, Electrical machinery $105bn…), **7 substitutable gaps** (Machinery $74bn, Chemicals, Plastics, Steel, Aircraft), and the concentrated bilateral deficit (China −$112bn). Built by `scripts/build_layer30_trade_deficit.py` |
| 35 | `layers/35_capital_cost_arbitrage_lens.json` | **Capital-cost arbitrage lens** — prioritizes which foreign markets to build NEW discovery sweeps for, using policy-rate gap vs India (25 economies below India's 5.25% repo rate, from the author's own cross-border debt-issuance research) crossed with the twin's existing lead coverage (layer 16) and IPA-source catalog (layer 31). Scope note: the source analysis's CIP-hedging cancellation applies to bond arbitrage, not real capex — kept here as one prioritization signal, not a scored certainty. Top gap found: **Switzerland** (5.25pt rate advantage, 3 leads, no catalogued IPA source). Built by `scripts/build_layer35_capital_cost_lens.py`; doc: [docs/CAPITAL_COST_ARBITRAGE.md](docs/CAPITAL_COST_ARBITRAGE.md) |
| 36 | `layers/36_investment_snapshots.json` | **Investment-announcement snapshots** — curated (not live-fetched) point-in-time company-level data from the two sources, of five investigated, that actually yielded structured data: **UPGIS 2023** (official interim MoU table, top ~12 of 19,058 total by name — Tauschen International HK ₹1,89,849cr, Unicorn Energy Germany ₹41,500cr…) and **The fDi Report 2025** (fDi Intelligence's free annual PDF, fetched off-domain since fdiintelligence.com's robots.txt blocks AI crawlers site-wide — AM/NS India $1.6bn Andhra Pradesh, Powerchip+Tata $11bn Dholera fab). Vibrant Gujarat and Invest Karnataka have no consolidated MOU table (press-release scatter only); access hazards (WAF blocks, a dead repurposed domain) recorded as data. Built by `scripts/build_layer36_investment_snapshots.py`; doc: [docs/INVESTMENT_SNAPSHOTS.md](docs/INVESTMENT_SNAPSHOTS.md) |

## Non-US filing discovery channels (sibling to the EDGAR sweep)

`scripts/build_dart_india_sweep.py` mirrors `build_edgar_india_sweep.py` for Korea's DART disclosure system — but DART has no full-text search API (confirmed live), so it's a list→download→grep sweep of KOSPI/KOSDAQ annual business reports (~953 + ~1,998/year) instead of a search-API query. Regex-filtered to exclude "인도" (India) hits that are actually the unrelated delivery-verb homonym 인도하다. First live test (40 filings) already surfaced a genuine new lead (SJG Sejong / Asentech, India-subsidiary establishment) not previously in the twin. Output: `layers/16_enrichment/dart_india_sweep.json`.

**Japan (EDINET)** — `scripts/build_edinet_india_sweep.py`. 🔴 **Correction (2026-08-09)**: an earlier scouting pass wrongly concluded `EDINET_API_KEY` was invalid/needed re-registration — it only tested a bare `Subscription-Key` HTTP header (which genuinely does 401). The correct auth (`?Subscription-Key=` query param, or the `Ocp-Apim-Subscription-Key` header) works fine, confirmed live by hand (742 real filings for 2026-08-07). EDINET also has no full-text search (list→download→grep, same as DART), but offers a clean CSV export per filing (UTF-16LE) instead of DART's raw XML dump. Same precision hazard as Chinese 印度/印度尼西亚: インド (India) is a substring of インドネシア (Indonesia) — avoided here by searching multi-character compound phrases ("インド市場", "インド進出"…) that don't collide, rather than a separate filter. First live test (60 filings, 5 days): 2 real hits — Pigeon Corp and Suntory Holdings both discussing India market growth/brand strategy. Output: `layers/16_enrichment/edinet_india_sweep.json`.

## China A-share filing sweep (cninfo — real API, but watch-list only)

`scripts/build_cninfo_india_sweep.py` — unlike DART, cninfo.com.cn (China's disclosure system) DOES expose a real keyless full-text search API, confirmed live 2026-08-09 (clone-EDGAR-easy). But it's tokenized/fuzzy, not exact-phrase, so raw hits are dominated by a substring collision: 印度尼西亚 ("Indonesia") starts with 印度 ("India") — a query for "invest in India" returned 19 hits whose top 3 were all Indonesia-only battery/subsidiary announcements (CATL, among others). Every hit is title-filtered to exclude that collision. First real run: **86 genuine India-establishment hits** (56 Indonesia false positives correctly excluded) — e.g. 安琪酵母/Angel Yeast (600298) establishing an India company, 深天马/Tianma (000050) establishing an India subsidiary, 思源电气 (002028) planning an India high-voltage switchgear plant. Full list with sec codes and source PDF links in the output JSON. Per this twin's own Press Note 3 framing (`build_target_leads.py`), these are written to a **watch-list bucket, not actionable outreach targets** — PN3 already routes all Chinese FDI through government approval. Output: `layers/16_enrichment/cninfo_india_sweep.json`.

## Norway + Western Europe filing sweeps

`scripts/build_oslo_newsweb_india_sweep.py` — Oslo Børs NewsWeb (Euronext) has a real no-auth JSON REST API found via network trace, clone-EDGAR-easy: title-search across 2015–2026 returned 158 "India" hits, locally classified into market-entry/investment (9: Orkla India IPO completed, Cambi's Mumbai wastewater contract, HydrogenPro's L&T electrolyser MoU, Scatec's 900MW solar plant agreement…), business-activity (143), and exit/divestment (6, correctly excluded from leads). Output: `layers/16_enrichment/oslo_newsweb_india_sweep.json`.

`scripts/build_esef_xbrl_india_sweep.py` — no UK/France/Italy/Netherlands regulator has a live full-text search yet (UK's FCA National Storage Mechanism is real but "due to go live soon"; Italy/Netherlands native sites are scrape-only; France's info-financiere.gouv.fr searches metadata, not filing text; ESAP isn't public until 2027). The one thing that works across all four: `filings.xbrl.org`, a live, keyless third-party ESEF/UKSEF aggregator with direct report URLs. Built with incremental checkpointing (a lesson from the DART sweep, which only writes at the very end of a run). Full run (300/country, 1,200 filings): **6 real hits** — Haleon plc (GSK's India subsidiary), Prysmian S.p.A. (Chiplun cable plant), Koninklijke Philips (site expansion), Technip Energies (polypropylene plant JV), RHI Magnesita (Bhiwadi refractories plant), Prosus N.V. (BillDesk acquisition, India fintech).

## Switzerland filing sweep (SIX Equity Issuer News — real API, full body text)

`scripts/build_switzerland_india_sweep.py` — Switzerland has no EDGAR/DART/EDINET equivalent (no central regulator with a searchable full-text archive), and is confirmed live (not assumed) to sit outside the ESEF/UKSEF regime — `filings.xbrl.org/api/filings?filter[country]=CH` returns zero. SIX Exchange Regulation's own "Official Notices" tool is real but only covers structured product/Connexor events, no prose. The source that actually works: SIX's "Equity Issuer News" tool, a network-traced, keyless JSON endpoint that — unlike Oslo NewsWeb — returns full press-release body text (not just titles) in up to 4 languages, each item flagged `ad_hoc` (Art. 53) true/false; the whole corpus (1,748 items) fetches in one paginated pass, no per-company IR-site crawl needed. **Step 0, done first**: the sibling [global-stock-screener](https://github.com/herrrickshaw/global-stock-screener) repo's `CH.csv` roster (192 tickers, zero populated names) was checked live against SIX's own authoritative "List of Equity Issuers" API (241 total issuers, 205 Swiss-domiciled) — 15 live issuers were missing, including Roche Holding AG and The Swatch Group AG, not obscure names. Fixed live: `CH.csv` rewritten in place (15 rows added, all 205 matched names backfilled), left uncommitted in the sibling repo; 2 stale tickers (YTME, ZWM) not found live were flagged, not deleted. 🔴 **Three precision hazards found + fixed live (2026-08-12)**: (1) boilerplate — the same company-footprint sentence repeats near-verbatim across a company's press releases (Gurit's "production sites... India..." appears in ~13 releases), collapsed via a punctuation-stripped (company, sentence) fingerprint; (2) context-only — India inside a disease-burden statistics list ("India (25%), Indonesia (10%)...", BioVersys) or a retiring executive's career bio reads as a hit but isn't a company disclosure, excluded; (3) reverse-direction — PIERER Mobility AG's (now Bajaj Mobility AG) filings disclose Bajaj Auto, an *Indian* company, taking control of the Swiss issuer — the opposite of what this sweep mines for, excluded via the EQS major-shareholder notification-obligation pattern. First real run: 93 raw India-mentioning items → 66 unique facts after dedup → **10 market-entry/investment** (Feintool's new Pune plant, Partners Group's Infinity Fincorp acquisition, ABB's $75M manufacturing/R&D expansion, Mikron's new India legal entity, Avolta's Kolkata Airport contract, Swiss Re's new India/Mexico partnerships, CPH Group's Sorbchem India acquisition, WISeKey's Quantum Corridor projects…), **2 exit/divestment** (Landis+Gyr's India real-estate sale, Partners Group's Vishal Mega Mart exit), **48 business-activity**, plus 4 context-only and 2 reverse-direction hits excluded from the counts. Materially changes layer 35's "Switzerland: 3 leads (THIN), no IPA source" baseline — this source is itself a legitimate, freely-searchable IPA-adjacent channel. Output: `layers/16_enrichment/switzerland_india_sweep.json`.

## Electronics & Semiconductors sector expansion (layer 16 enrichment, Batch 2 of sector-by-sector rebuild)

`focus-sector-investor-map/scripts/enrich_electronics_semiconductors_unswept.py` + a live SEC 10-K disclosure-mining pass — Batch 2 of a sector-by-sector rebuild of the 19,795-company `focus_sector_global_catalog.csv` (Batch 1 = Medical Devices). Swept all 3,433 previously-unswept Electronics & Semiconductors rows. **Stage 1** re-ran the profitability screen (margin>0 AND ROE>0) live via yfinance for every row, using a two-tier ticker construction fixed for this batch: the `Market` column (reused from `enrich_profitability.py`'s SUFFIX dict) where populated, falling back to the `Exchange` column for the 318 rows where `Market` is blank — verified live rather than copied from Batch 1's shallower fix, since several exchange codes in this sector behave differently. Result: 1,338 PROFITABLE / 699 NOT-PROFITABLE / 1,396 UNVERIFIED. **Stage 2** mined SEC 10-Ks for genuine India market-entry/investment language, prioritized by `Turnover_USD` — and surfaced a real, pre-existing catalog gap, transparently self-reported in the output file rather than silently worked around: `Turnover_USD` is populated for only 121 of the 1,338 PROFITABLE rows (114 US + 7 India), so every other country's profitable rows (China 533, Taiwan 261, Japan 178, etc.) went unmined this pass — not because those companies are smaller, but because the catalog lacks their turnover figure. **13 confirmed market-entry/investment signals** with real quoted filing text, incl. First Solar (3.2GW installed India manufacturing nameplate capacity, Series 7 modules), Ciena (177,000 sq ft new Gurgaon office lease, April 2025, on top of an existing 282,000 sq ft Gurgaon R&D campus), Sanmina (2023 JV — RSBVL acquired 50.1% of Sanmina SCI India Private Limited for $216M cash), Ribbon Communications (relocating manufacturing into India to meet a local-content mandate, $4.4M IP Optical revenue growth attributed to India sales), and Autoscope Technologies (new Chennai R&D subsidiary, legally formed Oct 2021) — plus 54 business-activity, 4 exit/divestment, and 15 context-only/4 extraction-failed/24 no-mention exclusions. Output: `layers/16_enrichment/electronics_semiconductors_sector_expansion.json`. The Turnover_USD gap will recur in later batches (Auto/EV & Components next) unless the source catalog is backfilled first.

## Country-linked FDI news sweep (real stock-market denominators)

`scripts/build_country_fdi_news_sweep.py` answers two gaps layer 35 couldn't close on its own. First, layer 35's "twin_lead_coverage" was a bare count with no denominator (Switzerland: 3 leads — out of how many *real* listed companies?); this script loads each priority country's ACTUAL stock-market roster from the sibling [global-stock-screener](https://github.com/herrrickshaw/global-stock-screener) repo's `data/global_universe/<CC>.csv` files (no new scraping — already on disk): Switzerland 192 names, Sweden 564, Denmark 104, Germany 449, Canada 2,091, China 2,895, UK 854, Hong Kong 2,793 (Netherlands/Italy/France/Norway have no dedicated file, only the thinner EU.csv exchange bucket: 25/40/39/24). Second, it adds a live discovery query per country (NewsAPI boolean search, the one already-keyed source with free-text country+intent search — Marketaux/AlphaVantage are ticker-lookup-only), matching hits back against the real roster with the same strong/weak fragment matcher `enrich_company_db_ii_tickers.py` uses, so a hit only counts if an actual listed company's name appears, not a bare country mention. 🔴 **Precision bug found + fixed live (2026-08-09)**: raw substring matching let an apostrophe-splitting artifact ("People's" → orphaned "s" token) false-match inside the unrelated word "people **s**aid" — switched to word-boundary regex matching. First real run (12 calls, 69 articles across the 12 priority countries): zero surviving matches — a genuine null result once the false positive was corrected, not zero effort. Output: `layers/16_enrichment/country_fdi_news_sweep.json`.

🔴 **General news-search verdict (2026-08-21)**: a later sector-primary NewsAPI sweep (`scripts/build_sector_news_sweep.py`, one query per twin focus-sector matched against 32,535 companies across 23 country rosters) produced false positives even after fixing an initial query-construction bug — a Micron press release unrelated to India, a macro India-GDP article coincidentally "matching" unrelated small-caps, general market commentary matching an unrelated holding company. Both runs' output was deleted, not merged into any target list. **Conclusion: filing-based sources (a company-name match inside that company's own regulatory filing is automatically correct) are reliable for discovery; general news search is not, at this scale, without much heavier per-hit verification** — reserve it for verifying already-identified candidates, not discovering new ones.

## EDGAR 8-K sweep — fresh material-event filings

`scripts/build_edgar_8k_sweep.py` extends the proven EDGAR full-text pattern to 8-K filings (material events, filed within 4 business days — much fresher than the annual 10-K/20-F cadence). Same zero-cost `efts.sec.gov` API, same phrase list. First run (2026 YTD): **22 filings**, including **Philip Morris International** (3 separate 8-Ks mentioning India investment), Trinity Industries, Figma, Nu Skin Enterprises, PROG Holdings, Alpha Pro Tech, Co-Diagnostics. Output: `layers/16_enrichment/edgar_8k_sweep.json`.

## Global textile trade association membership map (layer 39)

`scripts/build_layer39_textile_associations.py` — textiles is this twin's most fragmented sector (layer 38: only ASICS has real verified India-investment evidence out of 16 curated leads). Trade-association member rosters are a structurally different discovery channel: they list companies by industry membership directly, sidestepping the need for India-intent language. Mapped 11 associations, ~800+ companies (Swiss Textile Machinery Assoc. 42 full + verified, CEMATEX 9 national bodies, ITMF incl. India's 3 associate-member bodies CAI/CITI/Texprocil, VDMA/ACIMIT/UKFT/Textile Institute/BTMA/JTMA/CNTAC/KOFOTI at varying coverage). Strongest India signal: **~20 of 42 Swiss Textile Machinery Association members (~half) confirmed exhibiting at India ITME 2026**. UKFT's full 500-member list published as a [separate Claude Artifact](https://claude.ai/code/artifact/0e13b6c5-698e-46d4-a736-89c4cfe8b17e) rather than re-embedded.

**PDF archive pass (2026-08-22)**: found genuine downloadable member-directory PDFs for the Swiss association (2023 + 2025 editions, richer than the live scrape — full address/email/competence per member) and a bonus discovery: the **India ITME 2022 exhibitor catalog** (1,800+ entries, 148 international). This cross-validates the association findings directly — Heberlein AG, Jakob Müller AG, Loepfe Brothers, Rotorcraft AG, Saurer, Sedo Engineering, Uster Technologies, Xetma Vollenweider and Itema (all Swiss Textile Machinery Assoc. members) all exhibited in **2022**, proving the 2026 signal isn't a one-off. Also present: German (Trützschler, Lindauer Dornier, Mayer & Cie), Italian (Lonati, Santoni, Reggiani Macchine), and Japanese (Murata, Tsudakoma, TMT Machinery) names matching this layer's other association rosters. Most other bodies' directories are web-database-only (VDMA, UKFT's full roster) or Issuu-gated (ACIMIT) — no raw PDF found; recorded as data, not guessed. Output: `layers/39_textile_associations.json`, doc: `docs/TEXTILE_ASSOCIATIONS.md`.

## Association + event registry, all sectors (layer 40)

`scripts/build_layer40_association_event_registry.py` — extends the layer-39 pattern across every twin focus sector (plus Mining and Oil & Gas, not yet formal focus sectors, added per explicit request). **33 associations, 40 events tracked**, built as a durable SourceRoute-style pointer registry (URL + access method + recheck cadence — same convention as layer 15's portal directory), not a full data re-embed; each research pass's full company lists live in that pass's own scratch files, referenced here by count/sample.

The pattern confirmed repeatedly: **an India-domestic trade fair's exhibitor list is a stronger signal than bare association membership** — it's revealed preference (a company paid to physically exhibit in India), and every one of these produced a real, country-tagged roster this pass: **SEMICON India** (351, incl. ASML/Applied Materials/Lam Research/Micron), **ELECRAMA** (929-row XLSX), **Medical Fair India** (364, 40 international), **ChemTECH World Expo** (750+, 39+ countries), **Auto Expo Components** (~60 foreign across 7 national pavilions), **Aero India 2019** (165 foreign, complete — Airbus/Boeing/Dassault/Elbit/Rosoboronexport/Saab), **AAHAR** (139 foreign food-industry exhibitors), and **IMME 2024** (268 exhibitors/13 countries — Australia's 10-company delegation, led by **Austmine**, was the largest non-India contingent). DefExpo 2022 was a genuine structural exception, not a research gap: foreign OEMs were excluded as primary exhibitors that edition by design.

Global flagship events (non-India editions) were also mapped: **CPHI Worldwide** (2,909 exhibitors/80 countries, live country-filterable), **Automechanika Frankfurt** (country-filterable via URL param — proved by pulling 160 real Indian exhibitors as a test), **K Fair** (3,259/66 countries), **ACHEMA** (1,692), **Farnborough Airshow** (1,292, plain-fetchable, no browser needed), **electronica Munich** (full table + downloadable XLSX), **GIFA/METEC**, **Intersolar Europe** (incl. Adani Solar), **IAA Mobility**, **MEDICA** (3,020). Genuine gaps recorded rather than guessed: ITMA 2023's exhibitor data no longer exists anywhere (confirmed via Wayback CDX), ITMA Asia+CITME 2025's list was mobile-app-only and never web-indexed, WindEnergy Hamburg and SMM Hamburg both show "list under construction" with no archived prior data, MINExpo's 2024 gallery link expired.

New association rosters: **VDA Germany** (567 across 3 tiers — Group III alone is 484 real parts suppliers: Bosch, Continental, ZF, Schaeffler, Valeo, Magna, Mahle, Denso, Aptiv, Autoliv), **JAMA** (14, full, OEM-only), **CLEPA** (116, partial), **worldsteel** (133, incl. India's SAIL/JSW/Tata Steel/Jindal Steel/Sunflag/Saarloha), **ASD Europe** (51, full), **EFPIA** (47, full), **PhRMA** (31), **ICMM** (69, incl. Hindustan Zinc), **IPIECA** (39 oil majors), **Cefic** (Associated Companies list directly confirms Gujarat Fluorochemicals and Jubilant Pharmaceuticals already sit in a major European chemical-industry association's orbit). Output: `layers/40_association_event_registry.json`, doc: `docs/ASSOCIATION_EVENT_REGISTRY.md`.

## Railways — a genuinely new sector, plus other gaps (layer 40 extension)

A gap-analysis pass across the Delhi/Mumbai/Frankfurt/Düsseldorf trade-fair calendars surfaced **Railways & Rail Transport** — a sector the twin had never touched — anchored by **InnoTrans** (Berlin, the world's largest rail trade fair): live-verified 2026-08-22 by direct browser session, **3,082 exhibitors**, real company+address+hall/stand+segment+description per entry, no login required to browse. Confirmed sample: Knorr-Bremse, ABB Ltd. (Switzerland), Aarsleff Rail A/S (Denmark), 4AI Systems (Australia). The backend isn't a simple REST API (routes through blob: URLs behind a CloudFront/S3 SPA shell) — full pagination is a follow-up task, but the access method is proven. India's own counterpart, **IREE** (Bharat Mandapam, CII + Ministry of Railways, Asia's largest rail event), has a confirmed exhibitor-list PDF not yet parsed.

**Update (deep-dive completed)**: all six Frankfurt/Düsseldorf candidates got fully pulled, not just scoped. **Messe Frankfurt** shares one exhibitor-service API across its entire portfolio (public apikey baked into the site's JS bundle) — **Light + Building** (1,884 exhibitors), **ISH** (2,127, India 31), **Heimtextil** (1,182 — **India is the #1 exhibiting country, 304 of 1,182 = 25.7%**, the strongest India signal found this whole session). A bonus cross-show pull (omitting the event filter) returned **3,114 India-HQ'd exhibitors across 40+ Messe Frankfurt shows worldwide** in one API call. **Messe Düsseldorf** shares a DIMEDIS "vis" A-Z directory API (confirmed via a cross-domain test: interpack.com's server + a header pointing at k-online.com returned K Fair's own data) — **interpack** (3,085, India 111), **EuroShop** (2,014, India only 8 — weak signal), **wire & Tube Düsseldorf** (2,743 combined roster, India 167, #5 country). Same Düsseldorf platform confirmed live but not yet pulled for boot, drupa, glasstec, A+A, Caravan Salon. Registry now tracks **54 events** total. Data: `data/trade_fairs/messe_frankfurt/`, `data/trade_fairs/messe_duesseldorf/`.

Also deep-dived: **InnoTrans** (Berlin) — full 3,082-exhibitor extraction (not a sample), found by monkey-patching `window.fetch` on the live page to catch the real backend call after passive network observation showed nothing (the site is a Corussoft "EventGuide" white-label platform; true endpoint `POST live.messebackend.aws.corussoft.de/webservice/search`, form-urlencoded, short-lived anonymous JWT, reusable via curl once captured). 61 countries — Germany 1,039, China 241, France 217, India 92. **IREE** (India's own rail fair) PDF parsed: 250 entries, 34 flagged foreign/foreign-parent (27 clean of parser artifacts) — real finds include Wabtec Corporation (WIIPL), ZF Friedrichshafen AG, Vossloh India, Voestalpine VAE VKN India. **RailTrans Expo** confirmed as a genuine gap: no real exhibitor roster exists, only ~29 self-reported headline sponsors from a private events company. Data: `data/trade_fairs/railways/`.

## Association/exhibitor leads cross-reference (layer 41)

`scripts/build_layer41_association_leads_crossref.py` — cross-references layer 39/40's rosters against the twin's existing leads (layer 16) and company DB (layer 32) using the same word-boundary strong/weak fragment matcher as the filing sweeps. Sources: 4 re-parsed session scratch files (Aero India 2019, SEMICON India 2025, AAHAR 2024 Hall 1, India ITME 2022), 8 hand-curated association rosters, plus (after the InnoTrans/IREE/Messe Frankfurt/Messe Düsseldorf deep-dives) the durable `data/trade_fairs/` datasets: InnoTrans (3,082), IREE (27 clean foreign), and all 6 Frankfurt/Düsseldorf fairs (Light + Building, ISH, Heimtextil, interpack, EuroShop, wire & Tube). **14,570 new companies flagged** across 20 sources, checked against 1,769 known names — the large jump from the initial 733 reflects that Railways, Construction, Packaging, and Retail Tech were entirely untracked sectors before this pass, so most of what a first sweep finds there is necessarily new. Caught and fixed a real parsing bug along the way: the first AAHAR pass swallowed every subsequent exhibition hall (1,577 rows instead of the correct 139) because the stop-marker regex looked for "HALL NO. 2" when the actual text used "HALL 2 GROUND FLOOR" — caught via a sanity check against the scouting agent's own reported count. Also filtered out embassies/trade-promotion bodies (e.g. "High Commission of Canada") that were getting flagged as false-positive "new companies." 🔴 The 4 original scratch-file sources are session-ephemeral and won't survive to a future run — re-fetch via the URLs in layer 40 first; the newer `data/trade_fairs/` sources are durable repo data and will. Output: `layers/41_association_leads_crossref.json`, doc: `docs/ASSOCIATION_LEADS_CROSSREF.md`.

## Leads generation (layer 16)

`scripts/build_leads.py` crosses the market layer's **verified-profitable** screen (margin>0 AND ROE>0, from the 19,795-company catalog) with the twin's curated lane map — which central instruments are open per sector, and which states pay top-ups. Score = profitability (40) + expansion signal (25) + open central lane (25) + state top-up available (10).

Each lead carries its central lanes with live statuses (e.g. E-DRIVE closing 31-Jul, Make-II EOIs in August), state landing options, and a **contact-enrichment block** naming the roles to pull (CFO, Corp Dev, India country head, Govt Affairs) via **Lusha or Apollo** — enrichment is a separate deliberate step, no personal data is collected by the script (the Apollo MCP connector works once authenticated in claude.ai settings; Lusha has no connector, use its export).

## Land availability × open incentives + related repositories (layer 25)

The earlier layers catalogue *what incentives exist*; layer 25 adds the two
operational facts an investor actually acts on — **where developed industrial
land is vacant** and **which windows are open right now** — and wires the twin
to the sibling repos those facts come from. Rebuild any time with
`python3 scripts/build_layer25_linkages.py` (reads layer 17 locally, pulls the
land data live from the policy repo).

**Land availability** (from [india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations), IILB 2026-07): 37 states, 4,240 parks, **125,602 vacant developed-park plots**. Top vacant-land states — Maharashtra (19,659 Ha), Tamil Nadu (16,487), Andhra Pradesh (13,303), Gujarat (12,605), Rajasthan (11,541), Haryana (8,292). The central IILB counts *developed-park* vacant land only; larger undeveloped state banks are reachable via the machine-readable state portals layer 25 lists (Odisha IDCO ArcGIS, UPSIDA, APIIC, TGIIC, RIICO, SIPCOT).

**Currently-open incentives** (from layer 17, PIB-daily refreshed): **10 open** central windows — Semicon/ISM 2.0, ECMS (FCFS), IT Hardware 2.0, NGHM SIGHT, Agriculture Infrastructure Fund, BharatNet, ELI, UCF, RDI, Coal gasification; **1 closing soon** (PM E-DRIVE e-2W claims 31-Jul-2026); **UNNATI closed-oversubscribed**.

**The linked insight**: a company eligible for a sector-agnostic open central incentive can site in the land-rich states without a land constraint — but the pending IEM pipeline is metals/chemicals-heavy, so heavy-industry siting still faces the land deficit quantified in the policy repo's supply/demand scenarios.

**Project pipeline** (layer 26, from [India Investment Grid](https://www.indiainvestmentgrid.gov.in) / NIP — the same pipeline **PM Gati Shakti** coordinates): **12,385 NIP opportunities across 42 sectors** — Roads & Highways 2,306 ($314bn), Healthcare 1,153, Waste & Water 1,020 ($76bn), Real Estate 950, Railways 850, Education 858, Electricity Generation 650, Electronic Manufacturing 567. Each sector is mapped to its twin incentive lane (Electronic Manufacturing → Semicon/ISM 2.0/ECMS; Roads/Railways → Gati Shakti; Food Processing → PLI-FPI/AIF …), and flagship projects (Western DFC $15.6bn, Ganga Expressway $4.6bn, Jal Jeevan Mission $34.8bn) are pulled live from IIG's `rawData` endpoint. Gati Shakti's own GIS master-plan portal is login-gated (state/ministry SSO), so IIG is the machine-readable public surface for the same project set. **Together layers 25 + 26 answer WHERE (land) + WHAT INCENTIVE + WHICH PROJECT** for a siting decision.

| Related repo | Feeds the twin | Into layer |
|---|---|---|
| [india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations) | Industrial land availability + IEM demand match + supply/demand scenarios; **import-dependency / trade-deficit → policy-gap analysis, sector×country PLI-coverage scorecard, FDI pitch** | 25, 30, 16, 05 |
| [agri-commodity-tracker](https://github.com/herrrickshaw/agri-commodity-tracker) | FCI depot/storage footprint (478 depots) — agri-logistics behind FPI/AIF incentives | 02, 17 |
| [india-trade-tracker](https://github.com/herrrickshaw/india-trade-tracker) | DGFT EIDB trade flows — import-heavy = substitution targets | 16, 06 |
| [focus-sector-investor-map](https://github.com/herrrickshaw/focus-sector-investor-map) | Global company pools per incentivized sector | 06, 07 |
| [discom-debt-and-revenue-models](https://github.com/herrrickshaw/discom-debt-and-revenue-models) | State DISCOM health — power-cost context for siting under RDSS | 17 |

**External government pipelines linked** (layer 26): [India Investment Grid](https://www.indiainvestmentgrid.gov.in) (NIP, 12,385 projects — public), **PM Gati Shakti** (same NIP pipeline; GIS portal login-gated), and IIG's own linked **Industrial Information System** (= the IILB land bank already used in layer 25) and **Project Monitoring Group** — confirming land, projects and incentives are one system.

**Foreign market-entry facilitators** (layer 27): the demand side — **27 trade-promotion agencies & bilateral chambers across 20 countries** that host events and run B2B matchmaking to bring foreign companies into India. Anchored on the user's examples — **GTAI** and the **Indo-German Chamber (AHK/IGCC)**, **Swissnex** + **S-GE** — extended to UKIBC (UK), JETRO (Japan), KOTRA (Korea), Business France + IFCCI, ITA/ICE (Italy), USIBC + AMCHAM (US), Business Sweden, ADVANTAGE AUSTRIA, Austrade (Australia), Enterprise Ireland, EBTC (EU-wide) and more. Eleven carry verified live events calendars; every URL is liveness-checked on build (⚠️ the old Swiss-Indian Chamber domain `sicc.in` now redirects to an unrelated site — flagged, routed to swissnex + S-GE instead). This is where a firm eyeing an Indian incentive (layers 02/17), project (layer 26) or site (layer 25) goes for introductions.

The layer also carries the **Indian apex industry bodies** — **FICCI, CII, NASSCOM, ASSOCHAM** — the host-country counterparts that co-host the foreign chambers' delegations and run India's flagship investment summits (CII Partnership Summit, ASSOCHAM state investor roadshows like *Invest in Odisha*, NASSCOM for tech/GCC entrants). A foreign entrant typically meets both its home chamber and the Indian apex body at the same events.

## Policy watchlist (layer 28)

Where the incentive catalogue and scheme monitor capture policy *in force*, layer 28 looks *forward* — the policies being drafted, tabled, or publicly debated that will reshape the regulatory landscape. Rebuild live with `python3 scripts/build_layer28_policy_watchlist.py`.

- **PRS Legislative Research bill track** (authoritative pipeline): **962 bills** scraped, of which **33 are the active investment-relevant watchlist (2024+)**, each mapped to a twin sector — Income Tax Bill 2025 & Securities Markets Code 2025 (BFSI/tax), IBC & Banking Laws amendments (BFSI), Draft Electricity Amendment 2025 (Power/RDSS), Nuclear Energy Bill 2025, Indian Ports Bill + Coastal/Merchant Shipping (Gati Shakti maritime), MMDR & Oilfields amendments (mining/energy), Jan Vishwas (decriminalisation), the labour codes' central rules.
- **Drishti IAS** current-affairs editorials (what's being debated now — shipbuilding roadmap, AI regulation, digitising agriculture, corporate-sector reform); **Vision IAS / InsightsIAS** recorded for manual cross-check.
- **Parliament**: Lok Sabha bills page + the undocumented LS Q&A API (needs query params). 🔴 **Rajya Sabha** sources are blocked from this machine — recorded as data, not skipped.

When a watchlist bill is enacted it graduates into the scheme monitor (layer 17) / incentive catalogue; bills like Jan Vishwas and the Securities Markets Code directly reshape the decade report card's ease-of-doing-business lane (layer 05).

## MoSPI macro-statistics connector (layer 29)

The incentive/land/project layers describe the *offer*; layer 29 adds the *macro backdrop* — the official India statistics that frame whether the offer lands. It catalogues the **25 datasets available via [MoSPI](https://esankhyiki.mospi.gov.in)** (Ministry of Statistics & Programme Implementation), each tagged for investment relevance and linked to the twin layer it informs:

- **6 core macro** — NAS (GDP, growth, capital formation), CPI & WPI (retail/wholesale inflation), IIP (industrial output), PLFS (jobs, wages, unemployment), RBI (foreign trade, BoP, forex, exchange rates).
- **6 sector** — ASI (factory financials), MNRE (state-wise renewable capacity), ENERGY, EC (establishment clusters), ASUSE (MSME base), NSS77 (agri households).
- **13 context** — HCES consumption, AISHE/UDISE education, NFHS health, GENDER, ENVSTATS, and the NSS rounds.

**Access** is documented two ways: the official API (`api.mospi.gov.in/api/esankhyiki/`, per-dataset endpoints + [swagger](https://esankhyiki.mospi.gov.in/EC/swagger-ui/index.html), viz at `/viz/<dataset>`) and the MoSPI MCP connector's 4-step workflow (`list_datasets → get_indicators → get_metadata → get_data`; filter codes are arbitrary and must come from `get_metadata`). Known data quirks are recorded in-layer — 🔴 the RBI forex series lags ~13 months (use the `rbi.org.in` WSSView scrape instead), and WPI/IIP prints with large jumps need a cross-check.

## Trade-deficit & import-substitution map (layer 30)

Incentives don't exist in a vacuum — most PLI-type schemes are, at bottom, an *import-substitution* bet. Layer 30 makes that explicit, joining the twin's incentive lanes with the import-dependency / policy-gap analysis in [india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations) (HS-chapter trade from TRADESTAT/DGCI&S). It encodes four **trade-deficit clauses**:

1. A large or fast-growing import chapter is an investment opportunity **only where a policy lever is sized to it** — otherwise it's a policy *gap*, not an opportunity.
2. **Process-trade** chapters (gems & jewellery, $109bn) are trade-facilitation cases, not substitution targets.
3. **Structural imports** (crude oil $203bn, edible oils, fertilisers) aren't substitutable by manufacturing policy — the lever is efficiency / alternative feedstock.
4. The bilateral deficit is concentrated (**China −$112bn**, Russia −$51bn); Press Note 3 screening + the target shortlist (layer 16) route substitution demand toward specific source countries.

The payoff is the **gap list** — substitutable deficit chapters the incentive catalogue only partially covers or misses entirely: Machinery ($74bn), Organic & Inorganic Chemicals ($40bn combined), Plastics ($22bn), Iron & Steel ($16bn), Optical/medical instruments ($15bn), Aircraft ($14bn). Electronics (HS85, $105bn) is the one large deficit with *strong* coverage (Semicon/ISM 2.0 + ECMS). The full sector×country strategy, PLI-coverage scorecard and FDI pitch deck live in the linked repo.

## Auto-update scripts

`scripts/refresh_twin.py` implements the update engine — snapshots land in `state/` (append-only, diffs printed as `CHANGE` lines):

```bash
python3 scripts/refresh_twin.py weekly     # routes health (64 portals) + UNNATI notice diff + NSWS + RBI WSS
python3 scripts/refresh_twin.py pib        # delegates to the policy repo's pib_index.py --update
python3 scripts/refresh_twin.py catalogue  # rebuild flat index view -> docs/SCHEME_CATALOGUE.md
```

Suggested crontab (not auto-installed):
```cron
17 7 * * *   cd ~/digital-twin-for-ipa && python3 scripts/refresh_twin.py pib
23 8 * * 1   cd ~/digital-twin-for-ipa && python3 scripts/refresh_twin.py weekly
```

**Try it in 2 minutes**: the [quickstart notebook](notebooks/twin_quickstart.ipynb) clones the repo, explores the 312-instrument index, checks the interlinkage verification tally, and probes live portals — one click via the Colab badge at the top.

Reference docs: [SCHEME_CATALOGUE.md](docs/SCHEME_CATALOGUE.md) (generated, 312 instruments) · [REPORTAGE.md](docs/REPORTAGE.md) + [reportage.html](docs/reportage.html) (**quarterly reportage** — 819 key announcements × scheme × ministry, 2017Q1→today, PRID-linked; the HTML page pre-renders all rows (works without JS) with quarter/scheme/ministry filters and title search, **plus a State-level incentives section** — 15 states' scheme status, funds evidence with citations, arrears flags and news links; regenerated from the daily-refreshed PIB register) · [DIRECTORY.md](docs/DIRECTORY.md) · [ABBREVIATIONS.md](docs/ABBREVIATIONS.md) · [DATA_MODEL.md](docs/DATA_MODEL.md) · [PLI_SCHEME_BENEFICIARY_LEADS.md](docs/PLI_SCHEME_BENEFICIARY_LEADS.md) (hand-researched, no build script — 9 schemes' approved-applicant rosters, Parliament Q&A + PIB sourced) · [INTEGRATED_TARGET_DECISION.md](docs/INTEGRATED_TARGET_DECISION.md) (hand-researched — cross-references the beneficiary rosters against layer 16's disclosed-interest leads and layer 35's capital-cost prioritization into a tiered target list)

## State catalog clusters (layer 12)

| Cluster | States | Strongest verified finds |
|---|---|---|
| `west_gj_mh_rj_goa` | Gujarat, Maharashtra, Rajasthan, Goa | **MIISP 2025** (PSI-2019's actual successor, GR 31-12-2025) + 5 new Nov–Dec 2025 Maharashtra sector policies; RIPS 2024 full menu (75% SGST-7y / 13–28% capital / 1.2–2% turnover); Viksit Gujarat 2026 successor — now OCR-extracted (full matrix in ocr_extracts_gj_pb.json); Goa's Interest Subsidy 2008 lapsed-but-still-listed |
| `south_tn_ka` | Tamil Nadu, Karnataka | TN's 4 mutually-exclusive options (incl. 100% SGST 15y, flexible subsidy to 40% EFA); Karnataka IP 2025-30 capex-vs-production-linked choice (2.5/2.0/1.0% turnover by zone); GCC Policy 2024-29 full schedule; TN Shipbuilding + Circular Economy 2026 policies |
| `south_tg_ap_kl` | Telangana, AP, Kerala | AP IDP 4.0 quantified (12–15% FCI + **PLI top-up = 10% of central PLI**, Early Bird 30–40% FCI); Telangana Next-Gen Life Sciences 2026-30 + "Meet or Beat" guarantee; Kerala's 18-category package (incl. 20% PLI-investor top-up); Telangana has NO enacted post-2024 industrial policy |
| `north_up_hr_pb_uk_hp_dl` | UP, Haryana, Punjab, Uttarakhand, HP, Delhi | **UP ECMS top-up verified verbatim ("Equal to Central ECMS incentives")**; IIEPP-2022 10–30% grid; Punjab IBDP 2026 (gazette 08-03-2026, supersedes 2022; OCR-extracted); Uttarakhand MIIP 2025 + incentive calculator; Delhi has no post-2021 industrial policy |
| `central_east_mp_cg_od_wb_jh_br` | MP, Chhattisgarh, Odisha, WB, Jharkhand, Bihar | MP IPP-2025 BIPA formula (40%→10% EFCI, ₹200cr cap, multiplier-scaled); Odisha IPR-2022 **uncapped** 20–30% capital subsidy + 20-year GH₂ power package; CG's 50% capital + 50% interest headline stack; **wbidc.com is a hijacked/parked domain**; Bihar's industrial-policy web presence effectively dead |
| `ne_states_jk` | Assam, 7 NE states, J&K | **Assam semiconductor top-up = +40% of central ISM capex assistance** (Tata OSAT package, gazette-verified); J&K NCSS (30–50% capital, 100% GST-linked 10y) + IP-2021-30 state stack quantified, incl. an internal inconsistency in the official PDF; UNNATI registration **CLOSED — oversubscribed** (portal notice: applications exceeded state-allocated funding; verified 2026-07-20); **investinassam.com is squatted** (real portal: eodb.assam.gov.in) |

## Catalog v2 clusters (layer 09)

| Cluster | Entities | Strongest company-facing finds |
|---|---|---|
| `finance_mca_niti` | Finance (DEA/DFS/IFSCA), MCA, NITI | GIFT-IFSC FinTech Incentive Scheme; MCGS-MSME 60% guarantee to ₹100cr; AIM 2.0 |
| `power_mohua_jalshakti` | Power, MoHUA, Jal Shakti | **BESS VGF via PSDF** (Jul-2025); PSP/transmission TBCB; UCF ₹1L cr + CRGSS; Namami Gange HAM |
| `defence_space_atomic` | MoD, Space, DAE | iDEX/ADITI (₹25cr/project grants); SRIJAN + Positive Indigenisation Lists (assured demand); live Make-I/II EOIs |
| `scitech_earth_ayush` | DST/TDB, DBT/BIRAC, DSIR, MoES, AYUSH | **RDI Fund** open CFP-2026; BioE3 call family; DSIR deep-tech recognition relaxation |
| `agri_food_cooperation` | Agriculture, DFPD, Cooperation | AIF (₹94,272cr sanctioned, portal open); PEG 10-year FCI hiring guarantee; NCDC Sahakar loans |
| `environment_ib_education_doner` | MoEFCC, I&B, Education, MDoNER | **Five tradeable EPR certificate markets**; Green Credit Programme; film incentive up to 40% / ₹30cr |
| `social_admin_quick` | 17 social/administrative entities | Sleepers: PMJAY empanelment top-ups, DDU-GKY per-candidate PIA payments |
| `transport_tourism_skills` | Railways, MoRTH, Tourism, Skills | **PM-SETU** (₹60,000cr, ₹10,000cr industry tranche); GCT terminals (open on RailSAHAY); RVSF/ATS licence+mandated-demand |

## What the twin shows that no single source does

- **No aggregator — official or private — maintains scheme-stacking information systematically** (layer 10 finding). myscheme.gov.in is citizen-facing and API-locked; NSWS is the only real company-facing aggregator; stacking knowledge lives in scheme guideline PDFs and consultant sites.
- **Budget reality diverges from announcements** (layer 11): Semicon India utilization ran 23% → 9% → ~61%; BharatNet underspent 75%; IT-Hardware PLI 2.0 hit 3% of production targets while LSEM exceeded its investment target.
- **The government web estate has a common access pattern**: many ministry sites are JS shells over headless WordPress at `cms-<ministry>.digifootprint.gov.in/wp-json` — the twin's access notes document per-site routes (and the dead ends: dbtindia.gov.in unreachable, inspace.gov.in a ServiceNow shell, makeinindiadefence.gov.in 503).

## Method & provenance

- Sweeps run as parallel per-cluster agents fetching **official ministry sites first**, NSWS second, aggregators/explainers only as labeled SECONDARY.
- "Not published" / "unverifiable on-site" is recorded as data with the exact failure mode.
- Corrections are displayed, never silent (inherited from the companion policy program).

*Companions: [india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations) (PIB register, bulletins, quarterly Trade Watch) · [focus-sector-investor-map](https://github.com/herrrickshaw/focus-sector-investor-map) (market layer).*

<!-- 
DATA LIBRARY LINK - Add this section to every repo README.md
This snippet provides discovery and documentation links.
-->

## 📊 Data Discovery

This repository is part of the **Global Data Library** — a unified catalog of 10,528 datasets across 40+ repositories.

### Quick Links

- **[Global Data Library README](.ruflo/DATA_LIBRARY_README.md)** — Full catalog, search API, and usage examples
- **[Data Library Python Interface](.ruflo/data-library/data_library.py)** — Query datasets programmatically
- **[Repository Scanner](.ruflo/data-library/repo_scanner.py)** — Reindex all repos to update the catalog

### Datasets in This Repository

The data catalog automatically inventories all datasets in this repo. To find your data:

```python
from data_library import DataLibrary

lib = DataLibrary()

# Search this repo's datasets
results = lib.search("", source="<repo-name>")

# Get dataset details
dataset = lib.get("<dataset_id>")
print(f"Rows: {dataset['row_count']}")
print(f"Freshness: {dataset['freshness_hours']} hours old")
print(f"Storage: {dataset['storage_tier']}")
```

### Browse the Full Catalog

**Market Coverage** (5 markets, 21,279 symbols):
- India (NSE/BSE): 2,364 instruments
- US (NASDAQ/NYSE): 7,442 instruments
- Europe (17 exchanges): 1,214 instruments
- Japan (TSE): 3,709 instruments
- Korea (KRX): 2,768 instruments

**Government Sources** (30+ ministries):
- MOSPI: 25 datasets (GDP, CPI, trade, agri, power)
- SEBI: 151,928 XBRL results + IPO pipeline
- PIB: 25+ ministry announcements
- DGFT: India trade data (monthly)
- Agmarknet: 300+ mandi prices (daily)
- NSE/MCX: Real-time derivatives chains

See [Global Data Library README](.ruflo/DATA_LIBRARY_README.md) for complete documentation.

### Finding Data Across All Repos

```python
# Find India OHLCV data (might be in multiple repos)
lib.search("india ohlcv", market="india")

# Get the fastest/freshest version
optimal = lib.get_optimal("india ohlcv", latency="<100ms", freshness="<1day")
# Returns: {"storage_tier": "cassandra", "path": "..."}

# Check data gaps
gaps = lib.gaps("india", date_from="2026-01-01")

# See which collectors are stale
status = lib.collectors_status()
```

---
