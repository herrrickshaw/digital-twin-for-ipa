"""PIB headline visibility map: name -> regex derivation and the three-way visibility bucket."""
import json
import sqlite3
import sys

import pytest

from conftest import load_script


@pytest.fixture(scope="module")
def m():
    return load_script("pib_visibility", None)


@pytest.mark.parametrize("name,core,aliases", [
    ("Acme Corp.", "Acme", []),
    ("Acme Co., Ltd.", "Acme", []),
    ("Acme Holdings Limited", "Acme", []),
    ("The a2 Milk Company", "a2 Milk", []),
    ("Saudi Basic Industries (SABIC)", "Saudi Basic Industries", ["SABIC"]),
    ("Foo (ab)", "Foo", []),                       # alias shorter than 3 chars ignored
    ("Industries Qatar", "Industries Qatar", []),  # trailing-only stripping
    ("Beta Group plc", "Beta", []),
    ("", "", []), (None, "", []),
])
def test_core_name(m, name, core, aliases):
    assert m.core_name(name) == (core, aliases)


def test_pattern_for_unusable_and_excluded(m):
    assert m.pattern_for("") == (None, "no usable core name")
    rx, note = m.pattern_for("Ltd")
    assert rx is None
    rx, note = m.pattern_for("Astra Corp")
    assert rx is None and "ambiguous token 'Astra'" in note
    rx, note = m.pattern_for("Energy")
    assert rx is None and "single generic/short token 'Energy'" in note
    rx, note = m.pattern_for("Zy Holdings")
    assert rx is None and "short" in note


def test_pattern_for_curated_ambiguous(m):
    rx, note = m.pattern_for("Kerry Group plc")
    assert note == "curated pattern for ambiguous 'Kerry'"
    assert rx.search("kerry group invests") and not rx.search("John Kerry visits")
    rx, _ = m.pattern_for("Delta Electronics Inc")
    assert rx.search("Delta Electronics plant") and not rx.search("Ganga delta")


def test_pattern_for_short_acronym_is_case_sensitive(m):
    rx, note = m.pattern_for("GSK plc")
    assert note == "case-sensitive acronym match 'GSK'"
    assert rx.search("GSK opens unit") and not rx.search("gsk opens unit")
    assert rx.flags & 2 == 0
    # Title-case short single token also accepted
    rx, _ = m.pattern_for("Sony")                  # 4 chars -> not the acronym branch
    assert "case-sensitive" not in (m.pattern_for("Sony")[1] or "")
    rx2, note2 = m.pattern_for("Tata")
    assert rx2 is not None


def test_pattern_for_multi_token_matches_phrase_and_distinctive_first(m):
    rx, note = m.pattern_for("Suzuki Motor Corp")
    assert note is None
    assert rx.search("Maruti SUZUKI expands") and rx.search("Suzuki  Motor plant")
    rx, note = m.pattern_for("Food Empire Holdings")
    assert note == "phrase-only (generic first token 'Food')"
    assert rx.search("Food Empire MoU") and not rx.search("street food festival")
    # first-token below MIN_CORE not used alone
    rx, _ = m.pattern_for("Hon Hai Precision")
    assert not rx.search("Hon'ble Minister") and rx.search("Hon Hai Precision invests")


def test_pattern_for_aliases(m):
    rx, note = m.pattern_for("Saudi Basic Industries (SABIC)")
    assert rx.search("SABIC signs MoU") and rx.search("saudi basic industries")
    assert note == "phrase-only (generic first token 'Saudi')"
    rx, _ = m.pattern_for("Zenith Corp (Eli)")                     # alias shorter than MIN_CORE not added
    assert not rx.search("Eli Lilly")


def test_pattern_for_single_distinctive_token(m):
    rx, note = m.pattern_for("Reliance Industries")
    assert rx.search("Reliance announces")
    rx, note = m.pattern_for("Nestle SA")
    assert note is None and rx.search("Nestle India")


def _setup(root, tmp_path, leads, releases):
    mod = load_script("pib_visibility", root)
    mod.ROOT = str(root)
    db = tmp_path / "pib.sqlite"
    con = sqlite3.connect(db)
    con.execute("create table pib_items(id integer, date text, ministry text, title text)")
    con.executemany("insert into pib_items values(?,?,?,?)", releases)
    con.commit()
    con.close()
    mod.DB = str(db)
    (root / "layers/16_leads.json").write_text(json.dumps({"leads": leads}))
    return mod


def lead(company, intent=None, score=50, country="Japan", sector="Auto", ticker=None):
    d = {"company": company, "country": country, "sector": sector, "lead_score": score}
    if ticker:
        d["ticker"] = ticker
    if intent:
        d["india_apac_interest"] = {"level": intent}
    return d


