"""collect_company_news: multi-source news collection, archive and tiered company matching (HTTP faked)."""
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


def _env(tmp_path, monkeypatch, creds):
    home = tmp_path / "home"
    p = home / ".config/market-secrets/credentials.env"
    p.parent.mkdir(parents=True)
    if creds is not None:
        p.write_text(creds)
    monkeypatch.setenv("HOME", str(home))


def make(fake_repo, tmp_path, monkeypatch, creds="", companies=(), scores=(), clearance=()):
    _env(tmp_path, monkeypatch, creds)
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("collect_company_news", fake_repo)
    con = sqlite3.connect(fake_repo / "data/companies.db")
    con.executescript("""create table companies(company_id integer primary key, name text, ticker text);
        create table lead_scores(company_id integer, score real);
        create table clearance_activity(company_id integer, visibility_verdict text);""")
    con.executemany("insert into companies values (?,?,?)", companies)
    con.executemany("insert into lead_scores values (?,?)", scores)
    con.executemany("insert into clearance_activity values (?,?)", clearance)
    con.commit()
    con.close()
    write_json(fake_repo / "layers/32_company_db.json", {"layer": 32})
    return m


def run(m, *argv):
    old = sys.argv
    sys.argv = ["x", *argv]
    try:
        m.main()
    finally:
        sys.argv = old


def test_load_keys_parsing(fake_repo, tmp_path, monkeypatch):
    m = make(fake_repo, tmp_path, monkeypatch, creds="# c\nA=1\nB = ignored\nC=\"quoted\"\nD='sq'\nE=x=y\n\nnoequals\n#F=2\n")
    k = m.load_keys()
    assert k["A"] == "1" and k["C"] == "quoted" and k["D"] == "sq" and k["E"] == "x=y"
    assert "F" not in k and "#F" not in k and "noequals" not in k
    import os
    os.unlink(tmp_path / "home/.config/market-secrets/credentials.env")
    assert m.load_keys() == {}


def test_budget(fake_repo, tmp_path, monkeypatch):
    m = make(fake_repo, tmp_path, monkeypatch)
    b = m.Budget(2)
    assert [b.take(), b.take(), b.take(), b.take()] == [True, True, False, False] and b.used == 2
    assert m.Budget(0).take() is False


def test_get_json(fake_repo, tmp_path, monkeypatch):
    m = make(fake_repo, tmp_path, monkeypatch)
    seen = {}
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: (
        seen.update(ua=req.headers, t=timeout), FakeResp(jsonobj={"a": 1}))[1])
    assert m.get_json("http://x") == {"a": 1} and seen["t"] == 25 and seen["ua"]["User-agent"].startswith("Mozilla")


def _router(responses, log):
    def get_json(url):
        log.append(url)
        for frag, resp in responses:
            if frag in url:
                if isinstance(resp, Exception):
                    raise resp
                return resp(url) if callable(resp) else resp
        raise AssertionError(f"unexpected url {url}")
    return get_json


def test_main_no_keys_only_matches_existing(fake_repo, tmp_path, monkeypatch, capsys):
    m = make(fake_repo, tmp_path, monkeypatch, creds="")
    monkeypatch.setattr(m, "get_json", lambda u: pytest.fail("no network without keys"))
    run(m)
    layer = json.load(open(fake_repo / "layers/32_company_db.json"))
    s = layer["news_collection"]
    assert s["sources_skipped_or_errors"] == ["newsapi: no key", "newsdata: no key"]
    assert s["api_calls_used"] == 0 and s["articles_total"] == 0 and s["new_articles"] == 0
    assert "exception hits: 0" in capsys.readouterr().out


