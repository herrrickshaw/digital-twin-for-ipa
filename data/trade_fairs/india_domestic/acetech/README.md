# ACETECH — foreign exhibitor/participant presence (no public roster found)

Collected 2026-08-22 for the company-targeting database (foreign companies with India
investment/market interest, architecture/construction-technology/building-materials sector).

## Edition covered, and two premise corrections made while researching

- **Domain correction**: `acetechindia.com` (named in the task brief as a likely official domain) is
  **not** the trade fair — it resolves to an unrelated Delhi-based software company ("Acetech Information
  Systems," AI app development services), confirmed live 2026-08-22. The real, current official domain is
  **`acetechexpo.com`**.
- **Organizer correction**: the task brief named "ThreeSixty Marketing Services" as the organizer. No
  source checked (acetechexpo.com itself, its `/overview/` page, 10times.com's listing, or general web
  search) connects that name to ACETECH — the only "ThreeSixty" match found is an unrelated Buffalo, NY
  marketing agency (`three-sixty.agency`). The organizer named consistently across every source checked is
  **ABEC Exhibitions & Conferences Pvt. Ltd.** (acetechexpo.com/overview/: "conceptualizing over 70 shows
  across 10 verticals in over 19 major cities pan India"; independently confirmed as the listed organizer
  on 10times.com/et-acetech-mumbai). The show is also historically branded "ET ACETECH" / "The Economic
  Times Acetech" (10times page title, and a search-result title "About Economic Times ACETECH" pointing at
  `etacetech.com/about.html`) — but `etacetech.com` failed DNS resolution from this environment (both
  plain and `www.` hostnames) at time of access, so that branding/domain could not be independently
  fetched and verified beyond the search-engine snippet.
- **Cities/venues** (from acetechexpo.com's own "Upcoming Events" list, confirmed live 2026-08-22):
  Bengaluru (Bangalore International Exhibition Centre), **Mumbai (Bombay Exhibition Centre)**, New Delhi
  (Bharat Mandapam/Pragati Maidan), Hyderabad (Hitex Exhibition Center).
- **Most recent completed Mumbai edition: 6–9 Nov 2025, Bombay Exhibition Centre (NESCO), Goregaon,
  Mumbai — the 19th edition** (per topinteriorsindia.com: "19th Edition of Asia's Largest Architecture,
  Building & Interior Design Trade Show," cross-checked against exhibitionshowcase.com's 2021 article "15
  years of ACETECH — Now all set for its Mumbai Edition," which is consistent with a founding year of 2006
  and a 19th edition landing in 2025). Confirmed as the most recent completed Mumbai edition because the
  next scheduled one (19–22 Nov 2026, per acetechexpo.com) had not yet occurred as of the 2026-08-22
  access date.
- **"Largest venue" check**: Mumbai is repeatedly described in independent secondary sources as ACETECH's
  original (2006) and flagship city, run at its largest single venue (Bombay Exhibition Centre). No source
  found gives a same-year, city-by-city sq-ft or exhibitor-count comparison table across Mumbai/Delhi/
  Bengaluru/Hyderabad for a single edition — so "largest" here rests on the flagship/original-city framing
  repeated across sources (topinteriorsindia.com, acetechexpo.com/overview/), not on one audited
  comparative figure. Stated as a limitation rather than treated as independently measured. One data point
  worth flagging honestly: 10times.com separately lists "ACETECH Bangalore ... 20th Edition" (Oct 2026) —
  a higher edition count than Mumbai's 19th — so edition-count alone does not unambiguously prove Mumbai
  is the oldest/largest; it is the balance of qualitative sourcing (not a single hard metric) that points
  to Mumbai.

## 1. No public, downloadable, or parseable exhibitor list found

- Checked the entirety of `acetechexpo.com`'s indexed pages (via its own `sitemap_index.xml` →
  `page-sitemap.xml`, 18 URLs: `/`, `/official-fabricators/`, `/contact-us/`, `/privacy-policy/`,
  `/official-fabricators-2/`, `/testimonials/`, `/exhibit/`, `/careers/`, `/overview/`, `/e-brochures/`,
  `/exhibit-enquiry-form/`, `/terms-and-conditions/`, `/supported-by/`, `/podcast/`, `/space-booking/`,
  `/qr/`, `/sponsorship/`, `/media/`) — none is an exhibitor directory or a downloadable exhibitor-list
  PDF. `/e-brochures/` returned `HTTP 404` despite being listed in the sitemap.
- Checked `acetechindia.com` — confirmed unrelated site (see correction above).
- Checked `10times.com/et-acetech-mumbai` (third-party event aggregator): its "Exhibitors" tab does not
  render a distinct exhibitor list on an unauthenticated fetch — the page only surfaces a generic
  "Followers"/interested-user list (explicitly *not* exhibitors) with a self-reported "All Countries"
  breakdown of **platform-user interest**: India, UAE, USA, China, Bangladesh, UK, Italy, Taiwan, Ghana,
  Sri Lanka, Nepal, Pakistan, Qatar, Nigeria, Saudi Arabia, Australia, Colombia, Uganda, Oman, Egypt.
  Deliberately **not** used as exhibitor data — it conflates visitor/follower sign-ups with confirmed
  exhibitor presence, which is exactly the kind of unverified figure this project avoids.
