"""layer 41: cross-reference exhibitor / member rosters against companies already tracked."""
import csv
import json
import sqlite3

import pytest

from conftest import copy_script, load_script


@pytest.fixture
def mod(fake_repo, tmp_path):
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    m = load_script("build_layer41_association_leads_crossref", fake_repo)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    m.SCRATCH = str(scratch)
    return m, fake_repo, scratch


@pytest.mark.parametrize("name,expected", [
    ("Royal Netherlands Embassy", False), ("High Commission of Canada", False), ("Trade Commissioner Office", False),
    ("Sweden Chamber of Commerce", False), ("Trade & Investment Queensland", False), ("Investment and Trade Korea", False),
    ("Government Trade Office", False), ("Export Promotion Council", False),
])
def test_non_company_bodies_never_new(mod, name, expected):
    m, *_ = mod
    assert m.is_new(name, set()) is expected


def test_is_new_logic(mod):
    m, *_ = mod
    known = {"zenith quiet industries limited", "other company"}
    assert m.is_new("Brand New Systems", known) is True
    assert m.is_new("Zenith Quiet Industries", known) is False          # strong fragment appears in a known name
    assert m.is_new("Zenith Quiet", known) is False                      # first-two-token fragment on a word boundary
    assert m.is_new("", known) is False and m.is_new("   ", known) is False
    assert m.is_new("AB", known) is False                                # too short to judge either way
    assert m.is_new("Brand New Systems", set()) is True


def _write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def test_known_names(mod):
    m, root, _ = mod
    assert m.known_names() == set()
    (root / "layers/16_leads.json").write_text(json.dumps({"leads": [{"company": "  Alpha Corp  "}]}))
    con = sqlite3.connect(m.DB)
    con.execute("create table companies(company_id integer, name text)")
    con.executemany("insert into companies values (?,?)", [(1, "Beta Ltd"), (2, None), (3, "")])
    con.commit()
    con.close()
    assert m.known_names() == {"alpha corp", "beta ltd"}
    # a DB without the companies table is tolerated
    import os
    os.unlink(m.DB)
    sqlite3.connect(m.DB).close()
    assert m.known_names() == {"alpha corp"}


def test_load_raw_sources_scratch_and_repo_files(mod):
    m, root, scratch = mod
    pdfs = scratch / "pdfs"
    pdfs.mkdir()
    (pdfs / "aeroindia2019_foreign.txt").write_text(
        "  1  Airbus Group*   FRANCE\nheader line\n 12  Rolls Royce plc    UNITED KINGDOM\n")
    (scratch / "semicon_india_2025_names.txt").write_text("Applied Materials\n\n  Lam Research \n")
    (pdfs / "aahar2024.txt").write_text(
        "HALL NO. 1\n 1  Hall One Foods   Poland\n 2  Another Hall One   Italy\nHALL 2 GROUND FLOOR\n 3  Hall Two Foods   Spain\n")
    (scratch / "textile_pdfs").mkdir()
    (scratch / "textile_pdfs/india_itme_2022_exhibitors.txt").write_text(
        "INTERNATIONAL   Itema SpA   Italy\nINTERNATIONAL PROCESSING\nINTERNATIONAL   AB   x\nDOMESTIC Foo\nINTERNATIONAL   WEAVING   y\n")
    tf = root / "data/trade_fairs"
    _write_csv(tf / "railways/innotrans_2026_exhibitors.csv", ["company", "country"], [["Alstom", "FR"]])
    (tf / "railways/iree_2025_key_exhibitors.json").write_text(json.dumps([
        {"company": "Siemens Mobility", "origin_flag": "FOREIGN-PARENT"},
        {"company": "Merge Artifact", "origin_flag": "FOREIGN", "possible_merge_artifact": True},
        {"company": "Indian Rail Co", "origin_flag": "INDIAN"}]))
    _write_csv(tf / "messe_frankfurt/ish_exhibitors.csv", ["name", "country_label"], [["Grohe", "Germany"], ["", "x"]])
    _write_csv(tf / "messe_duesseldorf/boot_exhibitors.csv", ["name", "country"], [["Beneteau", "France"]])
    ind = tf / "india_domestic"
    (ind / "iijs").mkdir(parents=True)
    (ind / "iijs/iijs_participants.json").write_text(json.dumps([
        {"name": "Foreign Gem", "country_or_origin": "Thailand", "origin_flag": "FOREIGN"},
        {"name": "Local Gem", "origin_flag": "INDIA"}]))
    (ind / "convergence_india").mkdir()
    (ind / "convergence_india/convergence_india_participants_foreign_only.json").write_text(json.dumps(
        {"participants": [{"name": "Huawei", "country_origin": "China"}]}))
    (ind / "iitf").mkdir()
    (ind / "iitf/iitf_participants.json").write_text(json.dumps(
        {"company_level_exhibitors": {"records": [{"name": "Pavilion Co", "country_origin": "Iran"}]}}))
    (ind / "cement_expo").mkdir()
    (ind / "cement_expo/cement_expo_participants.json").write_text(json.dumps(
        {"participants": [{"name": "Holcim", "origin_flag": "FOREIGN-PARENT"}, {"name": "Local", "origin_flag": "INDIA"}]}))
    (ind / "india_mobile_congress").mkdir()
    (ind / "india_mobile_congress/india_mobile_congress_participants.json").write_text(json.dumps(
        {"participants": [{"name": "Nokia", "country_origin": "Finland", "flag_basis": "FOREIGN HQ"},
                          {"name": "Jio", "flag_basis": "domestic"}]}))
    rows = m.load_raw_sources()
    assert [r["company"] for r in rows["Aero India 2019 (foreign exhibitors)"]] == ["Airbus Group", "Rolls Royce plc"]
    assert rows["Aero India 2019 (foreign exhibitors)"][0]["country"] == "France"
    assert rows["Aero India 2019 (foreign exhibitors)"][1]["country"] == "United Kingdom"
    assert [r["company"] for r in rows["SEMICON India 2025"]] == ["Applied Materials", "Lam Research"]
    assert [r["company"] for r in rows["AAHAR 2024 (Hall 1, foreign participation)"]] == ["Hall One Foods", "Another Hall One"]
    assert [r["company"] for r in rows["India ITME 2022 (international exhibitors)"]] == ["Itema SpA"]
    assert rows["InnoTrans 2026 (all exhibitors)"] == [{"company": "Alstom", "country": "FR"}]
    assert [r["company"] for r in rows["IREE 2025 (foreign / foreign-parent, clean subset)"]] == ["Siemens Mobility"]
    assert rows["ISH 2027 (Messe Frankfurt)"] == [{"company": "Grohe", "country": "Germany"}]
    assert rows["boot 2027 (Messe Düsseldorf)"] == [{"company": "Beneteau", "country": "France"}]
    assert rows["IIJS Bharat 2026 (foreign-flagged subset)"] == [{"company": "Foreign Gem", "country": "Thailand"}]
    assert rows["Convergence India 2026 (foreign-flagged subset)"][0]["country"] == "China"
    assert rows["IITF 2025 (International Pavilion, company-level)"] == [{"company": "Pavilion Co", "country": "Iran"}]
    assert [r["company"] for r in rows["Cement Expo 2023 (foreign / foreign-parent)"]] == ["Holcim"]
    assert [r["company"] for r in rows["India Mobile Congress 2025 (named foreign companies, lower-confidence)"]] == ["Nokia"]
    # sources whose files are absent are simply not reported
    assert not any(k.startswith("Light + Building") for k in rows)


