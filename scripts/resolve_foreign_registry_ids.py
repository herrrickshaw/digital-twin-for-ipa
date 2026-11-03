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


def _reset_table(cur):
    """Drop and recreate the registry_ids table."""
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


def _foreign_companies(cur):
    """(company_id, name, country, ticker) for every non-Indian company."""
    cur.execute("""SELECT company_id, name, country, ticker FROM companies
                    WHERE country IS NOT NULL AND country NOT IN ('India','')
                    ORDER BY country, name""")
    return cur.fetchall()


def _edgar_map():
    """US: ticker -> zero-padded CIK from SEC company_tickers.json ({} on failure)."""
    cik_map = {}
    try:
        d = get_json("https://www.sec.gov/files/company_tickers.json", ua=EDGAR_UA)
        cik_map = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in d.values()}
        print("EDGAR ticker map:", len(cik_map))
    except Exception as e:
        print("EDGAR map failed:", type(e).__name__)
    return cik_map


def _dart_map(keys):
    """KR: stock_code -> corp_code from DART corpCode.xml (needs DART_KEY; {} otherwise or on failure)."""
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
    return dart_map


# ---- per-country national-registry resolvers --------------------------------
# Each takes (name, ticker, lei, ctx) and returns None (nothing found, state unchanged) or
# (national_id, id_type, registry, status); status None keeps the current status.
# Add a country by adding one function and one NATIONAL_RESOLVERS entry.

def _national_us(name, ticker, lei, ctx):
    cik = ctx["cik_map"].get(ticker.upper().split(".")[0]) if ticker else None
    return (cik, "CIK", "SEC EDGAR", "resolved") if cik else None


def _national_kr(name, ticker, lei, ctx):
    # DB format is 'A066570 (KOSE 066570)' — take the 6-digit code
    m6 = re.search(r"\b(\d{6})\b", ticker) if ticker else None
    code = ctx["dart_map"].get(m6.group(1)) if m6 else None
    return (code, "DART corp_code", "DART", "resolved") if code else None


def _national_ch(name, ticker, lei, ctx):
    d = post_json("https://www.zefix.ch/ZefixREST/api/v1/firm/search.json",
                  {"name": name.split()[0], "activeOnly": True})
    hits = d.get("list") or []
    return (hits[0].get("uidFormatted"), "UID", "Zefix", "resolved") if hits else None


def _national_fr(name, ticker, lei, ctx):
    q = urllib.parse.quote(name)
    d = get_json(f"https://recherche-entreprises.api.gouv.fr/search?q={q}&page=1&per_page=1")
    res = d.get("results") or []
    return (res[0].get("siren"), "SIREN", "recherche-entreprises", "resolved") if res else None


def _national_uk(name, ticker, lei, ctx):
    keys = ctx["keys"]
    if not keys.get("COMPANIES_HOUSE_KEY"):
        return (None, None, "Companies House (COMPANIES_HOUSE_KEY not in credentials.env)",
                "pending_key" if not lei else "lei_only")
    import base64
    q = urllib.parse.quote(name)
    req = urllib.request.Request(
        f"https://api.company-information.service.gov.uk/search/companies?q={q}&items_per_page=1",
        headers={"User-Agent": UA, "Authorization": "Basic " + base64.b64encode(
            (keys["COMPANIES_HOUSE_KEY"] + ":").encode()).decode()})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read())
    items = d.get("items") or []
    return (items[0].get("company_number"), "CRN", "Companies House", "resolved") if items else None


def _national_jp(name, ticker, lei, ctx):
    keys = ctx["keys"]
    if not keys.get("GBIZINFO_TOKEN"):
        return (None, None, "gBizINFO (GBIZINFO_TOKEN not in credentials.env)",
                "pending_key" if not lei else "lei_only")
    q = urllib.parse.quote(name)
    req = urllib.request.Request(
        f"https://info.gbiz.go.jp/hojin/v1/hojin?name={q}&limit=1",
        headers={"User-Agent": UA, "X-hojinInfo-api-token": keys["GBIZINFO_TOKEN"]})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read())
    items = d.get("hojin-infos") or []
    return (items[0].get("corporate_number"), "法人番号", "gBizINFO", "resolved") if items else None


NATIONAL_RESOLVERS = {
    "United States": _national_us, "South Korea": _national_kr, "Switzerland": _national_ch,
    "France": _national_fr, "United Kingdom": _national_uk, "Japan": _national_jp,
}


def _resolve_company(name, country, ticker, lei, ctx):
    """National-registry lookup; any failure leaves the company unresolved at national level."""
    resolver = NATIONAL_RESOLVERS.get(country)
    if not resolver:
        return None
    try:
        return resolver(name, ticker, lei, ctx)
    except Exception:
        return None


def _resolve_all(cur, companies, ctx, gleif_limit, today):
    """GLEIF (budgeted) + national lookup per company, inserted into registry_ids; returns GLEIF calls used."""
    gleif_used = 0
    for cid, name, country, ticker in companies:
        lei = lei_name = nat_id = nat_type = nat_reg = None
        status = "unresolved"
        if gleif_used < gleif_limit:
            try:
                lei, lei_name = gleif(name)
                gleif_used += 1
                time.sleep(0.12)
            except Exception:
                pass
        if lei:
            status = "lei_only"
        res = _resolve_company(name, country, ticker, lei, ctx)
        if res:
            nat_id, nat_type, nat_reg, new_status = res
            status = new_status or status
        cur.execute("INSERT INTO registry_ids VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, name, country, ticker, lei, lei_name,
                     nat_id, nat_type, nat_reg, status, today))
    return gleif_used


def _write_parquets():
    """One parquet per country via duckdb (system python only)."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gleif-limit", type=int, default=400)
    args = ap.parse_args()
    keys = env()
    today = date.today().isoformat()
    os.makedirs(OUTDIR, exist_ok=True)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    _reset_table(cur)
    companies = _foreign_companies(cur)
    print(f"{len(companies)} foreign companies")

    ctx = {"keys": keys, "cik_map": _edgar_map(), "dart_map": _dart_map(keys)}
    gleif_used = _resolve_all(cur, companies, ctx, args.gleif_limit, today)
    con.commit()

    counts = dict(cur.execute(
        "SELECT status, COUNT(*) FROM registry_ids GROUP BY 1").fetchall())
    print("statuses:", counts, "| gleif calls:", gleif_used)
    con.close()

    _write_parquets()


if __name__ == "__main__":
    main()
