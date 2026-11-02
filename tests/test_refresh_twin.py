"""refresh_twin.py with the network replaced by a fake fetcher and state/ redirected to tmp."""
import json

import pytest

import refresh_twin as rt


@pytest.fixture
def state(tmp_path, monkeypatch):
    monkeypatch.setattr(rt, "STATE", str(tmp_path))
    monkeypatch.setattr(rt, "TODAY", "2026-01-01")
    return tmp_path


def test_parse_latest_rbi_date_formats():
    assert rt.parse_latest_rbi_date("issue 12 Sep 2026 and 01/02/2025") == "12 Sep 2026"
    assert rt.parse_latest_rbi_date("dated Sep 5, 2026") == "Sep 5, 2026"
    assert rt.parse_latest_rbi_date("on 05/09/2026") == "05/09/2026"
    assert rt.parse_latest_rbi_date("nothing here") is None


def test_extract_unnati_notice():
    assert rt.extract_unnati_notice("x Important Notice: stopped.") == "Important Notice: stopped."
    assert rt.extract_unnati_notice("none") == "(no notice block found)"
    assert len(rt.extract_unnati_notice("Important Notice" + "a" * 5000)) == len("Important Notice") + 1200


def test_strip_tags():
    assert rt.strip_tags("<style>a</style><p>Hi &amp; <b>there</b></p><script>x()</script>") == "Hi & there"


def test_route_changes_only_reports_flips():
    prev = {"results": {"a": {"ok": True}, "b": {"ok": False}, "c": {"ok": True}}}
    now = {"a": {"ok": False, "http": "500"}, "b": {"ok": False, "http": "404"}, "d": {"ok": True, "http": "200"}}
    assert rt.route_changes(prev, now) == ["CHANGE route a: ok=True -> False (500)"]
    assert rt.route_changes(None, now) == []


def test_cmd_rbi_writes_snapshot_and_reports_change(state, capsys):
    rt.cmd_rbi(fetch=lambda url, timeout=0, insecure=False: ("200", "<p>01 Jan 2026</p>"))
    assert json.load(open(state / "rbi_2026-01-01.json")) == {"checked": "2026-01-01", "http": "200", "latest_wss": "01 Jan 2026"}
    (state / "rbi_2025-12-25.json").write_text(json.dumps({"latest_wss": "old"}))  # sorts before today's
    rt.cmd_rbi(fetch=lambda url, timeout=0, insecure=False: ("200", "<p>01 Jan 2026</p>"))
    assert "rbi: latest WSS issue = 01 Jan 2026" in capsys.readouterr().out


def test_cmd_routes_marks_down_portals(state, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rt, "ROOT", str(tmp_path))
    (tmp_path / "layers").mkdir()
    (tmp_path / "layers" / "15_directory.json").write_text(json.dumps(
        {"central": {"Up": {"url": "https://up.example"}}, "state": {"Down": {"url": "https://ditc.goa.gov.in/x"}}}))
    seen = {}

    def fake(url, timeout=0, insecure=False):
        seen[url] = insecure
        return ("200", "") if "up." in url else ("503", "")

    rt.cmd_routes(fetch=fake)
    snap = json.load(open(state / "routes_2026-01-01.json"))
    assert snap["down"] == ["Down"] and snap["results"]["Up"]["ok"] is True
    assert seen == {"https://up.example": False, "https://ditc.goa.gov.in/x": True}
    assert "routes: 2 checked, 1 down" in capsys.readouterr().out


def test_watchlist_script_order_is_stable():
    assert rt.WATCHLIST_SCRIPTS.index("build_company_db.py") < rt.WATCHLIST_SCRIPTS.index("enrich_company_db_ii_tickers.py")
    assert len(rt.WATCHLIST_SCRIPTS) == 16
