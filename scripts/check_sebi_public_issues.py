#!/usr/bin/env python3
"""Layer 32 enrichment — SEBI public-issues (DRHP/RHP) cross-check.

Answers: which companies the twin has analysed are MOVING TO THE STOCK MARKET
for funding? Pages through SEBI's public-issues filing list (DRHP / UDRHP /
RHP / addenda — the actual listing pipeline, not news) and matches filers
against the company DB with the shared tiered matcher.

Endpoint (found 2026-07-23, works with a plain POST — no cookies needed):
  POST https://www.sebi.gov.in/sebiweb/ajax/home/getnewslistinfo.jsp
  data: nextValue=<page>&next=n&sid=3&ssid=15&smid=10&intmid=-1...
  -> HTML fragment, 25 rows/page, ~87 pages (2,160 records)

Tables (companies.db): sebi_filings, sebi_company_matches.
Appends `sebi_public_issues` block to layers/32_company_db.json.

Usage: python3 scripts/check_sebi_public_issues.py [--since 2025-01-01] [--max-pages 60]
"""
import argparse
import importlib.util
import json
import os
import re
import sqlite3
import time
import urllib.parse
import urllib.request
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
LAYER = os.path.join(ROOT, "layers", "32_company_db.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
AJAX = "https://www.sebi.gov.in/sebiweb/ajax/home/getnewslistinfo.jsp"

_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments


def fetch_page(page):
    data = urllib.parse.urlencode({
        "nextValue": page, "next": "n", "search": "", "fromDate": "",
        "toDate": "", "fromYear": "", "toYear": "", "deptId": "",
        "sid": 3, "ssid": 15, "smid": 10, "intmid": -1, "sText": "",
        "Statutes": "", "fromResults": "", "toResults": ""}).encode()
    req = urllib.request.Request(AJAX, data=data, headers={
        "User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.sebi.gov.in/filings/public-issues.html"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def parse_rows(html):
    rows = []
    for m in re.finditer(
            r"<td>([A-Z][a-z]{2} \d{2}, \d{4})</td><td><a href='([^']+)'[^>]*"
            r"title=\"([^\"<]+)", html):
        d = datetime.strptime(m.group(1), "%b %d, %Y").date()
        rows.append((d.isoformat(), m.group(3).strip(), m.group(2)))
    return rows


def filing_company(title):
    """'Aastha Spintex Limited - Addendum to DRHP' -> company + doc type."""
    parts = title.split(" - ", 1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-01-01")
    ap.add_argument("--max-pages", type=int, default=60)
    args = ap.parse_args()
    today = date.today().isoformat()

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS sebi_filings (
            filing_id INTEGER PRIMARY KEY,
            filed     TEXT, company TEXT, doc_type TEXT,
            title TEXT, url TEXT UNIQUE, fetched TEXT);
        CREATE TABLE IF NOT EXISTS sebi_company_matches (
            filing_id  INTEGER REFERENCES sebi_filings(filing_id),
            company_id INTEGER REFERENCES companies(company_id),
            matched_fragment TEXT, match_quality TEXT,
            company_visibility TEXT,
            UNIQUE(filing_id, company_id));
    """)

    n_new, pages = 0, 0
    for page in range(args.max_pages):
        try:
            html = fetch_page(page)
        except Exception as e:
            print(f"page {page} fetch failed: {type(e).__name__}")
            break
        rows = parse_rows(html)
        if not rows:
            break
        pages += 1
        for filed, title, url in rows:
            comp, doc = filing_company(title)
            cur.execute("INSERT OR IGNORE INTO sebi_filings"
                        "(filed,company,doc_type,title,url,fetched)"
                        " VALUES (?,?,?,?,?,?)",
                        (filed, comp, doc, title, url, today))
            n_new += cur.rowcount
        if min(r[0] for r in rows) < args.since:
            break
        time.sleep(0.4)
    con.commit()

    # tiered matching: DB companies vs filer names (and filer names vs DB names,
    # since either side may be the longer string)
    cur.execute("""SELECT c.company_id, c.name,
                          (SELECT visibility_verdict FROM clearance_activity a
                            WHERE a.company_id=c.company_id
                              AND a.visibility_verdict IS NOT NULL LIMIT 1)
                     FROM companies c""")
    companies = [(cid, nm, vis, norm(nm)) for cid, nm, vis in cur.fetchall()]
    cur.execute("SELECT filing_id, company FROM sebi_filings WHERE filed >= ?",
                (args.since,))
    filings = [(fid, norm(cn)) for fid, cn in cur.fetchall()]
    n_match = 0
    for cid, nm, vis, nn in companies:
        for frag, quality in match_fragments(nn):
            hits = [fid for fid, fnorm in filings
                    if f" {frag} " in f" {fnorm} " or fnorm == frag]
            if hits:
                for fid in hits:
                    cur.execute("INSERT OR IGNORE INTO sebi_company_matches"
                                " VALUES (?,?,?,?,?)", (fid, cid, frag, quality, vis))
                    n_match += cur.rowcount
                break
    con.commit()

    rows = cur.execute("""
        SELECT DISTINCT c.name, m.company_visibility, m.match_quality,
                        f.filed, f.title, f.url
          FROM sebi_company_matches m
          JOIN companies c USING (company_id)
          JOIN sebi_filings f USING (filing_id)
         WHERE f.filed >= ? ORDER BY f.filed DESC""", (args.since,)).fetchall()
    matches = [{"company": r[0], "visibility": r[1], "quality": r[2],
                "filed": r[3], "filing": r[4], "url": r[5]} for r in rows]

    n_f = cur.execute("SELECT COUNT(*) FROM sebi_filings WHERE filed >= ?",
                      (args.since,)).fetchone()[0]
    summary = {
        "ran": today, "since": args.since, "pages_fetched": pages,
        "filings_in_window": n_f, "new_rows": n_new,
        "match_rows": n_match,
        "companies_moving_to_market": matches[:40],
        "what": ("SEBI public-issues (DRHP/UDRHP/RHP) filers matched onto the "
                 "company DB — the listing pipeline as a funding signal; shared "
                 "tiered matcher (strong/reviewed-promoted actionable, weak "
                 "review-only)"),
    }
    layer = json.load(open(LAYER))
    layer["sebi_public_issues"] = summary
    with open(LAYER, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "companies_moving_to_market"}, indent=1))
    for m in matches:
        print(f"  [{m['quality']}] {m['company']}  <- {m['filed']}: {m['filing'][:70]}")
    con.close()


if __name__ == "__main__":
    main()
