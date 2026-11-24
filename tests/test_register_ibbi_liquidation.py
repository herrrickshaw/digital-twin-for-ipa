"""IBBI liquidation auction register: HTML parsing, parquet merge, company cross-match, layer 34 block."""
import json
import sqlite3
import sys
import time

import pytest

from conftest import copy_script, load_script

duckdb = pytest.importorskip("duckdb")


def row(pdf, debtor, price="1,500,000", an="Liquidation", assets="Plant & machinery", ncells=10, pdf_markup=None):
    cells = [an, "01-01-2026", debtor, "20-01-2026", "Some IP", pdf_markup or
             f'<a href=https://ibbi.gov.in/uploads/auction_notice_liquidation/{pdf}.pdf>notice</a>',
             price, assets, "15-01-2026", "<a href=d.pdf>details</a>"]
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells[:ncells]) + "</tr>"


def page(*rows):
    return "<html><table>" + "\n".join(rows) + "</table></html>"


@pytest.fixture
def mod(fake_repo):
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("register_ibbi_liquidation", fake_repo)
    return m, fake_repo


def test_parse_price(mod):
    m, _ = mod
    assert m.parse_price("1,500,000") == 1500000 and m.parse_price(" 42 ") == 42
    assert m.parse_price("n/a") is None and m.parse_price("") is None and m.parse_price(None) is None
    assert m.parse_price("1.5") is None and m.parse_price("-5") is None


def test_parse_rows(mod):
    m, _ = mod
    html = page(
        row("a", "Alpha <b>Steels</b>  Ltd", price="2,00,000"),
        row("b", "Beta", price="n/a", pdf_markup="see auction_notice_liquidation page"),
        row("short", "Gamma", ncells=8),                                     # < 9 cells -> skipped
        "<tr><td>x</td><td>no marker</td></tr>",                              # no auction_notice_liquidation
        row("c", "Delta", ncells=9),                                          # exactly 9 cells ok
    )
    rows = m.parse_rows(html)
    assert [r["corporate_debtor"] for r in rows] == ["Alpha Steels Ltd", "Beta", "Delta"]
    a = rows[0]
    assert a["notice_pdf"] == "https://ibbi.gov.in/uploads/auction_notice_liquidation/a.pdf"
    assert a["reserve_price_inr"] == 200000 and a["an_type"] == "Liquidation" and a["emd_last_date"] == "15-01-2026"
    assert a["insolvency_professional"] == "Some IP" and a["nature_of_assets"] == "Plant & machinery"
    assert rows[1]["notice_pdf"] == "see auction_notice_liquidation page" and rows[1]["reserve_price_inr"] is None


def test_scrape_paging_and_failure(mod, monkeypatch, capsys):
    m, _ = mod
    urls = []

    def get(url, timeout=40):
        urls.append(url)
        if url.endswith("page=3"):
            raise OSError("boom")
        if url.endswith("page=4"):
            return page()
        return page(row("p" + url[-1], "Debtor"))
    monkeypatch.setattr(m, "get", get)
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    out = m.scrape(range(1, 6))
    assert urls == [m.BASE, m.BASE + "?page=2", m.BASE + "?page=3"]        # page 1 has no ?page, failure stops
    assert len(out) == 2
    text = capsys.readouterr().out
    assert "page 1: 1 rows" in text and "page 3: FETCH FAIL OSError" in text
    urls.clear()
    assert m.scrape([4]) == [] and "page 4: 0 rows (end?)" in capsys.readouterr().out


def _db(root, names):
    con = sqlite3.connect(root / "data/companies.db")
    con.execute("create table companies(company_id integer primary key, name text)")
    con.executemany("insert into companies(name) values(?)", [(n,) for n in names])
    con.commit()
    con.close()
    (root / "layers/34_stressed_assets.json").write_text(json.dumps({"layer": 34}))


