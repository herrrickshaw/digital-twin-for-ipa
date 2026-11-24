"""build_target_financials with a fake yfinance module (yfinance is not a CI dependency)."""
import json
import sys
import time
import types

import pytest

pd = pytest.importorskip("pandas")

from conftest import load_script  # noqa: E402


class FakeTicker:
    registry = {}

    def __init__(self, tk):
        spec = FakeTicker.registry[tk]
        if isinstance(spec, Exception):
            raise spec
        self.info = spec.get("info", {})
        if "financials" in spec:
            self.financials = spec["financials"]
        if "cashflow" in spec:
            self.cashflow = spec["cashflow"]


@pytest.fixture
def mod(fake_repo, monkeypatch):
    FakeTicker.registry = {}
    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(Ticker=FakeTicker))
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    m = load_script("build_target_financials", fake_repo)
    return m, fake_repo


@pytest.mark.parametrize("raw,expected", [
    ("TSE:7203", "7203.T"), ("krx:005930", "005930.KS"), ("KOSDAQ:123", "123.KQ"), ("LON:RR", "RR.L"),
    ("HKG:700", "700.HK"), ("XYZ:1", None), ("AAPL", "AAPL"), (" MSFT ", "MSFT"),
    ("", None), ("  ", None), ("NYSE:X", None),
])
def test_yf_ticker(mod, raw, expected):
    m, _ = mod
    assert m.yf_ticker(raw) == expected


def test_usd_and_pct(mod):
    m, _ = mod
    assert m.usd(2_500_000, 1.0) == 2.5 and m.usd(1_000_000_000, 0.0064) == 6.4
    assert m.usd(None, 1) is None and m.usd(5, None) is None and m.usd(float("nan"), 1) is None
    assert m.pct(1, 4) == 25.0 and m.pct(1, 3) == 33.3 and m.pct(-1, 4) == -25.0
    assert m.pct(None, 4) is None and m.pct(1, None) is None and m.pct(1, 0) is None
    assert m.pct(float("nan"), 4) is None and m.pct(1, float("nan")) is None


def test_pull_prefers_info_and_scales_units(mod):
    m, _ = mod
    FakeTicker.registry["T1"] = {"info": {
        "shortName": "Tee One", "financialCurrency": "JPY", "totalRevenue": 100_000_000_000,
        "revenueGrowth": 0.1234, "marketCap": 50_000_000_000, "fullTimeEmployees": 10,
        "grossMargins": 0.5, "operatingMargins": 0.25, "profitMargins": 0.1, "returnOnEquity": 0.123,
        "returnOnAssets": 0.05, "netIncomeToCommon": 10_000_000_000, "operatingCashflow": 20_000_000_000,
        "freeCashflow": 5_000_000_000, "ebitda": 30_000_000_000, "debtToEquity": 150.0, "currentRatio": 1.5,
        "trailingEps": 2.0, "forwardPE": 12.0}}
    r = m.pull("T1")
    assert r["currency"] == "JPY" and r["fx_usd"] == 0.0064 and r["name_yf"] == "Tee One"
    assert r["rev_musd"] == 640.0 and r["mktcap_musd"] == 320.0 and r["ni_musd"] == 64.0
    assert r["ocf_musd"] == 128.0 and r["fcf_musd"] == 32.0
    assert r["rev_growth_pct"] == 12.3 and r["roe_pct"] == 12.3 and r["gross_margin_pct"] == 50.0
    assert r["op_margin_pct"] == 25.0 and r["net_margin_pct"] == 10.0 and r["roa_pct"] == 5.0
    assert r["ebitda_margin_pct"] == 30.0 and r["fcf_margin_pct"] == 5.0
    assert r["debt_to_equity"] == 1.5 and r["current_ratio"] == 1.5 and r["eps"] == 2.0 and r["fwd_pe"] == 12.0


def test_pull_falls_back_to_statements(mod):
    m, _ = mod
    fin = pd.DataFrame({"2025": [1_000_000_000.0, 100_000_000.0], "2024": [float("nan"), 50.0]},
                       index=["Total Revenue", "Net Income"])
    cf = pd.DataFrame({"2025": [300_000_000.0, -100_000_000.0]}, index=["Operating Cash Flow", "Capital Expenditure"])
    FakeTicker.registry["T2"] = {"info": {"financialCurrency": "USD"}, "financials": fin, "cashflow": cf}
    r = m.pull("T2")
    assert r["rev_musd"] == 1000.0 and r["ni_musd"] == 100.0 and r["ocf_musd"] == 300.0
    assert r["fcf_musd"] == 200.0 and r["fcf_margin_pct"] == 20.0         # ocf + (negative) capex
    assert r["rev_growth_pct"] is None and r["roe_pct"] is None and r["debt_to_equity"] is None


