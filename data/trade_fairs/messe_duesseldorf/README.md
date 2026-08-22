# Messe Duesseldorf trade-fair exhibitor data

Collected 2026-08-22 for the company-targeting database (foreign companies with India
investment/market interest). Deep-dive follow-up to the CANDIDATE entries scoped in
`layers/40_association_event_registry.json` (interpack, EuroShop, wire & Tube Duesseldorf),
reusing the "DIMEDIS vis" platform technique already confirmed to work for K Fair and
GIFA/METEC (see those fairs' entries in the same registry).

## The platform: DIMEDIS "vis" directory API, one shared backend across ALL Messe Duesseldorf fairs

Each fair's own domain (`interpack.com`, `euroshop-tradefair.com`, `wire-tradefair.com`,
`tube-tradefair.com`, and confirmed working the same way for `boot.com`, `drupa.com`,
`glasstec.de`, `aplusa-online.com` (A+A), `caravan-salon.com`, `k-online.com`) serves an
`/vis/v1/en/directory/<a-z|other>` page. That page is a thin skeleton (`<div
id="finder-app">`) whose real data comes from a plain JSON API:

```
GET https://<domain>/vis-api/vis/v1/en/directory/<a-z|other>
Header: X-Vis-Domain: https://<domain>
```

No API key needed, just the `X-Vis-Domain` header (must match a domain the shared backend
recognizes -- confirmed by proof-of-concept: hitting `interpack.com`'s own server URL but
setting `X-Vis-Domain: https://www.k-online.com` returned **K Fair's** exhibitor data, not
interpack's -- proving all these fairs run on one shared backend cluster, addressable from
any of the frontend domains, purely routed by the header value). This directly answers the
task's question: **yes, Messe Duesseldorf has one shared platform across (at least) all of
interpack, EuroShop, wire, Tube, K Fair, GIFA, METEC, boot, drupa, glasstec, A+A, and
Caravan Salon** -- it is not a per-fair bespoke system.

`GET .../directory/meta` lists the 27 valid buckets (`a`-`z` + `other` for numeric-leading
names) and whether each is "filled" for that fair. Each bucket call returns the *complete*
list for that letter in one response (no further pagination observed or needed -- verified
by checking first/last alphabetical entries in each bucket, e.g. interpack's "a" bucket runs
cleanly from "A&D Verpackungsmaschinenbau GmbH" to "AZO GmbH & Co. KG").

Extraction script: `scripts/scratch_messe/duesseldorf_vis_pull.py <domain> <output_key>`.

## Fairs deep-dived this pass

| Fair | Domain used | Total exhibitors | Top countries | File |
|---|---|---|---|---|
| interpack (packaging processes & machinery) | `www.interpack.com` | 3,085 | Germany 609, China 451, Italy 436, Türkiye 301, **India 111** | `interpack_exhibitors.csv`/`.json` |
| EuroShop (retail technology) | `www.euroshop-tradefair.com` | 2,014 | Germany 586, China 244, Italy 177, Türkiye 113, India 8 | `euroshop_exhibitors.csv`/`.json` |
| wire & Tube Duesseldorf | `www.wire-tradefair.com` + `www.tube-tradefair.com` | 2,743 | China 679, Germany 519, Italy 367, Türkiye 200, **India 167** | `wire_dusseldorf_exhibitors.csv`/`.json` (+ identical `tube_dusseldorf_exhibitors.csv`) |

All three are **full rosters**, paged through all 27 letter buckets to completion --- no
sampling.

CSV columns: `name, country, city, location, exh, exhSeoId`. (`location` = hall/stand,
`exh`/`exhSeoId` = internal profile IDs, usable to construct a live profile URL if needed.)

**Important data characteristic, not a bug**: wire Duesseldorf and Tube Duesseldorf are
co-located sister fairs (same halls, same week) that share **one combined exhibitor
directory** -- pulling `www.wire-tradefair.com` and `www.tube-tradefair.com` independently
returned byte-for-byte identical 2,743-company datasets. Treat "wire & Tube" as a single
2,743-exhibitor roster spanning both wire and tube/pipe product categories, not two
independent 2,743-company fairs (i.e. do not double-count toward any combined total).

