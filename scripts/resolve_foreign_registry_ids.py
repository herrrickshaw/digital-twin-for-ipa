#!/usr/bin/env python3
"""Layer 32 enrichment — foreign registry-ID resolution -> country-wise parquets.

Resolves the twin's foreign companies against the corporate registries the
layer-31 access map verified as working, and writes one parquet per country
to data/registry_ids/ (via duckdb — no pandas needed).

Per jurisdiction:
  ALL       GLEIF LEI fulltext search (open)
  US        SEC EDGAR company_tickers.json ticker->CIK map (declared UA)
  KR        DART corpCode.xml (keyed, DART_KEY) stock_code->corp_code
  CH        Zefix POST name search -> UID
  FR        recherche-entreprises.api.gouv.fr -> SIREN
  UK        Companies House — needs COMPANIES_HOUSE_KEY (free registration);
            rows carry status=pending_key until it exists in credentials.env
  JP        gBizINFO — needs GBIZINFO_TOKEN; same pending_key convention

Run with /usr/bin/python3 (duckdb lives there, not in the venv).
Usage: /usr/bin/python3 scripts/resolve_foreign_registry_ids.py [--gleif-limit N]
"""
import argparse
import io
import json
import os
import re
import sqlite3
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
OUTDIR = os.path.join(ROOT, "data", "registry_ids")
CRED = os.path.expanduser("~/.config/market-secrets/credentials.env")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
EDGAR_UA = "digital-twin-for-ipa research umashankartd1991@gmail.com"


def env():
    d = {}
    if os.path.exists(CRED):
        for line in open(CRED):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                v = v.strip().strip('"').strip("'")
                # ignore unfilled placeholders like <your-key>
                if v and not v.startswith("<") and "your" not in v.lower():
                    d[k] = v
    return d