def test_main_buckets_and_ordering(fake_repo, tmp_path, monkeypatch, capsys):
    releases = [
        (1, "2024-01-01", "Min A", "Alpha Motors inaugurates plant in Gujarat"),
        (2, "2024-02-01", "Min B", "Alpha Motors MoU for new factory"),
        (3, "2024-03-01", "Min C", "Beta Works chief calls on Minister"),         # mention only
        (4, "2022-01-01", "Min D", "Gamma Steelworks historic MoU"),              # before window
        (5, "2023-07-21", "Min E", "Kappa Foods expansion crore"),                # exactly window start: recent
        (6, "2023-07-20", "Min F", "Epsilon Chemicals crore invest"),             # one day before window
        (7, "2025-05-01", "Min G", "Zeta Industrial invests billion"),
        (8, "2025-06-01", "Min G", "Zeta Industrial invests again"),
    ]
    leads = [lead("Alpha Motors Ltd", "HIGH", 70, ticker="ALP"), lead("Beta Works Inc", "MEDIUM", 60),
             lead("Gamma Steelworks Corp", "HIGH", 80), lead("Kappa Foods Ltd", "HIGH", 55),
             lead("Epsilon Chemicals Co", "MEDIUM", 90), lead("Quiet Systems Ltd", "HIGH", 40),
             lead("Quiet Two Ltd", "HIGH", 85), lead("Quiet Three Ltd", "MEDIUM", 99),
             lead("Zeta Industrial Ltd", "HIGH", 10), lead("Astra Corp", "HIGH", 77), lead("Low Intent Ltd", "LOW", 99)]
    mod = _setup(fake_repo, tmp_path, leads, releases)
    monkeypatch.setattr(sys, "argv", ["x"])
    mod.main()
    doc = json.load(open(fake_repo / "layers/19_pib_visibility.json"))
    by = {r["company"]: r for r in doc["all"]}
    assert by["Alpha Motors Ltd"]["visibility"] == "ANNOUNCED"
    assert by["Alpha Motors Ltd"]["pib_investment_hits_3y"] == 2 and by["Alpha Motors Ltd"]["ticker"] == "ALP"
    assert by["Beta Works Inc"]["visibility"] == "MENTIONED_ONLY" and by["Beta Works Inc"]["pib_hits_3y"] == 1
    assert by["Beta Works Inc"]["releases"][0]["investment_related"] is False
    assert by["Gamma Steelworks Corp"]["visibility"] == "HISTORIC" and by["Gamma Steelworks Corp"]["pib_hits_before"] == 1
    assert by["Kappa Foods Ltd"]["visibility"] == "ANNOUNCED"       # window start inclusive
    assert by["Epsilon Chemicals Co"]["visibility"] == "HISTORIC"           # day before the window
    assert by["Quiet Systems Ltd"]["visibility"] == "BELOW_RADAR"
    assert by["Astra Corp"]["visibility"] == "UNMATCHABLE" and "pib_hits_3y" not in by["Astra Corp"]
    assert doc["counts"] == {"ANNOUNCED": 3, "BELOW_RADAR": 4, "HISTORIC": 2, "MENTIONED_ONLY": 1, "UNMATCHABLE": 1}
    # below radar: graded only; HIGH before MEDIUM, then score desc
    assert [r["company"] for r in doc["below_radar"]] == ["Quiet Two Ltd", "Quiet Systems Ltd", "Quiet Three Ltd"]
    assert "Low Intent Ltd" not in [r["company"] for r in doc["below_radar"]]
    # announced: most investment headlines first
    assert [r["company"] for r in doc["announced"]][0] == "Alpha Motors Ltd"
    assert doc["register"] == "8 PIB releases, 6 in window"
    # releases carry the last five investment hits only
    assert [r["prid"] for r in by["Alpha Motors Ltd"]["releases"]] == [1, 2]
    out = capsys.readouterr().out
    assert "register 8 releases (6 in 3y window)" in out
    assert "  ANNOUNCED    3" in out
    assert "graded (HIGH/MEDIUM intent): 10 ->" in out
    assert "LOUDEST" in out and "QUIETEST" in out and "--- audit" not in out


def test_main_audit_flag_and_release_cap(fake_repo, tmp_path, monkeypatch, capsys):
    releases = [(i, f"2024-0{i}-01", f"Ministry {i}", f"Omega Works invests unit {i}") for i in range(1, 8)]
    mod = _setup(fake_repo, tmp_path, [lead("Omega Works Ltd", "HIGH")], releases)
    monkeypatch.setattr(sys, "argv", ["x", "--audit"])
    mod.main()
    doc = json.load(open(fake_repo / "layers/19_pib_visibility.json"))
    rel = doc["all"][0]["releases"]
    assert [r["prid"] for r in rel] == [3, 4, 5, 6, 7]       # last five only
    out = capsys.readouterr().out
    assert "--- audit: sample matched titles ---" in out
    assert "Omega Works Ltd (7 investment hits)" in out
    assert out.count("Omega Works invests unit") == 3        # last three printed in the audit
