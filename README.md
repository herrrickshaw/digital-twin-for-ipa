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
