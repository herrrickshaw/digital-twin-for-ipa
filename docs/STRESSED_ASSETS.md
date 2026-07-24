# Stressed / Distressed Assets — Consolidated View

*Layer 34 (`layers/34_stressed_assets.json`). Consolidates three
previously-scattered stressed-asset signal sources. Built 2026-07-23. The twin
holds **signals**, not a formal NPA/IBC register — see caveats.*

---

## 1. Company distress flags (twin DB — `stressed_assets` view)

Rating-channel and litigation signals on companies the twin already tracks.
Query live: `sqlite3 data/companies.db "SELECT * FROM stressed_assets WHERE …"`.
Classification uses a grade parser (current grade only — an *upgrade from* BBB+
is not stress; sub-IG = BB+ and below).

| Flag | Companies |
|---|---|
| **rating_darkness** (issuer-not-cooperating / withdrawn) | Matangi Industries LLP (CARE BBB, INC Mar-2026 — same quarter as its EC filings), Sandhya Organic Chemicals (CRISIL INC), D R Coats Ink & Resins (CRISIL INC since 2018), Jayshree Aromatics (Brickwork INC) |
| **litigation_or_regrade** | RSLD Biofuels — unrated, but CARE's parent rationale disclosed SEBI/IT/ED promoter litigations → HIGH-RISK regrade |
| **watch_negative** | Nayara Energy (CARE AA- RWN, post-Rosneft sanctions), Sigachi Industries (CARE BBB, watch + downgrade post-accident) |
| **downgrade** | Orchid Pharma (CARE A- RWD → BBB+ Apr-2026) |
| **sub_investment_grade** (BB+ and below, current) | Atharv Intertrade (CARE B+), Karimganj Biofuels (Infomerics BB+), Keyaan Distilleries (standalone BB+, CE-propped to BBB+) |

Note the overlap with the **E20 ethanol cohort** (RSLD, Karimganj, Keyaan,
Atharv, Bapuna-group) — the Lalta-Prasad state-fee risk (layer 33) compounds
their rating stress.

## 2. National distressed-LAND supply channels (from policy-recs repo)

Pulled live from `india-trade-sector-policy-recommendations/data/stressed_distressed_land_2026-07-22.json`.
This is the aggregate **supply pool** an investor buys distressed factory land from:

| Channel | Scale |
|---|---|
| **IBC liquidation** | 1,436 corporate-debtor liquidations ONGOING (of 2,728 entered); 824 running >2 yrs. Manufacturing ≈40% of CIRP admissions. For the 211 largest cases, assets valued ~₹0.45 tn against ₹9.59 tn admitted claims — steeply distressed |
| **Closed PSU / NLMC** | 26 closed CPSEs; ~3,400 acres surplus land referred to DIPAM; NLMC (100% GoI SPV) monetising |
| **Resumed plots** | State corporations cancel-and-reallot: GIDC ~1,800 ha, + UPSIDA/MIDC/RIICO |
| **ARC / SARFAESI** | ARCs (NARCL, ARCIL…) + secured lenders auction mortgaged industrial property (count not centrally disclosed) |

**Named liquidation assets already tracked**: Vindhyavasini Steel (MIDC Murbad,
~11,514 sqm), General Composites (Thane, ~42,200 sqm slump sale), Eurotas
Infrastructure (Nashik), Anmol Steel, Piaggio Vehicles plot (UPSIDA Surajpur,
33 acres cancelled), BSNL freehold (NLMC pilot, 8.7 acres).

## 3. Worked case — Dunlop India Ltd. (litigation case map)

The template for an individual manufacturer stressed asset: a wound-up factory
whose **land is the residual value**, tied up in multi-forum litigation.

- **Distress**: sick under SICA 1985 → wound up by Calcutta HC 31-Jan-2013
  (C.P. 233/2008); Official Liquidator in possession. Ownership trail
  Chhabria (Jumbo) → Ruia (2005). Allegation: ~₹2,300 cr of four properties
  transferred surreptitiously while before BIFR.
- **Asset thread TN** — Ambattur, Chennai: ~60.86 acres assigned land, sold
  ₹24.34 cr (2004) to V.N. Devadoss via BIFR/AAIFR; GoTN held sale in breach
  (G.O. Ms. 183, 2008); challenges dismissed on res judicata; SC Devadoss
  stamp-duty ruling 2009.
- **Asset thread WB** — Kings Court, 46B Chowringhee, Kolkata: Dunlop's 50%
  share (valuation ₹29.44 cr, 2024) under OL auction; contested by Salasar
  Towers (pre-emption) and Eyelid Mercantiles (unregistered 2006 agreement —
  no title, per *Suraj Lamp*). Lead judgment **17-Mar-2026** (J. Raja Basu
  Chowdhury): auction stands, Salasar may match, Eyelid gets liberty to sue
  for specific performance.
- Plus: 62A Mirza Ghalib St (OL possession), Worli Mumbai, Sahaganj plant
  (~228 acres, suspended 2011).
- **Status**: live liquidation; verify current auction status before acting
  (indiankanoon.org/doc/110197805).

## 4. The register — IBBI liquidation auction notices (LIVE)

The one machine-readable per-asset stressed-asset feed in India, now ingested.
`scripts/register_ibbi_liquidation.py` scrapes the server-rendered table (no
auth, `?page=N`, 20 rows/page, ~481 pages to inception) into a durable parquet
(`data/registers/ibbi_liquidation.parquet`) + the `ibbi_auction_notices` DB
table, and cross-matches corporate-debtor names against the twin's companies
(shared tiered matcher). Manual/on-demand (duckdb → run with `/usr/bin/python3`):
`--all` for the full history, `--pages N` to top up recent notices.

Structured fields per notice: **corporate debtor · auction date · reserve
price (₹) · nature of assets · EMD deadline · insolvency professional · notice
PDF**. This turns the aggregate "IBC liquidation 1,436 ongoing" pool of §2 into
named, priced, dated assets. See the `register` block in
`layers/34_stressed_assets.json` for the top-by-reserve-price list, asset-type
mix, and any twin-company matches.

### Other registers (routes named — reference)
| Register | URL | Twin status |
|---|---|---|
| NLMC | nlmc.dpe.gov.in | reference |
| SARFAESI / ARC | auctiontiger.in · bankeauctions.com · narcl.co.in | reference |
| State resumed plots | GIDC · UPSIDA · MIDC MILAAP · RIICO | overlaps layer-25 IILB data |

## Caveats

- Section 1 = **rating/litigation signals on the twin's own tracked companies**,
  not an exhaustive stressed-asset universe.
- No single official "total acres in IBC liquidation" figure exists — IBBI
  publishes process counts, not acreage.
- Dunlop facts are from a due-diligence workbook; the 17-Mar-2026 judgment is
  the latest known — verify live auction status before acting.
- **Next**: wire the IBBI liquidation-auction-notice list as the machine-readable
  per-asset stressed feed the twin currently lacks.
