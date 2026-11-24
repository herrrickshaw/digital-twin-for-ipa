"""National dashboard: layer summaries, MoU cards, stats row and layer index."""
import json
import re

import pytest

from conftest import load_script


@pytest.fixture(scope="module")
def m():
    return load_script("build_national_dashboard", None)


def test_esc(m):
    assert m._esc("a&b<c>d") == "a&amp;b&lt;c&gt;d"
    assert m._esc(None) == "" and m._esc(5) == "5" and m._esc(0) == "0"


def test_load(fake_repo):
    mod = load_script("build_national_dashboard", fake_repo)
    mod.LAYERS_DIR = str(fake_repo / "layers")
    assert mod.load("nothing") == {}
    (fake_repo / "layers/x.json").write_text('{"a": 1}')
    assert mod.load("x") == {"a": 1}


@pytest.mark.parametrize("name,content,expected", [
    ("raw.json", "not json", None),                                     # error: prefix
    ("list.json", [1, 2, 3], "list, 3 items"),
    ("32_company_db.json", {"counts": {"companies": 1849}, "count": 5}, "companies: 1849 (deduped, all layers)"),
    ("32_company_db.json", {"counts": {}}, "companies: — (deduped, all layers)"),
    ("a.json", {"count": 7, "total_mous": 3}, "count: 7"),                # first key in priority order
    ("a.json", {"total_findings": 4}, "total findings: 4"),
    ("a.json", {"total_new_flagged": 2}, "total new flagged: 2"),
    ("a.json", {"total_new_to_twin": 9}, "total new to twin: 9"),
    ("a.json", {"total_mous": 1}, "total mous: 1"),
    ("a.json", {"known_company_count": 8}, "known company count: 8"),
    ("a.json", {"total_records_available": 6}, "total records available: 6"),
    ("a.json", {"x": [1], "y": [1, 2, 3]}, "y: 3 items"),
    ("a.json", {"x": {"p": [1, 2], "q": [1, 2, 3, 4]}, "y": [1]}, "x.q: 4 items"),
    ("a.json", {"x": [1, 2, 3], "y": {"z": [1]}}, "x: 3 items"),
    ("a.json", {"x": 1, "y": "s"}, "—"),
])
def test_generic_summary(m, tmp_path, name, content, expected):
    p = tmp_path / name
    p.write_text(content if isinstance(content, str) else json.dumps(content))
    got = m.generic_summary(str(p))
    if expected is None:
        assert got.startswith("error: ")
    else:
        assert got == expected


def _mou(company, state, status, **kw):
    d = {"company": company, "state": state, "follow_through_status": status, "country_of_headquarters": "Japan",
         "sector": "Auto", "summit_or_event": "Summit", "mou_date": "2025-01-01", "proposed_investment": "Rs 10 cr",
         "source_url": "http://src/1; http://src/2", "confidence": "HIGH"}
    d.update(kw)
    return d


def test_main(fake_repo, capsys):
    mod = load_script("build_national_dashboard", fake_repo)
    L = fake_repo / "layers"
    mod.LAYERS_DIR, mod.OUT_HTML = str(L), str(fake_repo / "docs/national_dashboard.html")
    (L / "44_state_mou_5yr_sweep.json").write_text(json.dumps({
        "total_mous": 4, "total_new_to_twin": 2,
        "follow_through_breakdown": {"no follow-up news found": 1, "operational": 1},
        "by_state": {
            "Gujarat": {"mous": [_mou("Alpha & Co", "Gujarat", "operational -- plant live", status_detail="plant commissioned"),
                                 _mou("Beta", "Gujarat", "no follow-up news found", source_url="", proposed_investment="",
                                      mou_date="2026-03-01")]},
            "Tamil Nadu": {"mous": [_mou("Gamma <x>", "Tamil Nadu", "under construction (phase 1)", mou_date=None,
                                         confidence="MEDIUM"),
                                    _mou("Delta", "", "", mou_date="2024-05-05", confidence="LOW")]}}}))
    (L / "32_company_db.json").write_text(json.dumps({"counts": {"companies": 1849}}))
    (L / "16_leads.json").write_text(json.dumps({"count": 321}))
    (L / "40_association_event_registry.json").write_text(json.dumps({"events": [1, 2, 3], "associations": [1, 2]}))
    (L / "42_sector_investment_news_sweep.json").write_text(json.dumps({"total_findings": 76}))
    (L / "43_state_sector_convergence.json").write_text(json.dumps({"state_convergence": [1, 2]}))
    (L / "99_other.json").write_text(json.dumps({"count": 5}))
    (L / "bad.json").write_text("{")
    mod.main()
    html = open(mod.OUT_HTML, encoding="utf-8").read()
    # stats row
    for label, val in [("companies tracked", "1849"), ("foreign leads", "321"), ("state MoUs (5yr)", "4"),
                       ("MoUs with no follow-up", "25%"), ("investment-news findings", "76"),
                       ("states w/ any signal", "2"), ("trade-fair events tracked", "3"), ("layers", "8")]:
        assert f'<div class="stat"><b>{val}</b><span>{label}</span></div>' in html
    # cards ordered newest first (mou_date desc; missing date last)
    order = [html.index(x) for x in ("Beta", "Alpha &amp; Co", "Delta", "Gamma &lt;x&gt;")]
    assert order == sorted(order)
    assert html.count('<div class="card" data-status=') == 4
    # status class, first source URL only, empty-url fallback, detail fallbacks
    assert '<a href="http://src/1" target="_blank" rel="noopener">Alpha &amp; Co</a>' in html
    assert '<span style="font-weight:700">Beta</span>' in html
    assert '<span class="status op">operational</span>' in html and '<span class="status op">under construction</span>' in html
    assert '<span class="status ">no follow-up news found</span>' in html and '<span class="status ">—</span>' in html
    assert "plant commissioned" in html and "under construction (phase 1)" in html
    assert 'data-status="under construction"' in html
    assert '<span class="badge HIGH">HIGH</span>' in html and '<span class="badge LOW">LOW</span>' in html
    # layer tiles + index (featured layers excluded from index, the MoU layer too)
    assert "<b>Layer 32</b>" in html and "companies: 1849 (deduped, all layers)" in html
    idx = html[html.index('<table class="idx">'):]
    assert "<tr><td>99_other</td><td>count: 5</td></tr>" in idx
    assert "<td>32_company_db</td>" not in idx and "<td>44_state_mou_5yr_sweep</td>" not in idx
    assert "<td>bad</td><td>error: " in idx
    assert re.search(r'<a href="ASSOCIATION_EVENT_REGISTRY.md">view</a>', html)
    assert "reportage_latest.html" in html
    assert "4 MoU cards, 8 layers indexed" in capsys.readouterr().out


def test_main_empty_layers(fake_repo, capsys):
    mod = load_script("build_national_dashboard", fake_repo)
    mod.LAYERS_DIR, mod.OUT_HTML = str(fake_repo / "layers"), str(fake_repo / "docs/nd.html")
    mod.main()
    html = open(mod.OUT_HTML, encoding="utf-8").read()
    assert '<div class="stat"><b>—</b><span>companies tracked</span></div>' in html
    assert '<div class="stat"><b>—%</b><span>MoUs with no follow-up</span></div>' in html
    assert '<div class="stat"><b>0</b><span>state MoUs (5yr)</span></div>' in html
    assert "0 MoU cards, 0 layers indexed" in capsys.readouterr().out
