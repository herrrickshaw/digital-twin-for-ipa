"""NewsAPI country / sector FDI sweeps matched against stock rosters (all HTTP faked)."""
import json
import sys
import time
import urllib.request

import pytest
import requests

from _fakes import FakeResp
from conftest import copy_script, load_script


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)


def _home(tmp_path, monkeypatch, key_line="NEWSAPI_KEY=testvalue\n"):
    home = tmp_path / "home"
    cred = home / ".config/market-secrets/credentials.env"
    cred.parent.mkdir(parents=True)
    if key_line is not None:
        cred.write_text(key_line)
    univ = home / "repos/global-stock-screener/data/global_universe"
    univ.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    return home, univ


def _roster(univ, name, rows):
    (univ / name).write_text("name,yf_ticker,exchange\n" + "".join(f"{n},{t},{e}\n" for n, t, e in rows),
                             encoding="utf-8")


def _load(name, root, tmp_path, monkeypatch, key_line="NEWSAPI_KEY=testvalue\n"):
    home, univ = _home(tmp_path, monkeypatch, key_line)
    copy_script(root, "enrich_company_db_ii_tickers")
    return load_script(name, root), univ


# ----------------------------------------------------------- country sweep
def test_country_load_key_and_roster(fake_repo, tmp_path, monkeypatch):
    m, univ = _load("build_country_fdi_news_sweep", fake_repo, tmp_path, monkeypatch)
    assert m.load_key() == "testvalue"
    for bad in ("NEWSAPI_KEY=<k>\n", "NEWSAPI_KEY=Your-key\n", "NEWSAPI_KEY=\n", "X=1\n"):
        (tmp_path / "home/.config/market-secrets/credentials.env").write_text(bad)
        assert m.load_key() is None
    # roster: missing file -> []
    assert m.load_roster("Switzerland") == []
    _roster(univ, "CH.csv", [("Alpha AG", "ALP.SW", "SIX")])
    assert m.load_roster("Switzerland") == [{"name": "Alpha AG", "ticker": "ALP.SW", "exchange": "SIX"}]
    _roster(univ, "EU.csv", [("Ams Co", "A.AS", "Euronext Amsterdam"), ("Par Co", "P.PA", "Euronext Paris"),
                             ("Ams2", "B.AS", "Euronext Amsterdam")])
    assert [r["ticker"] for r in m.load_roster("Netherlands")] == ["A.AS", "B.AS"]
    assert [r["ticker"] for r in m.load_roster("France")] == ["P.PA"]
    assert m.load_roster("Italy") == []


def test_country_load_leads_tickers(fake_repo, tmp_path, monkeypatch):
    m, _ = _load("build_country_fdi_news_sweep", fake_repo, tmp_path, monkeypatch)
    assert m.load_leads_tickers() == set()
    (fake_repo / "layers/16_leads.json").write_text(json.dumps(
        {"leads": [{"ticker": "A"}, {"ticker": ""}, {}, {"ticker": "B"}]}))
    assert m.load_leads_tickers() == {"A", "B"}


def test_country_get_json_sends_ua(fake_repo, tmp_path, monkeypatch):
    m, _ = _load("build_country_fdi_news_sweep", fake_repo, tmp_path, monkeypatch)
    seen = []
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda req, timeout=None: (seen.append((req.full_url, req.headers, timeout)),
                                                   FakeResp(jsonobj={"a": 1}))[1])
    assert m.get_json("http://x/y") == {"a": 1}
    assert seen[0][1]["User-agent"].startswith("Mozilla") and seen[0][2] == 25


def _country_main(m, argv):
    monkeypatch_argv = ["x"] + argv
    old = sys.argv
    sys.argv = monkeypatch_argv
    try:
        m.main()
    finally:
        sys.argv = old


