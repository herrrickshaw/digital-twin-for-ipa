# Data model & information flow

The twin's canonical extraction model lives in [`layers/00_data_model.json`](../layers/00_data_model.json); every sweep and refresh maps into its nine entity types. The flat, query-ready product is [`layers/13_flat_instrument_index.json`](../layers/13_flat_instrument_index.json) — **312 instruments** (120 central v2 + 75 central v1 + 117 state) in one schema. The refresh design is [`layers/14_update_engine.json`](../layers/14_update_engine.json).

## Information flow — sources → model → products

```mermaid
flowchart TD
    subgraph SOURCES["Sources (per-source cadence)"]
        PIB["PIB register<br/>122,141 releases · daily<br/>(pib_index.py)"]
        MIN["Ministry sites<br/>via SourceRoute registry:<br/>headless-WP cms-*.digifootprint,<br/>backend APIs, browser, OCR"]
        STATE["State single-windows<br/>IFP · MAITRI · TNSWP · KYI<br/>dashboards (disbursal evidence)"]
        NSWS["NSWS<br/>the only official<br/>company-facing aggregator"]
        UNNATI["UNNATI portal<br/>notice diff (resumption watch)"]
        PRS["PRS Legislative Research<br/>DFG utilization + Bill Track"]
        FDI["DPIIT FDI quarterly<br/>+ RBI WSS archive"]
        CO["Company data<br/>NOW: Damodaran + yfinance + screener.in<br/>TARGET: Orbis (BvD-ID, ownership trees)<br/>free proxies: GLEIF LEI, MCA, OpenCorporates"]
    end

    subgraph MODEL["Canonical model (layers/00)"]
        OE["OfferingEntity<br/>86 central + 30 states"]
        INS["Instrument<br/>312 normalized"]
        AW["ApplicationWindow<br/>open/closed/oversubscribed"]
        EDGE["InterlinkageEdge<br/>23 stacks/excludes/feeds"]
        BUD["BudgetObservation<br/>PRS utilization"]
        COMP["Company 19,795"]
        PAIR["Pairing<br/>verified/prospective/stalled"]
        SR["SourceRoute<br/>access health incl. hijacked domains"]
        OBS["Observation (append-only,<br/>corrections displayed)"]
    end

    subgraph PRODUCTS["Products"]
        IDX["flat_instrument_index"]
        BULL["Bulletins + charts<br/>(policy repo)"]
        QTW["Quarterly Trade Watch<br/>+ FY series"]
        MAP["Investor map + pairings"]
    end

    PIB --> INS & AW & OE
    MIN --> INS & SR
    STATE --> INS & OBS
    NSWS --> AW
    UNNATI --> AW
    PRS --> BUD
    FDI --> OBS
    CO --> COMP & PAIR

    OE --> INS --> AW
    INS --> EDGE
    INS --> IDX
    EDGE & BUD --> BULL
    AW & OBS --> QTW
    COMP --> MAP
    PAIR --> MAP
    INS -.stacking evidence.-> EDGE
```

## Refresh cadence

| Trigger | Sources | Updates |
|---|---|---|
| Daily | PIB `--update` | new launches, windows |
| Weekly | NSWS, RBI WSS, UNNATI notice | window status, forex context |
| Monthly | top-20 instrument pages | guideline changes |
| Quarterly | full agent sweep, PRS DFG, DPIIT FDI | everything; Trade Watch rebuild |
| Event | Cabinet PRID keyword match, gazette upload, UNNATI notice text change | targeted re-verify |

**Corrections rule** (inherited program-wide): superseded values are retained with a `superseded_on` date and displayed — never silently overwritten. Type case: PM E-DRIVE "closure" that was actually a segment-wise extension.

**Known coverage gap**: unlisted companies. Orbis would close it (ownership trees, unlisted financials) but requires a license; until then GLEIF LEI + MCA + OpenCorporates are the free partial proxies, and the Company entity carries a `bvd_id` slot ready for the upgrade.
