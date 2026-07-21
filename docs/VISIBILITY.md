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

The 41 below-radar names with the strongest stated intent were checked against dated news. Absence from PIB headlines turns out to have four different causes — only one of them is an opportunity.

### Quiet investors — the outreach list (10)

Dated, sourced India activity in the last three years and **no government publicity found at all**: not a PIB headline, not a minister at the ribbon-cutting, not a state-government announcement. These are companies committing capital to India that the government is not currently courting.

**Andritz** (Austria, Green Energy & Fuels)
- 2026-04-14: [Advancing renewable energy: ANDRITZ to equip India's largest pumped storage plant](https://www.andritz.com/newsroom-en/hydro/2026-04-14-saidongar-group) — Low three-digit million EUR range
- 2026-03-17: [ANDRITZ secures major order from Tata Power for 1,000 MW Bhivpuri Pumped Storage Project in India](https://www.andritz.com/newsroom-en/hydro/2026-03-17-tata-power-group) — Low three-digit million EUR range
- 2022-09: [ANDRITZ to supply equipment for Gandhi Sagar pumped storage project in India](https://www.renewableenergyworld.com/energy-storage/pumped-storage/andritz-to-supply-equipment-for-gandhi-sagar-pumped-storage-project-in-india/) — 1,440 MW, expandable to 1,680 MW
- *Strongly active and genuinely unpublicised — two separate low-three-digit-EUR-million pumped-storage orders in six weeks (Tata Power Bhivpuri, Torrent Saidongar-1) plus a seven-project India pipeline, all announced only through Andritz's own hydro newsroom and*

**Schaeffler AG** (Germany, Auto, EV & Components)
- 2025-05-28: [Schaeffler India Opens Fifth Manufacturing Plant in Tamil Nadu to Boost Powertrain Production](https://www.autocarpro.in/news/schaeffler-india-opens-fifth-manufacturing-plant-in-tamil-nadu-to-boost-powertrain-production-126648) — INR 1,700 crore invested 2022-2024, against an original INR 1,500 crore commitment
- 2026-05-27: [How Schaeffler India is pumping in EUR 500 million over the next five years to boost capacity and increase loc](https://www.businesstoday.in/magazine/deep-dive/story/how-schaeffler-india-is-pumping-in-eu500-million-over-the-next-five-years-to-boost-capacity-and-increase-localisation-533647-2026-05-27) — EUR 500 million over five years
- 2026-02: [Schaeffler India to Raise Capex Above INR 5 Billion in 2026 as Plant Utilisation Crosses 85 Percent](https://machinist.in/2026/02/schaeffler-india-to-raise-capex-above-inr-5-billion-in-2026-as-plant-utilisation-crosses-85-percent/) — INR 5 billion+ 2026 capex; INR 4,500 crore by 2030
- *One of the clearest below-radar heavyweights — a fifth Indian plant opened May 2025 with no official present, INR 1,700 crore already spent 2022-24, and a EUR 500m / INR 4,500 crore forward programme visible only through trade press and stock-exchange filings.*

**Ericsson** (Sweden)
- 2025-06-26: [Ericsson strengthens R&D in India - to commence ASIC development in Bengaluru](https://www.ericsson.com/en/press-releases/2/2025/6/ericsson-strengthens-rd-in-india--to-commence-asic-development-in-bengaluru) — 150+ new positions (no India capex figure; Ericsson spends ~USD 5 billion/year on R&D globally)
- 2025-04-22: [Ericsson to expand local antenna manufacturing in India](https://developingtelecoms.com/telecom-business/vendor-news/18373-ericsson-to-expand-local-antenna-manufacturing-in-india.html) — 100% localisation of passive antennas by June 2025
- 2025-06-03: [Ericsson expands capabilities in India](https://www.rcrwireless.com/20250603/5g/ericsson-india) — ~2,000 R&D engineers
- *Consistently active and quiet — ASIC/semiconductor design added in Bengaluru with 150+ roles (Jun 2025), full passive-antenna localisation via VVDN and a Pune logistics hub (Apr 2025), all announced only through Ericsson's newsroom and telecom trade press.*

**CAE Inc** (Canada, Aerospace & Defence)
- 2026-04-15: [CAE and InterGlobe inaugurate new pilot training centre in Mumbai to support India's aviation growth](https://www.prnewswire.com/in/news-releases/cae-and-interglobe-inaugurate-new-pilot-training-centre-in-mumbai-to-support-indias-aviation-growth-302743367.html) — 44,000 sq ft; scalable to 6 FFS; network 16 FFS today rising to 23; India needs ~22,000 new pilots by 2034
- 2026-04: [CAE expand in India with new pilot-training site](https://www.flightglobal.com/archive/2026/04/cae-expand-in-india-with-new-pilot-training-site/) — not stated
- 2025-08-26: [New pilot training centre to open in Mumbai](https://avitrader.com/2025/08/26/new-pilot-training-centre-to-open-in-mumbai/) — not stated
- *A clean example of the target pattern — steady physical capex (5 simulators added since FY2024, fourth centre opened 2026) reported only in aviation trade press, zero government amplification.*

**Elbit Systems** (Israel, Aerospace & Defence)
- 2025-05-18: [Adani Defence & Aerospace and Sparton Enter Strategic Partnership to Indigenise Anti-Submarine Warfare Solutio](https://www.adani.com/newsroom/media-releases/adani-defence-aerospace-and-sparton-enter-strategic-partnership-to-indigenise-anti-submarine) — not stated
- 2025-05-18: [Adani Defence partners with US firm Sparton to build India's first indigenised sonobuoy systems for Navy](https://www.businesstoday.in/india/story/adani-defence-partners-with-us-firm-sparton-to-build-indias-first-indigenised-sonobuoy-systems-for-navy-476724-2025-05-18) — not stated
- 2025-05-18: [Adani partners with Sparton to develop anti-submarine warfare system](https://www.business-standard.com/companies/news/adani-group-sparton-sonobuoy-manufacturing-india-125051800478_1.html) — not stated
- *Active in-window via its Sparton subsidiary — a binding May-2025 India localisation agreement covered by Indian business press only, with the Elbit link often understated (outlets described Sparton as a 'US firm').*

**Croda International** (United Kingdom, Chemicals & Plastics)
- 2026-03-19: [Croda opens new manufacturing facility in Dahej, India to support growth and sustainable innovation](https://www.croda.com/en-gb/media-hub/news/general/croda-opens-new-manufacturing-facility-in-dahej) — Not disclosed in the opening release
- 2023-03-30: [Croda India to invest Rs. 500 crore in Dahej greenfield facility](https://www.indianchemicalnews.com/chemical/croda-india-to-invest-rs-500-crore-in-dahej-greenfield-facility-16925) — INR 500 crore (first phase). Note: one secondary source cites USD 5.4m for an earlier/narrower scope — figures conflict, prefer the INR 500 crore first-phase number.
- *Genuinely active and unpublicised — a INR 500 crore greenfield surfactants plant at Dahej commissioned March 2026, evidenced by trade press, the company's own release and its P&L, with no Indian government presence found.*

**Siam Cement Group (SCG)** (Thailand, Chemicals & Plastics)
- 2024-06-10: [SIAM Cement BigBloc Construction Launches India Operations; Joint Venture inaugurates commercial production of](https://www.business-standard.com/content/press-releases-ani/siam-cement-bigbloc-construction-launches-india-operations-joint-venture-inaugurates-commercial-production-of-india-s-first-aac-wall-plant-at-kheda-124061000859_1.html) — Rs 65 crore invested; 2.5 lakh cubic metre p.a. capacity, expandable to 5 lakh CBM in phase 2
- 2024-06: [SCG International and BigBloc Start JV Operations for First Plant of AAC Wall in India](https://scginternational.com/joint-venture-operations-india/) — 52:48 JV split (BigBloc:SCG International)
- *SCG's first-ever India investment — a Rs 65 crore Gujarat AAC-panel JV — landed entirely through trade press.*

**MediaTek** (Taiwan, Electronics & Semiconductors)
- 2026-05-09: [MediaTek leases 104,000 sq ft at BPTP Capital City in Noida for second India R&D hub](https://propnewstime.com/getdetailsStories/MzAwNTg=/mediatek-leases-104-000-sq-ft-at-bptp-capital-city-in-noida-for-second-india-r-d-hub) — 104,000 sq ft over three floors; part of a 780,000 sq ft development
- 2025-10-10: [MediaTek Eyes Chip Manufacturing In India, Sees $4.1 Billion R&D To Boost 5G and AI Innovation](https://www.etvbharat.com/en/!technology/mediatek-eyes-chip-manufacturing-in-india-sees-41-billion-r-d-to-boost-5g-and-ai-innovation-enn25101005874) — USD 4.1 billion global R&D spend cited; 1,000+ India engineers
- *Doubling India R&D via a second Noida centre; chip-manufacturing talk remains stated intent, not committed capex.*

**Leonardo** (Italy, Aerospace & Defence)
- 2026-02-03: [Adani Defence & Aerospace and Leonardo Forge Strategic Partnership to Build India's Helicopter Ecosystem](https://www.leonardo.com/en/press-release-detail/-/detail/03-02-2026-adani-defence-aerospace-and-leonardo-forge-strategic-partnership-to-build-india-s-helicopter-ecosystem) — No value disclosed
- *Genuinely below-radar and strategically significant — a Feb 2026 helicopter-manufacturing MoU with Adani that re-enters a market Leonardo was effectively locked out of, announced entirely through corporate and trade channels.*

**Arcelik** (Turkey, White Goods & Electricals)
- 2025-06-15: [JV Voltbek's FY25 revenue rises 39.5% to Rs 2,235.53 cr, volume grows 57%](https://www.business-standard.com/amp/companies/news/jv-voltbek-s-fy25-revenue-rises-39-5-to-2-235-53-cr-volume-grows-57-125061500286_1.html) — FY25 revenue Rs 2,235.53 crore (+39.5%); volume +57%; Voltas invested Rs 102.41 crore in Voltbek share capital in FY25; Sanand capacity being expanded ~50%
- *Quietly compounding — the Sanand JV is scaling hard (revenue +39.5%, capacity +50%, fresh equity from the Indian partner) but Arcelik's name surfaces only inside Voltas results coverage, never in its own right.*

### Invisible by construction — the publicity names the Indian principal (2)

These firms sit inside projects the government promotes *heavily* — but the announcements name the Indian principal (Tata Electronics, the India Semiconductor Mission, SAIL), never the foreign supplier. They are not being ignored; they are structurally unnameable in the current announcement format. The same mechanism is visible in the register itself: Nippon Steel surfaces only as *ArcelorMittal Nippon Steel India*, and CLP only as *Apraava Energy*.

**Danieli** (Italy, Specialty Steel & Metals)
- 2025-12-19: [SAIL Turns to Danieli For IISCO Plant Expansion](https://www.aist.org/sail-turns-to-danieli-for-iisco-plant-expansion) — ~4 million tonnes/year added capacity (contract value not stated in this item)
- 2025-12: [Danieli to supply equipment for India's SAIL, EUR500 million contract](https://www.marketscreener.com/news/danieli-to-supply-equipment-for-india-s-sail-eur500-million-contract-ce7d50dbdd89f62d) — EUR 500 million
- 2025-12: [Danieli strengthens its presence in India with major project for SAIL](https://www.danieli.com/en/news-media/news/danieli-strengthens-its-presence-india-major-project-sail_37_1020.htm) — EUR 500 million (per group)
- *Genuinely large in-window India activity — an approx EUR 500m equipment order for SAIL's IISCO Burnpur expansion (Dec 2025) — but it is an export order, not Indian capex by Danieli, and it sits inside a project the Indian state publicises loudly.*

**Merck KGaA** (Germany, Electronics & Semiconductors)
- 2025-09-02: [Tata Electronics and Merck Electronics Sign Memorandum of Understanding to Strengthen Semiconductor Capabiliti](https://www.tataelectronics.com/w/tata-electronics-and-merck-electronics-sign-memorandum-of-understanding-to-strengthen-semiconductor-capabilities-in-india) — Dholera fab total investment INR 91,000 crore (~USD 11 billion); Merck group sales EUR 21.2 billion (2024). No Merck-specific India figure disclosed.
- *Active but structurally invisible — a Sept 2025 materials-and-fab-infrastructure MoU for Tata's INR 91,000 crore Dholera fab, with Merck's role announced only by Tata and trade press while the government headline space goes to the Indian partner.*

### Publicised by a state, invisible at the centre (5)

Real activity that a **state government amplified** — land allotted and announced, a Chief Minister at the ground-breaking — while no PIB headline ever named the firm. This is a centre-versus-state visibility gap, not stealth, and it says something about which door these investors came through.

**AstraZeneca** (United Kingdom, Pharma & Bulk Drugs)
- 2025-06-26: [AstraZeneca expands Bangalore Global Hub in India with Rs 166 Crore Investment, creating 400 Jobs to boost R&D](https://www.astrazeneca.com/content/az-in/media/press-releases/2025/astrazeneca-expands-bangalore-global-hub-in-india.html) — INR 166 crore; 400 new jobs
- 2025-09-08: [AstraZeneca announces Rs 176 crore investments in India to expand Chennai GITC](https://medicaldialogues.in/news/industry/pharma/astrazeneca-announces-rs-176-crore-investments-in-india-to-expand-chennai-gitc-154816) — INR 176 crore
- 2024-07: [AstraZeneca plans to invest Rs 250 crore to grow its Global Innovation and Technology Centre in India, bringin](https://www.astrazeneca.com/content/az-in/media/press-releases/2024/astrazeneca-plans-to-invest-to-grow-its-gitc-in-india.html) — INR 250 crore; ~1,300 roles
- *Very active (three tranches, ~INR 592 crore across Bengaluru and Chennai in 15 months) but only half-hidden — the Chennai tranche was launched at a Tamil Nadu government roadshow alongside the CM, so the 'no PIB headline' signal understates its official visibi*

**Sanofi** (France, Pharma & Bulk Drugs)
- 2024-07-17: [Sanofi announces expansion of its Global Capability Centre in Hyderabad](https://www.sanofi.com/assets/countries/india/docs/Media/press-releases/2024/sanofi-announces-expansion-of-its-global-capability-centre-in-hyderabad.pdf) — EUR 400 million over six years, of which EUR 100 million by 2025 (reported elsewhere as ~USD 437 million)
- 2023-06: [Sanofi India sells muscle relaxant brand Myoril to Corona Remedies](https://www.business-standard.com/topic/sanofi-india) — INR 234 crore (divestment)
- *Large and real (EUR 400m Hyderabad GCC, Jul 2024) but not truly quiet — the Telangana CM publicly endorsed it; and the India story is mixed, with brand divestments and a consumer-health demerger running alongside the GCC build-out.*

**Thales** (France, Aerospace & Defence)
- 2026-02-17: [India-France Year of Innovation 2026: India is now part of the five Thales global corporate research centers](https://www.webwire.com/ViewPressRel.asp?aId=350676) — No India-specific figure; Thales spends >EUR 4 billion/year on R&D globally. Over 2,300 staff across Thales and its Indian JVs.
- date not verified: [Thales Unveils State-of-the-Art Inflight Entertainment & Services Lab at its Engineering Competence Centre in ](https://www.thalesgroup.com/en/news-centre/press-releases/thales-unveils-state-art-inflight-entertainment-services-lab-its) — Not disclosed
- *Real R&D escalation (India promoted to one of five global Thales corporate research centres, Feb 2026) but the least 'quiet' name in the set — a Karnataka minister spoke at the launch and it was staged inside a bilateral India-France innovation year.*

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

### Intent stated, not yet converted (8)

The annual report expresses India or APAC interest, but no dated India activity surfaced inside the three-year window — or the only commitment predates it. Intent has not become capex.

**Embraer** (Brazil, Aerospace & Defence)
- 2024-02-01: [Embraer and Mahindra announce collaboration on the C-390 Millennium Medium Transport Aircraft in India](https://www.embraer.com/media-center/en/?mediatype=NEWS&detail=13870) — IAF MTA requirement reported at up to 80 aircraft
- 2026-06: [Embraer to offer India its own C-390 assembly line as part of bid for new military transport](https://www.flightglobal.com/archive/2026/06/embraer-prepared-to-open-indian-c-390-assembly-site-to-support-sale/) — fleet recapitalisation up to 80 transport aircraft
- 2026-02-20: [Embraer, Mahindra plan C-390 MRO facility for India air force bid](https://www.flightglobal.com/fixed-wing/embraer-mahindra-plan-india-mro-for-c-390-bid/166387.article) — not stated
- *Sustained, escalating India campaign (Feb-2024 MoU to Oct-2025 cooperation agreement to Feb-2026 MRO siting) but strictly a competition bid — no signed aircraft order, so 'investment intent' is conditional, not committed.*

**Kerry Group** (Ireland, Food Processing)
- 2019-06-25: [Kerry opens new facility in India to boost research and innovation](https://www.foodbev.com/news/kerry-opens-new-facility-in-india-to-boost-research-and-innovation) — EUR 20 million
- *No India activity found in window (Jul 2023 - Jul 2026); the widely-cited Kerry India facility story is from June 2019 and predates the window by four years.*

**Indra Sistemas** (Spain, Aerospace & Defence)
- 2023-03-09: [Indra is set to improve flight capacity and safety in India with a pioneering system that centralizes all air ](https://www.indragroup.com/en/noticia/indra-set-improve-flight-capacity-safety-india-pioneering-system-centralizes-air-traffic) — More than EUR 55 million
- *No verifiable India activity found inside the window; the flagship EUR 55m AAI air-traffic contract lands March 2023, four months before the window opens — a genuine near-miss worth re-checking with better newsroom access.*

**Iveco Group** (Italy, Auto, EV & Components)
- 2025-07-30: [TATA MOTORS TO ACQUIRE IVECO GROUP, TOGETHER CREATING A GLOBAL PLAYER IN COMMERCIAL VEHICLES](https://static-assets.tatamotors.com/Production/www-tatamotors-com-NEW/wp-content/uploads/2025/07/TataMotorsIveco.pdf) — ~EUR 3.8 billion (Forbes India cites EUR 3.9bn)
- *No in-window India investment by Iveco; the only major India-linked news is Tata Motors acquiring Iveco (Jul 2025) — an inbound takeover that must not be scored as European investment into India.*

**Sika AG** (Switzerland, Auto, EV & Components)
- 2023-06-27: [Sika opens plant in India](https://www.indianchemicalnews.com/chemical/sika-opens-plant-in-india-17974) — Not disclosed
- *No India activity found in window — the Kharagpur plant opening lands 2023-06-27, four days before the window starts, and no later Indian plant, expansion or capex announcement could be verified.*

**Thungela Resources** (South Africa, Green Energy & Fuels)
- 2024-02-13: [Thungela establishes export marketing function in Dubai](https://www.worldcoal.com/coal/13022024/thungela-establishes-export-marketing-function-in-dubai/) — not stated
- *NO INDIA ACTIVITY FOUND IN WINDOW — India appears only as a demand-side export destination in results commentary (and 2024-25 commentary describes Indian demand as BELOW expectations); the marketing entity went to Dubai, not India.*

**Orica** (Australia, Chemicals & Plastics)
- *NO INDIA ACTIVITY FOUND IN WINDOW — Orica's Indian Explosives Pvt Ltd (Gomia, Jharkhand) is a long-standing wholly-owned subsidiary with revenue of Rs 467 crore in FY2023, but every located expansion reference (Gomia capacity upgrade, Nagpur site feasibility) *

**Ansell** (Australia, Medical Devices)
- *NO DATED IN-WINDOW NEWS ITEM FOUND — Ansell's material India commitment (the ~USD 80m Kovai greenfield plant in Tamil Nadu, with a further USD 40m phase taking it to USD 120m) was announced Dec-2022/Mar-2023, before the window; post-July-2023 coverage is only *

## Then we checked ministry publications — and a third of the list was wrong

PIB headlines are the wrong instrument for this question. Of 12 quiet investors checked against ministry publications, 8 were found named and their labels corrected. The channels that name companies are annexure PDFs, long directories, regulator orders and monthly summaries -- none of which put a company name in a title, so a title-indexed register structurally cannot see them.

**Channels that actually name companies** (none of which title-index them): PLI beneficiary annexures (DPIIT/MeitY/MoFPI); DSIR Directory of Recognised In-house R&D Units; MNRE ALMM approved-manufacturer lists; CERC / regulator orders; Ministry monthly summaries (e.g. MoPSW); Coffee Board / commodity-board registers.

**Two systemic blind spots in name-matching:**

- RENAMED ENTITIES: CLP -> Apraava (2022) erases every post-rename government record from a parent-name match
- SUBSIDIARY ALIASES: Indus Coffee, WEG Industries (India), Voltbek, Panasonic India -- the government names the Indian entity, never the foreign parent

**Disproofs — worth more than the confirmations:**

- Lenovo is NOT on MeitY's list of 27 approved IT-hardware PLI 2.0 companies, contrary to wide reporting
- Arcelik/Voltbek is NOT among the 42 White Goods PLI beneficiaries; JV parent Voltas Limited is (Sl. 11) -- a false-positive trap

**Invisibility that survived the check:**

- **Elbit Systems** — searched, not found -- defence opacity: every retrievable account of the Adani-Elbit UAV facility and the May-2025 Sparton sonobuoy agreement traces to Adani corporate media, never a ministry document
- **Siam Cement Group (SCG)** — searched, not found -- absent centrally; the Kheda (Kapadvanj) AAC plant inauguration was a Gujarat state event
- **MediaTek** — searched, not found -- structurally ineligible for the Design Linked Incentive, which is scoped to domestic startups/MSMEs/academia -- absence is by scheme design, not neglect
- **Arcelik** — searched, not found -- AFFIRMATIVELY DISPROVED, not merely unconfirmed: absent from all 42 White Goods PLI beneficiaries, the FDI table and the CoE referral table. Trap recorded -- JV parent Voltas Limited IS a separate beneficiary at Sl. 1

## How to use this

The **quiet investors** are the actionable list: they are spending money in India now, and no arm of government is visibly engaging them. The **state-publicised** names show which states are winning investors the centre has not claimed. The **Press Note 3** names should not be worked as leads at all. The **no-activity** names are the watch list — stated intent that has not become capex, worth re-checking next cycle.

Companion views: `docs/TARGET_LEADS.md` (scored targets), `docs/LEADS.md` (full layer), `docs/reportage_ministry.html` (what the government announced, by ministry).