def test_pull_alternate_row_names_and_missing_capex(mod):
    m, _ = mod
    cf = pd.DataFrame({"2025": [400_000_000.0]}, index=["Total Cash From Operating Activities"])
    FakeTicker.registry["T3"] = {"info": {"financialCurrency": "ZZZ", "totalRevenue": 10}, "cashflow": cf,
                                 "financials": pd.DataFrame()}
    r = m.pull("T3")
    assert r["fx_usd"] is None and r["rev_musd"] is None and r["ocf_musd"] is None    # unknown currency -> no USD figures
    FakeTicker.registry["T4"] = {"info": {"financialCurrency": "USD"}, "cashflow": cf}
    r = m.pull("T4")
    assert r["ocf_musd"] == 400.0 and r["fcf_musd"] is None                           # no capex row -> no fcf


def _shortlist(root, targets):
    (root / "layers").mkdir(exist_ok=True)
    (root / "layers/16_target_shortlist.json").write_text(json.dumps({"targets": targets}))


def test_main(mod, capsys):
    m, root = mod
    FakeTicker.registry["7203.T"] = {"info": {
        "financialCurrency": "USD", "totalRevenue": 4e12, "netIncomeToCommon": 3e11, "freeCashflow": 2e11,
        "returnOnEquity": 0.2, "profitMargins": 0.075, "shortName": "Toyota"}}
    FakeTicker.registry["BAD"] = RuntimeError("yahoo down " + "x" * 80)
    FakeTicker.registry["LOW"] = {"info": {"financialCurrency": "USD", "totalRevenue": 2e9, "netIncomeToCommon": 1e8,
                                           "freeCashflow": -1e7, "returnOnEquity": 0.05, "profitMargins": 0.05}}
    _shortlist(root, [
        {"company": "Toyota Motor Corporation Long Name Here", "ticker": "TSE:7203", "country": "Japan",
         "sector": "Auto, EV & Components", "tier": "HIGH", "target_score": 120},
        {"company": "Unmapped", "ticker": "XYZ:1", "country": "Nowhere", "sector": "S", "tier": "HIGH", "target_score": 90},
        {"company": "Broken", "ticker": "BAD", "country": "Japan", "sector": "S", "tier": "HIGH", "target_score": 80},
        {"company": "Lowco", "ticker": "LOW", "country": "Korea", "sector": "S", "tier": "MEDIUM", "target_score": 100},
    ])
    assert m.main() == 0
    out = json.load(open(root / "layers/16_enrichment/target_financials.json"))
    assert out["covered"] == 2 and out["total"] == 4
    by = {c["company"]: c for c in out["companies"]}
    assert by["Unmapped"]["error"] == "no yf mapping" and by["Unmapped"]["yf"] is None
    assert by["Broken"]["error"] == "RuntimeError: " + "yahoo down " + "x" * 29                # message cut to 40 chars
    assert by["Lowco"]["rev_musd"] == 2000.0 and by["Lowco"]["fcf_musd"] == -10.0
    assert not (root / "layers/16_enrichment/target_financials.json.tmp").exists()
    md = (root / "docs/TARGET_FINANCIALS.md").read_text()
    assert "2/4 India-intent targets with pulled financials" in md
    rows = [l for l in md.splitlines() if l.startswith("| ") and "Rev $M" not in l]
    assert rows[0].startswith("| Toyota Motor Corporation Lo")                     # highest score first, name cut to 28
    assert rows[1].startswith("| Lowco |") and len(rows) == 2
    assert "Combined revenue: **$4.0T** across 2 companies" in md
    assert "Combined net income: **$300.1B**" in md and "Combined free cash flow: **$200.0B**" in md
    assert "Median ROE: **12.5%**" in md
    text = capsys.readouterr().out
    assert "2/4 with financials" in text and "wrote docs/TARGET_FINANCIALS.md" in text


def test_main_progress_line_every_20(mod, capsys):
    m, root = mod
    FakeTicker.registry["OK"] = {"info": {"financialCurrency": "USD", "totalRevenue": 1e9, "returnOnEquity": 0.1,
                                          "profitMargins": 0.1, "netIncomeToCommon": 1e8, "freeCashflow": 1e8}}
    _shortlist(root, [{"company": f"C{i}", "ticker": "OK", "country": "Japan", "sector": "S", "tier": "HIGH",
                       "target_score": i} for i in range(21)])
    m.main()
    assert "…20/21 (0 unmapped/failed)" in capsys.readouterr().out
