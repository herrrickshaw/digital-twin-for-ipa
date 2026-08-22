# India Mobile Congress (IMC) — foreign exhibitor/participant data

Collected 2026-08-22 for the company-targeting database (foreign companies with India investment/market
interest, telecom/tech sector).

## Edition covered

**IMC 2025 — 9th edition, 8–11 Oct 2025, Yashobhoomi (India International Convention & Expo Centre),
Dwarka, New Delhi.** Confirmed as the most recent completed edition (checked before assuming — Wikipedia's
own IMC article is stale and only covers through IMC 2022; the 2025 dates/venue/edition-number were
cross-confirmed from PIB/newsonair.gov.in coverage, the organizer's own site, and Nokia's exhibitor page).
Organized by the Department of Telecommunications (DoT) and the Cellular Operators Association of India
(COAI). Theme: "Innovate to Transform." Official domain confirmed live: `www.indiamobilecongress.com`
(older domain `imc.org.in` was NOT used — that guess from the task brief was wrong; do not reuse it).

## 1. Official exhibitor directory — checked, found gated, not downloaded

- Page: `https://www.indiamobilecongress.com/resources/exhibitor-directory`
- Fetched 2026-08-22. This is **not a directory listing** — it is a lead-generation form. It requires
  submitting Full Name, Email, Mobile Number, and Organisation Name (plus selecting a year — 2022/2023/2024/
  2025 are options — and a type — "Exhibitor Directory" or "Aspire Start-Ups Directory") before any exhibitor
  data is shown. No exhibitor names, countries, booth numbers, or counts are visible without submitting the
  form.
- Per the task's own ground rules (never enter personal data into a form, never submit forms to unlock gated
  content), **this form was not filled in and the actual directory was never obtained.**
- The organizer's other public-facing pages (`/exhibitor` "Exhibitor Spotlight", `/exhibition`) either
  returned server errors (`HTTP 500`) when fetched or did not surface an actual company roster.
- **Conclusion: no public, downloadable, or parseable exhibitor list exists for IMC 2025.** This matches the
  pattern flagged as common for India-domestic B2B shows in the task brief — attendee/exhibitor lists gated
  behind registration.

## 2. Third-party aggregator — found, not usable

- `https://10times.com/imc-new/exhibitors` claims to list IMC exhibitor companies (a search-engine snippet
  surfaced partial names: Amphenol, QWave, Semtech Corporation, Global Certification Forum, Netcomm Labs,
  Veridic Technologies, Themagazineplus.com). Direct fetch returned `HTTP 403 Forbidden`, so the page's
  actual content, completeness, and — critically — **which IMC edition/year it covers** could not be
  verified. 10times event pages are commonly edition-agnostic aggregations across multiple years of a
  recurring show, so even if accessible this would need year-attribution work before use. **Not included
  in the dataset below; flagged here only as a lead for a future session with browser access.**

## 3. Fallback: named companies from verified press/organizer coverage

Since no roster exists, `india_mobile_congress_participants.json` follows the task's explicit fallback
instruction: it lists only individually-named companies found cited in real news/organizer coverage, each
with a source URL, clearly labeled as **lower-confidence and structurally different from a full roster**
(9 entries, not hundreds).

| Company | Country (HQ) | Flag | Source type |
|---|---|---|---|
| Nokia | Finland | FOREIGN | primary (Nokia's own IMC event page) |
| Ericsson | Sweden | FOREIGN | secondary (trade press) |
| Qualcomm | United States | FOREIGN | secondary (trade press) |
| Quectel Wireless Solutions | China | FOREIGN | secondary (trade press) |
| Samsung | South Korea | FOREIGN-PARENT (India subsidiary exhibited) | primary (Samsung India newsroom) |
| Skylo | United States | FOREIGN | secondary (GSMA event page + press) |
| IPification | Hong Kong | FOREIGN (lower-confidence flag — HQ sourced from third-party company-profile aggregators, not the company's own site) | secondary (GSMA event page + aggregators) |
| Reliance Jio | India | DOMESTIC (context only) | secondary (trade press) |
| Bharti Airtel | India | DOMESTIC (context only) | secondary (trade press) |

`flag_basis` in the JSON gives the full reasoning per row, matching the railways dataset's convention of
stating exactly what triggered a FOREIGN/FOREIGN-PARENT/DOMESTIC call rather than a bare label.

## 4. Qualitative event-scale facts (organizer/press-reported, not independently audited)

- 400+ exhibitors, 4.5 lakh (450,000) sq ft of exhibition space (exhibitionglobe.com / exhibitionshowcase.com
  coverage) — **self-reported by organizer/press, no UFI-audited figure found**, same caveat as the RailTrans
  Expo entry in the railways README.
- 150,000+ visitors, 7,000+ delegates, from 150+ countries (newsonair.gov.in, the government's own news
  service, reporting on the event's conclusion — PIB press release `PRID=2175355` returned `HTTP 403` when
  fetched directly and could not be independently re-confirmed from the primary PIB page).
- Named international **delegations** (government/industry, not necessarily exhibiting companies): Japan,
  Canada, United Kingdom, Russia, Ireland, Austria (newsonair.gov.in coverage of both the opening and closing
  of IMC 2025).
- A **Japan Pavilion** existed at IMC 2025: Japan's Ministry of Internal Affairs and Communications (MIC)
  issued a public call (23 Jul 2025) inviting Japanese ICT companies to apply for pavilion space, "to support
  Japanese companies... in entering the Indian market" — i.e. explicit revealed-preference intent from a
  foreign government agency. Source: `https://www.soumu.go.jp/main_sosiki/joho_tsusin/eng/pressrelease/2025/7/23_1.html`.
  **This is a call-for-applicants notice, not a list of which companies actually took a booth** — no
  post-event roster of Japan Pavilion exhibitors was found.
- A **GSMA Pavilion** (Hall 1, Booth D) hosted technical demo pods from Skylo and IPification, per GSMA's own
  event page and press coverage — the two entries above.

## Caveats, stated plainly

- **No company-level dataset with real coverage exists here** — this is 9 named companies, not a roster.
  Compare against IREE's 250-row PDF-derived catalog or InnoTrans's 3,082-row full directory (see the
  railways README) — IMC 2025 has neither.
- All "400+ exhibitors" / "150+ countries" figures are **event-scale claims**, not counts of named companies;
  they cannot be reconciled against the 9-row participant list.
- The Samsung entry is flagged FOREIGN-PARENT rather than plain FOREIGN because the participating entity is
  Samsung India (a subsidiary), consistent with how the railways dataset distinguishes an India-registered
  subsidiary/JV from a directly foreign-registered exhibitor.
- IPification's country flag (Hong Kong) rests on third-party company-profile aggregators (PitchBook,
  CB Insights), not the company's own site — lower confidence than the other FOREIGN flags here.
- PIB's own press release (`pib.gov.in/PressReleasePage.aspx?PRID=2175355`) could not be fetched directly
  (`HTTP 403`); its content was only available second-hand via newsonair.gov.in, which is also a government
  source (All India Radio's news service) but not the PIB release itself.
- Nothing in this directory was git-added, committed, or pushed, and no build/layer scripts were touched.
