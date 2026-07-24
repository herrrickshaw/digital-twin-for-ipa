#!/usr/bin/env python3
"""Layer 34 — IBBI register analysis: state-wise + resolution-friction heuristic.

Two views over data/registers/ibbi_liquidation.parquet (9,531 notices):

STATE-WISE — state is NOT a register column; it is parsed from the property
address inside `nature_of_assets` (only ~10% of rows carry it) AND, for the
top notices by reserve price, from the notice PDF address block. Coverage is
reported honestly; unresolved rows are counted as 'state_unknown'.

RESOLUTION-FRICTION — a transparent RULE-BASED proxy (low/medium/high), NOT a
probability of a court outcome and NOT legal advice. Signals, all register-
native:
  - asset liquidity: single-lot Land/Flat/Plot = low; Plant&Machinery/Inventory
    = medium; 'going concern' / multi-block / as-is-where-is = high
  - re-auction / stuck: same corporate debtor appearing >=3 times, or a FALLING
    reserve price across its notices = high (bidder/litigation drag)
  - ticket size: >Rs 100 cr = high (complex multi-forum litigation); a small
    single parcel <Rs 5 cr = low
Lower friction ≈ faster, cleaner realisation. This is a screening aid over
public data, not a prediction of any specific court's timeline.

Writes a `state_resolution` block into layers/34_stressed_assets.json.
Run with /usr/bin/python3 (duckdb). Usage: [--pdf-top N] (default 60)
"""
import argparse
import json
import os
import re
import urllib.request
import subprocess
import tempfile
from collections import Counter, defaultdict

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET = os.path.join(ROOT, "data", "registers", "ibbi_liquidation.parquet")
LAYER = os.path.join(ROOT, "layers", "34_stressed_assets.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

STATES = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
          "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
          "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
          "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
          "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
          "West Bengal", "Delhi", "Chandigarh", "Puducherry"]
_ST_ALT = {"Pondicherry": "Puducherry", "Orissa": "Odisha",
           "Jammu": "Jammu & Kashmir", "Kashmir": "Jammu & Kashmir"}
STATE_RE = re.compile(r"\b(" + "|".join(re.escape(s) for s in
                      list(STATES) + list(_ST_ALT)) + r")\b", re.I)


def find_state(text):
    m = STATE_RE.search(text or "")
    if not m:
        return None
    s = m.group(1).title()
    return _ST_ALT.get(s, s)


def liquidity(assets):
    a = (assets or "").lower()
    if any(t in a for t in ("going concern", "as-is-where-is", "as is where is",
                            "block a", "block no", "slump sale")):
        return "high"           # complex composite / going-concern sale
    if any(t in a for t in ("plant", "machinery", "inventory", "stock")):
        return "medium"
    if any(t in a for t in ("land", "building", "flat", "plot", "premise",
                            "residential", "shop", "office")):
        return "low"
    return "medium"


def friction(asset_liquidity, notice_count, reserve, falling):
    score = {"low": 0, "medium": 1, "high": 2}[asset_liquidity]
    if notice_count >= 3:
        score += 1
    if falling:
        score += 1
    if reserve and reserve > 1_00_00_00_000:      # > Rs 100 cr
        score += 1
    elif reserve and reserve < 5_00_00_000:       # < Rs 5 cr, single small parcel
        score -= 1
    return "low" if score <= 0 else ("medium" if score == 1 else "high")


