"""Second-round end-to-end checks: run the data-driven builders on a throw-away copy of the repo's
real inputs and assert cross-field invariants of what they write (network is blocked)."""
import json
import os
import sqlite3
import time

import pytest

import conftest
from conftest import load_script


@pytest.fixture(autouse=True)
def _nosleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)


def run(name, root):
    before = conftest._snapshot(root)
    load_script(name, root, run_name="__main__")
    after = conftest._snapshot(root)
    return sorted(os.path.relpath(p, str(root)) for p in after if before.get(p) != after[p])


def J(root, rel):
    return json.load(open(os.path.join(str(root), rel), encoding="utf-8"))


def test_layer34_stressed_assets(work_repo):
    changed = run("build_layer34_stressed_assets", work_repo)
    assert set(changed) == {"data/companies.db", "layers/34_stressed_assets.json"}
    d = J(work_repo, "layers/34_stressed_assets.json")
    flags = d["company_distress_flags"]
    # each flagged company carries at least one flag, and no flag count exceeds the company list
    assert flags["companies"] and sum(flags["counts_by_flag"].values()) >= len(flags["companies"])
    assert all(n <= len(flags["companies"]) for n in flags["counts_by_flag"].values())
    assert d["layer"] == 34 and len(d["registers_to_ingest"]) == 4
    con = sqlite3.connect(os.path.join(str(work_repo), "data/companies.db"))
    views = [r[0] for r in con.execute("select name from sqlite_master where type='view'")]
    con.close()
    assert "stressed_assets" in views


def test_layer35_capital_cost_lens(work_repo):
    changed = run("build_layer35_capital_cost_lens", work_repo)
    assert set(changed) == {"docs/CAPITAL_COST_ARBITRAGE.md", "layers/35_capital_cost_arbitrage_lens.json"}
    d = J(work_repo, "layers/35_capital_cost_arbitrage_lens.json")
    rate = d["india_policy_rate"]["rate_pct"]
    table = {r["economy"]: r for r in d["rate_table"]}
    for r in d["rate_table"]:
        assert r["gap_vs_india_pts"] == round(rate - r["policy_rate_pct"], 2)
        assert r["coverage_flag"] in ("THIN", "MODERATE", "COVERED")
    # the sweep priority list is a subset of deep markets in the rate table
    assert d["sweep_priority"]
    for p in d["sweep_priority"]:
        assert p["economy"] in table and table[p["economy"]]["deep_capital_market"] is True
    gaps = [p["gap_vs_india_pts"] for p in d["sweep_priority"]]
    assert gaps == sorted(gaps, reverse=True)                  # biggest rate gap first
    md = open(os.path.join(str(work_repo), "docs/CAPITAL_COST_ARBITRAGE.md"), encoding="utf-8").read()
    assert d["sweep_priority"][0]["economy"] in md


def test_layer36_investment_snapshots(work_repo):
    changed = run("build_layer36_investment_snapshots", work_repo)
    assert set(changed) == {"docs/INVESTMENT_SNAPSHOTS.md", "layers/36_investment_snapshots.json"}
    d = J(work_repo, "layers/36_investment_snapshots.json")
    assert d["layer"] == 36 and d["upgis_2023"]["companies"] and d["access_hazards"]
    md = open(os.path.join(str(work_repo), "docs/INVESTMENT_SNAPSHOTS.md"), encoding="utf-8").read()
    for c in d["upgis_2023"]["companies"][:3]:
        assert str(c.get("company") or c.get("name")) in md


def test_layer39_textile_associations(work_repo):
    changed = run("build_layer39_textile_associations", work_repo)
    assert set(changed) == {"docs/TEXTILE_ASSOCIATIONS.md", "layers/39_textile_associations.json"}
    d = J(work_repo, "layers/39_textile_associations.json")
    assert d["associations"] and all("name" in a for a in d["associations"].values())
    md = open(os.path.join(str(work_repo), "docs/TEXTILE_ASSOCIATIONS.md"), encoding="utf-8").read()
    for key in ("swiss_textile_machinery", "cematex"):
        assert d["associations"][key]["name"] in md
    assert d["total_companies_mapped"] > 0


def test_layer40_event_registry(work_repo):
    changed = run("build_layer40_association_event_registry", work_repo)
    assert set(changed) == {"docs/ASSOCIATION_EVENT_REGISTRY.md", "layers/40_association_event_registry.json"}
    d = J(work_repo, "layers/40_association_event_registry.json")
    assert d["associations"] and d["events"]
    names = [a.get("name") or a.get("association") for a in d["associations"]]
    assert len(names) == len(set(names))                       # no duplicated association rows
    md = open(os.path.join(str(work_repo), "docs/ASSOCIATION_EVENT_REGISTRY.md"), encoding="utf-8").read()
    assert names[0] in md


def test_layer42_sector_sweep(work_repo):
    changed = run("build_layer42_sector_investment_news_sweep", work_repo)
    assert set(changed) == {"docs/SECTOR_INVESTMENT_NEWS_SWEEP.md", "layers/42_sector_investment_news_sweep.json"}
    d = J(work_repo, "layers/42_sector_investment_news_sweep.json")
    sectors = d["sectors"]
    assert d["total_findings"] == sum(s["total_findings"] for s in sectors.values())
    assert d["total_new_to_twin"] == sum(s["new_to_twin"] for s in sectors.values())
    assert all(len(s["findings"]) == s["total_findings"] for s in sectors.values())
    assert sum(d["confidence_breakdown"].values()) == d["total_findings"]
    assert all(s["new_to_twin"] <= s["total_findings"] for s in sectors.values())


