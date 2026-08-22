# India International Trade Fair (IITF) — foreign country/company participation

Collected 2026-08-22 for the company-targeting database (foreign countries/companies with India
investment/market interest, general-purpose B2B/B2C fair).

## Edition covered

**IITF 2025 — 44th edition, 14–27 Nov 2025, Bharat Mandapam (Pragati Maidan), New Delhi.** Confirmed as
the most recent completed edition (checked, not assumed — the 44th-edition/dates/venue figure is
independently corroborated by a PIB government press release, ETV Bharat news coverage, and the ITPO
exhibitor-list PDF itself, all dated Nov 2025). Organizer: India Trade Promotion Organisation (ITPO),
Ministry of Commerce & Industry, Government of India. Theme: "Ek Bharat Shreshtha Bharat." Official
current domain confirmed: `itpo.gov.in` — the older show-specific domain `indiatradefair.com` now
serves only a redirect banner ("You are now being redirected to our new corporate website"), i.e. it is
a legacy ITPO property, not a separate/unofficial site.

Unlike the sector-specific B2B shows already in this repo (IREE, RailTrans Expo, InnoTrans), IITF is a
mixed B2B/B2C general trade fair built around India's own states (31 States/UTs, 4 Partner States —
Bihar, Maharashtra, Rajasthan, Uttar Pradesh — 1 Focus State — Jharkhand, for 2025) plus a much smaller
"International Pavilion" for foreign countries. No "Partner Country" was named for the 2025 edition in
any source checked — do not assume one exists; that field is left `null` in the JSON rather than guessed.

## 1. Country-level participation (primary source, government press release)

- Source: PIB press release, `https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190245&reg=48&lang=2`,
  dated 14 Nov 2025 ("Minister of State for Commerce & Industry ... inaugurates 44th India International
  Trade Fair 2025"). Fetched 2026-08-22 (WebFetch returned `HTTP 403`; the page was retrieved successfully
  via `curl` with a browser User-Agent header and its text extracted with a simple HTML-tag strip).
- Exact quote, attributed in the release to ITPO's Chairman & Managing Director, Shri Nitin Kumar Yadav,
  at the fair's inauguration: *"Eleven countries—China, Thailand, UAE, Malaysia, Sweden, Turkey, Iran,
  South Korea, Egypt, Lebanon, the Republic of Tunisia, and the Tibetan Chamber of Commerce—are
  participating in the International Pavilion."*
- Read literally this names 12 entities for "eleven countries" — because the Tibetan Chamber of Commerce
  is grouped in the same sentence but is **not a sovereign country** (India does not recognize Tibet as a
  separate state). `iitf_participants.json` keeps the 11 countries and the Tibetan Chamber of Commerce as
  two clearly separate fields (`country_level_participation.countries` vs.
  `country_level_participation.additional_named_participant_not_a_country`) rather than silently rounding
  to 11 or 12.
- No independent country-by-country breakdown (e.g. stall counts per country, company counts per country)
  was found anywhere else — this 11-country list is the full extent of the verified country-level data.

## 2. Company-level exhibitors (primary source, ITPO's own official PDF)

- Source: `https://www.itpo.gov.in/assets/images/iitf-pdf/IITF%202025%20-%20LIST%20OF%20EXHIBITORS.pdf`
  ("IITF 2025 - HALLWISE LIST OF EXHIBITORS"), confirmed live, 200 OK, 14 pages, saved here as
  `IITF 2025 - Hallwise List of Exhibitors.pdf`. Found via web search, hosted directly on `itpo.gov.in` —
  ITPO's own domain, not a third-party mirror.
- The PDF has a text layer (`pdftotext -layout` extracted it cleanly; WebFetch's own PDF handler reported
  it as unreadable "compressed binary," which was a tooling limitation, not a property of the file —
  `pdftotext` had no trouble with it).
- Structure: one continuous table, S.No 1–503, columns `NAME OF EXHIBITOR/MINISTRY/STATE/ORGANIZATION`,
  `HALL NO.`, `STALL NO.`, `CONTACT DETAILS`, `EMAIL`, broken into per-hall sections (Hall 1 FF/GF, Hall 2
  FF/GF, Hall 3 FF/GF, Hall 4 FF/GF, Hall 5 FF/GF, Halls 6/8/9/10/11, Hall 12-12A, Hall 14 GF). **503 total
  rows** — a mix of private companies, individual proprietors, Indian government ministries/PSUs, and
  state-government pavilions; this is not a "foreign vs. domestic" pre-split list.
