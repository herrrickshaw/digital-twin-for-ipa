#!/usr/bin/env python3
"""Layer 32 enrichment — Invest India announcement-ticker validation.

Scrapes the LATEST-UPDATES ticker from every Invest India sector page (the
company-investment announcement feed layer 31 identified) and validates the
company DB's EXCEPTION cohort against it:

  - QUIET / PARTIALLY_VISIBLE clearance leads: companies expanding via EC/FC
    filings without press coverage. If India's own national IPA is announcing
    them, the quiet verdict is CHALLENGED (displayed, never silently
    overwritten — layer-24 convention).
  - Credit-rating contradiction flags (e.g. Viyash's "no capex" vs 10 live
    filings): a ticker mention is a third data point.

Everything scraped is also stored as a general enrichment channel:
  ii_announcements        one row per ticker item per sector page
  ii_company_matches      conservative name matches vs the companies table
                          (matched fragment kept for review — validation,
                          not silent linkage)

The layer JSON (32_company_db.json) gets an `ii_ticker_validation` block
appended (read-modify-write; build_company_db.py owns the rest of the file).

Run AFTER build_company_db.py (the DB is dropped and rebuilt there).
Usage:  python3 scripts/enrich_company_db_ii_tickers.py
"""
import json
import os
import re
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
LAYER = os.path.join(ROOT, "layers", "32_company_db.json")
SITEMAP = "https://www.investindia.gov.in/sitemap.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")

# tokens that must never anchor a match: generic + geographic
STOP_TOKENS = {"india", "indian", "national", "the", "new", "bharat", "shree",
               "sri", "orissa", "gujarat", "premier", "united", "global",
               "green", "power", "solar", "energy", "steel", "cement",
               "west", "east", "north", "south", "tamil", "andhra", "uttar",
               "madhya", "maharashtra", "karnataka", "kerala", "punjab",
               "haryana", "bihar", "assam", "odisha", "telangana", "rajasthan",
               "bengal", "delhi", "mumbai", "chennai", "hindustan"}

SUFFIXES = re.compile(
    r"\b(private|pvt|limited|ltd|llp|llc|inc|incorporated|corp|corporation|plc|"
    r"co|company|gmbh|ag|sa|nv|bv|ab|as|asa|oyj|spa|kk|pte|sdn bhd|holdings?)\b\.?",
    re.I,
)


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"^m\s*/\s*s\.?\s+", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = SUFFIXES.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def sector_urls():
    xml = get(SITEMAP)
    return sorted(set(re.findall(r"<loc>(https://www\.investindia\.gov\.in/sectors?/[^<]+)</loc>", xml)))


def scrape_ticker(url):
    """-> list of (announcement_text, source_url) from one sector page."""
    try:
        html = get(url)
    except Exception as e:
        return [("__FETCH_ERROR__", f"{type(e).__name__}: {e}")]
    block = re.search(r'class="latest-update-items"(.*?)(?:<div class="blog-right|</section>|$)',
                      html, re.S)
    if not block:
        return []
    items = re.findall(r'<div class="latest-link">\s*<a href="([^"]+)"[^>]*>(.*?)</a>',
                       block.group(1), re.S)
    out = []
    import html as _html
    for href, text in items:
        text = _html.unescape(re.sub(r"<[^>]+>", "", text))
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            out.append((text, href.strip()))
    return out


