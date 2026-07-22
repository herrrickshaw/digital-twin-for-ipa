#!/usr/bin/env python3
"""Layer 31 — IPA source network.

The data-source layer for the investment-promotion apparatus itself: WAIPA
(the global IPA association) and its machine-readable member directory, peer
country IPAs with India-relevant data resources, Invest India's scrapeable
surfaces (no JSON API — sitemap + static PDF CDN + announcement tickers), and
NITI Aayog / NDAP official statistics.

Live on build:
  - WAIPA member directory: scraped from the htmlwidgets JSON blob inside
    https://waipa.org/wp-content/uploads/memberstable-16.html (138 members).
  - URL liveness: every cataloged URL gets a HEAD/GET status stamp (same
    convention as layer 27); failures recorded as data, never dropped.

Everything else is a curated catalog verified on 2026-07-23 (agent sweeps with
per-URL HTTP statuses; access failures like unctad.org 403 kept as data).

Usage:  python3 scripts/build_layer31_ipa_sources.py [--no-live]
Output: layers/31_ipa_source_network.json
"""
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "31_ipa_source_network.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")
WAIPA_TABLE = "https://waipa.org/wp-content/uploads/memberstable-16.html"


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout)


def status(url):
    try:
        return get(url).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR:{type(e).__name__}"


def fetch_waipa_members():
    """Scrape the member table's htmlwidgets JSON blob -> list of dicts."""
    html = get(WAIPA_TABLE, timeout=40).read().decode("utf-8", "replace")
    m = re.search(
        r'<script type="application/json" data-for="htmlwidget-[^"]+">(.*?)</script>',
        html, re.S)
    cols = json.loads(m.group(1))["x"]["data"]  # [flag_img, country, org, website_html]
    members = []
    for flag, country, org, site_html in zip(*cols):
        href = re.search(r"href='([^']+)'", site_html or "")
        members.append({"country": country, "organization": org,
                        "website": href.group(1) if href else None})
    return members


# --------------------------------------------------------------------------
# Curated catalog (agent-verified 2026-07-23; statuses re-stamped on build)
# --------------------------------------------------------------------------

