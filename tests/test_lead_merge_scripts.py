"""merge_cluster_leads, merge_news_visibility, apply_ministry_corrections, build_target_leads."""
import json
import sys

import pytest

from _fakes import write_json
from conftest import copy_script, load_script


# ----------------------------------------------------------- merge_cluster_leads
@pytest.fixture
def mcl(fake_repo, tmp_path):
    copy_script(fake_repo, "build_leads")
    m = load_script("merge_cluster_leads", fake_repo)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    m.SCRATCH = str(scratch)
    return m, fake_repo, scratch


LANE_OPEN = {"central": [("X", "open now")], "states": ["S1"]}
LANE_CLOSED = {"central": [("X", "closed for good")], "states": []}


@pytest.mark.parametrize("lane,company,expected", [
    (LANE_OPEN, {"profitability": {"margin": 0.25, "roe": 0.30}, "expansion_signal": True}, 100.0),
    (LANE_OPEN, {"profitability": {"margin": 0.5, "roe": 0.9}, "expansion_signal": True}, 100.0),     # capped
    (LANE_OPEN, {"profitability": {"margin": 0.125, "roe": 0.15}}, 10 + 10 + 25 + 10),
    (LANE_CLOSED, {"profitability": {"margin": 0.125, "roe": 0.15}}, 10 + 10 + 10),
    (LANE_CLOSED, {}, 10.0),                                                                          # lane none open, no states
    (LANE_OPEN, {"profitability": {"margin": "UNVERIFIED", "roe": None}}, 25 + 10),                   # non-numeric -> 0
    ({"central": [("X", "window closes soon")], "states": []}, {}, 25.0),                             # 'closes' counts as open
    ({"central": [("X", "OPERATIONAL")], "states": []}, {}, 25.0),
])
def test_score(mcl, lane, company, expected):
    m, *_ = mcl
    assert m.score(company, lane) == expected


def test_lanes_for(mcl):
    m, *_ = mcl
    assert m.lanes_for("Nope", {}) == {"central": [], "states": []}
    assert m.lanes_for("A", {"A": {"central": [1], "states": [2]}}) == {"central": [1], "states": [2]}


def _leads_file(root, leads):
    (root / "layers/16_leads.json").write_text(json.dumps({"leads": leads, "clusters_merged": ["old"]}))


def test_merge_flow(mcl, monkeypatch, capsys):
    m, root, scratch = mcl
    _leads_file(root, [{"company": "Existing Co", "ticker": "EXI", "lead_score": 50, "country": "X"}])
    write_json(scratch / "c1.json", {"cluster": "cl-one", "companies": [
        {"company": "New Co", "ticker": "new1", "sector": "Electronics & Semiconductors", "country": "JP",
         "market": "japan", "profitability": {"margin": 0.25, "roe": 0.3}, "expansion_signal": True,
         "india_apac_interest": {"level": "HIGH"}, "notes": "n"},
        {"company": "Dup By Ticker", "ticker": "exi"},                      # ticker match is case-insensitive
        {"company": " existing co ", "ticker": None},                       # name match is case/space-insensitive
        {"company": "No Ticker Co", "sector": "Unknown Sector", "country": "KR"},
        {"company": "New Co Again", "ticker": "NEW1"},                      # dup of just-added ticker
    ]})
    monkeypatch.setattr(sys, "argv", ["x", "--only", "c1.json", "--only", "gone.json"])
    m.main()
    idx = json.load(open(root / "layers/16_leads.json"))
    names = [l["company"] for l in idx["leads"]]
    assert idx["count"] == 3 and "Dup By Ticker" not in names and "New Co Again" not in names
    assert names[0] == "New Co"                                # sorted by score desc
    new = idx["leads"][0]
    assert new["lead_score"] == 100.0 and new["source_cluster"] == "cl-one" and new["notes"] == "n"
    assert new["region"] == "Foreign" and new["enrichment"]["status"] == "PENDING"
    assert new["central_lanes"] and new["state_landings"]
    nt = next(l for l in idx["leads"] if l["company"] == "No Ticker Co")
    assert nt["central_lanes"] == [] and nt["lead_score"] == 10.0 and "notes" not in nt
    assert idx["clusters_merged"] == ["cl-one", "old"]
    out = capsys.readouterr().out
    assert "merged 2 new leads (skipped 3 already present) -> 3 total" in out
    assert "MISSING cluster files (not merged): gone.json" in out
    assert "100.0  HIGH" in out and "?" in out


