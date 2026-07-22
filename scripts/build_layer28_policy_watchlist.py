#!/usr/bin/env python3
"""Layer 28 — policy watchlist: policies being discussed / in the pipeline.

Forward-looking counterpart to layer 17 (existing schemes): tracks NEW policy
that is drafted, tabled, or under public discussion but not yet in force —
the regulatory changes an investor should watch. Sources:

 - PRS Legislative Research bill track (prsindia.org/billtrack) — the
   authoritative list of bills & draft rules before Parliament / in consultation.
 - Drishti IAS current-affairs editorials (drishtiias.com) — what policy topics
   are being publicly debated now. Other IAS sources (Vision IAS, InsightsIAS)
   are reachable and recorded for manual cross-check.
 - Parliament: Lok Sabha bills page + the (undocumented) LS Q&A API. 🔴 Rajya
   Sabha sources are blocked from this machine (recorded, not skipped).

Investment-relevant bills are flagged and mapped to twin sectors/incentive lanes.
Output: layers/28_policy_watchlist.json. Re-run any time (lists are pulled live).
"""
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "layers"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

PRS_BILLTRACK = "https://prsindia.org/billtrack"
DRISHTI_CA = "https://www.drishtiias.com/current-affairs-news-analysis-editorials"

# investment-relevance keywords -> twin sector / incentive lane
RELEVANCE = {
    "income-tax": "Taxation", "taxation": "Taxation", "gst": "Taxation",
    "goods-and-services-tax": "Taxation", "central-excise": "Taxation",
    "provisional-collection-of-taxes": "Taxation",
    "securities-markets": "Financial markets / SEBI",
    "banking": "BFSI", "insolvency": "BFSI / IBC", "insurance": "BFSI",
    "bima": "BFSI / insurance", "corporate-laws": "Corporate / ease of business",
    "companies-act": "Corporate / ease of business",
    "jan-vishwas": "Ease of business (decriminalisation)",
    "electricity": "Power / RDSS", "nuclear-energy": "Nuclear power",
    "oilfields": "Oil & Gas", "mines-and-minerals": "Metals & Mining",
    "offshore-areas-mineral": "Offshore minerals",
    "ports": "Ports / Gati Shakti", "shipping": "Shipping / shipbuilding",
    "merchant-shipping": "Shipping", "coastal-shipping": "Shipping",
    "bills-of-lading": "Shipping / trade", "carriage-of-goods-by-sea": "Shipping",
    "railways": "Railways / Gati Shakti", "telecommunication": "Telecom",
    "broadcasting": "Media / broadcasting", "online-gaming": "Digital / gaming",
    "personal-data-protection": "Digital / DPDP", "it-rules": "Digital / IT",
    "boilers": "Manufacturing safety", "industrial-relations": "Labour codes",
    "code-on-wages": "Labour codes", "occupational-safety": "Labour codes",
    "social-security": "Labour codes", "oilfields-regulation": "Oil & Gas",
    "aircraft": "Aviation", "vayuyan": "Aviation", "immigration": "Mobility / talent",
    "research-foundation": "R&D / innovation", "anusandhan": "R&D / innovation",
    "post-office": "Logistics", "inland-vessels": "Inland waterways",
    "land-titling": "Land / property", "sports-governance": "Sports",
}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def titleize(slug):
    words = slug.replace("the-", "", 1).split("-")
    fix = {"gst": "GST", "it": "IT", "igst": "IGST", "iim": "IIM", "no2": "No.2",
           "and": "and", "of": "of", "for": "for", "the": "the", "to": "to",
           "on": "on", "in": "in"}
    out = []
    for i, w in enumerate(words):
        if w in fix:
            out.append(fix[w] if w not in ("and", "of", "for", "the", "to",
                                           "on", "in") or i == 0
                       else w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def classify(slug):
    for kw, lane in RELEVANCE.items():
        if kw in slug:
            return lane
    return None


def fetch_prs_bills():
    html = get(PRS_BILLTRACK)
    slugs = sorted(set(re.findall(r'href="/billtrack/([a-z0-9-]+)"', html)))
    slugs = [s for s in slugs if not s.startswith("category")]
    bills = []
    for s in slugs:
        yr = re.search(r'(20\d{2})', s)
        bills.append({
            "slug": s, "title": titleize(s),
            "year": int(yr.group(1)) if yr else None,
            "investment_lane": classify(s),
            "is_draft": s.startswith("draft") or "draft" in s,
            "url": f"https://prsindia.org/billtrack/{s}",
        })
    return bills


def fetch_drishti_editorials():
    html = get(DRISHTI_CA)
    slugs = sorted(set(re.findall(
        r'daily-news-editorials/([a-z0-9-]+)', html)))
    return [{"slug": s, "topic": titleize(s),
             "url": f"https://www.drishtiias.com/daily-updates/"
                    f"daily-news-editorials/{s}"} for s in slugs]


def build():
    bills = fetch_prs_bills()
    editorials = fetch_drishti_editorials()
    relevant = [b for b in bills if b["investment_lane"]]
    recent = [b for b in bills if (b["year"] or 0) >= 2024]
    # the actionable set: investment-relevant AND current (2024+)
    active = sorted([b for b in relevant if (b["year"] or 0) >= 2024],
                    key=lambda b: (-(b["year"] or 0), b["investment_lane"]))

    layer = {
        "layer": 28,
        "title": "Policy watchlist — policies in discussion / in the pipeline",
        "built": date.today().isoformat(),
        "purpose": "Forward-looking counterpart to the scheme monitor: NEW "
                   "policy drafted, tabled or under public debate that will "
                   "change the regulatory landscape for investors, before it is "
                   "in force.",
        "sources": {
            "prs_billtrack": {"url": PRS_BILLTRACK, "role": "authoritative bill "
                              "& draft-rule pipeline (Parliament + consultation)",
                              "access": "scraped live"},
            "drishti_ias": {"url": DRISHTI_CA, "role": "current-affairs "
                            "editorials — what policy is being debated now",
                            "access": "scraped live"},
            "other_ias": {"vision_ias": "https://visionias.in/current-affairs/",
                          "insights_ias": "https://www.insightsonindia.com/",
                          "access": "reachable; recorded for manual cross-check"},
            "lok_sabha": {"bills": "https://sansad.in/ls/legislation/bills",
                          "qa_api": "https://sansad.in/api_ls/question/"
                                    "qetFilteredQuestionsAns (needs query params; "
                                    "400 without)", "access": "reachable"},
            "rajya_sabha": {"access": "BLOCKED from this machine (recorded, not "
                            "skipped) — use browser/alternate host if needed"},
        },
        "counts": {"prs_bills_total": len(bills),
                   "investment_relevant": len(relevant),
                   "recent_2024plus": len(recent),
                   "active_watchlist": len(active),
                   "drishti_editorials": len(editorials)},
        "active_watchlist": active,
        "investment_relevant_bills": sorted(
            relevant, key=lambda b: -(b["year"] or 0)),
        "all_prs_bills": bills,
        "policy_debate_editorials": editorials,
        "linkage": {
            "to_layer_17": "When a watchlist bill is enacted it graduates into "
                           "the scheme monitor / incentive catalogue.",
            "to_layer_05": "Bills like Jan Vishwas (decriminalisation), the "
                           "Securities Markets Code and labour codes reshape the "
                           "decade report card's ease-of-doing-business lane.",
            "to_sectors": "investment_lane maps each relevant bill to the twin "
                          "sector it affects (Electricity Amendment -> Power; "
                          "Nuclear Energy Bill -> nuclear; Ports/Shipping -> "
                          "Gati Shakti maritime; Income Tax/Securities -> BFSI).",
        },
    }
    out = LAYERS / "28_policy_watchlist.json"
    out.write_text(json.dumps(layer, indent=1, ensure_ascii=False))
    print(f"layer 28: {len(bills)} PRS bills; {len(active)} active watchlist "
          f"(investment-relevant & 2024+); {len(relevant)} relevant all-time; "
          f"{len(editorials)} Drishti editorials -> {out}")


if __name__ == "__main__":
    build()
