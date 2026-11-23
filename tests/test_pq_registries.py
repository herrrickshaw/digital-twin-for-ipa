"""Lok Sabha / Rajya Sabha question registries: harvest, dedupe, classify, render."""
import json
import sys
import time
import urllib.parse
import urllib.request

import pytest

from _fakes import FakeResp
from conftest import load_script


@pytest.fixture(autouse=True)
def clean_modules(monkeypatch):
    before = set(sys.modules)
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    yield
    for k in set(sys.modules) - before:
        if k in ("build_reportage", "build_pq_registry"):
            del sys.modules[k]


@pytest.fixture
def ls(fake_repo):
    m = load_script("build_pq_registry", fake_repo)
    m.ROOT = str(fake_repo)
    m.CACHE = str(fake_repo / "data/registers/ls_pq_cache.json")
    m.OUT_HTML = str(fake_repo / "docs/pq_registry.html")
    return m, fake_repo


@pytest.fixture
def rs(fake_repo):
    m = load_script("build_rs_pq_registry", fake_repo)
    m.ROOT = str(fake_repo)
    m.CACHE = str(fake_repo / "data/registers/rs_pq_cache.json")
    m.OUT_HTML = str(fake_repo / "docs/rs_pq_registry.html")
    m.OUT_JSON = str(fake_repo / "data/registers/rs_pq_registry.json")
    return m, fake_repo


# ------------------------------------------------------------------- helpers
def test_iso_quarter_esc(ls):
    m, _ = ls
    assert m.iso("05.03.2024") == "2024-03-05" and m.iso("05.03.2024 extra") == "2024-03-05"
    assert m.iso("2024-03-05") == "" and m.iso("") == "" and m.iso(None) == ""
    assert m.quarter("2024-03-31") == "2024Q1" and m.quarter("2024-04-01") == "2024Q2"
    assert m.quarter("2024-12-01") == "2024Q4" and m.quarter("") == "?"
    assert m.esc('a & b <c> "d"') == 'a &amp; b &lt;c&gt; "d"' and m.esc(None) == ""


def test_keyword_lists_are_distinct_and_nonempty(ls):
    m, _ = ls
    assert len(m.KEYWORDS) == len(set(m.KEYWORDS)) and "PLI" in m.KEYWORDS
    assert set(m.KEYWORDS).isdisjoint(m.KEYWORDS_SUPPLEMENTARY)


# ------------------------------------------------------------------ LS fetch
def test_ls_fetch_builds_query_and_strips_control_chars(ls, monkeypatch):
    m, _ = ls
    seen = {}

    def fake_urlopen(req, timeout=None):
        seen["url"], seen["timeout"], seen["ua"] = req.full_url, timeout, req.headers
        return FakeResp(b'[{"totalRecordSize": 1, "note": "tab\there"}]')
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    d = m.fetch(18, "Surya Ghar", 2, size=50)
    assert d["note"] == "tab\there" and seen["timeout"] == 60
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(seen["url"]).query)
    assert q == {"loksabhaNo": ["18"], "keyWord": ["Surya Ghar"], "pageNo": ["2"], "pageSize": ["50"], "locale": ["en"]}


def _ls_q(n, subject="PLI scheme", date="05.03.2024", path=None, session=3, qtype="STARRED"):
    return {"sessionNo": session, "quesNo": n, "type": qtype, "subjects": f" {subject} ", "ministry": "power ministry",
            "member": ["A", "B", "C", "D"], "date": date, "questionsFilePath": path}


def test_ls_harvest_dedupes_paginates_and_isolates_failures(ls, monkeypatch, capsys):
    m, _ = ls
    monkeypatch.setattr(m, "KEYWORDS", ["kw1", "kw2", "kwfail"])
    calls = []

    def fake_fetch(lok, kw, page, size=200):
        calls.append((lok, kw, page))
        if kw == "kwfail":
            raise RuntimeError("down")
        if kw == "kw1" and page == 1:
            return {"totalRecordSize": 250, "listOfQuestions": [_ls_q(1, path="p1"), _ls_q(2, path=None)]}
        if kw == "kw1" and page == 2:
            return {"totalRecordSize": 250, "listOfQuestions": [_ls_q(3, path="p3")]}
        return {"totalRecordSize": 3, "listOfQuestions": [_ls_q(1, path="p1"), _ls_q(2, path=None), _ls_q(9, path="p9")]}
    monkeypatch.setattr(m, "fetch", fake_fetch)
    rows = m.harvest()
    # lok 17 and 18 both queried; a question is keyed by its PDF path when it has one (so the same
    # path in LS18 is a duplicate) and by lok-session-qno otherwise (so qno 2 reappears under LS18)
    keys = [(r["lok"], r["qno"]) for r in rows]
    assert keys == [(17, 1), (17, 2), (17, 3), (17, 9), (18, 2)]
    assert (17, "kw1", 2) in calls and (17, "kw2", 2) not in calls      # second page only when total > 200
    assert ("kwfail" in [c[1] for c in calls]) and len([c for c in calls if c[1] == "kwfail"]) == 2
    r0 = rows[0]
    assert r0["subject"] == "PLI scheme" and r0["ministry"] == "Power Ministry" and r0["pdf"] == "p1"
    assert r0["members"] == ["A", "B", "C", "D"]
    err = capsys.readouterr().err
    assert "! 17/kwfail p1: down" in err and "LS17 'kw1': total 250" in err


