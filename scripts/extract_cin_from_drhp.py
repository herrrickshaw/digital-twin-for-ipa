#!/usr/bin/env python3
"""Layer 32 enrichment — CIN + issue-structure extraction from SEBI prospectuses.

MCA's own registry is 403-blocked from this machine (re-tested 2026-07-23), so
the authoritative CIN route for companies in the listing pipeline is the
prospectus itself: every DRHP/RHP states the company's CIN, registered office
and the OBJECTS OF THE ISSUE — i.e. what the market money will fund, which is
the twin's actual question (are clearance-evidenced expansions being funded by
the primary market?).

For each company in sebi_company_matches: fetch its SEBI filing page, locate
the prospectus PDF, download to the scratchpad (never committed), pdftotext,
then regex out:
  - CIN  ([LU]DDDDDAADDDDAAADDDDDD)
  - fresh issue / offer-for-sale amounts (Rs cr)
  - the first lines of the OBJECTS OF THE ISSUE section

Results -> cin_records table + `cin_extraction` block in 32_company_db.json.

Usage: python3 scripts/extract_cin_from_drhp.py [--limit N]
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import tempfile
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "companies.db")
LAYER = os.path.join(ROOT, "layers", "32_company_db.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
CIN_RE = re.compile(r"\b([LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})\b")


def get(url, binary=False, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=timeout).read()
    return data if binary else data.decode("utf-8", "replace")


def find_pdf(url):
    if url.lower().endswith(".pdf"):
        return url
    html = get(url)
    m = re.search(r"[?&]file=(https://www\.sebi\.gov\.in/sebi_data/[^'\"&]+\.pdf)", html) \
        or re.search(r"['\"](https://www\.sebi\.gov\.in/sebi_data/[^'\"]+\.pdf)", html)
    return m.group(1) if m else None


def extract(pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        path = f.name
    try:
        # cover + front matter for CIN/issue box; full-doc grep is overkill
        txt = subprocess.run(["pdftotext", "-f", "1", "-l", "12", path, "-"],
                             capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
        full = subprocess.run(["pdftotext", path, "-"],
                              capture_output=True, timeout=300).stdout.decode("utf-8", "replace")
    finally:
        os.unlink(path)
    cin = (CIN_RE.search(txt) or CIN_RE.search(full))
    fresh = re.search(r"[Ff]resh [Ii]ssue[^.\n]{0,220}?(?:Rs\.?|₹|`)\s?([\d,]+(?:\.\d+)?)\s*(cr|crore|million|lakh)", full)
    ofs = re.search(r"[Oo]ffer [Ff]or [Ss]ale[^.\n]{0,220}?(?:Rs\.?|₹|`)\s?([\d,]+(?:\.\d+)?)\s*(cr|crore|million|lakh)", full)
    obj = ""
    # take the SECTION body, not the table-of-contents line (dotted leaders)
    for m in re.finditer(r"OBJECTS OF THE (?:ISSUE|OFFER)", full):
        seg = full[m.end():m.end() + 1500]
        if seg.count(".") > 200:      # TOC leader dots -> not the section
            continue
        seg = re.sub(r"\s+", " ", seg).strip()
        if len(seg) > 100:
            obj = seg[:600]           # keep LAST qualifying occurrence

    return (cin.group(1) if cin else None,
            f"{fresh.group(1)} {fresh.group(2)}" if fresh else None,
            f"{ofs.group(1)} {ofs.group(2)}" if ofs else None, obj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=15)
    args = ap.parse_args()
    today = date.today().isoformat()
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS cin_records (
            company_id INTEGER PRIMARY KEY REFERENCES companies(company_id),
            cin TEXT, fresh_issue TEXT, offer_for_sale TEXT,
            objects_of_issue TEXT, source_pdf TEXT, extracted TEXT);
    """)
    # companies.db is wiped weekly — reload durable records from state/ so we
    # never re-download a prospectus we already extracted (company_id remapped
    # by name because ids change across rebuilds)
    state_f = os.path.join(ROOT, "state", "cin_records.json")
    if os.path.exists(state_f) and not cur.execute(
            "SELECT 1 FROM cin_records LIMIT 1").fetchone():
        for r in json.load(open(state_f)):
            row = cur.execute("SELECT company_id FROM companies WHERE name=?",
                              (r["company"],)).fetchone()
            if row:
                cur.execute("INSERT OR REPLACE INTO cin_records VALUES (?,?,?,?,?,?,?)",
                            (row[0], r["cin"], r["fresh_issue"], r["offer_for_sale"],
                             r["objects_of_issue"], r["source_pdf"], r["extracted"]))
        con.commit()
    # latest filing per matched company, skip already-extracted
    rows = cur.execute("""
        SELECT c.company_id, c.name,
               group_concat(f.url, ' '), MAX(f.filed)
          FROM sebi_company_matches m
          JOIN companies c USING (company_id)
          JOIN sebi_filings f USING (filing_id)
         WHERE c.company_id NOT IN (SELECT company_id FROM cin_records
                                     WHERE cin IS NOT NULL)
         GROUP BY c.company_id LIMIT ?""", (args.limit,)).fetchall()
    results, errors = [], []
    for cid, name, url, filed in rows:
        try:
            pdf_url = None
            for u in url.split(" "):           # try every filing page for this company
                pdf_url = find_pdf(u)
                if pdf_url:
                    break
            if not pdf_url:
                errors.append({"company": name, "error": "no PDF link on any filing page",
                               "url": url})
                continue
            pdf = get(pdf_url, binary=True)
            cin, fresh, ofs, obj = extract(pdf)
            cur.execute("INSERT OR REPLACE INTO cin_records VALUES (?,?,?,?,?,?,?)",
                        (cid, cin, fresh, ofs, obj, pdf_url, today))
            results.append({"company": name, "cin": cin, "fresh_issue": fresh,
                            "offer_for_sale": ofs,
                            "objects_excerpt": obj[:250], "pdf": pdf_url})
            print(f"  {name}: CIN={cin} fresh={fresh} ofs={ofs}")
        except Exception as e:
            errors.append({"company": name, "error": f"{type(e).__name__}: {str(e)[:80]}"})
            print(f"  {name}: FAILED {type(e).__name__}")
    con.commit()
    # durable dump (survives the weekly DB rebuild)
    dump = [dict(zip(("company", "cin", "fresh_issue", "offer_for_sale",
                      "objects_of_issue", "source_pdf", "extracted"), row))
            for row in cur.execute(
                "SELECT c.name, r.cin, r.fresh_issue, r.offer_for_sale,"
                " r.objects_of_issue, r.source_pdf, r.extracted"
                " FROM cin_records r JOIN companies c USING (company_id)")]
    os.makedirs(os.path.join(ROOT, "state"), exist_ok=True)
    with open(os.path.join(ROOT, "state", "cin_records.json"), "w") as f:
        json.dump(dump, f, indent=1, ensure_ascii=False)
    layer = json.load(open(LAYER))
    layer["cin_extraction"] = {
        "ran": today,
        "what": ("CIN + issue structure + objects-of-issue extracted from SEBI "
                 "prospectus PDFs (MCA registry 403-blocked; the prospectus IS "
                 "the authoritative CIN source for listing-pipeline companies)"),
        "records": results, "errors": errors,
        "mca_status": "mca.gov.in 403 (re-tested 2026-07-23); zaubacorp 403; "
                      "thecompanycheck/falconebiz reachable but unofficial",
    }
    with open(LAYER, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)
    print(f"extracted {len(results)}, errors {len(errors)}")
    con.close()


if __name__ == "__main__":
    main()
