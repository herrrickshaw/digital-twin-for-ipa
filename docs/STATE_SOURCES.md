# State press-release sources — full directory & integration status

Feeds for `scripts/collect_state_news.py` (register: `data/registers/state_news.sqlite`;
history via `scripts/backfill_state_news.py`). All 28 states + 8 UTs probed 2026-08-02.
Non-English titles are machine-translated into `title_en` at collect time (or via the
capped signal pass in the daily cron) so the central scheme-keyword map can read them.

Daily cron (07:40, after the 07:17 PIB refresh): collect → capped signal-translation
resume → `build_reportage.py` rebuild.

## Integrated (16)

| Code | State | Source | Access | Language | Notes |
|---|---|---|---|---|---|
| MP | Madhya Pradesh | [mpinfo.org](https://www.mpinfo.org/Home/TodaysNews) | open GET JSON (`/HomePageWebservice.asmx/Todaynews`) | English subset + full Hindi wire | day-addressable MM/DD/YYYY; archive from ~2020-04; newsid de-obfuscated −0x80/char |
| UP | Uttar Pradesh | [information.up.gov.in](https://information.up.gov.in/cm_press_release_details.aspx) | plain HTML tables (CM + departmental) | Hindi | latest ~30 rows each; PDF per release; site slow (60–90 s) |
| GJ | Gujarat | [gujaratinformation.gujarat.gov.in](https://gujaratinformation.gujarat.gov.in/Department-Releases) | POST JSON (`/BindDepartmentPressRealese`), antiforgery token + cookie | English + Gujarati (merged on pressId) | latest 15/language; full text in `pressDesc` |
| MH | Maharashtra | [mahasamvad.in](https://mahasamvad.in/) (DGIPR wire) | stock WordPress REST (`/wp-json/wp/v2/posts`) | Marathi | real publish dates; archive to 2019-09 (25.7k posts) |
| KA | Karnataka | [cm.karnataka.gov.in](https://cm.karnataka.gov.in/) (CM office wire) | homepage scrape — sequential ids, English slugs | English (+ some Kannada) | no publish date on items → stamped at collection; DIPR sites are PDF shelves; karnatakavarthe.org is empty (1 post since 2021) |
| GA | Goa | [dip.goa.gov.in](https://dip.goa.gov.in/) | stock WordPress REST | English + Marathi | |
| RJ | Rajasthan | [dipr.rajasthan.gov.in](https://dipr.rajasthan.gov.in/) | open POST JSON (`/webapi/PublicPortal/DepartmentWebsite/GetDIPRPressReleaseByFilter`) | Hindi | 73k+ dated releases, fully paged — deepest state archive; no title field, derived from Description HTML |
| PB | Punjab | [ipr.punjab.gov.in](https://ipr.punjab.gov.in/en/press-releases/hq-press-releases/) | server-rendered HTML list | English | 30/page with dates ("July 31, 2026") |
| MZ | Mizoram | [dipr.mizoram.gov.in](https://dipr.mizoram.gov.in/category/english-press-releases) | server-rendered HTML | English | date has ordinal `<sup>` markup; Mizo twin category exists |
| NL | Nagaland | [ipr.nagaland.gov.in](https://ipr.nagaland.gov.in/naga-news) | Drupal view HTML | English | 6/page; /press-release is a 2020 dead end |
| SK | Sikkim | [ipr.sikkim.gov.in](https://ipr.sikkim.gov.in/Home/PressReleasesList) | ASP.NET Core HTML | English | per-release PDFs; slugs repeat — dedup on PDF GUID |
| CH | Chandigarh | [chandigarh.gov.in/public-notice](https://chandigarh.gov.in/public-notice) | HTML table | English | broken TLS chain → collector retries unverified; unknown paths soft-200 the homepage |
| DD | DNH & Daman-Diu | [ddd.gov.in](https://ddd.gov.in/document-category/latest-updates/) | S3WaaS table HTML | English | real press host 164.100.238.200/ddpress unreachable from non-NIC networks |
| KL | Kerala | [prd.kerala.gov.in](https://prd.kerala.gov.in/ml/pressrelease?tid=All&field_date_value=&page=0) | Drupal views HTML | Malayalam | ISO dates in `<time>`; bare ?page=N ignored without full filter query; occasional future-dated typo rows |
| TS | Telangana | [telangana.gov.in press RSS](https://www.telangana.gov.in/category/news/press-releases/feed/) | RSS 2.0 | Telugu + English | ipr.telangana.gov.in is static + stale (Jan 2026); portal wp-json auth-blocked, RSS live |
| AS | Assam | [dipr.assam.gov.in/portlets/press-release](https://dipr.assam.gov.in/portlets/press-release) | HTML table | English titles, EN/AS file pairs | curated ~14-row list, no date column — dates regex-extracted from titles, else stamped at collection |

## Probed in depth — not integrated

| State/UT | Site | Why not | Revisit trigger |
|---|---|---|---|
| Andhra Pradesh | [ipr.ap.gov.in](https://ipr.ap.gov.in/) | live JSON API but every call needs an RSA+AES-256-GCM+HMAC handshake (pubkey bootstrap `EWrvidWPWkaz2p6acWVHh8ISw9giKsLmqOe785rjzpE=` → `POST /iprapinew/api/_open/masters`, type 130 = per-day items, Telugu). Verified working, but needs the `cryptography` package — out of scope for the stdlib-only collector | add a venv-based AP sidecar if AP coverage becomes a priority |
| Chhattisgarh | [dprcg.gov.in](https://dprcg.gov.in/) | WordPress, but WAF serves empty 200s to curl/urllib | retry from browser automation or an IN IP |
| Odisha | [odisha.gov.in/en/news/archive-news](https://odisha.gov.in/en/news/archive-news) | archive stale since Sep 2023; live wire published elsewhere | find the DPR/CMO subdomain |
| West Bengal | [wb.gov.in/press-release.aspx](https://wb.gov.in/press-release.aspx) | ~9 rows, stale (Oct 2025), North-Bengal-flood-specific, no titles | find the real WB press host |
| Uttarakhand | [uttarainformation.gov.in](https://uttarainformation.gov.in/) | WP with feeds disabled; district categories stale since mid-2025; Krutidev mojibake in titles | check if the site resumes publishing |

## Unreachable / moved — need a new entry point (11)

| State/UT | Tried | Result | Next lead |
|---|---|---|---|
| Arunachal Pradesh | arunachalipr.gov.in | conn. error | arunachalpradesh.gov.in press section |
| Bihar | state.bihar.gov.in/prdbihar | 302 loop | needs session/redirect handling |
| Haryana | prharyana.gov.in | 404 (root) | site moved; check haryana.gov.in DIPR |
| Himachal Pradesh | himachalpr.gov.in | conn. error | himachal.nic.in/pressreleases? |
| Jharkhand | prdjharkhand.in | conn. error | jharkhand.gov.in press |
| Manipur | dipr.mn.gov.in | 404 | manipur.gov.in |
| Meghalaya | meghalaya.gov.in/press-releases | 404 | meghalaya.gov.in news route changed |
| Tamil Nadu | dipr.tn.gov.in | conn. error | tn.gov.in press releases mirror |
| Tripura | icatripura.nic.in | conn. error | tripura.gov.in ICA dept |
| Delhi (UT) | dip.delhi.gov.in | conn. error | delhi.gov.in DIP |
| J&K (UT) | dipr.jk.gov.in | conn. error | jk.gov.in / diprjk |
| Ladakh (UT) | ladakh.gov.in/press-releases | 404 | ladakh.gov.in news route |
| Puducherry (UT) | information.py.gov.in | conn. error | py.gov.in |
| Andaman & Nicobar (UT) | dt.andaman.gov.in | conn. error | andaman.gov.in |
| Lakshadweep (UT) | lakshadweep.gov.in/press-releases | 404 | lakshadweep.gov.in news route |
| Meghalaya/Manipur/Tripura etc. | — | many NE-state sites resolve only from IN IPs | retry via an Indian VPS |
| — | — | — | Govt sites often block non-IN IPs or need `www.`/http variants — retry before writing off |

## Why this exists

State cabinets clear industrial/investment decisions days before (or instead of) any
PIB coverage — MoUs, land allotments, policy amendments, incentive sanctions. The wire
feeds the "State wire" section of `docs/reportage_latest.html` and the quarterly
`docs/reportage_states.html` (Investment & MoUs / New projects / Policy & regulation),
filtered by the central scheme map plus `STATE_SIGNAL` language.
