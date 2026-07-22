#!/usr/bin/env python3
"""Layer 24 — leads mined from the PARIVESH clearance registers, news-verified.

A NEW lead-generation channel, and a stronger one than announcement-scanning:
a company with a LIVE environmental/forest clearance filing is not merely
talking about investing -- it has paid fees, filed EIA paperwork and put a
site on record. The register is the intent; the news check tells us which of
these verified investors are in the public limelight and which are QUIET.

Pipeline (all 2025-26 filings, live statuses only):
  EC register (majorClearanceType=1, 113,981 rows) -> manufacturing activities
  only (metallurgy, cement, chemicals, pharma API, pesticides, fertilizer,
  petrochemicals...) -> corporate proponents (persons and govt agencies
  stripped) -> dedup against the 321 companies already in layers/16_leads.json
  -> top filers + foreign-linked FC filers (Jio-bp, Nayara/Rosneft, HMEL)
  -> 3-agent public-news sweep -> ANNOUNCED / PARTIALLY_VISIBLE / QUIET.

Inputs (scratchpad): clearance_lead_shortlist.json, news_batch{1,2,3}.json
Output: layers/24_clearance_leads.json
"""
import datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = ("/private/tmp/claude-501/-Users-umashankar/"
           "0c3e9924-9f05-4396-80c8-81c306920b86/scratchpad")


def norm(name):
    n = name.lower()
    # canonicalise legal-suffix variants so 'JSW Steel Ltd' == 'Jsw Steel Limited'
    n = re.sub(r"\b(limited|ltd\.?|private|pvt\.?|llp|the)\b", "", n)
    n = re.sub(r"\(.*?\)", "", n)  # drop parentheticals like '(Adani group)'
    return re.sub(r"[^a-z0-9]", "", n)[:24]