def test_merge_dry_run_does_not_write(mcl, monkeypatch, capsys):
    m, root, scratch = mcl
    _leads_file(root, [])
    before = (root / "layers/16_leads.json").read_text()
    write_json(scratch / "apac_asean.json", {"companies": [{"company": "A"}]})
    monkeypatch.setattr(sys, "argv", ["x", "--dry-run"])
    m.main()
    assert (root / "layers/16_leads.json").read_text() == before
    out = capsys.readouterr().out
    assert "[DRY RUN]" in out and "apac_gulf_mena.json" in out        # default cluster list used
    # cluster name falls back to the file name when the cluster has no "cluster" key
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    idx = json.load(open(root / "layers/16_leads.json"))
    assert idx["clusters_merged"] == ["apac_asean", "old"] and idx["count"] == 1


# --------------------------------------------------------- merge_news_visibility
@pytest.fixture
def mnv(fake_repo, tmp_path):
    m = load_script("merge_news_visibility", fake_repo)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    m.SCRATCH = str(scratch)
    return m, fake_repo, scratch


@pytest.mark.parametrize("c,verdict", [
    ({"company": "Cameco Corp"}, "HEADLINED"),
    ({"company": "Ma'aden Phosphate"}, "HEADLINED"),
    ({"company": "AstraZeneca Plc"}, "STATE_PUBLICISED"),
    ({"company": "Merck KGaA"}, "SUBSUMED_IN_PARTNER"),
    ({"company": "BYD Auto", "activity_type": "plant", "summary_line": "x"}, "BLOCKED_PN3"),
    ({"company": "Haier Group", "activity_type": "none"}, "BLOCKED_PN3"),          # PN3 precedes the activity check
    ({"company": "Foo", "activity_type": "none", "summary_line": "nothing"}, "NO_ACTIVITY"),
    ({"company": "Foo", "activity_type": "", "summary_line": "nothing"}, "NO_ACTIVITY"),
    ({"company": "Foo", "activity_type": None, "summary_line": "nothing"}, "NO_ACTIVITY"),
    ({"company": "Foo", "activity_type": "bid", "summary_line": "tender"}, "NO_ACTIVITY"),
    ({"company": "Foo", "activity_type": "plant", "govt_visibility_note": "inbound mission only"}, "DIRECTION_INBOUND"),
    ({"company": "Foo", "activity_type": "plant", "summary_line": "wrong direction deal"}, "DIRECTION_INBOUND"),
    ({"company": "Foo", "activity_type": "plant",
      "govt_visibility_note": "Chief Minister attended the foundation event"}, "STATE_PUBLICISED"),
    ({"company": "Foo", "activity_type": "plant",
      "govt_visibility_note": "Tamil Nadu government inaugurated the unit"}, "STATE_PUBLICISED"),
    ({"company": "Foo", "activity_type": "plant",
      "govt_visibility_note": "No minister or state government publicity found"}, "QUIET_INVESTOR"),
    ({"company": "Foo", "activity_type": "plant",
      "govt_visibility_note": "FLAG: no minister publicity but see CM"}, "STATE_PUBLICISED"),
    ({"company": "Foo", "activity_type": "plant", "govt_visibility_note": "", "summary_line": "s"}, "QUIET_INVESTOR"),
    ({"company": "Foo", "activity_type": "plant"}, "QUIET_INVESTOR"),
])
def test_classify(mnv, c, verdict):
    m, *_ = mnv
    assert m.classify(c)[0] == verdict


