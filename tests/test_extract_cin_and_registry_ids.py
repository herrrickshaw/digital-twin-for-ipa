"""extract_cin_from_drhp (prospectus parsing) and resolve_foreign_registry_ids (LEI / national id lookup)."""
import io
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import types
import urllib.request
import zipfile

import pytest

from _fakes import FakeResp, completed, write_json
from conftest import load_script


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)


# ----------------------------------------------------------------- extract_cin
@pytest.fixture
def cin(fake_repo, monkeypatch, tmp_path):
    m = load_script("extract_cin_from_drhp", fake_repo)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    return m, fake_repo


def test_cin_regex(cin):
    m, _ = cin
    ok = "L12345MH2001PLC123456"
    assert m.CIN_RE.search(f"CIN: {ok}.").group(1) == ok
    assert m.CIN_RE.search("U99999GJ1999PTC000001").group(1) == "U99999GJ1999PTC000001"
    assert m.CIN_RE.search("X12345MH2001PLC123456") is None                # must start with L or U
    assert m.CIN_RE.search("L12345MH2001PLC12345") is None                 # six trailing digits


def test_find_pdf(cin, monkeypatch):
    m, _ = cin
    assert m.find_pdf("http://x/a.PDF") == "http://x/a.PDF"
    page = "<iframe src='x?file=https://www.sebi.gov.in/sebi_data/attachdocs/doc1.pdf&z=1'>"
    monkeypatch.setattr(m, "get", lambda u: page)
    assert m.find_pdf("http://x/page") == "https://www.sebi.gov.in/sebi_data/attachdocs/doc1.pdf"
    monkeypatch.setattr(m, "get", lambda u: '<a href="https://www.sebi.gov.in/sebi_data/attachdocs/doc2.pdf">')
    assert m.find_pdf("http://x/page") == "https://www.sebi.gov.in/sebi_data/attachdocs/doc2.pdf"
    monkeypatch.setattr(m, "get", lambda u: "<html>nothing</html>")
    assert m.find_pdf("http://x/page") is None


def test_get_binary_and_text(cin, monkeypatch):
    m, _ = cin
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResp("héllo".encode()))
    assert m.get("http://u") == "héllo" and m.get("http://u", binary=True) == "héllo".encode()


def _pdftotext(first, full):
    def run(cmd, capture_output=None, timeout=None):
        return completed(first if "-f" in cmd else full)
    return run


def test_extract_all_fields(cin, monkeypatch, tmp_path):
    m, _ = cin
    first = b"Cover page CIN L12345MH2001PLC123456 more"
    body = ("Fresh Issue of Equity Shares aggregating up to Rs. 1,250.50 cr. "
            "Offer for Sale of shares worth ₹ 300 million. "
            "OBJECTS OF THE ISSUE " + "word " * 40 + "end.")
    monkeypatch.setattr(subprocess, "run", _pdftotext(first, body.encode()))
    cin_, fresh, ofs, obj = m.extract(b"%PDF")
    assert cin_ == "L12345MH2001PLC123456"
    assert fresh == "1,250.50 cr" and ofs == "300 million"
    assert obj.startswith("word word") and len(obj) <= 600
    assert not list(tmp_path.glob("*.pdf"))                      # temp file removed


def test_extract_cin_falls_back_to_full_text_and_toc_skipped(cin, monkeypatch):
    m, _ = cin
    toc = "OBJECTS OF THE ISSUE " + "." * 250 + " page 5"
    real = "OBJECTS OF THE OFFER " + ("Funding capex and repayment of debt. " * 10)
    full = "U12345KA2010PTC654321 " + toc + " " + real
    monkeypatch.setattr(subprocess, "run", _pdftotext(b"no cin here", full.encode()))
    cin_, fresh, ofs, obj = m.extract(b"x")
    assert cin_ == "U12345KA2010PTC654321" and fresh is None and ofs is None
    assert obj.startswith("Funding capex") and 300 < len(obj) <= 600


def test_extract_nothing(cin, monkeypatch):
    m, _ = cin
    monkeypatch.setattr(subprocess, "run", _pdftotext(b"", b"short OBJECTS OF THE ISSUE tiny"))
    assert m.extract(b"x") == (None, None, None, "")


