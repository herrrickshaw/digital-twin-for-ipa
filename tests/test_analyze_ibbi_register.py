"""IBBI register analysis: state parsing, liquidity / friction rules, PDF fallback, layer 34 block."""
import json
import subprocess
import sys
import tempfile
import urllib.request

import pytest

from _fakes import FakeResp, completed
from conftest import load_script

duckdb = pytest.importorskip("duckdb")


@pytest.fixture(scope="module")
def m():
    return load_script("analyze_ibbi_register", None)


@pytest.mark.parametrize("text,state", [
    ("Plot at Surat, Gujarat 395007", "Gujarat"),
    ("flat in tamil nadu", "Tamil Nadu"),
    ("Pondicherry unit", "Puducherry"),
    ("Orissa plant", "Odisha"),
    ("Jammu plant", "Jammu & Kashmir"),
    ("kashmir orchard", "Jammu & Kashmir"),
    ("West Bengal and Assam", "Assam"),              # first match in text order? (regex alternation order)
    ("Biharsharif town", None),                       # word boundary
    ("no state here", None), ("", None), (None, None),
])
def test_find_state(m, text, state):
    got = m.find_state(text)
    if text == "West Bengal and Assam":
        assert got in ("West Bengal", "Assam")
    else:
        assert got == state


@pytest.mark.parametrize("assets,expected", [
    ("Sale as a Going Concern", "high"), ("As-Is-Where-Is basis", "high"), ("Block A of company", "high"),
    ("Slump sale of unit", "high"),
    ("Plant and Machinery", "medium"), ("Inventory lot", "medium"), ("Stock of goods", "medium"),
    ("Land and Building", "low"), ("residential flat", "low"), ("Office premises", "low"), ("Shop no 4", "low"),
    ("misc assets", "medium"), ("", "medium"), (None, "medium"),
    ("Plant on land", "medium"),                  # medium keywords checked before low
    ("going concern incl. land", "high"),
])
def test_liquidity(m, assets, expected):
    assert m.liquidity(assets) == expected


@pytest.mark.parametrize("liq,n,res,falling,expected", [
    ("low", 1, None, False, "low"),
    ("low", 1, 1, False, "low"),                           # small reserve pushes below zero -> low
    ("medium", 1, None, False, "medium"),
    ("high", 1, None, False, "high"),
    ("low", 3, None, False, "medium"),                     # notice_count threshold is >= 3
    ("low", 2, None, False, "low"),
    ("low", 1, None, True, "medium"),
    ("low", 3, None, True, "high"),
    ("low", 1, 1_00_00_00_001, False, "medium"),           # > Rs 100 cr
    ("low", 1, 1_00_00_00_000, False, "low"),              # exactly 100 cr is not "greater than"
    ("medium", 1, 5_00_00_000, False, "medium"),           # exactly 5 cr is not "< 5 cr"
    ("medium", 1, 4_99_99_999, False, "low"),              # small single parcel: -1
    ("high", 3, 2_00_00_00_000, True, "high"),
])
def test_friction(m, liq, n, res, falling, expected):
    assert m.friction(liq, n, res, falling) == expected


def test_pdf_state(m, monkeypatch, tmp_path):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResp(b"%PDF"))
    seen = {}

    def run(cmd, capture_output=None, timeout=None):
        seen["cmd"] = cmd
        return completed(b"Property situated at Nagpur, Maharashtra")
    monkeypatch.setattr(subprocess, "run", run)
    assert m.pdf_state("http://x/a.pdf") == "Maharashtra"
    assert seen["cmd"][:5] == ["pdftotext", "-f", "1", "-l", "6"]
    assert not list(tmp_path.glob("*.pdf"))              # temp file removed
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: completed(b"nothing"))
    assert m.pdf_state("u") is None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(OSError("net")))
    assert m.pdf_state("u") is None


