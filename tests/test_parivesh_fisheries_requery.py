"""PARIVESH fisheries re-query: dedupe, term / harbour classification, layer 33 write-back."""
import json
import sys
import time
import urllib.parse
import urllib.request

import pytest

from _fakes import FakeResp, write_json
from conftest import load_script


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)


@pytest.fixture
def mod(fake_repo):
    m = load_script("parivesh_fisheries_requery", fake_repo)
    write_json(fake_repo / "layers/33_policy_finance_extensions.json", {"fisheries": {"keep": 1}})
    return m, fake_repo


def run(m, *argv):
    old = sys.argv
    sys.argv = ["x", *argv]
    try:
        m.main()
    finally:
        sys.argv = old


@pytest.mark.parametrize("text,hit", [
    ("Shrimp hatchery expansion", True), ("Sea Food processing", True), ("AQUACULTURE farm", True),
    ("Aquaculture", True), ("surimi plant", True), ("mollusc depuration", True), ("Crustaceans export", True),
    ("Steel plant", False), ("", False), ("fishermen colony", True), ("Offish", True)])
def test_terms_regex(mod, text, hit):
    m, _ = mod
    assert bool(m.TERMS.search(text)) is hit


def test_harbour_regex(mod):
    m, _ = mod
    assert m.HARBOUR.search("Fishing Harbor upgrade") and m.HARBOUR.search("harbour works")
    assert not m.HARBOUR.search("Hartford")


def test_fetch_builds_query(mod, monkeypatch):
    m, _ = mod
    seen = {}
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: (
        seen.update(url=req.full_url, t=timeout), FakeResp(jsonobj={"data": []}))[1])
    assert m.fetch({"fromDate": "2025-01-01", "status": "Granted"}) == {"data": []}
    q = urllib.parse.parse_qs(urllib.parse.urlparse(seen["url"]).query)
    assert q == {"fromDate": ["2025-01-01"], "status": ["Granted"]} and seen["t"] == 40


def test_main(mod, monkeypatch, capsys):
    m, root = mod
    calls = []
    rows = {
        ("Received", "false"): [
            {"proposal_no": "P1", "project_name": "Shrimp Farm Expansion", "activity_name": "Aquaculture",
             "state_name": "AP", "investment_cost": 5},
            {"proposal_no": "P1", "project_name": "Shrimp Farm Expansion", "activity_name": "dup"},     # duplicate key
            {"proposal_no": "P2", "project_name": "Harbour Works Phase II", "activity_name": "Ports and Harbours",
             "state_name": "TN"},
            {"proposal_no": "P3", "project_name": "Harbour Road", "activity_name": "Roads"},               # harbour but not ports
            {"proposal_no": "P4", "project_name": None, "activity_name": None}],
        ("Received", "true"): [{"proposal_no": "P5", "project_name": "Seafood Park " + "x" * 200, "activity_name": "Food"}],
        ("Granted", "false"): None,                                    # fetch error
        ("Granted", "true"): [{"proposal_no": "P1", "project_name": "Shrimp Farm Expansion",
                               "activity_name": "Aquaculture"}],        # same proposal, different status -> kept
    }

    def fetch(params):
        calls.append(params)
        r = rows[(params["status"], params["is_state"])]
        if r is None:
            raise RuntimeError("boom")
        return {"data": r}
    monkeypatch.setattr(m, "fetch", fetch)
    run(m, "--from", "2026-01-01", "--to", "2026-02-01")
    assert [(c["status"], c["is_state"]) for c in calls] == [
        ("Received", "false"), ("Received", "true"), ("Granted", "false"), ("Granted", "true")]
    assert all(c["fromDate"] == "2026-01-01" and c["toDate"] == "2026-02-01" for c in calls)
    res = json.load(open(root / "layers/33_policy_finance_extensions.json"))
    assert res["fisheries"]["keep"] == 1
    r = res["fisheries"]["requery_2026_07"]
    assert r["rows_scanned"] == 6 and r["window"] == "2026-01-01..2026-02-01"
    hit = {(h["proposal_no"], h["status"], h["authority"]) for h in r["name_term_hits"]}
    assert hit == {("P1", "Received", "central"), ("P5", "Received", "state"), ("P1", "Granted", "state")}
    assert [h["proposal_no"] for h in r["fishing_harbour_hits_7e"]] == ["P2"]
    p5 = next(h for h in r["name_term_hits"] if h["proposal_no"] == "P5")
    assert len(p5["project"]) == 120                                # project name truncated
    out = capsys.readouterr().out
    assert "fetch error Granted/false: RuntimeError" in out
    assert "Received/central: 5 rows, 4 unique" in out and "Received/state: 1 rows, 1 unique" in out
    assert "scanned 6 | term hits 3 | harbour hits 1" in out
    assert "HARBOUR: Harbour Works Phase II" in out and "[Received/central] Shrimp Farm Expansion" in out


def test_main_defaults(mod, monkeypatch):
    m, root = mod
    seen = []
    monkeypatch.setattr(m, "fetch", lambda p: (seen.append(p), {"data": None})[1])
    run(m)
    assert seen[0]["fromDate"] == "2025-01-01" and len(seen) == 4
    from datetime import date
    assert seen[0]["toDate"] == date.today().isoformat()
    assert json.load(open(root / "layers/33_policy_finance_extensions.json"))["fisheries"]["requery_2026_07"]["rows_scanned"] == 0