def _cin_db(root, with_matches=True):
    con = sqlite3.connect(root / "data/companies.db")
    con.executescript("""create table companies(company_id integer primary key, name text);
        create table sebi_filings(filing_id integer primary key, filed text, url text);
        create table sebi_company_matches(filing_id integer, company_id integer);""")
    con.executemany("insert into companies values (?,?)", [(1, "Alpha Ltd"), (2, "Beta Ltd"), (3, "Gamma Ltd")])
    con.executemany("insert into sebi_filings values (?,?,?)", [
        (1, "2025-01-01", "http://p/a1"), (2, "2025-02-01", "http://p/a2"),
        (3, "2025-03-01", "http://p/b1"), (4, "2025-03-02", "http://p/c1")])
    con.executemany("insert into sebi_company_matches values (?,?)", [(1, 1), (2, 1), (3, 2), (4, 3)])
    con.commit()
    con.close()
    write_json(root / "layers/32_company_db.json", {"layer": 32})


def run(m, *argv):
    old = sys.argv
    sys.argv = ["x", *argv]
    try:
        m.main()
    finally:
        sys.argv = old


def test_cin_main_flow(cin, monkeypatch, capsys):
    m, root = cin
    _cin_db(root)

    def find_pdf(u):
        return {"http://p/a1": None, "http://p/a2": "http://p/a2.pdf", "http://p/b1": None,
                "http://p/c1": "http://p/c1.pdf"}[u]
    monkeypatch.setattr(m, "find_pdf", find_pdf)

    def get(u, binary=False, timeout=90):
        if u.endswith("c1.pdf"):
            raise OSError("download failed " + "x" * 200)
        return b"%PDF"
    monkeypatch.setattr(m, "get", get)
    monkeypatch.setattr(m, "extract", lambda b: ("L12345MH2001PLC123456", "10 crore", None, "objects " * 50))
    run(m)
    layer = json.load(open(root / "layers/32_company_db.json"))["cin_extraction"]
    assert [r["company"] for r in layer["records"]] == ["Alpha Ltd"]
    assert layer["records"][0]["pdf"] == "http://p/a2.pdf" and len(layer["records"][0]["objects_excerpt"]) == 250
    errs = {e["company"]: e for e in layer["errors"]}
    assert errs["Beta Ltd"]["error"] == "no PDF link on any filing page" and errs["Beta Ltd"]["url"] == "http://p/b1"
    assert errs["Gamma Ltd"]["error"].startswith("OSError: download failed") 
    assert len(errs["Gamma Ltd"]["error"]) == len("OSError: ") + 80
    dump = json.load(open(root / "state/cin_records.json"))
    assert [d["company"] for d in dump] == ["Alpha Ltd"] and dump[0]["cin"] == "L12345MH2001PLC123456"
    out = capsys.readouterr().out
    assert "Alpha Ltd: CIN=L12345MH2001PLC123456 fresh=10 crore ofs=None" in out and "Gamma Ltd: FAILED OSError" in out
    assert "extracted 1, errors 2" in out
    # second run: Alpha has a CIN so it is skipped; --limit respected
    monkeypatch.setattr(m, "find_pdf", lambda u: pytest.fail("Alpha must be skipped") if "a" in u[-2:] else None)
    run(m, "--limit", "1")
    assert "extracted 0, errors 1" in capsys.readouterr().out


def test_cin_reloads_durable_records_by_name(cin, monkeypatch):
    m, root = cin
    _cin_db(root)
    write_json(root / "state/cin_records.json", [
        {"company": "Beta Ltd", "cin": "U00000AA0000AAA000000", "fresh_issue": None, "offer_for_sale": None,
         "objects_of_issue": "", "source_pdf": "p", "extracted": "2025-01-01"},
        {"company": "Vanished Co", "cin": "X", "fresh_issue": None, "offer_for_sale": None,
         "objects_of_issue": "", "source_pdf": "p", "extracted": "d"}])
    seen = []
    monkeypatch.setattr(m, "find_pdf", lambda u: (seen.append(u), None)[1])
    run(m)
    assert "http://p/b1" not in seen                              # Beta restored -> already extracted
    dump = json.load(open(root / "state/cin_records.json"))
    assert [d["company"] for d in dump] == ["Beta Ltd"]            # unknown company dropped on rewrite


# --------------------------------------------------------- resolve_foreign_ids
def _creds(tmp_path, monkeypatch, text):
    home = tmp_path / "home"
    p = home / ".config/market-secrets/credentials.env"
    p.parent.mkdir(parents=True)
    if text is not None:
        p.write_text(text)
    monkeypatch.setenv("HOME", str(home))


@pytest.fixture
def reg(fake_repo, tmp_path, monkeypatch):
    def make(creds=""):
        _creds(tmp_path, monkeypatch, creds)
        return load_script("resolve_foreign_registry_ids", fake_repo)
    return make, fake_repo