def test_country_main_matches_and_calls_cap(fake_repo, tmp_path, monkeypatch, capsys):
    m, univ = _load("build_country_fdi_news_sweep", fake_repo, tmp_path, monkeypatch)
    _roster(univ, "CH.csv", [("Zurich Dynamics Systems", "ZDS.SW", "SIX"),   # strong
                             ("Verylongname", "VLN.SW", "SIX"),                # weak (single token >= 6)
                             ("Peoples", "PPL.SW", "SIX")])
    (fake_repo / "layers/16_leads.json").write_text(json.dumps({"leads": [{"ticker": "VLN.SW"}]}))
    queries = []

    def get_json(url):
        queries.append(url)
        if "Sweden" in url:
            raise RuntimeError("quota")
        return {"articles": [
            {"title": "Zurich Dynamics Systems to invest in India", "description": None,
             "url": "u1", "publishedAt": "2026-01-01"},
            {"title": "Verylongname eyes India", "description": "d", "url": "u2", "publishedAt": "2026-01-02"},
            {"title": "the peoples said", "description": ""},
            {"title": "verylongnames are not a word-boundary hit", "description": ""},
        ]}
    monkeypatch.setattr(m, "get_json", get_json)
    _country_main(m, ["--max-calls", "2"])
    out = json.load(open(m.OUT))
    assert out["calls_used"] == 2 and len(queries) == 3      # Switzerland ok, Sweden error (uncounted), Denmark ok
    ch = out["countries"]["Switzerland"]
    assert ch["roster_size"] == 3 and ch["articles_fetched"] == 4 and ch["roster_source"] == "CH.csv"
    byco = {x["company"]: x for x in ch["matches"]}
    assert byco["Zurich Dynamics Systems"]["match_quality"] == "strong"
    assert byco["Zurich Dynamics Systems"]["already_in_twin_leads"] is False
    assert byco["Verylongname"]["already_in_twin_leads"] is True
    assert [x["company"] for x in ch["matches"]].count("Verylongname") == 1
    assert byco["Peoples"]["match_quality"] == "weak"          # whole-name single token is weak only
    assert [n["company"] for n in out["new_leads_strong_match"]] == ["Zurich Dynamics Systems"]
    assert "error" in out["countries"]["Sweden"] and out["countries"]["Sweden"]["error"] == "RuntimeError: quota"
    # after 2 calls the remaining economies are not queried
    assert out["countries"]["Canada"]["articles_fetched"] == 0
    arch = (fake_repo / "state/news_articles.jsonl").read_text().splitlines()
    assert len(arch) == 8 and json.loads(arch[0])["source"] == "newsapi_country_sweep"
    assert json.loads(arch[0])["collected"] == out["built"]
    text = capsys.readouterr().out
    assert "calls used: 2/2 | NEW strong-match leads not in twin: 1" in text
    assert "NEW-LEAD: Zurich Dynamics Systems (ZDS.SW, SIX) -- Zurich Dynamics Systems to invest in India" in text
    assert "Sweden" in text and "ERROR:RuntimeError: quota" in text


def test_country_main_dry_run_and_missing_key(fake_repo, tmp_path, monkeypatch, capsys):
    m, univ = _load("build_country_fdi_news_sweep", fake_repo, tmp_path, monkeypatch, key_line=None)
    with pytest.raises(SystemExit, match="NEWSAPI_KEY missing"):
        _country_main(m, [])
    monkeypatch.setattr(m, "get_json", lambda u: pytest.fail("no network in dry run"))
    _country_main(m, ["--dry-run"])
    out = json.load(open(m.OUT))
    assert out["calls_used"] == 0 and len(out["countries"]) == 12
    assert "calls used: 0/15" in capsys.readouterr().out


def test_country_no_archive_when_state_dir_absent(fake_repo, tmp_path, monkeypatch):
    m, univ = _load("build_country_fdi_news_sweep", fake_repo, tmp_path, monkeypatch)
    import shutil
    shutil.rmtree(fake_repo / "state")
    monkeypatch.setattr(m, "get_json", lambda u: {"articles": [{"title": "t"}]})
    _country_main(m, ["--max-calls", "1"])
    assert not (fake_repo / "state").exists()


# ------------------------------------------------------------ sector sweep
def test_sector_load_key_and_rosters(fake_repo, tmp_path, monkeypatch):
    m, univ = _load("build_sector_news_sweep", fake_repo, tmp_path, monkeypatch)
    assert m.load_key() == "testvalue"
    cred = tmp_path / "home/.config/market-secrets/credentials.env"
    for bad in ("NEWSAPI_KEY=<x>\n", "NEWSAPI_KEY=your\n", "NEWSAPI_KEY=\n"):
        cred.write_text(bad)
        with pytest.raises(SystemExit, match="NEWSAPI_KEY missing"):
            m.load_key()
    _roster(univ, "JP.csv", [("Tokyo Works", "1.T", "TSE")])
    _roster(univ, "US.csv", [("Acme", "A", "NYSE"), ("Beta", "B", "NYSE")])
    _roster(univ, "IN.csv", [("Indian Co", "I", "NSE")])        # not in ROSTER_COUNTRIES
    r = m.load_all_rosters()
    assert set(r) == {"JP", "US"} and len(r["US"]) == 2 and r["JP"][0]["country"] == "JP"
    assert "IN" not in m.ROSTER_COUNTRIES


