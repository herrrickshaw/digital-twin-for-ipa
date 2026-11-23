import json
import sqlite3

import pytest

from conftest import load_script


@pytest.fixture
def ii(fake_repo):
    return load_script("enrich_company_db_ii_tickers", fake_repo)


@pytest.mark.parametrize("raw,expected", [
    (None, ""),
    ("", ""),
    ("M/s. Tata Steel Ltd.", "tata steel"),
    ("m / s Foo Bar Pvt Ltd", "foo bar"),
    ("Siemens AG", "siemens"),
    ("Acme Holdings Inc", "acme"),
    ("Acme Holding", "acme"),
    ("A&B  (India) Co.", "a b india"),
    ("Hyundai Motor Company", "hyundai motor"),
    ("CAMPUS Limited", "campus"),  # word-boundary: 'co' inside 'campus' must survive
    ("ASEA Brown", "asea brown"),  # 'as' / 'sa' suffixes only as whole words
])
def test_norm(ii, raw, expected):
    assert ii.norm(raw) == expected


@pytest.mark.parametrize("name,frags", [
    ("", []),
    ("abc", []),                                      # single token too short
    ("tesla", []),                                    # 5 chars < 6
    ("toyota", [("toyota", "weak")]),                 # exactly 6
    ("india", []),                                    # stop token
    ("reliance", [("reliance", "weak")]),
    ("airbus", [("airbus", "reviewed-promoted")]),
    ("sandisk", [("sandisk", "reviewed-promoted")]),
    ("tata steel", [("tata steel", "strong"), ("tata steel", "strong")]),
    ("global tech", [("global tech", "strong")]),     # first token stop -> no 2-token frag
    ("a b", []),                                      # len < 6
    ("abc de", [("abc de", "strong"), ("abc de", "strong")]),
    ("galaxy dyestuff chemicals", [("galaxy dyestuff chemicals", "strong"), ("galaxy dyestuff", "strong")]),
])
def test_match_fragments(ii, name, frags):
    assert ii.match_fragments(name) == frags


def test_match_fragments_two_token_short_two_prefix(ii):
    # whole name >= 6 but the 2-token prefix (== whole name here) fine; 3 tokens with short prefix
    assert ii.match_fragments("a b cdefgh") == [("a b cdefgh", "strong")]  # 'a b' < 6 chars


PAGE = '''<html><div class="latest-update-items">
 <div class="latest-link"> <a href="/news/1" target="_x"> Acme <b>Corp</b> &amp; Co to invest
   Rs 100 cr </a></div>
 <div class="latest-link"><a href=" /news/2 ">  </a></div>
 <div class="latest-link"><a href="/news/3">Second item</a></div>
 <div class="blog-right"><div class="latest-link"><a href="/no">Outside block</a></div></div>
</div></html>'''


def test_scrape_ticker_parses_items_and_stops_at_block_end(ii, monkeypatch):
    monkeypatch.setattr(ii, "get", lambda url, timeout=30: PAGE)
    assert ii.scrape_ticker("u") == [
        ("Acme Corp & Co to invest Rs 100 cr", "/news/1"),
        ("Second item", "/news/3"),
    ]


def test_scrape_ticker_no_block_and_fetch_error(ii, monkeypatch):
    monkeypatch.setattr(ii, "get", lambda url, timeout=30: "<html></html>")
    assert ii.scrape_ticker("u") == []

    def bad(url, timeout=30):
        raise OSError("down")

    monkeypatch.setattr(ii, "get", bad)
    assert ii.scrape_ticker("u") == [("__FETCH_ERROR__", "OSError: down")]


def test_sector_urls_dedup_sorted_and_filtered(ii, monkeypatch):
    xml = ("<loc>https://www.investindia.gov.in/sector/b</loc>"
           "<loc>https://www.investindia.gov.in/sectors/a</loc>"
           "<loc>https://www.investindia.gov.in/sector/b</loc>"
           "<loc>https://www.investindia.gov.in/other/c</loc>")
    monkeypatch.setattr(ii, "get", lambda url, timeout=30: xml)
    assert ii.sector_urls() == [
        "https://www.investindia.gov.in/sector/b",
        "https://www.investindia.gov.in/sectors/a",
    ]


def test_get_sends_user_agent(ii, monkeypatch):
    seen = {}

    class R:
        def read(self):
            return b"ok\xff"

    def urlopen(req, timeout):
        seen["ua"] = req.headers["User-agent"]
        seen["t"] = timeout
        return R()

    monkeypatch.setattr(ii.urllib.request, "urlopen", urlopen)
    assert ii.get("http://x", timeout=5) == "ok�"
    assert seen == {"ua": ii.UA, "t": 5}


