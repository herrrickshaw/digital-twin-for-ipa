# Visibility map — who the government announces, and who invests quietly

*Generated 2026-07-21 by `scripts/build_visibility_report.py` from `layers/19_pib_visibility.json` + `layers/20_visibility_verified.json` — do not hand-edit.*

## What this is

Every company in the leads layer, matched against **122216 PIB releases, 46170 in window** over the window **2023-07-21 .. 2026-07-21 (3 years)**, then — for those the government never headlined — checked against trade press for what they are actually doing in India.

**Read the method before the numbers.** The PIB register stores release *titles*, not bodies. A company named inside a release but not in its headline reads as absent here. So this measures **headline attention**, and it understates total government contact — two names in this report (Cameco, Ma'aden) were proven publicised once the news check ran, and their corrections are shown rather than quietly patched. The asymmetry is still the point: PIB headlines name firms when the government wants credit for the investment.

## The split

| Bucket | Count | Meaning |
|---|---|---|
| BELOW_RADAR | 203 | never named in a PIB headline |
| ANNOUNCED | 46 | named in an investment-related PIB headline |
| MENTIONED_ONLY | 36 | named only incidentally (condolences, unrelated merger clearances) |
| HISTORIC | 24 | named only before the window |
| UNMATCHABLE | 12 | name too generic to match safely (reason recorded per company) |

Of the 127 companies with HIGH or MEDIUM India intent in their own annual reports, **11 appear in an investment-related PIB headline** and **80 never do**.

## Who the government does headline

| PIB investment headlines (3y) | Company | Country | Most recent release |
|---|---|---|---|
| 5 | Safran SA | France | [2025-12-22](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2207389) IOL signs collaboration agreement with SAFRAN to manufacture two high-precisio |
| 4 | Hon Hai Precision Industry (Foxcon | Taiwan | [2026-02-21](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2231345) Prime Minister Shri Narendra Modi participates in the groundbreaking ceremony  |
| 2 | Suzuki Motor Corporation | Japan | [2025-06-17](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2136909) Union Railway Minister Inaugurates India’s Largest Automobile Gati Shakti Mult |
| 1 | Nippon Steel Corporation | Japan | [2026-05-30](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2266939) ArcelorMittal Nippon Steel India Secures First-Ever Strategic Investment Plan  |
| 1 | Hanwha Aerospace Co., Ltd. | South Korea | [2025-11-15](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190325) Minister Hardeep Singh Puri visits Hanwha Ocean’s shipbuilding facility in Sou |
| 1 | Siemens Energy AG | Germany | [2025-06-23](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2138973) Siemens & Alstom, Both the firms Capable to Manufacture 9000 Horse Power Locom |
| 1 | Schneider Electric S.E. | France | [2025-12-09](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2201090) CCI approves the proposed acquisition of certain stake in Schneider Electric I |
| 1 | Kongsberg Gruppen | Norway | [2025-06-03](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2133528) India to Build First-Ever Polar Research Vessel (PRV) as GRSE Signs MoU with N |
| 1 | BHP Group Limited | Australia | [2024-10-07](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2062763) BHP and SAIL sign MOU to accelerate potential pathways to steel decarbonisatio |
| 1 | ASML Holding N.V. | Netherlands | [2026-05-16](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2261878) Prime Minister witnesses signing of agreement between ASML and Tata Electronic |
| 1 | Wistron Corporation | Taiwan | [2024-01-24](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1999115) CCI approves 100% acquisition of Wistron Infocomm Manufacturing (India) Privat |

The pattern is narrow: semiconductors, defence, and marquee PM-attended ribbon-cuttings.

## Verified against the trade press

The 27 below-radar names with the strongest stated intent were checked against dated news. Absence from PIB headlines turns out to have four different causes — only one of them is an opportunity.

### Quiet investors — the outreach list (12)

Dated, sourced India activity in the last three years and **no government publicity found at all**: not a PIB headline, not a minister at the ribbon-cutting, not a state-government announcement. These are companies committing capital to India that the government is not currently courting.

**Lenovo Group** (Hong Kong, Electronics & Semiconductors)
- 2024-09-17: [Lenovo begins AI server production in India, opens R&D lab in Bengaluru](https://www.business-standard.com/companies/news/lenovo-begins-ai-server-production-in-india-opens-r-d-lab-in-bengaluru-124091700983_1.html) — 50,000 enterprise AI servers and 2,400 high-end GPU units annually; 4th global R&D centre
- 2024-09-19: [Lenovo turns to India as source of AI servers](https://www.theregister.com/2024/09/19/lenovo_india_ai_server_manufacturing/) — >60% of production for export
- 2025-03-07: [Lenovo to manufacture all PC models in India, plans AI server plant in Pondicherry](https://www.digitimes.com/news/a20250307VL204/lenovo-pc-ai-server-development-manufacturing.html) — 12 million units (2024); ~40% capacity increase planned for 2025
- *Genuine, substantial expansion — AI-server manufacturing in Puducherry plus a fourth global R&D lab in Bengaluru, export-oriented.*

**CAE Inc** (Canada, Aerospace & Defence)
- 2026-04-15: [CAE and InterGlobe inaugurate new pilot training centre in Mumbai to support India's aviation growth](https://www.prnewswire.com/in/news-releases/cae-and-interglobe-inaugurate-new-pilot-training-centre-in-mumbai-to-support-indias-aviation-growth-302743367.html) — 44,000 sq ft; scalable to 6 FFS; network 16 FFS today rising to 23; India needs ~22,000 new pilots by 2034
- 2026-04: [CAE expand in India with new pilot-training site](https://www.flightglobal.com/archive/2026/04/cae-expand-in-india-with-new-pilot-training-site/) — not stated
- 2025-08-26: [New pilot training centre to open in Mumbai](https://avitrader.com/2025/08/26/new-pilot-training-centre-to-open-in-mumbai/) — not stated
- *A clean example of the target pattern — steady physical capex (5 simulators added since FY2024, fourth centre opened 2026) reported only in aviation trade press, zero government amplification.*

**WEG S.A.** (Brazil, White Goods & Electricals)
- 2025-12: [WEG Expands Operations in India with Planned Acquisition of Sanelec](https://themachinemaker.com/news/weg-expands-operations-in-india-with-planned-acquisition-of-sanelec/) — USD 5.2 million; Sanelec 2024 net operating revenue ~USD 2.3m/month, EBITDA margin 29%
- 2025-12: [TT&A advises WEG on acquisition of Sanelec](https://www.barandbench.com/dealstreet/tta-advises-weg-on-acquisition-of-sanelec) — two-tranche deferred consideration, 18-month FEMA window
- 2025-05: [WEG Delivers Breakthrough IE4 Motors Project in India's F&B Sector](https://www.electricmachinery.com/institutional/US/en/news/products-and-solutions/weg-delivers-breakthrough-ie4-motors-project-in-india-s-f-b-sector) — dispatched 2025-04-22; WEG runs 4 production plants in India
- *Textbook quiet investor — four Indian plants, active Hosur manufacturing output, and a Dec-2025 bolt-on acquisition in Bengaluru, all covered only by niche trade and legal press.*

**Elbit Systems** (Israel, Aerospace & Defence)
- 2025-05-18: [Adani Defence & Aerospace and Sparton Enter Strategic Partnership to Indigenise Anti-Submarine Warfare Solutio](https://www.adani.com/newsroom/media-releases/adani-defence-aerospace-and-sparton-enter-strategic-partnership-to-indigenise-anti-submarine) — not stated
- 2025-05-18: [Adani Defence partners with US firm Sparton to build India's first indigenised sonobuoy systems for Navy](https://www.businesstoday.in/india/story/adani-defence-partners-with-us-firm-sparton-to-build-indias-first-indigenised-sonobuoy-systems-for-navy-476724-2025-05-18) — not stated
- 2025-05-18: [Adani partners with Sparton to develop anti-submarine warfare system](https://www.business-standard.com/companies/news/adani-group-sparton-sonobuoy-manufacturing-india-125051800478_1.html) — not stated
- *Active in-window via its Sparton subsidiary — a binding May-2025 India localisation agreement covered by Indian business press only, with the Elbit link often understated (outlets described Sparton as a 'US firm').*

**Panasonic Holdings** (Japan, Electronics & Semiconductors)
- 2025-09-19: [Panasonic India eyeing white goods PLI, new plant to tap market potential](https://www.business-standard.com/companies/news/panasonic-life-solutions-manufacturing-unit-pli-scheme-white-goods-125091900308_1.html) — PLI white-goods application; new unit unquantified
- 2025: [Panasonic Life Solutions to invest Rs 300 crore in Sri City's Manufacturing Plant](https://b2bpurchase.com/panasonic-life-solutions-to-invest-%E2%82%B9300-crore-in-sri-citys-manufacturing-plant/) — Rs 300 crore (phase 1 of Rs 600 crore); JPY 100bn global programme
- *Actively expanding India manufacturing (Sri City phase-1 Rs 300cr, new PLI-linked plant planned) with only trade-press coverage.*

**Eisai** (Japan, Pharma & Bulk Drugs)
- 2025-07: [Eisai Pharma announces its plans to set up GCC in Vizag](https://www.thehansindia.com/andhra-pradesh/eisai-pharma-announces-its-plans-to-set-up-gcc-in-vizag-986846) — Capex not disclosed; operational target Feb 2026
- 2025-07: [Japan's Leading Pharma Company Eisai to Set Up GCC in Visakhapatnam](https://www.yovizag.com/japans-leading-pharma-company-eisai-to-set-up-gcc-in-visakhapatnam/) — 50-acre existing site; GCC capex undisclosed
- *Quietly adding an AI/data R&D capability centre in Visakhapatnam on top of a long-standing API and formulation site.*

**Mitsui O.S.K. Lines** (Japan, Shipbuilding & Marine)
- 2025-12-16: [Mitsui O.S.K. Lines CVC (MOL PLUS) to Invest in India's Theia Ventures Fund 1](https://cyprusshippingnews.com/2025/12/16/mitsui-o-s-k-lines-cvc-mol-plus-to-invest-in-indias-theia-ventures-fund-1/) — Fund commitment size not disclosed; India desk established Nov 2024
- 2024-11: [Shipping giant Mitsui O.S.K. Lines opens India CVC office](https://globalventuring.com/corporate/asia/shipping-giant-mitsui-o-s-k-lines-opens-india-cvc-office/) — Third overseas CVC office; no capital figure disclosed
- *Building an India venture-capital beachhead (India desk 2024, first fund commitment Dec 2025) rather than physical shipping assets.*

**Siam Cement Group (SCG)** (Thailand, Chemicals & Plastics)
- 2024-06-10: [SIAM Cement BigBloc Construction Launches India Operations; Joint Venture inaugurates commercial production of](https://www.business-standard.com/content/press-releases-ani/siam-cement-bigbloc-construction-launches-india-operations-joint-venture-inaugurates-commercial-production-of-india-s-first-aac-wall-plant-at-kheda-124061000859_1.html) — Rs 65 crore invested; 2.5 lakh cubic metre p.a. capacity, expandable to 5 lakh CBM in phase 2
- 2024-06: [SCG International and BigBloc Start JV Operations for First Plant of AAC Wall in India](https://scginternational.com/joint-venture-operations-india/) — 52:48 JV split (BigBloc:SCG International)
- *SCG's first-ever India investment — a Rs 65 crore Gujarat AAC-panel JV — landed entirely through trade press.*

**MediaTek** (Taiwan, Electronics & Semiconductors)
- 2026-05-09: [MediaTek leases 104,000 sq ft at BPTP Capital City in Noida for second India R&D hub](https://propnewstime.com/getdetailsStories/MzAwNTg=/mediatek-leases-104-000-sq-ft-at-bptp-capital-city-in-noida-for-second-india-r-d-hub) — 104,000 sq ft over three floors; part of a 780,000 sq ft development
- 2025-10-10: [MediaTek Eyes Chip Manufacturing In India, Sees $4.1 Billion R&D To Boost 5G and AI Innovation](https://www.etvbharat.com/en/!technology/mediatek-eyes-chip-manufacturing-in-india-sees-41-billion-r-d-to-boost-5g-and-ai-innovation-enn25101005874) — USD 4.1 billion global R&D spend cited; 1,000+ India engineers
- *Doubling India R&D via a second Noida centre; chip-manufacturing talk remains stated intent, not committed capex.*

**CLP Holdings** (Hong Kong, Green Energy & Fuels)
- 2025: [Apraava commissions Fatehgarh IV transmission project in Rajasthan](https://powerpeakdigest.com/apraava-commissions-fatehgarh-iv-transmission-project-in-rajasthan/) — 2.5 GW transmission capacity; five 500 MVA transformers; 22 km line
- 2024: [Apraava Bags Project to Evacuate 5.5 GW Renewable Energy in Rajasthan](https://www.mercomindia.com/apraava-bags-project-to-evacuate-renewable-energy-in-rajasthan) — 5.5 GW evacuation capacity
- *Roughly Rs 18,000 crore deployed in India via Apraava (~2 GW generation, transmission and 2.5m smart meters), invisible under a rebranded local name.*

**Food Empire Holdings** (Singapore, Food Processing)
- 2025-07-10: [Food Empire to expand coffee manufacturing facility in India](https://www.just-drinks.com/news/food-empire-india-facility-expansion/) — USD 37 million; ~60% capacity increase
- 2025: [Food Empire to expand spray-dried soluble coffee manufacturing facility in India](https://www.comunicaffe.com/food-empire-to-expand-manufacturing-facility-in-india/) — USD 37 million
- *USD 37m Andhra Pradesh soluble-coffee capacity expansion, covered only by drinks trade press.*

**Arcelik** (Turkey, White Goods & Electricals)
- 2025-06-15: [JV Voltbek's FY25 revenue rises 39.5% to Rs 2,235.53 cr, volume grows 57%](https://www.business-standard.com/amp/companies/news/jv-voltbek-s-fy25-revenue-rises-39-5-to-2-235-53-cr-volume-grows-57-125061500286_1.html) — FY25 revenue Rs 2,235.53 crore (+39.5%); volume +57%; Voltas invested Rs 102.41 crore in Voltbek share capital in FY25; Sanand capacity being expanded ~50%
- *Quietly compounding — the Sanand JV is scaling hard (revenue +39.5%, capacity +50%, fresh equity from the Indian partner) but Arcelik's name surfaces only inside Voltas results coverage, never in its own right.*

### Publicised by a state, invisible at the centre (2)

Real activity that a **state government amplified** — land allotted and announced, a Chief Minister at the ground-breaking — while no PIB headline ever named the firm. This is a centre-versus-state visibility gap, not stealth, and it says something about which door these investors came through.

**LG Electronics** (South Korea, Electronics & Semiconductors)
- 2025-05-08: [LG Electronics India Limited Begins Construction of Its Third Manufacturing Plant in India](https://www.lgnewsroom.com/2025/05/lg-electronics-india-limited-begins-construction-of-its-third-manufacturing-plant-in-india/) — USD 600 million / Rs 5,001 crore over four years; capacity 800k refrigerators, 850k washing machines, 1.5m ACs, 2m compressors p.a.
- 2025-05: [LG Electronics Commences Construction of New Manufacturing Facility at Sri City](https://sricity.in/en/news_events/lg-electronics-commences-construction-of-new-manufacturing-facility-at-sri-city/) — 247 acres
- *Largest confirmed investment in this cluster — a USD 600m third India plant at Sri City, state-publicised but PIB-invisible.*

**Delta Electronics Thailand** (Thailand, Electronics & Semiconductors)
- 2025-09-12: [Delta Electronics India Begins Krishnagiri Plant Expansion](https://www.energetica-india.net/news/delta-electronics-india-begins-krishnagiri-plant-expansion) — 95-acre campus; up to 95% productivity increase claimed; 6.9 MWp solar rooftop
- 2025: [Delta Expanding India Operations With $500 Mn Investment](https://inc42.com/buzz/delta-expanding-india-operations-with-500-mn-investment/) — USD 500 million; workforce 3,750 to 5,000; 65% deployed
- *USD 500m Tamil Nadu expansion with the CM at the ground-breaking, yet never named in a central government release.*

### Already courted — corrections to the PIB match (2)

The PIB title match filed these as below-radar and the news check proved it wrong. Recorded here with the evidence, because the register indexes release *titles* only and these cases are exactly where that limit bites.

**Ma'aden / Saudi Arabian Mining Company** (Saudi Arabia)
- **Correction**: minister-fronted (signed during J.P. Nadda's Saudi visit, carried by DD News, the state broadcaster); also offtake, not Indian capex
- 2025-07: [Three Indian Fertilizer Companies Sign Long-Term DAP Supply Agreement with Saudi Arabia's Ma'aden](https://krishijagran.com/news/three-indian-fertilizer-companies-sign-long-term-dap-supply-agreement-with-saudi-arabia-s-ma-aden) — 3.1 million tonnes/yr DAP (up from 1.9 Mt in 2024-25); 5+5 year term
- 2025-04-10: [Coromandel International, Saudi Arabia's Ma'aden sign long-term DAP deal](https://www.business-standard.com/companies/news/coromandel-international-saudi-arabia-s-ma-aden-sign-long-term-dap-deal-125041000136_1.html) — not stated
- 2025-07-15: [India signs multiple phosphate agreements](https://www.worldfertilizer.com/phosphates/15072025/india-signs-multiple-phosphate-agreements/) — 3.1 Mt/yr
- *Large and strategically important, but NOT unpublicised — a minister-fronted, state-broadcaster-covered supply arrangement; also offtake, not Indian capex.*

**Cameco** (Canada, Green Energy & Fuels)
- **Correction**: PIB title match missed it: the CAD 2.6bn / 22M-lb uranium contract with the Dept of Atomic Energy was signed at a Delhi event attended by the PM and the Canadian PM -- publicised, just not in a PIB headline
- 2026-03-02: [Cameco Signs Long-Term Uranium Supply Agreement with India](https://www.cameco.com/media/news/cameco-signs-long-term-uranium-supply-agreement-with-india) — ~22 million lb U3O8; ~CAD 2.6 billion
- 2026-03-06: [Cameco uranium agreement a highlight of Canada-India deals](https://www.ans.org/news/2026-03-06/article-7823/cameco-uranium-agreement-a-highlight-of-canadaindia-deals/) — CAD 2.6 billion
- *NOT below-radar in substance — a USD-scale sovereign supply contract signed in front of two prime ministers; treat any 'unpublicised' classification as a PIB-headline-text artefact.*

### Press Note 3 cohort — absence has a different cause (6)

Chinese-domiciled names. Their absence from Indian government headlines is not modesty: their India activity is refusal, exclusion, or Indianisation of ownership. **None of this is inbound investment** and none of it is an outreach opportunity.

**SAIC Motor** (China, Auto, EV & Components)
- 2024: [CCI approves JSW's acquisition of up to 38% stake in MG Motor India](https://www.autocarpro.in/news/cci-approves-jsws-acquisition-of-up-to-38-stake-in-mg-motor-india-118841) — ~35-38% stake; ~USD 300 million; JV valued ~USD 1.2 billion
- 2025: [SAIC to reduce stake in JSW MG Motor JV amid investment curbs](https://www.autocarindia.com/industry/saic-to-reduce-stake-in-jsw-mg-motor-jv-amid-investment-curbs-437309) — Additional 10%; JSW 35%->45%, SAIC 49%->39%
- 2025: [JSW set to gain control of MG Motor JV as SAIC plans 10 percent stake sale](https://www.autocarindia.com/industry/jsw-to-gain-control-as-saic-plans-10-percent-stake-sale-in-jv-439840) — MG India sales 16,500 (2019) -> 61,000+ (2024)
- *NOT inbound investment — a staged retreat from majority ownership of MG India to JSW, forced by Press Note 3 and a rejected EV plant proposal, even as the brand thrives commercially.*

**BYD** (China, Auto, EV & Components)
- 2023-07: [BYD's US$1 billion investment plan reportedly rejected by India on security grounds in blow to global strategy](https://www.scmp.com/business/china-business/article/3228769/byds-go-global-strategy-dealt-setback-after-india-investment-plan-rejected-security-grounds-report) — USD 1 billion proposal rejected
- 2025-04-07: [India says no to BYD while wooing rival Tesla to invest](https://www.bloomberg.com/news/articles/2025-04-07/india-says-no-to-byd-while-wooing-rival-tesla-to-invest) — n/a
- *NOT an investment — a USD 1bn manufacturing proposal refused under Press Note 3, with the refusal reaffirmed through 2025.*

**Luxshare Precision** (China, Electronics & Semiconductors)
- 2024-08-23: [India reportedly allows Luxshare's investment in Tamil Nadu](https://www.digitimes.com/news/a20240823VL202/investment-luxshare-government-manufacturing-electronics.html) — Original plan Rs 7.5 billion (~USD 90m); clearance terms not detailed
- 2024: [Luxshare Precision (company profile — India/Vietnam capital reallocation)](https://grokipedia.com/page/Luxshare) — USD 330m diverted to Vietnam (2023); USD 504m Vietnam total by 2024
- *Press Note 3 friction pushed capital to Vietnam; a 2024 India clearance was reported but no confirmed India plant materialised in the window.*

**Hikvision** (China)
- 2025-05-28: ['China part of concern': India's CCTV crackdown over spying fears hits global giants like Hikvision, Xiaomi](https://www.businesstoday.in/industry/story/china-part-of-concern-indias-cctv-crackdown-over-spying-fears-hits-global-giants-like-hikvision-xiaomi-478143-2025-05-28) — 342 applications pending; 1 foreign-brand approval
- 2026-03-30: [India to ban Chinese CCTV from Apr 1 as security concerns reshape market](https://www.business-standard.com/industry/news/india-ban-chinese-cctv-government-security-concerns-hikvision-dahua-market-126033000316_1.html) — Indian brands >80% market share (Feb 2026), up from ~67%
- *NOT an investment — progressive regulatory exclusion from the India market, culminating in an effective sales ban from April 2026.*

**Haier Smart Home** (China, White Goods & Electricals)
- 2025-12-24: [Bharti Enterprises and Warburg Pincus Announce Strategic Investment in Haier India](https://warburgpincus.com/2025/12/24/bharti-enterprises-and-warburg-pincus-announce-strategic-investment-in-haier-india/) — 49% stake; deal valued around USD 2 billion
- 2025-12-24: [Haier Sells 49% Stake in Indian Unit to Bharti, Warburg Pincus](https://www.bloomberg.com/news/articles/2025-12-24/haier-sells-49-stake-in-indian-unit-to-bharti-warburg-pincus) — ~USD 2 billion valuation
- *NOT inbound investment — a 49% dilution to Bharti/Warburg Pincus (~USD 2bn) engineered to work around Press Note 3.*

**Midea Group** (China, White Goods & Electricals)
- 2025: [This Chinese home appliances giant might start manufacturing in India](https://www.newsbytesapp.com/news/business/midea-to-soon-announce-local-manufacturing-joint-venture-in-india/story) — No capex figure disclosed; JV unannounced as of reporting
- *No confirmed India investment in the window — only a stated intent to form a local manufacturing JV, itself a Press Note 3 workaround pattern.*

### Flow runs the other way (1)

The traceable activity is India reaching for the company's assets abroad, not the company investing in India. Worth tracking, wrong list for investment promotion.

**SQM / Sociedad Quimica y Minera** (Chile)
- 2025-03-28: [Exclusive-Indian state firms seek stake in SQM's lithium projects in Australia, sources say](https://www.miningweekly.com/article/indian-state-firms-seek-stake-in-sqms-lithium-projects-in-australia-sources-say-2025-03-28) — 20% stake for ~USD 600 million; full asset base valued ~USD 3 billion
- 2025-03-28: [Coal India, ONGC Videsh among firms seeking stake in SQM's lithium projects](https://www.business-standard.com/companies/news/coal-india-ongc-videsh-among-firms-seeking-stake-in-sqm-s-lithium-projects-125032800475_1.html) — USD 600 million for 20%
- *Genuinely below-radar but the traceable activity is inbound-to-SQM (Indian PSUs buying into its Australian lithium), and its own Pune subsidiary has zero press coverage — a real quiet-entry signal that trade press has not yet picked up.*

### Intent stated, not yet converted (4)

The annual report expresses India or APAC interest, but no dated India activity surfaced inside the three-year window — or the only commitment predates it. Intent has not become capex.

**Embraer** (Brazil, Aerospace & Defence)
- 2024-02-01: [Embraer and Mahindra announce collaboration on the C-390 Millennium Medium Transport Aircraft in India](https://www.embraer.com/media-center/en/?mediatype=NEWS&detail=13870) — IAF MTA requirement reported at up to 80 aircraft
- 2026-06: [Embraer to offer India its own C-390 assembly line as part of bid for new military transport](https://www.flightglobal.com/archive/2026/06/embraer-prepared-to-open-indian-c-390-assembly-site-to-support-sale/) — fleet recapitalisation up to 80 transport aircraft
- 2026-02-20: [Embraer, Mahindra plan C-390 MRO facility for India air force bid](https://www.flightglobal.com/fixed-wing/embraer-mahindra-plan-india-mro-for-c-390-bid/166387.article) — not stated
- *Sustained, escalating India campaign (Feb-2024 MoU to Oct-2025 cooperation agreement to Feb-2026 MRO siting) but strictly a competition bid — no signed aircraft order, so 'investment intent' is conditional, not committed.*

**Thungela Resources** (South Africa, Green Energy & Fuels)
- 2024-02-13: [Thungela establishes export marketing function in Dubai](https://www.worldcoal.com/coal/13022024/thungela-establishes-export-marketing-function-in-dubai/) — not stated
- *NO INDIA ACTIVITY FOUND IN WINDOW — India appears only as a demand-side export destination in results commentary (and 2024-25 commentary describes Indian demand as BELOW expectations); the marketing entity went to Dubai, not India.*

**Orica** (Australia, Chemicals & Plastics)
- *NO INDIA ACTIVITY FOUND IN WINDOW — Orica's Indian Explosives Pvt Ltd (Gomia, Jharkhand) is a long-standing wholly-owned subsidiary with revenue of Rs 467 crore in FY2023, but every located expansion reference (Gomia capacity upgrade, Nagpur site feasibility) *

**Ansell** (Australia, Medical Devices)
- *NO DATED IN-WINDOW NEWS ITEM FOUND — Ansell's material India commitment (the ~USD 80m Kovai greenfield plant in Tamil Nadu, with a further USD 40m phase taking it to USD 120m) was announced Dec-2022/Mar-2023, before the window; post-July-2023 coverage is only *

## How to use this

The **quiet investors** are the actionable list: they are spending money in India now, and no arm of government is visibly engaging them. The **state-publicised** names show which states are winning investors the centre has not claimed. The **Press Note 3** names should not be worked as leads at all. The **no-activity** names are the watch list — stated intent that has not become capex, worth re-checking next cycle.

Companion views: `docs/TARGET_LEADS.md` (scored targets), `docs/LEADS.md` (full layer), `docs/reportage_ministry.html` (what the government announced, by ministry).
