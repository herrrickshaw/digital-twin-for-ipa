"""layer 25 / 30 builders plus the Oslo NewsWeb and cninfo sweeps (all HTTP faked)."""
import json
import time
import urllib.request

import pytest
import requests

from _fakes import FakeResp
from conftest import load_script


# ----------------------------------------------------------------- layer 25
def _monitor(entries):
    return {"entries": [{"scheme": s, "ministry": "M", "tier": t, "monitor": {"window": w,
            "funds_allocated": "f", "last_verified": "v"}} for s, t, w in entries]}


@pytest.fixture
def l25(fake_repo, monkeypatch):
    m = load_script("build_layer25_linkages", fake_repo)
    payload = {"coverage": "37 states", "note": "vacant",
               "state_aggregates": [
                   {"state": "alpha", "available_area": 10, "parks": 1},
                   {"state": "beta", "available_area": 500, "parks": 5},
                   {"state": "gamma", "available_area": 0, "parks": 9},     # dropped (falsy)
                   {"state": "delta", "available_area": 70, "parks": 2},
               ]}
    seen = []
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda url, timeout=None: (seen.append((url, timeout)), FakeResp(jsonobj=payload))[1])
    return m, fake_repo, seen


def test_fetch_iilb_sorts_and_filters(l25):
    m, root, seen = l25
    cov, note, rows = m.fetch_iilb()
    assert cov == "37 states" and note == "vacant"
    assert [r["state"] for r in rows] == ["beta", "delta", "alpha"]
    url, timeout = seen[0]
    assert url.endswith("/data/iilb_industrial_land_2026-07-22.json") and timeout == 30


def test_fetch_iilb_accepts_dict_aggregates(l25, monkeypatch):
    m, root, seen = l25
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResp(jsonobj={
        "state_aggregates": {"a": {"state": "a", "available_area": 3, "parks": 1},
                             "b": {"state": "b", "available_area": 9, "parks": 1}}}))
    cov, note, rows = m.fetch_iilb()
    assert cov is None and [r["state"] for r in rows] == ["b", "a"]


@pytest.mark.parametrize("window,expected", [
    ("Oversubscribed -- open until", "CLOSED"),       # closed words win over 'open'
    ("STOPPED", "CLOSED"),
    ("Discontinued rolling", "CLOSED"),
    ("Open now", "OPEN"),
    ("operational", "OPEN"),
    ("Ongoing", "OPEN"),
    ("rolling", "OPEN"),
    ("tranches", "OPEN"),
    ("FCFS", "OPEN"),
    ("round-1", "OPEN"),
    ("closes 31 Dec 2026", "CLOSING-SOON"),
    ("Open; closes 31 Dec", "OPEN"),                  # open words checked before 'clos'
    ("not yet notified", "PENDING/OTHER"),
    ("", "PENDING/OTHER"),
    (None, "PENDING/OTHER"),
])
def test_open_incentives_status(l25, window, expected):
    m, root, _ = l25
    (root / "layers/17_scheme_monitor.json").write_text(json.dumps(_monitor([("S", "central", window)])))
    assert m.open_incentives()[0]["status"] == expected


def test_build_layer25(l25, capsys):
    m, root, _ = l25
    (root / "layers/17_scheme_monitor.json").write_text(json.dumps(_monitor([
        ("A", "central", "open"), ("B", "state", "open"), ("C", "central", "closes soon"),
        ("D", "central", "stopped"), ("E", "central", "tbd")])))
    m.build()
    out = json.load(open(root / "layers/25_land_incentive_linkages.json"))
    assert out["layer"] == 25
    assert [r["state"] for r in out["land_availability"]["top_states_by_vacant_developed_land"]] == [
        "beta", "delta", "alpha"]
    assert out["land_availability"]["top_states_by_vacant_developed_land"][0] == {
        "state": "beta", "available_vacant_ha": 500, "parks": 5}
    oi = out["open_incentives"]
    assert oi["open_or_closing_count"] == 3 and len(oi["windows"]) == 5
    li = out["linked_insight"]
    assert li["land_rich_states"] == ["Beta", "Delta", "Alpha"]
    assert li["open_central_windows"] == ["A", "C"]    # central only, OPEN + CLOSING-SOON
    assert "layer 25 written: 3 land states, 3 open/closing incentive windows" in capsys.readouterr().out


def test_build_layer25_caps_top_land_at_15(l25, monkeypatch):
    m, root, _ = l25
    rows = [{"state": f"s{i}", "available_area": i + 1, "parks": 1} for i in range(20)]
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: FakeResp(jsonobj={"state_aggregates": rows}))
    (root / "layers/17_scheme_monitor.json").write_text(json.dumps(_monitor([])))
    m.build()
    out = json.load(open(root / "layers/25_land_incentive_linkages.json"))
    assert len(out["land_availability"]["top_states_by_vacant_developed_land"]) == 15
    assert len(out["linked_insight"]["land_rich_states"]) == 6


