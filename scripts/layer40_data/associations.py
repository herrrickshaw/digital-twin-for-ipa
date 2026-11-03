"""Layer 40 trade-association table (hand-curated data, one dict per association)."""
# ---------------------------------------------------------------------------
# ASSOCIATIONS -- sector, scope, access method, linked events
# ---------------------------------------------------------------------------
ASSOCIATIONS = [
    {"name": "Swiss Textile Machinery Association", "sector": "Textiles & Apparel", "scope": "Switzerland",
     "url": "https://swisstextilemachinery.ch", "member_directory": "swisstextilemachinery.ch/members",
     "access_method": "public HTML (full) + downloadable PDF (2023, 2025 editions -- richer: address/email/competence)",
     "pdf_urls": ["https://www.swisstextilemachinery.ch/uploads/files/Swissmem-STM-Members_2025-1.pdf",
                  "https://www.swisstextilemachinery.ch/uploads/files/Swissmem-Members_Leporello_2023.pdf"],
     "member_count": 42, "linked_events": ["India ITME", "ITMA", "ITMA Asia+CITME"],
     "last_verified": "2026-08-22", "recheck_recommended": "annual, or before each India ITME cycle (biennial)"},
    {"name": "CEMATEX", "sector": "Textiles & Apparel", "scope": "Europe (federation of 9 national bodies)",
     "url": "https://cematex.com", "member_directory": "cematex.com/our-members",
     "access_method": "public HTML, federation-level only (9 national associations, not companies)",
     "member_count": 9, "linked_events": ["ITMA", "ITMA Asia+CITME"],
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "ITMF", "sector": "Textiles & Apparel", "scope": "Global (40+ countries)",
     "url": "https://itmf.org", "member_directory": "itmf.org/membership/members + /associate-members",
     "access_method": "public HTML partial (national members 19/40+) + full (associate members 19) "
                      "+ login-gated (corporate members); directory PDF path returns HTTP 504, dead",
     "member_count": None, "linked_events": [],
     "note": "India represented via 3 associate bodies: CAI, CITI, Texprocil -- no national-member seat",
     "last_verified": "2026-08-22", "recheck_recommended": "annual (also publishes ITMSS annual shipment stats)"},
    {"name": "VDMA Textile Machinery", "sector": "Textiles & Apparel", "scope": "Germany (+ AT/FR/NL/IT/PT/CH/SE ~13%)",
     "url": "https://vdma.eu/en/textile-machinery", "member_directory": "vdma.eu/en/members-textile-machinery",
     "access_method": "public but JS-rendered A-Z search UI, not scrapable via plain fetch; no PDF found",
     "member_count": 140, "linked_events": ["ITMA", "India ITME"],
     "note": "Runs own India offices: Bangalore, Kolkata, New Delhi/Noida, Mumbai",
     "last_verified": "2026-08-22", "recheck_recommended": "annual; needs browser automation for full scrape"},
    {"name": "ACIMIT", "sector": "Textiles & Apparel", "scope": "Italy",
     "url": "https://acimit.it", "member_directory": "acimit.it/en/acimit-members/product-search/",
     "access_method": "public HTML (full, 185 members, segment+city tagged); General Directory PDF "
                      "exists but Issuu-viewer-gated, no raw .pdf URL found (editions 2014/15/17/20/2023)",
     "member_count": 185, "linked_events": ["ITMA", "India ITME"],
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "UKFT (UK Fashion & Textile Association)", "sector": "Textiles & Apparel", "scope": "United Kingdom",
     "url": "https://ukft.org", "member_directory": "ukft.org/who-we-are/about-us/members",
     "access_method": "public HTML (500 of claimed 2,500+ members, many unlisted by request); "
                      "member area PDFs are quarterly newsletters only, no directory PDF",
     "member_count": 500, "linked_events": [],
     "note": "Member-paywalled India market guide exists (tied to UK-India CETA, force 15-Jul-2026)",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "The Textile Institute", "sector": "Textiles & Apparel", "scope": "Global (14 countries)",
     "url": "https://textileinstitute.org", "member_directory": "textileinstitute.org/my-ti/members-directory/",
     "access_method": "public HTML searchable DB, no PDF", "member_count": 50, "linked_events": [],
     "note": "5 of 50 corporate members are Indian (Gherzi, NITRA, SITRA, RmKV Silks, ITTA)",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "BTMA (British Textile Machinery Association)", "sector": "Textiles & Apparel", "scope": "United Kingdom",
     "url": "https://btma.org.uk", "member_directory": "btma.org.uk/our-members/",
     "access_method": "public HTML (full, 49 members); ITMA-2023 exhibitor-subset PDF also found "
                      "(btma.org.uk/wp-content/uploads/btma-itma-2023-brochure.pdf, ~31 members)",
     "member_count": 49, "linked_events": ["ITMA"],
     "last_verified": "2026-08-22", "recheck_recommended": "annual, or before each ITMA cycle"},
    {"name": "JTMA (Japan Textile Machinery Association)", "sector": "Textiles & Apparel", "scope": "Japan",
     "url": "http://www.jtma.or.jp", "member_directory": "jtma.or.jp/member/",
     "access_method": "UNRELIABLE -- site returned ECONNREFUSED during research; only secondary-"
                      "sourced (Wikipedia + search snippets), 5 names live-corroborated via search",
     "member_count": None, "linked_events": ["India ITME"],
     "last_verified": "2026-08-22", "recheck_recommended": "retry direct fetch; low confidence until then"},
    {"name": "CNTAC (China National Textile and Apparel Council)", "sector": "Textiles & Apparel", "scope": "China",
     "url": "cntac.org.cn", "member_directory": "N/A -- 42-unit federation of sub-associations/institutes/universities, not a company directory",
     "access_method": "partial council-roster PDF retrieved directly (~115 of likely 200+ entries)",
     "member_count": None, "linked_events": ["ITMA Asia+CITME"],
     "last_verified": "2026-08-22", "recheck_recommended": "low priority -- structurally not a company roster"},
    {"name": "KOFOTI (Korea Federation of Textile Industries)", "sector": "Textiles & Apparel", "scope": "Korea",
     "url": "kofoti.or.kr", "member_directory": "NONE FOUND",
     "access_method": "no public member directory; affiliated portal koreatextile.org claims ~4,000 "
                      "manufacturers by category but no extractable company names",
     "member_count": None, "linked_events": [],
     "last_verified": "2026-08-22", "recheck_recommended": "low priority until a real directory surfaces"},

    # -- Electronics & Semiconductors / White Goods --------------------------
    {"name": "SEMI", "sector": "Electronics & Semiconductors", "scope": "Global",
     "url": "https://www.semi.org", "member_directory": "semi.org/en/resources/member-directory",
     "access_method": "structure confirmed (~3,000 members, country/segment filterable) but "
                      "Cloudflare-blocked (403 on direct fetch/curl) -- needs live browser",
     "member_count": 3000, "linked_events": ["SEMICON India", "SEMICON West", "electronica"],
     "last_verified": "2026-08-22", "recheck_recommended": "retry with live browser session"},
    {"name": "IPC / Global Electronics Association", "sector": "Electronics & Semiconductors", "scope": "Global",
     "url": "https://www.electronics.org", "member_directory": "electronics.org/member-directory",
     "access_method": "public HTML, no login, country-filterable, verified live",
     "member_count": None, "linked_events": [],
     "note": "Country facet counts confirmed real: India 739, China 1317, US 7685, Germany 640, "
            "UK 644, Taiwan 332, France 335, Japan 275, Singapore 182, South Korea 120",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "CECED Europe / APPLiA (Home Appliance Europe)", "sector": "White Goods & Electricals", "scope": "Europe",
     "url": "https://appliaeurope.eu", "member_directory": "ceced.eu / appliaeurope.eu members page",
     "access_method": "direct fetch blocked (403); member list reconstructed via search-engine "
                      "summaries only, NOT raw-scraped -- spot-verify before formal use",
     "member_count": None, "linked_events": ["ELECRAMA"],
     "note": "Sample: Arçelik, Ariston Thermo, BSH, Candy, Daikin, De'Longhi, Electrolux, Gorenje, "
            "LG, Liebherr, Miele, Panasonic, Philips, Samsung, SEB, Vestel, Vorwerk, Whirlpool",
     "last_verified": "2026-08-22", "recheck_recommended": "verify raw on ceced.eu/appliaeurope.eu directly"},
    {"name": "AHAM (Association of Home Appliance Manufacturers)", "sector": "White Goods & Electricals", "scope": "United States",
     "url": "https://www.aham.org", "member_directory": "aham.org membership page",
     "access_method": "direct fetch blocked; only a partial Canada-council fragment surfaced "
                      "(Alticor, BISSELL, Blueair, Brown Stove Works, BSH, Panasonic Canada, "
                      "Samsung Canada) -- LOW CONFIDENCE, needs authenticated pull",
     "member_count": 150, "linked_events": [],
     "last_verified": "2026-08-22", "recheck_recommended": "needs direct authenticated pull from aham.org"},
    {"name": "CEAMA (Consumer Electronics and Appliances Manufacturers Association)", "sector": "White Goods & Electricals", "scope": "India",
     "url": "https://ceama.in", "member_directory": "NONE ACCESSIBLE",
     "access_method": "403 on both WebFetch and curl -- no member data obtained",
     "member_count": None, "linked_events": ["ELECRAMA"],
     "note": "India's own white-goods association -- the one clean gap in this sector, worth a "
            "manual visit or Wayback snapshot",
     "last_verified": "2026-08-22", "recheck_recommended": "manual browser visit or Wayback Machine"},

    # -- Auto, EV & Components ------------------------------------------------
    {"name": "VDA (Verband der Automobilindustrie)", "sector": "Auto, EV & Components", "scope": "Germany",
     "url": "https://www.vda.de", "member_directory": "vda.de/en/members/manufacturer-group-{I,II,III}",
     "access_method": "public HTML, live site, fully scraped across 3 tiers",
     "member_count": 567, "linked_events": ["IAA Mobility", "Automechanika Frankfurt", "Auto Expo Components"],
     "note": ("Group I (21 OEMs): Audi, BMW, Daimler Truck, Porsche, Ford-Werke, IVECO Deutschland, "
             "MAN Truck & Bus, Mercedes-Benz AG/Group, Opel, Stellantis Germany, TRATON, Volkswagen. "
             "Group II (62 trailer/body/bus): Daimler Buses, Schmitz Cargobull, Goldhofer, Kässbohrer, "
             "Erwin Hymer Group. Group III (484 parts suppliers, largest verified roster in this "
             "registry): Robert Bosch, Continental, ZF Friedrichshafen, Schaeffler, Valeo, Magna "
             "(Germany), MAHLE, Denso Automotive Deutschland, Aptiv Services Deutschland, Autoliv."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "JAMA (Japan Automobile Manufacturers Association)", "sector": "Auto, EV & Components", "scope": "Japan",
     "url": "https://www.jama.or.jp", "member_directory": "jama.or.jp/english/links/member-manufacuturers.html",
     "access_method": "public HTML, FULL list, verified", "member_count": 14, "linked_events": ["Auto Expo Components"],
     "note": ("Complete: Daihatsu, Hino Motors, Honda, Isuzu, Kawasaki Motors, Mazda, Mitsubishi "
             "Motors, Mitsubishi Fuso Truck & Bus, Nissan, Subaru, Suzuki, Toyota, UD Trucks, "
             "Yamaha Motor. OEM-only, no component-tier members. (GM Japan = former member.)"),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "CLEPA (European Association of Automotive Suppliers)", "sector": "Auto, EV & Components", "scope": "Europe",
     "url": "https://clepa.eu", "member_directory": "clepa.eu/flipbooks/membercatalogue/ (JS flipbook, not fetchable headlessly)",
     "access_method": "partial (~30 of 116 corporate members confirmed via search) -- full roster "
                      "needs a live-browser session against the flipbook",
     "member_count": 116, "linked_events": ["IAA Mobility", "Automechanika Frankfurt"],
     "note": ("~3,000 companies represented via 116 corporate + 12 national association + 19 "
             "associate members. Confirmed corporate sample: Bosch, Continental, Valeo, ZF, Magna, "
             "Schaeffler, Aptiv, Denso, Aisin, Lear, Marelli, Forvia, Brembo, SKF, Knorr-Bremse, "
             "Tenneco, Veoneer, Nexteer, BACC, Hengst, HL Mando, Horse, Murata; associate: OXA, "
             "Mobileye, Alcoa Wheels."),
     "last_verified": "2026-08-22", "recheck_recommended": "live-browser pull of the flipbook for the full 116"},
    {"name": "ACMA (Automotive Component Manufacturers Association of India)", "sector": "Auto, EV & Components", "scope": "India",
     "url": "https://www.acma.in", "member_directory": "N/A -- 750+ Indian manufacturer members only, no foreign roster",
     "access_method": "confirmed structurally: ACMA holds MOUs (not memberships) with counterpart "
                      "bodies in 27 countries incl. VDA/CLEPA/MEMA/JAMA -- use as context, not a target list",
     "member_count": 750, "linked_events": ["Auto Expo Components", "ACMA Automechanika New Delhi"],
     "last_verified": "2026-08-22", "recheck_recommended": "low priority -- structurally not a foreign-company source"},

    # -- Pharma & Bulk Drugs / Medical Devices --------------------------------
    {"name": "EFPIA (European Federation of Pharmaceutical Industries and Associations)", "sector": "Pharma & Bulk Drugs", "scope": "Europe",
     "url": "https://efpia.eu", "member_directory": "efpia.eu/about-us/membership/",
     "access_method": "public HTML, FULL list, verified", "member_count": 47, "linked_events": ["CPHI Worldwide"],
     "note": ("35 full corporate: AbbVie, Almirall, Amgen, Astellas, AstraZeneca, Bayer, Biogen, "
             "Boehringer Ingelheim, BMS, Chiesi, CSL Behring, CSL Vifor, Daiichi Sankyo, Gilead, "
             "Grünenthal, GSK, Ipsen, J&J, LEO Pharma, Eli Lilly, Lundbeck, Menarini, Merck KGaA, "
             "MSD, Novartis, Novo Nordisk, Otsuka, Pfizer, Pierre Fabre, Roche, Sanofi, Servier, "
             "Takeda, Teva, UCB; 4 affiliate + 8 SME members; 18 national assoc. full + 17 affiliate."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "PhRMA", "sector": "Pharma & Bulk Drugs", "scope": "United States",
     "url": "https://phrma.org", "member_directory": "phrma.org/membership (JS-rendered)",
     "access_method": "reconciled from Wikipedia/Ballotpedia citing PhRMA's own disclosures (June "
                      "2025), not raw-scraped",
     "member_count": 31, "linked_events": ["CPHI Worldwide"],
     "note": ("Alkermes, Amgen, Astellas, AstraZeneca (rejoined 2025), Bayer, Biogen, BioMarin, "
             "Boehringer Ingelheim, BMS, CSL Behring, Daiichi Sankyo, Eisai, Eli Lilly, EMD Serono, "
             "Genentech, Genmab, Gilead, GSK, Incyte, Ipsen, J&J, Lundbeck, Merck & Co., Neurocrine, "
             "Novartis, Novo Nordisk, Otsuka, Pfizer, Sage Therapeutics, Sanofi, Takeda, UCB. "
             "AbbVie and Teva have EXITED in recent years -- verify current before assuming membership."),
     "last_verified": "2026-08-22", "recheck_recommended": "verify raw on phrma.org/membership"},
    {"name": "MedTech Europe", "sector": "Medical Devices", "scope": "Europe",
     "url": "https://www.medtecheurope.org", "member_directory": "medtecheurope.org/about-us/members/",
     "access_method": "confirmed real, JS-filterable, didn't fully unroll via fetch",
     "member_count": 300, "linked_events": ["MEDICA", "Medical Fair India"],
     "note": "Sample: Abbott, Alcon, Ambu, Boston Scientific, J&J, Medtronic, Philips, Roche, "
            "Siemens Healthineers, Smith & Nephew, Stryker; ~40 national medtech associations also listed",
     "last_verified": "2026-08-22", "recheck_recommended": "needs live browser to unroll full filter"},
    {"name": "AdvaMed", "sector": "Medical Devices", "scope": "United States",
     "url": "https://www.advamed.org", "member_directory": "advamed.org/membership-join/membership-directory/",
     "access_method": "confirmed real, 1,000+ companies, partial extraction (60+)",
     "member_count": 1000, "linked_events": ["MEDICA", "Medical Fair India"],
     "note": "Sample: Abbott, Boston Scientific, J&J MedTech, Medtronic, Stryker, Zimmer Biomet, "
            "GE HealthCare, Siemens Healthineers, Canon Medical, Bio-Rad, bioMérieux, Hologic, "
            "Intuitive Surgical, DexCom, Insulet, Tandem Diabetes; sub-divisions AdvaMedDx, AdvaMed Accel",
     "last_verified": "2026-08-22", "recheck_recommended": "live browser for full 1,000+"},

    # -- Green Energy & Fuels / Chemicals & Plastics --------------------------
    {"name": "WindEurope", "sector": "Green Energy & Fuels", "scope": "Europe (35+ countries)",
     "url": "https://windeurope.org", "member_directory": "windeurope.org/membership/meet-our-members",
     "access_method": "official archival PDF found (Aug 2024 snapshot, 40 pages) -- only letters "
                      "A-D (page 1 of 4) extracted; trivial to complete",
     "pdf_url": "https://cms.influencemap.net/site/data/001/589/WindEurope_members_Aug2024-.pdf",
     "member_count": 600, "linked_events": ["WindEnergy Hamburg", "Intersolar Europe"],
     "note": ("24 Leading Members: Acciona, EDF Renouvelables, EDP, Enel Green Power, Enercon, "
             "Engie, Equinor, ERG, GE Vernova, Hitachi Energy, Iberdrola, Nordex, Ørsted, Repsol, "
             "RES, RWE, Shell, Siemens Energy, TPI, Vattenfall, Vestas, ZF Wind Power. A-D sample: "
             "ABB, ArcelorMittal, Arup, Axpo, BASF Renewable Energy, BayWa r.e., BP, Brookfield "
             "Renewable, Cadeler, Covestro Deutschland, Dassault Systèmes, DEME Offshore."),
     "last_verified": "2026-08-22", "recheck_recommended": "complete E-Z pages from the same PDF"},
    {"name": "SolarPower Europe", "sector": "Green Energy & Fuels", "scope": "Europe",
     "url": "https://solarpowereurope.org", "member_directory": "solarpowereurope.org/membership/meet-our-members (JS, empty on fetch)",
     "access_method": "THIRD-PARTY MIRROR ONLY (aalep.eu lobbying-transparency snapshot) -- "
                      "directional, not primary-sourced, verify before formal use",
     "member_count": 210, "linked_events": ["Intersolar Europe"],
     "note": "Sample: APESF, APREN, APPA, BSW Germany, Holland Solar, Swissolar, UNEF Spain; "
            "corporates ABB, Amazon, E.ON, Enel, Google, Huawei, Siemens, Tesla",
     "last_verified": "2026-08-22", "recheck_recommended": "verify against live site or browser-driven filter pull"},
    {"name": "Cefic (European Chemical Industry Council)", "sector": "Chemicals & Plastics", "scope": "Europe (+ global affiliates)",
     "url": "https://cefic.org", "member_directory": "cefic.org (ACOM corporate members list not fully retrieved)",
     "access_method": "TWO full official PDFs obtained (Partner Companies, Associated Companies); "
                      "main ACOM corporate-member list (hundreds of EU producers) not retrieved",
     "member_count": 670, "linked_events": ["ACHEMA", "K Fair", "ChemTECH World Expo"],
     "note": ("Partner Companies (60, full): Avient, KBR, Linde Engineering, Lummus Technology, "
             "Schneider Electric, Outotec, Group Roullier, VTG. Associated Companies (23, full, "
             "non-European producers): includes TWO India-HQ'd firms -- Gujarat Fluorochemicals "
             "and Jubilant Pharmaceuticals -- plus Petronas, Equate Petrochemicals, Saudi Kayan, "
             "OCP, Methanex, Daicel/Asahi Kasei/Adeka/Tayca, Lomon Billions."),
     "last_verified": "2026-08-22", "recheck_recommended": "pull the ACOM corporate list via the Scribd mirror referenced on cefic.org"},
    {"name": "Austmine (Australia's mining equipment, technology & services industry association)",
     "sector": "Specialty Steel & Metals", "scope": "Australia",
     "url": "https://www.austmine.com.au", "member_directory": "austmine.com.au/members (not yet scraped)",
     "access_method": "identified as the organiser of Australia's national delegation to IMME 2024 "
                      "Kolkata (10 exhibitors, largest non-India contingent) -- member directory itself not yet checked",
     "member_count": None, "linked_events": ["IMME"],
     "note": ("Australia was IMME 2024's largest non-India delegation (10 of 268 exhibitors), led "
             "by Austmine -- a real, concrete India-engagement signal for the Australian mining-"
             "tech sector specifically. The full 10-company Australian exhibitor list is inside "
             "the IMME 2024 event record below; Austmine's own member roster (likely larger, "
             "Australia-wide) has not yet been pulled -- follow-up candidate."),
     "last_verified": "2026-08-22", "recheck_recommended": "pull austmine.com.au/members directly; cross-check against the IMME 2024 Australia delegation"},

    # -- Aerospace & Defence / Specialty Steel & Metals -----------------------
    {"name": "ASD Europe (AeroSpace and Defence Industries Association of Europe)", "sector": "Aerospace & Defence", "scope": "Europe (22 countries)",
     "url": "https://www.asd-europe.org", "member_directory": "asd-europe.org/about-asd/all-our-members/",
     "access_method": "public HTML, FULL list, verified", "member_count": 51, "linked_events": ["Aero India", "DefExpo"],
     "note": ("28 direct company members: Airbus, Antonov, Avio Aero, BAE Systems, Czechoslovak "
             "Group, Dassault Aviation, Diehl, EME, Fincantieri, GKN Aerospace, Hensoldt, Indra, "
             "KNDS, Kongsberg, Leonardo, Liebherr, MBDA, Naval Group, Navantia, Patria, PGZ, "
             "Rolls-Royce, Saab, Safran, Sopra Steria, Terma, Thales, WB Group. 23 national "
             "associations (BDLI/BDSV Germany, GIFAS France, AIAD Italy, TEDAE Spain, ADS Group "
             "UK...) representing 4,000+ companies in aggregate."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "worldsteel (World Steel Association)", "sector": "Specialty Steel & Metals", "scope": "Global",
     "url": "https://worldsteel.org", "member_directory": "worldsteel.org/about-us/membership/",
     "access_method": "public HTML, FULL list, verified", "member_count": 133, "linked_events": ["GIFA/METEC"],
     "note": ("89 regular (raw-steel-producer) members incl. ArcelorMittal, Nippon Steel, POSCO, "
             "Tata Steel, JSW Steel, SAIL, China Baowu, Nucor, US Steel, Cleveland-Cliffs, Gerdau, "
             "thyssenkrupp Steel Europe, voestalpine, JFE Steel, Hyundai Steel, Jindal Steel & "
             "Power (JSPL), Sunflag Iron & Steel, Saarloha Advanced Materials. 44 affiliated "
             "national associations incl. AISI (US), CISA (China), EUROFER, JISF (Japan), KOSA "
             "(Korea), Indian Steel Association, Joint Plant Committee (India), UK Steel."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},

    # -- Mining / Oil & Gas ----------------------------------------------------
    {"name": "ICMM (International Council on Mining and Metals)", "sector": "Specialty Steel & Metals", "scope": "Global",
     "url": "https://www.icmm.com", "member_directory": "icmm.com/en-gb/our-story/our-members",
     "access_method": "public HTML, FULL list (403 to WebFetch, worked via curl+browser UA)",
     "member_count": 69, "linked_events": ["IMME", "MINExpo"],
     "note": ("26 company members: African Rainbow Minerals, Alcoa, Anglo American, AngloGold "
             "Ashanti, Antofagasta, Barrick, BHP, Boliden, Codelco, Freeport-McMoRan, Glencore, "
             "Gold Fields, Hindustan Zinc, Hydro, Ma'aden, Minera San Cristóbal, Minsur, MMG, "
             "Newmont, Orano, Rio Tinto, Sibanye-Stillwater, South32, Sumitomo Metal Mining, Teck, "
             "Vale. ~43 association members (AusIMM, IBRAM, MCA, National Mining Association)."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "IPIECA", "sector": "Oil & Gas (not yet a twin focus sector)", "scope": "Global",
     "url": "https://www.ipieca.org", "member_directory": "ipieca.org/about/membership",
     "access_method": "public HTML, FULL corporate list, verified via WebFetch",
     "member_count": 39, "linked_events": ["ADIPEC", "OTC", "India Energy Week"],
     "note": ("ADNOC, Aker BP, Aramco, BP, Chevron, CNOOC, ConocoPhillips, Ecopetrol, ENEOS, Eni, "
             "EOG Resources, Equinor, ExxonMobil, Harbour Energy, INPEX, Murphy Oil, OMV, Oxy, "
             "Petrobras, PETRONAS, PTTEP, QatarEnergy, Repsol, Shell, Sonangol, Suncor, "
             "TotalEnergies, Woodside; associate: Baker Hughes, Halliburton, SLB; ~35 assoc. members."),
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
    {"name": "IOGP (International Association of Oil & Gas Producers)", "sector": "Oil & Gas (not yet a twin focus sector)", "scope": "Global",
     "url": "https://www.iogp.org", "member_directory": "iogp.org/members/",
     "access_method": "public HTML, partial (no downloadable PDF)", "member_count": 90,
     "linked_events": ["ADIPEC", "OTC"],
     "note": "Sample: Addax Petroleum, ADNOC, Aker BP, Aramco, BP, Chevron, CNOOC, ConocoPhillips, "
            "Eni, Equinor, ExxonMobil, Shell, TotalEnergies, Woodside; service firms Baker Hughes, "
            "Halliburton, SLB, Subsea7, TechnipFMC",
     "last_verified": "2026-08-22", "recheck_recommended": "annual"},
]

# ---------------------------------------------------------------------------
# EVENTS -- trade fairs, exhibitor-list access, cross-validation value
