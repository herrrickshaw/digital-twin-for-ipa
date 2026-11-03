"""Layer 40 trade-fair table (hand-curated data, one dict per event)."""
EVENTS = [
    {"name": "India ITME", "sector": "Textiles & Apparel", "scope": "India (the sector's flagship India-domestic fair)",
     "frequency": "biennial", "last_edition": {"year": 2022, "location": "Greater Noida",
     "exhibitor_list_url": "https://corporate.india-itme.com/gttes2025/PDF/Past-Event-INDIA-ITME-2022-Exhibitor-List.pdf",
     "total_exhibitors": "1,800+", "international_exhibitors": 148},
     "next_edition": {"year": 2026, "dates": "Dec 4-9, 2026", "location": "Greater Noida"},
     "cross_validated_association_members": ["Swiss Textile Machinery Association (~20 of 42 confirmed exhibiting 2026)",
                                              "ACIMIT (Lonati, Santoni, Reggiani Macchine seen in 2022 list)",
                                              "VDMA-adjacent (Trützschler, Lindauer Dornier, Mayer & Cie seen in 2022 list)",
                                              "JTMA-adjacent (Murata Machinery, Tsudakoma, TMT Machinery seen in 2022 list)"],
     "value": "HIGHEST -- revealed-preference signal (paid to physically exhibit in India), independently verified against 4 separate national association rosters",
     "last_verified": "2026-08-22", "recheck_recommended": "before/after each biennial edition (next: Dec 2026)"},
    {"name": "ITMA", "sector": "Textiles & Apparel", "scope": "Global (run by CEMATEX, rotates European cities)",
     "frequency": "every 4 years", "last_edition": {"year": 2023, "location": "Milan",
     "exhibitor_list_url": "itma.com/exhibitor-list -- now 404, only a logistics pre-arrival-guide PDF found, NOT an exhibitor catalog"},
     "next_edition": {"year": 2027, "note": "per CEMATEX's normal 4-year cadence, not independently confirmed"},
     "cross_validated_association_members": ["BTMA (ITMA-2023 exhibitor brochure, ~31 of 49 UK members)"],
     "value": "MEDIUM -- exhibitor catalog is now an interactive online platform, not a downloadable PDF; only a partial (BTMA-subset) PDF found",
     "last_verified": "2026-08-22", "recheck_recommended": "check itma.com ahead of the 2027 edition for a catalog format change"},
    {"name": "ITMA Asia+CITME", "sector": "Textiles & Apparel", "scope": "Asia (CEMATEX + China's CTMA/CCPIT TEX co-owned)",
     "frequency": "irregular (last: Singapore 2025)", "last_edition": {"year": 2025, "location": "Singapore",
     "note": "India was the largest non-Europe/non-China exhibitor group (87 exhibitors) and topped overseas-visitor rankings"},
     "next_edition": None, "cross_validated_association_members": [],
     "value": "MEDIUM -- strong India-engagement STATISTIC published by CEMATEX, but no exhibitor-list PDF found in this pass",
     "last_verified": "2026-08-22", "recheck_recommended": "search itmaasia.com for a catalog closer to the next edition"},

    # -- India-domestic gold-find exhibitor catalogs --------------------------
    {"name": "SEMICON India", "sector": "Electronics & Semiconductors", "scope": "India",
     "frequency": "annual", "last_edition": {"year": 2025,
     "exhibitor_list_url": "https://expo.semi.org/india2025/public/exhibitors.aspx?ID=31493",
     "total_exhibitors": 351},
     "value": "HIGHEST -- 351 verified real exhibitors incl. ASML, Applied Materials, Lam Research, "
             "KLA-Tencor, Tokyo Electron, Micron, Synopsys, Cadence, plus co-exhibiting national "
             "bodies (KOTRA, Japan India Business Bureau, SPETA Singapore)",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "ELECRAMA", "sector": "White Goods & Electricals", "scope": "India",
     "frequency": "~3-yearly (IEEMA-run)", "last_edition": {"year": 2023,
     "exhibitor_list_url": "https://elecrama.com/wp-content/uploads/2023/02/ELECRAMA-2023-Exhibitor-List-with-Products-1-2.xlsx",
     "total_exhibitors": 929},
     "value": "HIGH -- real downloadable XLSX, 929 rows w/ hall/stall + product category; confirmed "
             "Canada, Germany, Italy, France national pavilions inside the data",
     "last_verified": "2026-08-22", "recheck_recommended": "next ~3-yearly edition"},
    {"name": "Medical Fair India", "sector": "Medical Devices", "scope": "India",
     "frequency": "annual", "last_edition": {"year": 2024,
     "exhibitor_list_url": "https://www.medicalfair-india.com/PDF/Exhibitor-List_MFI-2024.pdf",
     "total_exhibitors": 364, "international_exhibitors": 40},
     "value": "HIGHEST -- direct ITME-pattern match, country-tagged, real intl names (Germany, "
             "China, Korea, Taiwan, Italy, Malaysia, UK, Turkey, Australia, HK, Singapore, "
             "Thailand, Vietnam)",
     "last_verified": "2026-08-22", "recheck_recommended": "annual (2026 edition page already live)"},
    {"name": "IPHEX India", "sector": "Pharma & Bulk Drugs", "scope": "India",
     "frequency": "annual (Pharmexcil-run)", "last_edition": {"year": 2026,
     "note": "outbound-facing (Indian exporters showing to foreign buyers), not foreign companies entering India"},
     "value": "LOW -- structurally the wrong direction for this project's use case, deprioritized vs Medical Fair India",
     "last_verified": "2026-08-22", "recheck_recommended": "low priority"},
    {"name": "CPHI India", "sector": "Pharma & Bulk Drugs", "scope": "India",
     "frequency": "annual", "last_edition": {"year": 2024, "note": "~2,000 exhibitors reported (PMEC India component)"},
     "value": "MEDIUM-HIGH potential, LOW accessed -- real exhibitor portal exists "
             "(exhibitors.cphi.com/cpin24/ etc.) but gated behind free buyer-account signup + JS-rendered",
     "last_verified": "2026-08-22", "recheck_recommended": "worth a buyer-account signup follow-up"},
    {"name": "ChemTECH World Expo", "sector": "Chemicals & Plastics", "scope": "India",
     "frequency": "annual (Jasubhai Media/Chemtech Foundation)", "last_edition": {"year": 2024,
     "exhibitor_list_url": "https://jasubhaimedia.com/cloud/chemtech-2024/chemtech-2024-exhibitors-list.pdf",
     "total_exhibitors": "750+", "note": "39+ countries represented"},
     "value": "HIGHEST -- full complete PDF, real intl names across Germany, China, Czechia, "
             "Sweden, Singapore, Thailand, Iran, Russia, US",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "REI Expo (Renewable Energy India Expo)", "sector": "Green Energy & Fuels", "scope": "India",
     "frequency": "annual (Informa Markets)", "last_edition": {"year": 2024,
     "total_exhibitors": "800+", "note": "51,921 trade visitors; UK was Country Partner 2024"},
     "value": "MEDIUM -- real scale confirmed but exhibitor index is a dynamic directory, not a "
             "downloadable PDF (a Scribd 'Show Directory 2024' 357-page doc exists but wasn't extractable)",
     "last_verified": "2026-08-22", "recheck_recommended": "browser-based pull of the exhibitor-list-index or the Scribd doc"},
    {"name": "The smarter E India / Intersolar India", "sector": "Green Energy & Fuels", "scope": "India",
     "frequency": "annual", "last_edition": {"year": 2024, "location": "Gandhinagar, Gujarat",
     "note": "~500+ exhibitors, predominantly India-based with a China cluster"},
     "value": "MEDIUM -- confirms a real India edition exists; exhibitor list is a filterable web "
             "app, not a static catalog, so no clean company-by-country pull yet",
     "last_verified": "2026-08-22", "recheck_recommended": "browser-based pull of thesmartere.in/exhibitor-list"},
    {"name": "Plastindia", "sector": "Chemicals & Plastics", "scope": "India",
     "frequency": "~5-yearly (Plastindia Foundation)", "last_edition": {"year": 2023,
     "total_exhibitors": "1,800+", "note": "45 countries represented"},
     "value": "LOW-MEDIUM -- scale confirmed + real regional-agent structure (Messe Düsseldorf for "
             "Europe/Americas, Adsale for China/HK) but no exhibitor NAMES obtained (e-directory "
             "DNS-dead, mirrors blocked)",
     "last_verified": "2026-08-22", "recheck_recommended": "browser session against plastindiaexhibition.plastindia.org"},
    {"name": "Auto Expo — The Components Show", "sector": "Auto, EV & Components", "scope": "India",
     "frequency": "biennial (ACMA/CII/SIAM)", "last_edition": {"year": 2023,
     "exhibitor_list_url": "http://web.archive.org/web/20240801200908/http://autoexpo.in/components-show/images/exhibitor-list/list-of-exhibitors23.pdf",
     "total_exhibitors": "350+ India, ~60 foreign", "note": "live domain dead, recovered via Wayback"},
     "cross_validated_association_members": ["VDA (German pavilion incl. Mahle Holding India, Freudenberg-NOK)",
                                             "JAMA-adjacent (Japan pavilion incl. Sumida Corp, Teijin)"],
     "value": "HIGHEST -- 7 national pavilions (Japan, Korea, Germany, UK, Chinese Taipei, Poland, "
             "France) with real named companies, direct India-market-entry signal",
     "last_verified": "2026-08-22", "recheck_recommended": "next biennial edition"},
    {"name": "ACMA Automechanika New Delhi", "sector": "Auto, EV & Components", "scope": "India",
     "frequency": "annual/biennial (ACMA + Messe Frankfurt)", "last_edition": {"year": 2026,
     "total_exhibitors": "870+", "note": "20 countries; 2026 edition largest yet"},
     "value": "MEDIUM -- press-release names only (AutoTuner, GMB, Kamoi Kakoshi, Horse Powertrain "
             "Solutions) confirmed; full exhibitor directory is JS-search-gated, no PDF found",
     "last_verified": "2026-08-22", "recheck_recommended": "live-browser session against the exhibitor-search widget"},
    {"name": "Aero India", "sector": "Aerospace & Defence", "scope": "India",
     "frequency": "biennial", "last_edition": {"year": 2019,
     "exhibitor_list_url": "http://web.archive.org/web/20200928033301/https://aeroindia.gov.in/assets/pdf/AeroIndia2019_ExhibitorslistForeign.pdf",
     "total_exhibitors": 403, "international_exhibitors": 165, "note": "2025 edition's PDF exists but is an unparseable CorelDRAW export"},
     "value": "HIGHEST -- complete, country-tagged, real (dated 2019, structural reference): "
             "Airbus, Dassault, MBDA, Safran, Thales, Boeing, Lockheed Martin, Raytheon, GE "
             "Aviation, Elbit Systems, IAI, Rafael, BAE Systems, Rolls-Royce, Rosoboronexport, "
             "United Aircraft Corp, Sukhoi, Saab",
     "last_verified": "2026-08-22", "recheck_recommended": "next edition -- verify PDF format before assuming parseable"},
    {"name": "DefExpo India", "sector": "Aerospace & Defence", "scope": "India",
     "frequency": "biennial", "last_edition": {"year": 2022, "location": "Gandhinagar",
     "note": "STRUCTURALLY restricted to Indian companies as primary exhibitors -- foreign OEMs "
            "could only appear via Indian subsidiaries/JVs"},
     "value": "LOW by design, not a research gap -- 2020 (Lucknow) edition's 700+-exhibitor "
             "directory recovered via Wayback shows the pre-restriction pattern (Airbus, BAE "
             "Systems, Boeing, Dassault, Elbit, Embraer, Russian state shipbuilders) as a structural reference",
     "last_verified": "2026-08-22", "recheck_recommended": "check whether the Indian-only restriction persists at the next edition"},
    {"name": "India Maritime Week / INMEX SMM India", "sector": "Shipbuilding & Marine", "scope": "India",
     "frequency": "annual (IMW) / biennial (INMEX)", "last_edition": {"year": 2025,
     "total_exhibitors": "500+", "note": "85 countries represented at IMW 2025"},
     "value": "MEDIUM -- real named participants from press coverage (Maersk, DP World, Wärtsilä, "
             "Royal IHC, DNV) + ~26 INMEX SMM India exhibitor names from the site's logo gallery; "
             "no full directory PDF found, IMW registration is login-gated",
     "last_verified": "2026-08-22", "recheck_recommended": "browser session closer to next edition"},
    {"name": "AAHAR", "sector": "Food Processing", "scope": "India",
     "frequency": "annual (ITPO)", "last_edition": {"year": 2024,
     "exhibitor_list_url": "http://web.archive.org/web/20250419202637/https://indiatradefair.com/aahardelhi/uploads/pdfs/AAHAR%202024%20HALLWISE%20LIST%20OF%20PARTICIPANTS.pdf",
     "international_exhibitors": 139, "note": "live site (indiatradefair.com) retired Dec 2025, recovered via Wayback"},
     "value": "HIGHEST -- complete Hall 1 foreign-participation list: Kikkoman India, Lactalis, "
             "bioMérieux, Savencia, Kerry Ingredients India, plus multiple Italian specialty-food "
             "makers and national trade bodies (JETRO, Australian Trade & Investment Commission, "
             "British High Commission)",
     "last_verified": "2026-08-22", "recheck_recommended": "check itpo.gov.in for the successor listing"},
    {"name": "IMME (International Mining & Machinery Exhibition)", "sector": "Specialty Steel & Metals", "scope": "India",
     "frequency": "~4-yearly (CII-run, Kolkata)", "last_edition": {"year": 2024, "location": "Kolkata",
     "exhibitor_list_url": "https://immeindia.in/listofexhibitors.php", "total_exhibitors": 268,
     "note": "13 countries: India 235, Australia 10, Czech Republic 8, UK 4, Germany 2, plus 1 "
            "each US/Norway/Finland/Brazil/Russia/China/S.Korea/S.Africa/Poland"},
     "cross_validated_association_members": ["Austmine (led the 10-company Australian delegation, "
                                             "the largest non-India contingent)"],
     "value": "HIGHEST -- full HTML table scraped, real country tags per company; Australia's "
             "delegation is a clean, concrete India-mining-sector engagement signal",
     "last_verified": "2026-08-22", "recheck_recommended": "next ~4-yearly edition"},

    # -- Global flagship events (non-India editions) --------------------------
    {"name": "IAA Mobility", "sector": "Auto, EV & Components", "scope": "Global (Munich)",
     "last_edition": {"year": 2025, "exhibitor_list_url": "https://exhibitors.iaa-mobility.com/exhibitordirectory/2025/start/"},
     "value": "HIGH -- live scrapable HTML, country-tagged, paginated (15-60/page); Mercedes-Benz, "
             "BMW, Audi, BYD, plus a large international startup hall",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "Automechanika Frankfurt", "sector": "Auto, EV & Components", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://automechanika.messefrankfurt.com/frankfurt/en/exhibitor-search.html?country=<ISO3>",
     "total_exhibitors": "137 pages"},
     "value": "HIGH -- live, scrapable, COUNTRY-FILTERABLE via URL param (?country=IND returned 160 "
             "real Indian exhibitors as proof of concept) -- same technique usable for any country",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "CPHI Worldwide (CPHI Milan)", "sector": "Pharma & Bulk Drugs", "scope": "Global (Milan)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://exhibitors.cphi.com/cpww26/",
     "total_exhibitors": 2909, "note": "80-country filter confirmed working"},
     "value": "HIGHEST -- live, scrapable, explicitly country-tagged per exhibitor with booth "
             "number; India, Poland, Greece, Singapore, Italy, Denmark, Korea, China, US all sampled real",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "MEDICA", "sector": "Medical Devices", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://www.medica-tradefair.com/vis/v1/en/search",
     "total_exhibitors": 3020, "note": "country breakdown: Germany 607, China 428, US 239, Italy 222, Turkey 163"},
     "value": "HIGH -- live scrapable (needed a real browser, WebFetch alone returned blank), "
             "country-level index confirmed, per-company country tag needs one more extraction step",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "Arab Health / World Health Expo Dubai", "sector": "Medical Devices", "scope": "Global (Dubai)",
     "last_edition": {"year": 2026, "note": "official current-edition list did not render usable data"},
     "value": "GAP -- confirmed empty in live browser, not a fetch-tool artifact; third-party "
             "substitutes (exhibitor-catalogue.com, 10times.com) lack reliable per-company country tags",
     "last_verified": "2026-08-22", "recheck_recommended": "retry closer to the event, or check the exhibitor-catalogue.com 2025 edition"},
    {"name": "ACHEMA", "sector": "Chemicals & Plastics", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://www.achema.de/en/search", "total_exhibitors": 1692},
     "value": "HIGH -- live scrapable via browser (JS-blocked to plain fetch), ISO-code country tag per exhibitor",
     "last_verified": "2026-08-22", "recheck_recommended": "every 3 years (normal ACHEMA cadence)"},
    {"name": "K Fair", "sector": "Chemicals & Plastics", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2025, "exhibitor_list_url": "https://www.k-online.com/vis/v1/en/directory/a",
     "total_exhibitors": 3259, "note": "66 countries; A-Z paginated directory (Messe Düsseldorf 'vis/v1' platform, shared with GIFA/METEC)"},
     "value": "HIGH -- live scrapable via browser, city+country per exhibitor; sample includes "
             "Aawadkrupa Plastomech (India)",
     "last_verified": "2026-08-22", "recheck_recommended": "every 3 years (normal K cadence)"},
    {"name": "Intersolar Europe / The smarter E Europe", "sector": "Green Energy & Fuels", "scope": "Global (Munich)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://www.intersolar.de/ausstellerliste", "total_exhibitors": "2,600+"},
     "value": "HIGH -- live scrapable via browser, hall/booth + sub-exhibition + country per row; "
             "sample includes Adani Solar (India)",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "WindEnergy Hamburg", "sector": "Green Energy & Fuels", "scope": "Global (Hamburg)",
     "last_edition": {"year": 2024, "note": "page explicitly states 'list under construction' for the next (Sept 2026) edition; 2024 data taken down, no Wayback capture either"},
     "value": "GAP, confirmed genuine -- same organiser (Hamburg Messe) as SMM Hamburg, same pattern",
     "last_verified": "2026-08-22", "recheck_recommended": "closer to Sept 2026 edition; NEUREUTER FAIR MEDIA is organiser's only sanctioned 3rd-party list source, others flagged as scams by organiser"},
    {"name": "Farnborough International Airshow", "sector": "Aerospace & Defence", "scope": "Global (UK)",
     "last_edition": {"year": 2024, "exhibitor_list_url": "https://www.farnboroughairshow.com/the-show/exhibitor-listing/?page=N",
     "total_exhibitors": 1292},
     "value": "HIGHEST -- server-rendered HTML, plain-fetchable (no browser needed), company+stand+"
             "country per row across ~65 pages; sample includes Aero Fasteners (India)",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial (alternates with Paris Air Show)"},
    {"name": "GIFA/METEC (Bright World of Metals)", "sector": "Specialty Steel & Metals", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2023, "exhibitor_list_url": "https://www.gifa.com/vis/v1/en/directory/a",
     "note": "shared database across GIFA/METEC/THERMPROCESS/NEWCAST"},
     "value": "HIGH -- live scrapable via browser, city+country per exhibitor incl. AIST (US), "
             "ABIFA (Brazil), dense China refractory/metallurgy cluster",
     "last_verified": "2026-08-22", "recheck_recommended": "every 4 years (normal GIFA cadence)"},
    {"name": "SMM Hamburg", "sector": "Shipbuilding & Marine", "scope": "Global (Hamburg)",
     "last_edition": {"year": 2024, "note": "next (Sept 2026) edition directory shows dates only, zero exhibitor entries; 2024 data gone, Wayback captures from Apr 2026 also empty"},
     "value": "GAP, confirmed genuine -- only a product-category taxonomy PDF exists, not a roster",
     "last_verified": "2026-08-22", "recheck_recommended": "closer to Sept 2026 edition"},
    {"name": "SEMICON West", "sector": "Electronics & Semiconductors", "scope": "Global (US)",
     "last_edition": {"year": 2023, "exhibitor_list_url": "https://web.archive.org/web/20250118204001/https://expo.semi.org/west2023/Public/exhibitors.aspx?ID=26835",
     "note": "live site deactivates past editions post-show; recovered via Wayback"},
     "value": "HIGH -- real archived alphabetical list w/ national pavilions (Korea, Silicon "
             "Saxony/Germany, MATRADE/Malaysia); ASML, KLA, Lam Research, TEL, Veeco, Advantest",
     "last_verified": "2026-08-22", "recheck_recommended": "check Wayback for each subsequent annual edition post-show"},
    {"name": "electronica", "sector": "Electronics & Semiconductors", "scope": "Global (Munich)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://exhibitors.electronica.de/exhibitor-portal/2026/list-of-exhibitors/",
     "note": "official downloadable XLSX also exists"},
     "value": "HIGHEST of the global electronics events -- server-rendered HTML table, company+city"
             "+country+booth for every exhibitor, AND a direct XLSX export button",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "CES", "sector": "Electronics & Semiconductors", "scope": "Global (Las Vegas)",
     "last_edition": {"year": 2026, "note": "MapYourShow-platform JSON API confirmed working via archive, supports country filtering, but needs scripted pagination (thousands of exhibitors); no dedicated semiconductor category exists at CES"},
     "value": "MEDIUM, effort-heavy -- technically retrievable, needs a live-browser scripted pull, not a one-shot fetch",
     "last_verified": "2026-08-22", "recheck_recommended": "live-browser session with pagination script if pursued"},
    {"name": "MINExpo INTERNATIONAL", "sector": "Specialty Steel & Metals", "scope": "Global (Las Vegas)",
     "last_edition": {"year": 2024, "note": "MapYourShow gallery link now redirects to homepage, expired; next edition Sept 2028"},
     "value": "GAP -- no public exhibitor list currently live",
     "last_verified": "2026-08-22", "recheck_recommended": "closer to Sept 2028 edition"},
    {"name": "bauma", "sector": "Specialty Steel & Metals", "scope": "Global (Munich)",
     "last_edition": {"year": 2025, "note": "exhibitors.bauma.de confirmed real, Elasticsearch-backed, has a PDF-export API endpoint, but landing page returns no static data"},
     "value": "GAP for now, but access pattern CONFIRMED VIABLE (same Messe München style as electronica/IAA Mobility) -- needs a follow-up session driving the actual search/AJAX calls",
     "last_verified": "2026-08-22", "recheck_recommended": "dedicated follow-up session to drive the AJAX search"},
    {"name": "OTC (Offshore Technology Conference)", "sector": "Oil & Gas (not yet a twin focus sector)", "scope": "Global (Houston)",
     "last_edition": {"year": 2026, "exhibitor_list_url": "https://otc2026.smallworldlabs.com/exhibitors",
     "total_exhibitors": "1,100+"},
     "value": "MEDIUM-HIGH, PARTIALLY harvested -- real static-rendered directory, ~50 names sampled "
             "with some country tags (Nigeria, Brazil, India); fully paginated, not exhaustively pulled",
     "last_verified": "2026-08-22", "recheck_recommended": "complete the pagination pull if this sector becomes a twin focus"},
    {"name": "ADIPEC", "sector": "Oil & Gas (not yet a twin focus sector)", "scope": "Global (Abu Dhabi)",
     "last_edition": {"year": 2022, "note": "official site is marketing-only (2,250+ exhibitors, no names); real sample only via a third-party PDF mirror (pdfcoffee.com), unverified provenance"},
     "value": "MEDIUM, LOW-CONFIDENCE source -- ADNOC, bp, Chevron, ExxonMobil, Shell, TotalEnergies, "
             "Baker Hughes, Halliburton, Siemens Energy all sampled but from an unofficial mirror",
     "last_verified": "2026-08-22", "recheck_recommended": "find the official current-year exhibitor list directly"},
    {"name": "IMARC (International Mining and Resources Conference, Sydney)", "sector": "Specialty Steel & Metals", "scope": "Global (Sydney)",
     "last_edition": {"year": 2025, "note": "JS-rendered, 600+ exhibitors claimed but only a small unverifiable sample surfaced"},
     "value": "GAP, LOW-CONFIDENCE -- not a clean pull",
     "last_verified": "2026-08-22", "recheck_recommended": "live-browser session"},
    {"name": "India Energy Week", "sector": "Oil & Gas (not yet a twin focus sector)", "scope": "India",
     "last_edition": {"year": 2024, "location": "Goa", "note": "real exhibitor PDF exists on Scribd (name+stand+country of origin confirmed present) but preview-blocked from full extraction"},
     "value": "MEDIUM potential, LOW accessed -- needs direct Scribd download/login",
     "last_verified": "2026-08-22", "recheck_recommended": "manual Scribd download follow-up"},

    # -- Railways (NEW sector, not previously a twin focus sector) -----------
    {"name": "InnoTrans", "sector": "Railways & Rail Transport (not yet a twin focus sector)", "scope": "Global (Berlin)",
     "last_edition": {"year": 2026, "location": "Berlin", "dates": "Sep 22-25, 2026",
     "exhibitor_list_url": "https://plus.innotrans.de/showfloor/organizations", "total_exhibitors": 3082,
     "note": "5 segments: Railway Technology, Railway Infrastructure, Public Transport, Interiors, "
            "Tunnel Construction; occupies all 42 Berlin Exhibition Grounds halls"},
     "value": ("HIGHEST of the global railway sources -- FULL EXTRACTION COMPLETE 2026-08-22, all "
               "3,082 exhibitors, no sampling, no gaps (verified against the API's own `count` field, "
               "no duplicate IDs). Method: the site is a Corussoft 'EventGuide' white-label platform "
               "(confirmed via JS bundle analysis) -- passive network-request observation showed only "
               "static assets, so the real data call was caught by MONKEY-PATCHING window.fetch inside "
               "the live page and triggering a UI search. True backend: "
               "POST https://live.messebackend.aws.corussoft.de/webservice/search (form-urlencoded, "
               "short-lived anonymous beConnectionToken JWT, reusable via curl once captured -- no AWS "
               "SigV4 needed). Paginated with filterlist=entity_orga&order=lexic&numresultrows=75&"
               "startresultrow=N. 61 countries: Germany 1,039, China 241, France 217, Italy 215, "
               "Switzerland 143, INDIA 92, USA 50. Data: data/trade_fairs/railways/"
               "innotrans_2026_exhibitors.csv (company, country, city, postcode, hall, stand, segment, "
               "description, id). 🔑 This Corussoft platform pattern may be reused by OTHER Messe "
               "Berlin / white-label-hosted fairs -- worth checking for other events on the same "
               "platform before assuming each new fair needs its own bespoke scrape."),
     "last_verified": "2026-08-22", "recheck_recommended": "biennial; re-run the same fetch-patch method for the next edition"},
    {"name": "IREE (International Railway Equipment Exhibition)", "sector": "Railways & Rail Transport (not yet a twin focus sector)", "scope": "India",
     "last_edition": {"year": 2025, "location": "Bharat Mandapam, Delhi",
     "exhibitor_list_url": "https://www.ireeindia.com/pdf/2025/exhibition-form/IREE-Exhibitors-List.pdf",
     "total_exhibitors": 250,
     "note": "16th edition, CII + Ministry of Railways, Asia's largest rail-sector event; PDF's internal "
            "title is 'KEY EXHIBITORS' -- a submitted-profile directory, not necessarily literally all "
            "450+ exhibitors the event claims"},
     "value": ("HIGH -- 250 entries extracted (font-weight-aware PDF parsing), 34 flagged foreign/"
               "foreign-parent by a legal-suffix + description heuristic (27 without parser-merge "
               "artifacts). Genuine finds in the clean subset: Wabtec Corporation (WIIPL, US rail "
               "giant), ZF Friedrichshafen AG, Vossloh India (German parent), Voestalpine VAE VKN "
               "India (Austrian parent), AB Connectors Ltd (TT Electronics plc subsidiary -- also "
               "independently seen in the VDA Group III roster). 🔴 Some 'clean' rows are still parser "
               "artifacts despite the flag (e.g. 'Corporation Limited' alone, two names concatenated "
               "in a couple of rows) -- spot-check before treating any single row as ground truth. "
               "Data: data/trade_fairs/railways/iree_2025_key_exhibitors.json."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual, re-parse against the next edition's PDF"},
    {"name": "RailTrans Expo", "sector": "Railways & Rail Transport (not yet a twin focus sector)", "scope": "India",
     "last_edition": {"year": 2026, "location": "Bharat Mandapam, Delhi", "note": "6th edition, Jul 2026"},
     "value": ("LOW -- confirmed genuine gap, not under-researched: no exhibitor-list PDF or structured "
               "export exists. Only a 'Key Partners and Exhibitors 2025' page with ~29 headline "
               "sponsors (Siemens, Alstom, DB Engineering, MxV Rail, JICA, Jindal Stainless, BHEL). "
               "Organizer is a private events company (Urban Infra Communication Pvt. Ltd.), not CII/"
               "Ministry-run like IREE; self-reported ~250 exhibitors/6 countries/3-5k daily footfall "
               "are UNAUDITED claims, not independently verified."),
     "last_verified": "2026-08-22", "recheck_recommended": "low priority until a real roster surfaces"},

    # -- Other newly-identified sectors/events, not yet deep-dived -----------
    {"name": "Light + Building", "sector": "Construction & Building Materials (not yet a twin focus sector)", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2026, "note": "lighting, electrical engineering, building/home automation; biennial",
     "exhibitor_list_url": "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search?findEventVariable=LIGHTBUILDING",
     "total_exhibitors": "1884 (full roster pulled)"},
     "value": "HIGH -- deep-dived 2026-08-22, full 1884-exhibitor roster pulled via the shared Messe "
             "Frankfurt exhibitor-service API (same platform as Automechanika). Top countries China "
             "497, Germany 411, Italy 150. Data: data/trade_fairs/messe_frankfurt/lightbuilding_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "ISH", "sector": "Construction & Building Materials (not yet a twin focus sector)", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2027, "note": "HVAC, water, heating, sanitation/building technology; biennial",
     "exhibitor_list_url": "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search?findEventVariable=ISH",
     "total_exhibitors": "2127 (full roster pulled)"},
     "value": "HIGH -- deep-dived 2026-08-22, full 2127-exhibitor roster pulled. Top countries Germany "
             "579, Italy 345, China 247, India 31. Data: data/trade_fairs/messe_frankfurt/ish_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "Heimtextil", "sector": "Textiles & Apparel", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2027, "note": "home & contract textiles -- distinct from ITMA's machinery focus; annual",
     "exhibitor_list_url": "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search?findEventVariable=HEIMTEXTIL",
     "total_exhibitors": "1182 (full roster pulled)"},
     "value": "HIGH -- deep-dived 2026-08-22, full 1182-exhibitor roster pulled. India is the #1 "
             "exhibiting country (304 of 1182, 25.7%) -- strongest India signal of any fair checked "
             "this session. Data: data/trade_fairs/messe_frankfurt/heimtextil_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "interpack", "sector": "Chemicals & Plastics", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2026, "note": "packaging processes & machinery; every 3 years",
     "exhibitor_list_url": "https://www.interpack.com/vis-api/vis/v1/en/directory/<a-z|other>",
     "total_exhibitors": "3085 (full roster pulled)"},
     "value": "HIGH -- deep-dived 2026-08-22, full 3085-exhibitor roster pulled via the Messe "
             "Duesseldorf DIMEDIS 'vis' A-Z directory API. Top countries Germany 609, China 451, "
             "Italy 436, India 111. Data: data/trade_fairs/messe_duesseldorf/interpack_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "EuroShop", "sector": "Retail Technology (not yet a twin focus sector)", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2026, "note": "retail technology, store design/fit-out; every 3 years",
     "exhibitor_list_url": "https://www.euroshop-tradefair.com/vis-api/vis/v1/en/directory/<a-z|other>",
     "total_exhibitors": "2014 (full roster pulled)"},
     "value": "MEDIUM -- deep-dived 2026-08-22, full 2014-exhibitor roster pulled. Top countries "
             "Germany 586, China 244, Italy 177; India only 8 (weak signal, retail tech/store fit-out "
             "not an India strength area yet). Data: data/trade_fairs/messe_duesseldorf/euroshop_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "wire & Tube Düsseldorf", "sector": "Specialty Steel & Metals", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2026, "note": "wire, cable, tube & pipe manufacturing -- finished-goods, "
     "distinct from GIFA/METEC's raw-material focus; biennial",
     "exhibitor_list_url": "https://www.wire-tradefair.com/vis-api/vis/v1/en/directory/<a-z|other> "
     "(tube-tradefair.com shares an IDENTICAL dataset -- co-located sister fairs, one combined roster)",
     "total_exhibitors": "2743 (full roster pulled; wire+Tube combined, not additive)"},
     "value": "HIGH -- deep-dived 2026-08-22, full 2743-exhibitor combined roster pulled. Top "
             "countries China 679, Germany 519, Italy 367, India 167 (#5). Data: "
             "data/trade_fairs/messe_duesseldorf/wire_dusseldorf_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "drupa", "sector": "Printing (not yet a twin focus sector)", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2028, "note": "printing/print technology; every 4 years, next edition 2028; the vis-platform "
     "site still serves a live directory for the 2024/prior cycle in the meantime",
     "exhibitor_list_url": "https://www.drupa.com/vis-api/vis/v1/en/directory/<a-z|other>",
     "total_exhibitors": "1725 (full roster pulled)"},
     "value": "MEDIUM -- deep-dived 2026-08-22, full 1725-exhibitor roster pulled despite the 2028 gap "
             "(the vis platform serves the current live directory year-round, not just around the show "
             "dates). Top countries Germany 453, China 414, Italy 149, India 70 (#4). Data: "
             "data/trade_fairs/messe_duesseldorf/drupa_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "next live edition 2028; directory can be re-pulled anytime before then"},
    {"name": "boot", "sector": "Marine & Watersports (not yet a twin focus sector)", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2027, "note": "boats, watersports, diving; annual",
     "exhibitor_list_url": "https://www.boot.com/vis-api/vis/v1/en/directory/<a-z|other>",
     "total_exhibitors": "1773 (full roster pulled)"},
     "value": "LOW -- deep-dived 2026-08-22, full 1773-exhibitor roster pulled. Top countries Germany "
             "744, Italy 136, Netherlands 119; India only 1 (essentially no signal -- watersports/boat "
             "manufacturing is not an India-relevant sector for this twin).",
     "last_verified": "2026-08-22", "recheck_recommended": "low priority, weak India signal"},
    {"name": "glasstec", "sector": "Construction & Building Materials (not yet a twin focus sector)", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2026, "note": "glass industry/technology; biennial",
     "exhibitor_list_url": "https://www.glasstec.de/vis-api/vis/v1/en/directory/<a-z|other>",
     "total_exhibitors": "1158 (full roster pulled)"},
     "value": "MEDIUM -- deep-dived 2026-08-22, full 1158-exhibitor roster pulled. Top countries China "
             "366, Germany 253, Italy 144; India 13 (modest, not a standout).",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "A+A", "sector": "Occupational Safety & PPE (not yet a twin focus sector)", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2027, "note": "occupational safety, PPE, health at work; biennial",
     "exhibitor_list_url": "https://www.aplusa-online.com/vis-api/vis/v1/en/directory/<a-z|other> "
     "(live domain is .com, not the commonly-guessed .de)",
     "total_exhibitors": "2514 (full roster pulled)"},
     "value": "MEDIUM -- deep-dived 2026-08-22, full 2514-exhibitor roster pulled. Top countries China "
             "642, Germany 566, Italy 150; India 61 (moderate signal in a genuinely new sector for "
             "this twin -- PPE/industrial-safety manufacturing).",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},
    {"name": "Caravan Salon", "sector": "Automotive & Auto Components", "scope": "Global (Düsseldorf)",
     "last_edition": {"year": 2026, "note": "caravans, motorhomes, camping; annual",
     "exhibitor_list_url": "https://www.caravan-salon.com/vis-api/vis/v1/en/directory/<a-z|other> "
     "(live domain is .com, not the commonly-guessed .de)",
     "total_exhibitors": "1008 (full roster pulled)"},
     "value": "GAP CONFIRMED, not fabricated -- deep-dived 2026-08-22, full 1008-exhibitor roster "
             "pulled cleanly (all 27 buckets, no sampling), yet India's count is a genuine ZERO. Top "
             "countries Germany 629, Italy 72, Netherlands 56. Real negative finding: India has no "
             "visible presence in caravan/motorhome/camping manufacturing at this fair.",
     "last_verified": "2026-08-22", "recheck_recommended": "low priority given the confirmed-zero signal"},
    {"name": "Ambiente", "sector": "Consumer Goods & Retail (not yet a twin focus sector)", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2027, "note": "consumer goods, home & household, gifts; annual",
     "exhibitor_list_url": "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search?findEventVariable=AMBIENTE",
     "total_exhibitors": "3655 (full roster pulled)"},
     "value": "HIGH -- deep-dived 2026-08-22, full 3655-exhibitor roster pulled. India is the #1 "
             "exhibiting country (515 of 3655, 14.1%), ahead of China (372) and Germany (367) -- the "
             "second India-top-country standout this session alongside Heimtextil, and by far the "
             "largest fair (by exhibitor count) where that's true. Data: "
             "data/trade_fairs/messe_frankfurt/ambiente_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "Techtextil", "sector": "Textiles & Apparel", "scope": "Global (Frankfurt)",
     "last_edition": {"year": 2027, "note": "technical textiles & nonwovens -- distinct from Heimtextil's "
     "home/contract-textile focus; biennial",
     "exhibitor_list_url": "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search?findEventVariable=TECHTEXTIL",
     "total_exhibitors": "1474 (full roster pulled)"},
     "value": "MEDIUM -- deep-dived 2026-08-22, full 1474-exhibitor roster pulled. Top countries "
             "Germany 340, China 176, Italy 172, France 94, Türkiye 69; India 63 (#6, present but "
             "not a standout the way it is at Heimtextil/Ambiente). Data: "
             "data/trade_fairs/messe_frankfurt/techtextil_exhibitors.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "biennial"},

    # -- India-domestic events, deep-dived 2026-08-22 (Delhi/Mumbai gap-scan follow-up) ---------
    {"name": "India International Jewellery Show (IIJS)", "sector": "Jewellery & Gems (not yet a twin focus sector)", "scope": "India (Mumbai)",
     "last_edition": {"year": 2026, "location": "JWCC + Nesco, Mumbai", "dates": "Aug 5-10, 2026",
     "note": "IIJS Bharat -- Premiere, 42nd edition; GJEPC-run, 3 editions/year (Signature/Premiere/Tritiya), "
            "Premiere is the largest",
     "exhibitor_list_url": "https://gjepc.org/iijs-premiere/exhibitor-list.php", "total_exhibitors": 2163},
     "value": "HIGH -- deep-dived 2026-08-22. GJEPC serves the full 2,163-exhibitor table server-side in "
             "plain HTML (no PDF, no gate). 76 exhibitors (3.5%) flagged FOREIGN via GJEPC's own "
             "'International Machinery/Jewellery/Loose' section field: Italy 24, Thailand 13, Hong Kong "
             "11, UAE 10, Turkey 5, Japan 4, China 2, plus one each US/Netherlands/Singapore/Germany/"
             "Switzerland. Every row (including the 2,087 default-domestic ones) carries an explicit "
             "flag_basis field. Data: data/trade_fairs/india_domestic/iijs/iijs_participants.csv",
     "last_verified": "2026-08-22", "recheck_recommended": "re-pull each edition; cheap (one page fetch)"},
    {"name": "India Mobile Congress (IMC)", "sector": "Telecom (distinct from Electronics & Semiconductors)", "scope": "India (Delhi)",
     "last_edition": {"year": 2025, "location": "Yashobhoomi Convention & Expo Centre, Dwarka, New Delhi",
     "dates": "Oct 8-11, 2025", "note": "9th edition; DoT + COAI; organizer-claimed 400+ exhibitors/"
            "150+ countries (self-reported, unaudited); official domain is indiamobilecongress.com, "
            "NOT imc.org.in"},
     "value": "GAP CONFIRMED, not fabricated -- deep-dived 2026-08-22. The organizer's own exhibitor "
             "directory is a lead-gen form gate (requires submitting name/email/phone before showing "
             "any data) -- correctly not filled in or bypassed. No public roster exists. Lower-confidence "
             "fallback delivered instead: 9 named companies from verifiable press/organizer sources -- "
             "FOREIGN: Nokia, Ericsson, Qualcomm, Quectel, Skylo, IPification (lower-confidence); "
             "FOREIGN-PARENT: Samsung (via its India subsidiary); plus named country delegations "
             "(Japan, Canada, UK, Russia, Ireland, Austria) and a Japan/GSMA pavilion. Data: "
             "data/trade_fairs/india_domestic/india_mobile_congress/",
     "last_verified": "2026-08-22", "recheck_recommended": "low priority until the org opens a public directory"},
    {"name": "ACETECH", "sector": "Construction & Building Materials (not yet a twin focus sector)", "scope": "India (Mumbai/Delhi/Bengaluru)",
     "last_edition": {"year": 2025, "location": "Bombay Exhibition Centre (NESCO), Mumbai", "dates": "Nov 6-9, 2025",
     "note": "19th Mumbai edition (flagship city); organizer is ABEC Exhibitions & Conferences Pvt. Ltd., "
            "NOT 'ThreeSixty Marketing Services' as originally assumed -- correct live domain is "
            "acetechexpo.com, NOT acetechindia.com (that domain belongs to an unrelated software company)"},
     "value": "GAP CONFIRMED, not fabricated -- deep-dived 2026-08-22, genuinely no public exhibitor/"
             "participant roster exists anywhere checked (18-page site sitemap, 10times.com, ExpoFP, "
             "Scribd). Verified foreign exhibitor count: 0. Only qualitative signals found: 11 "
             "international trade chambers listed as 'supported by' (not exhibitors), and one "
             "candidate company correctly REJECTED after verification (an India-HQ'd firm with an old "
             "Italian JV, not foreign-HQ'd -- kept as a worked example of avoiding name-similarity "
             "false positives). Data: data/trade_fairs/india_domestic/acetech/",
     "last_verified": "2026-08-22", "recheck_recommended": "low priority until a real roster surfaces"},
    {"name": "Convergence India", "sector": "Telecom (distinct from Electronics & Semiconductors)", "scope": "India (Delhi)",
     "last_edition": {"year": 2026, "location": "Bharat Mandapam, New Delhi", "dates": "Mar 23-25, 2026",
     "note": "33rd edition; organized by Exhibitions India Group + ITPO, co-located with Smart Future "
            "Cities India/Satcom India/Broadcast India/India IoT Expo",
     "exhibitor_list_url": "https://www.convergenceindia.org/exhibitors-and-participants-convergence-india.aspx",
     "total_exhibitors": 1021},
     "value": "HIGH -- deep-dived 2026-08-22. Unlike most India-domestic B2B shows, the official site "
             "exposes a genuine structured exhibitor directory with a real Country field per row (JS "
             "widget, no public API -- driven live across 43 pages, cross-verified against the site's "
             "own '1,021 of 1,021' counter). 149 foreign (14.6%) across 22 countries: China 46, Russia "
             "24 (Moscow government pavilion), Taiwan 24 (TAITRA pavilion), US 15, New Zealand 13. "
             "Data: data/trade_fairs/india_domestic/convergence_india/ (full roster + foreign-only subset)",
     "last_verified": "2026-08-22", "recheck_recommended": "re-pull each edition via the same live-browser widget method"},
    {"name": "Cement Expo", "sector": "Construction & Building Materials (not yet a twin focus sector)", "scope": "India (multi-city)",
     "last_edition": {"year": 2023, "location": "Manekshaw Centre, New Delhi", "dates": "Dec 15, 2023",
     "note": "14th edition; organizer ASAPP Info Global Services (publisher of Indian Cement Review); "
            "official domain cementexpo.in; 15th (2025) and 16th (Dec 2026, Greater Noida) editions "
            "exist but only the 14th has a recoverable exhibitor list"},
     "value": "MEDIUM, PARTIAL -- deep-dived 2026-08-22. No live exhibitor-directory page exists on the "
             "official site (logo walls only, no addresses/countries). A genuine booth-numbered "
             "exhibitor+partner table for the 14th edition was recovered from the official downloadable "
             "brochure PDF's 'GLIMPSES OF THE PAST' section: 63 companies -- 2 FOREIGN (name states the "
             "country directly: Pentol Germany, MIDES Industriais Brazil), 17 FOREIGN-PARENT "
             "(India subsidiary of an independently-verified foreign parent -- AMETEK, Testo, IKA, ABB, "
             "Horiba, Loesche, Evonik, Flender, and others), 44 likely domestic (unconfirmed). Data: "
             "data/trade_fairs/india_domestic/cement_expo/",
     "last_verified": "2026-08-22", "recheck_recommended": "check whether the 15th/16th edition brochures add a fresher list"},
    {"name": "India International Trade Fair (IITF)", "sector": "Cross-sector (general trade fair, not sector-specific)", "scope": "India (Delhi)",
     "last_edition": {"year": 2025, "location": "Bharat Mandapam, New Delhi", "dates": "Nov 14-27, 2025",
     "note": "44th edition; ITPO-organized; mixed B2B/B2C with a formal partner-country/foreign-pavilion "
            "structure, distinct in character from the sector-specific B2B shows elsewhere in this registry",
     "exhibitor_list_url": "https://www.itpo.gov.in/assets/images/iitf-pdf/IITF%202025%20-%20LIST%20OF%20EXHIBITORS.pdf"},
     "value": "HIGH, two-layer finding -- deep-dived 2026-08-22. COUNTRY-level (primary source, PIB press "
             "release): 11 countries in the International Pavilion -- China, Thailand, UAE, Malaysia, "
             "Sweden, Turkey, Iran, South Korea, Egypt, Lebanon, Tunisia -- plus the Tibetan Chamber of "
             "Commerce named separately. COMPANY-level (primary source, ITPO's own 503-row official "
             "exhibitor PDF): 24 rows carry an explicit ITPO-annotated ' - <Country>' suffix, all "
             "confined to the Hall 1 Ground Floor International Pavilion section -- Korea 10, Iran 3, "
             "UAE 2, Thailand 2, one each China/Egypt/Lebanon/Sweden/Tunisia/Turkey/Tibet. Honest gap: "
             "Malaysia is named at country level but has zero matching company rows in the PDF -- "
             "flagged, not hidden. Data: data/trade_fairs/india_domestic/iitf/",
     "last_verified": "2026-08-22", "recheck_recommended": "annual, re-pull the PIB release + ITPO PDF each edition"},
    {"name": "Messe Frankfurt -- unified cross-show India pull", "sector": "Cross-sector platform note", "scope": "Global (all Messe Frankfurt shows)",
     "last_edition": {"year": 2026,
     "exhibitor_list_url": "api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search (no findEventVariable filter = searches ALL shows at once, hitsTotal 49,665)",
     "note": "public apikey baked into the site's own JS bundle, reusable via plain curl/urllib once captured from one live browser session"},
     "value": ("🔑 PLATFORM-LEVEL FINDING, not a single event: omitting the event filter on Messe "
               "Frankfurt's shared exhibitor-service API searches its ENTIRE global show portfolio in "
               "one query. A country-filtered India-only pull returned 3,114 India-HQ'd exhibitors "
               "spanning 40+ Messe Frankfurt shows worldwide (ACMA Automechanika New Delhi, Ambiente, "
               "Paperworld Mumbai/Delhi, Media Expo, and more) -- a single call surfaces India "
               "engagement across the WHOLE Messe Frankfurt portfolio at once, not just the "
               "individually-named fairs in this registry. Ambiente and Techtextil (both confirmed "
               "live here) were subsequently deep-dived in full -- see their own entries above. "
               "Formnext did not respond to plain fetch, a genuine gap not a fabrication. Data: "
               "data/trade_fairs/messe_frankfurt/ (india-wide pull saved separately, see that dir's README)."),
     "last_verified": "2026-08-22", "recheck_recommended": "re-run the India-only pull periodically; cheap (one API call) high-value refresh"},
    {"name": "Messe Düsseldorf -- shared DIMEDIS 'vis' platform note", "sector": "Cross-sector platform note", "scope": "Global (multiple Düsseldorf shows)",
     "last_edition": {"year": 2026,
     "note": "one shared backend across Düsseldorf-hosted fairs, confirmed by a cross-domain test: "
            "hitting interpack.com's server while setting the X-Vis-Domain header to k-online.com "
            "returned K Fair's own data -- the domain is just a routing key, not a separate backend"},
     "value": ("🔑 PLATFORM-LEVEL FINDING: the same '<domain>/vis-api/vis/v1/en/directory/<a-z|other>' "
               "API (already used for K Fair and GIFA/METEC) powers interpack, EuroShop, and wire/"
               "Tube Düsseldorf, confirmed. Same platform subsequently confirmed AND fully pulled for "
               "**boot**, **drupa**, **glasstec**, **A+A**, **Caravan Salon** too -- see their own "
               "entries above (two, A+A and Caravan Salon, turned out to live on .com not the "
               "commonly-guessed .de). Any Messe Düsseldorf fair is a near-zero-marginal-cost pull "
               "once the domain is confirmed, same pagination pattern each time."),
     "last_verified": "2026-08-22", "recheck_recommended": "check for any remaining un-pulled Messe Düsseldorf fairs on this platform"},
]
