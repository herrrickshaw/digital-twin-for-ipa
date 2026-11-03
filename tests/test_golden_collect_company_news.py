"""Characterisation of collect_company_news.main with a stubbed HTTP layer and a synthetic companies.db."""
import json
import sqlite3
import sys

import collect_company_news as ccn
from conftest import sha

GOLDEN = {"stdout": "1fd685c637727ea41b2046ba6f7a477dcbc59f40dc383436ad22a74e49fda2f7", "layer": "6df2d9c749f9c5441e6420c91475710b24a3f33b8c5d0f5ce56b8b0f1d9b01c8", "db": "2abc8932e4db2d4f5f3bf1595e7f83e1b466b3ff6b37d1887cb4964a862893c6", "archive": "b8cb5e2bcc232e84232c03d5291f387556a53f050246bd7d0c8dd0b222fa3725"}


def _fake_get_json(url):
    if "newsapi.org" in url:
        return {"articles": [
            {"title": "Acme Holdings invests in new plant", "description": "FDI", "url": "http://n/1" + str(len(url) % 7), "publishedAt": "2026-01-01"},
            {"title": "Quiet Metals expands", "description": "greenfield", "url": "http://n/q" + str(len(url) % 5), "publishedAt": "2026-01-02"}]}
    if "newsdata.io" in url:
        return {"results": [{"title": "Stock market rallies", "description": "d", "link": "http://d/1", "pubDate": "2026-01-03"}]}
    if "marketaux" in url:
        return {"data": [{"title": "Acme Holdings earnings", "description": "", "url": "http://m/" + str(len(url)), "published_at": "2026-01-04"}]}
    if "alphavantage" in url:
        return {"feed": [{"title": "Zed Corp outlook", "summary": "s", "url": "http://a/1", "time_published": "t", "overall_sentiment_label": "Bullish"}]}
    raise OSError("unexpected " + url)


def _make_db(path):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE companies(company_id INTEGER PRIMARY KEY, name TEXT, ticker TEXT);
    CREATE TABLE lead_scores(company_id INTEGER, score REAL);
    CREATE TABLE clearance_activity(company_id INTEGER, visibility_verdict TEXT);
    INSERT INTO companies VALUES (1,'Acme Holdings Ltd','ACM'),(2,'Quiet Metals Pvt Ltd',NULL),(3,'Zed Corp','ZED'),(4,'Other Co','OTH.NS');
    INSERT INTO lead_scores VALUES (1,5.0),(3,4.0),(4,1.0);
    INSERT INTO clearance_activity VALUES (2,'QUIET'),(1,'PARTIALLY_VISIBLE');
    """)
    con.commit()
    con.close()


def test_main_is_behaviour_identical(tmp_path, monkeypatch, capsys, frozen_today):
    (tmp_path / "data").mkdir()
    (tmp_path / "layers").mkdir()
    (tmp_path / "state").mkdir()
    db = tmp_path / "data" / "companies.db"
    _make_db(db)
    layer = tmp_path / "layers" / "32_company_db.json"
    layer.write_text(json.dumps({"existing": 1}))
    (tmp_path / "state" / "news_articles.jsonl").write_text(json.dumps({"url": "http://d/1"}) + "\n")
    monkeypatch.setattr(ccn, "DB", str(db))
    monkeypatch.setattr(ccn, "LAYER", str(layer))
    monkeypatch.setattr(ccn, "ROOT", str(tmp_path))
    monkeypatch.setattr(ccn, "load_keys", lambda: {"NEWSAPI_KEY": "k1", "NEWSDATA_KEY": "k2", "MARKETAUX_KEY": "k3", "ALPHAVANTAGE_KEY": "k4"})
    monkeypatch.setattr(ccn, "get_json", _fake_get_json)
    monkeypatch.setattr(ccn.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["collect_company_news.py", "--max-calls", "9"])
    ccn.main()
    out = capsys.readouterr().out
    con = sqlite3.connect(db)
    dump = "\n".join(con.iterdump())
    con.close()
    got = {"stdout": sha(out), "layer": sha(layer.read_bytes()), "db": sha(dump),
           "archive": sha((tmp_path / "state" / "news_articles.jsonl").read_bytes())}
    assert got == GOLDEN, got
