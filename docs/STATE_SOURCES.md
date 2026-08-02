# State press-release sources — directory & integration status

Feeds for `scripts/collect_state_news.py` (register: `data/registers/state_news.sqlite`).
Probed 2026-08-02. Non-English titles are machine-translated into `title_en` at collect
time so the central scheme-keyword map in `build_reportage.py` can read them.

## Integrated

| Code | State | Source | Access | Language | Notes |
|---|---|---|---|---|---|
| MP | Madhya Pradesh | [mpinfo.org](https://www.mpinfo.org/Home/TodaysNews) | open GET JSON (`/HomePageWebservice.asmx/Todaynews`) | English subset + full Hindi wire | day-addressable (MM/DD/YYYY); newsid de-obfuscated by −0x80/char |
| UP | Uttar Pradesh | [information.up.gov.in](https://information.up.gov.in/cm_press_release_details.aspx) | plain HTML tables (CM + departmental) | Hindi | latest ~30 rows each; PDF per release; site is slow (60–90 s) |
| GJ | Gujarat | [gujaratinformation.gujarat.gov.in](https://gujaratinformation.gujarat.gov.in/Department-Releases) | POST JSON (`/BindDepartmentPressRealese`), antiforgery token + cookie | English + Gujarati (merged on pressId) | latest 15/language; full release text in `pressDesc` |
| MH | Maharashtra | [mahasamvad.in](https://mahasamvad.in/) (DGIPR wire) | stock WordPress REST (`/wp-json/wp/v2/posts`) | Marathi | real publish dates; 200 newest posts per run |
| KA | Karnataka | [cm.karnataka.gov.in](https://cm.karnataka.gov.in/) (CM office wire) | homepage scrape — sequential item ids, English slugs | English slugs (+ some Kannada) | item pages carry NO publish date → new items stamped with collection date; DIPR sites are static PDF shelves, karnatakavarthe.org is an empty shell (1 post since 2021) |

## Probed, reachable — candidates for the next batch

| State | Site | Status | First look |
|---|---|---|---|
| Rajasthan | [dipr.rajasthan.gov.in](https://dipr.rajasthan.gov.in/) | 200 | press-note section; Hindi |
| Telangana | [ipr.telangana.gov.in](https://ipr.telangana.gov.in/) | 200 | English + Telugu releases |
| Assam | [dipr.assam.gov.in](https://dipr.assam.gov.in/) | 200 | standard Assam govt CMS |
| West Bengal | [wb.gov.in/press-release.aspx](https://wb.gov.in/press-release.aspx) | 200 | ASP.NET list, English |

## Probed, needs a different entry point

| State | Tried | Status | Next lead |
|---|---|---|---|
| Tamil Nadu | dipr.tn.gov.in/pressrelease | 404 | find current path on dipr.tn.gov.in; tn.gov.in also mirrors releases |
| Kerala | prd.kerala.gov.in/en/news | 404 | prd.kerala.gov.in restructured; check new news path |
| Haryana | prharyana.gov.in | 404 (root!) | site may have moved; check haryana.gov.in DIPR |
| Odisha | pr.odisha.gov.in | conn. error | odisha.gov.in press section |
| Punjab | diprpunjab.gov.in | conn. error | punjab.gov.in press |
| Bihar | state.bihar.gov.in/prdbihar | 302 loop | needs session/redirect handling |
| Andhra Pradesh | apdip.ap.gov.in | conn. error | ipr.ap.gov.in? |

## Why this exists

State cabinets clear industrial/investment decisions days before (or instead of) any
PIB coverage — MoUs, land allotments, policy amendments, incentive sanctions. The wire
feeds the "State wire" section of `docs/reportage_latest.html`, filtered to rows that
either hit the central scheme map or carry investment/industrial-policy signal language
(`STATE_SIGNAL` in `build_reportage.py`).