@pytest.mark.parametrize("text,ok", [
    ("will invest heavily", True), ("Expansion plans", True), ("new plant", True), ("new FACILITY", True),
    ("manufacturing hub", True), ("established unit", True), ("a subsidiary", True),
    ("joint venture", True), ("new office", False), ("nothing here", False),
    ("reinvestment", False),          # \binvest\w* needs a word boundary at start
])
def test_sector_intent_keywords(fake_repo, tmp_path, monkeypatch, text, ok):
    m, _ = _load("build_sector_news_sweep", fake_repo, tmp_path, monkeypatch)
    assert bool(m.INTENT_KEYWORDS.search(text)) is ok


def test_sector_get_json(fake_repo, tmp_path, monkeypatch):
    m, _ = _load("build_sector_news_sweep", fake_repo, tmp_path, monkeypatch)
    monkeypatch.setattr(requests, "get", lambda url, headers=None, timeout=None: FakeResp(jsonobj={"k": 1}))
    assert m.get_json("u") == {"k": 1}
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(b"", status=429))
    with pytest.raises(requests.HTTPError):
        m.get_json("u")


def test_sector_main(fake_repo, tmp_path, monkeypatch, capsys):
    m, univ = _load("build_sector_news_sweep", fake_repo, tmp_path, monkeypatch)
    _roster(univ, "JP.csv", [("Tokyo Works Ltd", "1.T", "TSE")])
    _roster(univ, "DE.csv", [("Berlin Solar Systems", "BSS.DE", "XETRA")])
    calls = []

    def get_json(url):
        calls.append(url)
        if len(calls) == 2:
            raise ValueError("rate")
        return {"articles": [
            {"title": "Tokyo Works to invest in India", "description": "", "url": "u1", "publishedAt": "p1"},
            {"title": "Tokyo Works new logo", "description": "no intent"},   # excluded: no intent keyword
            {"title": "Berlin Solar Systems expands", "description": None, "url": "u2"},
        ]}
    monkeypatch.setattr(m, "get_json", get_json)
    monkeypatch.setattr(sys, "argv", ["x", "--max-calls", "3"])
    m.main()
    out = json.load(open(m.OUT))
    assert out["calls_used"] == 3 and len(calls) == 4        # the failed call is not counted
    secs = list(out["sectors"])
    assert secs == list(m.SECTOR_QUERIES)[:4]
    first = out["sectors"][secs[0]]
    assert first["articles_fetched"] == 3 and first["excluded_no_intent"] == 1
    assert {x["company"] for x in first["matches"]} == {"Tokyo Works Ltd", "Berlin Solar Systems"}
    assert {x["country"] for x in first["matches"]} == {"JP", "DE"}
    assert out["sectors"][secs[1]]["error"] == "ValueError: rate" and out["sectors"][secs[1]]["matches"] == []
    assert len(out["strong_matches_all_sectors"]) == 6 and len(first["matches"]) == 2
    arch = (fake_repo / "state/news_articles.jsonl").read_text().splitlines()
    assert len(arch) == 6 and json.loads(arch[0])["query"].startswith(f"[{secs[0]}] ")
    text = capsys.readouterr().out
    assert "loaded 2 companies across 2 country rosters" in text
    assert f"[{secs[1]}] articles=0 matches=0 ERROR:ValueError: rate" in text
    assert "Tokyo Works Ltd (1.T, JP) [strong] -- Tokyo Works to invest in India" in text
    assert "calls used: 3 | strong matches across all sectors: 6" in text


def test_sector_max_calls_zero_stops_immediately(fake_repo, tmp_path, monkeypatch):
    m, univ = _load("build_sector_news_sweep", fake_repo, tmp_path, monkeypatch)
    monkeypatch.setattr(m, "get_json", lambda u: pytest.fail("no call expected"))
    monkeypatch.setattr(sys, "argv", ["x", "--max-calls", "0"])
    m.main()
    assert json.load(open(m.OUT))["sectors"] == {}
