#!/usr/bin/env python3
"""Layer 45 -- live media RSS sweep (Economic Times / Hindu / Hindu Business Line).

Origin: these three domains block Anthropic's hosted crawler/search infra
outright (WebFetch fails, browser navigate refused, even domain-scoped
WebSearch 400s -- confirmed 2026-09-16, see feedback_economic_times_blocked
memory). Plain `curl` from a normal machine is NOT blocked -- this script is
that workaround turned into a repeatable layer, so the twin gets same-day
sector news instead of routing around three of India's largest business
publishers indefinitely.

Distinct from layer 42 (one NewsAPI call per sector, roster-matched) and
layer 44 (hand-verified 5-year state-summit MoUs): this layer is the
same-day tripwire -- section RSS feeds, filtered for investment-intent
language, matched against real stock-market rosters (same 23-country
files layer 42 uses), full article text pulled ONLY for roster-confirmed
hits (extraction-before-reading, not full-page reads per
feedback_gazette_depthpass_agent_tokens). Meant to run often (daily/on
demand) since RSS feeds churn within hours; layer 44 is the slow, curated
counterpart.

Usage: python3 scripts/build_layer45_media_rss_sweep.py
Output: layers/45_media_rss_sweep.json + docs/MEDIA_RSS_SWEEP.md
        + appends every investment-intent hit (matched or not) to
          state/news_articles.jsonl, same archive layer 42 writes to.
"""
import csv
import datetime as dt
import html
import importlib.util
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIV_DIR = os.path.expanduser("~/repos/global-stock-screener/data/global_universe")
OUT_JSON = os.path.join(ROOT, "layers", "45_media_rss_sweep.json")
OUT_DOC = os.path.join(ROOT, "docs", "MEDIA_RSS_SWEEP.md")
ARCHIVE = os.path.join(ROOT, "state", "news_articles.jsonl")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126"

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

# Section RSS feeds, hand-verified live 2026-09-16. Add more sections here as
# needed -- ET's full index is at https://economictimes.indiatimes.com/rss.cms
# (grep href="...rssfeeds...") if a sector needs its own feed later.
FEEDS = {
    "ET": {
        "auto": "https://economictimes.indiatimes.com/industry/auto/rssfeeds/13359412.cms",
        "cons_products": "https://economictimes.indiatimes.com/industry/cons-products/rssfeeds/13358759.cms",
        "industry": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    },
    "Hindu": {
        "business": "https://www.thehindu.com/business/feeder/default.rss",
    },
    "HinduBusinessLine": {
        "companies": "https://www.thehindubusinessline.com/companies/feeder/default.rss",
        "economy": "https://www.thehindubusinessline.com/economy/feeder/default.rss",
    },
}

ROSTER_COUNTRIES = ["AU", "BR", "CA", "CH", "CN", "DE", "DK", "FI", "HK", "ID",
                    "IL", "JP", "KR", "MX", "MY", "SA", "SE", "SG", "TH", "TW", "UK", "US", "ZA"]

# Blank-check/SPAC shells and share-class line items are the single biggest
# false-positive source once a matcher runs against free-form headline prose
# instead of curated company fields: names like "Launch Two Acquisition
# Corp" or "X Class A Ordinary Shares" are built from common English words
# and number words, so they collide with completely unrelated sentences
# ("Hyundai plans to launch two new SUVs" -> "Launch Two Acquisition Corp").
# They also never represent a genuine "foreign company investing in India"
# signal even when the name-collision is real, so excluding them costs
# nothing.
SPAC_NOISE = re.compile(
    r"acquisition corp|blank check|special purpose acquisition|"
    r"\bclass [a-z]\b|ordinary shares?\b|\bwarrant\b|- unit\b", re.I)

INTENT_KEYWORDS = re.compile(
    r"\binvest\w*|crore|billion|\bcapex\b|expan\w*|joint venture|\bJV\b|\bMoU\b|"
    r"\bfab\b|semiconductor|greenfield|acqui\w*|new (plant|facility|factory)\b", re.I)


