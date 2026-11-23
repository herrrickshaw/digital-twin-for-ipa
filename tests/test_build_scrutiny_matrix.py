"""Scheme scrutiny matrix: bucket A/B/C classification from PIB + parliamentary-question registers."""
import datetime
import json
import sqlite3
import sys

import pytest

from conftest import load_script

TODAY = datetime.date.today()


def iso(days):
    return (TODAY - datetime.timedelta(days=days)).isoformat()


@pytest.fixture
def run(fake_repo, tmp_path, monkeypatch):
    # build_reportage is imported by name from the real scripts dir; keep sys.modules clean afterwards
    before = set(sys.modules)
    mod = load_script("build_scrutiny_matrix", fake_repo)
    yield mod, fake_repo, tmp_path
    for k in set(sys.modules) - before:
        if k == "build_reportage":
            del sys.modules[k]


def _prepare(mod, root, tmp_path, pib, ls, rs):
    db = tmp_path / "pib.sqlite"
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.execute("create table pib_items(date text, title text)")
    con.executemany("insert into pib_items values(?,?)", pib)
    con.commit()
    con.close()
    reg = root / "data/registers"
    reg.mkdir(parents=True, exist_ok=True)
    mod.DB = str(db)
    mod.PQ_LS = str(reg / "ls.json")
    mod.PQ_RS = str(reg / "rs.json")
    mod.OUT = str(root / "docs/SCHEME_SCRUTINY_MATRIX.md")
    json.dump(ls, open(mod.PQ_LS, "w"))
    json.dump(rs, open(mod.PQ_RS, "w"))


def q(iso_, schemes, qtype="UNSTARRED"):
    return {"iso": iso_, "schemes": schemes, "qtype": qtype}


def section(md, letter):
    start = md.index(f"## {letter}. ")
    nxt = md.find("\n## ", start + 5)
    return md[start:nxt]


def test_bucket_thresholds(run, capsys):
    mod, root, tmp = run
    ls = [q(iso(10), ["ECMS"], "STARRED") for _ in range(6)] + [q(iso(20), ["ECMS"]) for _ in range(2)]
    rs = [q(iso(30), ["ECMS"]) for _ in range(2)]                 # ECMS total 10 across houses, recent -> A
    # exactly 9 questions -> B (threshold is >= 10)
    ls += [q(iso(5), ["PM Surya Ghar"]) for _ in range(9)]
    # 10 questions but the latest one is older than 365 days -> B
    ls += [q(iso(400), ["PM-KUSUM"]) for _ in range(10)]
    # exactly on the 365-day recency boundary -> still A (>= recent cutoff)
    ls += [q(iso(365), ["SPECS"]) for _ in range(10)]
    pib = [(iso(100), "ECMS guidelines"), (iso(50), "Surya Ghar rooftop solar"), (iso(40), "Surya Ghar rooftop solar again"),
           ("2024-05-01", "RDSS extension approved"), (None, "ECMS undated"), (iso(1), "irrelevant item")]
    _prepare(mod, root, tmp, pib, ls, rs)
    mod.main()
    md = open(mod.OUT, encoding="utf-8").read()
    A, B, C = section(md, "A"), section(md, "B"), section(md, "C")
    assert "| ECMS |" in A and "| SPECS |" in A
    assert "| PM Surya Ghar |" in B and "| PM-KUSUM |" in B
    assert "| RDSS |" in C
    assert "| ECMS | " + iso(100) + " | 1 | " + iso(100) + " | 8 | 2 | 6 | " in A
    assert "| PM Surya Ghar | " + iso(50) + " | 2 | " + iso(40) + " | 9 |  |  | " in B
    # A is sorted by question count desc: ECMS (10) and SPECS (10) tie, both before nothing else
    assert md.index("| ECMS |") < md.index("| PM-KUSUM |")
    assert "**2 schemes actively discussed" in md and "- **2 with some discussion**" in md
    assert "**1 announced but with zero captured" in md
    assert "(4 scheme-mapped announcements)" in md                # undated + unmapped rows excluded
    out = capsys.readouterr().out
    assert "scrutiny matrix: 5 schemes -> A 2 / B 2 / C 1" in out


def test_first_last_and_totals_across_houses(run):
    mod, root, tmp = run
    ls = [q("2024-01-10", ["ECMS"]), q("2025-02-01", ["ECMS"], "STARRED")]
    rs = [q("2023-06-01", ["ECMS"], " STARRED "), q("2025-03-01", ["ECMS", "ECMS"])]   # duplicate scheme in one row counted once
    _prepare(mod, root, tmp, [], ls, rs)
    mod.main()
    md = open(mod.OUT, encoding="utf-8").read()
    row = next(l for l in md.splitlines() if l.startswith("| ECMS |"))
    cells = [c.strip() for c in row.strip("|").split("|")]
    # Scheme | first ann | PIB | last ann | LS | RS | star | first Q | last Q
    assert cells == ["ECMS", "", "0", "", "2", "2", "2", "2023-06-01", "2025-03-01"]
    assert "(0 scheme-mapped announcements)" in md


def test_reading_c_list_branches(run):
    mod, root, tmp = run
    # PLI - White Goods and Telecom PLI announced but never questioned
    pib = [("2025-01-01", "PLI scheme for white goods"), ("2025-01-02", "telecom PLI window")]
    _prepare(mod, root, tmp, pib, [], [])
    mod.main()
    md = open(mod.OUT, encoding="utf-8").read()
    assert "STILL in C" in md and "Telecom PLI**: in C" in md
    # now both are questioned -> moved out
    ls = [q(iso(3), ["PLI — White Goods"]), q(iso(3), ["Telecom PLI"])]
    _prepare(mod, root, tmp, pib, ls, [])
    mod.main()
    md = open(mod.OUT, encoding="utf-8").read()
    assert "moved OUT of C" in md and "left C once Rajya Sabha" in md
    assert "STILL in C" not in md