def test_convergence_file_may_be_a_bare_list(mod):
    m, root, scratch = mod
    p = root / "data/trade_fairs/india_domestic/convergence_india"
    p.mkdir(parents=True)
    (p / "convergence_india_participants_foreign_only.json").write_text(json.dumps([{"name": "Cisco", "country_origin": "US"}]))
    assert m.load_raw_sources()["Convergence India 2026 (foreign-flagged subset)"] == [{"company": "Cisco", "country": "US"}]


def test_main_end_to_end(mod, monkeypatch, capsys):
    m, root, scratch = mod
    (root / "layers/16_leads.json").write_text(json.dumps({"leads": [{"company": "Siemens Mobility GmbH"}]}))
    (scratch / "semicon_india_2025_names.txt").write_text(
        "Siemens Mobility\nBrand New Chips Corporation\nBrand New Chips Corporation\nxy\nEmbassy of Japan\nZeta Wafer Works\n")
    monkeypatch.setattr(m, "CURATED", {"Assoc One": ["Siemens Mobility", "Totally Unknown Industries"]})
    m.main()
    out = json.load(open(m.OUT_JSON))
    semi = out["sources"]["SEMICON India 2025"]
    assert semi["total_entries"] == 6 and semi["unique"] == 4          # 'xy' (<4 chars) and the repeat are skipped
    assert [e["company"] for e in semi["flagged"]] == ["Brand New Chips Corporation", "Zeta Wafer Works"]
    cur = out["sources"]["[curated] Assoc One"]
    assert [e["company"] for e in cur["flagged"]] == ["Totally Unknown Industries"] and cur["total_entries"] == 2
    assert out["total_new_flagged"] == 3 and out["known_company_count"] == 1
    md = open(m.OUT_DOC, encoding="utf-8").read()
    assert "**3 new companies flagged**" in md and "## SEMICON India 2025 (2 new of 4 unique)" in md
    assert "| Brand New Chips Corporation | — |" in md and "Embassy of Japan" not in md
    text = capsys.readouterr().out
    assert "known company names loaded: 1" in text and "TOTAL new companies flagged: 3" in text


def test_main_truncates_long_tables_and_marks_empty(mod, monkeypatch):
    m, root, scratch = mod
    names = [f"Uniquecorp{chr(65 + i // 26)}{chr(65 + i % 26)} Holdings International" for i in range(65)]
    monkeypatch.setattr(m, "CURATED", {"Big": names, "Empty": ["Siemens Mobility"]})
    (root / "layers/16_leads.json").write_text(json.dumps({"leads": [{"company": "Siemens Mobility"}]}))
    m.main()
    md = open(m.OUT_DOC, encoding="utf-8").read()
    assert "| ...+5 more | — |" in md and md.count("Uniquecorp") == 60
    assert "## [curated] Empty (0 new of 1 unique)" in md and "*(none flagged)*" in md