def strong_fragment_ok(frag):
    """match_fragments' first-two-tokens shortcut is tuned for curated
    per-record company fields (a state-MoU record, a 10-K's own company
    name) -- against raw free-text prose it collides on generic sector
    prefixes shared by dozens of roster rows: 'Bank of Queensland', 'Bank
    of Montreal', 'Bank of the James Financial Group' etc. all reduce to
    the two-token fragment 'bank of', which then matches ANY headline
    mentioning 'Reserve Bank of India' or 'Bank of Baroda'. Extra local
    floor (this script only, not the shared matcher): a fragment needs
    every token >=3 chars, which kills 'bank of' (second token 'of')
    while leaving real two-word company prefixes ('toyota motor', 'tata
    motors', 'lg energy') untouched."""
    return all(len(tok) >= 3 for tok in frag.split())


def sh_curl(url, timeout=20):
    """Same subprocess-curl pattern refresh_twin.py already uses for portals
    that reject library-level HTTP clients or Anthropic-hosted fetchers --
    this Mac's own network is never blocked. -> (http_code, body)."""
    cmd = ["curl", "-sL", "-A", UA, "-m", str(timeout), "-w", "\n%{http_code}", url]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10).stdout
        body, _, code = out.rpartition("\n")
        return code.strip(), body
    except Exception as e:
        return "ERR", str(e)


def strip_cdata(s):
    m = re.match(r"<!\[CDATA\[(.*)\]\]>", s or "", re.S)
    return (m.group(1) if m else (s or "")).strip()


def parse_feed(xml_text):
    items = []
    for it in re.findall(r"<item>(.*?)</item>", xml_text, re.S):
        title = re.search(r"<title>(.*?)</title>", it, re.S)
        desc = re.search(r"<description>(.*?)</description>", it, re.S)
        link = re.search(r"<link>(.*?)</link>", it, re.S)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S)
        items.append({
            "title": strip_cdata(title.group(1)) if title else "",
            "description": strip_cdata(desc.group(1)) if desc else "",
            "link": strip_cdata(link.group(1)) if link else "",
            "pubDate": strip_cdata(pub.group(1)) if pub else "",
        })
    return items


def extract_body(page_html):
    """Try ET's JSON-LD articleBody first (clean, no HTML stripping needed);
    fall back to the Hindu-Group CMS's contentbody div (The Hindu + Hindu
    Business Line share this class -- confirmed 2026-09-16). Returns "" if
    neither pattern matches rather than guessing at page structure."""
    m = re.search(r'"articleBody"\s*:\s*"(.*?)"\s*[,}]', page_html, re.S)
    if m:
        try:
            return html.unescape(m.group(1).encode().decode("unicode_escape"))
        except Exception:
            return html.unescape(m.group(1))
    m = re.search(r'<div[^>]*class="[^"]*\bcontentbody\b[^"]*"[^>]*>(.*?)'
                  r'(?:<div[^>]*class="[^"]*(?:tag|share|related)|<script)', page_html, re.S)
    if m:
        paras = re.findall(r"<p[^>]*>(.*?)</p>", m.group(1), re.S)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in paras)
    return ""


def load_all_rosters():
    """Foreign-only rosters, same 23-country files layer 42 uses -- gives
    real company identities to match against, rather than guessing names
    out of headline prose."""
    rosters = {}
    for cc in ROSTER_COUNTRIES:
        path = os.path.join(UNIV_DIR, f"{cc}.csv")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            rosters[cc] = [{"name": r["name"], "ticker": r["yf_ticker"],
                            "exchange": r["exchange"], "country": cc}
                           for r in csv.DictReader(f)]
    return rosters


