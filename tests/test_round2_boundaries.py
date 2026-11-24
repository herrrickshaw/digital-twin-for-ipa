"""Boundary tests added after the mutation pass (each pins an off-by-one that the first draft missed)."""
import csv
import datetime
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import time

import pytest

from _fakes import completed, write_json
from conftest import copy_script, load_script


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)


def test_edinet_checkpoint_saves_exactly_at_threshold(fake_repo, tmp_path, monkeypatch):
    m = load_script("build_edinet_india_sweep", fake_repo)
    creds = tmp_path / "e.env"
    creds.write_text("EDINET_API_KEY=testval\n")
    m.CREDS, m.OUT = str(creds), str(fake_repo / "layers/e.json")
    docs = [{"docID": f"D{i}", "ordinanceCode": "010", "docTypeCode": "120", "csvFlag": "1"} for i in range(3)]
    monkeypatch.setattr(m, "list_day", lambda k, d: docs)

    def sweep(k, doc):
        if doc == "D2":
            raise KeyboardInterrupt            # simulate an abort before the final save
        return []
    monkeypatch.setattr(m, "sweep_doc", sweep)
    monkeypatch.setattr(sys, "argv", ["x", "--days", "1", "--checkpoint-every", "2"])
    with pytest.raises(KeyboardInterrupt):
        m.main()
    saved = json.load(open(m.OUT))
    assert [r["doc_id"] for r in saved["results"]] == ["D0", "D1"]       # checkpoint fired on the 2nd doc


def test_build_leads_shows_eight_rows_per_sector(fake_repo, tmp_path):
    m = load_script("build_leads", fake_repo)
    rows = "".join(f"Co{i},T{i},us,USA,Food Processing,NA,0.1,0.1,0.1,False\n" for i in range(9))
    src = tmp_path / "s.csv"
    src.write_text("Name,Symbol,Market,Country,FocusSector,Region,profit_margin,roe,revenue_growth,expansion_signal\n" + rows)
    m.SRC, m.ROOT = str(src), str(fake_repo)
    m.build()
    md = (fake_repo / "docs/LEADS.md").read_text(encoding="utf-8")
    assert "## Food Processing (9 leads)" in md
    assert len([l for l in md.splitlines() if re.match(r"\| [\d.]+ \| Co\d", l)]) == 8


def test_kpmg_zero_roe_gets_no_bonus(fake_repo, tmp_path, monkeypatch):
    copy_script(fake_repo, "build_leads")
    home = tmp_path / "home"
    univ = home / "repos/global-stock-screener/data/global_universe"
    univ.mkdir(parents=True)
    (univ / "KR.csv").write_text("yf_ticker,name\n005930.KS,Samsung\n", encoding="utf-8")
    (univ / "JP.csv").write_text("yf_ticker,name\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    wb = tmp_path / "wb.md"
    wb.write_text("## Sheet: Korea DART Audit Clients\nStock Code | Company (Korean) | Audit Opinion\n5930 | x | ok\n", encoding="utf-8")
    q = tmp_path / "q.csv"
    q.write_text("market,yf_ticker,roe,opm,market_cap\nkorea,005930.KS,0,0,1\n", encoding="utf-8")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "", ""))
    out = tmp_path / "o"
    load_script("build_kpmg_jp_kr_leads", fake_repo, argv=[str(wb), str(q), str(out)])
    row = list(csv.DictReader(open(out / "kpmg_jp_kr_leads.csv", encoding="utf-8")))[0]
    assert row["lead_score"] == "40"          # zero ROE / zero margin earn neither +15


def test_ls_harvest_single_page_when_total_equals_page_size(fake_repo, monkeypatch):
    before = set(sys.modules)
    m = load_script("build_pq_registry", fake_repo)
    monkeypatch.setattr(m, "KEYWORDS", ["kw"])
    calls = []

    def fetch(lok, kw, page, size=200):
        calls.append((lok, page))
        return {"totalRecordSize": 200, "listOfQuestions": [{"quesNo": i, "questionsFilePath": f"{lok}-{i}"} for i in range(200)]}
    monkeypatch.setattr(m, "fetch", fetch)
    assert len(m.harvest()) == 400
    assert calls == [(17, 1), (18, 1)]
    sys.modules.pop("build_reportage", None)


def test_reportage_latest_includes_cutoff_day(fake_repo):
    m = load_script("build_reportage", fake_repo)
    m.ROOT = str(fake_repo)
    m.STATE_DB = str(fake_repo / "nope.sqlite")
    cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    m.write_html_latest([(11, cutoff, "Min", "ECMS news")], days=30)
    assert "PRID=11" in (fake_repo / "docs/reportage_latest.html").read_text()


