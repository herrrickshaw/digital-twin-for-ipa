"""16_leads builder: scoring, ordering, markdown rendering."""
import json

import pytest

from conftest import load_script

CSV = (
    "Name,Symbol,Market,Country,FocusSector,Region,profit_margin,roe,revenue_growth,expansion_signal\n"
    # margin and roe exceed their caps -> capped to 20 + 20; expansion +25; open lane +25; states +10 = 100
    "TopCo,TOP,japan,Japan,Electronics & Semiconductors,APAC,0.9,0.9,0.1,True\n"
    # half of each cap: 10 + 10; no expansion; unknown sector -> lane absent: 10, no states
    "Meh,MEH,korea,Korea,Unknown Sector,APAC,0.125,0.15,,False\n"
    # zero margin / roe, in a closed-lane-free sector
    "Zero,ZRO,us,USA,Pharma & Bulk Drugs,NA,0.0,0.0,0.5,False\n"
)


@pytest.fixture
def env(fake_repo, tmp_path):
    m = load_script("build_leads", fake_repo)
    src = tmp_path / "src.csv"
    src.write_text(CSV, encoding="utf-8")
    m.SRC = str(src)
    m.ROOT = str(fake_repo)
    return m, fake_repo


def test_build_scores_and_orders(env, capsys):
    m, root = env
    m.build()
    out = json.load(open(root / "layers/16_leads.json"))
    assert out["count"] == 3 == len(out["leads"])
    scores = {l["company"]: l["lead_score"] for l in out["leads"]}
    assert scores["TopCo"] == 100.0
    assert scores["Meh"] == 10 + 10 + 10   # margin/roe half caps + no-lane default 10
    assert scores["Zero"] == 0 + 0 + 0 + 25 + 10  # pharma: operational lane + states
    ordered = [l["company"] for l in out["leads"]]
    assert ordered == ["TopCo", "Zero", "Meh"]
    top = out["leads"][0]
    assert top["profitability"] == {"margin": 0.9, "roe": 0.9, "revenue_growth": 0.1}
    assert top["expansion_signal"] is True
    assert top["central_lanes"][0] == {"instrument": "ECMS", "status": "open -- Rs 40,000cr outlay, FCFS"}
    meh = next(l for l in out["leads"] if l["company"] == "Meh")
    assert meh["profitability"]["revenue_growth"] is None
    assert meh["central_lanes"] == [] and meh["state_landings"] == []
    assert meh["enrichment"]["status"] == "PENDING"
    md = (root / "docs/LEADS.md").read_text(encoding="utf-8")
    assert "## Electronics & Semiconductors (1 leads)" in md
    assert "| 100.0 | TopCo | TOP | Japan | 90.0% | 90.0% | 10.0% | ✅ |" in md
    assert "| 30.0 | Meh | MEH | Korea | 12.5% | 15.0% | 0.0% |  |" in md
    assert "leads: 3 -> layers/16_leads.json" in capsys.readouterr().out


def test_render_from_json(env, capsys):
    m, root = env
    leads = [
        {"company": "A" * 50, "country": "Germany-extra-long-name", "sector": "S1", "lead_score": 70,
         "india_apac_interest": {"level": "HIGH", "evidence": ["x|y" * 60]}},
        {"company": "B", "country": "USA", "sector": "S1", "lead_score": 80,
         "india_apac_interest": {"india_mentions": 4, "apac_mentions": 2, "india_trend_yoy": "+1",
                                 "investment_sentences": ["invest here"]}},
        {"company": "C", "country": "UK", "sector": "S2", "lead_score": 95},
    ]
    json.dump({"count": 3, "leads": leads,
               "china_pn3_note": "N" * 10 + " ‖ UPDATE hidden",
               "china_pn3_policy_update": {
                   "press_note": "PN-X", "date": "2026-01-01", "rule": "R", "still_gated": "G",
                   "primary_source": "src, http://x", "verified": "yes",
                   "cabinet_approval_source": "cab", "timeline_reconstructed": "tl",
                   "confirmed_second_lane": "lane2"}},
              open(root / "layers/16_leads.json", "w"))
    m.render()
    md = (root / "docs/LEADS.md").read_text(encoding="utf-8")
    assert "(3 leads, 7 markets)" in md
    assert "N" * 10 + "…" in md and "hidden" not in md
    assert "Policy update — PN-X (2026-01-01)**: R. Still gated: G. Source: src; verified yes" in md
    assert "Primary source confirmed**: cab" in md
    assert "> **Timeline**: tl" in md
    assert "Second lane (60-day fast-track, government route)**: lane2" in md
    # sectors ordered by max score desc: S2 (95) before S1 (80)
    assert md.index("## S2") < md.index("## S1")
    # within S1 rows ordered by score desc
    assert md.index("| 80 | B |") < md.index("| 70 | AAAA")
    assert "10-K: India×4, APAC×2, trend +1 | invest here" in md
    assert "| 95 | C | UK | domestic |  |" in md
    row_a = next(l for l in md.splitlines() if l.startswith("| 70 |"))
    assert row_a.split(" | ")[1] == "A" * 40
    assert row_a.split(" | ")[2] == "Germany-extra-lo"      # country[:16]
    assert "x/y" in row_a                                      # pipes escaped
    assert "rendered 3 leads" in capsys.readouterr().out


def test_render_without_optional_blocks(env):
    m, root = env
    json.dump({"count": 1, "leads": [{"company": "Z", "country": "C", "sector": "S", "lead_score": 1}]},
              open(root / "layers/16_leads.json", "w"))
    m.render()
    md = (root / "docs/LEADS.md").read_text(encoding="utf-8")
    assert "China / Press Note 3" not in md and "Policy update" not in md


def test_main_guard_dispatch(env, monkeypatch):
    m, root = env
    # __main__ with --render uses render(); without it uses build()
    json.dump({"count": 0, "leads": []}, open(root / "layers/16_leads.json", "w"))
    load_script("build_leads", root, argv=["--render"], run_name="__main__",
                globals_override={})
    assert (root / "docs/LEADS.md").exists()
