"""Layer builders that probe or scrape the web (26, 27, 28, 31, 33): HTTP faked, invariants asserted."""
import json
import sys
import urllib.error
import urllib.request

import pytest

from _fakes import FakeResp
from conftest import load_script


def offline(monkeypatch, handler):
    monkeypatch.setattr(urllib.request, "urlopen", handler)


# ------------------------------------------------------------------- layer 26
IIG = (
    '<a href="/opportunities/nip-project/101" x><div class="card-main-project-title" title=" Alpha Port ">'
    '</div><span data-counter-value="12.5">12.5</span><span> bn </span></a>'
    '<a href="/opportunities/nip-project/102"><div class="card-main-project-title" title="Beta Road"></div>'
    '<span data-counter-value="2500">2500</span><span>mn</span></a>'
    '<a href="/opportunities/nip-project/101"><div class="card-main-project-title" title="Alpha dup"></div></a>'
    '<a href="/opportunities/nip-project/103"><div class="no-title"></div></a>'
    '<a href="/opportunities/nip-project/104"><div class="card-main-project-title" title="Gamma No Value"></div></a>'
)


def test_layer26_fetch_and_build(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer26_projects", fake_repo)
    seen = {}
    offline(monkeypatch, lambda req, timeout=None: (seen.update(url=req.full_url, t=timeout), FakeResp(IIG))[1])
    got = m.fetch_flagship_projects()
    assert seen["url"].endswith("rawData=true&page=0") and seen["t"] == 30
    assert [(p["project_id"], p["name"], p["value_usd_bn"]) for p in got] == [
        ("101", "Alpha Port", 12.5), ("102", "Beta Road", 2.5), ("104", "Gamma No Value", None)]
    assert got[0]["url"].endswith("/nip-project/101")
    (fake_repo / "layers/26_iig_sector_seed.json").write_text(json.dumps([
        {"name": " Steel ", "value": "5", "id": 1}, {"name": "Roads & Highways", "value": "50", "id": 2},
        {"name": "Unknown Sector", "value": 7, "id": 3}]))
    m.build()
    out = json.load(open(fake_repo / "layers/26_project_pipeline.json"))
    assert [s["name"] for s in out["sectors"]] == ["Roads & Highways", "Unknown Sector", " Steel "]   # by size desc
    assert out["pipeline_totals"]["total_nip_opportunities"] == 62 and out["pipeline_totals"]["sectors"] == 3
    assert out["sectors"][0]["twin_incentive_lane"].startswith("PM Gati Shakti") and out["sectors"][0]["opportunities"] == 50
    assert out["sectors"][1]["twin_incentive_lane"] is None and out["sectors"][2]["twin_incentive_lane"] == "PLI-Specialty Steel"
    assert "value" not in out["sectors"][0] and out["sectors"][0]["iig_filter_id"] == 2
    assert len(out["flagship_projects"]) == 3
    assert "layer 26: 3 sectors / 62 NIP opportunities, 3 flagship projects" in capsys.readouterr().out


# ------------------------------------------------------------------- layer 27
def test_layer27_check_statuses(fake_repo, monkeypatch):
    m = load_script("build_layer27_entry_facilitators", fake_repo)

    def handler(req, timeout=None):
        u = req.full_url
        if "ok" in u:
            return FakeResp(status=200)
        if "waf" in u:
            raise urllib.error.HTTPError(u, 403, "forbidden", {}, None)
        if "gone" in u:
            raise urllib.error.HTTPError(u, 404, "nf", {}, None)
        raise OSError("dns")
    offline(monkeypatch, handler)
    assert m.check("http://ok") == 200 and m.check("http://waf") == 403
    assert m.check("http://gone") == 404 and m.check("http://other") == 0


def test_layer27_build(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer27_entry_facilitators", fake_repo)
    codes = {}

    def handler(req, timeout=None):
        u = req.full_url
        n = len(codes)
        codes[u] = n
        if n % 4 == 0:
            return FakeResp(status=200)
        if n % 4 == 1:
            raise urllib.error.HTTPError(u, 403, "x", {}, None)
        if n % 4 == 2:
            raise urllib.error.HTTPError(u, 500, "x", {}, None)
        raise OSError("dns")
    offline(monkeypatch, handler)
    m.build()
    out = json.load(open(fake_repo / "layers/27_entry_facilitators.json"))
    rows = out["facilitators"]
    assert out["coverage"]["bodies"] == len(rows) == len(m.FACILITATORS)
    assert out["coverage"]["countries"] == len({r["country"] for r in rows})
    assert out["coverage"]["live_on_build"] == sum(r["live"] for r in rows)
    assert out["coverage"]["with_events_page"] == sum(1 for r in rows if r.get("events_url"))
    for r in rows:
        assert r["live"] == (r["last_status"] in (200, 301, 302, 403))
    assert {r["last_status"] for r in rows} == {200, 403, 500, 0}
    text = capsys.readouterr().out
    assert f"layer 27: {len(rows)} bodies" in text and "NOT live (check):" in text


def test_layer27_no_dead_line_when_all_live(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer27_entry_facilitators", fake_repo)
    offline(monkeypatch, lambda req, timeout=None: FakeResp(status=200))
    m.build()
    assert "NOT live" not in capsys.readouterr().out


# ------------------------------------------------------------------- layer 28
@pytest.fixture(scope="module")
def l28():
    return load_script("build_layer28_policy_watchlist", None)


@pytest.mark.parametrize("slug,title", [
    ("the-income-tax-bill-2025", "Income Tax Bill 2025"),
    ("gst-amendment-bill", "GST Amendment Bill"),
    ("the-it-rules-draft", "IT Rules Draft"),
    ("securities-markets-code-2025", "Securities Markets Code 2025"),
])
def test_titleize(l28, slug, title):
    assert l28.titleize(slug) == title


@pytest.mark.parametrize("slug,lane", [
    ("the-electricity-amendment-bill-2025", "Power / RDSS"),
    ("income-tax-bill-2025", "Taxation"),
    ("merchant-shipping-bill", "Shipping / shipbuilding"),    # first matching keyword in RELEVANCE order wins
    ("unrelated-bill", None), ("", None),
])
def test_classify(l28, slug, lane):
    assert l28.classify(slug) == lane


def test_layer28_build(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer28_policy_watchlist", fake_repo)
    prs = ('<a href="/billtrack/the-electricity-amendment-bill-2025">x</a>'
           '<a href="/billtrack/income-tax-bill-2023">x</a><a href="/billtrack/draft-nuclear-energy-bill-2024">x</a>'
           '<a href="/billtrack/unrelated-bill-2026">y</a><a href="/billtrack/category-finance">c</a>'
           '<a href="/billtrack/the-electricity-amendment-bill-2025">dup</a><a href="/billtrack/no-year-ports-bill">z</a>')
    dr = ('daily-news-editorials/policy-one daily-news-editorials/policy-two daily-news-editorials/policy-one')
    offline(monkeypatch, lambda req, timeout=None: FakeResp(prs if "prsindia" in req.full_url else dr))
    bills = m.fetch_prs_bills()
    by = {b["slug"]: b for b in bills}
    assert "category-finance" not in by and len(bills) == 5
    e = by["the-electricity-amendment-bill-2025"]
    assert e["year"] == 2025 and e["investment_lane"] == "Power / RDSS" and e["is_draft"] is False
    assert by["draft-nuclear-energy-bill-2024"]["is_draft"] is True and by["no-year-ports-bill"]["year"] is None
    assert [d["slug"] for d in m.fetch_drishti_editorials()] == ["policy-one", "policy-two"]
    m.build()
    out = json.load(open(fake_repo / "layers/28_policy_watchlist.json"))
    c = out["counts"]
    assert c == {"prs_bills_total": 5, "investment_relevant": 4, "recent_2024plus": 3,
                 "active_watchlist": 2, "drishti_editorials": 2}
    # active = relevant and year >= 2024, newest year first
    assert [b["slug"] for b in out["active_watchlist"]] == [
        "the-electricity-amendment-bill-2025", "draft-nuclear-energy-bill-2024"]
    assert [b["year"] for b in out["investment_relevant_bills"]][:2] == [2025, 2024]
    assert "layer 28: 5 PRS bills; 2 active watchlist" in capsys.readouterr().out


# ------------------------------------------------------------------- layer 31
def test_layer31_status_and_waipa(fake_repo, monkeypatch):
    m = load_script("build_layer31_ipa_sources", fake_repo)

    def handler(req, timeout=None):
        u = req.full_url
        if u.endswith("/ok"):
            return FakeResp(status=200)
        if u.endswith("/blocked"):
            raise urllib.error.HTTPError(u, 403, "x", {}, None)
        raise TimeoutError("slow")
    offline(monkeypatch, handler)
    assert m.status("http://h/ok") == 200 and m.status("http://h/blocked") == 403
    assert m.status("http://h/other") == "ERR:TimeoutError"
    blob = json.dumps({"x": {"data": [["f1", "f2"], ["India", "Japan"], ["Invest India", "JETRO"],
                                      ["<a href='https://investindia.gov.in'>x</a>", None]]}})
    page = f'<html><script type="application/json" data-for="htmlwidget-abc">{blob}</script></html>'
    offline(monkeypatch, lambda req, timeout=None: FakeResp(page))
    assert m.fetch_waipa_members() == [
        {"country": "India", "organization": "Invest India", "website": "https://investindia.gov.in"},
        {"country": "Japan", "organization": "JETRO", "website": None}]


def _l31_main(m, monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["x", *argv])
    m.main()


def test_layer31_main_live(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer31_ipa_sources", fake_repo)
    monkeypatch.setattr(m, "fetch_waipa_members", lambda: [
        {"country": "Japan", "organization": "JETRO", "website": "http://jetro"},
        {"country": "Cyprus", "organization": "CIPA", "website": None},
        {"country": "India", "organization": "Invest India", "website": "http://ii"}])
    seen = []
    monkeypatch.setattr(m, "status", lambda u: (seen.append(u), 200 if "jetro" in u else 404)[1])
    _l31_main(m, monkeypatch, [])
    out = json.load(open(fake_repo / "layers/31_ipa_source_network.json"))
    mem = out["waipa_member_directory"]
    assert mem["fetched_live"] is True and mem["count"] == 3 and mem["website_liveness_swept"] is True
    assert [x.get("website_status") for x in mem["members"]] == [200, None, 404]
    cov = out["india_top_fdi_source_coverage"]
    assert cov["Japan"] == {"waipa_member": True, "tracked_via": "Japan"}
    assert cov["Mauritius"]["waipa_member"] is False        # not in the member list this time
    assert cov["Cyprus"]["waipa_member"] is True
    assert cov["Singapore"]["waipa_member"] is False        # no waipa name -> never a member
    assert out["url_liveness"][m.WAIPA_TABLE] == 404
    assert all(v == (200 if "jetro" in k else 404) for k, v in out["url_liveness"].items())
    assert "members scraped: 3 | urls checked:" in capsys.readouterr().out


def test_layer31_main_no_live_and_failure(fake_repo, monkeypatch):
    m = load_script("build_layer31_ipa_sources", fake_repo)
    monkeypatch.setattr(m, "status", lambda u: pytest.fail("no probing with --no-live"))
    monkeypatch.setattr(m, "fetch_waipa_members", lambda: pytest.fail("no fetch with --no-live"))
    _l31_main(m, monkeypatch, ["--no-live"])
    out = json.load(open(fake_repo / "layers/31_ipa_source_network.json"))
    assert out["url_liveness"] == {} and out["waipa_member_directory"]["count"] == 0
    assert out["waipa_member_directory"]["fetched_live"] is False
    # every FDI-source country is reported as a member candidate when the member list is unknown
    assert out["india_top_fdi_source_coverage"]["Japan"]["waipa_member"] is True
    # live fetch failure is recorded as data
    monkeypatch.setattr(m, "fetch_waipa_members", lambda: (_ for _ in ()).throw(OSError("blocked")))
    monkeypatch.setattr(m, "status", lambda u: 200)
    _l31_main(m, monkeypatch, [])
    out = json.load(open(fake_repo / "layers/31_ipa_source_network.json"))
    mem = out["waipa_member_directory"]
    assert mem["fetched_live"] is False and mem["members"][0]["error"] == "live fetch failed: OSError: blocked"
    assert mem["website_liveness_swept"] is False


# ------------------------------------------------------------------- layer 33
def test_layer33(fake_repo, monkeypatch, capsys):
    m = load_script("build_layer33_policy_finance", fake_repo)
    offline(monkeypatch, lambda req, timeout=None: FakeResp(
        '<a href="/sites/default/files/b.xlsx">b</a><a href="/sites/default/files/a.xlsx">a</a>'
        '<a href="/sites/default/files/a.xlsx">dup</a><a href="/sites/default/files/x.pdf">p</a>'))
    assert m.scrape_exim_loc_links() == ["/sites/default/files/a.xlsx", "/sites/default/files/b.xlsx"]
    monkeypatch.setattr(m, "status", lambda u: 200)
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    out = json.load(open(fake_repo / "layers/33_policy_finance_extensions.json"))
    assert out["exim_bank"]["loc_xlsx"]["current_links_scraped_on_build"] == [
        "https://www.eximbankindia.in/sites/default/files/a.xlsx",
        "https://www.eximbankindia.in/sites/default/files/b.xlsx"]
    assert len(out["url_liveness"]) == 9 and set(out["url_liveness"].values()) == {200}
    assert "loc links scraped: 2 | urls checked: 9" in capsys.readouterr().out
    # scrape failure + --no-live
    monkeypatch.setattr(m, "scrape_exim_loc_links", lambda: (_ for _ in ()).throw(OSError("x")))
    m.main()
    out = json.load(open(fake_repo / "layers/33_policy_finance_extensions.json"))
    assert out["exim_bank"]["loc_xlsx"]["current_links_scraped_on_build"] == ["SCRAPE FAILED: OSError"]
    monkeypatch.setattr(sys, "argv", ["x", "--no-live"])
    monkeypatch.setattr(m, "status", lambda u: pytest.fail("not live"))
    m.main()
    assert json.load(open(fake_repo / "layers/33_policy_finance_extensions.json"))["url_liveness"] == {}