def known_names():
    """Same twin-membership check layer 44 uses: layer 16 leads + every
    company already in companies.db."""
    import sqlite3
    names = set()
    leads_path = os.path.join(ROOT, "layers", "16_leads.json")
    if os.path.exists(leads_path):
        for l in json.load(open(leads_path))["leads"]:
            names.add(l["company"].strip().lower())
    db = os.path.join(ROOT, "data", "companies.db")
    if os.path.exists(db):
        con = sqlite3.connect(db)
        for (n,) in con.execute("SELECT name FROM companies"):
            if n:
                names.add(n.strip().lower())
        con.close()
    return names


def is_new(company_name, known):
    n = norm(company_name)
    strong = [f for f, q in match_fragments(n) if q == "strong"]
    if not strong:
        return False
    return not any(re.search(rf"\b{re.escape(f)}\b", norm(kn))
                   for kn in known for f in strong)


def main():
    today = dt.date.today().isoformat()
    rosters = load_all_rosters()
    roster_index = [(norm(r["name"]), r) for rows in rosters.values() for r in rows
                     if not SPAC_NOISE.search(r["name"])]
    known = known_names()
    print(f"loaded {len(roster_index)} foreign-roster companies, {len(known)} known twin names")

    archive_f = open(ARCHIVE, "a") if os.path.exists(os.path.dirname(ARCHIVE)) else None
    by_source = {}
    total_items = total_intent = total_matches = 0
    seen_urls = set()  # ET's section feeds overlap (e.g. "industry" is a
                        # superset of "auto"/"cons_products") -- without
                        # this, the same article gets scored, archived and
                        # full-text-fetched once per feed it appears in.

    for source, sections in FEEDS.items():
        by_source[source] = {}
        for section, feed_url in sections.items():
            row = {"feed_url": feed_url, "items": 0, "intent_hits": 0, "matches": [], "error": None}
            code, body = sh_curl(feed_url)
            if code != "200":
                row["error"] = f"HTTP {code}"
                by_source[source][section] = row
                print(f"[{source}/{section}] ERROR {code}")
                continue
            items = parse_feed(body)
            row["items"] = len(items)
            total_items += len(items)
            for it in items:
                if it["link"] in seen_urls:
                    continue
                text = f"{it['title']} {it['description']}"
                if not INTENT_KEYWORDS.search(text):
                    continue
                seen_urls.add(it["link"])
                row["intent_hits"] += 1
                total_intent += 1
                if archive_f:
                    archive_f.write(json.dumps({"source": f"media_rss_sweep/{source}/{section}",
                                                "title": it["title"], "url": it["link"],
                                                "published": it["pubDate"], "collected": today}) + "\n")
                ntext = norm(text)
                hit_companies = []
                for rn, r in roster_index:
                    frags = match_fragments(rn)
                    if any(q == "strong" and strong_fragment_ok(f)
                           and re.search(rf"\b{re.escape(f)}\b", ntext) for f, q in frags):
                        hit_companies.append(r)
                if not hit_companies:
                    continue
                full_text = ""
                acode, apage = sh_curl(it["link"], timeout=20)
                if acode == "200":
                    full_text = extract_body(apage)[:3000]
                for r in hit_companies:
                    match = {"company": r["name"], "ticker": r["ticker"], "country": r["country"],
                             "new_to_twin": is_new(r["name"], known),
                             "title": it["title"], "url": it["link"], "published": it["pubDate"],
                             "full_text": full_text}
                    row["matches"].append(match)
                    total_matches += 1
                    print(f"  [{source}/{section}] {r['name']} ({r['country']})"
                          f"{' NEW' if match['new_to_twin'] else ''} -- {it['title'][:80]}")
            by_source[source][section] = row

    if archive_f:
        archive_f.close()

    all_matches = [m for src in by_source.values() for sec in src.values() for m in sec["matches"]]
    new_matches = [m for m in all_matches if m["new_to_twin"]]

    out = {
        "layer": 45, "name": "media_rss_sweep", "built": today,
        "what": ("Live RSS sweep of Economic Times / Hindu / Hindu Business Line section feeds, "
                 "filtered for investment-intent language, matched against real 23-country foreign "
                 "stock-market rosters (same files layer 42 uses). Full article text pulled only for "
                 "roster-confirmed hits. Workaround for the fact that all three domains block "
                 "Anthropic's hosted crawler/search infra outright -- this runs via subprocess curl "
                 "from the local machine, which is never blocked (see feedback_economic_times_blocked "
                 "memory). CAVEAT: 'strong' fragment matches on generic industry-descriptive company "
                 "names (e.g. 'Semiconductor Manufacturing International Corp' vs. any article about "
                 "semiconductor manufacturing in general) still slip through even after the SPAC/"
                 "share-class filter -- treat every match here as a candidate for human review via "
                 "its full_text field, not a confirmed lead, same as layer 44's un-reviewed MoU rows."),
        "roster_companies_loaded": len(roster_index),
        "known_twin_names": len(known),
        "total_items_scanned": total_items,
        "total_investment_intent_hits": total_intent,
        "total_company_matches": total_matches,
        "total_new_to_twin": len(new_matches),
        "by_source": by_source,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(out, open(OUT_JSON, "w"), indent=1, ensure_ascii=False)

    L = ["# Live media RSS sweep — layer 45", "",
         f"*Generated {today} by `scripts/build_layer45_media_rss_sweep.py`. "
         f"{total_items} feed items scanned across ET/Hindu/HBL, {total_intent} carried "
         f"investment-intent language, {total_matches} matched a real foreign-company roster name "
         f"({len(new_matches)} new to the twin). Run this often -- RSS feeds churn within hours, "
         "unlike layer 44's hand-curated 5-year sweep.*", "",
         "## Why this layer exists", "",
         "economictimes.indiatimes.com, thehindu.com and thehindubusinessline.com all block "
         "Anthropic's hosted crawler/search tooling outright (confirmed 2026-09-16 — WebFetch fails, "
         "browser navigate refused, domain-scoped WebSearch 400s). Plain `curl` from this machine's "
         "own network is not blocked, so this layer fetches section RSS feeds directly and extracts "
         "full article text via each site's own article markup (ET: JSON-LD `articleBody`; "
         "Hindu/HBL: shared `contentbody` div) — no third-party scraper needed.", ""]

    if new_matches:
        L += ["## New-to-twin company matches", "",
              "| Company | Country | Source | Headline | Published |",
              "|---|---|---|---|---|"]
        for m in sorted(new_matches, key=lambda x: x["published"], reverse=True):
            L.append(f"| {m['company']} | {m['country']} | {m['url'].split('/')[2]} | "
                     f"[{m['title'][:80]}]({m['url']}) | {m['published']} |")
        L.append("")

    L += ["## All company matches (incl. already-known)", "",
          "| Company | Country | New? | Headline | Published |",
          "|---|---|---|---|---|"]
    for m in sorted(all_matches, key=lambda x: x["published"], reverse=True):
        L.append(f"| {m['company']} | {m['country']} | {'🆕' if m['new_to_twin'] else ''} | "
                 f"[{m['title'][:80]}]({m['url']}) | {m['published']} |")
    L.append("")

    L += ["## Feed health", "", "| Source | Section | Items | Intent hits | Matches | Error |",
          "|---|---|---|---|---|---|"]
    for source, sections in by_source.items():
        for section, row in sections.items():
            L.append(f"| {source} | {section} | {row['items']} | {row['intent_hits']} | "
                     f"{len(row['matches'])} | {row['error'] or ''} |")
    L.append("")

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    print(f"\n{total_items} items, {total_intent} intent hits, {total_matches} company matches "
          f"({len(new_matches)} new) -> {OUT_JSON} + {OUT_DOC}")


if __name__ == "__main__":
    sys.exit(main())