def _make_db(root):
    db = root / "data" / "companies.db"
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE companies(company_id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE clearance_activity(company_id INTEGER, visibility_verdict TEXT);
        INSERT INTO companies VALUES (1,'Acme Widgets Pvt Ltd'),(2,'Zenith Corp'),(3,'Pegatron Ltd'),
                                     (4,'Loud Co'),(5,'Quietone Industries');
        INSERT INTO clearance_activity VALUES (1,NULL),(1,'QUIET'),(3,'PARTIALLY_VISIBLE'),(4,'VISIBLE');
    """)
    con.commit()
    con.close()
    (root / "layers" / "32_company_db.json").write_text(json.dumps({"keep": 1}))
    return db


def test_main_matches_challenges_and_writes_layer(fake_repo, monkeypatch, capsys):
    ii = load_script("enrich_company_db_ii_tickers", fake_repo)
    _make_db(fake_repo)
    monkeypatch.setattr(ii, "sector_urls", lambda: ["https://x/sector/pharma", "https://x/sector/bad"])

    def scrape(url):
        if url.endswith("bad"):
            return [("__FETCH_ERROR__", "boom")]
        return [("Acme Widgets to open new plant", "/a"), ("Pegatron expands in Chennai", "/p"),
                ("Zenith Corporation news", "/z"), ("Loud announces", "/l"),
                ("Quietone Industries wins order", "/q")]

    monkeypatch.setattr(ii, "scrape_ticker", scrape)
    ii.main()
    out = capsys.readouterr().out
    layer = json.loads((fake_repo / "layers" / "32_company_db.json").read_text())
    v = layer["ii_ticker_validation"]
    assert layer["keep"] == 1
    assert v["sector_pages_scraped"] == 1 and v["fetch_errors"] == [{"url": "https://x/sector/bad", "error": "boom"}]
    assert v["announcements"] == 5
    ch = {c["company"]: c for c in v["exception_verdicts_challenged"]}
    assert set(ch) == {"Acme Widgets Pvt Ltd", "Pegatron Ltd"}
    assert ch["Acme Widgets Pvt Ltd"]["verdict_on_record"] == "QUIET"
    assert ch["Acme Widgets Pvt Ltd"]["matched_fragment"] == "acme widgets"
    assert ch["Pegatron Ltd"]["matched_fragment"] == "pegatron"  # reviewed-promoted counts as strong
    assert [w["company"] for w in v["weak_matches_for_review"]] == ["Zenith Corp"]
    con = sqlite3.connect(fake_repo / "data" / "companies.db")
    rows = con.execute(
        "SELECT c.name, m.match_quality FROM ii_company_matches m JOIN companies c USING(company_id)").fetchall()
    con.close()
    names = dict(rows)
    assert names == {"Acme Widgets Pvt Ltd": "strong", "Pegatron Ltd": "reviewed-promoted",
                     "Zenith Corp": "weak", "Quietone Industries": "strong"}
    assert "Loud Co" not in names  # 'loud' is only 4 chars
    assert v["companies_matched"] == 4 and v["match_rows"] == 4
    assert "CHALLENGED [QUIET] Acme Widgets Pvt Ltd <- pharma:" in out
    assert "2 sector pages" in out
    assert "exception verdicts challenged: 2" in out


def test_main_weak_match_listed_for_review(fake_repo, monkeypatch):
    ii = load_script("enrich_company_db_ii_tickers", fake_repo)
    _make_db(fake_repo)
    monkeypatch.setattr(ii, "sector_urls", lambda: ["https://x/sector/p"])
    monkeypatch.setattr(ii, "scrape_ticker", lambda u: [("Zenith hits a record", "/z")])
    ii.main()
    v = json.loads((fake_repo / "layers" / "32_company_db.json").read_text())["ii_ticker_validation"]
    assert v["weak_matches_for_review"] == [
        {"company": "Zenith Corp", "fragment": "zenith", "announcement": "Zenith hits a record"}]
    assert v["exception_verdicts_challenged"] == []


def test_main_blocked_keeps_previous_block(fake_repo, monkeypatch, capsys):
    ii = load_script("enrich_company_db_ii_tickers", fake_repo)
    _make_db(fake_repo)
    (fake_repo / "layers" / "32_company_db.json").write_text(
        json.dumps({"ii_ticker_validation": {"announcements": 7}}))

    def boom():
        raise OSError("403")

    monkeypatch.setattr(ii, "sector_urls", boom)
    ii.main()
    out = capsys.readouterr().out
    v = json.loads((fake_repo / "layers" / "32_company_db.json").read_text())["ii_ticker_validation"]
    assert v["announcements"] == 7
    assert v["refresh_status"].startswith("SKIPPED")
    assert v["last_refresh_attempt"]
    assert "sector_urls FAILED: OSError: 403" in out
    assert "exiting clean" in out


def test_main_blocked_empty_sitemap_without_prior_block(fake_repo, monkeypatch):
    ii = load_script("enrich_company_db_ii_tickers", fake_repo)
    _make_db(fake_repo)
    monkeypatch.setattr(ii, "sector_urls", lambda: [])
    ii.main()
    v = json.loads((fake_repo / "layers" / "32_company_db.json").read_text())["ii_ticker_validation"]
    assert set(v) == {"last_refresh_attempt", "refresh_status"}
