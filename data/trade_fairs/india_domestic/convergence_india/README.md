# Convergence India trade-fair participant data (India side)

Collected 2026-08-22 for the company-targeting database (foreign companies with India
investment/market interest, telecom/IT/broadcast/digital-technology sector).

## Event

- **Convergence India** — New Delhi telecom / IT / broadcast / digital-technology trade fair,
  part of Exhibitions India Group's "Digital Week" cluster (co-located with **Smart Future
  Cities India**, **Satcom India**, **Broadcast India Show**, and **India Internet of Things
  Expo**).
- Organizer confirmed: **Exhibitions India Group (EIG)**, jointly organised with the **India
  Trade Promotion Organisation (ITPO)**, with support from the IndiaAI Mission, Digital India
  and MeitY. (`10times.com`, `coinpedia.org`, and the event's own site all agree on this.)
- Most recent **completed** edition as of the 2026-08-22 access date: the **33rd Convergence
  India & 11th Smart Future Cities India Expo**, **23-25 March 2026**, Bharat Mandapam, New
  Delhi. (The site was already promoting the 34th/2027 edition at access time — see the edition
  caveat below — but the exhibitor data itself is the 33rd/2026 roster.)
- Official domain confirmed live: **`convergenceindia.org`**.

## What was found: a genuine, structured, full exhibitor directory

Unlike several other India-domestic B2B shows researched in this repo (e.g. RailTrans Expo,
India Mobile Congress — see their respective READMEs), Convergence India's official site
**does** expose a real, complete, machine-readable exhibitor directory — not just a curated
sponsor/partner highlight reel and not a lead-gated form.

- **Source page**: `https://www.convergenceindia.org/exhibitors-and-participants-convergence-india.aspx`
  (titled "Convergence India: List of Participants" at access time).
- This is a JS-rendered widget (`<div id="exhibitor-app">`) with built-in search, and filter
  facets for **Sector**, **Hall**, and **Country** — the country field is a first-class,
  site-maintained field per exhibitor, not something inferred from company names or free text.
- The page reports **"1,021 exhibitors found of 1,021 total"** with no login/paywall/lead form
  required to browse the full list (only paginated 20-something-per-page in the UI).
- **No public JSON/REST API endpoint was found** for this data (checked via live-session network
  traffic and `performance.getEntriesByType('resource')` — no XHR/fetch call resembling exhibitor
  data was observed). The data appears to be fully rendered client-side by the widget's own
  bundle with no separate API call visible from outside; the only way to obtain the full dataset
  was to **programmatically drive the widget's own "Next" pagination control in a live browser
  session and read the rendered DOM after each page** (43 pages total). This was scripted in the
  page's own JS context: `document.querySelector('button.ex-page-btn')` matched on "Next →" text,
  clicked, waited ~250ms for the React re-render, then each `.ex-card` element's `.ex-card-name`,
  `.ex-sector-badge`, `.ex-meta-chip` (hall/stand), and `.ex-country` sub-elements were read.
- The resulting count (1,021 rows) was independently cross-checked twice from the same live
  session and matches the site's own displayed total exactly — no rows dropped or duplicated by
  the pagination walk.

## Files

- **`convergence_india_participants.csv`** / **`convergence_india_participants.json`** — the
  full 1,021-row roster. Columns/fields: `s_no, name, country_origin, flag, flag_basis,
  category_segment, hall, stand, source_url`.
  - `flag` = `FOREIGN` (149 rows) or `INDIA-DOMESTIC` (872 rows).
  - `flag_basis` = the site's own structured **Country** filter field for that exhibitor (quoted
    verbatim per row), **not** a name-pattern guess or free-text mine. This is a materially
    stronger basis than the IREE/railways dataset's name-suffix heuristic, comparable to how
    IITF's PDF carried an explicit " - Country" annotation per exhibitor.
- **`convergence_india_participants_foreign_only.csv`** / **`..._foreign_only.json`** — the same
  149 `FOREIGN`-flagged rows only, for quick reference, with the same metadata header repeated.

## Foreign exhibitor count by country (149 of 1,021 total, ~14.6%)

| Country | Count |
|---|---|
| China | 46 |
| Russia | 24 |
| Taiwan | 24 |
| United States | 15 |
| New Zealand | 13 |
| United Arab Emirates | 5 |
| Singapore | 3 |
| France | 3 |
| Hong Kong | 2 |
| Germany | 2 |
| Bulgaria, Denmark, Bahrain, Canada, Malaysia, Czech Republic, Laos, Latvia, Philippines, Ukraine, Sri Lanka, United Kingdom | 1 each |

Three government-backed **Country Pavilions** are visible in the data as distinct entries in
their own right (in addition to the individual foreign companies exhibiting under them):
**Russia** (Moscow Center of International Cooperation / Anpo Moscow Export Centre — a large
Russian delegation of ~15+ separate Russian companies clustered at Hall 3, stand B3-50/C3-75),
**Taiwan** (Taiwan Excellence / TAITRA, branded "Taiwan AI Island" — a cluster of ~20 Taiwanese
electronics/hardware manufacturers at Hall 5, stand A5-150), and **New Zealand** (New Zealand
Trade & Enterprise — a cluster of ~13 New Zealand companies at Hall 5, stand E5-50). This
matches press coverage found separately (see Corroborating press coverage below).

## Caveats — read before using this data