def test_classify_truncates_basis(mnv):
    m, *_ = mnv
    long = "z" * 400
    assert m.classify({"company": "BYD", "summary_line": long})[1] == "z" * 300
    assert m.classify({"company": "Foo", "activity_type": "bid", "summary_line": long})[1] == \
        "campaign/bid only, not a committed investment: " + "z" * 240
    assert m.classify({"company": "Foo", "activity_type": "plant", "summary_line": long})[1] == "z" * 300


def test_merge_news_main(mnv, capsys):
    m, root, scratch = mnv
    write_json(root / "layers/19_pib_visibility.json", {"window": "w", "all": [
        {"company": "Alpha Motors", "sector": "Auto", "india_intent": "HIGH", "visibility": "BELOW_RADAR",
         "pib_investment_hits_3y": 0},
        {"company": "Beta Works", "sector": "Chem", "india_intent": "MEDIUM", "visibility": "ANNOUNCED",
         "pib_investment_hits_3y": 4}]})
    write_json(scratch / "news_below_radar_eu.json", {"companies": [
        {"company": "Alpha Systems", "country": "DE", "activity_type": "plant", "govt_visibility_note": "",
         "summary_line": "builds a plant", "india_news": [{"date": "2026-01-02T00:00", "headline": "H" * 80}]},
        {"company": "Beta Co", "country": "FR", "activity_type": "none", "summary_line": "idle", "india_news": []},
        {"company": "Cameco", "country": "CA", "activity_type": "plant", "india_news": [1, 2]},
        {"company": "Nolink Inc", "country": "US", "activity_type": "plant", "summary_line": "s"},
    ]})
    doc = m.main()
    out = json.load(open(root / "layers/20_visibility_verified.json"))
    assert out == json.loads(json.dumps(doc))
    assert out["clusters_missing"] == ["news_below_radar_asia.json", "news_below_radar_row.json"]
    order = [r["company"] for r in out["companies"]]
    # QUIET (more news first) -> HEADLINED -> NO_ACTIVITY
    assert order == ["Alpha Systems", "Nolink Inc", "Cameco", "Beta Co"]
    by = {r["company"]: r for r in out["companies"]}
    assert by["Alpha Systems"]["sector"] == "Auto" and by["Alpha Systems"]["pib_visibility"] == "BELOW_RADAR"
    assert by["Beta Co"]["pib_investment_hits_3y"] == 4 and by["Beta Co"]["india_intent"] == "MEDIUM"
    assert by["Nolink Inc"]["pib_visibility"] == "UNKNOWN" and by["Nolink Inc"]["sector"] is None
    assert by["Nolink Inc"]["pib_investment_hits_3y"] == 0
    assert out["counts"] == {"QUIET_INVESTOR": 2, "HEADLINED": 1, "NO_ACTIVITY": 1}
    assert {c["company"] for c in out["corrections_applied"]} >= {"Cameco", "Thales"}
    text = capsys.readouterr().out
    assert "merged 4 companies (MISSING: " in text
    assert "  QUIET_INVESTOR     2" in text and "QUIET INVESTORS" in text
    assert "2026-01-02" in text and "H" * 60 in text and "H" * 61 not in text
    assert "None" in text                                    # missing news prints placeholders


def test_merge_news_no_missing_key_when_all_present(mnv):
    m, root, scratch = mnv
    write_json(root / "layers/19_pib_visibility.json", {"window": "w", "all": []})
    for f in m.NEWS:
        write_json(scratch / f, {"companies": []})
    doc = m.main()
    assert "clusters_missing" not in doc and doc["counts"] == {}


