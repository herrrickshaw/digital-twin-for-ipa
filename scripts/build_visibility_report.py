#!/usr/bin/env python3
"""Render the visibility findings as docs/VISIBILITY.md (generated -- never hand-edit).

Answers the question the layers were built for: of the foreign companies with
verified India intent, which ones does the government put in its headlines, and
which are investing without any publicity at all?

Sources: layers/19_pib_visibility.json (PIB headline match, 3-year window)
         layers/20_visibility_verified.json (trade-press verification of the
         below-radar names, with corrections applied)

    python3 scripts/build_visibility_report.py
"""
import datetime, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLURB = {
 "QUIET_INVESTOR": ("Quiet investors — the outreach list",
    "Dated, sourced India activity in the last three years and **no government publicity found at all**: "
    "not a PIB headline, not a minister at the ribbon-cutting, not a state-government announcement. "
    "These are companies committing capital to India that the government is not currently courting."),
 "SUBSUMED_IN_PARTNER": ("Invisible by construction — the publicity names the Indian principal",
    "These firms sit inside projects the government promotes *heavily* — but the announcements name the "
    "Indian principal (Tata Electronics, the India Semiconductor Mission, SAIL), never the foreign supplier. "
    "They are not being ignored; they are structurally unnameable in the current announcement format. "
    "The same mechanism is visible in the register itself: Nippon Steel surfaces only as *ArcelorMittal "
    "Nippon Steel India*, and CLP only as *Apraava Energy*."),
 "STATE_PUBLICISED": ("Publicised by a state, invisible at the centre",
    "Real activity that a **state government amplified** — land allotted and announced, a Chief Minister at "
    "the ground-breaking — while no PIB headline ever named the firm. This is a centre-versus-state "
    "visibility gap, not stealth, and it says something about which door these investors came through."),
 "HEADLINED": ("Already courted — corrections to the PIB match",
    "The PIB title match filed these as below-radar and the news check proved it wrong. Recorded here with "
    "the evidence, because the register indexes release *titles* only and these cases are exactly where "
    "that limit bites."),
 "BLOCKED_PN3": ("Press Note 3 cohort — absence has a different cause",
    "Chinese-domiciled names. Their absence from Indian government headlines is not modesty: their India "
    "activity is refusal, exclusion, or Indianisation of ownership. **None of this is inbound investment** "
    "and none of it is an outreach opportunity."),
 "DIRECTION_INBOUND": ("Flow runs the other way",
    "The traceable activity is India reaching for the company's assets abroad, not the company investing in "
    "India. Worth tracking, wrong list for investment promotion."),
 "NO_ACTIVITY": ("Intent stated, not yet converted",
    "The annual report expresses India or APAC interest, but no dated India activity surfaced inside the "
    "three-year window — or the only commitment predates it. Intent has not become capex."),
}