1. **Edition-label ambiguity, resolved but worth flagging.** At access time
   (2026-08-22) the site's top navigation/logo/footer already showed **"34th Convergence India
   Expo, 23-25 March 2027"** branding — i.e. registration for the *next* edition was open — while
   the "List of Participants" page underneath still displayed the exhibitor roster. The roster's
   own numbers (1,021 exhibitors / participants) and country-pavilion set (Russia, Taiwan, New
   Zealand) match the **33rd edition's** (23-25 March 2026, already completed as of the access
   date) organizer-published statistics (`convergenceindia.org/exhibitor-profile.aspx` separately
   states "1,022 participants... representation from 23 countries" for the 33rd/2026 edition) and
   independent press coverage of that same 2026 edition. This dataset is treated as the **2026
   (33rd edition) roster**, left live on the site while next-year registration opened around it —
   the same "stale year label, content mismatch" pattern flagged for RailTrans Expo in this
   repo's sibling `railways/README.md`. If the organizer refreshes the widget for the 2027
   edition, re-scraping this page later would silently pick up different data under the same URL.
2. **`country_origin` is the exhibiting stand's registered country, not necessarily the ultimate
   parent's global HQ.** Several globally foreign-headquartered names are listed with
   `country_origin = India` because they registered via their Indian entity: `Google India Pvt.
   Ltd.`, `Qualcomm India Pvt. Ltd.`, `Amazon Web services` / `AWS`, `Microsoft`, `Zoom`, `Siemens`,
   `Telit Cinterion`, `Grandstream` (vs. the separately-listed foreign-flagged `Grandstream
   Network Inc.`), `Western Digital`. These are correctly excluded from `FOREIGN` under this
   dataset's own `flag_basis` (the site's structured country field is the ground truth used
   here), but a follow-up pass keyed on ultimate parent HQ rather than exhibiting-entity
   registration would reclassify some of them if that is the use case's definition of "foreign."
3. **Country string casing was inconsistent in the source** (e.g. `CHINA` vs `China` on different
   rows for otherwise-identical Chinese exhibitors) and was normalized to title case in
   `country_origin`; the exact as-scraped raw string is preserved inside each row's `flag_basis`
   quote.
4. **A few rows have no `category_segment` and/or no `hall`/`stand`** — these are trade
   associations, government bodies, or state-startup pavilions listed in the directory without an
   assigned physical booth, not parser failures.
5. **Some near-duplicate name pairs exist** for what is plausibly the same exhibitor listed
   twice under slightly different names or the same stand (`Amazon Web services` / `AWS`; `Tait`
   / `Tait Communications`; `Diagnomitra Healthcare Solutions Private Limited` / `diagnomitra
   healthcare solutions pvt ltd`; `Grandstream` / `Grandstream Network Inc.`). These are left as
   separate rows exactly as the source directory lists them — not merged — since de-duplication
   would require a judgment call this pass didn't make.
6. **`Country Pavilion` is a `category_segment` value, not a country**, for four umbrella/pavilion
   -organizer entries (`Moscow Center Of International Cooperation The Govt. of Moscow`, `New
   Zealand Trade & Enterprise`, `Taiwan Excellence (TAITRA)`, `Anpo Moscow Export Centre`) — these
   represent the pavilion organizers themselves and are counted once each alongside the
   individual foreign companies exhibiting under their respective pavilions.

## Corroborating press coverage (qualitative, lower-confidence, cited separately from the roster)

Independent of the structured roster above, press coverage of the 33rd/2026 edition separately
named country pavilions and "notable brand" participation — consistent with, and corroborating,
the structured data:

- Country pavilions "supported by the governments of Moscow, Taiwan (Taiwan Excellence) — with
  their pavilion christened Taiwan AI Island — and New Zealand," and international speakers
  including "Sergey Cheremin, Minister of the Government of Moscow" and "Graham Rouse, New
  Zealand Consul-General & Trade Commissioner, India & South Asia."
  Source: <https://digitalterminal.in/amp/story/trending/convergence-india-2026-to-showcase-next-generation-tech-innovations-in-new-delhi>
- "976 participants... representation from 26 countries" for the 2026 edition.
  Source: <https://www.exhibitionshowcase.com/convergence-india-expo-2026-opens-with-strong-global-participation/>
- General event/organizer background: <https://10times.com/convergence-india>,
  <https://events.coinpedia.org/convergence-india-2026-8391/>

These press figures (976 participants / 26 countries; vs. the roster's 1,021 / ~13 non-India
country codes actually present as country values, though "26 countries" in press coverage may
count delegate/visitor nationalities rather than exhibitor countries) are organizer/press
self-reported and were **not** used to build the structured dataset above — they are included
here only as independent corroboration that a genuine multi-country foreign presence (Russia,
Taiwan, New Zealand pavilions specifically) is real and matches what the structured directory
shows, not as a substitute for it.

## Regenerating / re-checking

No throwaway extraction script is retained in this directory (the pagination-walk + DOM-read was
done interactively in a live browser session, not as a standalone script). To redo it: open
`https://www.convergenceindia.org/exhibitors-and-participants-convergence-india.aspx` in a real
browser, clear any active Sector/Hall/Country filter, then repeatedly click the `button.ex-page-btn`
element whose text is "Next →" (43 times for the full 1,021-row set at the time of this pass),
reading each page's `.ex-card` elements' `.ex-card-name`, `.ex-sector-badge`, `.ex-meta-chip`
(×2, hall then stand), and `.ex-country` sub-elements after every click (a short wait, ~250ms, is
needed between clicks for the React re-render). Re-verify the total exhibitor count shown at the
top of the page ("N exhibitors found of N total") still matches the row count collected before
trusting a re-run — and re-check the edition-label caveat above, since the same URL may render a
future edition's data if the organizer refreshes it.
