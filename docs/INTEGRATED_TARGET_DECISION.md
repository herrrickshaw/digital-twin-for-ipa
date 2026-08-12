# Integrated target decision — scheme-approval roster × disclosed-interest leads

*Hand-researched synthesis, 2026-08-12. Cross-references [PLI_SCHEME_BENEFICIARY_LEADS.md](PLI_SCHEME_BENEFICIARY_LEADS.md) (government-approval evidence, Parliament Q&A + PIB) against layer 16 ([LEADS.md](LEADS.md) / [TARGET_LEADS.md](TARGET_LEADS.md), yfinance/filing-disclosure evidence) and layer 35 ([CAPITAL_COST_ARBITRAGE.md](CAPITAL_COST_ARBITRAGE.md), policy-rate-gap country prioritization). No build script — the two source layers use structurally different evidence (company says it's interested vs government confirms it's approved), so this can't be mechanically joined; it required reading both in full and judging each match by hand. Refresh manually when either source layer or the beneficiary doc updates.*

## Why this is worth doing

The two existing systems answer different questions and neither alone is sufficient:

- **Layer 16** (filing-mining) answers *"does this company say it's interested in India?"* — strong on breadth (263+ companies, 26+ countries) and recency (own-disclosure quotes), but structurally blind to two things: (1) companies that got a scheme approved without ever saying so in an annual report or 10-K (most PLI-Auto Component Champions never mention India by name in a way the mention-counter catches), and (2) schemes with **zero** current participants — a filing-mining approach can never surface "nobody has won this yet," because there's no filing to mine.
- **The PLI beneficiary roster** (this session's work) answers *"has the Indian government actually approved this company for money?"* — authoritative where it has data, but scoped only to the ~9 schemes harvested this session, and silent on companies operating in India outside any PLI-type scheme (pure market entrants, M&A, greenfield FDI with no incentive attached).

Put together, four evidence classes emerge, and they carry different decision weight.

## Tier S — Double-confirmed (disclosed interest + government-approved)

The strongest possible case: the company itself says it's committed to India, *and* the government's own record confirms an approved project or scheme slot. These are not prospects — they are proof points and expansion conversations.

| Company | Twin evidence (layer 16) | Scheme-roster evidence | Combined rationale |
|---|---|---|---|
| **Micron Technology** | Twin's #1 Tier-1 target (score 139): 10-K discloses the Gujarat ATMP incentive terms directly | ISM Landed, ₹22,516cr, 50% central support, production live since Feb 2026 | The single best-evidenced case in the entire twin. Company discloses the deal in its own 10-K, government confirms it in Parliament, production is verifiably running. Lead with this as the reference case for every other Tier-1/2 conversation — "here's what it looks like when it works." |
| **Suzuki Motor Corporation** | Twin #2: "growth investment...to meet growing demand in India" | Suzuki Motor Gujarat (Champion OEM) + Maruti Suzuki India (Component Champion) — two **separate** PLI-Auto approvals | The twin's single lead actually maps to two distinct approved legal entities. Expansion conversation: Kharkhoda (10 lakh PV/yr potential, ₹11,000cr phase 1, PMO-confirmed) is the live next-phase ask. |
| **Mitsubishi Electric Corporation** | Twin #3: AC/refrigeration strategy names India | PLI-Auto (Mitsubishi Electric Automotive India, Component Champion) **and** a separate 2016 M-SIPS approval (Haryana, automotive electronics) — same corporate family, two schemes, ten years apart | Longest-running double-confirmed relationship in the set — proof of durable commitment, not a one-off. |
| **Panasonic Holdings** | Twin #4: "India remains our top priority" (exec quote) | PLI White Goods beneficiary (AC + LED categories) | Matches the twin's qualitative signal with a hard capex program. |
| **LG Electronics** | Twin #8: NSE IPO Oct 2025, ~₹11,607cr, 54x subscribed | PLI White Goods (Korea) **+** three separate 2016 M-SIPS approvals (fridge, LED TV, washer, Maharashtra) | Doubly strong: fresh capital-markets validation (IPO) stacked on a decade of scheme participation. The IPO itself is worth opening with — it signals LG wants Indian public-market capital for further India expansion. |
| **Hyundai Motor Company** | Twin #9: ₹27,870cr IPO, "largest in India's history" | PLI-Auto Champion OEM; RHP shows Sriperumbudur at 97.1% utilisation | Utilisation ceiling + fresh capital-markets signal = the live expansion conversation is Talegaon, not a cold pitch. |
| **Kia Corporation** | Twin #10: Anantapur capacity 300k→350k | PLI-Auto Champion OEM | Matches exactly — expansion already disclosed and scheme-confirmed. |
| **Schaeffler AG** | Twin #27: ₹1,700cr invested 2022-24 + ₹4,500cr planned to 2030 | PLI-Auto Component Champion (Germany, majority-owned) | Best-quantified Component Champion case in the whole roster — a named forward capex number to cite in any conversation. |
| **Nokia Oyj** | Twin #38: Chennai 5G/Massive MIMO factory | PLI Telecom beneficiary — ₹166cr claimed / **₹157cr actually paid** | The only entry in this table where the government-side evidence includes a real disbursement figure, not just an approval. Strongest "this scheme genuinely pays out" reference case for Telecom. |
| **Hon Hai / Foxconn** | Twin #39: Foxconn Singapore raised India stake to 99.9%, $2.82bn cumulative | Landed three ways — Vama Sundari ISM unit (₹3,706cr), iPhone assembly Sriperumbudur, **₹357.17cr** PLI-LSEM disbursed | The most heavily cross-validated single entity in the entire system. Any Foxconn conversation should reference all three programmes. |
| **Pegatron Corporation** | Twin #40: Tata acquired 60% of Pegatron's Chennai iPhone plant, Jan 2025 | PLI-LSEM approved (Taiwan) | 🔑 **Synthesis finding not visible in either source alone**: Tata Electronics has now acquired *two* separate Apple-assembly operations — Wistron's plant (per the beneficiary roster's note that the Wistron PLI-LSEM entity was renamed to a Tata Electronics subsidiary) **and** Pegatron's Chennai plant (per this twin lead). Tata is consolidating India's iPhone assembly base under one domestic owner. Worth its own line of inquiry: is a third acquisition (of the remaining independent assembler) plausible? |
| **PSMC (Powerchip)** | Twin #59: "Tata Electronics has completed the Definitive Agreement with PSMC," Sept 2024 | ISM fab partner on the ₹91,526cr TEPL Gujarat project — 72% of the entire semiconductor programme's value | Twin supplies the founding-document date; roster supplies the confirmed capex scale. Together: the largest single relationship in India's semiconductor programme, fully dated and fully costed. |
| **Elbit Systems** | Twin #52: 20-F discloses the Adani-Elbit JV, Hyderabad UAV complex | One of only **3** confirmed defence-indigenisation JVs in any government record (the others: IRRPL/Russia, Tata-Airbus/Spain) | Doubly confirmed from Elbit's own regulatory filing (20-F) and the PLI Drones approved-applicant list. Given how thin confirmed defence JVs are generally (Part 7E of the beneficiary doc — the "45 JVs" figure has no published names), this is disproportionately valuable evidence. |

## Tier A — Scheme-landed, not separately disclosure-mined

Real government approval that the filing-mining methodology structurally couldn't catch — mostly Component Champions and mid-cap suppliers who don't get individual India mentions in a parent's 10-K/annual report, or JV entities whose India presence is buried inside a larger corporate filing.

**All 64 PLI-Auto Component Champions not listed above** are in this tier by default — Aisin, Daicel, Musashi, Nidec, Toyota Industries Engine, Toyota Kirloskar Auto Parts, Yazaki (Japan); Bosch ×2, BASF, Hella, Mahle, Vitesco, Valeo, Wabco/ZF (Germany); Aptiv ×2, Cummins, Dana ×2, Garrett (US); HL Mando (Korea). None of these appear in `LEADS.md`'s 321-company scan — worth checking whether the yfinance/10-K methodology could be extended to Tier-1 auto suppliers specifically (many are private/subsidiary entities with no standalone 10-K, which is likely *why* they're absent, not an oversight).