GLOBAL_SOURCES = {
    "waipa": {
        "what": "World Association of Investment Promotion Agencies — the global IPA umbrella body",
        "members_landing": "https://waipa.org/members/",
        "members_data_url": WAIPA_TABLE,
        "members_access": ("htmlwidgets JSON blob inside the members table HTML "
                           "(no CSV offered; blob parses to 4 cols x 138 rows) — "
                           "scraped live by this script"),
        "community_portal": {"url": "https://members.waipa.org/",
                             "access": "member-only, 403 to curl"},
        "publications": [
            {"title": "State of Investment Promotion Agencies — WAIPA-World Bank joint global survey (flagship)",
             "url": "https://waipa.org/wp-content/uploads/State-of-Investment-Promotion-Agencies-Evidence-from-WAIPA-WBG-s-Joint-Global-Survey.pdf",
             "companion_page": "https://waipa.org/state-of-investment-promotion-agencies/"},
            {"title": "Overview of Investment Promotion — WAIPA Annual Survey 2018",
             "url": "https://waipa.org/wp-content/uploads/Overview-of-Investment-Promotion-2019.pdf"},
            {"title": "OCO Global x WAIPA — The New Laws of FDI Attraction (2023, 74 IPAs surveyed)",
             "url": "https://waipa.org/wp-content/uploads/OCO-Global-WAIPA-Innovation-Report-2023.pdf"},
            {"title": "Impact of COVID-19 from the IPA perspective (2020 survey)",
             "url": "https://waipa.org/wp-content/uploads/The-impact-of-COVID-19-from-the-perspective-of-IPAs.pdf"},
            {"title": "UNIDO x WAIPA — Investment Promotion in the ACP Region",
             "url": "https://downloads.unido.org/ot/32/67/32672501/UNIDO-WAIPA_Report.pdf"},
            {"title": "Index pages (publications / annual reports / insights)",
             "url": "https://waipa.org/publications/"},
        ],
        "india_connection": {
            "invest_india_is_member": True,
            "indian_members": ["Invest India", "Invest Telangana Cell",
                               "Maharashtra Industrial Development Corporation (MIDC)"],
            "leadership_history": ("Deepak Bagla (MD & CEO Invest India 2015-2023) "
                                   "served as elected WAIPA President"),
            "regional_note": ("2025-27 Regional Director for South Asia is Board of "
                              "Investment Pakistan, not an Indian agency; current "
                              "president: KDIPA Kuwait"),
        },
    },
    "unctad_and_alternatives": [
        {"name": "UNCTAD main site", "url": "https://unctad.org",
         "note": "403-blocked from this machine — recorded as data"},
        {"name": "UNCTAD Investment Policy Hub", "url": "https://investmentpolicy.unctad.org",
         "note": ("REACHABLE despite unctad.org block — IIA navigator, investment "
                  "laws navigator, ISDS case database; the UNCTAD workaround")},
        {"name": "Investment Monitor (GlobalData)", "url": "https://www.investmentmonitor.ai",
         "note": "FDI journalism + datasets; commercial"},
        {"name": "OECD investment pages", "url": "https://www.oecd.org/en/topics/investment.html",
         "note": "oecd.org 403-blocked; data-explorer.oecd.org / SDMX API untested"},
    ],
    # Peer IPAs whose published data covers India corridors. Overlaps layer 27
    # (entry facilitators) deliberately: 27 catalogs the *event/B2B* function,
    # this layer catalogs the *data* function.
    "country_ipas": [
        {"name": "JETRO", "country": "Japan", "url": "https://www.jetro.go.jp/en/",
         "data_resources": ["Invest Japan Report (annual)",
                            "Survey of Japanese-affiliated companies overseas — India edition",
                            "Japanese FDI statistics"],
         "india_relevance": "Annual survey of Japanese firms operating in India; 5 India offices"},
        {"name": "KOTRA", "country": "South Korea", "url": "https://www.kotra.or.kr/english/index.do",
         "data_resources": ["Overseas market reports", "K-stat trade statistics"],
         "india_relevance": "4 India offices; Korea-India CEPA investment corridor"},
        {"name": "Invest Korea (KOTRA inbound arm)", "country": "South Korea",
         "url": "https://www.investkorea.org/ik-en/main.do",
         "data_resources": ["Korea FDI statistics", "Investment guides"],
         "india_relevance": "Holds a WAIPA Vice-President seat"},
        {"name": "GTAI", "country": "Germany", "url": "https://www.gtai.de/en",
         "data_resources": ["Country market/industry analyses", "Annual Germany FDI report"],
         "india_relevance": "Regular India market analyses; India office"},
        {"name": "Business France", "country": "France", "url": "https://www.businessfrance.fr/en/home",
         "data_resources": ["Annual Report on Foreign Investment in France (project-level)"],
         "india_relevance": "India desk; report includes Indian investor projects"},
        {"name": "SelectUSA", "country": "United States", "url": "https://www.trade.gov/selectusa",
         "data_resources": ["SelectUSA Stats (BEA FDI dashboards)",
                            "FDI fact sheets by source country"],
         "india_relevance": "Publishes India-US FDI fact sheet"},
        {"name": "Invest in Holland / NFIA", "country": "Netherlands", "url": "https://investinholland.com",
         "data_resources": ["Annual NFIA results (projects, jobs, capex)"],
         "india_relevance": "3 India offices; targets Indian IT/pharma EU HQs"},
        {"name": "Enterprise Singapore", "country": "Singapore", "url": "https://www.enterprisesg.gov.sg",
         "data_resources": ["Country market guides", "Trade statistics",
                            "EDB (edb.gov.sg) inbound FDI reports"],
         "india_relevance": "Singapore = top treaty-routed FDI source into India"},
    ],
}