def test_env_parsing(reg):
    make, _ = reg
    m = make("# c\nA=1\nB=\"two\"\nC='three'\nD=<your-key>\nE=your-token\nF=\nG=x=y\nnoequals\n")
    assert m.env() == {"A": "1", "B": "two", "C": "three", "G": "x=y"}


def test_gleif(reg, monkeypatch):
    make, _ = reg
    m = make()
    seen = {}
    monkeypatch.setattr(m, "get_json", lambda url, ua=m.UA, timeout=25: (seen.update(url=url), {
        "data": [{"attributes": {"lei": "LEI123", "entity": {"legalName": {"name": "ACME PLC"}}}}]})[1])
    assert m.gleif("Acme & Co") == ("LEI123", "ACME PLC")
    assert "Acme%20%26%20Co" in seen["url"] and "page%5Bsize%5D=1" in seen["url"]
    monkeypatch.setattr(m, "get_json", lambda *a, **k: {"data": []})
    assert m.gleif("x") == (None, None)
    monkeypatch.setattr(m, "get_json", lambda *a, **k: {})
    assert m.gleif("x") == (None, None)


def test_get_and_post_json(reg, monkeypatch):
    make, _ = reg
    m = make()
    seen = {}
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: (
        seen.update(h=req.headers, d=req.data, t=timeout), FakeResp(jsonobj={"ok": 1}))[1])
    assert m.get_json("http://u", ua="custom-ua", timeout=7) == {"ok": 1}
    assert seen["h"]["User-agent"] == "custom-ua" and seen["t"] == 7
    assert m.post_json("http://u", {"a": 1}) == {"ok": 1}
    assert json.loads(seen["d"]) == {"a": 1} and seen["h"]["Content-type"] == "application/json" and seen["t"] == 25


class FakeDuck:
    copies = []

    def __init__(self):
        self.last = None

    def execute(self, sql, params=None):
        if "SELECT DISTINCT country" in sql:
            self.last = [("United States",), ("South Korea",)]
        elif sql.strip().startswith("COPY"):
            FakeDuck.copies.append((sql, params))
        return self

    def fetchall(self):
        return self.last


def _setup_ids(root, rows):
    con = sqlite3.connect(root / "data/companies.db")
    con.execute("create table companies(company_id integer primary key, name text, country text, ticker text)")
    con.executemany("insert into companies values (?,?,?,?)", rows)
    con.commit()
    con.close()


def test_main_resolution_paths(reg, monkeypatch, capsys):
    make, root = reg
    m = make("DART_KEY=testdart\n")
    _setup_ids(root, [
        (1, "Apple Inc", "United States", "AAPL"),
        (2, "Samsung", "South Korea", "A005930 (KOSE 005930)"),
        (3, "Nestle", "Switzerland", None),
        (4, "Danone", "France", None),
        (5, "Barclays", "United Kingdom", None),
        (6, "Sony", "Japan", None),
        (7, "Indian Co", "India", None),
        (8, "Nowhere", "Narnia", None),
        (9, "Blank", "", None),
        (10, "NoTicker US", "United States", None),
    ])
    dart_xml = ("<corp_code>00126380</corp_code><corp_name>S</corp_name><stock_code>005930</stock_code>"
                "<corp_code>99999999</corp_code><corp_name>X</corp_name><stock_code> </stock_code>")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("CORPCODE.xml", dart_xml)

    def get_json(url, ua=None, timeout=25):
        if "company_tickers" in url:
            assert ua == m.EDGAR_UA
            return {"0": {"ticker": "aapl", "cik_str": 320193}}
        if "gleif" in url:
            if "Narnia" in url or "Nowhere" in url:
                raise RuntimeError("gleif down")
            if "Sony" in url:
                return {"data": []}
            return {"data": [{"attributes": {"lei": "LEI-" + url[-30:-20], "entity": {"legalName": {"name": "L"}}}}]}
        if "recherche-entreprises" in url:
            return {"results": [{"siren": "552032534"}]}
        raise AssertionError(url)
    monkeypatch.setattr(m, "get_json", get_json)
    monkeypatch.setattr(m, "post_json", lambda url, body, timeout=25: {"list": [{"uidFormatted": "CHE-1"}]}
                        if body["name"] == "Nestle" else {"list": []})
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResp(buf.getvalue())
                        if "corpCode" in req.full_url else (_ for _ in ()).throw(AssertionError(req.full_url)))
    FakeDuck.copies = []
    monkeypatch.setitem(sys.modules, "duckdb", types.SimpleNamespace(connect=lambda: FakeDuck()))
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    con = sqlite3.connect(root / "data/companies.db")
    rows = {r[1]: r for r in con.execute("select * from registry_ids")}
    con.close()
    assert "Indian Co" not in rows and "Blank" not in rows           # India and empty country excluded
    assert rows["Apple Inc"][6:10] == ("0000320193", "CIK", "SEC EDGAR", "resolved")
    assert rows["Samsung"][6:10] == ("00126380", "DART corp_code", "DART", "resolved")
    assert rows["Nestle"][6:10] == ("CHE-1", "UID", "Zefix", "resolved")
    assert rows["Danone"][6:10] == ("552032534", "SIREN", "recherche-entreprises", "resolved")
    assert rows["Barclays"][9] == "lei_only" and "COMPANIES_HOUSE_KEY" in rows["Barclays"][8]
    assert rows["Sony"][9] == "pending_key" and rows["Sony"][4] is None and "GBIZINFO_TOKEN" in rows["Sony"][8]
    assert rows["Nowhere"][9] == "unresolved"
    assert rows["NoTicker US"][9] == "lei_only" and rows["NoTicker US"][6] is None
    out = capsys.readouterr().out
    assert "8 foreign companies" in out and "EDGAR ticker map: 1" in out and "DART stock->corp map: 1" in out
    assert "gleif calls: 7" in out and "wrote 2 parquets" in out
    paths = [c[0] for c in FakeDuck.copies]
    assert any("United_States.parquet" in p for p in paths) and any("South_Korea.parquet" in p for p in paths)
    assert [c[1] for c in FakeDuck.copies] == [["United States"], ["South Korea"]]


