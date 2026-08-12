#!/usr/bin/env python3
"""Switzerland India-sweep -- sibling to build_oslo_newsweb_india_sweep.py /
build_dart_india_sweep.py / build_cninfo_india_sweep.py / build_esef_xbrl_india_sweep.py.

Switzerland has no EDGAR/DART/EDINET equivalent -- no single central regulator
publishes a searchable full-text filing archive, and Switzerland is NOT in the
EU/UK ESEF/UKSEF regime (verified live 2026-08-12: filings.xbrl.org's
/api/filings?filter[country]=CH returns zero results -- confirmed, not
assumed). Candidates tried, in order, all tested live before committing:
  1. SIX Exchange Regulation's own Art. 53 ad-hoc-publicity archive --
     found: six-group.com's "Official Notices" tool
     (sheldon/official_notices/v2/find.json) is real and keyless, but it only
     covers STRUCTURED product/connexor events (barrier events, ex-dividend
     notices...), not prose disclosure text -- not useful for a text sweep.
  2. SIX's own "Equity Issuer News" tool -- THIS is the one that works.
     Network-traced (not documented) endpoint:
     six-group.com/en/market-data/news-tools/equity-issuer-news/_jcr_content/
     sections/section/content/equity_issuer_news.equityissuer.json
     ?from=YYYYMMDD&to=YYYYMMDD&pageNumber=0&pageSize=<n>
     Keyless, confirmed live 2026-08-12: returns FULL press-release body text
     (not just titles, unlike Oslo NewsWeb) in up to 4 languages (en/de/fr/it)
     per item, each item flagged `ad_hoc` (Art. 53 disclosure) true/false.
     total=1748 items in one page with pageSize=2000 -- the whole corpus in a
     single HTTP call. BUT the feed's actual retained history is only ~15
     months (2025-04-30 to 2026-08-12 in this run), not the multi-year
     archive Oslo NewsWeb offers -- despite requesting from=2015-01-01, only
     the live rolling window is returned. Recorded as a real corpus-size
     limit, not silently. 141 distinct issuers appear in that window (of 205
     Swiss-domiciled SIX equity issuers per the corrected roster below) --
     covers the largest/most-active names by construction (a company only
     appears if it published news in the window), which is exactly the
     "prioritize the largest/most likely-relevant companies" fallback this
     task asked for if per-company IR scraping were needed -- it wasn't:
     this source made a 192-company one-by-one IR-site crawl unnecessary.
  3. Per-company IR-site annual-report crawl -- NOT NEEDED; source #2 covers
     it with far less scraping surface and gives full body text already.
  4. filings.xbrl.org (ESEF/UKSEF) -- tested live, CH returns 0 (Switzerland
     is not EU/UK, confirmed rather than assumed per the task brief).

STEP 0 -- roster verification (done first, per instruction, before the sweep
itself): the sibling global-stock-screener repo's
data/global_universe/CH.csv (192 rows) was NOT taken on faith. Cross-checked
live against SIX's own authoritative "List of Equity Issuers"
(six-group.com/sheldon/equity_issuers/v1/equity_issuers.json, confirmed live
2026-08-12): 241 total issuers on SIX, of which 205 are Swiss-domiciled
(country=CH) -- the rest are cross-listed foreign primary/secondary listings
(3M, Abbott, ams-OSRAM AT, Bajaj Mobility AT, 17 mainland-Chinese GDR
listings under a "10" pseudo-country code) correctly excluded from a
"Switzerland" roster. Delta vs CH.csv: 15 live CH issuers were MISSING from
CH.csv, including Roche Holding AG (both share classes, RO/ROP -- one of
Switzerland's three largest companies by market cap) and The Swatch Group AG
(UHRN) -- not obscure names. CH.csv's `name` column was also 100% blank
across all 192 existing rows (tickers only). FIXED live in this run: CH.csv
rewritten in place (same 4-column schema: yf_ticker,name,exchange,market) --
15 missing rows added, `name` backfilled for all 205 matched tickers from
the authoritative SIX company names. 2 CH.csv tickers (YTME, ZWM) were not
found anywhere in the live 241-issuer list -- flagged as likely
delisted/renamed but NOT deleted (could not independently confirm the cause
live); recorded in this script's roster_verification block, not silently
dropped. This CH.csv fix lives in the SIBLING repo
(~/repos/global-stock-screener), left as an uncommitted working-tree change,
same as every other file this task touched -- nothing was committed or
pushed in either repo. NOTE for a future pass: CH.csv shipping with a fully
blank name column and 15 missing issuers (before this fix) suggests the same
pattern -- staleness, missing recent listings, unpopulated name fields --
plausibly generalizes to the sibling per-country CSVs in that same directory
(SE.csv, DK.csv, DE.csv, CA.csv, CN.csv, UK.csv, HK.csv, EU.csv); NOT checked
here, flagged only as an observation for a possible follow-up.

PRECISION HAZARDS found and fixed, live, in the sweep itself (every prior
sweep in this family found one; this one found three):
  1. Boilerplate repetition: the same company footprint sentence (e.g.
     Gurit's "Gurit operates production sites and offices in ... India ...")
     is repeated near-verbatim in EVERY one of that company's press
     releases -- 93 raw India-mentioning news items collapse to a much
     smaller set of genuinely distinct facts once repeated boilerplate is
     dedup'd. Fixed by fingerprinting each hit on
     (company, normalized India-sentence-text) -- normalization strips ALL
     punctuation before hashing (an early version that only lowercased text
     under-deduplicated: minor PR-template punctuation drift, e.g. an Oxford
     comma present in one Gurit release's boilerplate and absent in another,
     defeated an exact-string fingerprint).
  2. Context-only false positives: India mentioned in a TB disease-burden
     statistics list ("India (25%), Indonesia (10%)...", BioVersys) or a
     retiring executive's career biography ("held various roles across
     India, Switzerland...", Nestle / a board nominee's bio, Interroll) is a
     real substring match but NOT a company-disclosed India business signal
     -- excluded into context_only, not silently dropped, not counted as a
     lead.
  3. Reverse-direction hits: PIERER Mobility AG's (now renamed Bajaj
     Mobility AG) press releases disclose that Bajaj Auto -- an INDIAN
     company -- took a controlling stake in the Swiss/Austrian-domiciled
     issuer. That is Indian investment INTO a SIX-listed company, the
     OPPOSITE of what this sweep is mining for (a foreign/Swiss company's
     disclosed interest in India). Detected via the EQS major-shareholder
     notification-obligation form pattern ("notification obligation" +
     "Country: Indien") and the "India has taken control of" construction;
     excluded into reverse_direction, kept for transparency, never counted
     as a lead.

Usage: python3 scripts/build_switzerland_india_sweep.py
Output: layers/16_enrichment/switzerland_india_sweep.json
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "16_enrichment", "switzerland_india_sweep.json")
SIBLING_UNIV_DIR = os.path.expanduser("~/repos/global-stock-screener/data/global_universe")
CH_CSV = os.path.join(SIBLING_UNIV_DIR, "CH.csv")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
ISSUERS_URL = "https://www.six-group.com/sheldon/equity_issuers/v1/equity_issuers.json"
NEWS_URL = ("https://www.six-group.com/en/market-data/news-tools/equity-issuer-news/"
            "_jcr_content/sections/section/content/equity_issuer_news.equityissuer.json")
ESEF_URL = "https://filings.xbrl.org/api/filings"

INDIA_RE = re.compile(r"\bIndia\b|\bIndien\b|\bInde\b")
TAG_RE = re.compile(r"<[^>]+>")
SENT_SPLIT_RE = re.compile(r"(?<!\bU\.S)(?<!\bU\.K)(?<=[.!?])\s+(?=[A-Z])")
PUNCT_RE = re.compile(r"[^a-z0-9]+")

# Category #2 hazard: statistics lists ("India (25%), Indonesia (10%)...")
STATS_LIST_RE = re.compile(r"\bIndia\s*\(\s*\d{1,3}\s*%\s*\)")
# Category #2 hazard: personnel/career biography mentions
BIO_RE = re.compile(
    r"(held various (roles|positions)|career (spanning|of more than)|"
    r"cross-cultural leadership).{0,80}India|India.{0,80}(held various|"
    r"career (spanning|of more than))", re.I)
# Category #3 hazard: reverse-direction (Indian entity acquiring the Swiss issuer)
REVERSE_NOTIFY_RE = re.compile(r"notification obligation", re.I)
REVERSE_COUNTRY_RE = re.compile(r"Country:\s*Indien", re.I)
REVERSE_CONTROL_RE = re.compile(r"India\s+has\s+taken\s+control\s+of", re.I)

EXIT_RE = re.compile(
    r"\b(exit\w*|divest\w*|disposal|sold|sale of|ceases?|ceasing|terminat\w*|withdraw\w*)\b", re.I)
ENTRY_RE = re.compile(
    r"\b(entry into|enters?\b|expansion|expand\w*|establish\w*|incorporated|new legal entity|"
    r"new (production )?plant|new project|new facilit\w*|subsidiary|initial public offering|"
    r"\bipo\b|invests?\b|investment in|acquisition of|acquir\w*|awarded|new contract|"
    r"regulatory approval|completion of the production plant|new supply agreement)\b", re.I)

# Two more live-found precision refinements on top of the classify() keyword match:
# (a) a "which included a major project..." construction is a PRIOR-YEAR comparison
#     baseline being restated for a revenue-delta explanation, not new news this period
#     (Huber+Suhner's India infrastructure project, referenced retrospectively in 3
#     separate quarterly releases without ever being newly announced in any of them).
RETROSPECTIVE_RE = re.compile(
    r"(compared (to|with).{0,80}which included|prior-year period,? which included|"
    r"which included (the|a).{0,40}(project|gain))", re.I)
# (b) "expansion"/"footprint" qualified by a diffuse 3+-country list (not India-specific
#     concrete action) is too vague to count as an India investment signal on its own
#     (Straumann: "further expansion in Australia, India, Japan, and Vietnam").
VAGUE_MULTI_COUNTRY_RE = re.compile(
    r"(expansion|footprint) in ([A-Z][a-zA-Z]+,\s*){2,}(and\s+)?[A-Z][a-zA-Z]+", re.I)
# (c) "tender offer to acquire <this issuer>" means a THIRD PARTY is acquiring the SIX
#     issuer itself -- "acquisition of"/"acquir*" in that context describes the deal
#     acquiring the Swiss company, not the Swiss company acquiring something in India
#     (PolyPeptide/Samsung Biologics: India is only mentioned as an existing facility
#     location in the same press release, not as the acquisition's subject).
SELF_ACQUISITION_TARGET_RE = re.compile(r"tender offer to acquire", re.I)

LANG_PRIORITY = ["en", "de", "fr", "it"]


def get_json(url, params=None, timeout=30):
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def strip_html(html: str) -> str:
    html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html or "", flags=re.S)
    text = TAG_RE.sub(" ", html)
    text = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fingerprint(company: str, sentences: list[str]) -> str:
    norm = PUNCT_RE.sub(" ", (company + "|" + "|".join(sentences)).lower())
    norm = re.sub(r"\s+", " ", norm).strip()
    return hashlib.sha1(norm.encode()).hexdigest()[:16]


def classify(snippet: str, title: str) -> str:
    if EXIT_RE.search(snippet):
        return "exit_or_divestment"
    if ENTRY_RE.search(snippet):
        if RETROSPECTIVE_RE.search(snippet):
            return "business_activity"
        if VAGUE_MULTI_COUNTRY_RE.search(snippet) and not re.search(
                r"\b(plant|facilit\w*|legal entity|office|subsidiary)\b", snippet, re.I):
            return "business_activity"
        if SELF_ACQUISITION_TARGET_RE.search(title or ""):
            return "business_activity"
        return "market_entry_or_investment"
    return "business_activity"


# ---------------------------------------------------------------------------
# Step 0: verify + (if needed) correct the sibling repo's CH.csv roster
# ---------------------------------------------------------------------------
def verify_roster(issuers: list[dict]) -> dict:
    ch_live = {x["valorSymbol"]: x for x in issuers if x.get("country") == "CH"}
    report = {
        "source": ISSUERS_URL,
        "checked_live": dt.date.today().isoformat(),
        "total_six_equity_issuers": len(issuers),
        "live_ch_domiciled_issuers": len(ch_live),
        "excluded_non_ch_domiciled_note": (
            "of the total, non-CH entries are cross-listed foreign issuers (US names like "
            "3M/Abbott, ams-OSRAM AT, Bajaj Mobility AT) and 17 mainland-China GDR listings "
            "under a non-country '10' code -- excluded from the Switzerland roster"),
    }
    if not os.path.exists(CH_CSV):
        report["status"] = f"CH.csv not found at {CH_CSV} -- skipped roster fix"
        return report

    with open(CH_CSV) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        existing = list(reader)
    existing_by_symbol = {r["yf_ticker"].replace(".SW", ""): r for r in existing}

    missing = sorted(set(ch_live) - set(existing_by_symbol))
    stale = sorted(set(existing_by_symbol) - set(ch_live))

    merged = {}
    for sym, row in existing_by_symbol.items():
        name = ch_live[sym]["company"] if sym in ch_live else row.get("name", "")
        merged[sym] = {"yf_ticker": sym + ".SW", "name": name, "exchange": "CH", "market": "CH"}
    for sym in missing:
        merged[sym] = {"yf_ticker": sym + ".SW", "name": ch_live[sym]["company"],
                        "exchange": "CH", "market": "CH"}

    report.update({
        "chcsv_path": CH_CSV,
        "chcsv_before_count": len(existing),
        "chcsv_before_names_populated": sum(1 for r in existing if r.get("name")),
        "chcsv_after_count": len(merged),
        "missing_from_chcsv_added": [
            {"ticker": s + ".SW", "company": ch_live[s]["company"], "isin": ch_live[s]["isin"]}
            for s in missing],
        "stale_in_chcsv_not_found_live": stale,
        "stale_note": ("present in CH.csv but not found anywhere in the live 241-issuer list -- "
                       "likely delisted/renamed; NOT removed (cause not independently "
                       "confirmed live), flagged only"),
    })

    if missing or any(not r.get("name") for r in existing):
        with open(CH_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for sym in sorted(merged):
                w.writerow(merged[sym])
        report["status"] = (f"UPDATED live: added {len(missing)} missing issuer(s), backfilled "
                             f"name for {len(merged) - report['chcsv_before_names_populated']} "
                             "rows that had a blank name column. Left as an uncommitted "
                             "working-tree change in the sibling repo -- not committed/pushed.")
    else:
        report["status"] = "CH.csv already complete and current vs the live SIX issuer list -- no changes made."
    return report


def check_esef_ch() -> dict:
    """Confirm (not assume) Switzerland is outside the ESEF/UKSEF regime."""
    try:
        d = get_json(ESEF_URL, {"filter[country]": "CH", "page[size]": 5})
        n = len(d.get("data", []))
        return {"checked_live": True, "ch_filings_found": n,
                "verdict": ("CH not in ESEF/UKSEF regime, confirmed live -- 0 filings" if n == 0
                             else f"unexpected: {n} CH filings found on filings.xbrl.org")}
    except Exception as e:
        return {"checked_live": True, "error": f"{type(e).__name__}: {e}"}


def fetch_all_news(since="20150101"):
    today = dt.date.today().strftime("%Y%m%d")
    items, page_size, offset = [], 500, 0
    while True:
        d = get_json(NEWS_URL, {"from": since, "to": today, "pageNumber": offset // page_size,
                                 "pageSize": page_size})
        batch = d.get("data", [])
        items.extend(batch)
        total = d.get("total", len(items))
        offset += len(batch)
        if not batch or offset >= total:
            return items, total


def main():
    print("Step 0: verifying Switzerland CH.csv roster against SIX's live equity-issuer list...")
    issuers_resp = get_json(ISSUERS_URL)
    issuers = issuers_resp.get("itemList", [])
    roster_report = verify_roster(issuers)
    print(f"  {roster_report['status']}")
    isin_to_ticker = {x["isin"]: x["valorSymbol"] for x in issuers if x.get("country") == "CH"}

    esef_check = check_esef_ch()
    print(f"  ESEF/UKSEF check: {esef_check.get('verdict', esef_check.get('error'))}")

    print("\nStep 1: fetching SIX Equity Issuer News (full corpus, keyless)...")
    news_items, total = fetch_all_news()
    print(f"  fetched {len(news_items)} of {total} equity issuer news items")
    ad_hoc_count = sum(1 for x in news_items if x.get("ad_hoc"))
    dates = [x["news_date"] for x in news_items if x.get("news_date")]
    date_range = None
    if dates:
        date_range = [dt.date.fromtimestamp(min(dates) / 1000).isoformat(),
                       dt.date.fromtimestamp(max(dates) / 1000).isoformat()]

    print("\nStep 2: sweeping for India mentions + local classification...")
    raw_hits = []
    for item in news_items:
        contents = {c["language"]: c for c in item.get("content", [])}
        for lang in LANG_PRIORITY:
            c = contents.get(lang)
            if not c:
                continue
            text = strip_html(c.get("content", "")) + " " + (c.get("title") or "")
            if not INDIA_RE.search(text):
                continue
            sents = [s.strip() for s in SENT_SPLIT_RE.split(text) if INDIA_RE.search(s)]
            snippet = " ".join(sents)[:600]
            company = item["company"]["name"]
            isin = item["company"].get("isin")
            raw_hits.append({
                "news_id": item["id"], "company": company, "isin": isin,
                "ticker": isin_to_ticker.get(isin),
                "ad_hoc": item.get("ad_hoc"),
                "news_date": (dt.date.fromtimestamp(item["news_date"] / 1000).isoformat()
                              if item.get("news_date") else None),
                "lang": lang, "title": c.get("title"), "snippet": snippet,
                "fingerprint": fingerprint(company, sents),
            })
            break  # one row per news item, first matched language in priority order

    print(f"  raw India-mentioning news items: {len(raw_hits)}")

    # Hazard #1: collapse boilerplate -- keep first occurrence per (company, fingerprint)
    deduped, seen = [], set()
    boilerplate_collapsed = 0
    for h in sorted(raw_hits, key=lambda r: r["news_date"] or ""):
        key = (h["company"], h["fingerprint"])
        if key in seen:
            boilerplate_collapsed += 1
            continue
        seen.add(key)
        deduped.append(h)
    print(f"  after boilerplate dedup: {len(deduped)} ({boilerplate_collapsed} duplicate "
          "boilerplate repeats collapsed)")

    # Hazards #2 and #3: exclude context-only and reverse-direction hits
    context_only, reverse_direction, actionable = [], [], []
    for h in deduped:
        s = h["snippet"]
        if STATS_LIST_RE.search(s) or BIO_RE.search(s):
            context_only.append(h)
        elif REVERSE_CONTROL_RE.search(s) or (REVERSE_NOTIFY_RE.search(s) and REVERSE_COUNTRY_RE.search(s)):
            reverse_direction.append(h)
        else:
            actionable.append(h)

    for h in actionable:
        h["tier"] = classify(h["snippet"], h.get("title") or "")

    entry = [h for h in actionable if h["tier"] == "market_entry_or_investment"]
    business = [h for h in actionable if h["tier"] == "business_activity"]
    exits = [h for h in actionable if h["tier"] == "exit_or_divestment"]

    out = {
        "layer": "16_enrichment/switzerland_india_sweep",
        "built": dt.date.today().isoformat(),
        "method": ("SIX's 'Equity Issuer News' tool (network-traced JSON endpoint, keyless, "
                   "confirmed live 2026-08-12) -- full press-release body text (en/de/fr/it), "
                   "not title-only. SIX's 'Official Notices' feed was tried first but only "
                   "covers structured product events, no prose. filings.xbrl.org/ESEF confirmed "
                   "live to have zero CH filings (Switzerland outside the ESEF/UKSEF regime). "
                   "No per-company IR-site crawl needed -- this source already gives full body "
                   "text. India/Indien/Inde matched with \\b word boundaries, then classified "
                   "into market_entry_or_investment / business_activity / exit_or_divestment, "
                   "with two exclusion buckets for hazards found live: context_only (disease-"
                   "burden statistics lists, personnel career bios) and reverse_direction "
                   "(an Indian company acquiring the Swiss issuer itself, not the other way)."),
        "esef_xbrl_check": esef_check,
        "roster_verification": roster_report,
        "corpus": {
            "total_equity_issuer_news_items": total,
            "fetched": len(news_items),
            "date_range_actual": date_range,
            "date_range_note": ("requested from 2015-01-01 but the feed's retained history is "
                                 "only the live rolling window shown above -- smaller than Oslo "
                                 "NewsWeb's 2015-2026 archive, recorded as a real corpus limit"),
            "distinct_issuers_in_window": len({x["company"]["name"] for x in news_items}),
            "ad_hoc_flagged": ad_hoc_count,
        },
        "raw_india_mentioning_items": len(raw_hits),
        "boilerplate_duplicates_collapsed": boilerplate_collapsed,
        "unique_facts_after_dedup": len(deduped),
        "excluded_context_only": context_only,
        "excluded_reverse_direction": reverse_direction,
        "market_entry_or_investment": entry,
        "business_activity": business,
        "exit_or_divestment": exits,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

    print(f"\nexcluded context_only: {len(context_only)} | excluded reverse_direction: "
          f"{len(reverse_direction)}")
    print(f"market_entry_or_investment: {len(entry)} | business_activity: {len(business)} | "
          f"exit_or_divestment: {len(exits)} -> {OUT}")
    for e in entry:
        print(f"  ENTRY: {e['company']} ({e['ticker']}) -- {e['title']}")
    for e in exits:
        print(f"  EXIT: {e['company']} ({e['ticker']}) -- {e['title']}")


if __name__ == "__main__":
    main()