## Other Messe Duesseldorf fairs confirmed on the same platform (not deep-dived)

Confirmed via a live `directory/meta` 200 response (i.e. genuinely scrapable with this exact
technique whenever prioritized), beyond the already-covered K Fair / GIFA / METEC:

- **boot Duesseldorf** (watersports & boats) -- `www.boot.com`
- **drupa** (print technology) -- `www.drupa.com`
- **glasstec** (glass industry) -- `www.glasstec.de`
- **A+A** (occupational safety & health) -- `www.aplusa-online.com`
- **Caravan Salon** (RVs/caravans) -- `www.caravan-salon.com`

(MEDICA is already covered per the existing registry entry, on its own separate domain --
not re-checked here.)

## Verification note

All company names, countries, cities in the CSV/JSON files are exactly as returned by the
live API on 2026-08-22 -- nothing fabricated or inferred. Spot-checked Indian exhibitors at
interpack (e.g. ACG Pam Pharma Technologies, Ajit Industries, AUM Paper Products) read as
real, plausible Indian packaging-sector companies.

## Second pass (2026-08-22): boot, drupa, glasstec, A+A, Caravan Salon deep-dived

Follow-up to the "confirmed on same platform, not deep-dived" list above. For each fair, the
live official domain was re-verified (WebSearch + direct fetch, not assumed from the prior
pass's list) and `directory/meta` was hit live before pulling. All five returned HTTP 200 with
filled buckets on the DIMEDIS vis platform -- same shared backend as interpack/EuroShop/wire/Tube.
Full rosters pulled via `scripts/scratch_messe/duesseldorf_vis_pull5.py` (same fetch pattern as
`duesseldorf_vis_pull.py`, extended to write CSV directly alongside JSON), paging all 27 letter
buckets to completion, no sampling.

| Fair | Domain used (live-verified) | Total exhibitors | Top countries | India-linked | File |
|---|---|---|---|---|---|
| boot Duesseldorf (watersports & boats) | `www.boot.com` | 1,773 | Germany 744, Italy 136, Netherlands 119, France 97, Indonesia 49 | 1 | `boot_exhibitors.csv`/`.json` |
| drupa (print technology) | `www.drupa.com` | 1,725 | Germany 453, China 414, Italy 149, **India 70**, UK 65 | 70 | `drupa_exhibitors.csv`/`.json` |
| glasstec (glass industry) | `www.glasstec.de` | 1,158 | China 366, Germany 253, Italy 144, Türkiye 48, UK 41 | 13 | `glasstec_exhibitors.csv`/`.json` |
| A+A (occupational safety & health) | `www.aplusa-online.com` | 2,514 | China 642, Germany 566, Italy 150, France 97, UK 83 | 61 | `a_a_exhibitors.csv`/`.json` |
| Caravan Salon (motorhomes/caravans/camping) | `www.caravan-salon.com` | 1,008 | Germany 629, Italy 72, Netherlands 56, Austria 31, France 26 | 0 | `caravan_salon_exhibitors.csv`/`.json` |

Notes:
- India-linked counts are exact matches on `country == "India"` in the pulled data, not an
  estimate -- straightforward to compute since the API returns a clean country string per
  exhibitor.
- **Caravan Salon has zero India-linked exhibitors** in this pull -- an honest negative
  finding, not a pull failure (1,008 total exhibitors were returned successfully; India is
  simply absent from the country distribution for this fair, consistent with caravans/RVs
  being a low-India-relevance sector so far).
- boot Duesseldorf has only 1 India-linked exhibitor despite 1,773 total -- consistent with
  watersports/marine being a low-India-export-relevance sector relative to industrial fairs
  like drupa/A+A/glasstec.
- Same CSV schema as the first pass: `name, country, city, location, exh, exhSeoId`.
- Domain re-verification for A+A and Caravan Salon specifically checked against the task's
  suggested `.de` guesses -- both are wrong; the real, live, WebSearch-confirmed official
  domains are `aplusa-online.com` and `caravan-salon.com` (`.com`, not `.de`).