def _mkparquet(root, rows):
    reg = root / "data/registers"
    reg.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("create table t(notice_pdf varchar, corporate_debtor varchar, reserve_price_inr bigint,"
                " nature_of_assets varchar, auction_date varchar, notice_date varchar)")
    con.executemany("insert into t values (?,?,?,?,?,?)", rows)
    con.execute(f"copy t to '{reg / 'ibbi_liquidation.parquet'}' (format parquet)")
    (root / "layers/34_stressed_assets.json").write_text(json.dumps({"keep": 1}))


def test_main(fake_repo, monkeypatch, capsys, tmp_path):
    rows = [
        # debtor A: 3 notices, falling reserve; two in Gujarat text
        ("a1", "Alpha", 6_00_00_000, "Land at Surat Gujarat", "d", "n"),
        ("a2", "Alpha", 5_50_00_000, "Land at Surat Gujarat", "d", "n"),
        ("a3", "Alpha", 5_00_00_000, "Land and flat", "d", "n"),
        # debtor B: single going-concern notice in Assam, tiny
        ("b1", "Beta", 1_00_000, "Going concern, Guwahati, Assam", "d", "n"),
        # C: no state in text, largest reserve -> PDF lookup
        ("/uploads/c1.pdf", "Gamma", 50_00_00_000, "Plant", "d", "n"),
        # D: no state, no reserve -> never PDF looked-up
        ("d1", "Delta", None, "Plant", "d", "n"),
        # E: no state, second largest reserve (excluded when --pdf-top 1)
        ("https://x/e1.pdf", "Epsilon", 20_00_00_000, "Land", "d", "n"),
    ]
    _mkparquet(fake_repo, rows)
    m = load_script("analyze_ibbi_register", fake_repo)
    pdf_calls = []
    monkeypatch.setattr(m, "pdf_state", lambda url: (pdf_calls.append(url), "Karnataka")[1])
    monkeypatch.setattr(sys, "argv", ["x", "--pdf-top", "1"])
    m.main()
    assert pdf_calls == ["https://ibbi.gov.in/uploads/c1.pdf"]
    layer = json.load(open(fake_repo / "layers/34_stressed_assets.json"))
    sr = layer["state_resolution"]
    assert layer["keep"] == 1 and sr["total_notices"] == 7
    cov = sr["state_coverage"]
    assert cov["resolved"] == 4 and cov["from_pdf_top"] == 1 and cov["unknown"] == 3
    assert cov["from_asset_text"] == 3
    assert "top-1 by reserve price" in cov["note"] and "~43 pct" in cov["note"]
    table = {r["state"]: r for r in sr["state_wise"]}
    assert table["Gujarat"]["notices"] == 2 and table["Assam"]["notices"] == 1 and table["Karnataka"]["notices"] == 1
    assert [r["state"] for r in sr["state_wise"]][0] == "Gujarat"            # most common first
    # Alpha has 3 notices with a falling reserve: land (0) + 1 + 1 = high for both Gujarat notices
    g = table["Gujarat"]
    assert (g["friction_low"], g["friction_medium"], g["friction_high"]) == (0, 0, 2)
    assert g["median_reserve_inr"] == 6_00_00_000 and g["low_friction_pct"] == round(100 * g["friction_low"] / 2)
    assert table["Assam"]["median_reserve_inr"] == 1_00_000
    assert sum(sr["friction_overall"].values()) == 7
    assert sr["friction_method"].startswith("RULE-BASED proxy")
    out = capsys.readouterr().out
    assert "notices 7 | state resolved 4 (+1 via PDF) | unknown 3" in out
    assert "state               notices  low%  med  high  median_reserve" in out
    assert "Rs 60,000,000" in out


def test_main_pdf_top_default_covers_all_and_no_reserve_skipped(fake_repo, monkeypatch):
    _mkparquet(fake_repo, [("x1", "A", 10, "Land", "d", "n"), ("x2", "B", None, "Land", "d", "n"),
                           ("x3", "C", 0, "Land", "d", "n")])
    m = load_script("analyze_ibbi_register", fake_repo)
    calls = []
    monkeypatch.setattr(m, "pdf_state", lambda url: (calls.append(url), None)[1])
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    assert calls == ["x1"]            # falsy reserves (None / 0) are never PDF-parsed