# --------------------------------------------------- apply_ministry_corrections
def test_apply_ministry_corrections(fake_repo, tmp_path, capsys):
    m = load_script("apply_ministry_corrections", fake_repo)
    scratch = tmp_path / "s"
    scratch.mkdir()
    m.SCRATCH = str(scratch)
    write_json(scratch / "ministry_check_quiet.json", {"x": 1})
    write_json(fake_repo / "layers/20_visibility_verified.json", {"companies": [
        {"company": "Panasonic Corp", "verdict": "QUIET_INVESTOR"},
        {"company": "Mitsui O.S.K. Lines", "verdict": "QUIET_INVESTOR"},
        {"company": "CAE Inc", "verdict": "QUIET_INVESTOR"},
        {"company": "MediaTek", "verdict": "QUIET_INVESTOR"},
        {"company": "Arcelik AS", "verdict": "NO_ACTIVITY"},
        {"company": "Unrelated", "verdict": "HEADLINED"},
    ]})
    m.main()
    out = json.load(open(fake_repo / "layers/22_visibility_ministry_checked.json"))
    by = {r["company"]: r for r in out["companies"]}
    p = by["Panasonic Corp"]
    assert p["verdict"] == "MINISTRY_NAMED" and p["pib_verdict_before_ministry_check"] == "QUIET_INVESTOR"
    assert "Sl. 24" in p["ministry_basis"]
    assert by["CAE Inc"]["verdict"] == "QUIET_INVESTOR" and "pib_verdict_before_ministry_check" in by["CAE Inc"]
    assert by["MediaTek"]["ministry_check"].startswith("searched, not found -- structurally ineligible")
    assert by["Arcelik AS"]["verdict"] == "NO_ACTIVITY" and "AFFIRMATIVELY DISPROVED" in by["Arcelik AS"]["ministry_check"]
    assert "ministry_check" not in by["Unrelated"] and "pib_verdict_before_ministry_check" not in by["Unrelated"]
    mc = out["ministry_check"]
    assert [c["company"] for c in mc["corrected"]] == ["Panasonic Corp", "Mitsui O.S.K. Lines", "CAE Inc"]
    assert mc["invisibility_survives"] == ["MediaTek", "Arcelik AS"]
    assert mc["raw_files"] == ["ministry_check_quiet.json"]
    assert "3 were found named" in mc["headline_finding"]
    assert out["counts"] == {"MINISTRY_NAMED": 2, "QUIET_INVESTOR": 2, "NO_ACTIVITY": 1, "HEADLINED": 1}
    text = capsys.readouterr().out
    assert "corrected 3 verdicts; 2 invisibilities survived" in text
    assert "Panasonic Corp" in text and "-> MINISTRY_NAMED" in text and "survives as invisible: MediaTek, Arcelik AS" in text


def test_apply_ministry_first_matching_key_wins(fake_repo, tmp_path):
    m = load_script("apply_ministry_corrections", fake_repo)
    m.SCRATCH = str(tmp_path)
    write_json(fake_repo / "layers/20_visibility_verified.json", {"companies": [
        {"company": "Lenovo Group", "verdict": "V"}, {"company": "Food Empire Holdings", "verdict": "V"}]})
    m.main()
    out = json.load(open(fake_repo / "layers/22_visibility_ministry_checked.json"))
    assert [r["verdict"] for r in out["companies"]] == ["MINISTRY_NAMED_BRAND_ONLY", "MINISTRY_NAMED_SUBSIDIARY_ONLY"]
    assert out["ministry_check"]["raw_files"] == []


# ------------------------------------------------------------- build_target_leads
@pytest.fixture(scope="module")
def btl():
    return load_script("build_target_leads", None)


@pytest.mark.parametrize("ia,expected", [
    ({"level": "HIGH", "evidence": ["quote"]}, ("HIGH", 30, "quote")),
    ({"level": "MEDIUM", "evidence": []}, ("MEDIUM", 15, "")),
    ({"level": "LOW", "evidence": ["x"]}, None),
    ({"india_mentions": 8, "india_trend_yoy": 0, "investment_sentences": ["s"]}, ("HIGH", 12.0, "s")),
    ({"india_mentions": 7, "india_trend_yoy": 0}, ("MEDIUM", 10.5, "")),
    ({"india_mentions": 5, "india_trend_yoy": 0.1, "india_sentences": ["i"]}, ("HIGH", 12.5, "i")),
    ({"india_mentions": 5, "india_trend_yoy": 0}, ("MEDIUM", 7.5, "")),
    ({"india_mentions": 4, "india_trend_yoy": 0}, ("MEDIUM", 6.0, "")),
    ({"india_mentions": 3, "india_trend_yoy": 1}, None),
    ({"india_mentions": 40, "india_trend_yoy": 1}, ("HIGH", 35.0, "")),                # mention weight capped at 20
    ({"india_mentions": None, "india_trend_yoy": None}, None),
    ({}, None),
])
def test_classify_target(btl, ia, expected):
    assert btl.classify({"india_apac_interest": ia}) == expected


