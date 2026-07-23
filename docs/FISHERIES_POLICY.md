# India's Fisheries Policy Apparatus — Detailed Note

*Companion to layer 33 (`layers/33_policy_finance_extensions.json`, fisheries block).
Researched 2026-07-23; every figure carries its source in the layer; HTTP statuses
verified from this machine. This note is hand-written — re-read the layer before
citing figures.*

---

## 1. The apparatus

Fisheries sits in an unusual dual structure:

- **Department of Fisheries (DoF)**, Ministry of Fisheries, Animal Husbandry &
  Dairying — owns the production-side incentive stack (PMMSY, PM-MKSSY, FIDF).
  `dof.gov.in` → 200; `pmmsy.dof.gov.in` → 200.
- **MPEDA** (Marine Products Export Development Authority, under **Commerce**) —
  owns the export side: promotion, exporter registration, quality/traceability,
  and the TDSVMP processing-upgrade subsidy. `mpeda.gov.in` → 200.
- Support institutions: **NFDB** (National Fisheries Development Board, PMMSY
  nodal agency — 🔴 unreachable from this machine, NIC IP times out), **RGCA**
  (MPEDA's R&D arm: SPF shrimp broodstock, seabass, mud crab — 🔴 DNS SERVFAIL),
  and the National Fisheries Digital Platform (**NFDP**, `nfdp.dof.gov.in` → 200),
  which is now the registration gateway for the whole sector.

The split matters to an investor: *capex subsidies come from DoF; export
entitlements, certification and the processing-upgrade money come from MPEDA.*

## 2. PMMSY — the umbrella (₹20,050 cr, FY21–25, extended to FY26)

The Pradhan Mantri Matsya Sampada Yojana is the sector's flagship, structured as
centrally-sponsored (states co-fund) plus central-sector components.

**Funded status** (the twin's key numbers):
- Approved projects: **₹21,394.88 cr** — already *above* the nominal outlay —
  with central share ₹9,510.89 cr (Rajya Sabha reply, 22-Jul-2026)
- Earlier marker: ₹20,864.29 cr approvals as of Dec-2024 (PIB)
- Extended by the Department of Expenditure **up to FY2025-26** on the existing
  design and funding pattern — i.e. the current fiscal year is the tail
- The **National Framework on Traceability in Fisheries and Aquaculture 2025**
  has been released — the compliance rail exporters will be measured against

**What companies actually get**: beneficiary-oriented components pay **40%
capital assistance (general) / 60% (SC/ST/women)** across hatcheries, ponds,
RAS, feed mills, ice plants, cold storage, processing, transport (incl. reefer),
and marketing infrastructure.

⚠️ A "₹2,500 cr Budget 2026-27 fisheries allocation" circulates on unofficial
scheme-guide sites only — **unconfirmed against any official source**; the twin
records it as such. Do not cite it.

## 3. PM-MKSSY — the formalization sub-scheme (₹6,000+ cr, FY24–27, FINAL YEAR)

The Matsya Kisan Samridhi Sah-Yojana is a central-sector sub-scheme aimed at
formalizing the sector's micro/small end. Four components:

| Component | What it pays |
|---|---|
| 1A | Self-registration of fishers/enterprises on **NFDP** (the sector's identity layer) |
| 1B | One-time **aquaculture insurance incentive** for farms up to 4 ha WSA |
| 2 | Credit facilitation (bank linkage) |
| 3 | **Performance grants** to micro/small fisheries enterprises for safety & quality systems |

**Timing signal**: FY2026-27 is the scheme's final year — enterprises that want
the insurance incentive or performance grants need to be registered on NFDP now.
Apply via `nfdp.dof.gov.in` (200) or myScheme (200); 🔴 the dedicated portal
`pmmkssy.dof.gov.in` is TCP-refused from this machine — recorded as data.

## 4. FIDF — the concessional-credit leg (₹7,522.48 cr, extended to 2025-26)

The Fisheries & Aquaculture Infrastructure Development Fund is the debt-side
instrument — not a grant, but an **interest subvention of up to 3% p.a.** with
the nodal lender's rate floored at 5%, **12-year tenure including a 2-year
moratorium**. Nodal loaning entities: NABARD, NCDC, and all scheduled banks.

**Utilization (as of Mar-2026)**: 228 projects approved, ₹5,559.54 cr total cost
(₹4,351.86 cr subvention-eligible); loans sanctioned for 111 projects
(₹4,212.05 cr); **₹1,600.56 cr disbursed** — a sanction-to-disbursal lag worth
pricing in.

**The state usage pattern is lopsided**: Tamil Nadu is the largest user by far
(108 projects, ₹2,169.03 cr — mostly fishing harbours), then Maharashtra (42,
₹1,230.90 cr) and Gujarat (₹984.74 cr). Most coastal states barely use it —
which means uncontested headroom for a company that brings a bankable project.

**Eligible assets**: fishing harbours, ice plants, cold storage, integrated cold
chain, **fish feed mills/plants**, processing units, hatcheries, cage culture,
mariculture.

🔴 Portal note: the real FIDF portal is **`fidf.in`** (200); `fidf.dof.gov.in`
is NXDOMAIN.

## 5. The export machine — MPEDA and the tariff year

**FY2025-26 was a record despite the US tariff shock**:

| Metric | FY25 | FY26 |
|---|---|---|
| Volume | 16,98,170 t | **19,72,018 t** |
| Value | ₹62,408 cr ($7.45 bn) | **₹73,890.46 cr ($8.46 bn)** |
| Frozen shrimp share of USD earnings | 69.46% | 66.52% |

**The US tariff timeline** (the single biggest exogenous variable):
1. Oct-2024: final CVD 5.63–5.87% + AD 0–2.49% on frozen warmwater shrimp
2. Apr–Aug-2025: IEEPA "reciprocal" tariffs escalate 10% → 25% → 50% (second
   25% tied to Russian-oil purchases) — **~58% effective** on Indian shrimp
3. FY26 result: US shipments **−19.51% by volume** (CRISIL had projected
   −15–18%) — but record diversion to China, EU and SE Asia more than covered it
4. **Feb-2026 US-India trade deal cuts the reciprocal tariff to 18%** (AD/CVD
   remain on top) — partial restoration of US competitiveness
5. Still pending: the proposed "India Shrimp Tariff Act" (progressive 40%
   shrimp-specific duty) — a bill, not law

**MPEDA money**: the TDSVMP processing-technology scheme disbursed **₹118.10 cr
to 89 processing units** (FY22–FY26) — small per-unit but real.

**Access notes**: MPEDA stats are PDF-only (no API); WordPress pretty-URLs 404 —
use `?page_id=` URLs; the **exporter registry is scrapeable** at the
`e-mpeda.nic.in` ASP.NET report pages (200).

## 6. The state layer

| State | What's verified |
|---|---|
| **Tamil Nadu** | Largest FIDF borrower (108 projects, ₹2,169 cr) — harbour-infrastructure-led |
| **Andhra Pradesh** | Largest PMMSY user (~₹2,398.72 cr approved); interest subsidy extends to **feed/seed manufacturers**; concessional aqua power tariff |
| **Odisha** | Fisheries Policy 2015 (PDF verified) — and the sharper instrument: **Food & Seafood Processing is an IPR-2022 Priority Sector**, so processors get the 20% *uncapped* capital-subsidy + 100% net-SGST stack (see layer 33 × state-policy doc) |
| **Kerala** | Department scheme set verified (aquaculture promotion) |
| **Gujarat** | Commissioner-of-Fisheries assistance (hatcheries, shrimp-farm construction, equipment) |

## 7. Investment lanes — who funds what

| Lane | Funding stack |
|---|---|
| **Shrimp/fish feed mills** | FIDF concessional debt (3% subvention) **+** PMMSY 40/60% capital assistance **+** AP's feed-manufacturer interest subsidy — the deepest stack in the sector |
| **Processing plants** | PMMSY post-harvest 40/60% **+** FIDF (18 plant expansions funded, ₹345.89 cr) **+** MPEDA TDSVMP **+** PM-MKSSY quality-system grants (micro/small) **+** Odisha IPR priority stack if sited there |
| **Cold chain** | FIDF "Integrated Cold Chain (Marine & Inland)" + PMMSY ice plants/cold storage. ⚠️ **Routed through FIDF/PMMSY, not the Agriculture Infrastructure Fund** — AIF's post-harvest list targets agri produce; fisheries has its own dedicated fund |
| **Hatcheries/broodstock** | PMMSY + RGCA programs (SPF broodstock multiplication) — RGCA's own site unreachable, work through MPEDA |

## 8. The investor read

- **Stack example**: a feed-mill or processing project in AP or Odisha can
  combine PMMSY capital assistance + FIDF concessional debt + the state's own
  subsidy/priority-sector stack — three instruments, none mutually exclusive on
  the record the twin holds.
- **Timing**: PM-MKSSY closes after FY27; PMMSY's extension runs to FY26 —
  both argue for applications this fiscal year. FIDF's sanction-to-disbursal
  lag (₹4,212 cr sanctioned vs ₹1,601 cr disbursed) says model conservative
  drawdown timelines.
- **Tariff risk is priced but volatile**: the 18% post-deal rate restores US
  math, but AD/CVD reviews continue (May-2026 preliminary results published)
  and the 40% bill remains pending.
- **Compliance direction**: the 2025 Traceability Framework + NFDP registration
  are becoming the de-facto license to operate/export — early registration is
  cheap optionality.

## 9. Twin linkages and gaps

- **Foreign lead**: Charoen Pokphand Foods (Thailand, layer 16) — world-scale
  shrimp-feed player with India aquaculture operations; the FIDF feed-mill lane
  is its natural instrument.
- **Gap recorded as data**: the EC/FC clearance pool (layers 24b/24e) contains
  **no seafood-processing filers** — the earlier "marine" hits were
  pigment/aero false positives. Either the sector expands below the EC
  threshold, or through state single-window routes the register doesn't
  capture. Worth a dedicated PARIVESH re-query with fisheries-specific
  activity terms.
- **Access map for future sessions**: working — pmmsy.dof.gov.in, fidf.in,
  nfdp.dof.gov.in, mpeda.gov.in (`?page_id=` form), e-mpeda.nic.in registry;
  blocked from this machine — nfdb.gov.in (timeout), pmmkssy.dof.gov.in
  (TCP-refused), rgca.org.in (DNS SERVFAIL).
