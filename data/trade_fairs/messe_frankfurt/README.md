# Messe Frankfurt trade-fair exhibitor data

Collected 2026-08-22 for the company-targeting database (foreign companies with India
investment/market interest). Deep-dive follow-up to the CANDIDATE entries scoped in
`layers/40_association_event_registry.json` (Light + Building, ISH, Heimtextil), extending
the technique that already worked for Automechanika Frankfurt (see that fair's entry in the
same registry).

## The platform: `exhibitor-service` API, shared across ALL Messe Frankfurt shows

Every Messe Frankfurt fair's `<subdomain>.messefrankfurt.com/frankfurt/en/exhibitor-search.html`
page mounts a small JS widget (`<div id="mf-ex-root" data-config='{...}'>`) whose config carries
an `API_EVENT_ID` (e.g. `LIGHTBUILDING`, `ISH`, `HEIMTEXTIL`, `AUTOMECHANIKA`, `AMBIENTE`,
`TECHTEXTIL`). Despite the config's `API_URL` pointing at `exhibitorsearch.messefrankfurt.com`
(which 404s), the real live traffic (confirmed via a browser network-request capture on
`automechanika.messefrankfurt.com/frankfurt/en/exhibitor-search.html?country=IND`) goes to a
**different host**:

```
GET https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search
    ?language=en-GB&q=&orderBy=name&pageNumber=1&pageSize=200
    &orSearchFallback=false&showJumpLabels=true
    &findEventVariable=<EVENT_ID>          (optional -- see below)
    &country=<ISO3>                        (optional filter)
Header: apikey: LXnMWcYQhipLAS7rImEzmZ3CkrU033FMha9cwVSngG4vbufTsAOCQQ==
```

The `apikey` is a **public** key baked into the SPA's own `main.js` bundle (client-side,
served to every visitor's browser — not a secret, same access level as using the website).
Plain `curl`/`urllib` works fine with it; no live browser needed once you have the key.
Response JSON: `result.metaData.hitsTotal` / `result.hits[].exhibitor.{name, address:
{city, email, country:{iso3, label}}, homepage, exhibition:{id, name}}`.

**Major finding — this is the "broader Messe Frankfurt directory" the task asked to check
for**: omitting `findEventVariable` does NOT error or default to one show — it searches
**across every Messe Frankfurt fair globally in one query**. `q=""` with no event filter
returned `hitsTotal: 49665`, with hits spanning shows like Beautyworld Japan Fukuoka,
Interior Lifestyle Tokyo, Arminera 2025 (Argentina), Interpets Tokyo — i.e. this single
endpoint is a **unified cross-show search**, not per-fair. Adding `country=IND` with no
event filter returned **3,114** India-HQ'd exhibitors across the entire global Messe
Frankfurt show portfolio (see `messefrankfurt_global_india_exhibitors.*` if present in this
folder — bonus pull beyond the 3 named fairs, same session).

Extraction script: `scripts/scratch_messe/mf_exhibitor_pull.py` (per-fair) and
`scripts/scratch_messe/mf_global_india_pull.py` (cross-show, country-filtered).

## Fairs deep-dived this pass

| Fair | API_EVENT_ID | Total exhibitors | Top countries | File |
|---|---|---|---|---|
| Light + Building | `LIGHTBUILDING` | 1,884 | China 497, Germany 411, Italy 150, Hong Kong 135, Türkiye 93 | `lightbuilding_exhibitors.csv`/`.json` |
| ISH | `ISH` | 2,127 | Germany 579, Italy 345, China 247, Türkiye 157, Poland 88 | `ish_exhibitors.csv`/`.json` |
| Heimtextil | `HEIMTEXTIL` | 1,182 | **India 304 (top!)**, Pakistan 184, Türkiye 161, Germany 87, Spain 55 | `heimtextil_exhibitors.csv`/`.json` |

All three are **full rosters**, paged to completion (`pageSize=200`, looped until
`hitsTotal` reached — no sampling). Heimtextil is the standout for this project: India is
its single largest exhibiting country (25.7% of all exhibitors), stronger signal than any
other fair checked in this session.

CSV columns: `name, country_iso3, country_label, city, email, homepage, rewriteId`.

## Other Messe Frankfurt fairs confirmed on the same platform (not deep-dived, event IDs found)

Confirmed live via the same `data-config` extraction, i.e. genuinely scrapable with this
exact technique whenever prioritized:

- **Ambiente** (consumer goods / household, housewares, gifts) — `API_EVENT_ID: AMBIENTE`
- **Techtextil** (technical textiles / nonwovens) — `API_EVENT_ID: TECHTEXTIL`

**Formnext** (additive manufacturing / 3D printing) was NOT confirmed — `formnext.com`
(and the guessed `formnext.messefrankfurt.com`, which does not resolve — NXDOMAIN) did not
respond to plain `curl`/`urllib` requests (TLS connects, then hangs/no response — looks like
bot-protection, not a dead site). Flagged as a genuine gap needing a live-browser follow-up,
not fabricated as working.

## Verification note

All company names, cities, countries in the CSV/JSON files are exactly as returned by the
live API on 2026-08-22 — nothing fabricated or inferred. Spot-checked samples (Indian
exhibitors at Heimtextil/interpack, European exhibitors at ISH/EuroShop) read as real,
plausible companies for their sector and geography.