def test_layer43_state_sector_convergence(work_repo):
    changed = run("build_layer43_state_sector_convergence", work_repo)
    assert set(changed) == {"docs/STATE_SECTOR_CONVERGENCE.md", "docs/reportage_state_sector.html",
                            "layers/43_state_sector_convergence.json"}
    d = J(work_repo, "layers/43_state_sector_convergence.json")
    states = d["state_convergence"]
    assert d["revealed_event_count"] == sum(s["revealed_event_count"] for s in states)
    assert d["policy_landing_count"] == sum(s["policy_company_count"] for s in states)
    for s in states:
        assert s["revealed_sector_count"] == len(s["revealed_sectors"])
        assert s["policy_sector_count"] == len(s["policy_sectors"])
    hubs = {h["state"] for h in d["multi_sector_hubs"]}
    assert hubs <= {s["state"] for s in states}
    assert [h["state"] for h in d["multi_sector_hubs"]] == [
        s["state"] for s in states if s["revealed_sector_count"] >= 3]
    html = open(os.path.join(str(work_repo), "docs/reportage_state_sector.html"), encoding="utf-8").read()
    assert html.lstrip().lower().startswith("<!doctype html") and states[0]["state"] in html


def test_layer44_state_mou_sweep(work_repo):
    changed = run("build_layer44_state_mou_5yr_sweep", work_repo)
    assert set(changed) == {"docs/STATE_MOU_5YR_SWEEP.md", "layers/44_state_mou_5yr_sweep.json"}
    d = J(work_repo, "layers/44_state_mou_5yr_sweep.json")
    by_state = d["by_state"]
    assert d["total_mous"] == sum(s["mou_count"] for s in by_state.values())
    assert d["total_new_to_twin"] == sum(s["new_to_twin"] for s in by_state.values())
    assert all(len(s["mous"]) == s["mou_count"] for s in by_state.values())
    assert sum(d["confidence_breakdown"].values()) == d["total_mous"]
    assert sum(d["follow_through_breakdown"].values()) == d["total_mous"]


def test_global_sweep_targets(work_repo):
    changed = run("build_global_sweep_targets", work_repo)
    assert set(changed) == {"docs/GLOBAL_SWEEP_TARGETS.md", "layers/37_global_sweep_targets.json"}
    d = J(work_repo, "layers/37_global_sweep_targets.json")
    for key in ("tier1_controlling_establishment", "tier2_market_presence", "china_pn3_watchlist"):
        t = d[key]
        assert t["count"] == len(t["all"]) and 0 <= t["new_to_twin"] <= t["count"]
    assert all(x.get("company") or x.get("name") for x in d["tier1_controlling_establishment"]["all"])


def test_company_db(work_repo):
    changed = run("build_company_db", work_repo)
    assert set(changed) == {"data/companies.db", "layers/32_company_db.json"}
    d = J(work_repo, "layers/32_company_db.json")
    con = sqlite3.connect(os.path.join(str(work_repo), "data/companies.db"))
    n = con.execute("select count(*) from companies").fetchone()[0]
    tables = {r[0] for r in con.execute("select name from sqlite_master where type in ('table','view')")}
    con.close()
    assert d["counts"]["companies"] == n > 0
    assert set(d["schema"]) <= tables
    assert sum(d["counts"]["by_country_top10"].values()) <= n
    assert d["counts"]["in_more_than_one_layer"] <= n


def test_textile_sector_targets_and_electronics_footprint(work_repo):
    changed = run("build_textile_sector_targets", work_repo)
    assert set(changed) == {"docs/TEXTILE_SECTOR_TARGETS.md", "layers/38_textile_sector_targets.json"}
    d = J(work_repo, "layers/38_textile_sector_targets.json")
    assert set(d["static_leads_by_confidence"]) == {"real_evidence", "weak_or_bare_mention", "india_domestic", "no_evidence"}
    changed = run("build_electronics_footprint_ambiente_techtextil", work_repo)
    assert changed == ["layers/16_enrichment/ambiente_techtextil_electronics_footprint.json"]
    f = J(work_repo, "layers/16_enrichment/ambiente_techtextil_electronics_footprint.json")
    for fair in f["results"].values():
        assert fair["direct_match_count"] == len(fair["direct_matches"])
        assert fair["keyword_signal_count"] >= len(fair["keyword_signals_sample"])
    assert f["known_electronics_company_count"] > 0


def test_mospi_connector(work_repo):
    changed = run("mospi_connector", work_repo)
    assert changed == ["layers/29_mospi_data_sources.json"]
    d = J(work_repo, "layers/29_mospi_data_sources.json")
    c = d["counts"]
    assert c["datasets"] == len(d["data_sources"]) == c["core_relevance"] + c["sector_relevance"] + c["context_relevance"]


def test_visibility_report_and_company_directory(work_repo):
    changed = run("build_visibility_report", work_repo)
    assert changed == ["docs/VISIBILITY.md"]
    md = open(os.path.join(str(work_repo), "docs/VISIBILITY.md"), encoding="utf-8").read()
    ver = J(work_repo, "layers/22_visibility_ministry_checked.json")
    assert sum(ver["counts"].values()) == len(ver["companies"])
    assert "Quiet investors" in md and "Press Note 3 cohort" in md
    changed = run("build_company_directory_state_sector", work_repo)
    assert changed == ["docs/company_directory_state_sector.html"]