def main():
    short = json.load(open(os.path.join(SCRATCH, "clearance_lead_shortlist.json")))
    news = {}
    for f in ("news_batch1.json", "news_batch2.json", "news_batch3.json"):
        p = os.path.join(SCRATCH, f)
        if os.path.exists(p):
            for r in json.load(open(p)):
                news[norm(r["company"])] = r
    # CARE Ratings enrichment (rationales disclose capex/site/funding that never
    # reaches the press -- run for the QUIET + PARTIALLY_VISIBLE leads)
    care = {}
    cp = os.path.join(SCRATCH, "care_ratings.json")
    if os.path.exists(cp):
        for r in json.load(open(cp)):
            care[norm(r["company"])] = r

    leads, unmatched = [], []
    for s in short:
        n = news.get(norm(s["company"]))
        if n is None:  # fuzzy: try containment either way
            for k, v in news.items():
                if k[:12] in norm(s["company"]) or norm(s["company"])[:12] in k:
                    n = v
                    break
        rec = {
            "company": s["company"],
            "clearance_evidence": {
                "filings_2025_26": s["filings"],
                "activities": s.get("activities", {}),
                "states": s.get("states", {}),
                "latest_filing": s["latest_filing"],
                "register": s.get("source", "EC register"),
            },
        }
        if s.get("note"):
            rec["note"] = s["note"]
        if n:
            rec["news_verdict"] = n.get("verdict")
            rec["news_summary"] = n.get("news_summary")
            rec["match_with_filings"] = n.get("match_with_filings")
            rec["best_source_url"] = n.get("best_source_url")
            if n.get("announced_capex_rs_cr"):
                rec["announced_capex_rs_cr"] = n["announced_capex_rs_cr"]
        else:
            rec["news_verdict"] = "UNCHECKED"
            unmatched.append(s["company"])
        c = care.get(norm(s["company"]))
        if c is None:
            for k, v in care.items():
                if k[:12] in norm(s["company"]) or norm(s["company"])[:12] in k:
                    c = v
                    break
        if c:
            rec["credit_rating"] = {
                "rated_by_care": c.get("rated_by_care"),
                "rating": c.get("rating"),
                "rating_date": c.get("rating_date"),
                "rationale_capex_disclosure": c.get("rationale_capex_disclosure"),
                "rationale_url": c.get("rationale_url"),
                "adds_beyond_news": c.get("adds_beyond_news"),
            }
        leads.append(rec)

    for r in leads:
        r["tier"] = 1

    # ---- tier 2: next slice of the pool (2-3 filings, July-2026 recency,
    # sector-diversity capped). Agents did news + rating in ONE pass.
    t2p = os.path.join(SCRATCH, "tier2_shortlist.json")
    if os.path.exists(t2p):
        t2v = {}
        for f in ("tier2_verify1.json", "tier2_verify2.json", "tier2_verify3.json"):
            p = os.path.join(SCRATCH, f)
            if os.path.exists(p):
                for r in json.load(open(p)):
                    t2v[norm(r["company"])] = r
        for s in json.load(open(t2p)):
            v = t2v.get(norm(s["company"]))
            if v is None:
                for k, vv in t2v.items():
                    if k[:12] in norm(s["company"]) or norm(s["company"])[:12] in k:
                        v = vv
                        break
            rec = {"company": s["company"], "tier": 2,
                   "clearance_evidence": {"filings_2025_26": s["filings"],
                                          "activities": s.get("activities", {}),
                                          "states": s.get("states", {}),
                                          "latest_filing": s["latest_filing"],
                                          "register": "EC register"}}
            if v:
                rec["news_verdict"] = v.get("verdict")
                rec["news_summary"] = v.get("news_summary")
                rec["best_source_url"] = v.get("best_source_url")
                if v.get("announced_capex_rs_cr"):
                    rec["announced_capex_rs_cr"] = v["announced_capex_rs_cr"]
                if v.get("note"):
                    rec["note"] = v["note"]
                rec["credit_rating"] = {"rating": v.get("rating"),
                                        "rationale_capex_disclosure": v.get("rationale_capex_disclosure")}
            else:
                rec["news_verdict"] = "UNCHECKED"
                unmatched.append(s["company"])
            leads.append(rec)

    # ---- tier 3: POLICY-ALIGNED slice of the remaining ~1,384 pool. The whole
    # remainder was triaged locally against live policy programs (see
    # layers/24b_pool_policy_triage.json); agents verified the top-40 slice.
    t3p = os.path.join(SCRATCH, "tier3_shortlist.json")
    if os.path.exists(t3p):
        t3v = {}
        for f in ("tier3_verify1.json", "tier3_verify2.json", "tier3_verify3.json", "tier3_verify4.json"):
            p = os.path.join(SCRATCH, f)
            if os.path.exists(p):
                for r in json.load(open(p)):
                    t3v[norm(r["company"])] = r
        for s in json.load(open(t3p)):
            v = t3v.get(norm(s["company"]))
            if v is None:
                for k, vv in t3v.items():
                    if k[:12] in norm(s["company"]) or norm(s["company"])[:12] in k:
                        v = vv
                        break
            rec = {"company": s["company"], "tier": 3,
                   "policy_program": s.get("policy_program"),
                   "clearance_evidence": {"filings_2025_26": s["filings"],
                                          "activities": {s.get("activity"): s["filings"]},
                                          "states": s.get("states", {}),
                                          "latest_filing": s["latest"],
                                          "register": "EC register"}}
            if v:
                rec["news_verdict"] = v.get("verdict")
                rec["news_summary"] = v.get("news_summary")
                rec["best_source_url"] = v.get("best_source_url")
                if v.get("announced_capex_rs_cr"):
                    rec["announced_capex_rs_cr"] = v["announced_capex_rs_cr"]
                if v.get("pli_status") and v["pli_status"] != "not surfaced":
                    rec["pli_status"] = v["pli_status"]
                if v.get("note"):
                    rec["note"] = v["note"]
                rec["credit_rating"] = {"rating": v.get("rating"),
                                        "rationale_capex_disclosure": v.get("rationale_capex_disclosure")}
            else:
                rec["news_verdict"] = "UNCHECKED"
                unmatched.append(s["company"])
            leads.append(rec)

    # ---- CARE-specific pass on the tier-3 policy targets that lacked confirmed
    # CARE coverage. "CARE does not rate" is recorded -- it tells us which
    # verification channel is authoritative per name.
    cp3 = os.path.join(SCRATCH, "care_tier3.json")
    if os.path.exists(cp3):
        c3 = {norm(r["company"]): r for r in json.load(open(cp3))}
        for r in leads:
            c = c3.get(norm(r["company"]))
            if c is None:
                for k, v in c3.items():
                    if k[:12] in norm(r["company"]) or norm(r["company"])[:12] in k:
                        c = v
                        break
            if c:
                cc = {"care_rates_it": c["care_rates_it"], "delta_vs_other_agency": c.get("delta")}
                for f in ("care_rating", "care_date", "highlights", "url"):
                    if c.get(f):
                        cc[f] = c[f]
                r.setdefault("credit_rating", {})["care_check"] = cc

    counts = {}
    for r in leads:
        counts[r["news_verdict"]] = counts.get(r["news_verdict"], 0) + 1
    out = {
        "layer": 24,
        "name": "clearance_register_leads",
        "built": datetime.date.today().isoformat(),
        "method": ("PARIVESH EC/FC registers (2025-26 filings, live statuses, manufacturing "
                   "activities, corporate proponents only, deduped against layer 16's 321 leads) "
                   "-> public-news sweep -> visibility verdict -> CREDIT-RATING enrichment "
                   "(CARE Ratings first, CRISIL/ICRA/India Ratings where CARE does not rate). "
                   "A clearance filing is stronger evidence of intent than an announcement: fees "
                   "paid, EIA filed, site on record. Rating rationales are the third channel: for "
                   "unlisted/quiet companies they are often the ONLY document quantifying the "
                   "capex, site and funding mix behind the filings."),
        "sources": ["PARIVESH 2.0 EC register (majorClearanceType=1) + FC register (=2)",
                    "public news (3-agent WebSearch sweep, 2025-26)",
                    "CARE Ratings rationales (careratings.com) -- CRISIL/ICRA/India Ratings "
                    "used where CARE does not rate the entity, flagged as such"],
        "why_quiet_matters": ("QUIET = verified investment intent with NO public announcement -- "
                              "the same below-radar category the PIB-visibility work found most "
                              "valuable for investment-promotion targeting."),
        "verdict_counts": counts,
        "recommendations": {
            "A_immediate_outreach_quiet_verified": {
                "why": ("QUIET = paid-up clearance filings with zero press. Nobody else's lead list has "
                        "these names; first-mover advantage for state investment-promotion agencies is "
                        "total. Rank within the bucket by capital-in-evidence."),
                "ranked": [
                    "Swarup Steel Industries (UP) -- Rs 35 cr paid-up, near-zero revenue: an equity-funded "
                    "greenfield metallurgy build; UP should be at their door before ground-breaking",
                    "Minakshi Agro Industries LLP (Latur, MH) -- 3 filings, multi-unit ethanol in the sugar "
                    "belt, Rs 150-250 cr class, zero press",
                    "Rexxon Speciality Chemical LLP (Rajkot, GJ) -- Jan-2025 LLP already 4 filings; the "
                    "filings are its ONLY public record",
                    "Amur Spirits + Rajdheer Wine (Deola/Bhilwad, Nashik) -- same-village promoter cluster "
                    "moving from wine into distillation; treat as ONE lead",
                    "SRK Organics (TG-registered, filing in Karnataka) -- pre-public greenfield; both states "
                    "have a claim, Karnataka holds the site",
                    "Hemanjali Polymers, Krishmah Lifesciences (Rs 19 cr MPCB-disclosed), Valeshvar Bio Tech, "
                    "Sandhya Organic (expanding with NO live rating), Bagul Exim, Siddharth Speciality, "
                    "Vantage Chemical, Paras Croplife, Galaxy Dyestuff -- the small-cap chemicals tail; "
                    "cluster outreach via GIDC/MIDC estates beats company-by-company",
                ]},
            "B_state_mismatch_unannounced_legs": {
                "why": ("The filings reveal a next plant in a state the company has NOT announced -- the "
                        "state that moves first shapes siting, incentives and timing."),
                "ranked": [
                    "JK Lakshmi Cement -> WEST BENGAL (11 filings; CARE rationale's Rs 2,500 cr program has "
                    "four unnamed grinding units 'awaiting clearances' -- WB is the likely home)",
                    "Ambuja Concrete North (Adani) -> MAHARASHTRA (13 filings; all press is Bihar)",
                    "Bharat Rasayan -> GUJARAT expansion NOT in its rating case; 0.08x gearing funds it "
                    "quietly",
                    "Matrix Pharmacorp -> TELANGANA (news is all Vizag/AP)",
                    "Deepak Nitrite -> TELANGANA (Jeedimetla; outside the headline Rs 11,000 cr program)",
                ]},
            "C_foreign_linked_fdi_relevant": {
                "why": "Direct FDI-promotion targets with verified land/clearance activity.",
                "ranked": [
                    "Kansai Nerolac (Kansai Paint, JAPAN) -- Sayakha/Bawal expansions, self-funded from "
                    "Rs 2,000+ cr cash; anchor tenant for Gujarat's Japan corridor",
                    "TruAlt Bioenergy x Sumitomo (JAPAN) -- 16 CBG plants planned from 2026; the clearance "
                    "trail will show siting before announcements",
                    "ArcelorMittal Nippon Steel (LUX/JAPAN) -- Hazira Rs 60,000 cr underway",
                    "Reliance BP Mobility (BP, UK) -- 58 land filings; HMEL (Mittal) Bathinda Rs 2,600 cr",
                    "Viyash (Carlyle, US) + Anjan Drug (PE-held) -- sponsor-funded pharma capacity",
                    "CAUTION: Nayara (Rosneft) is on CARE Rating Watch Negative post-sanctions -- engage "
                    "only with sanctions-compliance review",
                ]},
            "D_early_signals_read_throughs": [
                "Alok Ferro Alloys filings = Godawari Power & Ispat (GPIL) capex before announcement -- "
                "listed-market read-through",
                "Shakambhari Ispat: Mar-2025 rationale says capex DONE, Jul-2026 filings say NEW phase -- "
                "ahead of agency coverage",
                "Bhor Chemicals (Nashik, est. 1943): pivot into carbon-fiber prepregs/laminates for "
                "aerospace/UAV -- defence-supply-chain relevance beyond its size",
                "IMFA: ferro-alloys major building a Rs 160 cr grain-ethanol plant on surplus land -- "
                "heavy industry monetising land banks via ethanol is a pattern to watch",
                "Shree Cement Meghalaya: board approval and EC filings in the SAME month -- clearance "
                "registers track board decisions in near-real-time",
            ],
            "F_policy_aligned_targets_tier3": {
                "why": ("Tier 3 = the policy-weighted top-40 of the remaining pool (full triage in layer "
                        "24b). Targets grouped by the policy instrument they validate."),
                "api_ksm_pli_china_substitution": [
                    "Orchid Pharma -- the ONLY confirmed KSM/API-PLI beneficiary found (Rs 600 cr 7-ACA, "
                    "J&K): but land delays + Apr-2026 downgrade = the scheme's flagship is its biggest "
                    "execution risk; needs hand-holding, not celebration",
                    "IOL Chemicals (Rs 1,220 cr Barnala) + Farmson (PAP at Jhagadia) -- paracetamol chain "
                    "localisation happening WITHOUT PLI participation surfacing: the market is doing the "
                    "scheme's job",
                    "Anthem Biosciences (~Rs 1,700 cr, explicitly pitched as China alternative), Aarti "
                    "Pharmalabs (Rs 450 cr CDMO), Piramal (Rs 890 cr/yr), Virupaksha (Rs 740 cr IPO), "
                    "Aarti Drugs -- the China+1 CDMO/API buildout is broad and self-funded",
                    "Sharika Life Science (QUIET; semi-synthetic penicillin -- the most China-dependent "
                    "fermentation chain) -- exactly the profile KSM-PLI was built for, invisible to it"],
                "import_substitution_chemicals": [
                    "Lanxess (GERMANY, Rs 750 cr cumulative Jhagadia, more signalled) and SRF (Odisha "
                    "Rs 2,300 cr of a Rs 10,000 cr pledge -- the pesticide filings are the agrochem leg's "
                    "leading indicator)",
                    "Indo Amines -- expansion explicitly framed by the company as import-reduction",
                    "Jayshree Aromatics -- ~19x capacity jump visible ONLY in EC documents; largest "
                    "disclosure gap found",
                    "WBCIL -- Kolkata API maker expanding in Dahej (the WB-named-Gujarat-filing mystery)"],
                "ethanol_blending_programme": [
                    "Keyaan (Rs 1,200 cr Gorakhpur, 300->500 KLPD path), Kamakhya (Assam Rs 371 cr, NE's "
                    "rare EBP asset), RSLD (Chhattisgarh Rs 200 cr, paddy-surplus play), Bannari Amman "
                    "(AA-, self-funded E20 expansion), Bapuna (IG group building through unrated SPV)",
                    "CAUTION on activity tags: Mowa + Mahunza are Maharashtra MAHUA heritage-liquor "
                    "ventures, NOT fuel ethanol -- 'distillery' filings need feedstock disambiguation"],
                "textiles_mmf_pli": [
                    "HS Hyosung (KOREA -- world #1 spandex + tyre cord; ~Rs 3,000 cr cumulative, two "
                    "Maharashtra sites) and Grasim (Gujarat filings = the quiet Vilayat leg, distinct from "
                    "the announced Rs 3,094 cr Karnataka lyocell)"],
                "risk_flags": [
                    "Sigachi: two-notch post-accident downgrade; AP filing is diversification, not recovery",
                    "Matangi: went ISSUER-NOT-COOPERATING the same quarter it filed pesticide ECs",
                    "Atharv Intertrade: B+ credit attempting a 7.5x distillery scale-up",
                    "Shiva Pharmachem: accident + Negative outlook + OFS-only IPO (no fresh capex money)"],
                "policy_reading": ("Two systemic findings: (1) the paracetamol/API localisation wave is "
                                   "largely happening OUTSIDE the PLI frame -- self-funded balance sheets, "
                                   "not scheme money, are driving China-substitution; (2) the one confirmed "
                                   "PLI flagship (Orchid 7-ACA) carries the worst execution profile in the "
                                   "cohort -- scheme administrators should treat land assembly, not "
                                   "incentive size, as the binding constraint.")},
            "E_process": [
                "Wire refresh_ec.py + this pipeline into the quarterly reportage cycle -- July-2026 "
                "filings were visible here months before any press",
                "Join the 1,445-company pool against DPIIT IEM proponents to measure who files both",
                "Monitor certificateUrl on tracked proposals: grant events = trigger for outreach",
                "~1,387 pool companies remain untriaged below tier 2",
            ],
        },
        "leads": leads,
        "unmatched_in_news_sweep": unmatched,
        "candidate_pool": {"ec_corporate_filers_2025_26": 1445,
                           "after_dedup_vs_layer16": 1723,
                           "note": ("shortlist is the TOP of a 1,445-company pool of live corporate "
                                    "industrial filers -- the pool file (scratchpad ec_lead_candidates.json) "
                                    "supports deeper batches")},
    }
    p = os.path.join(ROOT, "layers/24_clearance_leads.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"layer 24: {len(leads)} leads | verdicts {counts} | unmatched {len(unmatched)}")


if __name__ == "__main__":
    main()
