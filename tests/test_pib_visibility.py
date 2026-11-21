import pytest

import pib_visibility as pv


@pytest.mark.parametrize("name,core", [
    ("Kerry Group plc", "Kerry"),
    ("Mitsubishi Heavy Industries Co., Ltd.", "Mitsubishi Heavy Industries"),
    ("The a2 Milk Company", "a2 Milk"),
    ("Saudi Basic Industries Corporation (SABIC)", "Saudi Basic Industries"),
])
def test_core_name_strips_suffixes(name, core):
    assert pv.core_name(name)[0] == core


def test_core_name_collects_parenthetical_aliases():
    assert pv.core_name("Saudi Basic Industries Corporation (SABIC)")[1] == ["SABIC"]


def test_distinctive_first_token_matches_alone():
    pat, _ = pv.pattern_for("Suzuki Motor Corporation")
    assert pat.search("Maruti Suzuki opens plant")


def test_generic_first_token_is_phrase_only():
    pat, note = pv.pattern_for("Food Empire Holdings")
    assert pat.search("Food Empire to invest") and not pat.search("street food stalls")
    assert "phrase-only" in note


@pytest.mark.parametrize("company", ["Hon Hai Precision", "ELI LILLY AND COMPANY"])
def test_short_first_token_never_matches_alone(company):
    pat, _ = pv.pattern_for(company)
    assert not pat.search("Hon'ble Minister launches ELI scheme")


def test_short_single_acronym_is_case_sensitive():
    pat, note = pv.pattern_for("GSK plc")
    assert pat.search("GSK expands") and not pat.search("gsk")
    assert "acronym" in note


def test_ambiguous_names_excluded_or_curated():
    assert pv.pattern_for("Astra Industrial Group")[0] is None
    pat, _ = pv.pattern_for("Kerry Group")
    assert not pat.search("John Kerry visits India") and pat.search("Kerry Group invests")


def test_empty_name_excluded():
    assert pv.pattern_for("")[0] is None