def test_main_end_to_end(mod, monkeypatch, capsys):
    m, root = mod
    _db(root, ["Alpha Steels Limited", "Beta Power Private Limited", "Unrelated Co"])
    pages = {
        1: page(row("n1", "ALPHA STEELS LIMITED (in liquidation)", price="9,000,000", assets="Land"),
                row("n2", "Gamma Textiles Ltd", price="500", assets="Land"),
                row("dup", "Zed Zed Industries", price="1")),
        2: page(row("n3", "Beta Power Pvt Ltd", price="7,000,000", assets="Plant"),
                row("dup", "Zed Zed Industries", price="1")),          # duplicate notice_pdf across pages
    }
    monkeypatch.setattr(m, "get", lambda url, timeout=40: pages[int(url[-1]) if "page=" in url else 1])
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    monkeypatch.setattr(sys, "argv", ["x", "--pages", "2"])
    m.main()
    out = capsys.readouterr().out
    assert "scraping 2 pages..." in out and "parsed 4 unique notices" in out
    layer = json.load(open(root / "layers/34_stressed_assets.json"))
    reg = layer["register"]
    assert layer["layer"] == 34                     # existing keys preserved
    assert reg["total_notices"] == 4 and reg["scraped_this_run"] == 4
    assert [t["reserve_price_inr"] for t in reg["top_by_reserve_price"]] == [9000000, 7000000, 500, 1]
    assert reg["asset_type_mix"]["Land"] == 2
    names = {t["company"] for t in reg["twin_company_matches"]}
    assert "Alpha Steels Limited" in names and "Unrelated Co" not in names
    assert all(t["quality"] in ("strong", "reviewed-promoted") for t in reg["twin_company_matches"])
    con = sqlite3.connect(root / "data/companies.db")
    assert con.execute("select count(*) from ibbi_auction_notices").fetchone()[0] == 4
    assert con.execute("select count(*) from ibbi_company_matches").fetchone()[0] >= 1
    con.close()
    assert (root / "data/registers/ibbi_liquidation.parquet").exists()
    assert "parquet total: 4 | twin matches:" in out and "Alpha Steels Limited <- CD:" in out


def test_main_merges_with_existing_parquet(mod, monkeypatch):
    m, root = mod
    _db(root, ["Alpha Steels Limited"])
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    monkeypatch.setattr(m, "get", lambda url, timeout=40: page(row("one", "Alpha Steels Limited")))
    monkeypatch.setattr(sys, "argv", ["x", "--pages", "1"])
    m.main()
    monkeypatch.setattr(m, "get", lambda url, timeout=40: page(row("two", "Other Debtor"), row("one", "Alpha Steels Limited")))
    m.main()
    reg = json.load(open(root / "layers/34_stressed_assets.json"))["register"]
    assert reg["total_notices"] == 2 and reg["scraped_this_run"] == 2          # union, deduped on the full row
    # a run with no new rows must keep the parquet intact (no overwrite with nothing)
    monkeypatch.setattr(m, "get", lambda url, timeout=40: page())
    m.main()
    reg = json.load(open(root / "layers/34_stressed_assets.json"))["register"]
    assert reg["total_notices"] == 2 and reg["scraped_this_run"] == 0


def test_main_all_flag_scrapes_481_pages(mod, monkeypatch, capsys):
    m, root = mod
    _db(root, ["X Co"])
    seen = []
    monkeypatch.setattr(m, "get", lambda url, timeout=40: (seen.append(url), page(row(f"u{len(seen)}", "D")))[1])
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    monkeypatch.setattr(sys, "argv", ["x", "--all"])
    m.main()
    assert len(seen) == 481 and "scraping ALL pages..." in capsys.readouterr().out


def test_main_first_page_empty_with_prior_parquet_absent(mod, monkeypatch):
    m, root = mod
    _db(root, [])
    monkeypatch.setattr(m, "get", lambda url, timeout=40: page())
    monkeypatch.setattr(sys, "argv", ["x"])
    with pytest.raises(duckdb.IOException):       # no parquet and nothing scraped -> reading the missing parquet fails
        m.main()
