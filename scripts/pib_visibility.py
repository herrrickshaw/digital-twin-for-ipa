#!/usr/bin/env python3
"""Visibility map: which leads the government actually announces, and which invest quietly.

Cross-matches every company in layers/16_leads.json against the PIB register
(122k+ releases) over the LAST 3 YEARS, and buckets them:

    ANNOUNCED    named in a PIB release title in the last 3 years
    HISTORIC     named only before the 3-year window
    BELOW_RADAR  never named -- despite (for the graded ones) verified India intent

WHAT THIS CAN AND CANNOT SHOW. The register stores release TITLES, not bodies, so
a company mentioned inside a release but not in its headline reads as BELOW_RADAR.
Title-naming is therefore a proxy for *headline* government attention, not for all
government contact -- it understates visibility and is stated that way everywhere
the output is used. The asymmetry is still informative: PIB headlines name firms
when the government wants credit for the investment.

Matching is deliberately conservative:
  - corporate suffixes stripped to a core name (Kerry Group -> Kerry)
  - word-boundary regex, case-insensitive, core name >= 4 chars
  - AMBIGUOUS names (common words, or shared with unrelated entities) are never
    auto-matched; each is either given an explicit safe pattern or excluded, with
    the reason recorded in the output so nobody re-derives it later

    python3 scripts/pib_visibility.py            # rebuild the map
    python3 scripts/pib_visibility.py --audit    # print sample titles per match
"""
import argparse, datetime, json, os, re, sqlite3
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.expanduser("~/india-trade-sector-policy-recommendations/data/pib_index.sqlite")
WINDOW_START = "2023-07-21"   # last 3 years

# stripped ONLY from the end of a name, repeatedly -- never mid-name, or
# "Industries Qatar" would collapse to "Qatar" and match every Amir headline.
TRAILING = re.compile(
    r"[\s,.-]*\b(inc|corp|corporation|incorporated|co|company|ltd|limited|plc|llc|lp|"
    r"sa|sab|spa|ag|nv|bv|as|asa|ab|oyj|group|holdings?|holding|pcl|berhad|bhd|tbk|"
    r"qpsc|psc|gmbh|kgaa|se|sas|srl|pte|pvt|private|public|cv|aktiengesellschaft|"
    r"a\.s|s\.a|s\.p\.a|n\.v|c\.v|q\.p\.s\.c)\b\.?\s*$", re.I)

# A company's FIRST token is only safe to match alone when it is distinctive.
# These are not: they are country/city/sector words that saturate PIB headlines.
GENERIC_FIRST = {
    "food", "foods", "saudi", "qatar", "thai", "china", "chinese", "india", "indian",
    "japan", "japanese", "korea", "korean", "national", "international", "associated",
    "united", "general", "american", "british", "royal", "global", "great", "first",
    "new", "world", "central", "eastern", "western", "northern", "southern", "asia",
    "asian", "pacific", "euro", "european", "swiss", "dutch", "german", "french",
    "industries", "industrial", "energy", "power", "steel", "cement", "motor",
    "motors", "auto", "electric", "electronics", "chemical", "chemicals", "pharma",
    "pharmaceutical", "pharmaceuticals", "medical", "health", "life", "green",
    "solar", "wind", "gas", "oil", "petro", "petroleum", "mining", "metals", "metal",
    "bank", "capital", "trading", "tokyo", "shanghai", "beijing", "hong", "taiwan",
    "singapore", "malaysia", "vietnam", "gulf", "arab", "emirates", "abu", "grupo",
    "compagnie", "societe", "aluminium", "aluminum", "sugar", "dairy", "milk",
}

