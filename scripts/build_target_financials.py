#!/usr/bin/env python3
"""
build_target_financials.py — CFO-level financial dossier for the India-intent
target companies (layers/16_target_shortlist.json).

For each recommended foreign company, pulls the metrics a CFO/IC screens on
before an outreach or investment decision — so the shortlist stops being just
"they said India in a filing" and becomes "…and here is the balance-sheet
capacity behind that intent":

  scale       : revenue (USD), market cap, employees
  growth      : revenue YoY
  profitability: gross / operating / net margin, EBITDA margin, ROE, ROA
  cash/ROI    : operating cash flow, free cash flow, FCF margin, ROIC proxy
  leverage    : total debt / equity, net-debt/EBITDA, current ratio
  earnings    : net income (USD), diluted EPS, forward P/E

Ticker mapping: the twin stores exchange-prefixed tickers (TSE:7269, KRX:...)
-> yfinance suffixes. US bare tickers pass through.

Output: layers/16_enrichment/target_financials.json + docs table.
"""
from __future__ import annotations

import json
import os
import sys
import time

import pandas as pd
import yfinance as yf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORTLIST = os.path.join(ROOT, "layers", "16_target_shortlist.json")
OUT = os.path.join(ROOT, "layers", "16_enrichment", "target_financials.json")
OUT_MD = os.path.join(ROOT, "docs", "TARGET_FINANCIALS.md")

# exchange prefix -> yfinance suffix
SUFFIX = {
    "TSE": ".T", "KRX": ".KS", "KOSDAQ": ".KQ", "LSE": ".L", "LON": ".L",
    "ETR": ".DE", "FRA": ".F", "EPA": ".PA", "AMS": ".AS", "BIT": ".MI",
    "BME": ".MC", "STO": ".ST", "SWX": ".SW", "VIE": ".VI", "ASX": ".AX",
    "TPE": ".TW", "TWSE": ".TW", "HKG": ".HK", "TSX": ".TO", "BterseMV": "",
}


def yf_ticker(raw: str) -> str | None:
    raw = str(raw).strip()
    if ":" not in raw:
        return raw or None
    exch, code = raw.split(":", 1)
    suf = SUFFIX.get(exch.upper())
    if suf is None:
        return None
    return f"{code}{suf}"


# reporting-currency -> USD (approx spot, 2026-07; ratios are FX-immune, only
# absolute $ sums need this — the mixed-currency sum bug fixed here)
FX_USD = {
    "USD": 1.0, "JPY": 0.0064, "KRW": 0.00072, "TWD": 0.031, "HKD": 0.128,
    "EUR": 1.08, "GBP": 1.28, "DKK": 0.145, "SEK": 0.095, "CHF": 1.12,
    "AUD": 0.66, "INR": 0.0116, "CNY": 0.139, "NOK": 0.093, "SGD": 0.74,
}


def usd(x, fx=1.0):
    if x is None or fx is None or pd.isna(x):
        return None
    return round(x * fx / 1e6, 1)  # $M


def pct(a, b):
    if a is None or b in (None, 0) or pd.isna(a) or pd.isna(b):
        return None
    return round(100 * a / b, 1)


def pull(tk: str) -> dict:
    t = yf.Ticker(tk)
    info = t.info or {}
    fx = FX_USD.get(info.get("financialCurrency"), None)
    fin = t.financials if hasattr(t, "financials") else pd.DataFrame()
    cf = t.cashflow if hasattr(t, "cashflow") else pd.DataFrame()

    def fin_row(*names):
        for n in names:
            if not fin.empty and n in fin.index:
                v = fin.loc[n].dropna()
                if len(v):
                    return float(v.iloc[0])
        return None

    def cf_row(*names):
        for n in names:
            if not cf.empty and n in cf.index:
                v = cf.loc[n].dropna()
                if len(v):
                    return float(v.iloc[0])
        return None

    rev = info.get("totalRevenue") or fin_row("Total Revenue")
    ni = info.get("netIncomeToCommon") or fin_row("Net Income")
    ocf = info.get("operatingCashflow") or cf_row("Operating Cash Flow",
                                                  "Total Cash From Operating Activities")
    fcf = info.get("freeCashflow")
    if fcf is None and ocf is not None:
        capex = cf_row("Capital Expenditure")
        fcf = ocf + capex if capex is not None else None
    ebitda = info.get("ebitda")

    return {
        "name_yf": info.get("shortName"),
        "currency": info.get("financialCurrency"), "fx_usd": fx,
        "rev_musd": usd(rev, fx),
        "rev_growth_pct": round(info["revenueGrowth"] * 100, 1)
            if info.get("revenueGrowth") is not None else None,
        "mktcap_musd": usd(info.get("marketCap"), fx),
        "employees": info.get("fullTimeEmployees"),
        "gross_margin_pct": round(info["grossMargins"] * 100, 1)
            if info.get("grossMargins") is not None else None,
        "op_margin_pct": round(info["operatingMargins"] * 100, 1)
            if info.get("operatingMargins") is not None else None,
        "net_margin_pct": round(info["profitMargins"] * 100, 1)
            if info.get("profitMargins") is not None else None,
        "ebitda_margin_pct": pct(ebitda, rev),
        "roe_pct": round(info["returnOnEquity"] * 100, 1)
            if info.get("returnOnEquity") is not None else None,
        "roa_pct": round(info["returnOnAssets"] * 100, 1)
            if info.get("returnOnAssets") is not None else None,
        "ni_musd": usd(ni, fx),
        "ocf_musd": usd(ocf, fx),
        "fcf_musd": usd(fcf, fx),
        "fcf_margin_pct": pct(fcf, rev),
        "debt_to_equity": round(info["debtToEquity"] / 100, 2)
            if info.get("debtToEquity") is not None else None,
        "current_ratio": info.get("currentRatio"),
        "eps": info.get("trailingEps"),
        "fwd_pe": info.get("forwardPE"),
    }