# ----------------------------------------------------------------- layer 30
def _l30_net(monkeypatch, matrix, country):
    def fake(req, timeout=None):
        url = req.full_url
        assert req.headers.get("User-agent", "").startswith("Mozilla")
        if "import_dependency" in url:
            return FakeResp(jsonobj={"matrix": matrix})
        return FakeResp(jsonobj={"country_balances": country})
    monkeypatch.setattr(urllib.request, "urlopen", fake)


def test_layer30_build(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer30_trade_deficit", fake_repo)
    matrix = [
        {"hs": "85", "name": "Electrical", "value": "~$120.5 bn", "growth": "+9%", "coverage": "strong", "note": "n85"},
        {"hs": "84", "name": "Machinery", "value": "$60bn", "coverage": "partial", "note": "n84"},
        {"hs": "39", "name": "Plastics", "value": "n/a", "coverage": "gap", "note": "n39"},
        {"hs": "27", "name": "Energy", "value": "$150 bn", "coverage": "gap"},        # structural -> not a gap
        {"hs": "71", "name": "Gems", "coverage": "na"},                                 # process-trade
        {"hs": "99", "name": "Other", "value": "$1bn", "coverage": "strong"},          # strong -> not a gap
    ]
    country = [{"name": "China", "code": "CN", "balance": -112345.0},
               {"name": "Russia", "code": "RU", "balance": -50000},
               {"name": "UAE", "code": "AE", "balance": 12000}]
    _l30_net(monkeypatch, matrix, country)
    m.build()
    out = json.load(open(fake_repo / "layers/30_trade_deficit_map.json"))
    rows = {r["hs_chapter"]: r for r in out["import_dependency_matrix"]}
    assert rows["85"]["import_usd_bn"] == 120.5 and rows["85"]["twin_incentive_lane"].startswith("Semicon")
    assert rows["39"]["import_usd_bn"] is None and rows["39"]["twin_incentive_lane"] is None
    assert rows["27"]["substitution_type"] == "structural (crude/energy)"
    assert rows["71"]["substitution_type"] == "process-trade (import-to-re-export)"
    assert rows["99"]["substitution_type"] == "manufacturing-substitutable" and rows["99"]["twin_incentive_lane"] is None
    assert [g["hs"] for g in out["policy_gaps"]] == ["84", "39"]
    top = out["top_deficit_countries"]
    assert [c["code"] for c in top] == ["CN", "RU", "AE"]
    assert top[0]["balance_usd_bn"] == -112.3
    assert "top deficit country China ($-112.3bn)" in capsys.readouterr().out


def test_layer30_top_deficit_limit_8(fake_repo, monkeypatch):
    m = load_script("build_layer30_trade_deficit", fake_repo)
    country = [{"name": f"c{i}", "code": str(i), "balance": -i} for i in range(12)]
    _l30_net(monkeypatch, [{"hs": "85", "name": "E", "coverage": "gap"}], country)
    m.build()
    out = json.load(open(fake_repo / "layers/30_trade_deficit_map.json"))
    assert [c["code"] for c in out["top_deficit_countries"]] == [str(i) for i in range(11, 3, -1)]


# --------------------------------------------------------------------- oslo
@pytest.mark.parametrize("title,tier", [
    ("Divest India unit", "exit_or_divestment"),
    ("Sale of shares in India Ltd", "exit_or_divestment"),
    ("Company ceases operations in India", "exit_or_divestment"),
    ("Terminates India JV", "exit_or_divestment"),
    ("Withdrawal from India", "exit_or_divestment"),
    ("Entry into India market", "market_entry_or_investment"),
    ("New plant in India", "market_entry_or_investment"),
    ("IPO of India sub", "market_entry_or_investment"),
    ("Invests in India", "market_entry_or_investment"),
    ("Expansion in India", "market_entry_or_investment"),
    ("India Q3 results", "business_activity"),
    ("", "business_activity"),
    # exit pattern wins when both appear
    ("Sale of manufacturing unit in India", "exit_or_divestment"),
])
def test_oslo_classify(title, tier):
    m = load_script("build_oslo_newsweb_india_sweep", None)
    assert m.classify(title) == tier


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="EXIT_RE uses \\bdivest\\b so 'Divestment'/'divested' are not recognised as exits "
                          "(build_oslo_newsweb_india_sweep.py:36): a 'Divestment of ... subsidiary' title lands in "
                          "market_entry_or_investment")
def test_oslo_classify_divestment_word_forms():
    m = load_script("build_oslo_newsweb_india_sweep", None)
    assert m.classify("Divestment of Indian subsidiary") == "exit_or_divestment"


