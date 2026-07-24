#!/usr/bin/env python3
"""Layer 34 register — IBBI liquidation auction notices (the real stressed-asset feed).

The one machine-readable per-asset stressed-asset register in India: IBBI
publishes every liquidation e-auction as a server-rendered table row with
structured fields (corporate debtor, auction date, reserve price, nature of
assets, EMD deadline) + the notice PDF. ~481 pages × 20 rows back to inception.

  https://ibbi.gov.in/liquidation-auction-notices/lists?page=N   (no auth)

This collector:
  - pages the table (default: recent --pages, or --all for the full ~9,600)
  - parses rows into structured records
  - writes a durable parquet (data/registers/ibbi_liquidation.parquet, duckdb)
    AND an ibbi_auction_notices table in companies.db
  - cross-matches corporate-debtor names against the twin's companies table
    using the SHARED tiered matcher — turning the aggregate 'IBC liquidation'
    pool of layer 34 into named assets linked to tracked companies
  - appends a `register` block to layers/34_stressed_assets.json

Run with /usr/bin/python3 (duckdb lives there). Durable across the weekly DB
wipe: the parquet is the system of record; the DB table is rebuilt from it.
Usage: /usr/bin/python3 scripts/register_ibbi_liquidation.py [--pages N | --all]
"""
import argparse
import importlib.util
import json
import os
import re
import sqlite3
import time
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
LAYER = os.path.join(ROOT, "layers", "34_stressed_assets.json")
OUTDIR = os.path.join(ROOT, "data", "registers")
PARQUET = os.path.join(OUTDIR, "ibbi_liquidation.parquet")
BASE = "https://ibbi.gov.in/liquidation-auction-notices/lists"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# shared tiered matcher (norm, match_fragments, REVIEWED_WEAK_OK)
_spec = importlib.util.spec_from_file_location(
    "iiticker", os.path.join(ROOT, "scripts", "enrich_company_db_ii_tickers.py"))
_ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ii)
norm, match_fragments = _ii.norm, _ii.match_fragments

def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def parse_price(s):
    s = (s or "").replace(",", "").strip()
    return int(s) if s.isdigit() else None


def _celltext(c):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()


def parse_rows(html):
    """Each data <tr> has 10 <td> cells:
    0 AN type · 1 notice date · 2 corporate debtor · 3 auction date ·
    4 IP · 5 notice PDF · 6 reserve price · 7 nature of assets ·
    8 EMD last date · 9 details PDF."""
    html = re.sub(r"\s+", " ", html)
    out = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        if "auction_notice_liquidation" not in tr:
            continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(cells) < 9:
            continue
        pdf = re.search(r"href=(\S+?\.pdf)", cells[5])
        out.append({
            "an_type": _celltext(cells[0]),
            "notice_date": _celltext(cells[1]),
            "corporate_debtor": _celltext(cells[2]),
            "auction_date": _celltext(cells[3]),
            "insolvency_professional": _celltext(cells[4]),
            "notice_pdf": pdf.group(1) if pdf else _celltext(cells[5]),
            "reserve_price_inr": parse_price(_celltext(cells[6])),
            "nature_of_assets": _celltext(cells[7]),
            "emd_last_date": _celltext(cells[8]),
        })
    return out