def match_fragments(name_norm):
    """-> [(fragment, quality)] — STRONG fragments (full name / first two
    tokens) may challenge verdicts; WEAK ones (a lone distinctive token, only
    when the company's whole name IS that token) are review-only. A
    multi-token company must never match on its first token alone — that is
    how 'Reliance Bp Mobility' swallowed every Reliance Industries story and
    'Galaxy Dyestuff' matched Samsung Galaxy phones."""
    toks = name_norm.split()
    frags = []
    if len(toks) >= 2 and len(name_norm) >= 6:
        frags.append((name_norm, "strong"))          # full normalized name
        two = " ".join(toks[:2])
        if len(two) >= 6 and toks[0] not in STOP_TOKENS:
            frags.append((two, "strong"))            # first two tokens
    elif len(toks) == 1 and len(toks[0]) >= 6 and toks[0] not in STOP_TOKENS:
        frags.append((toks[0], "weak"))              # single-word company name
    return frags


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS ii_announcements;
        DROP TABLE IF EXISTS ii_company_matches;
        CREATE TABLE ii_announcements (
            ann_id     INTEGER PRIMARY KEY,
            sector_url TEXT, sector TEXT,
            text       TEXT, source_url TEXT,
            fetched    TEXT
        );
        CREATE TABLE ii_company_matches (
            ann_id     INTEGER REFERENCES ii_announcements(ann_id),
            company_id INTEGER REFERENCES companies(company_id),
            matched_fragment TEXT,               -- kept for review
            match_quality TEXT,                  -- strong | weak (weak = review-only)
            company_visibility TEXT              -- verdict at match time
        );
        """
    )

    urls = sector_urls()
    print(f"{len(urls)} sector pages")
    with ThreadPoolExecutor(max_workers=8) as ex:
        pages = dict(zip(urls, ex.map(scrape_ticker, urls)))

    today = date.today().isoformat()
    fetch_errors = []
    for url, items in sorted(pages.items()):
        sector = url.rstrip("/").split("/")[-1]
        for text, src in items:
            if text == "__FETCH_ERROR__":
                fetch_errors.append({"url": url, "error": src})
                continue
            cur.execute(
                "INSERT INTO ii_announcements(sector_url,sector,text,source_url,fetched)"
                " VALUES (?,?,?,?,?)", (url, sector, text, src, today))

    # ---- conservative matching ----------------------------------------------
    cur.execute("""SELECT c.company_id, c.name,
                          (SELECT visibility_verdict FROM clearance_activity a
                            WHERE a.company_id=c.company_id
                              AND a.visibility_verdict IS NOT NULL LIMIT 1)
                     FROM companies c""")
    companies = [(cid, name, vis, norm(name)) for cid, name, vis in cur.fetchall()]
    cur.execute("SELECT ann_id, text FROM ii_announcements")
    anns = [(aid, " " + norm(t) + " ") for aid, t in cur.fetchall()]

    n_matches = 0
    for cid, name, vis, nn in companies:
        for frag, quality in match_fragments(nn):
            hit = [aid for aid, ntext in anns if f" {frag} " in ntext]
            if hit:
                for aid in hit:
                    cur.execute("INSERT INTO ii_company_matches VALUES (?,?,?,?,?)",
                                (aid, cid, frag, quality, vis))
                    n_matches += 1
                break   # strongest fragment wins; don't re-match weaker ones

    con.commit()

    # ---- exception validation -----------------------------------------------
    rows = cur.execute("""
        SELECT DISTINCT c.name, m.company_visibility, m.matched_fragment,
                        a.sector, a.text, a.source_url
          FROM ii_company_matches m
          JOIN companies c USING (company_id)
          JOIN ii_announcements a USING (ann_id)
         WHERE m.company_visibility IN ('QUIET','PARTIALLY_VISIBLE')
           AND m.match_quality = 'strong'
    """).fetchall()
    challenged = [
        {"company": r[0], "verdict_on_record": r[1], "matched_fragment": r[2],
         "sector_page": r[3], "announcement": r[4], "source_url": r[5],
         "implication": ("verdict CHALLENGED — the national IPA itself surfaces "
                         "this company; re-examine before citing the quiet "
                         "verdict (displayed correction, verdict not overwritten)")}
        for r in rows]

    weak_rows = cur.execute("""
        SELECT DISTINCT c.name, m.matched_fragment, a.text
          FROM ii_company_matches m
          JOIN companies c USING (company_id)
          JOIN ii_announcements a USING (ann_id)
         WHERE m.match_quality = 'weak'
    """).fetchall()
    weak_for_review = [{"company": r[0], "fragment": r[1], "announcement": r[2]}
                       for r in weak_rows]

    n_ann = cur.execute("SELECT COUNT(*) FROM ii_announcements").fetchone()[0]
    n_matched_companies = cur.execute(
        "SELECT COUNT(DISTINCT company_id) FROM ii_company_matches").fetchone()[0]

    # ---- append validation block to layer 32 JSON ---------------------------
    layer = json.load(open(LAYER))
    layer["ii_ticker_validation"] = {
        "ran": today,
        "what": ("Invest India sector-page LATEST-UPDATES tickers scraped as an "
                 "announcement channel and matched (conservatively, fragments "
                 "kept for review) against the company DB; QUIET/"
                 "PARTIALLY_VISIBLE clearance leads that the national IPA "
                 "itself announces are flagged as challenged verdicts"),
        "sector_pages_scraped": len(urls) - len(fetch_errors),
        "fetch_errors": fetch_errors,
        "announcements": n_ann,
        "companies_matched": n_matched_companies,
        "match_rows": n_matches,
        "exception_verdicts_challenged": challenged,
        "weak_matches_for_review": weak_for_review,
        "tables": ["ii_announcements", "ii_company_matches"],
        "caveat": ("ticker items are undated in the DOM and rotate — treat a "
                   "match as 'announced at some point recently', not a dated "
                   "event; source_url usually carries the date"),
    }
    with open(LAYER, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)

    print(f"announcements: {n_ann} | companies matched: {n_matched_companies} "
          f"| match rows: {n_matches} | exception verdicts challenged: {len(challenged)}")
    for c in challenged:
        print(f"  CHALLENGED [{c['verdict_on_record']}] {c['company']} <- "
              f"{c['sector_page']}: {c['announcement'][:90]}")
    con.close()


if __name__ == "__main__":
    main()