INVEST_INDIA = {
    "what": ("India's national IPA (DPIIT). Drupal 10.4 site, JSON:API disabled "
             "(/jsonapi 404) — machine-readable strategy is sitemap-driven HTML "
             "scraping + the static S3 PDF archive"),
    "surfaces": [
        {"name": "sitemap", "url": "https://www.investindia.gov.in/sitemap.xml",
         "contents": ("flat 338-URL crawl frontier: 41 sector pages, 36 state "
                      "profiles, 7 SIRU papers, 227 blog posts, 13 initiative pages. "
                      "All lastmod stamped identically — useless for change "
                      "detection, diff page content instead")},
        {"name": "sector pages (/sector/*)",
         "url": "https://www.investindia.gov.in/sector/automobile",
         "contents": ("per-sector: 3 hero stats (incl. cumulative FDI), FDI-cap "
                      "statement, scheme list w/ PDF links, investor logo wall, "
                      "and a dated LATEST-UPDATES ticker of company investment "
                      "announcements — a scrapeable event feed that joins onto "
                      "the layer-32 company DB")},
        {"name": "state profiles (/state/*)",
         "url": "https://www.investindia.gov.in/state/gujarat",
         "contents": ("per-state: hero stats (FDI uses DPIIT Oct-2019+ attribution "
                      "window), 7 potential tabs (PLFS demographics, infra, "
                      "education), and a STATE-POLICY PDF carousel (Gujarat exposes "
                      "15+ named policies w/ documents) — direct feed for the "
                      "layer-12/13 state instrument catalog")},
        {"name": "static PDF archive", "url": "https://static.investindia.gov.in/",
         "contents": ("S3-fronted CDN holding every scheme/policy PDF at "
                      "/s3fs-public/YYYY-MM/name.pdf — the de-facto document "
                      "archive of the agency (Consolidated FDI Policy, PLI docs, "
                      "state policies, SIRU papers)")},
        {"name": "ODOP",
         "url": "https://www.investindia.gov.in/one-district-one-product",
         "contents": ("district-product master list PDF (2026-02 version) + vendor "
                      "directory PDF + 4 catalogue volumes + 14-row state-emporium "
                      "link table")},
        {"name": "FDI statistics explainer",
         "url": "https://www.investindia.gov.in/india-fdi-investment-key-sectors",
         "contents": ("DPIIT-sourced figures (dated Jul-2026): cumulative $1.16 Tn "
                      "Apr-2000..Mar-2026, FY25-26 $94.53 Bn, PLI outcomes 892 "
                      "approved applications / Rs 2.4 lakh cr investment")},
        {"name": "SIRU research papers", "url": "https://www.investindia.gov.in/siru",
         "contents": ("Strategic Investment Research Unit is being WOUND DOWN — "
                      "listing page 301s to /contact-us; 7 papers survive in the "
                      "sitemap (PLI deep-dives: white goods, food processing, "
                      "solar; ASEAN; UP expressways; Ayurveda), each HTML + "
                      "companion PDF. Archive-what-remains")},
        {"name": "EFTA desk", "url": "https://www.investindia.gov.in/efta-desk",
         "contents": "bilateral desk page for the India-EFTA TEPA"},
    ],
    "dead_paths_recorded": [
        "/jsonapi 404 (Drupal JSON:API disabled)", "/api 404",
        "/bip 404 (no Bilateral Investment Promotion property)",
        "/pm-gati-shakti 404 (zero GatiShakti integration on the site)",
        "/magazine 404 (publications section dead)",
        "strategicinvestmentresearchunit subdomain NXDOMAIN",
    ],
    "note": ("India Investment Grid (project pipeline) is Invest India-adjacent "
             "but already covered as layer 26; state single-window portals are "
             "layer 15. This layer adds the national-IPA data surfaces on top."),
}

