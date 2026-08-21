#!/usr/bin/env python3
"""Textile-industry-specific target list -- Textiles & Apparel sector companies
with offices or announced India interest. Two ingredients:

  1. The twin's existing static Textiles & Apparel leads (layers/16_leads.json,
     yfinance-verified profitable subset), with each company's real
     india_apac_interest evidence surfaced and confidence-flagged (real
     quoted evidence vs a bare mention count vs no evidence at all vs
     already India-domestic).
  2. A live textile-specific re-sweep of the sources already built for the
     general FDI-discovery pass (2026-08), using textile-industry phrases
     instead of the general "establish India subsidiary" phrases:
       - cninfo (China): 5 phrase variants (印度纺织/印度面料/印度化纤/
         印度服装厂/印度产业用纺织品) -- ZERO hits, endpoint verified still
         working via a control query (印度设立 -> 58, matching the prior run)
       - Oslo Bors NewsWeb (Norway): 1 "textile" title hit (Circa Group,
         textile RECYCLING) -- not India-related, excluded
       - DART (Korea): bounded 400-filing re-sweep with 6 textile phrases
         (인도 섬유/원단/의류/방적/직물/니트) -- see korea_textile_sweep below

Trigger: a user-supplied reference PDF on textile composites for automotive
seat upholstery (Kovacevic et al., IntechOpen 2017, Univ. of Zagreb) --
academic materials-science literature with NO company names, but it defines
the technical-textile/Mobiltech niche (woven+PU foam+knit composites,
polyester/aramid/glass fibre) that this sector search is scoped toward,
matching the twin's existing "Technical textiles mission" central lane.

Usage: python3 scripts/build_textile_sector_targets.py
Output: layers/38_textile_sector_targets.json + docs/TEXTILE_SECTOR_TARGETS.md
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "38_textile_sector_targets.json")
OUT_DOC = os.path.join(ROOT, "docs", "TEXTILE_SECTOR_TARGETS.md")

# Filled in by hand from the live re-sweep results (see docstring) -- update
# korea_textile_sweep if/when the bounded DART re-sweep finds hits.
NEGATIVE_RESULTS = {
    "cninfo_china": {"phrases_tried": ["印度纺织", "印度面料", "印度化纤", "印度服装厂", "印度产业用纺织品"],
                     "hits": 0, "control_query": "印度设立 -> 58 hits (endpoint confirmed working)"},
    "oslo_norway": {"phrase_tried": "textile", "hits": 1,
                    "note": "Circa Group AS -- textile RECYCLING announcement, not India-related, excluded"},
}
korea_textile_sweep = {"status": "complete -- 0 hits (2026-08-21)", "phrases": ["인도 섬유", "인도 원단",
                       "인도 의류", "인도 방적", "인도 직물", "인도 니트"], "filings_checked": 400,
                       "filings_in_range": 2834, "hits": []}



# 🔴 second correction, hand-verified: containing the word "india" isn't enough
# either -- Steven Madden's evidence turned out to be a bare sourcing-country
# LIST ("...manufacturers in China, Cambodia, Vietnam, Mexico, Brazil, India,
# Bangladesh, Italy...") -- existing supply chain, not investment/expansion
# intent. Manually verified against the full (untruncated) sentence in
# layers/16_leads.json; no further heuristic trusted without eyeballing.
KNOWN_SOURCING_ONLY_NOT_INVESTMENT = {"STEVEN MADDEN, LTD."}


def confidence(l):
    # 🔴 first correction: the upstream mention-mining "evidence"/
    # "investment_sentences" field is the sentence NEAREST a keyword hit, not
    # necessarily a sentence that actually mentions India (caught live: Ralph
    # Lauren's "evidence" was credit-facility boilerplate with no India
    # mention at all) -- require the literal word "india" in the evidence text.
    ia = l.get("india_apac_interest") or {}
    if l["country"] == "India":
        return "domestic", None
    if l["company"] in KNOWN_SOURCING_ONLY_NOT_INVESTMENT:
        ev = ((ia.get("evidence") or ia.get("investment_sentences")) or [""])[0]
        return "weak", ev
    if ia.get("level") in ("HIGH", "MEDIUM"):
        ev = (ia.get("evidence") or [""])[0]
        return ("real_evidence" if "india" in ev.lower() else "weak"), ev
    if isinstance(ia.get("india_mentions"), int) and ia["india_mentions"] > 0:
        ev = (ia.get("investment_sentences") or [""])[0]
        return ("real_evidence" if ev and "india" in ev.lower() else "weak_mention"), ev
    return "no_evidence", None


def main():
    leads = json.load(open(os.path.join(ROOT, "layers/16_leads.json")))
    textile = [l for l in leads["leads"] if l["sector"] == "Textiles & Apparel"]

    rows = []
    for l in textile:
        conf, ev = confidence(l)
        rows.append({"company": l["company"], "country": l["country"], "ticker": l.get("ticker"),
                    "lead_score": l["lead_score"], "confidence": conf, "evidence": (ev or "")[:250]})
    rows.sort(key=lambda r: (r["confidence"] != "real_evidence", r["confidence"] == "domestic", -r["lead_score"]))

    real = [r for r in rows if r["confidence"] == "real_evidence"]
    weak = [r for r in rows if r["confidence"] in ("weak", "weak_mention")]
    domestic = [r for r in rows if r["confidence"] == "domestic"]
    none_ = [r for r in rows if r["confidence"] == "no_evidence"]

    out = {"layer": 38, "name": "textile_sector_targets", "built": dt.date.today().isoformat(),
           "what": ("Textiles & Apparel sector filter of the twin's target lists, plus a live "
                    "textile-specific re-sweep of the 2026-08 discovery sources. Triggered by a "
                    "user-supplied academic reference on automotive textile composites (Mobiltech/"
                    "technical-textile niche), which has no company data itself but scopes the search."),
           "static_leads_by_confidence": {"real_evidence": real, "weak_or_bare_mention": weak,
                                          "india_domestic": domestic, "no_evidence": none_},
           "live_resweep_negative_results": NEGATIVE_RESULTS,
           "korea_textile_sweep": korea_textile_sweep,
           "technical_textile_context": ("PM MITRA parks + Technical textiles mission (open central "
                                         "lane, per build_leads.py LANES) is the twin's existing "
                                         "policy hook for the automotive/Mobiltech textile-composite "
                                         "niche the reference PDF describes -- no specific company "
                                         "match found yet in this niche.")}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = ["# Textile-industry target list — companies with offices or announced India interest", "",
         f"*Generated {out['built']} by `scripts/build_textile_sector_targets.py`. Sector: Textiles & "
         "Apparel. Scoped by a user-supplied reference on automotive textile composites (technical-"
         "textile/Mobiltech niche) -- see script docstring.*", "",
         "## Real, quoted India-interest evidence", "",
         "| Company | Country | Ticker | Score | Evidence |", "|---|---|---|---|---|"]
    for r in real:
        L.append(f"| {r['company']} | {r['country']} | {r['ticker']} | {r['lead_score']} | {r['evidence']} |")
    L += ["", "## Weak / bare-mention only (not a real signal on its own)", "",
          "| Company | Country | Ticker | Score |", "|---|---|---|---|"]
    for r in weak:
        L.append(f"| {r['company']} | {r['country']} | {r['ticker']} | {r['lead_score']} |")
    L += ["", "## India-domestic (not foreign investors)", "",
          "| Company | Ticker | Score |", "|---|---|---|"]
    for r in domestic:
        L.append(f"| {r['company']} | {r['ticker']} | {r['lead_score']} |")
    L += ["", "## No India evidence at all (sourcing-only mentions, excluded from targeting)", "",
          "| Company | Country | Ticker | Score |", "|---|---|---|---|"]
    for r in none_:
        L.append(f"| {r['company']} | {r['country']} | {r['ticker']} | {r['lead_score']} |")
    L += ["", "## Live re-sweep results (2026-08)", "",
          f"- **China (cninfo)**: 0 hits across 5 textile-specific phrases ({', '.join(NEGATIVE_RESULTS['cninfo_china']['phrases_tried'])}); "
          f"endpoint confirmed working via control query ({NEGATIVE_RESULTS['cninfo_china']['control_query']}).",
          f"- **Norway (Oslo NewsWeb)**: 1 'textile' hit, Circa Group AS (textile recycling) -- not India-related, excluded.",
          f"- **Korea (DART)**: {korea_textile_sweep['status']}.", ""]
    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"real_evidence: {len(real)} | weak: {len(weak)} | domestic: {len(domestic)} | "
          f"no_evidence: {len(none_)} -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    main()
