import json

import pytest

import build_layer46_pli_bulk_drugs as l46


def test_list_sizes_match_their_names():
    assert len(l46.CRITICAL_53) == 53
    assert len(l46.PLI_APPROVED_41) == 41
    assert len(l46.COMMERCIAL_18) == 18
    assert len({l46.norm(x) for x in l46.CRITICAL_53}) == 53     # no near-duplicates


def test_commercial_products_are_all_pli_approved():
    pli = {l46.norm(p) for p in l46.PLI_APPROVED_41}
    assert {l46.norm(c) for c in l46.COMMERCIAL_18} <= pli


def test_every_bdmai_project_product_is_a_pli_product():
    pli = {l46.norm(p) for p in l46.PLI_APPROVED_41}
    assert all(l46.norm(p) in pli for _, _, p, _ in l46.BDMAI_PROJECTS)


def test_state_wise_projects_sum_to_official_48():
    assert sum(r[1] for r in l46.STATE_WISE) == 48


def test_norm_folds_case_hyphens_and_parentheses():
    assert l46.norm("Para-Amino Phenol (PAP)") == "para amino phenol pap"


def test_main_outputs_consistent_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(l46, "OUT_JSON", str(tmp_path / "46.json"))
    monkeypatch.setattr(l46, "OUT_DOC", str(tmp_path / "46.md"))
    l46.main()
    out = json.loads((tmp_path / "46.json").read_text())
    gap = out["finding_gap_apis_no_pli_project"]
    n_status = len(out["critical_api_status"])
    assert n_status == 53
    assert gap["count"] + len(out["pli_approved_not_yet_commercial"]) + \
        len(out["commercial_critical_apis"]) == 53
    assert out["total_committed_capacity_mt"] == sum(p[3] for p in l46.BDMAI_PROJECTS)


@pytest.mark.xfail(strict=True, reason=(
    "Known bug, not fixed: the 41 PLI 'products' are mostly key starting materials / "
    "intermediates (Para-amino phenol -> Paracetamol, DCDA -> Metformin, CDA -> Gabapentin, "
    "2-MNI -> Metronidazole/Tinidazole/Ornidazole, Penicillin G -> Amoxicillin, ...) that "
    "the scheme maps onto the 53 critical APIs. Matching product NAMES against API names "
    "reports 22 'gap APIs with no PLI project' (incl. Paracetamol and Metformin) even though "
    "their KSMs are PLI-approved and in commercial production. Needs a verified KSM->API "
    "mapping from the DoP scheme guidelines."))
def test_paracetamol_and_metformin_are_covered_via_their_pli_ksms(tmp_path, monkeypatch):
    monkeypatch.setattr(l46, "OUT_JSON", str(tmp_path / "46.json"))
    monkeypatch.setattr(l46, "OUT_DOC", str(tmp_path / "46.md"))
    l46.main()
    status = json.loads((tmp_path / "46.json").read_text())["critical_api_status"]
    assert status["Paracetamol"]["pli_project_approved"]
    assert status["Metformin"]["pli_project_approved"]
