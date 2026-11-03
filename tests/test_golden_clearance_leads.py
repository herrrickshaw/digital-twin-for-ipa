"""Characterisation of build_clearance_leads.main on synthetic scratch inputs (golden captured pre-refactor)."""
import hashlib
import json

import build_clearance_leads as bcl

GOLDEN = {"json": "2ed35010f8c66c7b4c1323c91455e6abade83ab0caa7ea6049699d4492c9b865", "stdout": "9ae239e268075384fd4dab841416be3ccbd7822378c234245098518e32a5b55f"}


def _write(d, name, doc):
    (d / name).write_text(json.dumps(doc))


def _run(tmp_path, monkeypatch, capsys):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    (tmp_path / "layers").mkdir()
    _write(scratch, "clearance_lead_shortlist.json", [
        {"company": "Alpha Steel Ltd", "filings": 5, "activities": {"metallurgy": 5}, "states": {"GJ": 5}, "latest_filing": "2026-07-01"},
        {"company": "Beta Chem Pvt Ltd", "filings": 3, "latest_filing": "2026-06-01", "source": "FC register", "note": "n1"},
        {"company": "Gamma Agro LLP", "filings": 2, "latest_filing": "2026-05-01"}])
    _write(scratch, "news_batch1.json", [{"company": "Alpha Steel Limited", "verdict": "ANNOUNCED", "news_summary": "s",
                                          "match_with_filings": "yes", "best_source_url": "u", "announced_capex_rs_cr": 100}])
    _write(scratch, "news_batch2.json", [{"company": "Beta Chem", "verdict": "QUIET"}])
    _write(scratch, "care_ratings.json", [{"company": "Alpha Steel", "rated_by_care": True, "rating": "AA", "rating_date": "2026-01-01"}])
    _write(scratch, "tier2_shortlist.json", [{"company": "Delta Cement Ltd", "filings": 2, "states": {"MH": 2}, "latest_filing": "2026-07-02"}])
    _write(scratch, "tier2_verify1.json", [{"company": "Delta Cement", "verdict": "PARTIALLY_VISIBLE", "news_summary": "x", "note": "nt",
                                            "rating": "A", "rationale_capex_disclosure": "cap", "announced_capex_rs_cr": 5}])
    _write(scratch, "tier3_shortlist.json", [{"company": "Eps Pharma Ltd", "filings": 4, "activity": "api", "states": {"TG": 4},
                                              "latest": "2026-07-03", "policy_program": "PLI"},
                                             {"company": "Zeta Unmatched", "filings": 1, "activity": "x", "latest": "2026-01-01"}])
    _write(scratch, "tier3_verify1.json", [{"company": "Eps Pharma", "verdict": "QUIET", "pli_status": "approved", "note": "q"}])
    _write(scratch, "care_tier3.json", [{"company": "Eps Pharma", "care_rates_it": False, "delta": "d", "url": "http://c"}])
    monkeypatch.setattr(bcl, "ROOT", str(tmp_path))
    monkeypatch.setattr(bcl, "SCRATCH", str(scratch))
    bcl.main()
    return (tmp_path / "layers" / "24_clearance_leads.json").read_bytes(), capsys.readouterr().out


def test_main_output_is_byte_identical(tmp_path, monkeypatch, capsys, frozen_today):
    out, stdout = _run(tmp_path, monkeypatch, capsys)
    assert hashlib.sha256(out).hexdigest() == GOLDEN.get("json"), hashlib.sha256(out).hexdigest()
    assert hashlib.sha256(stdout.encode()).hexdigest() == GOLDEN.get("stdout"), hashlib.sha256(stdout.encode()).hexdigest()