def test_collect_news_alphavantage_gets_eight_us_tickers(fake_repo, tmp_path, monkeypatch):
    home = tmp_path / "home"
    p = home / ".config/market-secrets/credentials.env"
    p.parent.mkdir(parents=True)
    p.write_text("ALPHAVANTAGE_KEY=testval\n")
    monkeypatch.setenv("HOME", str(home))
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("collect_company_news", fake_repo)
    con = sqlite3.connect(fake_repo / "data/companies.db")
    con.executescript("""create table companies(company_id integer primary key, name text, ticker text);
        create table lead_scores(company_id integer, score real);
        create table clearance_activity(company_id integer, visibility_verdict text);""")
    for i in range(1, 13):
        con.execute("insert into companies values (?,?,?)", (i, f"Co {i}", f"T{i:02d}"))
        con.execute("insert into lead_scores values (?,?)", (i, 100 - i))
    con.commit()
    con.close()
    write_json(fake_repo / "layers/32_company_db.json", {})
    seen = []
    monkeypatch.setattr(m, "get_json", lambda u: (seen.append(u), {"feed": []})[1])
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    import urllib.parse
    q = urllib.parse.parse_qs(urllib.parse.urlparse(seen[0]).query)
    assert q["tickers"] == ["T01,T02,T03,T04,T05,T06,T07,T08"]


def test_sebi_page_whose_oldest_row_equals_since_does_not_stop(fake_repo, monkeypatch):
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("check_sebi_public_issues", fake_repo)
    con = sqlite3.connect(fake_repo / "data/companies.db")
    con.executescript("create table companies(company_id integer primary key, name text);"
                      "create table clearance_activity(company_id integer, visibility_verdict text);")
    con.commit()
    con.close()
    write_json(fake_repo / "layers/32_company_db.json", {})
    pages = {0: ("Jan 01, 2025", "http://f/0"), 1: ("Dec 01, 2024", "http://f/1")}
    fetched = []

    def fetch(p):
        fetched.append(p)
        d, u = pages[p]
        return f"<td>{d}</td><td><a href='{u}' title=\"Co{p} Limited - DRHP\">x</a></td>"
    monkeypatch.setattr(m, "fetch_page", fetch)
    monkeypatch.setattr(sys, "argv", ["x", "--since", "2025-01-01"])
    m.main()
    assert fetched == [0, 1]


def _cin(root):
    return load_script("extract_cin_from_drhp", root)


@pytest.mark.parametrize("dots,length,expect_obj", [(200, 400, True), (201, 402, False), (0, 100, False), (0, 101, True)])
def test_extract_objects_section_thresholds(fake_repo, monkeypatch, tmp_path, dots, length, expect_obj):
    m = _cin(fake_repo)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    body = ("x." * dots) if dots else ("a" * length)
    full = "OBJECTS OF THE ISSUE " + body
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: completed(b"" if "-f" in cmd else full.encode()))
    obj = m.extract(b"x")[3]
    assert bool(obj) is expect_obj


def test_stats_list_allows_three_digit_percent(fake_repo):
    m = load_script("build_switzerland_india_sweep", None)
    assert m.STATS_LIST_RE.search("India (100%)") and not m.STATS_LIST_RE.search("India (1000%)")


def test_dashboard_truncates_investment_and_detail(fake_repo):
    m = load_script("build_national_dashboard", fake_repo)
    L = fake_repo / "layers"
    m.LAYERS_DIR, m.OUT_HTML = str(L), str(fake_repo / "docs/nd.html")
    mou = {"company": "C", "state": "S", "follow_through_status": "x", "proposed_investment": "I" * 300,
           "status_detail": "D" * 400}
    (L / "44_state_mou_5yr_sweep.json").write_text(json.dumps({"total_mous": 1, "by_state": {"S": {"mous": [mou]}}}))
    m.main()
    html = open(m.OUT_HTML, encoding="utf-8").read()
    assert "I" * 220 in html and "I" * 221 not in html
    assert "D" * 320 in html and "D" * 321 not in html


def test_layer41_names_shorter_than_four_chars_are_ignored(fake_repo, tmp_path):
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("build_layer41_association_leads_crossref", fake_repo)
    scratch = tmp_path / "s"
    scratch.mkdir()
    m.SCRATCH = str(scratch)
    m.CURATED = {}
    (scratch / "semicon_india_2025_names.txt").write_text("Abc\nBrand New Chips Corporation\n")
    m.main()
    assert json.load(open(m.OUT_JSON))["sources"]["SEMICON India 2025"]["unique"] == 1