# IPAs of India's top FDI-source jurisdictions that are NOT WAIPA members —
# the WAIPA directory (112 countries) misses ten of the jurisdictions that
# matter most for India inbound flows. Tracked here so the layer covers the
# whole corridor map, not just the association's membership.
NON_WAIPA_IPAS = [
    {"name": "SelectUSA (US Dept. of Commerce / ITA)", "country": "United States",
     "url": "https://www.trade.gov/selectusa",
     "data_resources": ["SelectUSA Stats (BEA FDI dashboards)", "FDI fact sheets by source country"]},
    {"name": "EDB Singapore", "country": "Singapore", "url": "https://www.edb.gov.sg",
     "data_resources": ["Inbound FDI reports", "Sector guides"],
     "note": "EnterpriseSG (outbound/trade) at enterprisesg.gov.sg"},
    {"name": "NFIA / Invest in Holland", "country": "Netherlands",
     "url": "https://investinholland.com",
     "data_resources": ["Annual NFIA results (projects, jobs, capex)"]},
    {"name": "GTAI (Germany Trade & Invest)", "country": "Germany", "url": "https://www.gtai.de/en",
     "data_resources": ["Country market/industry analyses", "Annual Germany FDI report"]},
    {"name": "InvestHK", "country": "Hong Kong", "url": "https://www.investhk.gov.hk",
     "data_resources": ["Sector guides", "Startup/FDI statistics"]},
    {"name": "InvesTaiwan", "country": "Taiwan", "url": "https://investtaiwan.nat.gov.tw",
     "data_resources": ["Investment guides", "Taiwan FDI statistics"]},
    {"name": "Business Sweden", "country": "Sweden", "url": "https://www.business-sweden.com",
     "data_resources": ["Market reports", "Establishment guides"]},
    {"name": "Invest in Canada", "country": "Canada", "url": "https://www.investcanada.ca",
     "data_resources": ["Sector strategies", "FDI performance reports"]},
    {"name": "Austrade / Global Australia", "country": "Australia",
     "url": "https://www.globalaustralia.gov.au",
     "data_resources": ["Investor guides", "Australia FDI statistics"],
     "note": "austrade.gov.au is the parent agency"},
    {"name": "(none — routing jurisdiction)", "country": "Cayman Islands", "url": None,
     "data_resources": [],
     "note": ("No classic IPA; appears in India's top FDI sources as a "
              "fund-routing jurisdiction, not an operating-investor origin")},
]

# DPIIT cumulative top FDI-source jurisdictions into India (equity inflows),
# normalized to the WAIPA directory's country spellings where they differ.
INDIA_TOP_FDI_SOURCES = {
    "Mauritius": "Mauritius", "Singapore": None, "United States": None,
    "Netherlands": None, "Japan": "Japan", "United Arab Emirates": "United Arab Emirates",
    "United Kingdom": "United Kingdom", "Germany": None, "Cyprus": "Cyprus",
    "Cayman Islands": None, "France": "France", "Switzerland": "Switzerland",
    "South Korea": "Korea, Rep.", "China": "China, People Republic of",
    "Hong Kong": None, "Taiwan": None, "Sweden": None, "Canada": None,
    "Australia": None,  # value = WAIPA directory spelling, None = not a member
}

