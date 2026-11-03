"""Characterisation of enrich_company_db_ii_tickers.main with stubbed scraping and a synthetic companies.db."""
import json
import sqlite3

import enrich_company_db_ii_tickers as eii
from conftest import sha

GOLDEN = {'normal': {'db': '2574f9e05b1db674ad775397187f3d636af16017cfc6ead65f1c8f7d3a74589c', 'layer': '43a49062048becc76a75d803ce65bcd16dcec71b4d5d46440dd09c0fd8a1033b', 'out': 'e19a0ccdf927110f441ca3d3d2453025b6bf0fa631d9be7bada703adc74b6ef1'}, 'blocked': {'db': '61427b2b9258ec2d9f904c48dd741c8a8ccbb59d016ed062ccc59cd67d68ad61', 'layer': 'f33f6051966cdeb53f3ba89dfa7c9f27faa275125b37415667e35b4c292aeed5', 'out': 'a565e8cc1da0c9c0ca2d1b23dcce53c2ff90991f512ea5f6069c9d9908477156'}}


def _setup(tmp_path, monkeypatch, urls, pages, frozen):
    monkeypatch.setattr(eii, "date", frozen)
    db = tmp_path / "companies.db"
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE companies(company_id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE clearance_activity(company_id INTEGER, visibility_verdict TEXT);
    INSERT INTO companies VALUES (1,'Acme Holdings Ltd'),(2,'Quiet Metals Pvt Ltd'),(3,'Panasonic'),(4,'Unrelated Inc');
    INSERT INTO clearance_activity VALUES (2,'QUIET'),(1,'PARTIALLY_VISIBLE');
    """)
    con.commit()
    con.close()
    layer = tmp_path / "32.json"
    layer.write_text(json.dumps({"keep": 1, "ii_ticker_validation": {"old": True}}))
    monkeypatch.setattr(eii, "DB", str(db))
    monkeypatch.setattr(eii, "LAYER", str(layer))
    monkeypatch.setattr(eii, "sector_urls", urls)
    monkeypatch.setattr(eii, "scrape_ticker", lambda u: pages[u])
    return db, layer


def _snapshot(db, layer, out):
    con = sqlite3.connect(db)
    dump = "\n".join(con.iterdump())
    con.close()
    return {"db": sha(dump), "layer": sha(layer.read_bytes()), "out": sha(out)}


def test_normal_run(tmp_path, monkeypatch, capsys, frozen_today):
    pages = {"http://s/a": [("Quiet Metals plans a plant in Gujarat", "http://src/1"), ("Panasonic opens centre", "http://src/2")],
             "http://s/b": [("__FETCH_ERROR__", "HTTP 500"), ("Acme Holdings expands", "http://src/3")]}
    db, layer = _setup(tmp_path, monkeypatch, lambda: list(pages), pages, frozen_today)
    eii.main()
    got = _snapshot(db, layer, capsys.readouterr().out)
    assert got == GOLDEN["normal"]


def test_blocked_run(tmp_path, monkeypatch, capsys, frozen_today):
    def boom():
        raise OSError("403")
    db, layer = _setup(tmp_path, monkeypatch, boom, {}, frozen_today)
    eii.main()
    got = _snapshot(db, layer, capsys.readouterr().out)
    assert got == GOLDEN["blocked"]
