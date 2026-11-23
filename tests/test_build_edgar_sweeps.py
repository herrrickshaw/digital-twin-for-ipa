"""EDGAR full-text-search sweeps (10-K/20-F and 8-K), HTTP faked."""
import datetime as dt
import json

import pytest
import requests

from _fakes import FakeResp
from conftest import load_script

NAMES = ["build_edgar_india_sweep", "build_edgar_8k_sweep"]


def hit(adsh, company, date="2026-01-01", forms=("10-K",)):
    return {"_source": {"adsh": adsh, "display_names": [company], "root_forms": list(forms),
                        "file_date": date}}


def search_payload(hits, total=None):
    return {"hits": {"total": {"value": len(hits) if total is None else total}, "hits": hits}}


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    import time
    monkeypatch.setattr(time, "sleep", lambda *a: None)


@pytest.mark.parametrize("name", NAMES)
def test_classify_pe_fund(name):
    m = load_script(name, None)
    assert m.classify("Acme Growth FUND III") == "pe_fund"
    assert m.classify("Foo Holdings L.P.") == "pe_fund"
    assert m.classify("Bar Partners Fund") == "pe_fund"
    assert m.classify("Baz Corp") == "foreign_operator"


def test_classify_india_domiciled():
    m = load_script("build_edgar_india_sweep", None)
    assert m.classify("ICICI BANK LTD (CIK 0001103838)") == "india_domiciled"
    assert m.classify("WIPRO (CIK 0001123799)") == "india_domiciled"
    # india-domiciled check precedes the fund check
    assert m.classify("Some FUND (CIK 0001094324)") == "india_domiciled"
    assert m.classify("Widgets Inc (CIK 0000000001)") == "foreign_operator"


@pytest.mark.parametrize("name", NAMES)
def test_search_pagination_and_cap(name, monkeypatch):
    m = load_script(name, None)
    calls = []

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append(dict(params))
        n = params["from"]
        return FakeResp(jsonobj=search_payload([hit(f"a{n}{i}", "C") for i in range(40)], total=500))
    monkeypatch.setattr(requests, "get", fake_get)
    hits = m.search("expansion in India", "2026-01-01", "2026-02-01")
    # cap: stops when from >= min(total, 100): 40, 80, 120 -> three pages
    assert len(hits) == 120 and [c["from"] for c in calls] == [0, 40, 80]
    assert calls[0]["q"] == '"expansion in India"' and calls[0]["startdt"] == "2026-01-01"
    assert calls[0]["enddt"] == "2026-02-01" and calls[0]["dateRange"] == "custom"
    assert calls[0]["forms"] == m.FORMS


@pytest.mark.parametrize("name", NAMES)
def test_search_stops_on_empty_batch_and_total(name, monkeypatch):
    m = load_script(name, None)
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(jsonobj=search_payload([])))
    assert m.search("p", "a", "b") == []
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(jsonobj=search_payload([hit("x", "C")], total=1)))
    assert len(m.search("p", "a", "b")) == 1       # from(1) >= total(1) -> done


@pytest.mark.parametrize("name", NAMES)
def test_search_retries_then_gives_up(name, monkeypatch, capsys):
    m = load_script(name, None)
    n = {"c": 0}

    def boom(*a, **k):
        n["c"] += 1
        raise RuntimeError("x" * 100)
    monkeypatch.setattr(requests, "get", boom)
    assert m.search("my phrase", "a", "b") == []
    assert n["c"] == 3
    out = capsys.readouterr().out
    assert "'my phrase': FAILED RuntimeError: " + "x" * 60 in out and "x" * 61 not in out


@pytest.mark.parametrize("name", NAMES)
def test_search_recovers_after_transient_error(name, monkeypatch):
    m = load_script(name, None)
    seq = iter([RuntimeError("500"), FakeResp(jsonobj=search_payload([hit("a", "C")], total=1))])

    def get(*a, **k):
        v = next(seq)
        if isinstance(v, Exception):
            raise v
        return v
    monkeypatch.setattr(requests, "get", get)
    assert len(m.search("p", "a", "b")) == 1


@pytest.mark.parametrize("name", NAMES)
def test_search_http_error_is_retried(name, monkeypatch):
    m = load_script(name, None)
    seq = iter([FakeResp(status=500), FakeResp(status=500), FakeResp(jsonobj=search_payload([hit("a", "C")], total=1))])
    monkeypatch.setattr(requests, "get", lambda *a, **k: next(seq))
    assert len(m.search("p", "a", "b")) == 1


def _run(name, root, argv=None):
    return load_script(name, root, argv=argv or [], run_name="__main__")


