"""Characterisation of the national dashboard renderer; golden hash from the pre-refactor script."""
import hashlib

import build_national_dashboard as nd

EXPECTED_HTML_SHA = "28213445708bd2cf5fbe4f252ccee4f7c426cecb846a23bb1bd7e43baabcbeb6"


def test_html_is_bit_identical_to_pre_refactor(mini_root):
    page, n_mous, n_layers = nd.build_html(str(mini_root / "layers"), today="2026-01-01")
    assert (n_mous, n_layers) == (2, 17)
    assert hashlib.sha256(page.encode()).hexdigest() == EXPECTED_HTML_SHA


def test_collect_mous_sorts_newest_first():
    l44 = {"by_state": {"A": {"mous": [{"mou_date": "2021-01-01"}]}, "B": {"mous": [{"mou_date": "2025-01-01"}, {}]}}}
    assert [m.get("mou_date") for m in nd.collect_mous(l44)] == ["2025-01-01", "2021-01-01", None]


def test_render_mou_card_escapes_and_picks_first_source_url():
    card = "\n".join(nd.render_mou_card({"company": "A<B>", "source_url": "https://x/1; https://x/2",
                                         "follow_through_status": "operational -- live"}))
    assert "A&lt;B&gt;" in card and 'href="https://x/1"' in card and 'status op">operational' in card


def test_generic_summary_variants(tmp_path):
    import json
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"count": 4}))
    assert nd.generic_summary(str(p)) == "count: 4"
    p.write_text(json.dumps({"a": [1, 2], "b": {"c": [1, 2, 3]}}))
    assert nd.generic_summary(str(p)) == "b.c: 3 items"
    p.write_text(json.dumps([1, 2]))
    assert nd.generic_summary(str(p)) == "list, 2 items"
    assert nd.generic_summary(str(tmp_path / "missing.json")).startswith("error:")