def test_classify_target_missing_interest(btl):
    assert btl.classify({}) is None and btl.classify({"india_apac_interest": None}) is None


def test_open_lane(btl):
    assert btl.open_lane({"central_lanes": [{"instrument": "A", "status": "closed"},
                                            {"instrument": "B", "status": "Open now"}]}) == "B (Open now)"
    assert btl.open_lane({"central_lanes": [{"instrument": "A", "status": "x"}, {"instrument": "B", "status": "y"},
                                            {"instrument": "C", "status": "z"}]}) == "A; B"
    assert btl.open_lane({"central_lanes": []}) == "(no mapped lane)"
    assert btl.open_lane({"central_lanes": [{"instrument": "A", "status": "window closes"}]}) == "A (window closes)"


def test_target_main(fake_repo, capsys):
    def lead(name, country, ia, score, tick="T"):
        return {"company": name, "ticker": tick, "country": country, "sector": "Sec", "lead_score": score,
                "india_apac_interest": ia, "central_lanes": [{"instrument": "I", "status": "open"}],
                "state_landings": ["a", "b", "c", "d"], "enrichment": {"roles_to_pull": ["CFO", "CEO", "COO", "CTO"]}}
    write_json(fake_repo / "layers/16_leads.json", {"china_pn3_note": "first ‖ second", "leads": [
        lead("Indian Co", "India", {"level": "HIGH"}, 99),
        lead("Hi One", "Japan", {"level": "HIGH", "evidence": ["E" * 300]}, 50),
        lead("Hi Two", "Korea", {"level": "HIGH", "evidence": ["e"]}, 80),
        lead("Med One", "Japan", {"level": "MEDIUM", "evidence": ["m"]}, 70),
        lead("Low One", "Japan", {"level": "LOW"}, 90),
        lead("Chinese Co", "China", {"level": "HIGH", "evidence": ["c"]}, 60),
        lead("Chinese Two", "China", {"level": "MEDIUM", "evidence": ["c2"]}, 90),
    ]})
    m = load_script("build_target_leads", fake_repo, run_name="__main__")
    out = json.load(open(fake_repo / "layers/16_target_shortlist.json"))
    assert out["count"] == 3 and out["china_pn3_count"] == 2
    # HIGH tier first (score desc), then MEDIUM
    assert [t["company"] for t in out["targets"]] == ["Hi Two", "Hi One", "Med One"]
    assert [t["target_score"] for t in out["targets"]] == [110, 80, 85]
    hi1 = next(t for t in out["targets"] if t["company"] == "Hi One")
    assert len(hi1["evidence"]) == 220 and hi1["state_landings"] == ["a", "b", "c"]
    assert hi1["why_now"] == "I (open)" and hi1["target_score"] == 80
    assert [t["company"] for t in out["china_pn3_watchlist"]] == ["Chinese Two", "Chinese Co"]
    md = (fake_repo / "docs/TARGET_LEADS.md").read_text()
    assert "2 priority + 1 warm targets across 2 countries; 2 China names" in md
    assert "**1. Hi Two** (T, Korea)" in md and "- Approach: CFO, CEO, COO" in md
    assert "> first\n\n> **‖** second" in md
    assert "| 85 | Med One | Japan | Sec | I (open) |" in md
    assert "targets: 2 HIGH + 1 MEDIUM + 2 PN3" in capsys.readouterr().out
