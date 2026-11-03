"""Characterisation of register_ibbi_liquidation.main with stub pages, a temp parquet and a synthetic companies.db."""
import json
import sqlite3
import sys

import pytest

duckdb = pytest.importorskip("duckdb")
import register_ibbi_liquidation as rib  # noqa: E402
from conftest import sha  # noqa: E402

GOLDEN = {'out': '1092c607a247ed366788569e249884a887e168cc56d0b7ef6d8242428b71d434', 'db': '18d81b1a79cad7caf8fa54b6837ba5f2e9deb75d64a53c37094217dc10160d94', 'layer': '1917068bb6666db9fada1d75ee609a08705b580e7510dae4066a3490dfbc522d', 'pq': '389c5b162e463888846c33dca936ddf1dde7055a41da9a035138da36a718bcbc'}


def _page(rows):
    trs = ""
    for i, (cd, price, assets) in enumerate(rows):
        trs += ("<tr><td>Liquidation</td><td>01-01-2026</td><td>%s</td><td>10-02-2026</td><td>IP %d</td>"
                '<td><a href=/auction_notice_liquidation/notice%s.pdf>pdf</a></td><td>%s</td><td>%s</td><td>05-02-2026</td><td>d</td></tr>' % (cd, i, cd[:3], price, assets))
    return "<table>" + trs + "<tr><td>no marker</td></tr></table>"


PAGES = {
    "https://ibbi.gov.in/liquidation-auction-notices/lists": _page([("Acme Holdings Limited", "1,50,000", "Plant"), ("Zed Steel Pvt Ltd", "25,00,000", "Land"), ("Bad Price Co", "n/a", "Plant")]),
    "https://ibbi.gov.in/liquidation-auction-notices/lists?page=2": _page([("Acme Holdings Limited", "1,50,000", "Plant"), ("Quiet Metals Pvt Ltd", "900", "Stock")]),
}


def test_main_identical(tmp_path, monkeypatch, capsys, frozen_today):
    db = tmp_path / "companies.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE companies(company_id INTEGER PRIMARY KEY, name TEXT)")
    con.executemany("INSERT INTO companies VALUES (?,?)", [(1, "Acme Holdings Ltd"), (2, "Quiet Metals Pvt Ltd"), (3, "Other")])
    con.commit()
    con.close()
    layer = tmp_path / "34.json"
    layer.write_text(json.dumps({"keep": 1}))
    reg = tmp_path / "registers"
    monkeypatch.setattr(rib, "DB", str(db))
    monkeypatch.setattr(rib, "LAYER", str(layer))
    monkeypatch.setattr(rib, "OUTDIR", str(reg))
    monkeypatch.setattr(rib, "PARQUET", str(reg / "ibbi.parquet"))
    monkeypatch.setattr(rib, "date", frozen_today)
    monkeypatch.setattr(rib, "get", lambda url, timeout=40: PAGES.get(url, "<html></html>"))
    monkeypatch.setattr(rib.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["register.py", "--pages", "4"])
    rib.main()
    out = capsys.readouterr().out.replace(str(tmp_path), "<TMP>")
    c = sqlite3.connect(db)
    dump = "\n".join(c.iterdump())
    c.close()
    pq = duckdb.connect().execute(f"SELECT * FROM read_parquet('{reg / 'ibbi.parquet'}') ORDER BY notice_pdf").fetchall()
    # asset_type_mix tie order is engine-dependent, hence the sorted-key JSON hash for the layer
    got = {"out": sha(out), "db": sha(dump), "layer": sha(json.dumps(json.loads(layer.read_text()), sort_keys=True)), "pq": sha(repr(pq))}
    assert got == GOLDEN
