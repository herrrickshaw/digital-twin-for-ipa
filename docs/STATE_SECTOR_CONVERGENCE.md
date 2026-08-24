# State x sector convergence — layer 43

*Generated 2026-08-24 by `scripts/build_layer43_state_sector_convergence.py`. 81 revealed investment-event state mentions (layer 42), 939 policy-eligible state landings (layer 16, 321 companies). DPIIT's IEM data does not publish a joint state×sector matrix — see methodology note below.*

## Methodology

Two genuinely different signals, shown side by side, never summed:

- **Revealed** — real, dated, individually-verified company investment/JV/plant events (layer 42), state/city extracted from the actual announcement text. Small N, high confidence — this is what companies have *actually done*. Caveat: a handful of MEDIUM-confidence findings describe a company still *evaluating between* multiple candidate states (e.g. LG Energy Solution's battery JV, reportedly weighing Tamil Nadu/Telangana/Andhra Pradesh) rather than a completed site decision — each candidate state is counted once, so these inflate event counts slightly versus a true one-state landing. Cross-check the `confidence` field per row in the JSON before treating any single event as a done deal.
- **Policy-eligible** — which states' scheme stacks (PLI top-ups, land, capital subsidy) make a company's sector eligible to land there (layer 16 leads' `state_landings`, 321 companies). Larger N, but structural/eligibility only — a state appearing here doesn't mean any company has chosen it yet.

DPIIT's own IEM data (data.gov.in, checked live 2026-08-24, current through Aug 2026) is cited below as independent reference — but DPIIT publishes only separate state-total and industry-total marginals, never a joint state×sector cross-tabulation, so it cannot itself answer "which states are converging on which sectors"; it corroborates scale/rank only.

## DPIIT IEM — state totals (reference, national, cumulative)

*Source: https://www.data.gov.in/resource/state-wise-iem-part-data-investment-and-employment-august-1991-till-last-month, as of 2026-08-15.*

| State | IEM count | Investment (₹ lakh) | Employment |
|---|---|---|---|
| GUJARAT | 14709 | 2310357 | 3053318 |
| ODISHA | 2354 | 2248216 | 1120737 |
| MAHARASHTRA | 20720 | 2069429 | 20612795 |
| KARNATAKA | 5644 | 1635266 | 2228609 |
| CHATTISGARH | 3690 | 1627684 | 1328457 |
| ANDHRA PRADESH | 4896 | 1053475 | 1315173 |
| MADHYA PRADESH | 4936 | 992945 | 1441751 |
| WEST BENGAL | 5589 | 760578 | 1443269 |
| TAMIL NADU | 8700 | 582256 | 2727154 |
| JHARKHAND | 1242 | 484889 | 439913 |
| UTTAR PRADESH | 8442 | 481539 | 16291044 |
| RAJASTHAN | 4683 | 406039 | 1128949 |
| TELANGANA | 4469 | 300901 | 766299 |
| BIHAR | 590 | 188367 | 125134 |
| HARYANA | 5135 | 187687 | 917522 |

## DPIIT IEM — industry totals (reference, national, cumulative)

*Source: https://www.data.gov.in/resource/industry-wise-iem-part-data-investment-and-employment-august-1991-till-last-month, as of 2026-08-15.*

| Industry | IEM count | Investment (₹ lakh) | Employment |
|---|---|---|---|
| GRAND TOTAL | 112521 | 15696491 | 65850319 |
| ELECTRICALS EQUIPMENT | 8814 | 4762276 | 2196623 |
| METALLURGICAL INDUSTRIES | 16192 | 2936295 | 3951144 |
| OTHERS | 12029 | 2246990 | 39467457 |
| CHEMICALS (OTHER THAN FERTILIZERS) | 11822 | 1204844 | 1642602 |
| CEMENT & GYPSUM PRODUCTS | 2979 | 758704 | 873039 |
| FUELS | 744 | 584167 | 198025 |
| TEXTILES | 14166 | 514782 | 5835158 |
| TRANSPORTATION INDUSTRY | 2436 | 330108 | 900507 |
| FERTILIZERS | 1131 | 295725 | 162448 |
| FOOD PROCESSING INDUSTRY | 6277 | 248032 | 1517788 |
| SUGAR | 3550 | 242730 | 1186423 |
| MISCELLANEOUS MECHANICAL & ENGINEERING INDUSTRIES | 4540 | 202248 | 2616661 |
| FERMENTATION INDUSTRIES | 2634 | 196305 | 335753 |
| COMMERCIAL , OFFICE  AND HOUSEHOLD EQUIPMENT | 755 | 179845 | 439221 |

## Multi-sector hub states

States where either signal shows real breadth — ≥3 distinct sectors (revealed) or ≥5 distinct sectors (policy-eligible).

| State | Revealed sectors | Revealed events | Policy sectors | Policy companies |
|---|---|---|---|---|
| **Maharashtra** | 10 (Aerospace & Defence, Auto, EV & Components, Chemicals & Plastics, Electronics & Semiconductors, Food Processing, Medical Devices, Shipbuilding & Marine, Specialty Steel & Metals, Textiles & Apparel, White Goods & Electricals) | 14 | 1 | 16 |
| **Gujarat** | 7 (Aerospace & Defence, Chemicals & Plastics, Electronics & Semiconductors, Food Processing, Green Energy & Fuels, Medical Devices, Shipbuilding & Marine) | 12 | 5 | 131 |
| **Tamil Nadu** | 6 (Auto, EV & Components, Electronics & Semiconductors, Food Processing, Green Energy & Fuels, Medical Devices, White Goods & Electricals) | 9 | 6 | 136 |
| **Karnataka** | 6 (Aerospace & Defence, Chemicals & Plastics, Electronics & Semiconductors, Food Processing, Pharma & Bulk Drugs, Specialty Steel & Metals) | 7 | 1 | 26 |
| **Andhra Pradesh** | 5 (Auto, EV & Components, Green Energy & Fuels, Medical Devices, Specialty Steel & Metals, White Goods & Electricals) | 9 | 2 | 39 |
| **Telangana** | 4 (Aerospace & Defence, Green Energy & Fuels, Medical Devices, Pharma & Bulk Drugs) | 7 | 2 | 40 |
| **Uttar Pradesh** | 3 (Electronics & Semiconductors, Food Processing, White Goods & Electricals) | 5 | 4 | 111 |

## Full state convergence table

| State | Revealed sectors | Revealed events | Policy sectors | Policy companies |
|---|---|---|---|---|
| Maharashtra | 10 | 14 | 1 | 16 |
| Gujarat | 7 | 12 | 5 | 131 |
| Tamil Nadu | 6 | 9 | 6 | 136 |
| Karnataka | 6 | 7 | 1 | 26 |
| Andhra Pradesh | 5 | 9 | 2 | 39 |
| Telangana | 4 | 7 | 2 | 40 |
| Uttar Pradesh | 3 | 5 | 4 | 111 |
| Odisha | 2 | 3 | 3 | 104 |
| Delhi | 2 | 2 | 0 | 0 |
| Haryana | 2 | 3 | 0 | 0 |
| Kerala | 2 | 3 | 0 | 0 |
| West Bengal | 2 | 2 | 0 | 0 |
| Madhya Pradesh | 1 | 1 | 2 | 58 |
| Rajasthan | 1 | 1 | 2 | 65 |
| Assam | 1 | 1 | 1 | 41 |
| Chhattisgarh | 1 | 1 | 1 | 39 |
| Punjab | 1 | 1 | 0 | 0 |
| Jharkhand | 0 | 0 | 2 | 69 |
| Himachal Pradesh | 0 | 0 | 2 | 40 |
| Sikkim | 0 | 0 | 1 | 24 |

## Per-sector state rankings

### Aerospace & Defence

**Revealed (real events):** Telangana (3), Maharashtra (3), Haryana (2), Karnataka (2), Delhi (1), Gujarat (1)

**Policy-eligible (companies):** Karnataka (26), Uttar Pradesh (26), Tamil Nadu (26)

### Auto, EV & Components

**Revealed (real events):** Tamil Nadu (3), Maharashtra (1), Haryana (1), Andhra Pradesh (1)

**Policy-eligible (companies):** Tamil Nadu (28), Madhya Pradesh (28), Uttar Pradesh (28)

### Chemicals & Plastics

**Revealed (real events):** Gujarat (3), Maharashtra (1), West Bengal (1), Karnataka (1), Kerala (1)

**Policy-eligible (companies):** Gujarat (35), Odisha (35), Rajasthan (35)

### Electronics & Semiconductors

**Revealed (real events):** Gujarat (4), Uttar Pradesh (2), Karnataka (1), Tamil Nadu (1), Maharashtra (1)

**Policy-eligible (companies):** Uttar Pradesh (41), Assam (41), Tamil Nadu (41), Gujarat (41)

### Food Processing

**Revealed (real events):** Uttar Pradesh (2), Karnataka (1), Maharashtra (1), West Bengal (1), Assam (1), Madhya Pradesh (1), Tamil Nadu (1), Gujarat (1), Odisha (1), Rajasthan (1), Punjab (1)

**Policy-eligible (companies):** Andhra Pradesh (30), Madhya Pradesh (30), Jharkhand (30)

### Green Energy & Fuels

**Revealed (real events):** Andhra Pradesh (2), Gujarat (1), Tamil Nadu (1), Telangana (1)

**Policy-eligible (companies):** Odisha (30), Gujarat (30), Rajasthan (30)

### Medical Devices

**Revealed (real events):** Tamil Nadu (2), Andhra Pradesh (2), Gujarat (1), Telangana (1), Delhi (1), Maharashtra (1)

**Policy-eligible (companies):** Telangana (16), Tamil Nadu (16), Himachal Pradesh (16)

### Pharma & Bulk Drugs

**Revealed (real events):** Telangana (2), Karnataka (1)

**Policy-eligible (companies):** Telangana (24), Himachal Pradesh (24), Sikkim (24)

### Shipbuilding & Marine

**Revealed (real events):** Kerala (2), Maharashtra (2), Gujarat (1)

**Policy-eligible (companies):** Gujarat (9), Andhra Pradesh (9), Tamil Nadu (9)

### Specialty Steel & Metals

**Revealed (real events):** Odisha (2), Karnataka (1), Maharashtra (1), Andhra Pradesh (1), Chhattisgarh (1)

**Policy-eligible (companies):** Odisha (39), Chhattisgarh (39), Jharkhand (39)

### Textiles & Apparel

**Revealed (real events):** Maharashtra (1)

**Policy-eligible (companies):** Tamil Nadu (16), Gujarat (16), Maharashtra (16), Uttar Pradesh (16)

### White Goods & Electricals

**Revealed (real events):** Andhra Pradesh (3), Maharashtra (2), Uttar Pradesh (1), Tamil Nadu (1)

