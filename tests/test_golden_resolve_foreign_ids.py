"""Characterisation of resolve_foreign_registry_ids.main with stubbed registries, a fake duckdb and a synthetic companies.db."""
import io
import sqlite3
import sys
import types
import zipfile

import pytest

import resolve_foreign_registry_ids as rfr
from conftest import sha

GOLDEN = {'ch_key': {'out': '6ecf7d8160526a94e34dd48f3ac3673f9a7f4bdf6459d93cc645e446e27087a7', 'db': 'b703e5515baaaf625cc9b72f915bda1cbd162cba7841990d7f63938afa97b5f0', 'duck': '0ba159b978001500bbc0d9e3b6fddfe2101c4c2b053709446776b5a62a998fb5'}, 'jp_key': {'out': 'b4c3a3b0e14f6cd1afa100e90e2afd41f120ac2a7c71d4bf507badf46224faf7', 'db': '928113c111c221a65d6df1069f4c61b34a5fd5099fa9b2eb5799d7daecd6086d', 'duck': '0ba159b978001500bbc0d9e3b6fddfe2101c4c2b053709446776b5a62a998fb5'}}

COMPANIES = [(1, "Apple Inc", "United States", "AAPL"), (2, "Apple Dup", "United States", None),
             (3, "LG Electronics", "South Korea", "A066570 (KOSE 066570)"), (4, "Nestle SA", "Switzerland", "NESN.SW"),
             (5, "Danone", "France", "BN.PA"), (6, "Unilever", "United Kingdom", "ULVR.L"),
             (7, "Toyota", "Japan", "7203.T"), (8, "Germany Co", "Germany", None), (9, "Indian Co", "India", "X"),
             (10, "Boom Ltd", "Switzerland", None)]

CORPCODE = ("<result><list><corp_code>00126380</corp_code><corp_name>LG</corp_name><stock_code>066570</stock_code></list></result>")


class _Resp:
    def __init__(self, data):
        self._d = data

    def read(self):
        return self._d


def _run(tmp_path, monkeypatch, capsys, frozen_today, keys):
    db = tmp_path / "companies.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE companies(company_id INTEGER PRIMARY KEY, name TEXT, country TEXT, ticker TEXT)")
    con.executemany("INSERT INTO companies VALUES (?,?,?,?)", COMPANIES)
    con.commit()
    con.close()
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        z.writestr("CORPCODE.xml", CORPCODE)

    def fake_get_json(url, ua=rfr.UA, timeout=25):
        if "company_tickers" in url:
            return {"0": {"ticker": "AAPL", "cik_str": 320193}}
        if "gleif" in url:
            if "Boom" in url or "Dup" in url:
                raise OSError("gleif down")
            return {"data": [{"attributes": {"lei": "LEI" + str(len(url)), "entity": {"legalName": {"name": "Legal"}}}}]} if "Toyota" not in url else {"data": []}
        if "gouv.fr" in url:
            return {"results": [{"siren": "552032534"}]}
        raise OSError(url)

    def fake_post(url, body, timeout=25):
        if body["name"] == "Boom":
            raise OSError("zefix")
        return {"list": [{"uidFormatted": "CHE-1"}]}

    def fake_urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req
        if "opendart" in url:
            return _Resp(zbuf.getvalue())
        if "company-information" in url:
            return _Resp(b'{"items": [{"company_number": "00000042"}]}')
        if "gbiz" in url:
            return _Resp('{"hojin-infos": [{"corporate_number": "1234567890123"}]}'.encode())
        raise OSError(url)

    fake_duck = types.SimpleNamespace(calls=[])

    class Con:
        def execute(self, sql, params=None):
            fake_duck.calls.append((" ".join(sql.split()), params))
            return types.SimpleNamespace(fetchall=lambda: [("United States",), ("South Korea",), ("Hong Kong",)])

    fake_duck.connect = lambda: Con()
    monkeypatch.setitem(sys.modules, "duckdb", fake_duck)
    monkeypatch.setattr(rfr, "DB", str(db))
    monkeypatch.setattr(rfr, "OUTDIR", str(tmp_path / "out"))
    monkeypatch.setattr(rfr, "env", lambda: keys)
    monkeypatch.setattr(rfr, "date", frozen_today)
    monkeypatch.setattr(rfr, "get_json", fake_get_json)
    monkeypatch.setattr(rfr, "post_json", fake_post)
    monkeypatch.setattr(rfr.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(rfr.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["resolve.py", "--gleif-limit", "7"])
    rfr.main()
    out = capsys.readouterr().out.replace(str(tmp_path), "<TMP>")
    con = sqlite3.connect(db)
    dump = "\n".join(con.iterdump())
    con.close()
    calls = repr([(c[0].replace(str(tmp_path), "<TMP>"), c[1]) for c in fake_duck.calls])
    return {"out": sha(out), "db": sha(dump), "duck": sha(calls)}


@pytest.mark.parametrize("name,keys", [("ch_key", {"DART_KEY": "d", "COMPANIES_HOUSE_KEY": "c"}), ("jp_key", {"GBIZINFO_TOKEN": "g"})])
def test_main_identical(name, keys, tmp_path, monkeypatch, capsys, frozen_today):
    got = _run(tmp_path, monkeypatch, capsys, frozen_today, keys)
    assert got == GOLDEN[name]
