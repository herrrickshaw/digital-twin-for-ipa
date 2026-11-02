"""Characterisation of the shared name normaliser and known-company lookup."""
import json
import sqlite3

import pytest

from twin_common import known_company_names, norm_company

# Expected values captured from the pre-refactor build_company_db.norm().
CASES = [
    ("M/s Bharat Steel Ltd.", "bharat steel"),
    ("Acme Holdings GmbH", "acme"),
    ("Tata  Consultancy Services Limited", "tata consultancy services"),
    ("  JSW Steel (India) Pvt. Ltd ", "jsw steel india"),
    ("", ""),
    (None, ""),
    ("Nestlé S.A.", "nestl s a"),
]


@pytest.mark.parametrize("raw,expected", CASES)
def test_norm_company(raw, expected):
    assert norm_company(raw) == expected


def test_known_company_names_reads_leads_and_db(mini_root):
    (mini_root / "data").mkdir()
    con = sqlite3.connect(str(mini_root / "data" / "companies.db"))
    con.execute("CREATE TABLE companies (name TEXT)")
    con.executemany("INSERT INTO companies VALUES (?)", [(" Zed Corp ",), (None,)])
    con.commit()
    con.close()
    names = known_company_names(str(mini_root))
    assert "acme holdings gmbh" in names and "zed corp" in names


def test_known_company_names_db_error_policy(mini_root):
    (mini_root / "data").mkdir()
    (mini_root / "data" / "companies.db").write_text("not a database")
    assert "acme holdings gmbh" in known_company_names(str(mini_root), tolerate_db_errors=True)
    with pytest.raises(Exception):
        known_company_names(str(mini_root))


def test_known_company_names_without_inputs(tmp_path):
    assert known_company_names(str(tmp_path)) == set()
    (tmp_path / "layers").mkdir()
    (tmp_path / "layers" / "16_leads.json").write_text(json.dumps({"leads": [{"company": " A B "}]}))
    assert known_company_names(str(tmp_path)) == {"a b"}
