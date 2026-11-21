import json
import sys

import pytest

duckdb = pytest.importorskip("duckdb")
import analyze_ibbi_register as ib  # noqa: E402


@pytest.mark.parametrize("text,state", [
    ("Plot at Sector 5, Gurugram, Haryana", "Haryana"),
    ("Flat in Pondicherry", "Puducherry"),
    ("land in orissa", "Odisha"),
    ("Srinagar, Kashmir", "Jammu & Kashmir"),
    ("", None), (None, None),
])
def test_find_state(text, state):
    assert ib.find_state(text) == state


@pytest.mark.parametrize("assets,liq", [
    ("Sale as a going concern", "high"),
    ("Plant and Machinery", "medium"),
    ("Residential flat", "low"),
    ("Something else", "medium"),
    (None, "medium"),
])
def test_liquidity(assets, liq):
    assert ib.liquidity(assets) == liq


def test_friction_scoring_hand_computed():
    assert ib.friction("low", 1, 10 * 10**7, False) == "low"           # 0
    assert ib.friction("low", 3, 10 * 10**7, False) == "medium"        # +1 repeat
    assert ib.friction("medium", 1, 200 * 10**7, True) == "high"       # 1+1+1
    assert ib.friction("medium", 1, 1 * 10**7, False) == "low"         # 1-1 small ticket
    assert ib.friction("high", 1, None, False) == "high"


def _run_main(tmp_path, monkeypatch, rows):
    pq = tmp_path / "ibbi.parquet"
    con = duckdb.connect()
    con.execute("CREATE TABLE t (notice_date VARCHAR, corporate_debtor VARCHAR, "
                "auction_date VARCHAR, notice_pdf VARCHAR, reserve_price_inr BIGINT, "
                "nature_of_assets VARCHAR)")
    con.executemany("INSERT INTO t VALUES (?,?,?,?,?,?)", rows)
    con.execute(f"COPY t TO '{pq}' (FORMAT PARQUET)")
    layer = tmp_path / "34.json"
    layer.write_text("{}")
    monkeypatch.setattr(ib, "PARQUET", str(pq))
    monkeypatch.setattr(ib, "LAYER", str(layer))
    monkeypatch.setattr(sys, "argv", ["x", "--pdf-top", "0"])
    ib.main()
    return json.loads(layer.read_text())["state_resolution"]


def test_falling_reserve_detected_with_register_in_newest_first_order(tmp_path, monkeypatch):
    """The IBBI register (and the committed parquet) lists notices newest first.
    A debtor re-auctioned at Rs 80 cr after an earlier Rs 100 cr notice has a
    FALLING reserve (+1 friction -> medium); comparing first-listed vs
    last-listed instead read it as rising (-> low)."""
    rows = [  # newest first, as in the register
        ("23-07-2026", "SYNTH DEBTOR", "10-08-2026", "/n2.pdf", 80 * 10**7, "Land in Goa"),
        ("02-01-2026", "SYNTH DEBTOR", "01-02-2026", "/n1.pdf", 100 * 10**7, "Land in Goa"),
    ]
    sr = _run_main(tmp_path, monkeypatch, rows)
    assert sr["friction_overall"] == {"medium": 2}


def test_rising_reserve_not_flagged_falling(tmp_path, monkeypatch):
    rows = [
        ("23-07-2026", "SYNTH DEBTOR", "10-08-2026", "/n2.pdf", 100 * 10**7, "Land in Goa"),
        ("02-01-2026", "SYNTH DEBTOR", "01-02-2026", "/n1.pdf", 80 * 10**7, "Land in Goa"),
    ]
    sr = _run_main(tmp_path, monkeypatch, rows)
    assert sr["friction_overall"] == {"low": 2}
    assert sr["state_wise"][0]["state"] == "Goa"