# NITI Aayog / NDAP — verified 2026-07-23 (live API tests from this machine).
NITI_NDAP = {
    "ndap": {
        "what": ("National Data & Analytics Platform — NITI Aayog's aggregation of "
                 "official datasets: 6,784 datasets / 416 collections / 53 "
                 "ministries / 72,960 indicators (live /v1/metadata, 2026-07-23)"),
        "catalog_url": "https://ndap.niti.gov.in/catalogue",
        "api": {
            "backend_host": "https://loadqa.ndapapi.com",
            "discovery": ("ndap.niti.gov.in/api is 404 — the real backend is the "
                          "'loadqa' host hardcoded in the site's JS bundle "
                          "(main.c26d7b32.chunk.js); despite the name it IS production"),
            "required_header": ("Origin: https://ndap.niti.gov.in — without it every "
                                "endpoint returns {'Message':'Invalid Request'}"),
            "anonymous_endpoints": [
                "GET /v1/metadata?domain=ndap — platform totals",
                "GET /v1/search/catalogue?query=<terms>&search=Variables,DatasetInfo&domain=ndap"
                " — ranked collections+datasets w/ id, granularity, ministry, years, frequency",
                "GET /v1/search/filters?domain=ndap — filter taxonomy",
            ],
            "authenticated_endpoints": ("POST /v1/dataset/details|download|export, "
                                        "/v1/openapi/getdetails — require an AWS "
                                        "Cognito bearer (pool ap-south-1_y62WUtDqD) + "
                                        "per-user API_Key from /get-api after free "
                                        "registration. NO public sample key (unlike "
                                        "data.gov.in). Dataset detail pages now "
                                        "login-gate anonymous browser visits too"),
            "tested": ("curl -H 'Origin: https://ndap.niti.gov.in' "
                       "'https://loadqa.ndapapi.com/v1/metadata?domain=ndap' -> 200, "
                       "6784 datasets"),
        },
        "investment_relevant_datasets": [
            {"id": "7113", "name": "State-wise FDI Equity Inflow (DPIIT)",
             "granularity": "State", "frequency": "Quarterly", "updated": "2026-05"},
            {"id": "7471", "name": "FDI Flows to India, industry-wise (RBI Annual Report)",
             "granularity": "Country/industry", "period": "2006-2024"},
            {"id": "8530", "name": "State-wise IEM (Industrial Entrepreneurs Memorandum) filed",
             "granularity": "State", "period": "2008-2024"},
            {"id": "7041", "name": "ASI principal characteristics by major state",
             "granularity": "State", "period": "2017-2021"},
            {"id": "6631", "name": "ASI principal characteristics by organisation type",
             "granularity": "Country", "period": "2008-2021"},
            {"id": "8058", "name": "CEA power supply position (energy + peak)",
             "granularity": "Country", "frequency": "Monthly", "period": "2014-2026"},
            {"id": "7571", "name": "State-wise installed capacity & gross generation",
             "granularity": "State", "period": "2017-2023"},
            {"id": "3224", "name": "MSME Udyam registrations (live)",
             "granularity": "State", "frequency": "Daily"},
            {"id": "7796", "name": "State-wise MSME employment (live)",
             "granularity": "State", "frequency": "Daily"},
            {"id": "7123", "name": "PLFS household survey",
             "granularity": "State", "period": "2017-2023"},
            {"id": "6793", "name": "Country-wise Export-Import Data Bank (total trade)",
             "granularity": "Country", "frequency": "Monthly", "period": "1998-2024"},
            {"id": "7367", "name": "SDG India Index composite (goal-wise at 7351-7366)",
             "granularity": "State", "period": "2020"},
        ],
    },
    "niti": {
        "url": "https://www.niti.gov.in",
        "state_indices": [
            {"index": "Export Preparedness Index", "latest": "EPI 2024 (4th ed., Jan-2026; 5th in procurement)",
             "pdf": "https://www.niti.gov.in/sites/default/files/2026-01/Export_Preparedness_Index_2024.pdf",
             "open_data": "No CSV — tables in PDF annexures only"},
            {"index": "India Innovation Index", "latest": "III 2021 (3rd ed.; 2025 ed. under preparation)",
             "pdf": "https://www.niti.gov.in/sites/default/files/2022-07/India-Innovation-Index-2021-Web-Version_21_7_22.pdf",
             "open_data": "No"},
            {"index": "SDG India Index", "latest": "2023-24 (4th ed., Jul-2024)",
             "pdf": "https://www.niti.gov.in/sites/default/files/2024-07/SDG_India_Index_2023-24.pdf",
             "open_data": ("YES — dashboard sdgindiaindex.niti.gov.in exposes "
                           "state x goal scores; also NDAP ids 7351-7367")},
            {"index": "Fiscal Health Index", "latest": "FHI 2026 (2nd ed., Mar-2026)",
             "pdf": "https://www.niti.gov.in/sites/default/files/2026-03/Fiscal-Health-Index-2026.pdf",
             "open_data": "No CSV; 18-state sub-index tables in PDF"},
            {"index": "State Energy & Climate Index", "latest": "Round I (Apr-2022) still latest",
             "pdf": "https://www.niti.gov.in/sites/default/files/2022-04/StateEnergy-and-ClimateIndexRoundI-10-04-2022.pdf",
             "open_data": "No; related live energy data on iced.niti.gov.in + CEA/NDAP"},
        ],
        "manufacturing_investment_reports": [
            {"title": "Electronics: GVC participation", "date": "2024-07",
             "url": "https://www.niti.gov.in/sites/default/files/2024-07/GVC%20Report_Updated_Final_11zon.pdf"},
            {"title": "Automotive: GVC participation", "date": "2025-04",
             "url": "https://www.niti.gov.in/sites/default/files/2025-06/Automotive%20Industry%20Powering%20India%E2%80%99s%20participation%20in%20GVC_Non%20Confidential.pdf",
             "note": "widely-cited 2025-04/ path now 404s; 2025-06/ path is live"},
            {"title": "Chemical Industry: GVC participation", "date": "2025-07",
             "url": "https://www.niti.gov.in/sites/default/files/2025-07/NITI-Aayog-Chemical-industry-report.pdf"},
            {"title": "Hand & Power Tools: $25bn export potential", "date": "2025-04",
             "url": "https://www.niti.gov.in/sites/default/files/2025-04/India_Hand_Power_Tools_Sector_Report.pdf"},
            {"title": "Boosting Exports from MSMEs", "date": "2024-03",
             "url": "https://www.niti.gov.in/sites/default/files/2024-03/Boosting%20Exports%20from%20MSMEs_March%202024_compressed.pdf"},
            {"title": "Trade Watch Quarterly Q1 FY26", "date": "2026-01",
             "url": "https://niti.gov.in/sites/default/files/2026-01/Trade_Watch_Quarterly_April_June_Q1_FY26.pdf"},
        ],
    },
    "datagov_overlap": {
        "finding": ("DPIIT IEM data is natively on data.gov.in AND works with the "
                    "public sample key (tested 200) — easier row-level access than "
                    "NDAP's login-gated download. FDI state/sector tables there are "
                    "Rajya-Sabha PQ extracts, not DPIIT-native uploads"),
        "iem_datasets": [
            {"uuid": "651edf6f-1dbc-4528-8023-0e72911072ce",
             "title": "State-wise IEM Part-A investment+employment, Aug-1991..last month",
             "tested": "200 with sample key, rows w/ STATE/INVESTMENT/EMPLOYMENT"},
            {"uuid": "424d78ab-e958-4b8a-9208-ef084c07e096",
             "title": "Industry-wise IEM Part-A, Aug-1991..last month"},
            {"uuid": "70e8beb7-0807-40de-acb8-4279b4277784",
             "title": "Last-month state-wise IEM Part-A"},
            {"uuid": "555dcb40-564a-496f-b83f-7638590cb46b",
             "title": "Last-month industry-wise IEM Part-A"},
            {"uuid": "ae0a0ac2-de28-4cb9-8d2f-b5a010562047",
             "title": "State-wise IEMs implemented (Part B), Aug-1991..Jun-2017"},
        ],
        "fdi_pq_datasets": [
            {"uuid": "08803423-90fc-42ac-9725-951f1f0a24bc",
             "title": "State/UT-wise FDI equity inflow FY20-FY25 (Rajya Sabha PQ)"},
            {"uuid": "95fbda02-bdf7-48f0-8c18-6cc925f729ae",
             "title": "Sector-wise FDI equity inflow FY20-FY25 (Rajya Sabha PQ)"},
            {"uuid": "d29c49c8-c8af-415a-8b7b-75c7993b668c",
             "title": "Year-wise FDI equity inflow, manufacturing FY20-FY25 (RS PQ)"},
            {"uuid": "82e470b9-62a8-4000-b0b2-c273cadfaeab",
             "title": "Year-wise total FDI inflows FY20-FY25 (RS PQ)"},
        ],
        "access_pattern": ("search: www.data.gov.in/backend/dmspublic/v1/resources"
                           "?query=... (no key); rows: api.data.gov.in/resource/"
                           "<uuid>?api-key=<public-sample-key>&format=json"),
    },
}