def main():
    vis = json.load(open(os.path.join(ROOT, "layers/19_pib_visibility.json")))
    ver = json.load(open(os.path.join(ROOT, "layers/20_visibility_verified.json")))
    today = datetime.date.today().isoformat()

    L = [f"# Visibility map — who the government announces, and who invests quietly", "",
         f"*Generated {today} by `scripts/build_visibility_report.py` from "
         f"`layers/19_pib_visibility.json` + `layers/20_visibility_verified.json` — do not hand-edit.*", "",
         "## What this is", "",
         f"Every company in the leads layer, matched against **{vis['register']}** over "
         f"the window **{vis['window']}**, then — for those the government never headlined — checked "
         "against trade press for what they are actually doing in India.", "",
         "**Read the method before the numbers.** The PIB register stores release *titles*, not bodies. "
         "A company named inside a release but not in its headline reads as absent here. So this measures "
         "**headline attention**, and it understates total government contact — two names in this report "
         "(Cameco, Ma'aden) were proven publicised once the news check ran, and their corrections are shown "
         "rather than quietly patched. The asymmetry is still the point: PIB headlines name firms when the "
         "government wants credit for the investment.", ""]

    L += ["## The split", "", "| Bucket | Count | Meaning |", "|---|---|---|"]
    meaning = {"ANNOUNCED": "named in an investment-related PIB headline",
               "MENTIONED_ONLY": "named only incidentally (condolences, unrelated merger clearances)",
               "HISTORIC": "named only before the window",
               "BELOW_RADAR": "never named in a PIB headline",
               "UNMATCHABLE": "name too generic to match safely (reason recorded per company)"}
    for k, v in sorted(vis["counts"].items(), key=lambda kv: -kv[1]):
        L.append(f"| {k} | {v} | {meaning.get(k,'')} |")
    L += ["", f"Of the {len([r for r in vis['all'] if r['india_intent'] in ('HIGH','MEDIUM')])} companies "
              f"with HIGH or MEDIUM India intent in their own annual reports, "
              f"**{len(vis['announced'])} appear in an investment-related PIB headline** and "
              f"**{len(vis['below_radar'])} never do**.", ""]

    L += ["## Who the government does headline", "",
          "| PIB investment headlines (3y) | Company | Country | Most recent release |", "|---|---|---|---|"]
    for r in vis["announced"][:14]:
        rel = r["releases"][-1] if r["releases"] else {}
        t = (rel.get("title") or "")[:78].replace("|", "/")
        d = rel.get("date", "")
        p = rel.get("prid")
        link = f"[{d}](https://www.pib.gov.in/PressReleasePage.aspx?PRID={p}) {t}" if p else t
        L.append(f"| {r['pib_investment_hits_3y']} | {r['company'][:34]} | {r['country']} | {link} |")
    L += ["", "The pattern is narrow: semiconductors, defence, and marquee PM-attended ribbon-cuttings.", ""]

    order = ["QUIET_INVESTOR", "SUBSUMED_IN_PARTNER", "STATE_PUBLICISED", "HEADLINED",
             "BLOCKED_PN3", "DIRECTION_INBOUND", "NO_ACTIVITY"]
    L += ["## Verified against the trade press", "",
          f"The {len(ver['companies'])} below-radar names with the strongest stated intent were checked "
          "against dated news. Absence from PIB headlines turns out to have four different causes — only "
          "one of them is an opportunity.", ""]
    for verdict in order:
        rows = [r for r in ver["companies"] if r["verdict"] == verdict]
        if not rows:
            continue
        title, blurb = BLURB[verdict]
        L += [f"### {title} ({len(rows)})", "", blurb, ""]
        for r in rows:
            head = f"**{r['company']}** ({r['country']}"
            if r.get("sector"):
                head += f", {r['sector']}"
            head += ")"
            L.append(head)
            if verdict == "HEADLINED":
                L.append(f"- **Correction**: {r['verdict_basis']}")
            for n in r["india_news"][:3]:
                fig = f" — {n['figure']}" if n.get("figure") else ""
                url, hl = n.get("url"), (n.get("headline") or "")[:110]
                L.append(f"- {n.get('date','')}: " + (f"[{hl}]({url})" if url else hl) + fig)
            if r.get("summary"):
                L.append(f"- *{r['summary'][:260]}*")
            L.append("")

    L += ["## How to use this", "",
          "The **quiet investors** are the actionable list: they are spending money in India now, and no arm "
          "of government is visibly engaging them. The **state-publicised** names show which states are "
          "winning investors the centre has not claimed. The **Press Note 3** names should not be worked as "
          "leads at all. The **no-activity** names are the watch list — stated intent that has not become "
          "capex, worth re-checking next cycle.", "",
          "Companion views: `docs/TARGET_LEADS.md` (scored targets), `docs/LEADS.md` (full layer), "
          "`docs/reportage_ministry.html` (what the government announced, by ministry).", ""]

    out = os.path.join(ROOT, "docs/VISIBILITY.md")
    open(out, "w").write("\n".join(L))
    n_quiet = len([r for r in ver["companies"] if r["verdict"] == "QUIET_INVESTOR"])
    print(f"visibility report: {len(ver['companies'])} verified companies, {n_quiet} quiet investors -> {out}")
    if ver.get("clusters_missing"):
        print("  NOTE: news clusters still missing:", ver["clusters_missing"])


if __name__ == "__main__":
    main()
