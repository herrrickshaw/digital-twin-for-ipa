"""layer 24: PARIVESH clearance leads merged with news / rating sweeps."""
import json

import pytest

from _fakes import write_json
from conftest import load_script


@pytest.fixture
def mod(fake_repo, tmp_path):
    m = load_script("build_clearance_leads", fake_repo)
    m.ROOT = str(fake_repo)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    m.SCRATCH = str(scratch)
    (fake_repo / "layers").mkdir(exist_ok=True)
    return m, scratch, fake_repo


def _short(company, filings=3, **kw):
    d = {"company": company, "filings": filings, "activities": {"chem": filings},
         "states": {"GJ": filings}, "latest_filing": "2026-07-01"}
    d.update(kw)
    return d


def test_norm_strips_suffixes_parentheticals_and_truncates():
    m = load_script("build_clearance_leads", None)
    assert m.norm("JSW Steel Ltd") == m.norm("Jsw Steel Limited") == "jswsteel"
    assert m.norm("Alpha Pvt. Ltd (Adani group)") == "alpha"
    assert m.norm("The Foo LLP") == "foo"
    long = "A" * 40
    assert len(m.norm(long)) == 24


def test_tier1_news_fuzzy_match_and_unchecked(mod):
    m, scratch, root = mod
    write_json(scratch / "clearance_lead_shortlist.json", [
        _short("Matrix Pharmacorp Private Limited", note="n1"),
        _short("Zeta Chemicals Limited"),
        _short("Quiet Organics LLP"),
    ])
    write_json(scratch / "news_batch1.json", [
        {"company": "Matrix Pharmacorp Ltd", "verdict": "ANNOUNCED", "news_summary": "s",
         "match_with_filings": "yes", "best_source_url": "http://u",
         "announced_capex_rs_cr": 120},
        # fuzzy only: first 12 chars of norm contained in the short company's norm
        {"company": "Zeta Chemicals Ltd Unit II", "verdict": "PARTIALLY_VISIBLE"},
    ])
    write_json(scratch / "care_ratings.json", [
        {"company": "Matrix Pharmacorp", "rated_by_care": True, "rating": "AA",
         "rating_date": "2026-01", "rationale_capex_disclosure": "cap", "rationale_url": "u",
         "adds_beyond_news": "x"},
    ])
    m.main()
    out = json.load(open(root / "layers/24_clearance_leads.json"))
    by = {r["company"]: r for r in out["leads"]}
    a = by["Matrix Pharmacorp Private Limited"]
    assert a["news_verdict"] == "ANNOUNCED" and a["announced_capex_rs_cr"] == 120
    assert a["note"] == "n1"
    assert a["credit_rating"]["rating"] == "AA" and a["credit_rating"]["rated_by_care"] is True
    assert by["Zeta Chemicals Limited"]["news_verdict"] == "PARTIALLY_VISIBLE"
    assert "announced_capex_rs_cr" not in by["Zeta Chemicals Limited"]
    q = by["Quiet Organics LLP"]
    assert q["news_verdict"] == "UNCHECKED" and "credit_rating" not in q
    assert out["unmatched_in_news_sweep"] == ["Quiet Organics LLP"]
    assert out["verdict_counts"] == {"ANNOUNCED": 1, "PARTIALLY_VISIBLE": 1, "UNCHECKED": 1}
    assert all(r["tier"] == 1 for r in out["leads"])
    assert out["layer"] == 24 and out["name"] == "clearance_register_leads"


def test_tier2_tier3_and_care_check(mod, capsys):
    m, scratch, root = mod
    write_json(scratch / "clearance_lead_shortlist.json", [])
    write_json(scratch / "tier2_shortlist.json", [_short("Beta Industries Limited"), _short("Gamma Works")])
    write_json(scratch / "tier2_verify1.json", [
        {"company": "Beta Industries", "verdict": "QUIET", "news_summary": "ns", "rating": "A-",
         "rationale_capex_disclosure": "rc", "announced_capex_rs_cr": 5, "note": "t2note",
         "best_source_url": "bu"}])
    write_json(scratch / "tier3_shortlist.json", [
        {"company": "Delta Pharma Limited", "filings": 2, "activity": "api", "states": {"TG": 2},
         "latest": "2026-06-30", "policy_program": "KSM-PLI"},
        {"company": "Epsilon Bio", "filings": 1, "activity": "bio", "states": {}, "latest": "2026-05-01"},
    ])
    write_json(scratch / "tier3_verify1.json", [
        {"company": "Delta Pharma", "verdict": "ANNOUNCED", "pli_status": "not surfaced"},
        {"company": "Epsilon Bio Ltd", "verdict": "QUIET", "pli_status": "approved",
         "note": "n3", "rating": "BBB"},
    ])
    write_json(scratch / "care_tier3.json", [
        {"company": "Delta Pharma", "care_rates_it": True, "delta": "+1", "care_rating": "AA",
         "care_date": "2026-02", "highlights": "h", "url": "u"},
        {"company": "Epsilon Bio", "care_rates_it": False},
    ])
    m.main()
    out = json.load(open(root / "layers/24_clearance_leads.json"))
    by = {r["company"]: r for r in out["leads"]}
    b = by["Beta Industries Limited"]
    assert b["tier"] == 2 and b["news_verdict"] == "QUIET" and b["note"] == "t2note"
    assert b["credit_rating"] == {"rating": "A-", "rationale_capex_disclosure": "rc"}
    assert b["clearance_evidence"]["register"] == "EC register"
    g = by["Gamma Works"]
    assert g["news_verdict"] == "UNCHECKED" and g["tier"] == 2
    d = by["Delta Pharma Limited"]
    assert d["tier"] == 3 and d["policy_program"] == "KSM-PLI"
    assert d["clearance_evidence"]["activities"] == {"api": 2}
    assert d["clearance_evidence"]["latest_filing"] == "2026-06-30"
    assert "pli_status" not in d  # "not surfaced" is suppressed
    assert d["credit_rating"]["care_check"] == {
        "care_rates_it": True, "delta_vs_other_agency": "+1", "care_rating": "AA",
        "care_date": "2026-02", "highlights": "h", "url": "u"}
    e = by["Epsilon Bio"]
    assert e["pli_status"] == "approved" and e["note"] == "n3"
    assert e["credit_rating"]["care_check"] == {"care_rates_it": False, "delta_vs_other_agency": None}
    assert out["unmatched_in_news_sweep"] == ["Gamma Works"]
    assert "layer 24: 4 leads" in capsys.readouterr().out


def test_missing_optional_inputs_ok(mod):
    m, scratch, root = mod
    write_json(scratch / "clearance_lead_shortlist.json", [_short("Solo Co")])
    m.main()
    out = json.load(open(root / "layers/24_clearance_leads.json"))
    assert [r["company"] for r in out["leads"]] == ["Solo Co"]
    assert out["verdict_counts"] == {"UNCHECKED": 1}
