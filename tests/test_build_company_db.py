"""Characterisation of layer 32 (company DB) on a miniature fixture; golden values from the pre-refactor script."""
import datetime
import hashlib
import json
import sqlite3

import build_company_db as cdb

EXPECTED_COUNTS = {
    "companies": 11, "in_more_than_one_layer": 3,
    "by_role": {"alias_check": 1, "clearance_lead": 2, "defence_corridor_tenant": 2, "foreign_lead": 2,
                "pairing_prospective": 1, "pairing_verified": 1, "plant_location_check": 1,
                "pli_bulk_drugs_beneficiary": 1, "pli_medical_devices_beneficiary": 1,
                "pli_textiles_foreign_beneficiary": 1, "pool_policy": 1, "pool_visibility": 1,
                "shortlist_target": 1},
    "india_entities": 4, "credit_rated": 1,
    "by_country_top10": {"India": 6, "?": 2, "Switzerland": 1, "Germany": 1, "France": 1},
}
EXPECTED_DUMP_SHA = "b28d56f0dd59e928c13765ab5c7cb4e0a0a9f151dc7d67328970ce6b8f37cf48"


def run(mini_root, monkeypatch):
    monkeypatch.setattr(cdb, "LAYERS", str(mini_root / "layers"))
    monkeypatch.setattr(cdb, "DATA", str(mini_root / "data"))
    db_path = str(mini_root / "data" / "companies.db")
    monkeypatch.setattr(cdb, "DB_PATH", db_path)
    con = cdb.build_database()
    return con, db_path


def test_dedup_and_counts(mini_root, monkeypatch):
    con, _ = run(mini_root, monkeypatch)
    summary = cdb.build_summary(con.cursor(), "2026-01-01")
    assert summary["counts"] == EXPECTED_COUNTS
    assert summary["sources"] == cdb.SOURCE_LAYERS and summary["layer"] == 32


def test_database_dump_is_bit_identical_to_pre_refactor(mini_root, monkeypatch):
    con, _ = run(mini_root, monkeypatch)
    digest = hashlib.sha256("\n".join(con.iterdump()).encode()).hexdigest()
    assert digest == EXPECTED_DUMP_SHA


def test_upsert_keeps_longest_name_and_fills_blanks(mini_root, monkeypatch):
    con, _ = run(mini_root, monkeypatch)
    row = con.execute("SELECT name, sector, ticker, market FROM companies WHERE name_norm='acme' AND country='Germany'").fetchone()
    assert row == ("Acme Holdings GmbH", "Auto", "ACM", "XETRA")


def test_main_writes_layer_file(mini_root, monkeypatch, capsys):
    monkeypatch.setattr(cdb, "OUT_LAYER", str(mini_root / "layers" / "32_company_db.json"))
    run(mini_root, monkeypatch)[0].close()
    cdb.main()
    out = json.load(open(cdb.OUT_LAYER))
    assert out["built"] == datetime.date.today().isoformat() and out["counts"]["companies"] == 11
    assert "wrote" in capsys.readouterr().out
    assert sqlite3.connect(cdb.DB_PATH).execute("SELECT COUNT(*) FROM company_card").fetchone()[0] == 11