def test_main_full_flow(fake_repo, tmp_path, monkeypatch, capsys):
    creds = "NEWSAPI_KEY=nk\nNEWSDATA_KEY=dk\nMARKETAUX_KEY=mk\nALPHAVANTAGE_KEY=ak\n"
    companies = [(1, "Acme Dynamics Limited", "ACME"), (2, "Zenith Quiet Industries", "ZQI.NS"),
                 (3, "Plain Corp", ""), (4, "Visible Works Ltd", "VIS")]
    scores = [(1, 90), (2, 50), (4, 10)]
    clearance = [(2, "QUIET"), (4, "ANNOUNCED"), (1, "PARTIALLY_VISIBLE")]
    m = make(fake_repo, tmp_path, monkeypatch, creds, companies, scores, clearance)
    log = []
    news = lambda url: {"articles": [{"title": "Acme Dynamics invests in India", "description": "plant",
                                      "url": "http://a/" + str(len(log)), "publishedAt": "t"}]}
    monkeypatch.setattr(m, "get_json", _router([
        ('newsapi.org/v2/everything?q=%22Zenith', {"articles": [{"title": "Zenith Quiet Industries raises capex",
                                                                  "description": None, "url": "http://z/1", "publishedAt": "t"}]}),
        ("newsapi.org", news),
        ("newsdata.io", {"results": [{"title": "FDI up", "description": "d", "link": "http://n/1", "pubDate": "p"}]}),
        ("marketaux", {"data": [{"title": "Acme Dynamics shares", "description": "x", "url": "http://m/1", "published_at": "p"}]}),
        ("alphavantage", {"feed": [{"title": "t", "summary": "Zenith Quiet Industries rated", "url": "http://av/1",
                                    "time_published": "p", "overall_sentiment_label": "Bullish"}]}),
    ], log))
    run(m)
    s = json.load(open(fake_repo / "layers/32_company_db.json"))["news_collection"]
    # 4 FDI queries + 2 newsdata + 1 marketaux batch (2 listed tickers -> 1 call) + 1 AV + 1 quiet probe = 9
    assert s["api_calls_used"] == 9
    assert s["calls_by_source"]["newsapi"] == 5 and s["calls_by_source"]["newsdata"] == 2
    assert s["calls_by_source"]["marketaux"] == 1 and s["calls_by_source"]["alphavantage"] == 1
    assert s["sources_skipped_or_errors"] == []
    # marketaux symbols: only companies with a ticker AND a lead score, best score first
    mx = [u for u in log if "marketaux" in u][0]
    assert urllib.parse.parse_qs(urllib.parse.urlparse(mx).query)["symbols"] == ["ACME,ZQI.NS,VIS"]
    av = [u for u in log if "alphavantage" in u][0]
    assert urllib.parse.parse_qs(urllib.parse.urlparse(av).query)["tickers"] == ["ACME,VIS"]      # US tickers only
    nd = [u for u in log if "newsdata" in u][0]
    assert "country=in" in nd and "category=business" in nd
    exc = {e["company"]: e for e in s["exception_news_hits"]}
    assert exc["Zenith Quiet Industries"]["verdict"] == "QUIET"
    assert exc["Acme Dynamics Limited"]["verdict"] == "PARTIALLY_VISIBLE"
    assert "Visible Works Ltd" not in exc
    arch = [json.loads(l) for l in (fake_repo / "state/news_articles.jsonl").read_text().splitlines()]
    assert len({a["url"] for a in arch}) == len(arch) == s["articles_total"]
    assert any(a["source"] == "alphavantage" and a["sentiment"] == "Bullish" for a in arch)
    con = sqlite3.connect(fake_repo / "data/companies.db")
    assert con.execute("select count(*) from news_company_matches").fetchone()[0] == s["match_rows_added"]
    con.close()
    out = capsys.readouterr().out
    assert "[QUIET] Zenith Quiet Industries <- " in out
    assert f"exception hits: {len(s['exception_news_hits'])}" in out and len(s["exception_news_hits"]) >= 2


def test_main_budget_and_error_isolation(fake_repo, tmp_path, monkeypatch):
    m = make(fake_repo, tmp_path, monkeypatch, "NEWSAPI_KEY=nk\nNEWSDATA_KEY=dk\n",
             [(1, "Quiet Co Ltd", "Q")], [(1, 1)], [(1, "QUIET")])
    log = []

    def get_json(url):
        log.append(url)
        if "newsdata" in url:
            raise OSError("down")
        return {"articles": []}
    monkeypatch.setattr(m, "get_json", get_json)
    run(m, "--max-calls", "3")
    s = json.load(open(fake_repo / "layers/32_company_db.json"))["news_collection"]
    assert s["api_calls_used"] == 3 and len(log) == 3          # budget stops the sweep
    run(m, "--max-calls", "6")
    s = json.load(open(fake_repo / "layers/32_company_db.json"))["news_collection"]
    assert any(e.startswith("newsdata FDI investment: OSError") for e in s["sources_skipped_or_errors"])
    assert any(e.startswith("newsdata stock market: OSError") for e in s["sources_skipped_or_errors"])


def test_dry_run_does_not_write_layer(fake_repo, tmp_path, monkeypatch, capsys):
    m = make(fake_repo, tmp_path, monkeypatch, "")
    before = (fake_repo / "layers/32_company_db.json").read_text()
    run(m, "--dry-run")
    assert (fake_repo / "layers/32_company_db.json").read_text() == before
    assert '"api_calls_used": 0' in capsys.readouterr().out


def test_archive_is_url_deduped_and_tolerates_bad_lines(fake_repo, tmp_path, monkeypatch):
    m = make(fake_repo, tmp_path, monkeypatch, "NEWSAPI_KEY=nk\n")
    arch = fake_repo / "state/news_articles.jsonl"
    arch.write_text(json.dumps({"url": "http://dup"}) + "\nnot json\n")
    monkeypatch.setattr(m, "get_json", lambda u: {"articles": [
        {"title": "a", "url": "http://dup"}, {"title": "b", "url": "http://new"}, {"title": "c", "url": None}]})
    run(m, "--max-calls", "1")
    urls = [json.loads(l).get("url") for l in arch.read_text().splitlines() if l.startswith("{")]
    assert urls.count("http://dup") == 1 and urls.count("http://new") == 1 and None not in urls[1:]


def test_matching_requires_word_boundaries(fake_repo, tmp_path, monkeypatch):
    m = make(fake_repo, tmp_path, monkeypatch, "NEWSAPI_KEY=nk\n",
             [(1, "Alpha Beta Limited", "")], [], [(1, "QUIET")])
    monkeypatch.setattr(m, "get_json", lambda u: {"articles": [
        {"title": "Alpha Betatron lab", "description": "", "url": "http://1"},     # not a boundary hit
        {"title": "News on alpha beta today", "description": None, "url": "http://2"}]})
    run(m, "--max-calls", "1")
    con = sqlite3.connect(fake_repo / "data/companies.db")
    rows = con.execute("select n.url, m.match_quality, m.company_visibility from news_company_matches m "
                       "join news_articles n using(art_id)").fetchall()
    con.close()
    assert rows == [("http://2", "strong", "QUIET")]