def test_oslo_main(fake_repo, monkeypatch, capsys):
    m = load_script("build_oslo_newsweb_india_sweep", fake_repo)
    calls = []
    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append((url, params, timeout))
        return FakeResp(jsonobj={"data": {"overflow": False, "messages": [
            {"issuerName": "A", "issuerSign": "A1", "title": "Expansion in India", "publishedTime": "t1",
             "category": [{"category_en": "Press"}], "messageId": 1},
            {"issuerName": "B", "title": "Sale of India unit", "messageId": 2},
            {"issuerName": "C", "title": None, "messageId": 3, "category": []},
        ]}})
    monkeypatch.setattr(requests, "get", fake_get)
    m.OUT = str(fake_repo / "layers/16_enrichment/oslo.json")
    m.main()
    assert calls[0][1]["messageTitle"] == "India" and calls[0][1]["fromDate"] == "2015-01-01"
    out = json.load(open(m.OUT))
    assert out["total_india_titles"] == 3
    assert [r["message_id"] for r in out["market_entry_or_investment"]] == [1]
    assert [r["message_id"] for r in out["exit_or_divestment"]] == [2]
    assert [r["message_id"] for r in out["business_activity"]] == [3]
    assert out["market_entry_or_investment"][0]["category"] == "Press"
    assert out["business_activity"][0]["category"] is None
    text = capsys.readouterr().out
    assert "total: 3 | market_entry/investment: 1 | business_activity: 1 | exit/divestment: 1" in text
    assert "ENTRY: A -- Expansion in India" in text


# ------------------------------------------------------------------- cninfo
def test_cninfo_sweep(fake_repo, monkeypatch, capsys):
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    calls = []

    def fake_post(url, headers=None, data=None, timeout=None):
        calls.append((data["searchkey"], data["pageNum"]))
        if data["searchkey"] == "印度设立":
            if data["pageNum"] == 1:
                return FakeResp(jsonobj={"totalAnnouncement": 45, "announcements": [
                    {"announcementId": "1", "announcementTitle": "关于在印度设立子公司的公告",
                     "secName": "公司A", "secCode": "000001", "adjunctUrl": "finalpage/x.PDF",
                     "announcementTime": 1},
                    {"announcementId": "2", "announcementTitle": "印度尼西亚设立", "secName": "X"},   # Indonesia
                    {"announcementId": "3", "announcementTitle": "印度设立工厂", "secName": "公司B"},
                ]})
            return FakeResp(jsonobj={"totalAnnouncement": 45, "announcements": [
                {"announcementId": "1", "announcementTitle": "印度重复", "secName": "公司A"},   # dup id
                {"announcementId": "4", "announcementTitle": "印度基地", "secName": "公司C"}]})
        if data["searchkey"] == "印度建厂":
            raise RuntimeError("boom")
        return FakeResp(jsonobj={"announcements": []})
    monkeypatch.setattr(requests, "post", fake_post)
    m = load_script("build_cninfo_india_sweep", fake_repo, argv=["--max-pages-per-phrase", "2"],
                    run_name="__main__")
    out = json.load(open(fake_repo / "layers/16_enrichment/cninfo_india_sweep.json"))
    assert out["count"] == 3 == len(out["china_pn3_watchlist"])
    assert out["excluded_indonesia_false_positives"] == 1
    first = out["china_pn3_watchlist"][0]
    assert first["pdf_url"] == "http://static.cninfo.com.cn/finalpage/x.PDF"
    assert out["china_pn3_watchlist"][1]["pdf_url"] is None
    assert first["matched_phrase"] == "印度设立"
    # page cap: 2 pages max for phrase 1 even though total says 45 (> 60?) -> page 2 then stop by cap
    assert calls.count(("印度设立", 1)) == 1 and ("印度设立", 2) in calls and ("印度设立", 3) not in calls
    # empty announcements breaks after first page; the error phrase also breaks
    assert calls.count(("印度建厂", 1)) == 1
    text = capsys.readouterr().out
    assert "印度建厂 page 1: ERROR RuntimeError: boom" in text
    assert "genuine India hits: 3 | excluded as Indonesia false-positives: 1" in text


def test_cninfo_stops_when_all_pages_read(fake_repo, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    calls = []
    def fake_post(url, headers=None, data=None, timeout=None):
        calls.append((data["searchkey"], data["pageNum"]))
        return FakeResp(jsonobj={"totalAnnouncement": 30, "announcements": [
            {"announcementId": data["searchkey"], "announcementTitle": "印度子公司", "secName": "n"}]})
    monkeypatch.setattr(requests, "post", fake_post)
    load_script("build_cninfo_india_sweep", fake_repo, run_name="__main__")
    # total == 30 -> page 1 * 30 >= 30 -> never goes to page 2 (default cap is 3)
    assert all(p == 1 for _, p in calls) and len(calls) == 8
