import pytest

import build_layer34_stressed_assets as l34


@pytest.mark.parametrize("rating,grade", [
    ("CARE AA+; Stable", "AA+"),
    ("CRISIL BBB-/Negative", "BBB-"),
    ("IND BB+ (upgraded from BB)", "BB+"),
    ("ICRA A- ; downgraded from A+", "A-"),
    ("CARE D", "D"),
    ("CARE AAA", "AAA"),
    ("no grade here", None),
])
def test_current_grade_keeps_notch_and_ignores_prior_grade(rating, grade):
    assert l34.current_grade(rating) == grade


@pytest.mark.parametrize("rating,care,adds,expected", [
    ("CARE BB; Issuer Not Cooperating", None, None, "rating_darkness"),
    ("CARE A", "litigation pending", None, "litigation_or_regrade"),
    ("CARE A", None, "HIGH-RISK flag", "litigation_or_regrade"),
    ("CARE A (Rating Watch with Negative Implications)", None, None, "watch_negative"),
    ("CARE BBB (RWN)", None, None, "watch_negative"),
    ("CARE BBB; downgraded from A-", None, None, "downgrade"),
    ("CARE BB+; Stable", None, None, "sub_investment_grade"),
    ("CARE BBB-; Stable", None, None, None),
    ("CARE AA", None, None, None),
])
def test_classify(rating, care, adds, expected):
    assert l34.classify(rating, care, adds) == expected


def test_sub_ig_boundary_is_bb_plus():
    assert l34._GRADE_RANK["BB+"] == l34.SUB_IG_MAX_RANK
    assert l34._GRADE_RANK["BBB-"] == l34.SUB_IG_MAX_RANK + 1
