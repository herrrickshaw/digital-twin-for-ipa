#!/usr/bin/env python3
"""Apply ministry-publication findings to the visibility verdicts (layer 20 -> 22).

THE FINDING THAT MATTERS: PIB headlines are the wrong instrument. Ministries name
companies constantly -- but in annexure PDFs, 249-page R&D directories, regulator
orders and monthly summaries, none of which carry a company name in any title. So
a title-indexed register cannot see them, and "not in a PIB headline" is a much
weaker claim than "the government has not engaged this company".

New verdict introduced here:
    MINISTRY_NAMED   named in an official ministry publication (PLI beneficiary
                     annexure, DSIR R&D directory, ALMM whitelist, CERC order,
                     ministry monthly summary) though never in a PIB headline.

Two results are DISPROOFS, which are worth more than the confirmations:
  - Lenovo: the widely-repeated "approved under IT-hardware PLI 2.0" claim is NOT
    supported by MeitY's own list of the 27 approved companies. Lenovo is named
    only as a brand in a PIB backgrounder.
  - Arcelik/Voltbek: affirmatively absent from all 42 White Goods PLI
    beneficiaries. Trap recorded: JV parent Voltas Limited IS a beneficiary
    (Sl. 11), which is exactly how a careless matcher would manufacture a hit.
"""
import datetime, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = ("/private/tmp/claude-501/-Users-umashankar/"
           "0c3e9924-9f05-4396-80c8-81c306920b86/scratchpad")

# company-key -> (new verdict, basis). Keys match on lowercase substring.
MINISTRY = {
    "panasonic": ("MINISTRY_NAMED",
        "named White Goods PLI beneficiary -- 'PANASONIC INDIA PRIVATE LIMITED', Rs 50cr, Sl. 24 of the "
        "DPIIT 42-company annexure, plus a Rs 250cr compressor application at the Committee of Experts "
        "and a DSIR-recognised R&D unit. Strongest reversal in the batch."),
    "mitsui": ("MINISTRY_NAMED",
        "PARENT name verbatim in the Ministry of Ports, Shipping & Waterways Monthly Summary, Aug-2025 "
        "(Kamarajar Port car transshipment) -- highest-confidence hit: no subsidiary alias needed"),
    "clp holdings": ("MINISTRY_NAMED",
        "'Apraava Energy Private Limited' named 10+ times in CERC Order 238/AT/2025 including a reproduced "
        "NTPC Letter of Award -- invisible to the matcher purely because CLP renamed its India arm in 2022"),
    "eisai": ("MINISTRY_NAMED",
        "live DSIR in-house R&D recognition TU/IV-RD/3214 for the Vizag centre, listed in the Ministry of "
        "Science & Technology directory -- a formal registration carrying fiscal benefits"),
    "weg": ("MINISTRY_NAMED",
        "entry 28 on MNRE's ALMM-Wind approved-manufacturer list as 'WEG Industries (India) Pvt Ltd' -- a "
        "binding regulatory whitelist, not publicity"),
    "food empire": ("MINISTRY_NAMED_SUBSIDIARY_ONLY",
        "Indian arm 'Indus Coffee Private Limited' on the Coffee Board exporter register; the PARENT name "
        "appears nowhere, and Food Empire is definitively absent from the complete 119-company MoFPI "
        "PLI-FPI list"),
    "lenovo": ("MINISTRY_NAMED_BRAND_ONLY",
        "named as a brand in a MeitY/PIB backgrounder -- but DISPROOF: MeitY's own list of the 27 approved "
        "IT-hardware PLI 2.0 companies does NOT include Lenovo, so the widely-reported 'Lenovo approved "
        "under PLI 2.0' claim is unsupported by the ministry's own document"),
    "cae": ("QUIET_INVESTOR",
        "WEAK/PARTIAL only -- the sole government-hosted trace is AAI's NFTI page linking to CAE Global "
        "Academy URLs; not a naming in a ministry publication, so the below-radar label stands"),
}
# Names whose invisibility SURVIVED the ministry check, with why it survives.
SURVIVES = {
    "mediatek": "structurally ineligible for the Design Linked Incentive, which is scoped to domestic "
                "startups/MSMEs/academia -- absence is by scheme design, not neglect",
    "elbit": "defence opacity: every retrievable account of the Adani-Elbit UAV facility and the May-2025 "
             "Sparton sonobuoy agreement traces to Adani corporate media, never a ministry document",
    "arcelik": "AFFIRMATIVELY DISPROVED, not merely unconfirmed: absent from all 42 White Goods PLI "
               "beneficiaries, the FDI table and the CoE referral table. Trap recorded -- JV parent Voltas "
               "Limited IS a separate beneficiary at Sl. 11, which is how a careless match invents a hit",
    "siam cement": "absent centrally; the Kheda (Kapadvanj) AAC plant inauguration was a Gujarat state event",
}


