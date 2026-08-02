# State press-release sources — full directory & integration status

Feeds for `scripts/collect_state_news.py` (register: `data/registers/state_news.sqlite`;
history via `scripts/backfill_state_news.py`). All 28 states + 8 UTs probed 2026-08-02.
Non-English titles are machine-translated into `title_en` at collect time (or via the
capped signal pass in the daily cron) so the central scheme-keyword map can read them.

Daily cron (07:40, after the 07:17 PIB refresh): collect → capped signal-translation
resume → `build_reportage.py` rebuild.

## Integrated (5)

| Code | State | Source | Access | Language | Notes |
|---|---|---|---|---|---|
| MP | Madhya Pradesh | [mpinfo.org](https://www.mpinfo.org/Home/TodaysNews) | open GET JSON (`/HomePageWebservice.asmx/Todaynews`) | English subset + full Hindi wire | day-addressable MM/DD/YYYY; archive from ~2020-04; newsid de-obfuscated −0x80/char |
| UP | Uttar Pradesh | [information.up.gov.in](https://information.up.gov.in/cm_press_release_details.aspx) | plain HTML tables (CM + departmental) | Hindi | latest ~30 rows each; PDF per release; site slow (60–90 s) |
| GJ | Gujarat | [gujaratinformation.gujarat.gov.in](https://gujaratinformation.gujarat.gov.in/Department-Releases) | POST JSON (`/BindDepartmentPressRealese`), antiforgery token + cookie | English + Gujarati (merged on pressId) | latest 15/language; full text in `pressDesc` |
| MH | Maharashtra | [mahasamvad.in](https://mahasamvad.in/) (DGIPR wire) | stock WordPress REST (`/wp-json/wp/v2/posts`) | Marathi | real publish dates; archive to 2019-09 (25.7k posts) |
| KA | Karnataka | [cm.karnataka.gov.in](https://cm.karnataka.gov.in/) (CM office wire) | homepage scrape — sequential ids, English slugs | English (+ some Kannada) | no publish date on items → stamped at collection; DIPR sites are PDF shelves; karnatakavarthe.org is empty (1 post since 2021) |

## Reachable — integration candidates (15)

| State/UT | Site | HTTP | First look |
|---|---|---|---|
| Andhra Pradesh | [ipr.ap.gov.in](https://ipr.ap.gov.in/) | 200 | IPR dept portal |
| Assam | [dipr.assam.gov.in](https://dipr.assam.gov.in/) | 200 | standard Assam govt CMS |
| Chhattisgarh | [dprcg.gov.in](https://dprcg.gov.in/) | 200 | DPR portal, Hindi wire |
| Goa | [dip.goa.gov.in](https://dip.goa.gov.in/) | 200 | Dept of Information & Publicity |
| Kerala | [prd.kerala.gov.in](https://prd.kerala.gov.in/) | 200 | root live (old `/en/news` path 404s — find new news route) |
| Mizoram | [dipr.mizoram.gov.in](https://dipr.mizoram.gov.in/) | 200 | DIPR portal |
| Nagaland | [ipr.nagaland.gov.in](https://ipr.nagaland.gov.in/) | 200 | IPR portal |
| Odisha | [odisha.gov.in/news](https://odisha.gov.in/news) | 200 | state portal news section (pr.odisha.gov.in dead) |
| Punjab | [ipr.punjab.gov.in](https://ipr.punjab.gov.in/) | 200 | IPR portal (diprpunjab.gov.in dead) |
| Rajasthan | [dipr.rajasthan.gov.in](https://dipr.rajasthan.gov.in/) | 200 | press-note section; Hindi |
| Sikkim | [ipr.sikkim.gov.in](https://ipr.sikkim.gov.in/) | 200 | IPR portal |
| Telangana | [ipr.telangana.gov.in](https://ipr.telangana.gov.in/) | 200 | English + Telugu releases |
| Uttarakhand | [uttarainformation.gov.in](https://uttarainformation.gov.in/) | 200 | Information dept portal |
| West Bengal | [wb.gov.in/press-release.aspx](https://wb.gov.in/press-release.aspx) | 200 | ASP.NET list, English |
| Chandigarh (UT) | [chandigarh.gov.in/press-release](https://chandigarh.gov.in/press-release) | 200 | admin portal press page |
| Dadra NH & Daman Diu (UT) | [ddd.gov.in](https://ddd.gov.in/) | 200 | admin portal |

## Unreachable / moved — need a new entry point (16)

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
| — | — | — | Govt sites often block non-IN IPs or need `www.`/http variants — retry before writing off |

## Why this exists

State cabinets clear industrial/investment decisions days before (or instead of) any
PIB coverage — MoUs, land allotments, policy amendments, incentive sanctions. The wire
feeds the "State wire" section of `docs/reportage_latest.html` and the quarterly
`docs/reportage_states.html` (Investment & MoUs / New projects / Policy & regulation),
filtered by the central scheme map plus `STATE_SIGNAL` language.