def get_json(url, ua=UA, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def post_json(url, body, timeout=25):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"User-Agent": UA,
                                          "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def gleif(name):
    q = urllib.parse.quote(name)
    d = get_json(f"https://api.gleif.org/api/v1/lei-records?filter%5Bfulltext%5D={q}&page%5Bsize%5D=1")
    recs = d.get("data") or []
    if recs:
        a = recs[0]["attributes"]
        return a["lei"], a["entity"]["legalName"]["name"]
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gleif-limit", type=int, default=400)
    args = ap.parse_args()
    keys = env()
    today = date.today().isoformat()
    os.makedirs(OUTDIR, exist_ok=True)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS registry_ids;
        CREATE TABLE registry_ids (
            company_id INTEGER REFERENCES companies(company_id),
            name TEXT, country TEXT, ticker TEXT,
            lei TEXT, lei_legal_name TEXT,
            national_id TEXT, national_id_type TEXT, national_registry TEXT,
            status TEXT,             -- resolved | lei_only | pending_key | unresolved
            resolved TEXT);
    """)
    cur.execute("""SELECT company_id, name, country, ticker FROM companies
                    WHERE country IS NOT NULL AND country NOT IN ('India','')
                    ORDER BY country, name""")
    companies = cur.fetchall()
    print(f"{len(companies)} foreign companies")

    # ---- national maps fetched once -----------------------------------------
    # US: ticker -> CIK
    cik_map = {}
    try:
        d = get_json("https://www.sec.gov/files/company_tickers.json", ua=EDGAR_UA)
        cik_map = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in d.values()}
        print("EDGAR ticker map:", len(cik_map))
    except Exception as e:
        print("EDGAR map failed:", type(e).__name__)
    # KR: stock_code -> corp_code
    dart_map = {}
    if keys.get("DART_KEY"):
        try:
            u = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={keys['DART_KEY']}"
            raw = urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60).read()
            xml = zipfile.ZipFile(io.BytesIO(raw)).read("CORPCODE.xml").decode("utf-8")
            for m in re.finditer(r"<corp_code>(\d+)</corp_code>\s*<corp_name>[^<]*</corp_name>"
                                 r"(?:\s*<corp_eng_name>[^<]*</corp_eng_name>)?"
                                 r"\s*<stock_code>([A-Za-z0-9]+)</stock_code>", xml):
                dart_map[m.group(2)] = m.group(1)
            print("DART stock->corp map:", len(dart_map))
        except Exception as e:
            print("DART map failed:", type(e).__name__)

    gleif_used = 0
    for cid, name, country, ticker in companies:
        lei = lei_name = nat_id = nat_type = nat_reg = None
        status = "unresolved"
        # GLEIF for everyone (budgeted)
        if gleif_used < args.gleif_limit:
            try:
                lei, lei_name = gleif(name)
                gleif_used += 1
                time.sleep(0.12)
            except Exception:
                pass
        if lei:
            status = "lei_only"
        # national registries
        try:
            if country == "United States" and ticker:
                cik = cik_map.get(ticker.upper().split(".")[0])
                if cik:
                    nat_id, nat_type, nat_reg, status = cik, "CIK", "SEC EDGAR", "resolved"
            elif country == "South Korea" and ticker:
                # DB format is 'A066570 (KOSE 066570)' — take the 6-digit code
                m6 = re.search(r"\b(\d{6})\b", ticker)
                code = dart_map.get(m6.group(1)) if m6 else None
                if code:
                    nat_id, nat_type, nat_reg, status = code, "DART corp_code", "DART", "resolved"
            elif country == "Switzerland":
                d = post_json("https://www.zefix.ch/ZefixREST/api/v1/firm/search.json",
                              {"name": name.split()[0], "activeOnly": True})
                hits = d.get("list") or []
                if hits:
                    nat_id, nat_type, nat_reg, status = (hits[0].get("uidFormatted"),
                                                         "UID", "Zefix", "resolved")
            elif country == "France":
                q = urllib.parse.quote(name)
                d = get_json(f"https://recherche-entreprises.api.gouv.fr/search?q={q}&page=1&per_page=1")
                res = d.get("results") or []
                if res:
                    nat_id, nat_type, nat_reg, status = (res[0].get("siren"),
                                                         "SIREN", "recherche-entreprises", "resolved")
            elif country == "United Kingdom":
                if keys.get("COMPANIES_HOUSE_KEY"):
                    import base64
                    q = urllib.parse.quote(name)
                    req = urllib.request.Request(
                        f"https://api.company-information.service.gov.uk/search/companies?q={q}&items_per_page=1",
                        headers={"User-Agent": UA, "Authorization": "Basic " + base64.b64encode(
                            (keys["COMPANIES_HOUSE_KEY"] + ":").encode()).decode()})
                    d = json.loads(urllib.request.urlopen(req, timeout=25).read())
                    items = d.get("items") or []
                    if items:
                        nat_id, nat_type, nat_reg, status = (items[0].get("company_number"),
                                                             "CRN", "Companies House", "resolved")
                else:
                    status = "pending_key" if not lei else "lei_only"
                    nat_reg = "Companies House (COMPANIES_HOUSE_KEY not in credentials.env)"
            elif country == "Japan":
                if keys.get("GBIZINFO_TOKEN"):
                    q = urllib.parse.quote(name)
                    req = urllib.request.Request(
                        f"https://info.gbiz.go.jp/hojin/v1/hojin?name={q}&limit=1",
                        headers={"User-Agent": UA, "X-hojinInfo-api-token": keys["GBIZINFO_TOKEN"]})
                    d = json.loads(urllib.request.urlopen(req, timeout=25).read())
                    items = d.get("hojin-infos") or []
                    if items:
                        nat_id, nat_type, nat_reg, status = (items[0].get("corporate_number"),
                                                             "法人番号", "gBizINFO", "resolved")
                else:
                    status = "pending_key" if not lei else "lei_only"
                    nat_reg = "gBizINFO (GBIZINFO_TOKEN not in credentials.env)"
        except Exception:
            pass
        cur.execute("INSERT INTO registry_ids VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, name, country, ticker, lei, lei_name,
                     nat_id, nat_type, nat_reg, status, today))
    con.commit()

    counts = dict(cur.execute(
        "SELECT status, COUNT(*) FROM registry_ids GROUP BY 1").fetchall())
    print("statuses:", counts, "| gleif calls:", gleif_used)
    con.close()

    # ---- country-wise parquets via duckdb -----------------------------------
    import duckdb
    dcon = duckdb.connect()
    dcon.execute(f"ATTACH '{DB}' AS c (TYPE sqlite)")
    countries = [r[0] for r in dcon.execute(
        "SELECT DISTINCT country FROM c.registry_ids").fetchall()]
    for ctry in countries:
        safe = re.sub(r"[^A-Za-z0-9]+", "_", ctry).strip("_")
        dcon.execute(f"""COPY (SELECT * FROM c.registry_ids WHERE country = ?
                          ORDER BY name)
                         TO '{OUTDIR}/{safe}.parquet' (FORMAT PARQUET)""", [ctry])
    print(f"wrote {len(countries)} parquets -> {OUTDIR}/")


if __name__ == "__main__":
    main()