def test_india_sweep_main_merges_and_flags_new_leads(fake_repo, monkeypatch, capsys):
    out_path = fake_repo / "layers/16_enrichment/edgar_india_sweep.json"
    out_path.parent.mkdir(parents=True)
    out_path.write_text(json.dumps({"filings": [
        {"adsh": "OLD1", "company": "Old Co", "file_date": "2025-01-01", "phrases": []},
        {"adsh": "DUP", "company": "stale", "file_date": "2020-01-01", "phrases": []}]}))
    (fake_repo / "layers/16_target_shortlist.json").write_text(json.dumps(
        {"targets": [{"company": "Known Corporation Inc"}]}))

    def fake_get(url, params=None, headers=None, timeout=None):
        q = params["q"]
        if q == '"expansion in India"':
            return FakeResp(jsonobj=search_payload([
                hit("DUP", "Dup Corp", "2026-03-01"),
                hit("N1", "Known Corporation Inc", "2026-02-01", forms=("10-K", "20-F")),
                hit("N2", "Brand New Operator", "2026-04-01"),
                hit("N3", "ICICI BANK (CIK 0001103838)", "2026-05-01", forms=("20-F",)),
                {"_id": "ID-ONLY", "_source": {"file_type": "10-K"}},
            ]))
        if q == '"invest in India"':
            return FakeResp(jsonobj=search_payload([hit("N2", "Brand New Operator", "2026-04-01")]))
        return FakeResp(jsonobj=search_payload([]))
    monkeypatch.setattr(requests, "get", fake_get)
    with pytest.raises(SystemExit) as ei:
        _run("build_edgar_india_sweep", fake_repo, ["--since", "2026-01-01"])
    assert ei.value.code == 0
    out = json.load(open(out_path))
    ids = [f["adsh"] for f in out["filings"]]
    # sorted by file_date desc, old entries kept, duplicate adsh replaced by the fresh record
    assert ids == ["N3", "N2", "DUP", "N1", "OLD1", "ID-ONLY"]
    by = {f["adsh"]: f for f in out["filings"]}
    assert by["DUP"]["company"] == "Dup Corp"
    assert by["N1"]["form"] == "10-K,20-F" and by["N2"]["phrases"] == ["expansion in India", "invest in India"]
    assert by["N3"]["segment"] == "india_domiciled"
    assert by["ID-ONLY"]["company"] == "?" and by["ID-ONLY"]["form"] == "10-K" and by["ID-ONLY"]["file_date"] is None
    assert by["OLD1"]["company"] == "Old Co"
    assert out["layer"] == "edgar_india_sweep" and not (out_path.parent / "edgar_india_sweep.json.tmp").exists()
    text = capsys.readouterr().out
    assert "window 2026-01-01.." in text and "5 filings across 11 phrases" in text
    assert "(6 cumulative)" in text
    leads = [l for l in text.splitlines() if "NEW-LEAD" in l]
    assert len(leads) == 3
    assert leads[0].startswith("  NEW-LEAD [foreign_operator] 2026-04-01 10-K   Brand New Operator")
    assert leads[0].endswith("expansion in India, invest in India")
    assert "Dup Corp" in leads[1] and "?" in leads[2]
    assert "Known Corporation" not in text and "ICICI" not in text


def test_india_sweep_default_window_and_no_shortlist(fake_repo, monkeypatch, capsys):
    seen = []
    monkeypatch.setattr(requests, "get", lambda url, params=None, **k: (seen.append(params), FakeResp(jsonobj=search_payload([])))[1])
    with pytest.raises(SystemExit):
        _run("build_edgar_india_sweep", fake_repo)
    start = seen[0]["startdt"]
    assert (dt.date.fromisoformat(seen[0]["enddt"]) - dt.date.fromisoformat(start)).days == 200
    assert len(seen) == 11
    assert "NEW-LEAD" not in capsys.readouterr().out


def test_8k_sweep_main(fake_repo, monkeypatch, capsys):
    out_path = fake_repo / "layers/16_enrichment/edgar_8k_sweep.json"

    def fake_get(url, params=None, headers=None, timeout=None):
        assert params["forms"] == "8-K"
        if params["q"] == '"subsidiary in India"':
            return FakeResp(jsonobj=search_payload([hit("K1", "Big Fund L.P.", "2026-06-01", forms=("8-K",)),
                                                    hit("K2", "Op Inc", "2026-07-01", forms=())]))
        return FakeResp(jsonobj=search_payload([]))
    monkeypatch.setattr(requests, "get", fake_get)
    with pytest.raises(SystemExit) as ei:
        _run("build_edgar_8k_sweep", fake_repo, ["--since", "2026-01-01"])
    assert ei.value.code == 0
    out = json.load(open(out_path))
    assert [f["adsh"] for f in out["filings"]] == ["K2", "K1"]
    by = {f["adsh"]: f for f in out["filings"]}
    assert by["K1"]["segment"] == "pe_fund" and by["K2"]["segment"] == "foreign_operator"
    assert by["K2"]["form"] == ""                   # no root_forms and no file_type
    text = capsys.readouterr().out
    assert "2 8-K filings across 12 phrases" in text
    lines = [l for l in text.splitlines() if "NEW-LEAD" in l]
    assert lines[0].startswith("  NEW-LEAD [foreign_operator] 2026-07-01 Op Inc")
    assert lines[1].startswith("  NEW-LEAD [pe_fund] 2026-06-01 Big Fund L.P.")


def test_8k_sweep_merges_prior_output(fake_repo, monkeypatch):
    out_path = fake_repo / "layers/16_enrichment/edgar_8k_sweep.json"
    out_path.parent.mkdir(parents=True)
    out_path.write_text(json.dumps({"filings": [{"adsh": "P", "company": "Prior", "file_date": "2024-01-01"}]}))
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(jsonobj=search_payload([])))
    with pytest.raises(SystemExit):
        _run("build_edgar_8k_sweep", fake_repo)
    assert [f["adsh"] for f in json.load(open(out_path))["filings"]] == ["P"]
