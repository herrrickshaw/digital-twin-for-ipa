# digital-twin-for-ipa

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
