# Policy Comparison Workbook — Summary

*Companion to [STATE_POLICY_COMPARISON.md](STATE_POLICY_COMPARISON.md). The workbook
(`Policy Comparison.xlsx`) is maintained offline in the user's Google Drive; this page
records its structure and headline content so the repo carries the summary. Built
2026-07-23 from layers 12/13/17/18/31 — verified-on-site claims only.*

## Sheet inventory (18 sheets)

| Sheet | Contents |
|---|---|
| `Sheet1` / `Sheet2` | Original template (15 incentive categories × country columns; country list) — untouched |
| **India State Stackup** | 16 states × 8 investor decision columns: umbrella policy + status, headline capital/tax offer, central-stacking rule, sector verticals, arrears record, transparency, investor note. Orange = payment-risk flags, green = best-in-class transparency |
| **Category × State Matrix** | The template's 15 incentive categories (Tax, Subsidies, Workforce, Infrastructure, R&D, IP, Clusters, Energy, Regulatory, Loans, Waivers, Trade…) × 10 major states, every cell a concrete verified instrument |
| **Sector Verticals × State** | 13 verticals × 12 states + "Other states (notable)"; green cell per row = strongest verified offer |
| **V-*** (13 sheets) | One per sector focus: central-lane banner (which central scheme the state policies stack on, with live window status), per-state rows (policy + year, verified terms, stacking rule, caveat), gap-flag rows for thin verticals |

## Headline content

### Investor decision variables (Stackup sheet)

Umbrella policy texts converge, so the sheet is organized around what actually
differs: **(a)** central-stacking top-up size, **(b)** arrears record, **(c)**
disbursal transparency.

- **Verified stacking rules**: UP (ECMS top-up equal to central grant — doubling),
  Assam (+40% of ISM capex), AP (10% of PLI), Kerala (20% of eligible central schemes).
- **Payment-risk flags (orange)**: Telangana ₹3,736 cr confirmed arrears; AP
  ₹3,000–5,000 cr pending; Punjab's Q1-FY26 catch-up admission; J&K ~₹83 cr FY24
  approvals vs ₹28,400 cr outlay; Odisha ₹15 cr/yr provision vs ₹24,823 cr MoU
  pipeline; 5 states with UNVERIFIED aggregate disbursals.
- **Transparency (green)**: Rajasthan — annual press-released RIPS disbursals
  (₹765.78 cr FY25, +293%).
- **Live transition risks**: Maharashtra (PSI-2019 closed, MIISP-2025 rules
  settling), Haryana (HEEP-2020 expires 2025-12-31, successor awaited).

### Sector-vertical leaders (green cells, Verticals sheet)

| Vertical | Strongest verified offer |
|---|---|
| Semiconductor / ESDM | **Assam** — +40% of ISM capex over 5 yrs, nominal land, 100% stamp (Tata OSAT precedent); UP's ECMS doubling for components |
| EV / Auto | **Tamil Nadu** — choice of 100% SGST 15 yrs / turnover subsidy / capital subsidy + battery-ACC special |
| Pharma / Life Sciences | **Telangana** — Next-Gen Life Sciences 2026-30 (Genome Valley; 100% stamp reimbursement, power Re 1/unit) |
| IT / GCC | **Karnataka** — GCC Policy 2024-29, India's first (rent 50% cap ₹2 cr, EPF ₹3,000/emp/mo, Beyond-Bengaluru weighting) |
| Textiles | **Gujarat** — Textile Policy 2024 + live registration workflow |
| Defence / Aero | **UP** — corridor-node-tied capital subsidy (+ Defence Policy 2025 page) |
| Data centres | **UP** — DC Policy 2021 + new 2026 policy, dual-grid power (thinnest vertical: 2 states verified) |
| Green hydrogen | **Odisha** — 20-yr electricity-duty exemption + ₹3/unit power reimbursement, embedded in IPR-2022 (2 states verified vs OPEN central SIGHT window — policy gap) |
| Renewables / Storage | **Uttarakhand** — Solar 2023 + Pumped Storage 2023 (+ Rajasthan's RIPS-embedded green-growth) |
| Food processing | **Odisha** — Priority-sector status ⇒ 20% uncapped capital subsidy stack |
| Logistics | **Maharashtra** — Logistics 2024 + Park Policy 2018 |
| Startups / R&D | **Tamil Nadu** — R&D 2022 (25% capex, cap ₹25 cr, intangibles to 20% of EFA) + FinTech 2021 |
| Niche | **Telangana** — "Meet or Beat": matches any competing state's offer (>USD 30 mn / >1,000 jobs) |

### Honesty conventions carried into every sheet

- "—" = not verified in the twin's catalog, **not** proof of absence; thin verticals
  carry explicit gap-flag rows pointing to the layer-31 Invest India state-page PDF
  carousels as the feed to close them.
- Customs/tariffs and trade rows note these are central-government domain; the state
  lever is stamp-duty/electricity-duty waivers.
- Terms marked "not machine-extracted" (TN semiconductor GO, MP Feb-2025 wave,
  Marathi-language MIISP GR) must be read from the policy PDF before financial
  modelling.
- Window statuses rot: check `layers/17_scheme_monitor.json` + `state/` snapshots
  before relying on any scheme being open.
