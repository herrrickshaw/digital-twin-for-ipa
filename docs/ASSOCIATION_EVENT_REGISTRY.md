# Association + event registry — for ongoing monitoring

*Generated 2026-08-22 by `scripts/build_layer40_association_event_registry.py`. Durable registry (URL + access method + recheck cadence), not a data snapshot -- see `docs/TEXTILE_ASSOCIATIONS.md` (layer 39) for the actual textile membership data this registry points to.*

## Associations

| Association | Sector | Scope | Members | Access | Linked events | Recheck |
|---|---|---|---|---|---|---|
| Swiss Textile Machinery Association | Textiles & Apparel | Switzerland | 42 | public HTML (full) + downloadable PDF (2023, 2025 editions - | India ITME, ITMA, ITMA Asia+CITME | annual, or before each India ITME cycle (biennial) |
| CEMATEX | Textiles & Apparel | Europe (federation of 9 national bodies) | 9 | public HTML, federation-level only (9 national associations, | ITMA, ITMA Asia+CITME | annual |
| ITMF | Textiles & Apparel | Global (40+ countries) | — | public HTML partial (national members 19/40+) + full (associ | — | annual (also publishes ITMSS annual shipment stats) |
| VDMA Textile Machinery | Textiles & Apparel | Germany (+ AT/FR/NL/IT/PT/CH/SE ~13%) | 140 | public but JS-rendered A-Z search UI, not scrapable via plai | ITMA, India ITME | annual; needs browser automation for full scrape |
| ACIMIT | Textiles & Apparel | Italy | 185 | public HTML (full, 185 members, segment+city tagged); Genera | ITMA, India ITME | annual |
| UKFT (UK Fashion & Textile Association) | Textiles & Apparel | United Kingdom | 500 | public HTML (500 of claimed 2,500+ members, many unlisted by | — | annual |
| The Textile Institute | Textiles & Apparel | Global (14 countries) | 50 | public HTML searchable DB, no PDF | — | annual |
| BTMA (British Textile Machinery Association) | Textiles & Apparel | United Kingdom | 49 | public HTML (full, 49 members); ITMA-2023 exhibitor-subset P | ITMA | annual, or before each ITMA cycle |
| JTMA (Japan Textile Machinery Association) | Textiles & Apparel | Japan | — | UNRELIABLE -- site returned ECONNREFUSED during research; on | India ITME | retry direct fetch; low confidence until then |
| CNTAC (China National Textile and Apparel Council) | Textiles & Apparel | China | — | partial council-roster PDF retrieved directly (~115 of likel | ITMA Asia+CITME | low priority -- structurally not a company roster |
| KOFOTI (Korea Federation of Textile Industries) | Textiles & Apparel | Korea | — | no public member directory; affiliated portal koreatextile.o | — | low priority until a real directory surfaces |
| SEMI | Electronics & Semiconductors | Global | 3000 | structure confirmed (~3,000 members, country/segment filtera | SEMICON India, SEMICON West, electronica | retry with live browser session |
| IPC / Global Electronics Association | Electronics & Semiconductors | Global | — | public HTML, no login, country-filterable, verified live | — | annual |
| CECED Europe / APPLiA (Home Appliance Europe) | White Goods & Electricals | Europe | — | direct fetch blocked (403); member list reconstructed via se | ELECRAMA | verify raw on ceced.eu/appliaeurope.eu directly |
| AHAM (Association of Home Appliance Manufacturers) | White Goods & Electricals | United States | 150 | direct fetch blocked; only a partial Canada-council fragment | — | needs direct authenticated pull from aham.org |
| CEAMA (Consumer Electronics and Appliances Manufacturers Association) | White Goods & Electricals | India | — | 403 on both WebFetch and curl -- no member data obtained | ELECRAMA | manual browser visit or Wayback Machine |
| VDA (Verband der Automobilindustrie) | Auto, EV & Components | Germany | 567 | public HTML, live site, fully scraped across 3 tiers | IAA Mobility, Automechanika Frankfurt, Auto Expo Components | annual |
| JAMA (Japan Automobile Manufacturers Association) | Auto, EV & Components | Japan | 14 | public HTML, FULL list, verified | Auto Expo Components | annual |
| CLEPA (European Association of Automotive Suppliers) | Auto, EV & Components | Europe | 116 | partial (~30 of 116 corporate members confirmed via search)  | IAA Mobility, Automechanika Frankfurt | live-browser pull of the flipbook for the full 116 |
| ACMA (Automotive Component Manufacturers Association of India) | Auto, EV & Components | India | 750 | confirmed structurally: ACMA holds MOUs (not memberships) wi | Auto Expo Components, ACMA Automechanika New Delhi | low priority -- structurally not a foreign-company source |
| EFPIA (European Federation of Pharmaceutical Industries and Associations) | Pharma & Bulk Drugs | Europe | 47 | public HTML, FULL list, verified | CPHI Worldwide | annual |
| PhRMA | Pharma & Bulk Drugs | United States | 31 | reconciled from Wikipedia/Ballotpedia citing PhRMA's own dis | CPHI Worldwide | verify raw on phrma.org/membership |
| MedTech Europe | Medical Devices | Europe | 300 | confirmed real, JS-filterable, didn't fully unroll via fetch | MEDICA, Medical Fair India | needs live browser to unroll full filter |
| AdvaMed | Medical Devices | United States | 1000 | confirmed real, 1,000+ companies, partial extraction (60+) | MEDICA, Medical Fair India | live browser for full 1,000+ |
| WindEurope | Green Energy & Fuels | Europe (35+ countries) | 600 | official archival PDF found (Aug 2024 snapshot, 40 pages) -- | WindEnergy Hamburg, Intersolar Europe | complete E-Z pages from the same PDF |
| SolarPower Europe | Green Energy & Fuels | Europe | 210 | THIRD-PARTY MIRROR ONLY (aalep.eu lobbying-transparency snap | Intersolar Europe | verify against live site or browser-driven filter pull |
| Cefic (European Chemical Industry Council) | Chemicals & Plastics | Europe (+ global affiliates) | 670 | TWO full official PDFs obtained (Partner Companies, Associat | ACHEMA, K Fair, ChemTECH World Expo | pull the ACOM corporate list via the Scribd mirror referenced on cefic.org |
| Austmine (Australia's mining equipment, technology & services industry association) | Specialty Steel & Metals | Australia | — | identified as the organiser of Australia's national delegati | IMME | pull austmine.com.au/members directly; cross-check against the IMME 2024 Australia delegation |
| ASD Europe (AeroSpace and Defence Industries Association of Europe) | Aerospace & Defence | Europe (22 countries) | 51 | public HTML, FULL list, verified | Aero India, DefExpo | annual |
| worldsteel (World Steel Association) | Specialty Steel & Metals | Global | 133 | public HTML, FULL list, verified | GIFA/METEC | annual |
| ICMM (International Council on Mining and Metals) | Specialty Steel & Metals | Global | 69 | public HTML, FULL list (403 to WebFetch, worked via curl+bro | IMME, MINExpo | annual |
| IPIECA | Oil & Gas (not yet a twin focus sector) | Global | 39 | public HTML, FULL corporate list, verified via WebFetch | ADIPEC, OTC, India Energy Week | annual |
| IOGP (International Association of Oil & Gas Producers) | Oil & Gas (not yet a twin focus sector) | Global | 90 | public HTML, partial (no downloadable PDF) | ADIPEC, OTC | annual |

## Events

| Event | Sector | Frequency | Last edition | Next edition | Value |
|---|---|---|---|---|---|
| India ITME | Textiles & Apparel | biennial | 2022 (Greater Noida) | 2026 Dec 4-9, 2026 | HIGHEST -- revealed-preference signal (paid to physically exhibit in I |
| ITMA | Textiles & Apparel | every 4 years | 2023 (Milan) | 2027  | MEDIUM -- exhibitor catalog is now an interactive online platform, not |
| ITMA Asia+CITME | Textiles & Apparel | irregular (last: Singapore 2025) | 2025 (Singapore) | TBD | MEDIUM -- strong India-engagement STATISTIC published by CEMATEX, but  |
| SEMICON India | Electronics & Semiconductors | annual | 2025 (?) | TBD | HIGHEST -- 351 verified real exhibitors incl. ASML, Applied Materials, |
| ELECRAMA | White Goods & Electricals | ~3-yearly (IEEMA-run) | 2023 (?) | TBD | HIGH -- real downloadable XLSX, 929 rows w/ hall/stall + product categ |
| Medical Fair India | Medical Devices | annual | 2024 (?) | TBD | HIGHEST -- direct ITME-pattern match, country-tagged, real intl names  |
| IPHEX India | Pharma & Bulk Drugs | annual (Pharmexcil-run) | 2026 (?) | TBD | LOW -- structurally the wrong direction for this project's use case, d |
| CPHI India | Pharma & Bulk Drugs | annual | 2024 (?) | TBD | MEDIUM-HIGH potential, LOW accessed -- real exhibitor portal exists (e |
| ChemTECH World Expo | Chemicals & Plastics | annual (Jasubhai Media/Chemtech Foundation) | 2024 (?) | TBD | HIGHEST -- full complete PDF, real intl names across Germany, China, C |
| REI Expo (Renewable Energy India Expo) | Green Energy & Fuels | annual (Informa Markets) | 2024 (?) | TBD | MEDIUM -- real scale confirmed but exhibitor index is a dynamic direct |
| The smarter E India / Intersolar India | Green Energy & Fuels | annual | 2024 (Gandhinagar, Gujarat) | TBD | MEDIUM -- confirms a real India edition exists; exhibitor list is a fi |
| Plastindia | Chemicals & Plastics | ~5-yearly (Plastindia Foundation) | 2023 (?) | TBD | LOW-MEDIUM -- scale confirmed + real regional-agent structure (Messe D |
| Auto Expo — The Components Show | Auto, EV & Components | biennial (ACMA/CII/SIAM) | 2023 (?) | TBD | HIGHEST -- 7 national pavilions (Japan, Korea, Germany, UK, Chinese Ta |
| ACMA Automechanika New Delhi | Auto, EV & Components | annual/biennial (ACMA + Messe Frankfurt) | 2026 (?) | TBD | MEDIUM -- press-release names only (AutoTuner, GMB, Kamoi Kakoshi, Hor |
| Aero India | Aerospace & Defence | biennial | 2019 (?) | TBD | HIGHEST -- complete, country-tagged, real (dated 2019, structural refe |
| DefExpo India | Aerospace & Defence | biennial | 2022 (Gandhinagar) | TBD | LOW by design, not a research gap -- 2020 (Lucknow) edition's 700+-exh |
| India Maritime Week / INMEX SMM India | Shipbuilding & Marine | annual (IMW) / biennial (INMEX) | 2025 (?) | TBD | MEDIUM -- real named participants from press coverage (Maersk, DP Worl |
| AAHAR | Food Processing | annual (ITPO) | 2024 (?) | TBD | HIGHEST -- complete Hall 1 foreign-participation list: Kikkoman India, |
| IMME (International Mining & Machinery Exhibition) | Specialty Steel & Metals | ~4-yearly (CII-run, Kolkata) | 2024 (Kolkata) | TBD | HIGHEST -- full HTML table scraped, real country tags per company; Aus |
| IAA Mobility | Auto, EV & Components | — | 2025 (?) | TBD | HIGH -- live scrapable HTML, country-tagged, paginated (15-60/page); M |
| Automechanika Frankfurt | Auto, EV & Components | — | 2026 (?) | TBD | HIGH -- live, scrapable, COUNTRY-FILTERABLE via URL param (?country=IN |
| CPHI Worldwide (CPHI Milan) | Pharma & Bulk Drugs | — | 2026 (?) | TBD | HIGHEST -- live, scrapable, explicitly country-tagged per exhibitor wi |
| MEDICA | Medical Devices | — | 2026 (?) | TBD | HIGH -- live scrapable (needed a real browser, WebFetch alone returned |
| Arab Health / World Health Expo Dubai | Medical Devices | — | 2026 (?) | TBD | GAP -- confirmed empty in live browser, not a fetch-tool artifact; thi |
| ACHEMA | Chemicals & Plastics | — | 2026 (?) | TBD | HIGH -- live scrapable via browser (JS-blocked to plain fetch), ISO-co |
| K Fair | Chemicals & Plastics | — | 2025 (?) | TBD | HIGH -- live scrapable via browser, city+country per exhibitor; sample |
| Intersolar Europe / The smarter E Europe | Green Energy & Fuels | — | 2026 (?) | TBD | HIGH -- live scrapable via browser, hall/booth + sub-exhibition + coun |
| WindEnergy Hamburg | Green Energy & Fuels | — | 2024 (?) | TBD | GAP, confirmed genuine -- same organiser (Hamburg Messe) as SMM Hambur |
| Farnborough International Airshow | Aerospace & Defence | — | 2024 (?) | TBD | HIGHEST -- server-rendered HTML, plain-fetchable (no browser needed),  |
| GIFA/METEC (Bright World of Metals) | Specialty Steel & Metals | — | 2023 (?) | TBD | HIGH -- live scrapable via browser, city+country per exhibitor incl. A |
| SMM Hamburg | Shipbuilding & Marine | — | 2024 (?) | TBD | GAP, confirmed genuine -- only a product-category taxonomy PDF exists, |
| SEMICON West | Electronics & Semiconductors | — | 2023 (?) | TBD | HIGH -- real archived alphabetical list w/ national pavilions (Korea,  |
| electronica | Electronics & Semiconductors | — | 2026 (?) | TBD | HIGHEST of the global electronics events -- server-rendered HTML table |
| CES | Electronics & Semiconductors | — | 2026 (?) | TBD | MEDIUM, effort-heavy -- technically retrievable, needs a live-browser  |
| MINExpo INTERNATIONAL | Specialty Steel & Metals | — | 2024 (?) | TBD | GAP -- no public exhibitor list currently live |
| bauma | Specialty Steel & Metals | — | 2025 (?) | TBD | GAP for now, but access pattern CONFIRMED VIABLE (same Messe München s |
| OTC (Offshore Technology Conference) | Oil & Gas (not yet a twin focus sector) | — | 2026 (?) | TBD | MEDIUM-HIGH, PARTIALLY harvested -- real static-rendered directory, ~5 |
| ADIPEC | Oil & Gas (not yet a twin focus sector) | — | 2022 (?) | TBD | MEDIUM, LOW-CONFIDENCE source -- ADNOC, bp, Chevron, ExxonMobil, Shell |
| IMARC (International Mining and Resources Conference, Sydney) | Specialty Steel & Metals | — | 2025 (?) | TBD | GAP, LOW-CONFIDENCE -- not a clean pull |
| India Energy Week | Oil & Gas (not yet a twin focus sector) | — | 2024 (Goa) | TBD | MEDIUM potential, LOW accessed -- needs direct Scribd download/login |
| InnoTrans | Railways & Rail Transport (not yet a twin focus sector) | — | 2026 (Berlin) | TBD | HIGHEST of the global railway sources -- FULL EXTRACTION COMPLETE 2026 |
| IREE (International Railway Equipment Exhibition) | Railways & Rail Transport (not yet a twin focus sector) | — | 2025 (Bharat Mandapam, Delhi) | TBD | HIGH -- 250 entries extracted (font-weight-aware PDF parsing), 34 flag |
| RailTrans Expo | Railways & Rail Transport (not yet a twin focus sector) | — | 2026 (Bharat Mandapam, Delhi) | TBD | LOW -- confirmed genuine gap, not under-researched: no exhibitor-list  |
| Light + Building | Construction & Building Materials (not yet a twin focus sector) | — | 2026 (?) | TBD | HIGH -- deep-dived 2026-08-22, full 1884-exhibitor roster pulled via t |
| ISH | Construction & Building Materials (not yet a twin focus sector) | — | 2027 (?) | TBD | HIGH -- deep-dived 2026-08-22, full 2127-exhibitor roster pulled. Top  |
| Heimtextil | Textiles & Apparel | — | 2027 (?) | TBD | HIGH -- deep-dived 2026-08-22, full 1182-exhibitor roster pulled. Indi |
| interpack | Chemicals & Plastics | — | 2026 (?) | TBD | HIGH -- deep-dived 2026-08-22, full 3085-exhibitor roster pulled via t |
| EuroShop | Retail Technology (not yet a twin focus sector) | — | 2026 (?) | TBD | MEDIUM -- deep-dived 2026-08-22, full 2014-exhibitor roster pulled. To |
| wire & Tube Düsseldorf | Specialty Steel & Metals | — | 2026 (?) | TBD | HIGH -- deep-dived 2026-08-22, full 2743-exhibitor combined roster pul |
| drupa | Printing (not yet a twin focus sector) | — | 2028 (?) | TBD | MEDIUM -- deep-dived 2026-08-22, full 1725-exhibitor roster pulled des |
| boot | Marine & Watersports (not yet a twin focus sector) | — | 2027 (?) | TBD | LOW -- deep-dived 2026-08-22, full 1773-exhibitor roster pulled. Top c |
| glasstec | Construction & Building Materials (not yet a twin focus sector) | — | 2026 (?) | TBD | MEDIUM -- deep-dived 2026-08-22, full 1158-exhibitor roster pulled. To |
| A+A | Occupational Safety & PPE (not yet a twin focus sector) | — | 2027 (?) | TBD | MEDIUM -- deep-dived 2026-08-22, full 2514-exhibitor roster pulled. To |
| Caravan Salon | Automotive & Auto Components | — | 2026 (?) | TBD | GAP CONFIRMED, not fabricated -- deep-dived 2026-08-22, full 1008-exhi |
| Ambiente | Consumer Goods & Retail (not yet a twin focus sector) | — | 2027 (?) | TBD | HIGH -- deep-dived 2026-08-22, full 3655-exhibitor roster pulled. Indi |
| Techtextil | Textiles & Apparel | — | 2027 (?) | TBD | MEDIUM -- deep-dived 2026-08-22, full 1474-exhibitor roster pulled. To |
| India International Jewellery Show (IIJS) | Jewellery & Gems (not yet a twin focus sector) | — | 2026 (JWCC + Nesco, Mumbai) | TBD | HIGH -- deep-dived 2026-08-22. GJEPC serves the full 2,163-exhibitor t |
| India Mobile Congress (IMC) | Telecom (distinct from Electronics & Semiconductors) | — | 2025 (Yashobhoomi Convention & Expo Centre, Dwarka, New Delhi) | TBD | GAP CONFIRMED, not fabricated -- deep-dived 2026-08-22. The organizer' |
| ACETECH | Construction & Building Materials (not yet a twin focus sector) | — | 2025 (Bombay Exhibition Centre (NESCO), Mumbai) | TBD | GAP CONFIRMED, not fabricated -- deep-dived 2026-08-22, genuinely no p |
| Convergence India | Telecom (distinct from Electronics & Semiconductors) | — | 2026 (Bharat Mandapam, New Delhi) | TBD | HIGH -- deep-dived 2026-08-22. Unlike most India-domestic B2B shows, t |
| Cement Expo | Construction & Building Materials (not yet a twin focus sector) | — | 2023 (Manekshaw Centre, New Delhi) | TBD | MEDIUM, PARTIAL -- deep-dived 2026-08-22. No live exhibitor-directory  |
| India International Trade Fair (IITF) | Cross-sector (general trade fair, not sector-specific) | — | 2025 (Bharat Mandapam, New Delhi) | TBD | HIGH, two-layer finding -- deep-dived 2026-08-22. COUNTRY-level (prima |
| Messe Frankfurt -- unified cross-show India pull | Cross-sector platform note | — | 2026 (?) | TBD | 🔑 PLATFORM-LEVEL FINDING, not a single event: omitting the event filte |
| Messe Düsseldorf -- shared DIMEDIS 'vis' platform note | Cross-sector platform note | — | 2026 (?) | TBD | 🔑 PLATFORM-LEVEL FINDING: the same '<domain>/vis-api/vis/v1/en/directo |

## Coverage note

Extended 2026-08-22 across all twin focus sectors: Electronics & Semiconductors, White Goods & Electricals, Auto/EV & Components, Pharma & Bulk Drugs, Medical Devices, Green Energy & Fuels, Chemicals & Plastics, Aerospace & Defence, Specialty Steel & Metals, Shipbuilding & Marine, Food Processing -- plus Mining and Oil & Gas (not yet formal twin focus sectors, added per explicit request). 33 associations, 64 events tracked. Highest-value pattern confirmed repeatedly: an India-domestic trade fair's exhibitor list is a stronger signal than bare association membership (revealed preference -- paid to physically exhibit in India) -- India ITME, SEMICON India, ELECRAMA, Medical Fair India, ChemTECH World Expo, Auto Expo Components, Aero India, AAHAR, and IMME all produced real country-tagged rosters this pass.