# Names that must NOT be auto-matched: the bare token collides with unrelated
# things in Indian government headlines. Value = safe pattern, or None to exclude.
AMBIGUOUS = {
    "Kerry": r"Kerry Group",              # John Kerry (US climate envoy) dominates PIB
    "Delta": r"Delta Electronics",        # "Delta variant", "Ganga delta"
    "Astra": None,                        # collides with AstraZeneca + Astra missile
    "Indra": r"Indra Sistemas",           # Indra/Indira as a personal name
    "Ball": None,                         # generic word
    "Gulf": None,                         # region, not the Thai company
    "Sigma": None,                        # generic
    "Alfa": None,                         # generic
    "Aster": None,                        # Aster DM Healthcare is a different Indian firm
    "Apple": r"\bApple Inc|\bApple\b(?!.*\b(fruit|orchard|horticultur))",
    "Orbia": r"Orbia|Netafim",            # Netafim is its India-facing brand
    "a2": None,                           # too short/generic
    "Union": None,                        # Thai Union -> "Union" collides constantly
    "Top": None,                          # Top Glove
    "Press": None,                        # Press Metal
    "Siam": r"Siam Cement|\bSCG\b",
    "Charoen": r"Charoen Pokphand|\bCP Foods\b",
    "Fisher": r"Fisher\s*&?\s*Paykel",
    "Hoa": r"Hoa Phat",
    "Grupo": None,                        # many Grupos
    "Bimbo": r"Grupo Bimbo|\bBimbo\b",
    "Ford": r"Ford Otosan",               # bare "Ford" = Ford India, a different story
    "Universal": None,
    "Barito": r"Barito",
    "Chandra": r"Chandra Asri",           # "Chandra" is a common Indian name
    "Ezz": None,
    "Abou": None,
    "Nemak": r"Nemak",
    "Erdemir": r"Erdemir|Eregli",
    "Metlen": r"Metlen|Mytilineos",
    "Iveco": r"Iveco",
    "Aluar": r"Aluar",
    "Juhayna": r"Juhayna",
    "Cochlear": None,                     # "cochlear implant" is a clinical term
    "Dassault": r"Dassault Aviation|Rafale",   # not Dassault Systemes (software)
    "Mitsui": r"Mitsui O\.?\s?S\.?\s?K\.?",    # not Sumitomo Mitsui / Mitsui & Co
    "Merck": r"Merck KGaA|EMD ",          # Merck & Co (US) is a different company
    "Sumitomo": r"Sumitomo (Chemical|Electric|Metal|Heavy)",
}
MIN_CORE = 4

# A PIB headline naming a company is only an ANNOUNCEMENT of activity if it is
# about investment/production; condolences, obituaries and unrelated-affiliate
# merger clearances are incidental mentions and are counted separately.
INVESTMENT_RX = re.compile(
    r"inaugurat|foundation stone|groundbreaking|ground.breaking|bhoomi|"
    r"\bMoU\b|memorandum of understanding|joint venture|\bJV\b|invest|"
    r"plant|factory|facility|manufactur|production unit|expansion|"
    r"commission(ed|ing)|sign(s|ed) (a |an )?(agreement|contract|pact)|"
    r"crore|billion|approval under|incentive|scheme", re.I)


def core_name(name):
    """Strip parentheticals and TRAILING corporate suffixes; return (core, aliases)."""
    raw = name or ""
    aliases = [a.strip() for a in re.findall(r"\(([^)]{3,})\)", raw)]
    n = re.sub(r"\([^)]*\)", " ", raw)
    n = re.sub(r"[^\w\s&.'-]", " ", n)
    n = re.sub(r"^the\s+", "", n, flags=re.I)      # "The a2 Milk" -> "a2 Milk"
    n = re.sub(r"\s+", " ", n).strip()
    prev = None
    while prev != n:                       # e.g. "... Co., Ltd." -> two passes
        prev = n
        n = TRAILING.sub("", n).strip(" .,-&")
    return n, aliases