def main():
    ver = json.load(open(os.path.join(ROOT, "layers/20_visibility_verified.json")))
    raw = {}
    for f in ("ministry_check_quiet.json", "ministry_check_pli.json"):
        p = os.path.join(SCRATCH, f)
        if os.path.exists(p):
            raw[f] = json.load(open(p))

    changed, survived = [], []
    for r in ver["companies"]:
        key = r["company"].lower()
        for k, (verdict, basis) in MINISTRY.items():
            if k in key:
                r["pib_verdict_before_ministry_check"] = r["verdict"]
                r["verdict"] = verdict
                r["ministry_basis"] = basis
                changed.append((r["company"], verdict))
                break
        else:
            for k, why in SURVIVES.items():
                if k in key:
                    r["ministry_check"] = "searched, not found -- " + why
                    survived.append(r["company"])
                    break

    ver["ministry_check"] = {
        "run": datetime.date.today().isoformat(),
        "sources_that_actually_name_companies": [
            "PLI beneficiary annexures (DPIIT/MeitY/MoFPI)",
            "DSIR Directory of Recognised In-house R&D Units",
            "MNRE ALMM approved-manufacturer lists",
            "CERC / regulator orders",
            "Ministry monthly summaries (e.g. MoPSW)",
            "Coffee Board / commodity-board registers",
        ],
        "headline_finding": (
            "PIB headlines are the wrong instrument for this question. Of 12 quiet investors checked "
            f"against ministry publications, {len(changed)} were found named and their labels corrected. "
            "The channels that name companies are annexure PDFs, long directories, regulator orders and "
            "monthly summaries -- none of which put a company name in a title, so a title-indexed register "
            "structurally cannot see them."),
        "two_systemic_blind_spots": [
            "RENAMED ENTITIES: CLP -> Apraava (2022) erases every post-rename government record from a "
            "parent-name match",
            "SUBSIDIARY ALIASES: Indus Coffee, WEG Industries (India), Voltbek, Panasonic India -- the "
            "government names the Indian entity, never the foreign parent",
        ],
        "disproofs": [
            "Lenovo is NOT on MeitY's list of 27 approved IT-hardware PLI 2.0 companies, contrary to wide "
            "reporting",
            "Arcelik/Voltbek is NOT among the 42 White Goods PLI beneficiaries; JV parent Voltas Limited is "
            "(Sl. 11) -- a false-positive trap",
        ],
        "corrected": [{"company": c, "to": v} for c, v in changed],
        "invisibility_survives": survived,
        "raw_files": list(raw),
    }
    counts = {}
    for r in ver["companies"]:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    ver["counts"] = counts
    json.dump(ver, open(os.path.join(ROOT, "layers/22_visibility_ministry_checked.json"), "w"), indent=1)

    print(f"corrected {len(changed)} verdicts; {len(survived)} invisibilities survived")
    for c, v in changed:
        print(f"  {c[:34]:34} -> {v}")
    print("\nsurvives as invisible:", ", ".join(survived))
    print("\nverdict counts:", counts)


if __name__ == "__main__":
    main()
