import json

import pytest

import build_layer43_state_sector_convergence as l43


def test_states_in_text_state_names_and_cities():
    t = "New plant at Sanand and an R&D centre in Bengaluru; HQ stays in Tamil Nadu"
    assert l43.states_in_text(t) == ["Gujarat", "Karnataka", "Tamil Nadu"]


def test_states_in_text_city_match_is_case_insensitive_and_dedups():
    assert l43.states_in_text("PUNE and Chakan plants, Maharashtra") == ["Maharashtra"]


def test_states_in_text_none():
    assert l43.states_in_text("A 50:50 joint venture in India") == []


@pytest.mark.parametrize("token,expected", [
    ("Tamil Nadu (PLI top-up 2023)", ["Tamil Nadu"]),
    ("UP/Gujarat/TN", ["Uttar Pradesh", "Gujarat", "Tamil Nadu"]),
    ("Andhra Pradesh, Telangana", ["Andhra Pradesh", "Telangana"]),
    ("UP EV 2022 + upevsubsidy portal", ["Uttar Pradesh"]),
    ("Karnataka A&D 2022-27", ["Karnataka"]),
    ("Orissa industrial policy", ["Odisha"]),
    ("Nowhere scheme", []),
])
def test_parse_state_landing(token, expected):
    assert l43.parse_state_landing(token) == expected


def _write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))


@pytest.fixture
def twin(tmp_path, monkeypatch):
    """Minimal synthetic layers 42 + 16 and IEM registers in a temp ROOT."""
    _write(tmp_path / "layers" / "42_sector_investment_news_sweep.json", {"sectors": {
        "EV (electric vehicles)": {"findings": [
            {"company": "SynthCo A", "signal": "New plant in Hosur and Pune", "confidence": "HIGH"},
            {"company": "SynthCo B", "signal": "Expansion at Chennai", "confidence": "HIGH"}]},
        "Semiconductors": {"findings": [
            {"company": "SynthCo C", "signal": "OSAT unit at Sanand", "confidence": "HIGH"}]},
        "Textiles": {"findings": [
            {"company": "SynthCo D", "signal": "Mill in Coimbatore", "confidence": "MEDIUM"}]},
    }})
    _write(tmp_path / "layers" / "16_leads.json", {"leads": [
        {"company": "L1", "sector": "EV", "state_landings": ["TN EV policy", "Gujarat"]},
        {"company": "L2", "sector": "EV", "state_landings": ["Tamil Nadu (capital subsidy)"]},
        {"company": "L3", "sector": None, "state_landings": ["Kerala"]},
    ]})
    _write(tmp_path / "data" / "registers" / "iem_state_totals.json", {"rows": [
        {"state": "Gujarat", "investment": 100}, {"state": "Gujarat", "investment": 250},
        {"state": "GRAND TOTAL", "investment": 9999}, {"state": "Kerala", "investment": None}]})
    (tmp_path / "docs").mkdir()
    monkeypatch.setattr(l43, "ROOT", str(tmp_path))
    monkeypatch.setattr(l43, "OUT_JSON", str(tmp_path / "layers" / "43.json"))
    monkeypatch.setattr(l43, "OUT_DOC", str(tmp_path / "docs" / "43.md"))
    return tmp_path


def test_iem_reference_keeps_latest_cumulative_row_and_drops_grand_total(twin):
    iem = l43.load_iem_reference()
    rows = iem["state_totals"]["rows"]
    assert [(r["state"], r["investment"]) for r in rows] == [("Gujarat", 250), ("Kerala", None)]
    assert iem["industry_totals"] is None


def test_convergence_counts_and_rankings(twin):
    l43.main()
    out = json.loads((twin / "layers" / "43.json").read_text())
    conv = {c["state"]: c for c in out["state_convergence"]}
    tn = conv["Tamil Nadu"]
    # revealed: EV (Hosur, Chennai) + Textiles (Coimbatore) = 2 sectors, 3 events
    assert (tn["revealed_sector_count"], tn["revealed_event_count"]) == (2, 3)
    # policy: EV via L1 + L2 -> 1 sector, 2 companies; L3 has no sector -> ignored
    assert (tn["policy_sector_count"], tn["policy_company_count"]) == (1, 2)
    assert "Kerala" not in conv
    assert out["revealed_event_count"] == 5          # state mentions, not findings (4)
    ev = out["sector_state_rankings"]["EV"]
    assert ev["revealed_ranking"][0] == {"state": "Tamil Nadu", "event_count": 2}
    assert ev["policy_ranking"][0] == {"state": "Tamil Nadu", "company_count": 2}
    assert out["multi_sector_hubs"] == []            # nobody reaches >=3 revealed / >=5 policy
    assert (twin / "docs" / "reportage_state_sector.html").exists()


def test_html_escapes_state_and_sector_names(twin):
    l43.main()
    html = (twin / "docs" / "reportage_state_sector.html").read_text()
    assert "<script" not in html.lower()
    assert l43._esc("<b>&") == "&lt;b&gt;&amp;"


def test_num_tolerates_commas_and_junk():
    assert l43._num("1,234.5") == 1234.5
    assert l43._num(None) == 0.0 and l43._num("n/a") == 0.0