def test_main_gleif_limit_and_failed_maps(reg, monkeypatch, capsys):
    make, root = reg
    m = make("")
    _setup_ids(root, [(i, f"Co{i}", "Germany", None) for i in range(1, 6)])
    calls = []

    def get_json(url, ua=None, timeout=25):
        if "company_tickers" in url:
            raise OSError("edgar down")
        calls.append(url)
        return {"data": [{"attributes": {"lei": "L", "entity": {"legalName": {"name": "n"}}}}]}
    monkeypatch.setattr(m, "get_json", get_json)
    monkeypatch.setitem(sys.modules, "duckdb", types.SimpleNamespace(connect=lambda: FakeDuck()))
    monkeypatch.setattr(sys, "argv", ["x", "--gleif-limit", "2"])
    m.main()
    assert len(calls) == 2
    con = sqlite3.connect(root / "data/companies.db")
    st = sorted(r[0] for r in con.execute("select status from registry_ids order by company_id"))
    con.close()
    assert st == ["lei_only", "lei_only", "unresolved", "unresolved", "unresolved"]
    out = capsys.readouterr().out
    assert "EDGAR map failed: OSError" in out and "DART stock->corp map" not in out


def test_main_uk_japan_with_keys(reg, monkeypatch):
    make, root = reg
    m = make("COMPANIES_HOUSE_KEY=chtest\nGBIZINFO_TOKEN=gbtest\n")
    _setup_ids(root, [(1, "Barclays", "United Kingdom", None), (2, "Sony", "Japan", None), (3, "Empty UK", "United Kingdom", None)])
    monkeypatch.setattr(m, "get_json", lambda url, ua=None, timeout=25: (_ for _ in ()).throw(OSError("n/a")) if "company_tickers" in url
                        else {"data": []})
    seen = []

    def urlopen(req, timeout=None):
        seen.append((req.full_url, dict(req.headers)))
        if "company-information" in req.full_url:
            return FakeResp(jsonobj={"items": [{"company_number": "00048839"}] if "Barclays" in req.full_url else []})
        return FakeResp(jsonobj={"hojin-infos": [{"corporate_number": "7010001008844"}]})
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    monkeypatch.setitem(sys.modules, "duckdb", types.SimpleNamespace(connect=lambda: FakeDuck()))
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    con = sqlite3.connect(root / "data/companies.db")
    rows = {r[1]: r for r in con.execute("select * from registry_ids")}
    con.close()
    assert rows["Barclays"][6:10] == ("00048839", "CRN", "Companies House", "resolved")
    assert rows["Sony"][6:10] == ("7010001008844", "法人番号", "gBizINFO", "resolved")
    assert rows["Empty UK"][9] == "unresolved"
    auth = [h for u, h in seen if "company-information" in u][0]["Authorization"]
    import base64
    assert base64.b64decode(auth.split()[1]).decode() == "chtest:"
    assert [h for u, h in seen if "gbiz" in u][0]["X-hojininfo-api-token"] == "gbtest"
