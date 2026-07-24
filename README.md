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
| 16 | `layers/16_leads.json` | **Leads generation** — **263 leads across 26 countries**: 147 yfinance-verified-profitable US/India firms (US leads carry SEC 10-K India/APAC mention-mining with YoY trend) + 116 annual-report deep-dive leads from 19 more countries (JP/KR/CN/UK/AU + DACH/NL, France/South-EU/Nordics, TW/HK/SG, CA/BR/ZA/Saudi/Israel) with quoted evidence, yfinance tickers, and per-region policy context (PN3, TEPA, SHANTI, ECTA); view: [docs/LEADS.md](docs/LEADS.md) |
| 25 | `layers/25_land_incentive_linkages.json` | **Land availability × open incentives (cross-repo linkage)** — joins the twin's scheme monitor with industrial-land data from sibling repos: the two operational facts an investor needs — WHERE developed land is vacant (IILB 37-state, 125,602 vacant plots) and WHICH windows are open right now (10 open central incentives). Built by `scripts/build_layer25_linkages.py` |
| 26 | `layers/26_project_pipeline.json` | **Investment-project pipeline — IIG / NIP + PM Gati Shakti** — the actual government-listed projects an investor can enter, from the [India Investment Grid](https://www.indiainvestmentgrid.gov.in) (public window onto the National Infrastructure Pipeline, the set PM Gati Shakti coordinates): **12,385 NIP opportunities across 42 sectors** + flagship projects (live), each sector mapped to its twin incentive lane. Built by `scripts/build_layer26_projects.py` |
| 27 | `layers/27_entry_facilitators.json` | **Market-entry facilitators in India** — the trade-promotion agencies & bilateral chambers that host events and B2B matchmaking to bring foreign firms into India, plus the **Indian apex industry bodies** (FICCI, CII, NASSCOM, ASSOCHAM) that co-host them (**31 bodies, 21 countries**): GTAI + Indo-German Chamber (AHK/IGCC), Swissnex + S-GE, UKIBC, JETRO, KOTRA, Business France + IFCCI, ITA/ICE, USIBC + AMCHAM, EBTC and more. 11 verified events calendars; URLs liveness-checked on build. Built by `scripts/build_layer27_entry_facilitators.py` |
| 28 | `layers/28_policy_watchlist.json` | **Policy watchlist — policies in discussion / in the pipeline** — the forward-looking counterpart to layer 17: NEW policy drafted, tabled or debated but not yet in force. **962 PRS bills** (live), **33 active investment-relevant bills (2024+)** mapped to twin sectors — Income Tax Bill 2025, Securities Markets Code, IBC & Banking amendments, Draft Electricity Amendment 2025, Nuclear Energy Bill, Indian Ports/Shipping bills, Jan Vishwas, labour codes — plus Drishti IAS policy editorials. Sources: PRS + Drishti IAS (live), Lok Sabha (API), 🔴 Rajya Sabha blocked. Built by `scripts/build_layer28_policy_watchlist.py` |
| 29 | `layers/29_mospi_data_sources.json` | **MoSPI macro-statistics connector** — the official India macro/statistics backdrop the twin lacked: **25 MoSPI datasets** (6 core macro · 6 sector · 13 context), each tagged for investment relevance and linked to the twin layer it informs — NAS (GDP), CPI/WPI (inflation), IIP (industrial output), PLFS (jobs), RBI (external sector), MNRE (renewable capacity), ASI, EC. Documents the official API (`api.mospi.gov.in`) + eSankhyiki portal + MCP-connector 4-step workflow. Built by `scripts/mospi_connector.py` |
| 31 | `layers/31_ipa_source_network.json` | **IPA source network** — the data sources of the investment-promotion world itself: **WAIPA member directory live-scraped on build (138 IPAs, 112 countries** incl. Invest India, Invest Telangana, MIDC; every member website liveness-swept — 107 live), 10 non-WAIPA IPAs covering the top India FDI-source jurisdictions WAIPA misses (SelectUSA, EDB Singapore, NFIA, GTAI, InvestHK, InvesTaiwan…), WAIPA-World Bank IPA survey PDFs, Invest India's scrapeable surfaces (no JSON API — sitemap w/ 41 sector + 36 state pages, static S3 PDF archive, company-announcement tickers, ODOP, winding-down SIRU), **NDAP API access pattern** (`loadqa.ndapapi.com` backend + Origin header; 6,784 datasets; 12 investment-relevant ids), NITI state indices (EPI/III/SDG/FHI/SECI) + GVC reports, and the data.gov.in DPIIT **IEM datasets that work with the public sample key**. Access failures recorded as data (unctad.org 403 — but investmentpolicy.unctad.org works; oecd.org 403). Built by `scripts/build_layer31_ipa_sources.py` |
| 32 | `layers/32_company_db.json` + `data/companies.db` | **Company database** — every company the twin has touched (**1,785 unique**, deduped on normalized-name+country) consolidated from seven layers into one queryable SQLite DB: 321 foreign leads · 136 shortlist targets · 98 clearance leads (82 credit-rated via the layer-24 CARE/CRISIL/ICRA channel) · 1,371 EC-filer pool · alias checks · pairings. `company_sources` keeps every source record verbatim (provenance per row); `company_card` view = one row per company. Built by `scripts/build_company_db.py`. **Enrichment**: `scripts/enrich_company_db_ii_tickers.py` scrapes the Invest India sector-page announcement tickers (439 items across 41 sectors) into `ii_announcements`/`ii_company_matches` and validates the exception cohort — tiered matching (strong challenges verdicts, weak is review-only after 'Reliance Bp Mobility' swallowed Reliance Industries stories and 'Galaxy Dyestuff' matched Samsung Galaxy); first run: 41 companies matched, and Nayara Energy's QUIET-side verdict CHALLENGED — the national IPA itself carries its 400-petrol-pump rollout, corroborating the CARE rationale's DODO buildout |
| 33 | `layers/33_policy_finance_extensions.json` | **Policy-finance extensions** — four analysis blocks with per-claim sources + HTTP-verified access + layer-32 company linkages: **fisheries** (PMMSY ₹21,395 cr approved / PM-MKSSY final year / FIDF 3% subvention, TN largest user / MPEDA record FY26 exports $8.46bn w/ US −19.5% on tariffs → 18% post-deal), **state-excise bottling fees** (4-6-levy fee stack; Rajasthan the only primary-sourced per-BL rate; 🔑 SC *Lalta Prasad Vaish* 9-judge ruling lets states tax industrial alcohol — structural fee-creep risk for the E20 ethanol cohort; Punjab ₹1/BL first mover, MoPNG rollback demand; Maharashtra +50% duty shock), **customs duties** (Feb-2026 posture per sector; steel 12% safeguard stepping to Apr-2028; solar BCD+AIDC; 3 duty×incentive stacks; WITS/ICEGATE-CIP working lookup routes, indiantradeportal 403), **India Exim Bank** (LOC .xlsx links live-scraped each build — 298 LOCs $25.5bn structured; Ubharte Sitaare 106 export champions; EOU 20%-export screen). Built by `scripts/build_layer33_policy_finance.py` |
| 34 | `layers/34_stressed_assets.json` + `stressed_assets` view | **Stressed/distressed assets** — consolidates three previously-scattered sources: (1) company-level rating/litigation distress flags from the layer-32 DB as a `stressed_assets` SQLite view (11 flagged: 4 rating-darkness/issuer-not-cooperating, 2 watch-negative incl. Nayara, 1 downgrade, 1 promoter-litigation regrade RSLD, 3 sub-IG BB+-and-below via a grade parser that excludes upgrades), (2) national distressed-LAND supply channels + 7 named liquidation assets pulled live from the policy-recs repo (IBC 1,436 ongoing liquidations, closed-PSU/NLMC ~3,400 acres, GIDC ~1,800 ha resumed, ARC/SARFAESI), (3) the **Dunlop India** litigation case map (wound-up manufacturer, TN Ambattur 60.86 ac + WB Kings Court 50%, lead judgment 17-Mar-2026). Real registers (IBBI/NLMC/SARFAESI) named with routes. Docs: [docs/STRESSED_ASSETS.md](docs/STRESSED_ASSETS.md). Built by `scripts/build_layer34_stressed_assets.py` |
| 30 | `layers/30_trade_deficit_map.json` | **Trade-deficit & import-substitution map** — links incentives to India's trade deficit: which large import chapters an open incentive actually addresses vs where the deficit is a **policy gap**. From [india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations) — 12 import chapters (Mineral fuels $203bn, Electrical machinery $105bn…), **7 substitutable gaps** (Machinery $74bn, Chemicals, Plastics, Steel, Aircraft), and the concentrated bilateral deficit (China −$112bn). Built by `scripts/build_layer30_trade_deficit.py` |

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

Reference docs: [SCHEME_CATALOGUE.md](docs/SCHEME_CATALOGUE.md) (generated, 312 instruments) · [REPORTAGE.md](docs/REPORTAGE.md) + [reportage.html](docs/reportage.html) (**quarterly reportage** — 819 key announcements × scheme × ministry, 2017Q1→today, PRID-linked; the HTML page pre-renders all rows (works without JS) with quarter/scheme/ministry filters and title search, **plus a State-level incentives section** — 15 states' scheme status, funds evidence with citations, arrears flags and news links; regenerated from the daily-refreshed PIB register) · [DIRECTORY.md](docs/DIRECTORY.md) · [ABBREVIATIONS.md](docs/ABBREVIATIONS.md) · [DATA_MODEL.md](docs/DATA_MODEL.md)

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
