# IIJS (India International Jewellery Show) — foreign exhibitor/participant data

Collected 2026-08-22 for the company-targeting database (foreign companies with India investment/market
interest, gems & jewellery sector).

## Edition covered

**IIJS Bharat — Premiere 2026, 42nd edition.** 5–9 August 2026 at Jio World Convention Centre (JWCC), BKC,
Mumbai, running concurrently 6–10 August 2026 at the Bombay Exhibition Centre / Mumbai Exhibition Centre
(Nesco), Goregaon, Mumbai. Organizer: Gem & Jewellery Export Promotion Council (GJEPC), official domain
`gjepc.org` (confirmed live). Held jointly with IGJME Bharat — Premiere 2026 (India Gem & Jewellery
Machinery Expo).

**Confirmed as the most recent completed edition, not assumed.** GJEPC runs multiple IIJS Bharat editions
per year and the brief warned not to guess:
- IIJS Bharat — Signature 2026 (18th edition): 8–12 Jan 2026, Mumbai — completed, but earlier.
- IIJS Bharat — Tritiya 2026 (4th edition), with IGJME Bharat — Tritiya: 21–23 Mar 2026, Bengaluru —
  completed, but earlier.
- **IIJS Bharat — Premiere 2026 (42nd edition): 5–10 Aug 2026, Mumbai — most recent, and already
  completed as of the 2026-08-22 research date (today − 12 days).**
- The next scheduled edition (Signature, Jan 2027) has not happened yet.

Premiere is also GJEPC's largest/flagship edition by scale — press coverage (Indian Jeweller, 25 Jul 2026)
cites 25,000+ trade-visitor registrations ahead of the show and an organizer claim of "2,100+ exhibitors and
50,000+ trade visitors," which is consistent with the 2,163 exhibitor rows found in the live directory below.

## 1. Official exhibitor directory — found, live, parsed directly (no PDF needed)

- URL: `https://gjepc.org/iijs-premiere/exhibitor-list.php`
- Fetched 2026-08-22 via `curl` (HTTP 200, ~4.4 MB HTML). Unlike the Railways/IREE precedent, this is not a
  PDF — GJEPC serves the **full exhibitor table server-side, embedded directly in the page HTML** as a
  DataTables-style `<table id="example">` with one `<tr data-id="EXH####" data-name="..." ...>` per
  exhibitor, carrying `data-description`, `data-images`, `data-logo` attributes plus `<td>` cells for
  Section, Hall No, Stall No, and City. No login, no JS execution, and no separate API call were needed —
  the whole roster is present in the raw page source, so it was parsed with a Python regex/HTML pass
  (no `extract.py`/`clean.py` scripts retained; this was a single throwaway session script, same as the
  IREE precedent — the raw HTML would need re-fetching to redo the parse).
- Row count: **2,163 exhibitor entries** with a unique `EXH####`-style GJEPC exhibitor ID each.
- Columns available in source: Exhibitor Name, Section (a controlled-vocabulary field — see below), Hall No,
  Stall No, City. There is **no explicit Country column** — country/origin had to be inferred per the method
  below.

## 2. How foreign vs. domestic was determined

GJEPC's own `Section` field turned out to be the strongest and most reliable signal — better than the
free-text description parsing the Railways/IREE precedent needed, because GJEPC itself pre-classifies
exhibitors into three explicit foreign-facing sections, distinct from all domestic sections:

- `International Machinery` (32 entries)
- `International Jewellery` (22 entries)
- `International Loose` (loose stones/gems, 21 entries)

versus domestic sections (`plain_gold`, `diamond_colorstone`, `silver_jewellery_artifacts`,
`loose_stones_color_stones`, `machinery`, `the_select_club`, `loose_stones_diamonds`, `allied`,
`lgd_jewellery`, `lgd_diamond`, `lab_edu`).

**75 exhibitors** carry one of the three `International *` Section values. Cross-checking their `City` field
(where present — many of these rows have a blank City in the source) confirms the flag: Hong Kong/Kowloon,
Dubai/Sharjah/UAE, Bangkok/Thailand, Istanbul/Turkey, several Italian towns (Vicenza, Verona, Strambino,
Piocene Rocchette — all real Italian goldsmith/jewellery-machinery districts), Osaka/Kobe/Kofu (Japan),
Ningbo/Shenzhen (China), Amsterdam-adjacent Plan-les-Ouates (Switzerland), Heimsheim (Germany), Singapore,
and "US". A separate full-file scan (`origin_flag` pass over all 2,163 rows, not just the International
sections) for foreign-legal-entity name suffixes (S.R.L., S.p.A., GmbH, DMCC, FZC, Pte Ltd, etc.) or
non-Indian cities outside those three sections turned up exactly **one more** genuine hit:

- **`CATAWIKI`** (Amsterdam) — listed under the domestic-style `diamond_colorstone` Section, not an
  `International *` one, but with City = `AMSTERDAM`. Flagged by city alone; this is the one exhibitor in
  the whole dataset where GJEPC's own Section classification and the City field disagree, worth noting as a
  caveat on trusting Section alone. (Two other name-suffix hits — `AB JEWELS PRIVATE LIMITED` and
  `GODREJ & BOYCE MFG CO LTD` — were false positives from the regex matching "LTD"/generic legal-suffix
  fragments in ordinary Indian company names; both are well-known Indian firms and were excluded.)

**Total foreign-flagged: 76 of 2,163 exhibitors (≈3.5%).** This is expected and not a data-quality problem:
IIJS Premiere is overwhelmingly a domestic B2B show for India's own gold/diamond/silver jewellery trade: the
foreign presence is concentrated in dedicated international pavilions for machinery, loose stones, and
finished jewellery from a handful of countries, which is exactly what the `International *` sections
capture.

`flag_basis` per row states its evidence explicitly, following the same principle as the Railways precedent:
- `GJEPC exhibitor-list Section field = 'International Machinery/Jewellery/Loose'` — the primary,
  highest-confidence basis (organizer's own classification), used for 75 of 76.
- City-field-only basis, used for Catawiki (the one Section/City mismatch).
- For a handful of the 75 with a blank City field, `country_or_origin` was additionally inferred from
  in-name signals — Italian legal suffixes (S.R.L./S.p.A.) for several Italian machinery firms, "HK" in
  `REAL GEMS HK LTD`, Turkish-language wording in `ATLIHAN KALIP KUYUMCULUK MAKINA SAN TIC` — each explicitly
  labeled as inferred, not confirmed. **One entry (`GI CRAFT PAVILION`) has no country signal at all beyond
  the Section flag** and is recorded as `Unknown`; **one (`ORO FRANCO DI FRANCO YURI`) is a low-confidence
  Italian-language-naming guess**, explicitly marked as unconfirmed in its `flag_basis`.

Country breakdown of the 76 foreign-flagged exhibitors (approximate — several are inferred, see above):

| Country/origin | Count |
|---|---|
| Italy | 24 |
| Thailand | 13 |
| Hong Kong SAR, China | 11 |
| United Arab Emirates | 10 |
| Turkey | 5 |
| Japan | 4 |
| China (Mainland) | 2 |
| United States | 2 |
| Netherlands | 1 |
| Switzerland | 1 |
| Singapore | 1 |
| Germany | 1 |
| Unknown (Section-flag only, no other signal) | 1 |

## 3. Files

- `iijs_participants.json` / `iijs_participants.csv` — **all 2,163 exhibitor rows**, not just the foreign
  subset, following the Railways precedent of shipping the full roster with an `origin_flag` per row rather
  than a pre-filtered foreign-only list. Columns: `gjepc_exhibitor_id, name, origin_flag,
  country_or_origin, flag_basis, section, hall, stall, city_as_listed`.
  - `origin_flag` is either `FOREIGN` (76 rows, see above) or
    `INDIAN-DOMESTIC (default — unconfirmed against a company registry)` (2,087 rows) — the domestic default
    is exactly that, a default: not independently checked against India's MCA company registry or similar,
    same caveat the Railways README applied to its "LIKELY INDIAN-DOMESTIC (unconfirmed)" bucket.
  - `country_or_origin` is `India (assumed)` for the domestic-default rows and a real country (or the
    `Unknown`/low-confidence labels above) for the 76 foreign rows.

## Caveats

- **Section field is organizer-assigned, not independently audited.** GJEPC decides which exhibitors go in
  `International *` sections; this dataset trusts that classification rather than re-deriving it from
  scratch, which is why it is the primary `flag_basis` rather than a secondary corroborating signal (a
  reversal from the IREE precedent, where the PDF's free-text descriptions were the only signal available).
- **No independent verification of any company's actual HQ/incorporation.** All flags rest on what GJEPC's
  own exhibitor-list page states (Section + City), not on a company-registry or corporate-filings check.
- **Country inference for blank-City rows is explicitly weaker** — several of the 75 International-section
  rows have no City value in the source at all; country was inferred from company-name legal suffixes or
  language where possible, and left `Unknown` (1 row) or flagged low-confidence (1 row) where it wasn't.
  These are individually called out in each row's own `flag_basis`, not silently guessed.
- **This is Premiere only.** GJEPC's Signature and Tritiya editions (earlier in 2026) were not parsed — this
  file does not attempt to dedupe or merge across editions; a company exhibiting at multiple 2026 editions
  would appear here only if it exhibited at Premiere specifically.
- **The raw HTML source file was not retained** in this directory (unlike IREE's PDF) — it was a 4.4 MB
  temporary fetch; re-fetching `https://gjepc.org/iijs-premiere/exhibitor-list.php` and re-running the same
  regex/HTML extraction (Section/City/Hall/Stall from each `<tr data-id="EXH####">` block) would reproduce
  it, so long as GJEPC has not since taken the page down or changed to post-event archival state.