def main():
    live = "--no-live" not in sys.argv

    waipa_members = []
    if live:
        try:
            waipa_members = fetch_waipa_members()
        except Exception as e:
            waipa_members = [{"error": f"live fetch failed: {type(e).__name__}: {e}"}]

    # liveness-sweep every member IPA's website (the tracker function):
    # a dead website on the association's own directory is itself a signal
    if live and waipa_members and "error" not in waipa_members[0]:
        sites = [m["website"] for m in waipa_members if m.get("website")]
        with ThreadPoolExecutor(max_workers=16) as ex:
            results = dict(zip(sites, ex.map(lambda u: status(u), sites)))
        for m in waipa_members:
            m["website_status"] = results.get(m.get("website"))

    # WAIPA coverage vs India's top FDI-source jurisdictions
    member_countries = {m.get("country") for m in waipa_members} if waipa_members else set()
    fdi_coverage = {}
    for pretty, waipa_name in INDIA_TOP_FDI_SOURCES.items():
        in_waipa = bool(waipa_name) and (not member_countries or waipa_name in member_countries)
        tracked = next((i for i in NON_WAIPA_IPAS if i["country"] == pretty), None)
        fdi_coverage[pretty] = {
            "waipa_member": in_waipa,
            "tracked_via": (waipa_name if in_waipa
                            else (tracked["name"] if tracked else "UNTRACKED")),
        }

    # liveness-stamp the primary URLs (layer-27 convention)
    checked = {}
    if live:
        urls = ([WAIPA_TABLE, "https://waipa.org/members/",
                 "https://investmentpolicy.unctad.org",
                 "https://www.investindia.gov.in/sitemap.xml",
                 "https://static.investindia.gov.in/s3fs-public/2025-01/fdi_policy_consolidated.pdf"]
                + [i["url"] for i in GLOBAL_SOURCES["country_ipas"]]
                + [i["url"] for i in NON_WAIPA_IPAS if i["url"]]
                + ([NITI_NDAP["ndap"]["catalog_url"], NITI_NDAP["niti"]["url"]]
                   if NITI_NDAP else []))
        for u in urls:
            checked[u] = status(u)

    layer = {
        "layer": 31,
        "name": "ipa_source_network",
        "built": date.today().isoformat(),
        "what": ("Data-source network of the investment-promotion world itself: "
                 "WAIPA + its live-scraped member directory, peer country IPAs "
                 "with India-relevant data, Invest India's scrapeable surfaces, "
                 "and NITI Aayog / NDAP official statistics. Access failures are "
                 "recorded as data (unctad.org 403, oecd.org 403, Invest India "
                 "JSON:API disabled)"),
        "global": GLOBAL_SOURCES,
        "waipa_member_directory": {
            "fetched_live": bool(live and waipa_members and "error" not in waipa_members[0]),
            "count": len(waipa_members),
            "website_liveness_swept": bool(live and waipa_members
                                           and "website_status" in waipa_members[0]),
            "members": waipa_members,
        },
        "non_waipa_ipas": NON_WAIPA_IPAS,
        "india_top_fdi_source_coverage": fdi_coverage,
        "invest_india": INVEST_INDIA,
        "niti_ndap": NITI_NDAP,
        "url_liveness": checked,
        "feeds": {
            "layer_32_company_db": [
                "Invest India sector-page LATEST-UPDATES tickers (company investment announcements)",
                "JETRO survey of Japanese-affiliated companies in India",
                "Business France annual FDI report (Indian investor projects)",
            ],
            "layer_12_13_state_instruments": [
                "Invest India state-profile policy-PDF carousels"],
            "layer_17_scheme_monitor": [
                "Invest India FDI statistics explainer (PLI outcome figures)"],
            "layer_18_state_monitor": [
                "NITI state indices (Export Preparedness, Fiscal Health, SDG, Innovation)"
                if NITI_NDAP else "NITI state indices"],
        },
    }
    with open(OUT, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    print("members scraped:", len(waipa_members),
          "| urls checked:", len(checked))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
