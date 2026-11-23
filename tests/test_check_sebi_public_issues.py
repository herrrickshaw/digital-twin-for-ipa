"""SEBI public-issues (DRHP) filer collector and company matcher."""
import json
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

import pytest

from _fakes import FakeResp, write_json
from conftest import copy_script, load_script


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)


@pytest.fixture
def mod(fake_repo):
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("check_sebi_public_issues", fake_repo)
    con = sqlite3.connect(fake_repo / "data/companies.db")
    con.executescript("""create table companies(company_id integer primary key, name text);
        create table clearance_activity(company_id integer, visibility_verdict text);""")
    con.execute("insert into companies values (1,'Aastha Spintex Limited')")
    con.execute("insert into companies values (2,'Zenith Quiet Industries')")
    con.execute("insert into companies values (3,'Unrelated Holdings')")
    con.execute("insert into clearance_activity values (1,'QUIET')")
    con.execute("insert into clearance_activity values (1,NULL)")
    con.commit()
    con.close()
    write_json(fake_repo / "layers/32_company_db.json", {"layer": 32})
    return m, fake_repo


def html(*items):
    return "<table>" + "".join(
        f"<tr><td>{d}</td><td><a href='{u}' target='_blank' title=\"{t}\">x</a></td></tr>" for d, u, t in items) + "</table>"


def test_parse_rows(mod):
    m, _ = mod
    rows = m.parse_rows(html(("Jan 06, 2025", "http://a/1", " Aastha Spintex Limited - DRHP "),
                             ("Dec 31, 2024", "http://a/2", "Other Ltd - Addendum")) + "<td>junk</td>")
    assert rows == [("2025-01-06", "Aastha Spintex Limited - DRHP", "http://a/1"),
                    ("2024-12-31", "Other Ltd - Addendum", "http://a/2")]
    assert m.parse_rows("") == []


@pytest.mark.parametrize("title,expected", [
    ("Aastha Spintex Limited - Addendum to DRHP", ("Aastha Spintex Limited", "Addendum to DRHP")),
    ("Solo Name", ("Solo Name", "")),
    ("A - B - C", ("A", "B - C")),
    ("  Padded  -  Doc ", ("Padded", "Doc")),
])
def test_filing_company(mod, title, expected):
    m, _ = mod
    assert m.filing_company(title) == expected


def test_fetch_page_posts_form(mod, monkeypatch):
    m, _ = mod
    seen = {}

    def urlopen(req, timeout=None):
        seen.update(data=req.data, headers=req.headers, timeout=timeout, url=req.full_url)
        return FakeResp(b"<html>ok</html>")
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    assert m.fetch_page(3) == "<html>ok</html>"
    form = urllib.parse.parse_qs(seen["data"].decode())
    assert form["nextValue"] == ["3"] and form["next"] == ["n"] and form["sid"] == ["3"] and form["ssid"] == ["15"]
    assert seen["headers"]["Content-type"] == "application/x-www-form-urlencoded" and seen["timeout"] == 30
    assert "public-issues.html" in seen["headers"]["Referer"]


def run(m, *argv):
    old = sys.argv
    sys.argv = ["x", *argv]
    try:
        m.main()
    finally:
        sys.argv = old


def test_main_pages_stop_conditions_and_matching(mod, monkeypatch, capsys):
    m, root = mod
    pages = {
        0: html(("Mar 01, 2025", "http://f/1", "Aastha Spintex Limited - DRHP"),
                ("Feb 20, 2025", "http://f/2", "Zenith Quiet Industries - RHP")),
        1: html(("Jan 10, 2025", "http://f/3", "Aastha Spintex Limited - Addendum"),
                ("Dec 15, 2024", "http://f/4", "Old Filer Limited - DRHP")),   # crosses --since -> stop after this page
        2: html(("Jan 01, 2020", "http://f/5", "Never Reached - DRHP")),
    }
    fetched = []

    def fetch(p):
        fetched.append(p)
        return pages[p]
    monkeypatch.setattr(m, "fetch_page", fetch)
    run(m, "--since", "2025-01-01")
    assert fetched == [0, 1]
    s = json.load(open(root / "layers/32_company_db.json"))["sebi_public_issues"]
    assert s["pages_fetched"] == 2 and s["since"] == "2025-01-01"
    assert s["filings_in_window"] == 3 and s["new_rows"] == 4
    names = [x["company"] for x in s["companies_moving_to_market"]]
    assert names.count("Aastha Spintex Limited") == 2 and "Unrelated Holdings" not in names
    first = s["companies_moving_to_market"][0]
    assert first["filed"] == "2025-03-01" and first["visibility"] == "QUIET" and first["quality"] == "strong"
    assert [x["filed"] for x in s["companies_moving_to_market"]] == sorted(
        (x["filed"] for x in s["companies_moving_to_market"]), reverse=True)
    out = capsys.readouterr().out
    assert "[strong] Aastha Spintex Limited  <- 2025-03-01: Aastha Spintex Limited - DRHP" in out
    assert "companies_moving_to_market" not in out.split("[strong]")[0]
    # idempotent: a second run inserts nothing new and matches nothing new
    fetched.clear()
    run(m, "--since", "2025-01-01")
    s = json.load(open(root / "layers/32_company_db.json"))["sebi_public_issues"]
    assert s["new_rows"] == 0 and s["match_rows"] == 0


def test_main_stops_on_error_and_empty_page(mod, monkeypatch, capsys):
    m, root = mod
    calls = []

    def fetch(p):
        calls.append(p)
        if p == 1:
            raise OSError("down")
        return html(("Mar 01, 2025", f"http://f/{p}", f"Co{p} Limited - DRHP"))
    monkeypatch.setattr(m, "fetch_page", fetch)
    run(m)
    assert calls == [0, 1] and "page 1 fetch failed: OSError" in capsys.readouterr().out
    s = json.load(open(root / "layers/32_company_db.json"))["sebi_public_issues"]
    assert s["pages_fetched"] == 1 and s["since"] == "2025-01-01"
    # empty page ends the crawl without counting a page
    monkeypatch.setattr(m, "fetch_page", lambda p: "<html></html>")
    run(m)
    assert json.load(open(root / "layers/32_company_db.json"))["sebi_public_issues"]["pages_fetched"] == 0


def test_main_max_pages_caps_crawl(mod, monkeypatch):
    m, root = mod
    calls = []

    def fetch(p):
        calls.append(p)
        return html(("Mar 01, 2025", f"http://f/{p}", f"Co{p} Limited - DRHP"))
    monkeypatch.setattr(m, "fetch_page", fetch)
    run(m, "--max-pages", "3")
    assert calls == [0, 1, 2]


def test_match_window_excludes_filings_before_since(mod, monkeypatch):
    m, root = mod
    monkeypatch.setattr(m, "fetch_page", lambda p: html(
        ("Mar 01, 2025", "http://f/1", "Zenith Quiet Industries - DRHP"),
        ("Jan 01, 2024", "http://f/2", "Aastha Spintex Limited - DRHP")) if p == 0 else "")
    run(m, "--since", "2025-01-01")
    s = json.load(open(root / "layers/32_company_db.json"))["sebi_public_issues"]
    assert [x["company"] for x in s["companies_moving_to_market"]] == ["Zenith Quiet Industries"]
    assert s["filings_in_window"] == 1 and s["new_rows"] == 2