- **Foreign identification method**: within this table, one specific block — **Hall 1 Ground Floor**, the
  fair's International Pavilion — is the only place exhibitor names carry ITPO's own explicit
  `" - <Country>"` suffix (e.g. `AINGA CO.,LTD - Korea`, `THE EMBASSY OF LEBANON - Lebanon`). This suffix is
  ITPO's own annotation in the source document, not an inference — so every row picked up this way is a
  high-confidence FOREIGN flag, word-boundary-matched against the literal `" - <Country>"` pattern (not a
  bare name/keyword guess). No such suffix convention exists anywhere else in the 503-row document, so no
  foreign flagging was attempted outside Hall 1 GF (see caveats below).
- **24 company/organization rows** matched this pattern, covering 10 distinct countries plus the Tibetan
  Chamber of Commerce: Korea (10 rows), Iran (3), UAE (2), Thailand (2), and one row each for China, Egypt,
  Lebanon, Sweden, Tunisia, Turkey, and Tibet. Full records with hall/stall/email/`flag_basis` are in
  `iitf_participants.json` (`company_level_exhibitors.records`) and mirrored in
  `iitf_exhibitors_international_pavilion.csv`.
- Two of the Hall 1 GF rows are the Embassy of Lebanon and the Embassy of the Republic of Tunisia
  themselves (diplomatic missions, not trading companies) — kept in the dataset with their actual
  `flag_basis` since they are still real Hall 1 GF International Pavilion entries per the source document,
  but they are not commercial exhibitors and should be treated differently from the 22 genuine companies
  if this feeds into an outreach-lead pipeline.

## 3. Cross-check between the two sources — an honest gap

Comparing the PIB's 11-country list against the 24 company-level rows: **Malaysia is named by PIB as an
International Pavilion participant, but no exhibitor row anywhere in the 503-row PDF carries a "Malaysia"
country suffix** (checked with case-insensitive search across the entire extracted text, not just Hall 1
GF). The other 10 PIB-named countries (China, Thailand, UAE, Sweden, Turkey, Iran, South Korea, Egypt,
Lebanon, Republic of Tunisia) and the Tibetan Chamber of Commerce all have at least one matching Hall 1 GF
row. Possible explanations, none confirmed: Malaysia's stall may have been an official/government desk not
itemized by individual company name in this PDF; the PDF may be incomplete for that one country; or the
country suffix was simply omitted for that entry. **This gap is reported as-is rather than papered over** —
`iitf_participants.json` marks Malaysia's `company_level_exhibitor_rows_found: false` with this exact note.

## 4. Not found / not attempted

- No per-country exhibitor counts, no total foreign-vs-domestic exhibitor split, and no "Partner Country"
  designation were found for IITF 2025 in any source checked.
- A separate ITPO factsheet PDF was referenced in search results
  (`indiatradefair.com/iitf/uploads/pdfs/iitf2025/Factsheet-IITF 2025.pdf` and a sibling path without
  `/iitf/`) but both returned `HTTP 404` when fetched directly — likely a stale/renamed path — so it was
  not used as a source here.
- Visitor/footfall totals (e.g. "18 lakh visitors" reported by some secondary outlets) were seen in search
  results but not independently verified against a primary ITPO/PIB source, so they are **not** included in
  `iitf_participants.json` to avoid mixing verified and unverified figures in one file.

## Regenerating / re-checking

`iitf_participants.json` and the companion CSV were built by a throwaway script
(`build_iitf_json.py`, not included here) that hand-transcribes the 24 Hall 1 GF rows from
`pdftotext -layout` output of the retained PDF, plus the PIB quote. To re-verify: re-run
`pdftotext -layout "IITF 2025 - Hallwise List of Exhibitors.pdf" -` and grep for
`" - Korea| - UAE| - Thailand| - Iran| - Egypt| - China| - Sweden| - Lebanon| - Tunisia| - Tibet| - Turkey| - Malaysia"`
(case-insensitive) — this is exactly the method used to build the 24-row list and to confirm the Malaysia
gap.