def pattern_for(company):
    """Return (regex, note) or (None, reason-excluded).

    Matches the full core phrase (word-flexible), plus the bare first token only
    when that token is distinctive -- so 'Suzuki Motor' also catches 'Maruti
    Suzuki', while 'Food Empire' never matches a street-food headline."""
    core, aliases = core_name(company)
    if not core:
        return None, "no usable core name"
    tokens = core.split()
    first = tokens[0]
    key = first.title()
    if key in AMBIGUOUS:
        pat = AMBIGUOUS[key]
        if pat is None:
            return None, f"ambiguous token '{first}' -- excluded to avoid false positives"
        return re.compile(pat, re.I), f"curated pattern for ambiguous '{first}'"

    # A short leading token is only safe alone when it IS the whole name:
    # "GSK plc" -> \bGSK\b (case-sensitive) is distinctive, but "Hon Hai" must
    # never reduce to \bHon\b ("Hon'ble"), nor "ELI LILLY" to \bELI\b (the
    # Employment Linked Incentive scheme), nor "The a2 Milk" to \bThe\b.
    if len(tokens) == 1 and 3 <= len(first) < MIN_CORE and (first.isupper() or first.istitle()):
        alt = "|".join([r"\b" + re.escape(t) + r"\b"
                        for t in [first] + [a for a in aliases if 3 <= len(a) < MIN_CORE]])
        return re.compile(alt), f"case-sensitive acronym match '{first}'"

    parts = []
    if len(tokens) > 1:
        parts.append(r"\b" + r"\s+".join(re.escape(t) for t in tokens) + r"\b")
        if first.lower() not in GENERIC_FIRST and len(first) >= MIN_CORE:
            parts.append(r"\b" + re.escape(first) + r"\b")
    else:
        if first.lower() in GENERIC_FIRST or len(first) < MIN_CORE:
            return None, f"single generic/short token '{first}' -- excluded"
        parts.append(r"\b" + re.escape(first) + r"\b")
    for a in aliases:                       # SABIC, Ma'aden, ANTAM, SCG ...
        if len(a) >= MIN_CORE and a.lower() not in GENERIC_FIRST:
            parts.append(r"\b" + re.escape(a) + r"\b")

    note = None if len(tokens) == 1 or first.lower() not in GENERIC_FIRST else \
        f"phrase-only (generic first token '{first}')"
    return re.compile("|".join(parts), re.I), note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true", help="print sample matched titles")
    args = ap.parse_args()

    leads = json.load(open(os.path.join(ROOT, "layers/16_leads.json")))
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT id, date, ministry, title FROM pib_items ORDER BY date").fetchall()
    recent = [r for r in rows if r[1] >= WINDOW_START]

    out, buckets = [], defaultdict(list)
    for l in leads["leads"]:
        rx, note = pattern_for(l["company"])
        rec = {"company": l["company"], "ticker": l.get("ticker"), "country": l["country"],
               "sector": l["sector"], "lead_score": l["lead_score"],
               "india_intent": (l.get("india_apac_interest") or {}).get("level"),
               "match_note": note}
        if rx is None:
            rec["visibility"] = "UNMATCHABLE"
            buckets["UNMATCHABLE"].append(rec); out.append(rec); continue
        hits = [(d, prid, m, t) for prid, d, m, t in recent if rx.search(t or "")]
        older = [(d, prid, m, t) for prid, d, m, t in rows
                 if d < WINDOW_START and rx.search(t or "")]
        inv = [h for h in hits if INVESTMENT_RX.search(h[3] or "")]
        rec["pib_hits_3y"] = len(hits)
        rec["pib_investment_hits_3y"] = len(inv)
        rec["pib_hits_before"] = len(older)
        rec["releases"] = [{"date": d, "prid": p, "ministry": m, "title": t[:150],
                            "investment_related": bool(INVESTMENT_RX.search(t or ""))}
                           for d, p, m, t in (inv or hits)[-5:]]
        rec["visibility"] = ("ANNOUNCED" if inv else
                             "MENTIONED_ONLY" if hits else
                             "HISTORIC" if older else "BELOW_RADAR")
        buckets[rec["visibility"]].append(rec); out.append(rec)

    graded = [r for r in out if r["india_intent"] in ("HIGH", "MEDIUM")]
    quiet = sorted([r for r in graded if r["visibility"] == "BELOW_RADAR"],
                   key=lambda r: (r["india_intent"] != "HIGH", -r["lead_score"]))
    loud = sorted([r for r in graded if r["visibility"] == "ANNOUNCED"],
                  key=lambda r: -r["pib_investment_hits_3y"])

    doc = {"layer": "pib_visibility_map", "built": datetime.date.today().isoformat(),
           "window": f"{WINDOW_START} .. {datetime.date.today().isoformat()} (3 years)",
           "register": f"{len(rows)} PIB releases, {len(recent)} in window",
           "method": ("company-name match against release TITLES only (the register stores no bodies), "
                      "so this measures HEADLINE government attention and understates total contact; "
                      "ambiguous tokens are curated or excluded, never auto-matched"),
           "counts": {k: len(v) for k, v in sorted(buckets.items())},
           "announced": loud, "below_radar": quiet, "all": out}
    json.dump(doc, open(os.path.join(ROOT, "layers/19_pib_visibility.json"), "w"), indent=1)

    print(f"register {len(rows)} releases ({len(recent)} in 3y window)")
    for k, v in sorted(buckets.items()):
        print(f"  {k:<12} {len(v)}")
    print(f"\ngraded (HIGH/MEDIUM intent): {len(graded)} -> {len(loud)} announced, {len(quiet)} below radar")
    print("\nLOUDEST (most PIB headlines, 3y):")
    for r in loud[:10]:
        print(f"  {r['pib_investment_hits_3y']:>3}  {r['india_intent']:<6} {r['company'][:38]:38} {r['country']}")
    print("\nQUIETEST (verified intent, zero PIB headlines):")
    for r in quiet[:15]:
        print(f"       {r['india_intent']:<6} {r['company'][:38]:38} {r['country'][:14]:14} {r['sector'][:26]}")
    if args.audit:
        print("\n--- audit: sample matched titles ---")
        for r in loud[:8]:
            print(f"\n{r['company']} ({r['pib_investment_hits_3y']} investment hits)")
            for rel in r["releases"][-3:]:
                print(f"   {rel['date']} [{rel['ministry'][:28]}] {rel['title'][:100]}")


if __name__ == "__main__":
    main()
