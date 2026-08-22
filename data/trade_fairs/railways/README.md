# Railways trade-fair exhibitor data (India side)

Collected 2026-08-22 for the company-targeting database (foreign companies with India investment/market interest, Railways sector).

## 1. IREE — International Railway Equipment Exhibition

- 16th edition, 15-17 Oct 2025, Bharat Mandapam, New Delhi. Organized by CII with the Ministry of Railways.
- Source PDF (confirmed live, 200 OK, 32.4MB): `https://www.ireeindia.com/pdf/2025/exhibition-form/IREE-Exhibitors-List.pdf`
  saved here as `IREE-2025-Exhibitors-List.pdf`.
- **Important**: despite the filename, this PDF's internal title is "KEY EXHIBITORS" — it is a 45-page
  illustrated directory of exhibitors who submitted a company profile, not necessarily the full roster of
  450+ exhibitors the event claims. Well-known attendees reported in press coverage (e.g. Siemens, Alstom,
  BEML per news articles) do not all appear as standalone entries in this specific PDF — they may have
  exhibited under a group/stand name, been omitted from this directory, or press claims may be imprecise.
- `iree_2025_key_exhibitors.csv` / `.json`: 250 unique company/organization entries extracted directly from
  the PDF (text + font-weight parsing: company names are set in a medium-weight font, descriptions in
  regular weight, used to programmatically separate the two from the two-column layout).
  - `origin_flag`: heuristic classification —
    - `FOREIGN` = company name itself carries a non-Indian legal-entity suffix (GmbH, AG, Corporation, Co./Ltd.
      East-Asia style, S.p.A., PLC, Inc., etc.)
    - `FOREIGN-PARENT (India subsidiary/JV)` = Indian-registered entity (Pvt Ltd / India in the name) whose
      description text names a foreign parent/HQ (e.g. Voestalpine VAE VKN India Pvt Ltd — Austrian parent;
      Vossloh India — German parent; Wabtec Corporation (WIIPL) — US parent; WISKA India, WAGO — German parents)
    - `LIKELY INDIAN-DOMESTIC (unconfirmed)` = default when no foreign signal was found; **not independently
      verified against a company registry** — treat as a starting hypothesis, not a confirmed classification.
  - `possible_merge_artifact` = `true` for ~29 rows where the two-column-to-text parser likely concatenated
    two or more adjacent company blocks into one messy string (mostly around a "SAME AS ABOVE"-repeated-stand
    stretch of the PDF and a few page-boundary rows). These rows are still included for completeness but
    should be manually re-split/verified before use. The 27 "clean" foreign/foreign-parent rows (i.e.
    `origin_flag` starts with FOREIGN and `possible_merge_artifact` is false) are the highest-confidence
    foreign-signal subset.
  - `pdf_pages`: source page(s) in the PDF; 13 rows note `"43-44 (manually recovered - parser missed this
    page region)"` — these (Vestalpine, Vossloh India, Wabtec, Wagner Rail GmbH, Wago, Wiska India, Western
    Railway, etc.) were dropped by the automated column-parser due to a layout/rotation glitch on those two
    pages and were re-added by hand from the plain-text (`pdftotext -layout`) extraction, cross-checked
    against the PDF.
- Also found but not downloaded/parsed (lower priority, same catalog family):
  - `https://www.ireeindia.com/pdf/2019/IREE2019_List_of_Exhibitors.pdf` (2019 edition, for trend/history)
  - `https://www.scribd.com/document/933820800/IREE-Exhibitors-List` and
    `https://www.scribd.com/document/971688904/IREE-Key-Exhibitors-List-1` (Scribd mirrors of the same
    catalog family; not independently checked for content differences)

## 2. RailTrans Expo

- 6th edition, 3-4 Jul 2026, Bharat Mandapam, New Delhi. Organizer: Urban Infra Communication Pvt. Ltd.
  (a private events company, CIN U92140DL2022PTC392284) — not CII/Ministry of Railways as with IREE, i.e.
  a materially less established, privately-run event.