def main() -> int:
    sl = json.load(open(SHORTLIST))
    targets = sl["targets"]
    out = []
    fail = 0
    for i, x in enumerate(targets, 1):
        tk = yf_ticker(x.get("ticker", ""))
        rec = {k: x.get(k) for k in ("company", "ticker", "country", "sector",
                                     "tier", "target_score")}
        rec["yf"] = tk
        if tk:
            try:
                rec.update(pull(tk))
            except Exception as e:
                rec["error"] = f"{type(e).__name__}: {str(e)[:40]}"
                fail += 1
        else:
            rec["error"] = "no yf mapping"
            fail += 1
        out.append(rec)
        if i % 20 == 0:
            print(f"  …{i}/{len(targets)} ({fail} unmapped/failed)")
        time.sleep(0.3)

    df = pd.DataFrame(out)
    covered = df["rev_musd"].notna().sum()
    print(f"  {covered}/{len(df)} with financials")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"layer": "target_financials",
               "built": pd.Timestamp.now().strftime("%Y-%m-%d"),
               "covered": int(covered), "total": len(df),
               "companies": out}, open(OUT + ".tmp", "w"), indent=1, default=str)
    os.replace(OUT + ".tmp", OUT)

    # markdown: top targets by score, CFO metrics
    show = df[df["rev_musd"].notna()].copy()
    lines = [
        f"# Target-company CFO financials — {pd.Timestamp.now():%Y-%m-%d}",
        "",
        f"{covered}/{len(df)} India-intent targets with pulled financials "
        "(yfinance; USD millions unless noted). Metrics a CFO/IC screens "
        "before committing to an outreach or co-investment.",
        "",
        "| Company | Country | Sector | Score | Rev $M | Rev YoY% | Net mgn% "
        "| EBITDA mgn% | ROE% | FCF $M | FCF mgn% | Net inc $M | D/E |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    show = show.sort_values("target_score", ascending=False)
    for _, r in show.head(50).iterrows():
        g = lambda k: "" if pd.isna(r.get(k)) else r.get(k)  # noqa: E731
        lines.append(
            f"| {str(r['company'])[:28]} | {r['country'][:11]} "
            f"| {str(r['sector'])[:20]} | {g('target_score')} | {g('rev_musd')} "
            f"| {g('rev_growth_pct')} | {g('net_margin_pct')} "
            f"| {g('ebitda_margin_pct')} | {g('roe_pct')} | {g('fcf_musd')} "
            f"| {g('fcf_margin_pct')} | {g('ni_musd')} | {g('debt_to_equity')} |")

    # portfolio-level CFO aggregates
    agg = show[["rev_musd", "ni_musd", "fcf_musd"]].sum()
    lines += [
        "",
        "## Aggregate financial capacity of the recommendation set",
        "",
        f"- Combined revenue: **${agg['rev_musd'] / 1e6:.1f}T** across "
        f"{covered} companies",
        f"- Combined net income: **${agg['ni_musd'] / 1e3:.1f}B**",
        f"- Combined free cash flow: **${agg['fcf_musd'] / 1e3:.1f}B** "
        "(the war-chest actually available for Indian capex)",
        f"- Median ROE: **{show['roe_pct'].median():.1f}%** · "
        f"median net margin: {show['net_margin_pct'].median():.1f}% · "
        f"median FCF margin: {show['fcf_margin_pct'].median():.1f}%",
        "",
        "Read: these are the balance sheets behind the annual-report India",
        "intent. High FCF + high ROE names can self-fund an India plant from",
        "operating cash — the incentive is an accelerant, not a dependency.",
        "Low-FCF names need the PLI/capex subsidy to make the numbers work —",
        "a different (more incentive-sensitive) outreach conversation.",
    ]
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  wrote {os.path.relpath(OUT_MD, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