def scrape(pages):
    out = []
    for p in pages:
        url = BASE if p == 1 else f"{BASE}?page={p}"
        try:
            html = get(url)
        except Exception as e:
            print(f"  page {p}: FETCH FAIL {type(e).__name__}")
            break
        rows = parse_rows(html)
        if not rows:
            print(f"  page {p}: 0 rows (end?)")
            break
        out.extend(rows)
        print(f"  page {p}: {len(rows)} rows")
        time.sleep(0.4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=25,
                    help="recent pages to scrape (20 rows each)")
    ap.add_argument("--all", action="store_true", help="scrape all ~481 pages")
    args = ap.parse_args()
    today = date.today().isoformat()
    os.makedirs(OUTDIR, exist_ok=True)

    pages = range(1, (482 if args.all else args.pages + 1))
    print(f"scraping {'ALL' if args.all else args.pages} pages...")
    records = scrape(pages)
    # dedupe by notice_pdf (stable id)
    seen, uniq = set(), []
    for r in records:
        if r["notice_pdf"] not in seen:
            seen.add(r["notice_pdf"]); uniq.append(r)
    print(f"parsed {len(uniq)} unique notices")

    # ---- merge into durable parquet (union with prior, dedupe) --------------
    import duckdb
    dcon = duckdb.connect()
    dcon.execute("CREATE TABLE new_notices AS SELECT * FROM (VALUES " +
                 ",".join("(?,?,?,?,?,?,?,?,?)" for _ in uniq) +
                 ") AS t(an_type,notice_date,corporate_debtor,auction_date,"
                 "insolvency_professional,notice_pdf,reserve_price_inr,"
                 "nature_of_assets,emd_last_date)",
                 [v for r in uniq for v in
                  (r["an_type"], r["notice_date"], r["corporate_debtor"],
                   r["auction_date"], r["insolvency_professional"],
                   r["notice_pdf"], r["reserve_price_inr"],
                   r["nature_of_assets"], r["emd_last_date"])]) if uniq else None
    if os.path.exists(PARQUET) and uniq:
        dcon.execute(f"""COPY (
            SELECT * FROM new_notices
            UNION
            SELECT * FROM read_parquet('{PARQUET}')
        ) TO '{PARQUET}' (FORMAT PARQUET)""")
    elif uniq:
        dcon.execute(f"COPY new_notices TO '{PARQUET}' (FORMAT PARQUET)")
    total = dcon.execute(f"SELECT COUNT(*) FROM read_parquet('{PARQUET}')").fetchone()[0]

    # ---- rebuild DB table from the parquet ----------------------------------
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS ibbi_auction_notices;
        CREATE TABLE ibbi_auction_notices (
            notice_pdf TEXT PRIMARY KEY, an_type TEXT, notice_date TEXT,
            corporate_debtor TEXT, auction_date TEXT,
            insolvency_professional TEXT, reserve_price_inr INTEGER,
            nature_of_assets TEXT, emd_last_date TEXT);
        DROP TABLE IF EXISTS ibbi_company_matches;
        CREATE TABLE ibbi_company_matches (
            notice_pdf TEXT, company_id INTEGER REFERENCES companies(company_id),
            matched_fragment TEXT, match_quality TEXT);
    """)
    allrows = dcon.execute(f"""SELECT notice_pdf,an_type,notice_date,
        corporate_debtor,auction_date,insolvency_professional,
        reserve_price_inr,nature_of_assets,emd_last_date
        FROM read_parquet('{PARQUET}')""").fetchall()
    cur.executemany("INSERT OR IGNORE INTO ibbi_auction_notices VALUES (?,?,?,?,?,?,?,?,?)",
                    allrows)
    con.commit()

    # ---- cross-match corporate debtors vs the twin's companies --------------
    cur.execute("SELECT company_id, name FROM companies")
    companies = [(cid, name, norm(name)) for cid, name in cur.fetchall()]
    debtors = [(r[0], norm(r[3])) for r in allrows]   # (notice_pdf, norm cd)
    n_match = 0
    for cid, name, nn in companies:
        for frag, quality in match_fragments(nn):
            hits = [pdf for pdf, cd in debtors if f" {frag} " in f" {cd} "]
            if hits:
                for pdf in hits:
                    cur.execute("INSERT INTO ibbi_company_matches VALUES (?,?,?,?)",
                                (pdf, cid, frag, quality))
                    n_match += 1
                break
    con.commit()

    matches = cur.execute("""
        SELECT DISTINCT c.name, n.corporate_debtor, n.reserve_price_inr,
               n.nature_of_assets, n.auction_date, m.match_quality
          FROM ibbi_company_matches m JOIN companies c USING(company_id)
          JOIN ibbi_auction_notices n USING(notice_pdf)
         WHERE m.match_quality IN ('strong','reviewed-promoted')
         ORDER BY n.reserve_price_inr DESC""").fetchall()

    # ---- layer 34 register block --------------------------------------------
    top = dcon.execute(f"""SELECT corporate_debtor, reserve_price_inr,
        nature_of_assets, auction_date FROM read_parquet('{PARQUET}')
        WHERE reserve_price_inr IS NOT NULL
        ORDER BY reserve_price_inr DESC LIMIT 15""").fetchall()
    asset_mix = dcon.execute(f"""SELECT nature_of_assets, COUNT(*) n
        FROM read_parquet('{PARQUET}') GROUP BY 1 ORDER BY 2 DESC LIMIT 12""").fetchall()

    layer = json.load(open(LAYER))
    layer["register"] = {
        "ran": today,
        "source": "IBBI liquidation auction notices (ibbi.gov.in/liquidation-auction-notices/lists)",
        "access": ("server-rendered table, no auth; ?page=N (20 rows/page, "
                   "~481 pages to inception); durable parquet at "
                   "data/registers/ibbi_liquidation.parquet"),
        "total_notices": total,
        "scraped_this_run": len(uniq),
        "fields": ["an_type", "notice_date", "corporate_debtor", "auction_date",
                   "insolvency_professional", "reserve_price_inr",
                   "nature_of_assets", "emd_last_date", "notice_pdf"],
        "top_by_reserve_price": [
            {"corporate_debtor": d, "reserve_price_inr": p,
             "nature_of_assets": a, "auction_date": ad} for d, p, a, ad in top],
        "asset_type_mix": {a: n for a, n in asset_mix},
        "twin_company_matches": [
            {"company": m[0], "corporate_debtor": m[1], "reserve_price_inr": m[2],
             "nature_of_assets": m[3], "auction_date": m[4], "quality": m[5]}
            for m in matches],
        "tables": ["ibbi_auction_notices", "ibbi_company_matches"],
    }
    with open(LAYER, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    con.close()
    print(f"parquet total: {total} | twin matches: {len(matches)}")
    for m in matches[:15]:
        cr = f"Rs {m[2]:,}" if m[2] else "n/a"
        print(f"  {m[0]} <- CD:{m[1][:40]} | {cr} | {m[3]}")


if __name__ == "__main__":
    main()