- No exhibitor-list PDF or structured export was found on railtransexpo.com. The site's own navigation
  only exposes a "Key Partners and Exhibitors 2025" page
  (`https://www.railtransexpo.com/p/participants-2025.html`) — a curated, logo-driven list of ~29
  headline partners/sponsors, not a full exhibitor roster, and its year label does not clearly match the
  6th (Jul 2026) edition being researched — treat the edition-year attribution as unconfirmed.
- `railtrans_expo_participants.json` captures that page's content plus self-reported event-scale figures
  (site claims ~250 exhibitors, 3,000-5,000 daily footfall, delegates from 6 named countries for the 6th
  edition) — **all organizer self-reported, no independent/UFI-audited figures found.**
- **Gap, stated plainly**: RailTrans Expo has no genuine company-level exhibitor list accessible online.
  What exists is a sponsor/partner highlight reel, materially thinner than IREE's catalog. Do not treat the
  "~250 exhibitors from 6 countries" figure as verified in the way the IREE PDF's per-company data is.

## 3. InnoTrans (Berlin) — world's largest railway trade fair

- 22-25 Sep 2026, Messe Berlin (confirmed from `www.innotrans.de`). Global scope, not India-specific — used
  here as a foreign-company universe (many exhibitors will have India market/investment relevance as
  suppliers, JV partners, or export targets).
- `innotrans_2026_exhibitors.csv` / `.json`: **3,082 exhibitors — the full directory, no login required to
  browse it** (login only gates a separate "Participants" networking feature). Columns: `company, country,
  city, postcode, hall, stand, segment, description, id`.
- **How it was actually extracted** — the public site (`https://plus.innotrans.de/showfloor/organizations`)
  is a React SPA on CloudFront/S3; every path (including guessed REST paths) returns the same static
  `index.html` shell, so naive scraping/curl-ing that URL gets nothing. The real data source is a separate
  backend the SPA calls client-side: **`POST https://live.messebackend.aws.corussoft.de/webservice/search`**
  (a Corussoft "EventGuide" platform backend — the same white-label system likely powers other Corussoft-run
  trade-fair sites). Found by monkey-patching `window.fetch` in a live browser session and triggering a UI
  search, which surfaced the real POST call (plain form-urlencoded body, JSON response) — it never appears
  as a normal XHR/fetch entry in some network-capture tools, so a fetch/XHR override inside the page is the
  reliable way to find this class of endpoint.
  - Auth: a `beConnectionToken` JWT (HS512, `type:"beConnection"`), issued anonymously per session and sent
    as a request header — reusable directly via `curl` for the lifetime of that session (no login, no
    AWS SigV4 signing needed despite the backend running on AWS).
  - Pagination: `filterlist=entity_orga&order=lexic&numresultrows=75&startresultrow=<N>`, walked via the
    response's `nextStartIndex`/`hasMore` until exhausted — confirmed `count:3082` exactly matches the
    number of unique `id`s collected (no duplicates, no gaps).
  - `segment` = the category entry in each org's `categories[]` that carries a `badgeType` (the same set the
    site's own "Segments" filter dropdown exposes, e.g. "Railway Technology", "Railway Infrastructure",
    "Public Transport", "Interiors"); an org can carry more than one, joined with `; `.
  - `hall` / `stand` are joined with `; ` where an exhibitor has multiple stands (common for larger firms
    with an indoor + Outdoor Display presence).
- Not yet done: no `origin_flag` foreign/foreign-parent/domestic classification pass (unlike the IREE data)
  — `country` is a clean structured field here (unlike IREE's free-text descriptions), so that pass should
  be a simpler exact-match on `country != "India"` rather than the regex/heuristic approach IREE needed.

## Regenerating / re-checking

The extraction scripts (`extract.py`, `clean.py`, `classify.py`, `patch.py`) used to build the IREE CSV/JSON from
the raw PDF are not included here (they were throwaway session scripts); the PDF itself is retained so the
extraction can be redone or spot-checked against source at any time.

The InnoTrans fetch/merge scripts (`fetch_innotrans.py`, `merge_innotrans.py`) are similarly throwaway and not
included; re-running requires capturing a fresh `beConnectionToken` from a live browser session against
`https://plus.innotrans.de/showfloor/organizations` (the token is not a fixed secret — it's short-lived and
tied to an anonymous session) and repeating the fetch/patch-window.fetch steps described above.