def test_ls_harvest_stops_on_empty_page(ls, monkeypatch):
    m, _ = ls
    monkeypatch.setattr(m, "KEYWORDS", ["only"])
    n = {"c": 0}

    def fake_fetch(lok, kw, page, size=200):
        n["c"] += 1
        return {"totalRecordSize": 9999, "listOfQuestions": []}
    monkeypatch.setattr(m, "fetch", fake_fetch)
    assert m.harvest() == [] and n["c"] == 2     # one call per house, no infinite paging


# ------------------------------------------------------------ LS classify
def test_ls_classify_sorting_dedup_and_filters(ls):
    m, _ = ls
    rows = [
        {"subject": "Status of PLI scheme for automobile", "date": "05.03.2024", "qno": 5},
        {"subject": "Status of PLI scheme for automobile", "date": "05.03.2024", "qno": 9},
        {"subject": "Weather", "date": "05.03.2024", "qno": 1},                       # no scheme hit
        {"subject": "ECMS progress", "date": "bad-date", "qno": 2},                    # unparseable date
        {"subject": "ECMS progress", "date": "01.01.2025", "qno": 3},
        {"subject": "PLI Specialty Steel update", "date": "02.02.2023", "qno": 4},
    ]
    out = m.classify(rows)
    assert [r["qno"] for r in out] == [3, 9, 5, 4]            # iso desc, then qno desc
    assert out[0]["q"] == "2025Q1" and out[0]["iso"] == "2025-01-01" and out[0]["schemes"] == ["ECMS"]
    steel = out[-1]
    # "PLI Specialty Steel" (generic family -> sector split) and the dedicated scheme label collapse to one
    assert len(steel["schemes"]) == 1
    assert out[1]["schemes"] == ["PLI — Auto & Components"]


def test_ls_write_html(ls):
    m, root = ls
    rows = [
        {"lok": 18, "qno": 3, "qtype": "STARRED", "subject": "ECMS <progress>", "ministry": "MeitY & Co",
         "members": ["A", "B", "C", "D"], "pdf": "http://x/p?a=1&b=2", "iso": "2025-01-01", "q": "2025Q1", "schemes": ["ECMS"]},
        {"lok": 17, "qno": 4, "qtype": None, "subject": "s2", "ministry": "M2", "members": ["Z"],
         "pdf": "p", "iso": "2023-02-02", "q": "2023Q1", "schemes": ["A", "B"]},
    ]
    m.write_html(rows)
    html = open(m.OUT_HTML, encoding="utf-8").read()
    assert "2 Lok Sabha questions" in html
    assert html.index('data-q="2025Q1"><h2>') < html.index('data-q="2023Q1"><h2>')       # newest quarter first
    assert "ECMS &lt;progress&gt;" in html and "MeitY &amp; Co" in html and 'href="http://x/p?a=1&amp;b=2"' in html
    assert "A, B, C &amp; ors." in html and "Asked by Z</div>" in html
    assert 'data-s="A; B"' in html and 'data-t=""' in html and "LS17 &middot; ? Q.4" in html
    assert "<h2>2025Q1 <span class=\"n\">&middot; 1 questions</span>" in html


def test_ls_main_uses_cache_unless_refresh(ls, monkeypatch, capsys):
    m, root = ls
    (root / "data/registers").mkdir(parents=True, exist_ok=True)
    cache = [{"subject": "ECMS progress", "date": "01.01.2025", "qno": 3, "lok": 18, "qtype": "STARRED",
              "ministry": "M", "members": [], "pdf": "p"}]
    json.dump(cache, open(m.CACHE, "w"))
    monkeypatch.setattr(m, "harvest", lambda: pytest.fail("cache hit must not harvest"))
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    reg = json.load(open(root / "data/registers/ls_pq_registry.json"))
    assert len(reg) == 1 and reg[0]["schemes"] == ["ECMS"]
    out = capsys.readouterr().out
    assert "pq registry: 1 scheme-mapped questions (2025Q1..2025Q1) of 1 harvested" in out
    # --refresh harvests again and rewrites the cache
    fresh = [dict(cache[0], qno=4), dict(cache[0], qno=5)]
    monkeypatch.setattr(m, "harvest", lambda: fresh)
    monkeypatch.setattr(sys, "argv", ["x", "--refresh"])
    m.main()
    assert len(json.load(open(m.CACHE))) == 2
    assert "harvested 2 raw questions" in capsys.readouterr().out


def test_ls_main_harvests_when_cache_missing(ls, monkeypatch):
    m, root = ls
    monkeypatch.setattr(m, "harvest", lambda: [{"subject": "ECMS", "date": "01.01.2025", "qno": 1, "lok": 17,
                                                "qtype": "", "ministry": "", "members": [], "pdf": "p"}])
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    assert len(json.load(open(m.CACHE))) == 1


