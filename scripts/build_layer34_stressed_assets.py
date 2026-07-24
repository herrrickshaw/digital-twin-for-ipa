#!/usr/bin/env python3
"""Layer 34 — stressed / distressed assets consolidator.

Pulls together the twin's THREE stressed-asset signal sources that were
scattered before:
  1. company-level distress flags from the layer-32 credit-rating channel
     (rating-darkness, watch-negative, downgrade, sub-IG, promoter litigation)
     — queried live from data/companies.db and materialized as a
     `stressed_assets` VIEW.
  2. the national distressed-LAND supply channels + named liquidation assets
     from the sibling repo india-trade-sector-policy-recommendations
     (data/stressed_distressed_land_2026-07-22.json) — the IBC/PSU/ARC pools.
  3. the Dunlop India litigation case map (a wound-up manufacturer with
     property threads in TN + WB) — the worked single-asset example, sourced
     from the user's offline workbook (kept as data, not the GDrive path).

Real stressed-asset registers (IBBI, NLMC, SARFAESI e-auctions) are named
with access routes — the twin does not yet ingest them, recorded as data.

Usage:  python3 scripts/build_layer34_stressed_assets.py [--no-land]
Output: layers/34_stressed_assets.json  (+ stressed_assets view in companies.db)
"""
import argparse
import json
import os
import re
import sqlite3
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
OUT = os.path.join(ROOT, "layers", "34_stressed_assets.json")
# sibling repo, pulled live from HEAD (same pattern as layers 25/30)
LAND_RAW = ("https://raw.githubusercontent.com/herrrickshaw/"
            "india-trade-sector-policy-recommendations/main/"
            "data/stressed_distressed_land_2026-07-22.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Dunlop India case map — condensed from the due-diligence workbook
# (Dunlop_Stressed_Asset_Case_Map.xlsx). Facts only; the workbook itself stays
# offline. This is the worked example of an individual stressed asset.
DUNLOP = {
    "entity": "Dunlop India Ltd. (formerly Dunlop Rubber Co. (India) Ltd., inc. 1929)",
    "distress": ("declared sick under SICA 1985; ordered WOUND UP by Calcutta HC "
                 "31-Jan-2013 (C.P. 233/2008), appeal dismissed 02-May-2013; "
                 "Official Liquidator in possession"),
    "ownership_trail": "Chhabria (Jumbo) group -> Ruia group (2005)",
    "plants": ["Sahaganj, Hooghly (WB) — earthmover/aero-tyre, suspended 08-Oct-2011",
               "Ambattur, Chennai (TN) — suspended Feb-2012"],
    "key_allegation": ("~Rs 2,300 cr of four valuable properties allegedly "
                       "transferred surreptitiously while before BIFR (Div. Bench "
                       "order 02-May-2013)"),
    "asset_threads": {
        "TN_Ambattur": ("~60.86 acres assigned land (of ~149 acres acquired 1959); "
                        "sold Rs 24.34 cr (2004) to V.N. Devadoss via BIFR/AAIFR; "
                        "GoTN held sale in breach (G.O. Ms. 183, 31-Mar-2008); "
                        "workers' + Dunlop challenges dismissed (res judicata) — "
                        "SC Devadoss stamp-duty ruling 08-May-2009"),
        "WB_KingsCourt": ("50% share in 'Kings Court', 46B Chowringhee Rd, Kolkata "
                          "(5-storey, 12 flats); sale-notice valuation Rs 29.44 cr "
                          "(2024); OL sale contested by Salasar Towers (pre-emption) "
                          "+ Eyelid Mercantiles (unregistered 2006 agreement, no "
                          "title per Suraj Lamp); lead judgment 17-Mar-2026 "
                          "(J. Raja Basu Chowdhury): auction stands, Salasar may "
                          "match, Eyelid gets liberty to sue for specific "
                          "performance"),
    },
    "other_properties": ["62A Mirza Ghalib St, Kolkata (OL possession)",
                         "Worli, Mumbai (OL sought leave to take over)",
                         "Athipattu, Chennai (voluntarily sold)"],
    "status": ("live liquidation — Kings Court 50% under OL auction as of the "
               "17-Mar-2026 Calcutta HC judgment (indiankanoon.org/doc/110197805)"),
    "twin_relevance": ("the worked template for a manufacturer stressed asset: a "
                       "wound-up factory whose LAND is the residual value, tied up "
                       "in multi-forum litigation — exactly the IBC/liquidation "
                       "pool the land dataset counts in aggregate. Ambattur/"
                       "Sahaganj are the physical parcels; the litigation is the "
                       "acquisition risk"),
}

REGISTERS = [
    {"name": "IBBI liquidation auction notices", "url": "https://ibbi.gov.in/liquidation-auction-notices/lists",
     "holds": "per-liquidator e-auction PDFs (land+building parcels of corporate debtors)",
     "twin_status": "NOT yet ingested — the machine-readable stressed-asset feed to add next"},
    {"name": "NLMC (National Land Monetisation Corp)", "url": "https://nlmc.dpe.gov.in",
     "holds": "surplus/non-core land of closed & disinvesting CPSEs (~3,400 acres referred)",
     "twin_status": "reference only"},
    {"name": "SARFAESI / ARC e-auctions", "url": "auctiontiger.in · bankeauctions.com · narcl.co.in · arcil.co.in",
     "holds": "mortgaged industrial property enforced by secured lenders/ARCs",
     "twin_status": "reference only (count not centrally disclosed)"},
    {"name": "State industrial-corp resumed plots", "url": "GIDC · UPSIDA · MIDC MILAAP · RIICO",
     "holds": "allotted-but-unutilised plots cancelled and re-offered (GIDC ~1,800 ha)",
     "twin_status": "reference — overlaps the layer-25 IILB land data"},
]


# rating-grade rank: lower = worse. sub-investment-grade = BB+ and below (<=11).
_GRADE_RANK = {}
for _i, _g in enumerate(["D", "C", "CC", "CCC", "B-", "B", "B+", "BB-", "BB",
                         "BB+", "BBB-", "BBB", "BBB+", "A-", "A", "A+", "AA-",
                         "AA", "AA+", "AAA"]):
    _GRADE_RANK[_g] = _i
SUB_IG_MAX_RANK = _GRADE_RANK["BB+"]   # 9
_GRADE_RE = re.compile(r"\b(AAA|AA[+-]?|A[+-]?|BBB[+-]?|BB[+-]?|B[+-]?|CCC|CC|C|D)\b")


def current_grade(rating):
    """Parse the CURRENT long-term grade, ignoring 'upgraded/downgraded from X'
    prior grades that trail the string."""
    head = re.split(r"upgraded from|downgraded from|\bfrom\b|reaffirmed from",
                    rating, flags=re.I)[0]
    m = _GRADE_RE.search(head)
    return m.group(1) if m else None


def classify(rating, care_check, adds):
    rl = rating.lower()
    if any(t in rl for t in ("not cooperating", "issuer not", "withdraw")):
        return "rating_darkness"
    if (care_check and "litig" in care_check.lower()) or \
       (adds and "high-risk" in adds.lower()):
        return "litigation_or_regrade"
    if "watch" in rl and "negativ" in rl or "(rwn)" in rl:
        return "watch_negative"
    if "downgrad" in rl:
        return "downgrade"
    if "standalone bb" in rl:
        return "sub_investment_grade"
    g = current_grade(rating)
    if g and _GRADE_RANK.get(g, 99) <= SUB_IG_MAX_RANK:
        return "sub_investment_grade"
    return None


def build_view(cur):
    """A convenience view mirroring the event-based flags (robust in pure SQL);
    the authoritative classification (incl. grade-parsed sub-IG) is computed in
    Python below and carried in the layer JSON."""
    cur.execute("DROP VIEW IF EXISTS stressed_assets")
    cur.execute(
        """
        CREATE VIEW stressed_assets AS
        SELECT c.company_id, c.name, c.country, r.agency, r.rating,
               (SELECT visibility_verdict FROM clearance_activity a
                  WHERE a.company_id=c.company_id
                    AND a.visibility_verdict IS NOT NULL LIMIT 1) AS ec_visibility,
               CASE
                 WHEN lower(r.rating) LIKE '%not cooperating%'
                   OR lower(r.rating) LIKE '%issuer not%'
                   OR lower(r.rating) LIKE '%withdraw%'      THEN 'rating_darkness'
                 WHEN lower(COALESCE(r.care_check,'')) LIKE '%litig%'
                   OR lower(COALESCE(r.adds_beyond_news,'')) LIKE '%high-risk%'
                                                             THEN 'litigation_or_regrade'
                 WHEN lower(r.rating) LIKE '%watch%negativ%'
                   OR lower(r.rating) LIKE '%(rwn)%'         THEN 'watch_negative'
                 WHEN lower(r.rating) LIKE '%downgrad%'      THEN 'downgrade'
                 WHEN lower(r.rating) LIKE '%standalone bb%' THEN 'sub_investment_grade'
                 ELSE 'grade_check_in_python'
               END AS event_flag,
               r.care_check, r.adds_beyond_news, r.rationale_url
          FROM companies c JOIN credit_ratings r USING (company_id)
         WHERE r.rating IS NOT NULL
        """
    )
    out = []
    for row in cur.execute(
            "SELECT company_id, name, country, agency, rating, ec_visibility, "
            "care_check, adds_beyond_news, rationale_url FROM stressed_assets"):
        (cid, name, country, agency, rating, vis, cc, adds, url) = row
        flag = classify(rating, cc, adds)
        if flag:
            out.append({"company_id": cid, "name": name, "country": country,
                        "agency": agency, "rating": rating,
                        "current_grade": current_grade(rating),
                        "ec_visibility": vis, "stress_flag": flag,
                        "rationale_url": url})
    out.sort(key=lambda r: (r["stress_flag"], r["name"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-land", action="store_true")
    args = ap.parse_args()
    today = date.today().isoformat()

    con = sqlite3.connect(DB)
    cur = con.cursor()
    company_flags = build_view(cur)
    con.commit()
    con.close()

    land = None
    if not args.no_land:
        try:
            req = urllib.request.Request(LAND_RAW, headers={"User-Agent": UA})
            land = json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            land = {"error": f"live pull failed: {type(e).__name__}",
                    "fallback": "sibling repo india-trade-sector-policy-recommendations"}

    from collections import Counter
    by_flag = Counter(f["stress_flag"] for f in company_flags)

    layer = {
        "layer": 34,
        "name": "stressed_assets",
        "built": today,
        "what": ("Consolidated stressed/distressed-asset view across three "
                 "previously-scattered sources: (1) company-level credit-rating "
                 "distress flags from the layer-32 DB (stressed_assets VIEW), "
                 "(2) national distressed-LAND supply channels + named "
                 "liquidation assets (sibling policy-recs repo), (3) the Dunlop "
                 "India litigation case map (worked single-asset example). Real "
                 "registers (IBBI/NLMC/SARFAESI) named with routes, not yet "
                 "ingested."),
        "company_distress_flags": {
            "note": ("materialized as the `stressed_assets` view in "
                     "companies.db; these are RATING/LITIGATION signals, NOT a "
                     "formal NPA/IBC classification"),
            "counts_by_flag": dict(by_flag),
            "companies": company_flags,
        },
        "distressed_land_channels": {
            "source": ("india-trade-sector-policy-recommendations / "
                       "data/stressed_distressed_land_2026-07-22.json (pulled live)"),
            "pools": (land.get("pools") if isinstance(land, dict) else None),
            "named_assets": (land.get("named_assets") if isinstance(land, dict) else None),
            "best_access_routes": (land.get("best_access_routes") if isinstance(land, dict) else None),
            "caveats": (land.get("caveats") if isinstance(land, dict) else land),
        },
        "worked_case_dunlop": DUNLOP,
        "registers_to_ingest": REGISTERS,
        "caveats": [
            "The company_distress_flags are RATING-channel signals on companies "
            "the twin already tracks — NOT an exhaustive stressed-asset universe.",
            "No single official 'total acres in IBC liquidation' statistic exists "
            "(IBBI reports process counts, not acreage) — see land caveats.",
            "Dunlop facts are from a due-diligence workbook; verify the live "
            "auction status before acting (17-Mar-2026 judgment is the latest).",
        ],
        "next": ("wire the IBBI liquidation-auction-notice list "
                 "(ibbi.gov.in/liquidation-auction-notices/lists) as a real "
                 "machine-readable stressed-asset feed — the one register that "
                 "publishes structured per-asset notices"),
    }
    with open(OUT, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    print(f"company distress flags: {len(company_flags)} -> {dict(by_flag)}")
    print(f"land pools: {len(land.get('pools', [])) if isinstance(land, dict) else 0}, "
          f"named assets: {len(land.get('named_assets', [])) if isinstance(land, dict) else 0}")
    print("wrote", OUT, "+ stressed_assets view")


if __name__ == "__main__":
    main()