def pdf_state(url, timeout=45):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=timeout).read()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(data); path = f.name
        txt = subprocess.run(["pdftotext", "-f", "1", "-l", "6", path, "-"],
                             capture_output=True, timeout=60).stdout.decode("utf-8", "replace")
        os.unlink(path)
        return find_state(txt)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-top", type=int, default=60,
                    help="PDF-parse state for the top-N by reserve price")
    args = ap.parse_args()

    d = duckdb.connect()
    rows = d.execute(f"""SELECT notice_pdf, corporate_debtor, reserve_price_inr,
        nature_of_assets, auction_date, notice_date FROM read_parquet('{PARQUET}')
        """).fetchall()

    # notice-count + falling-reserve per corporate debtor (stuck signal)
    by_cd = defaultdict(list)
    for pdf, cd, res, na, auc, nd in rows:
        by_cd[cd].append(res or 0)
    stuck = {}
    for cd, prices in by_cd.items():
        nonzero = [p for p in prices if p]
        falling = len(nonzero) >= 2 and nonzero[0] > nonzero[-1]
        stuck[cd] = (len(prices), falling)

    # per-notice state (from asset text) + friction
    recs = []
    for pdf, cd, res, na, auc, nd in rows:
        st = find_state(na)
        liq = liquidity(na)
        nc, falling = stuck[cd]
        recs.append({"notice_pdf": pdf, "cd": cd, "reserve": res, "assets": na,
                     "state": st, "liquidity": liq,
                     "friction": friction(liq, nc, res, falling),
                     "notice_count": nc, "reserve_falling": falling})

    # PDF-enrich state for the top-N by reserve price that lack an in-text state
    top = sorted([r for r in recs if r["reserve"] and not r["state"]],
                 key=lambda r: -r["reserve"])[:args.pdf_top]
    pdf_hits = 0
    for r in top:
        full = r["notice_pdf"]
        if full.startswith("/"):
            full = "https://ibbi.gov.in" + full
        st = pdf_state(full)
        if st:
            r["state"] = st; pdf_hits += 1

    resolved = [r for r in recs if r["state"]]
    state_counts = Counter(r["state"] for r in resolved)
    friction_by_state = defaultdict(lambda: Counter())
    for r in resolved:
        friction_by_state[r["state"]][r["friction"]] += 1

    overall_friction = Counter(r["friction"] for r in recs)

    # state table: count + friction split + median reserve
    state_table = []
    for st, n in state_counts.most_common():
        fr = friction_by_state[st]
        reserves = sorted(r["reserve"] for r in resolved
                          if r["state"] == st and r["reserve"])
        med = reserves[len(reserves) // 2] if reserves else None
        state_table.append({
            "state": st, "notices": n,
            "friction_low": fr["low"], "friction_medium": fr["medium"],
            "friction_high": fr["high"],
            "low_friction_pct": round(100 * fr["low"] / n) if n else 0,
            "median_reserve_inr": med})

    layer = json.load(open(LAYER))
    layer["state_resolution"] = {
        "ran": __import__("datetime").date.today().isoformat(),
        "total_notices": len(rows),
        "state_coverage": {
            "resolved": len(resolved),
            "from_asset_text": len([r for r in recs if r["state"] and r not in top]),
            "from_pdf_top": pdf_hits,
            "unknown": len(rows) - len(resolved),
            "note": (f"state is NOT a register field — parsed from the property "
                     f"address in nature_of_assets (~10 pct of rows) + PDF-address "
                     f"for the top-{args.pdf_top} by reserve price. "
                     f"~{round(100 * (len(rows) - len(resolved)) / len(rows))} pct "
                     f"remain state_unknown; full coverage needs parsing all "
                     f"{len(rows)} notice PDFs.")},
        "state_wise": state_table,
        "friction_method": ("RULE-BASED proxy (low/medium/high) — NOT a probability "
                            "of a court outcome, NOT legal advice. Signals: asset "
                            "liquidity + re-auction/stuck (repeat notices or falling "
                            "reserve) + ticket size. Lower friction ~= faster, "
                            "cleaner realisation."),
        "friction_overall": dict(overall_friction),
        "friction_reading": (f"low ~{round(100 * overall_friction['low'] / len(rows))} "
                             f"pct of notices — single-lot land/flat, fresh notice, "
                             f"small ticket: quickest to clear. high — going-concern/"
                             f"composite, re-auctioned or >Rs100cr: expect multi-forum "
                             f"drag (the Dunlop pattern)."),
    }
    with open(LAYER, "w") as f:
        json.dump(layer, f, indent=1, ensure_ascii=False)

    print(f"notices {len(rows)} | state resolved {len(resolved)} "
          f"(+{pdf_hits} via PDF) | unknown {len(rows)-len(resolved)}")
    print("friction:", dict(overall_friction))
    print("\nstate               notices  low%  med  high  median_reserve")
    for r in state_table[:16]:
        mr = f"Rs {r['median_reserve_inr']:,}" if r["median_reserve_inr"] else "-"
        print(f"  {r['state']:18} {r['notices']:5}  {r['low_friction_pct']:3}%  "
              f"{r['friction_medium']:3}  {r['friction_high']:4}  {mr}")


if __name__ == "__main__":
    main()
