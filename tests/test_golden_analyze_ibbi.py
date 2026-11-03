"""Characterisation of analyze_ibbi_register.main on a synthetic parquet with a stubbed PDF state lookup."""
import json
import sys

import pytest

duckdb = pytest.importorskip("duckdb")
import analyze_ibbi_register as air  # noqa: E402
from conftest import sha  # noqa: E402

GOLDEN = {'out': '82f04008b1eae7cabf26b7cce9746fee8940966780559c9e15c3951a46e50a17', 'layer': '187e135fc1c97ce2653c87c535f6824cb64f618d78b9d140bfbcba3dda1d6301'}

ROWS = [
    ("/a/1.pdf", "Acme Ltd", 150000000, "Land and building at Plot 4, Pune, Maharashtra", "2026-02-01", "2026-01-01"),
    ("/a/2.pdf", "Acme Ltd", 100000000, "Land and building at Plot 4, Pune, Maharashtra", "2026-03-01", "2026-02-01"),
    ("/a/3.pdf", "Zed Steel", 900000, "Plant and machinery as going concern, Gujarat", "2026-02-01", "2026-01-01"),
    ("/a/4.pdf", "Quiet Co", 5000000, "Stock of finished goods", "2026-02-01", "2026-01-01"),
    ("/b/5.pdf", "Loner", 2500000000, "Composite going concern, whole company", "2026-02-01", "2026-01-01"),
    ("/b/6.pdf", "NoPrice", None, "Flat in Chennai, Tamil Nadu", "2026-02-01", "2026-01-01"),
]


def test_main_identical(tmp_path, monkeypatch, capsys, frozen_today):
    pq = tmp_path / "ibbi.parquet"
    con = duckdb.connect()
    con.execute("CREATE TABLE t(notice_pdf VARCHAR, corporate_debtor VARCHAR, reserve_price_inr BIGINT, nature_of_assets VARCHAR, auction_date VARCHAR, notice_date VARCHAR)")
    con.executemany("INSERT INTO t VALUES (?,?,?,?,?,?)", ROWS)
    con.execute(f"COPY (SELECT * FROM t ORDER BY notice_pdf) TO '{pq}' (FORMAT PARQUET)")
    layer = tmp_path / "34.json"
    layer.write_text(json.dumps({"keep": 1}))
    monkeypatch.setattr(air, "PARQUET", str(pq))
    monkeypatch.setattr(air, "LAYER", str(layer))
    monkeypatch.setattr(air, "pdf_state", lambda url: "Karnataka" if url.endswith("/b/5.pdf") else None)
    monkeypatch.setattr(sys, "argv", ["analyze.py", "--pdf-top", "3"])
    air.main()
    out = capsys.readouterr().out
    got = {"out": sha(out), "layer": sha(layer.read_bytes())}
    assert got == GOLDEN
