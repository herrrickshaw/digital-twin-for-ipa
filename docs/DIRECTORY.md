# Portal & Source Directory

*Generated 2026-07-20 from `layers/15_directory.json` (machine version used by `scripts/refresh_twin.py routes`).*

## Central government

| Portal | URL | Access note |
|---|---|---|
| PIB register | https://www.pib.gov.in | POST to www subdomain ONLY (bare-domain 301 turns POSTs into GETs) |
| NSWS | https://www.nsws.gov.in | only official company-facing aggregator |
| UNNATI portal | https://unnati.dpiit.gov.in | registration STOPPED (oversubscribed) as of 2026-07-20; watch notice for resumption |
| DPIIT | https://www.dpiit.gov.in | FDI quarterly fact sheets under publications |
| RBI WSS archive | https://rbi.org.in/scripts/WSSView.aspx?Id=N | enumerable to 1998, no key |
| MeitY (headless WP) | https://www.meity.gov.in/cms/wp-json | 22-scheme API list |
| Ministry of Power CMS | https://cms-powermin.digifootprint.gov.in/wp-json/wp/v2/ | digifootprint headless-WP pattern |
| MoHUA CMS | https://cms-mohua.digifootprint.gov.in/wp-json/wp/v2/ |  |
| DSIR CMS | https://cms-dsir.digifootprint.gov.in/wp-json/wp/v2/ |  |
| Tourism CMS | https://www.tourism.gov.in/cms/wp-json/wp/v2/schemes_and_services |  |
| MSDE CMS | https://www.msde.gov.in/cms/wp-json/wp/v2/schemes_and_services |  |
| BIRAC | https://birac.nic.in/cfp.php | resolves only via pinned IP 164.100.228.150 when DNS fails |
| TDB | https://tdb.gov.in | RDI Fund / active CFPs |
| iDEX | https://idex.gov.in |  |
| SRIJAN | https://srijandefence.gov.in |  |
| DDP MoD | https://www.ddpmod.gov.in |  |
| AIF agri portal | https://agriinfra.dac.gov.in | live sanction stats on homepage |
| DFPD | https://dfpd.gov.in | fully client-side; needs browser |
| NCDC | https://www.ncdc.in/index.jsp?page=scheme |  |
| CPCB EPR portals | https://cpcb.gov.in/all-epr-portals-of-cpcb/ | six-portal SSO listing page |
| Green Credit portal | https://moefcc-gcp.in |  |
| MIB film incentives | https://mib.gov.in | guidelines = 6MB scanned PDF; local pypdf |
| RailSAHAY GCT | https://www.fois.indianrail.gov.in/RailSAHAY/index.jsp |  |
| Bharat Gaurav | https://bharatgauravtrains.indianrailways.gov.in |  |
| MoRTH backend API | https://morth.gov.in/backend/api/gazettes-notifications | search params ignored; download+grep |
| Vehicle scrapping single window | https://vscrap.parivahan.gov.in |  |
| PRS DFG | https://prsindia.org/budgets/parliament | curl+Chrome-UA clean |

## States & UTs

| Portal | URL | Access note |
|---|---|---|
| Gujarat IFP | https://ifp.gujarat.gov.in/DIGIGOV/ | incentives-granted dashboard |
| Gujarat IC | https://ic.gujarat.gov.in |  |
| Maharashtra MAITRI | https://maitri.maharashtra.gov.in/resources/policies/ |  |
| Rajasthan RajNivesh | https://rajnivesh.rajasthan.gov.in | rips.rajasthan.gov.in refuses connections |
| Goa DITC | https://ditc.goa.gov.in | invalid TLS cert; curl -k |
| TN Guidance | https://www.investingintamilnadu.com/business-in-tamil-nadu/policy-notifications |  |
| TN single window | https://tnswp.com/DIGIGOV/swp-tnswp.jsp |  |
| Karnataka Udyog Mitra | https://investkarnataka.co.in | invest.karnataka.gov.in does NOT exist |
| Karnataka EITBT | https://eitbt.karnataka.gov.in |  |
| Telangana invest | https://invest.telangana.gov.in/policies/ |  |
| TG-iPASS | https://ipass.telangana.gov.in |  |
| Telangana Life Sciences | https://lifesciences.telangana.gov.in |  |
| AP Industries | https://www.apindustries.gov.in/APIndus/Default.aspx |  |
| Kerala KSIDC | https://ksidc.org/invest-kerala/incentive-schemes/ |  |
| Kerala K-SWIFT | https://kswift.kerala.gov.in |  |
| Kerala invest | https://invest.kerala.gov.in |  |
| UP Invest | https://invest.up.gov.in/policies/ |  |
| UP Nivesh Mitra | https://niveshmitra.up.nic.in |  |
| Haryana single window | https://investharyana.in | policy texts login-gated; names in public JS bundle |
| Punjab Invest | https://investpunjab.gov.in | Angular shell; IBDP 2026 gazette PDF path known |
| Uttarakhand invest | https://investuttarakhand.uk.gov.in/site/Policies |  |
| Himachal SWCS | https://app.emerginghimachal.hp.gov.in/frontend/web/index.php/site/schemes-policies |  |
| Delhi industries | https://industries.delhi.gov.in |  |
| MP invest (WP paths) | https://invest.mp.gov.in/policy-acts-rules/ | root redirects to React shell; use direct WP paths |
| Chhattisgarh invest | https://invest.cg.gov.in/investment_promotion | subsidy calculator at /calculator |
| Odisha invest | https://investodisha.gov.in/policy-framework/industrial-policy-resolution-2022 |  |
| WB Silpasathi | https://silpasathi.wb.gov.in/msme_Incentives | wbidc.com is HIJACKED -- never cite |
| Jharkhand Advantage | https://advantage.jharkhand.gov.in/SingleWindow/registrations/policies/ |  |
| Bihar Udyami | https://udyami.bihar.gov.in |  |
| Bihar BIADA | https://biada1.bihar.gov.in/ActRule.aspx |  |
| Assam EODB | https://eodb.assam.gov.in/site/government_incentives | investinassam.com is SQUATTED -- never cite |
| Meghalaya industry | https://megindustry.gov.in |  |
| Tripura industries | https://industries.tripura.gov.in/incentives |  |
| Mizoram industries | https://industries.mizoram.gov.in |  |
| Nagaland industry | https://industry.nagaland.gov.in/unnati/ |  |
| Sikkim industries | https://industries.sikkim.gov.in/visitors/schemes |  |
| J&K single window | https://singlewindow.jk.gov.in |  |

## 🔴 Known-bad domains — never cite

| Domain | Why |
|---|---|
| wbidc.com | HIJACKED (suspended cPanel iframing ad domain) |
| investinassam.com | SQUATTED (gambling-link blog) |
| biharbusinessconnect.com | lapsed/parked redirect |
| invest.karnataka.gov.in | NXDOMAIN |
| kum.karnataka.gov.in | NXDOMAIN |
| morth.nic.in | DNS dead |
| udyog.bihar.gov.in | NXDOMAIN |
| invest.rajasthan.gov.in | retired |
| goa-idc.com | NXDOMAIN |
| dic.nagaland.gov.in | NXDOMAIN |
| fert.nic.in | dead |
| texmin.nic.in | dead |
