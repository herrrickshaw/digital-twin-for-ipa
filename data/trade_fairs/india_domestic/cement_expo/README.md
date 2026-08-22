# Cement Expo trade-fair exhibitor data (India side)

Collected 2026-08-22 for the company-targeting database (foreign companies with India
investment/market interest, cement/building-materials sector).

## 0. Disambiguation — which "Cement Expo" this is

The name "Cement Expo" is ambiguous; several unrelated India events use variants of it
(e.g. "World of Concrete India" run by a different organizer, NESCO Mumbai, next edition
Oct 2027). WebSearch confirms the real, notable, currently-running event by this exact
name is:

- **Cement Expo**, organized by **ASAPP Info Global Services Pvt. Ltd.** (the publisher of
  *Indian Cement Review* magazine), official site `cementexpo.in`. It is co-located every
  year with the **Indian Cement Review Conference** and **Indian Cement Review Awards**
  (same organizer). This is a private-publisher-run trade show, not a CII/CMA-run one —
  though CMA India (Cement Manufacturers' Association) and CMA Nepal appear as
  **association partners** (confirmed from `cementexpo.in/partner`'s own logo list), and
  the Ministry of Commerce & Industry / other government bodies are shown as supporting
  logos on the event site — it is not a ministry-run event.
- It is a **recurring, multi-city annual/near-annual series**, numbered continuously
  ("14th", "15th", "16th" edition) but held in different cities in different years:
  - 14th edition: 15 Dec 2023, Manekshaw Centre, New Delhi
  - 15th edition: sources disagree on venue/date — `infrastructuretoday.co.in` and a
    cached page title report "15th Cement Expo, 5-6 Mar 2025, Hitex Exhibition Centre,
    Hyderabad"; the organizer's own downloadable brochure PDF (see below) instead states
    "15th Cement Expo, 12-13 Nov 2025, Yashobhoomi, Delhi". **This inconsistency is
    reported as-is, not resolved** — it's unclear whether the event was rescheduled/moved
    from Hyderabad to Delhi keeping the same edition number, or whether these are two
    different sub-events sharing one number due to organizer/press sloppiness.
  - 16th edition (next/current, as of access date): 15-17 Dec 2026, India Expo Centre &
    Mart, Greater Noida (confirmed live from `cementexpo.in/expo`, accessed 2026-08-22).
- Sources: [tradeindia.com Cement Expo 2025 New Delhi listing](https://www.tradeindia.com/tradeshows/139568/cement-expo-2025-new-delhi.html), [15th Cement EXPO to be held in March 2025 in Hyderabad - Infrastructure Today](https://infrastructuretoday.co.in/15th-cement-expo-to-be-held-in-march-2025-in-hyderabad/), [cementexpo.in/about-us](https://cementexpo.in/about-us), [cementexpo.in/expo](https://cementexpo.in/expo).

This is the event used below. (The World of Concrete India show, `woc-india.com`, was
checked and ruled out — different organizer, different brand, not the subject of this
research.)

## 1. What was actually found: no clean exhibitor-list page, but a real exhibitor+booth table inside a brochure PDF

The official site (`cementexpo.in`) has **no dedicated exhibitor-directory page or
downloadable exhibitor-list PDF** for any edition. Pages checked directly:
`/why-exhibitor`, `/exhibitor-profile`, `/floor-plan`, `/gallery`, `/partner` — all of
these turned out to be **marketing logo walls**: raw HTML inspection (`curl` + grep on
`<img>` tags) showed every "exhibitor name" on those pages is actually just an image
filename (e.g. `assets-home/img/brand/FC.jpg`, `CG.jpg`, `TI.jpg`) with **empty `alt=""`
text** — no addresses, no countries, no descriptions, and several filenames are opaque
2-3 letter codes that cannot be reliably expanded to a real company name without
guessing. These pages also don't state which edition/year the logos are from (a
cumulative "who's exhibited with us" wall spanning multiple years). **This logo-wall
content was deliberately NOT used to build the structured dataset below** — it fails the
"no guessing off bare name similarity" rule and has no verifiable per-company origin
signal at all.

What *was* found and *is* usable: the official downloadable event brochure —
`https://cementexpo.in/assets-home/pdf/Cement-Expo-Brochure.pdf` (confirmed live, 200 OK,
10.58 MB; saved here as
`Cement-Expo-15th-2025-Brochure-with-14th-2023-exhibitor-list.pdf`) — is nominally the
promotional brochure for the (upcoming, at time of its writing) 15th edition, but its
"GLIMPSES OF THE PAST" retrospective section (captioned "December 15, 2023, Manekshaw
Centre, New Delhi") reproduces a genuine **two-column "Exhibitors — Company names / booth
no" table plus a separate "Partners" list**, from the **14th Cement Expo (2023)**. This
is the only place a real, company-level, booth-numbered participant list for this event
was found anywhere online (site search, WebSearch, and the site's own navigation all
turned up nothing more current or more complete).

- **Caveat on which edition this covers**: this is the 14th edition (2023), not the "most
  recent completed edition" (which would be the 15th, held sometime in 2025 per the
  conflicting Hyderabad/Delhi reporting above). No exhibitor list could be found for the
  15th or 16th editions — only the generic, undated, un-sourced logo walls described
  above.
- **Caveat on internal numbering inconsistency**: the same brochure PDF, on the same
  spread, captions this content once as "7TH INDIAN CEMENT REVIEW CONFERENCE, EXPO &
  AWARDS 2023" and once as "The 14th Cement EXPO and the 9th Indian Cement Review
  Conference 2023" — i.e. the organizer's own document doesn't agree on the *conference*
  edition number. This doesn't affect the exhibitor table itself, which is unambiguously
  dated Dec 15, 2023, Manekshaw Centre — but it means the "14th" label for the *Expo*
  should be treated as sourced-but-not-independently-cross-checked.
- Extraction method: `curl`-fetched the PDF, ran `pdftotext -layout`, then manually
  transcribed the exhibitor and partner tables verbatim (no OCR needed — text layer was
  clean).

## 2. `cement_expo_participants.json`

**63 unique participants** (61 booth-numbered exhibitors + 2 entries whose "booth" field
is instead "Sponsor", per the source table). Columns: `name`, `booth_no`, `origin_flag`,
`flag_basis`, and `country_of_origin` where flagged non-domestic.

- `origin_flag` values, following the same three-tier scheme as the Railways precedent
  (`data/trade_fairs/railways/README.md`):
  - **`FOREIGN`** (2 companies: Pentol Germany, MIDES Industriais Brazil) — the country
    name appears directly inside the exhibitor's own listed name in the source table.
    Highest confidence.
  - **`FOREIGN-PARENT`** (17 companies) — an India-registered entity (Pvt Ltd / India in
    the name) whose foreign parent company's headquarters was **independently confirmed
    via web search** against the parent's own site, Wikipedia, or an equivalent
    company-registry-grade source, **not** from anything stated in the source PDF itself
    (unlike the Railways IREE dataset, this booth-list table carries zero descriptive
    text — no addresses, no "About us" blurbs — so every FOREIGN-PARENT flag here rests
    on external verification, cited per-row with the search date). One exception:
    ATS Conveyors India Pvt Ltd's French parent (ATS Group) is stated on the organizer's
    own `cementexpo.in/partner` page, so that flag is source-internal, not external.
  - **`LIKELY INDIAN-DOMESTIC (unconfirmed)`** (44 companies) — default when no foreign
    signal was found or verifiable. Several names carry a plausible-but-unconfirmed
    foreign-brand echo that was **deliberately left unflagged rather than guessed**, per
    the "no guessing off bare name similarity" rule — see the `flag_basis` text for
    `IKN Engineering India Pvt Ltd`, `Intensiv-Filter Himenviro`, `Elektromag - Joest
    Vibration Pvt Ltd`, `M/S Cima Sri Airjet Spares`, and `Larvij India Pvt Ltd` (the last
    is adjacent, in the same brochure's photo captions, to a mention of "representatives
    of the Magnezit Group" — a Russian refractories firm — at what may or may not be its
    own booth; too ambiguous to flag with confidence).
- Counts: 2 `FOREIGN` + 17 `FOREIGN-PARENT` = **19 of 63 (30%) flagged non-domestic**;
  44 `LIKELY INDIAN-DOMESTIC (unconfirmed)`.
- No `category`/`segment` column exists in the source table itself (it's just name +
  booth number), so none was fabricated or guessed into the dataset.

## 3. What was NOT done / known gaps

- No independent company-registry check (MCA/CIN lookup) was run on any of the 44
  "LIKELY INDIAN-DOMESTIC (unconfirmed)" entries — same caveat as the Railways IREE
  dataset.
- The site's marketing logo walls (`/exhibitor-profile`, `/gallery`, `/partner`) were
  inspected but not parsed into structured data — see Section 1. If a future session
  wants to mine them anyway, the raw filenames are visible via
  `curl -sL https://cementexpo.in/exhibitor-profile | grep -oE '<img[^>]*>'`, but doing
  so cannot produce a defensible `origin_flag` without additional independent research
  per company (most are single-word or 2-3 letter filename stubs with no other context).
- The Hyderabad-vs-Delhi "15th edition" date/venue conflict (Section 0) was reported but
  not resolved — a definitive answer would need contacting the organizer directly or
  finding a post-event report specific to that edition (neither was found).
- Two "past partner" logos on `cementexpo.in/partner` (`Taiheiyo` — Taiheiyo Cement,
  Japan; `Isgec`) were seen but not incorporated into the structured JSON since that page
  is a partner/sponsor wall, not an exhibitor list, and (like the exhibitor pages) carries
  no dates or per-entry text beyond a bare logo filename.

## Regenerating / re-checking

No custom extraction script was written — the whole pipeline was `curl` (download PDF) →
`pdftotext -layout` (get clean text) → manual transcription of the two visible tables
into the JSON above. The source PDF is retained in this directory
(`Cement-Expo-15th-2025-Brochure-with-14th-2023-exhibitor-list.pdf`) so the extraction can
be redone or spot-checked against source at any time; re-running `pdftotext -layout` on it
reproduces the same table text used here.