- Checked ExpoFP's interactive floor-plan page for ACETECH 2025 Mumbai
  (`expofp.com/bombay-exhibition-center/acetech-2025`) — no exhibitor names or booth data present in the
  fetched page content, only venue/logistics info.
- A Scribd search result titled "Acetech 2025 Exhibitor List" resolved to a document whose actual title is
  "Ace-Tech-Stall-List" with a Scribd document ID pattern consistent with a much older upload (unrelated,
  unverifiable vintage/authenticity) — not pursued further as a source.
- **Conclusion: no genuine, official, company-level exhibitor roster for ACETECH Mumbai 2025 (or any other
  recent ACETECH edition) is publicly downloadable or scrapable as of 2026-08-22.** This is the same
  pattern already documented in this repo for RailTrans Expo (see `../../railways/README.md` §2) — a
  materially thinner public data footprint than IREE's or IITF's official PDFs.

## 2. Qualitative, lower-confidence signals actually verified (NOT an exhibitor roster)

- **Organizer-level self-reported cumulative stats**, from the acetechexpo.com homepage (confirmed live
  2026-08-22): "4,095+ Exhibitors," "864,914+ Visitors," "5,500+ Brands On Display," "2,500,000+ Total
  Exhibition Area (Sq.Ft)." These are **not** dated or attributed to a single city/edition on the page —
  they read as a running/cumulative marketing figure (the same "4,095 exhibitors" number independently
  appears on the unrelated 10times.com listing page, suggesting a fixed reused marketing figure rather
  than a fresh per-edition count). Do not treat as Mumbai-2025-specific.
- **International "Supported By" partners** — `acetechexpo.com/supported-by/`, "International" tab
  (confirmed live 2026-08-22; the tab's logos carry no `alt` text, so each was individually downloaded and
  visually read to identify it). 11 named bilateral/international trade bodies are listed as supporters of
  ACETECH generally — the page does not date or attribute any of them to the Mumbai-2025 edition
  specifically:
  1. IACC — Indo-American Chamber of Commerce
  2. Indo-Australian Chamber of Commerce
  3. KOTRA — Korea Trade-Investment Promotion Agency
  4. India China Chamber of Commerce & Industry
  5. "New Zealand" (silver-fern logo; the issuing organization's full name is not legible from the logo
     image itself, so it is left exactly as labeled rather than guessed)
  6. EU India Chambers
  7. The Indo-Italian Chamber of Commerce and Industry
  8. IFCCI — Indo-French Chamber of Commerce & Industry
  9. Indo-Arab Chamber of Commerce & Industries
  10. Singapore Indian Chamber of Commerce & Industry
  11. Indo-Spanish Chamber of Technology

  **This is a list of supporting trade institutions, not exhibiting companies.** It is a genuine signal
  that ACETECH maintains institutional outreach channels toward the US, Australia, South Korea, China,
  New Zealand, the EU, Italy, France, Arab-League countries, Singapore, and Spain — useful as
  lead-generation context, not as evidence that any specific company from those countries exhibited.
- **One specific press-verified exhibitor mention, checked and downgraded**: a LinkedIn post by "Italia
  Group" (`linkedin.com/posts/italia-group...`) states it exhibited a "Palladio" mosaic showcase "At
  aceTECH Mumbai 2025." Investigated further (`italiagroup.in/about`, corroborating web search): Italia
  Group is headquartered in Gujarat, India, founded 1990, and entered a 2000 joint venture with **Trend
  Group of Italy** for glass-mosaic manufacturing — i.e. an **Indian-domestic company with a foreign
  (Italian) JV partner**, not a foreign-HQ'd exhibitor. Under this repo's `flag_basis` convention (see
  `../../railways/README.md`), this would be `FOREIGN-PARENT (India subsidiary/JV)` at most, never a bare
  `FOREIGN`. Kept here only as a worked example of a name that *looked* foreign ("Italia Group") but was
  actually checked rather than assumed — it is **not** counted in any foreign-exhibitor tally below.

## 3. Total count

**Zero (0) individually verified foreign-headquartered exhibitor companies for ACETECH Mumbai 2025.** No
genuine company-level roster exists publicly; the one specific company found via press coverage (Italia
Group) was checked and is Indian-domestic with a foreign JV partner, not a foreign-HQ company. This is
reported as a real "none found" result, not a manufactured one — per the task's own instruction that a
smaller real number (here, zero) beats a bigger invented one.

## Files

- `README.md` — this file.
- `acetech_qualitative_signals.json` — structured version of the verified qualitative findings above
  (organizer self-reported stats, the 11 international supporting trade chambers, and the checked/rejected
  Italia Group candidate). Its top-level `record_type` is explicitly set to `"NOT_AN_EXHIBITOR_ROSTER"` so
  downstream tooling cannot mistake it for a company list.

## Regenerating / re-checking

No scripts were used — everything here was hand-fetched via WebSearch/WebFetch and a live browser session
on 2026-08-22. To re-check the international-chambers list: open `https://acetechexpo.com/supported-by/`,
click the "International" tab (its content is not present at initial page load — it requires the tab
click to render), and re-download the numbered logo images under
`https://acetechexpo.com/wp-content/uploads/2024/03/` — the 11 international ones are `01-2.jpg` through
`11-2.jpg` — to re-verify the chamber list by eye, since the page carries no `alt` text on any of these
images.