Also in this tier: the **medical devices bench** (Philips, Siemens Healthcare, Varex, Nipro, Omron, GE-BE) — none scored in `LEADS.md`'s 16-lead Medical Devices section except Philips (twin #26) — Siemens Healthcare, Varex, Nipro and Omron are real PLI Medical Devices beneficiaries with **zero** presence in the disclosure-mined lead list. **Recommend a targeted layer-16 rescan for these four names specifically** — their absence looks like a coverage gap in the filing sweep, not an absence of India interest (both hold disbursed incentive money, which by definition means active India operations).

## Tier B — Disclosed interest, no scheme presence found

Real, twin-sourced signal, but the beneficiary roster found no matching government approval — genuine warm-to-cold leads, not corrections.

- **AstraZeneca, Croda, Sanofi, Novo Nordisk, Bayer** (twin's Pharma & Bulk Drugs section) — none appear in the 55-company PLI Pharmaceuticals list. Real Indian operations (subsidiaries, capex), just not through this particular incentive channel — worth checking PLI Bulk Drugs (48 projects, no named list published) or Bulk Drug Parks (zero tenants — see the beneficiary doc's Part 5E) before assuming no incentive relationship exists at all.
- **Rolls-Royce, Safran, Thales, Dassault Aviation, Leonardo, Saab, CAE, Embraer, Hanwha Aerospace, Kongsberg, Indra Sistemas** (Aerospace & Defence) — strong disclosed interest, **zero** overlap with the 3 confirmed defence JVs. This is the largest Tier-B cluster in the system: eleven real companies with real India activity, and the government's own defence-indigenisation record names almost none of them by JV partner. Confirms the beneficiary doc's finding (Part 7E) that defence JV disclosure is structurally the weakest coverage in the whole PLI landscape — not a research gap, a genuine government transparency gap.
- **🚩 LG Energy Solution** (twin's White Goods & Electricals section, score 90, evidence: "non-binding agreement with JSW Energy for a 50:50 India battery JV") — **flag this entry directly**. The beneficiary doc's battery section (Part 4) is built on an exhaustive 3,766-document sweep that found **zero** government mentions of LG anywhere in India's battery record, and confirmed JSW's only battery-scheme appearance is a *losing* Waitlist-4 bid. The twin's own evidence is honestly hedged ("non-binding," scored MEDIUM not HIGH) so this is not a twin error — but any future use of this lead should carry the caveat: **neither party holds a PLI-ACC award, and the JV, if real, sits entirely outside the government incentive system as currently structured.** Do not let this entry's presence in a "leads" file imply government backing.

## Tier C — Open doors: neither dataset has anything, which is the point

Filing-mining finds nothing because no company has committed yet. Government records show nothing because nobody has won yet. This is where first-mover advantage is real and undiluted by existing competition — and it is invisible to Layer 16 by construction.

- **Rare Earth Magnet scheme** (₹7,280cr, up to 5 slots) — technical bids opened 13.08.2026, zero beneficiaries as of the beneficiary doc's research date. **Recommend actively sourcing Japanese magnet makers (Shin-Etsu, TDK, Hitachi Metals/Proterial) or German (VAC)** even without prior disclosed India interest — precisely because disclosed interest doesn't yet exist for anyone in this scheme.
- **SPMEPCI** (EV import-duty-for-local-manufacturing) — zero applications as of the 21.10.2025 deadline. Any EV OEM without existing India manufacturing is a live target; VinFast has reportedly signalled intent to re-apply.
- **Telangana's 3 unnamed semiconductor proposals** (1 fab, 2 OSAT) — a state actively seeking an anchor, currently without one, applicants undisclosed even to Parliament.
- **MPMS** (₹62,500cr, the PLI-LSEM successor, Cabinet-approved July 2026) — too new for any applicant to exist yet. Worth flagging in layer 28 (policy watchlist) as an imminent-graduation item to monitor for the first beneficiary announcement.

## Country-level cross-validation against layer 35 (capital-cost arbitrage)

Layer 35 prioritizes sweep targets by policy-rate gap × existing lead thinness, using an entirely separate methodology (bond-market rate arbitrage) from the beneficiary roster (scheme approvals). Where both agree independently, confidence compounds; where they diverge, that's diagnostic.

| Country | Layer 35 finding | Beneficiary-roster finding | Read |
|---|---|---|---|
| **Japan** | 12 leads (COVERED), IPA source yes, 4.25pt rate gap | Deepest PLI-Auto bench of any country (8+ distinct companies across Champion OEM + Component Champion) + PLI White Goods (Daikin, Panasonic, Mitsubishi Electric, JCH) + ISM's Renesas/CG Power OSAT | **Independent confirmation.** Two unrelated methodologies (rate arbitrage, scheme approval) both rank Japan top. Highest-confidence country in the entire system. |
| **South Korea** | 12 leads (COVERED), IPA yes, 2.75pt gap | Hyundai/Kia/HL Mando (PLI-Auto); Samsung/LG (PLI-LSEM, M-SIPS, White Goods); Hanwha/POSCO (twin-only, defence/steel) | **Confirmed second-strongest.** Every major twin lead in Korea maps to at least one real scheme approval. |
| **Germany** | 7 leads (MODERATE), IPA yes, 3.0pt gap | Bosch/BASF/Hella/Mahle/Schaeffler/Vitesco/Valeo/Wabco (PLI-Auto, 8 distinct entities) + Siemens Healthcare (Med Devices) | Roster shows Germany's bench is actually *deeper* than layer 35's "MODERATE" tag suggests — recommend upgrading Germany's sweep priority. |
| **Switzerland** | **Top rate-gap opportunity (5.25pt), but only 3 leads, no IPA source — flagged as the biggest gap** | **Zero landed entries in any of the 9 schemes harvested.** No Swiss company appears in PLI-Auto, ISM, Pharma, Medical Devices, Electronics, or Renewables/Green beneficiary lists. | **Independent confirmation of a genuine gap, not a coverage artifact.** Two unrelated methodologies agree Switzerland is underrepresented. This is the single clearest "go build a discovery sweep here" signal in the combined system — ABB and Sika (twin leads, Auto & Components) are the only disclosed-interest anchors to build outward from. |
| **United States** | 75 leads (deepest coverage), IPA yes, but only 1.63pt gap (weakest rate advantage) | Micron (ISM), Varex/Nipro-adjacent US medtech names, Cummins/Aptiv/Dana/Garrett (PLI-Auto), Jabil/Commscope/Sanmina-SCI (PLI-Telecom) | Confirms the expected pattern: deepest lead coverage, weakest capital-cost argument. US companies come to India for market size and supply-chain diversification, not cheap capital — a different pitch than the yen-carry framing that works for Japan. |

## Recommended 90-day approach list (drawing on all four tiers)

Ranked by combined confidence, not just score:

1. **Micron** — Tier S. Phase-2 conversation, not a cold pitch.
2. **Nokia** — Tier S. The only entry with confirmed disbursement; strongest "the scheme pays out" reference for a Telecom-sector pitch to a peer (e.g. Ericsson, also a twin Tier-1 lead but without confirmed disbursement evidence).
3. **A named Japanese magnet maker (Shin-Etsu/TDK/Hitachi Metals-Proterial)** — Tier C. Zero competition, bids open now.
4. **Schaeffler** — Tier S. Best-quantified forward capex commitment (₹4,500cr to 2030) to build an expansion conversation around.
5. **Siemens Healthcare, Varex, Nipro, Omron** — Tier A. Confirmed beneficiaries the twin's own methodology is currently blind to; low-effort, high-confidence outreach once contact-enriched via the existing layer-16 pipeline (Lusha/Apollo).
6. **A Swiss company beyond ABB/Sika** — Tier C, country-level. Both methodologies agree this is the clearest sweep gap in the system; worth a dedicated EDINET-style filing sweep for Swiss SIX-listed companies (no sweep script exists yet for Switzerland, per the README's filing-discovery-channels section).
7. **Any Aerospace & Defence twin lead (Rolls-Royce, Safran, Thales, Saab)** — Tier B. Real disclosed interest; the government's own JV-naming gap means these conversations have to be built from the company side, not verified from the government side first.

## What should propagate back into the twin

- `docs/LEADS.md` / `layers/16_leads.json`: the LG Energy Solution entry should carry an explicit "no PLI-ACC award; JV non-binding" caveat rather than sitting at a bare MEDIUM score with no scheme-status context.
- Any future addition to `data/companies.db` (layer 32) naming **Daiichi Sankyo**, **SK Hynix** (as an India semiconductor manufacturer), **Samsung** (specifically re: a Hyderabad fab), or **LG Energy Solution** (as a PLI-ACC beneficiary) should be checked against the "Standing corrections" section of `PLI_SCHEME_BENEFICIARY_LEADS.md` before being trusted — these are the four most widely-circulated errors this session's research found and refuted against the primary record.
- Consider a targeted layer-16 rescan for Siemens Healthcare, Varex Imaging, Nipro, and Omron (Tier A above) — real beneficiaries currently invisible to the disclosure-mining sweep.