# ---------------------------------------------------------------------- RS
def test_rs_fetch_quotes_where_clause(rs, monkeypatch):
    m, _ = rs
    seen = {}
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: (
        seen.update(url=req.full_url, timeout=timeout), FakeResp(b'[{"qno": 1}]'))[1])
    assert m.fetch("qtitle like '%PLI%'") == [{"qno": 1}]
    assert seen["timeout"] == 90
    where = urllib.parse.parse_qs(urllib.parse.urlsplit(seen["url"]).query)["whereclause"][0]
    assert where == "qtitle like '%PLI%'"


def test_rs_harvest(rs, monkeypatch, capsys):
    m, _ = rs
    monkeypatch.setattr(m, "KEYWORDS", ["PLI", "O'Brien"])
    monkeypatch.setattr(m, "KEYWORDS_SUPPLEMENTARY", ["bad"])
    wheres = []

    def fake_fetch(where):
        wheres.append(where)
        if "bad" in where:
            raise RuntimeError("x")
        return [{"ses_no": 250, "qno": "7", "qtype": " STARRED ", "qtitle": " PLI q ", "min_name": "power",
                 "shri": "Shri", "name": "A Kumar", "adate": "2024-03-05T00:00:00", "files": "f1"},
                {"ses_no": 250, "qno": None, "qtype": None, "qtitle": None, "min_name": None, "shri": None,
                 "name": None, "adate": None, "files": None}]
    monkeypatch.setattr(m, "fetch", fake_fetch)
    rows = m.harvest()
    assert wheres[1] == "qtitle like '%O''Brien%' and adate >= '2019-01-01'"       # quote doubled
    assert len(wheres) == 3
    assert [r["qno"] for r in rows] == [7, 0]                  # second keyword's records deduped by key
    r = rows[0]
    assert r["qtype"] == "STARRED" and r["subject"] == "PLI q" and r["ministry"] == "Power"
    assert r["members"] == ["Shri A Kumar"] and r["iso_date"] == "2024-03-05" and r["pdf"] == "f1"
    assert rows[1]["members"] == [] and rows[1]["iso_date"] == "" and rows[1]["subject"] == ""
    assert "! 'bad': x" in capsys.readouterr().err


def test_rs_classify_requires_hit_and_date(rs):
    m, _ = rs
    rows = [{"subject": "ECMS progress", "iso_date": "2025-01-01", "qno": 2},
            {"subject": "ECMS progress", "iso_date": "", "qno": 3},
            {"subject": "nothing", "iso_date": "2025-01-01", "qno": 4},
            {"subject": "ECMS again", "iso_date": "2025-01-01", "qno": 9},
            {"subject": "ECMS old", "iso_date": "2024-01-01", "qno": 99}]
    out = m.classify(rows)
    assert [r["qno"] for r in out] == [9, 2, 99]
    assert out[0]["iso"] == "2025-01-01" and out[0]["q"] == "2025Q1" and out[0]["schemes"] == ["ECMS"]


def test_rs_write_html_and_main(rs, monkeypatch, capsys):
    m, root = rs
    (root / "data/registers").mkdir(parents=True, exist_ok=True)
    cache = [{"session": 260, "qno": 5, "qtype": "UNSTARRED", "subject": "ECMS <x>", "ministry": "Meity",
              "members": ["Shri A", "B", "C", "D"], "iso_date": "2025-02-02", "pdf": "http://pdf"},
             {"session": 260, "qno": 6, "qtype": "", "subject": "ECMS y", "ministry": "Meity",
              "members": [], "iso_date": "2024-02-02", "pdf": "p2"}]
    json.dump(cache, open(m.CACHE, "w"))
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    html = open(m.OUT_HTML, encoding="utf-8").read()
    assert "2 Rajya Sabha questions" in html and "since 2019" in html
    assert "ECMS &lt;x&gt;" in html and "RS Sess.260 &middot; UNSTARRED Q.5" in html
    assert "RS Sess.260 &middot; ? Q.6" in html
    assert "Asked by Shri A, B, C</div>" in html          # only the first three members, no "& ors."
    assert html.index('data-q="2025Q1"><h2>') < html.index('data-q="2024Q1"><h2>')
    reg = json.load(open(m.OUT_JSON))
    assert [r["qno"] for r in reg] == [5, 6]
    assert "rs pq registry: 2 scheme-mapped questions (2024Q1..2025Q1) of 2 harvested" in capsys.readouterr().out


def test_rs_main_refresh_harvests(rs, monkeypatch, capsys):
    m, root = rs
    monkeypatch.setattr(m, "harvest", lambda: [{"session": 1, "qno": 1, "qtype": "", "subject": "ECMS", "ministry": "",
                                                "members": [], "iso_date": "2025-01-01", "pdf": "p"}])
    monkeypatch.setattr(sys, "argv", ["x", "--refresh"])
    m.main()
    assert "harvested 1 raw RS questions" in capsys.readouterr().out
    assert len(json.load(open(m.CACHE))) == 1
