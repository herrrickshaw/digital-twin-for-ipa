"""Quarterly reportage builder: scheme keyword mapping, quarters, state wire, HTML views."""
import datetime
import json
import sqlite3

import pytest

from conftest import load_script

TODAY = datetime.date.today()


def iso(days_ago):
    return (TODAY - datetime.timedelta(days=days_ago)).isoformat()


@pytest.fixture(scope="module")
def m():
    return load_script("build_reportage", None)


# ---------------------------------------------------------------- pure helpers
@pytest.mark.parametrize("d,q", [("2026-01-01", "2026Q1"), ("2026-03-31", "2026Q1"), ("2026-04-01", "2026Q2"),
                                 ("2026-06-30", "2026Q2"), ("2026-07-01", "2026Q3"), ("2026-09-30", "2026Q3"),
                                 ("2026-10-01", "2026Q4"), ("2026-12-31", "2026Q4")])
def test_quarter_of(m, d, q):
    assert m.quarter_of(d) == q


@pytest.mark.parametrize("text,iso_", [
    ("notified on 05-03-2024", "2024-03-05"),
    ("dated 5/11/2023 by GR", "2023-11-05"),
    ("31.12.2025", "2025-12-31"),
    ("13-13-2024 nothing valid", None),
    ("00-05-2024", None),
    ("on 7 March 2024", "2024-03-07"),
    ("on 31 Feb 2024", "2024-02-28"),         # day clipped to 28
    ("12-Sept-2022", "2022-09-12"),
    ("5 Foo 2024", None),
    ("effective Sep-2024", "2024-09-15"),
    ("March 2023 notification", "2023-03-15"),
    ("Foo 2023", None),
    ("year 2031 only", None),                 # outside 20[12]x
    ("", None), (None, None),
])
def test_extract_date(m, text, iso_):
    assert m._extract_date(text) == iso_


def test_scheme_hits_labels_and_ministry(m):
    assert m.scheme_hits("Cabinet approves ECMS scheme") == ["ECMS"]
    assert m.scheme_hits("ECMS and Surya Ghar rooftop solar") == ["ECMS", "PM Surya Ghar"]
    assert m.scheme_hits("ECMS", with_ministry=True) == [("ECMS", "MeitY")]
    assert m.scheme_hits("nothing relevant") == [] and m.scheme_hits(None) == []


@pytest.mark.parametrize("title,expected", [
    ("PLI scheme for automobile sector", "PLI — Auto & Components"),
    ("PLI for white goods", "PLI — White Goods"),
    ("production linked incentive for drones", "PLI — Drones"),
    ("PLI textile MMF", "PLI — Textiles"),
    ("PLI scheme for bulk drug", "PLI — Pharma/MedDev"),
    ("PLI food processing", "PLI — Food Processing"),
    ("PLI for steel", "PLI — Specialty Steel"),
    ("PLI telecom", "PLI — Telecom"),
    ("PLI for IT hardware", "PLI — IT Hardware"),
    ("PLI solar", "PLI — Solar Modules"),
    ("PLI electronics", "PLI — Electronics/LSEM"),
    ("PLI scheme", "PLI (general)"),
])
def test_pli_refinement(m, title, expected):
    assert m.refine_pli("PLI (family)", title) == expected
    assert m.scheme_hits(title)[0] == expected or expected in m.scheme_hits(title)
    assert m.refine_pli("ECMS", title) == "ECMS"       # only the generic label is refined


@pytest.mark.parametrize("title,label", [
    ("IIT (ISM) Dhanbad semiconductor lab", "India Semiconductor Mission / Semicon"),
    ("Sanchar Mitra launched", "PM MITRA / textiles PLI"),
    ("CCI approves AIF acquisition", "Agriculture Infrastructure Fund"),
    ("Krishi Unnati Mela inaugurated", "UNNATI 2024 (ex NEIDS)"),
])
def test_scheme_vetoes_drop_false_positives(m, title, label):
    assert label not in m.scheme_hits(title)


def test_scheme_true_positives_not_vetoed(m):
    assert "India Semiconductor Mission / Semicon" in m.scheme_hits("India Semiconductor Mission approves fab")
    assert "PM MITRA / textiles PLI" in m.scheme_hits("PM MITRA park announced")
    assert "Agriculture Infrastructure Fund" in m.scheme_hits("Agriculture Infrastructure Fund extended")
    assert m._vetoed("ECMS", "anything") is False and m._vetoed("x", None) is False


@pytest.mark.parametrize("title,bucket", [
    ("Gujarat signs MoU with firm", "investment"),
    ("Rs 500 crore plant to be set up", "investment"),
    ("CM inaugurated the highway", "projects"),
    ("foundation stone laid", "projects"),
    ("New industrial policy notified", "regulation"),
    ("Stamp duty exemption", "regulation"),
    ("Weather report", None), ("", None), (None, None),
    # earlier bucket wins when several match: investment before regulation
    ("Policy offers incentive", "investment"),
])
def test_classify_state_row(m, title, bucket):
    assert m.classify_state_row(title) == bucket


# ---------------------------------------------------------------- state wire
def make_state_db(path, rows, with_title_en=True):
    con = sqlite3.connect(path)
    cols = "state text, date text, title text, category text, url text" + (", title_en text" if with_title_en else "")
    con.execute(f"create table state_news({cols})")
    for r in rows:
        if with_title_en:
            con.execute("insert into state_news values(?,?,?,?,?,?)", r)
        else:
            con.execute("insert into state_news values(?,?,?,?,?)", r[:5])
    con.commit()
    con.close()


def test_state_wire_filters_cutoff_and_translates(m, tmp_path, monkeypatch):
    db = tmp_path / "s.sqlite"
    make_state_db(db, [
        ("MP", iso(2), "native", "cat", "http://u1", "ECMS scheme state support"),       # scheme hit, title_en used
        ("GJ", iso(3), "Gujarat investors summit planned", None, None, None),             # signal only
        ("ZZ", iso(4), "random news", "c", "u", "weather"),                               # neither -> dropped
        ("UP", iso(40), "ECMS old", "c", "u", None),                                      # older than 30d
        ("XX", iso(1), "PLI scheme for auto", "c", "u", None),                            # unknown state code kept
    ])
    monkeypatch.setattr(m, "STATE_DB", str(db))
    rows = m.state_wire()
    assert [r["state"] for r in rows] == ["Unknown" if False else "XX", "Madhya Pradesh", "Gujarat"]
    mp = rows[1]
    assert mp["title"] == "ECMS scheme state support" and mp["schemes"] == ["ECMS"]
    gj = rows[2]
    assert gj["category"] == "" and gj["url"] == "" and gj["schemes"] == []
    assert len(m.state_wire(days=60)) == 4
    assert len(m.state_wire(days=0)) == 0


def test_state_wire_without_title_en_and_missing_db(m, tmp_path, monkeypatch):
    db = tmp_path / "s2.sqlite"
    make_state_db(db, [("MP", iso(1), "ECMS native title", "c", "u")], with_title_en=False)
    monkeypatch.setattr(m, "STATE_DB", str(db))
    assert [r["title"] for r in m.state_wire()] == ["ECMS native title"]
    monkeypatch.setattr(m, "STATE_DB", str(tmp_path / "nope.sqlite"))
    assert m.state_wire() == []


# ----------------------------------------------------------------- full build
TEMPLATE = "<html>__ROWS__|__STATES__|__TOTAL__|__NQ__|__GEN__|__POLICY__</html>"


@pytest.fixture
def world(fake_repo, tmp_path, monkeypatch):
    mod = load_script("build_reportage", fake_repo)
    mod.ROOT = str(fake_repo)
    mod.STATE_DB = str(fake_repo / "data/registers/state_news.sqlite")
    (fake_repo / "data/registers").mkdir(parents=True)
    pib = tmp_path / "pib.sqlite"
    con = sqlite3.connect(pib)
    con.execute("create table pib_items(id integer, date text, ministry text, title text)")
    rows = [
        (1, "2025-01-15", "Ministry of Electronics", "ECMS guidelines notified | with pipe"),
        (2, "2025-02-10", None, "Cabinet approves ECMS | outlay"),
        (3, "2025-02-11", "Cabinet", "Cabinet approves ropeway project with incentive"),   # unmapped cabinet
        (4, "2025-03-01", "Other Ministry", "Unrelated press note"),                         # dropped
        (5, "2025-04-02", "Heavy Industries", "PM E-DRIVE extended"),
        (6, iso(5), "Power", "RDSS extension approved"),
        (7, iso(4), "Cabinet", "Cabinet approves new capital outlay for roads"),
        (8, iso(3), "Textiles", "PLI scheme for textile sector"),
        (9, iso(2), "Textiles", "PLI scheme for textile MMF second tranche"),
    ]
    con.executemany("insert into pib_items values(?,?,?,?)", rows)
    con.commit()
    con.close()
    mod.DB = str(pib)
    make_state_db(mod.STATE_DB, [
        ("MP", iso(3), "Industrial park MoU signed", "Industry", "http://state/1", None),
        ("RJ", iso(40), "Policy notified", "Gov", "", None),
        ("MP", iso(2), "Foundation stone laid for ECMS fab", None, "", "ECMS fab foundation stone laid"),
    ])
    docs = fake_repo / "docs"
    (docs / "_reportage_template.html").write_text(TEMPLATE)
    (docs / "_reportage_ministry_template.html").write_text(TEMPLATE)
    return mod, fake_repo


def test_main_markdown(world, capsys):
    mod, root = world
    mod.CAP_PER_QUARTER = 1
    mod.main()
    md = (root / "docs/REPORTAGE.md").read_text()
    # quarters sorted newest first
    qs = [l.split(" — ")[0][3:] for l in md.splitlines() if l.startswith("## ")]
    assert qs == sorted(qs, reverse=True) and "2025Q1" in qs and "2025Q2" in qs
    assert "## 2025Q1 — 2 scheme-mapped announcements" in md
    assert "## 2025Q2 — 1 scheme-mapped announcements" in md
    # cap of 1 per quarter: second Q1 row hidden and counted honestly; Q2 (n == cap) has no note
    assert md.count("further scheme-mapped rows not shown") == 2          # 2025Q1 (2 rows) and current quarter (3 rows)
    assert "*1 further scheme-mapped rows not shown (cap 1)" in md
    assert "*2 further scheme-mapped rows not shown (cap 1)" in md
    # first row is shown with pipes in the title escaped for the markdown table
    assert ("| 2025-01-15 | **ECMS** | Ministry of Electronics | ECMS guidelines notified / with pipe | "
            "[1](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1) |") in md
    assert "outlay" not in md.split("## 2025Q1")[1].split("<details>")[0]      # row 2 hidden by the cap
    assert "Other Cabinet/CCEA approvals this quarter (1)" in md
    assert "- 2025-02-11 · Cabinet approves ropeway project with incentive · [3](" in md
    assert "Unrelated press note" not in md
    out = capsys.readouterr().out
    assert "reportage: 6 scheme-mapped announcements across" in out
    assert "reportage html:" in out and "reportage ministry html:" in out
    assert "reportage latest html:" in out and "reportage states html:" in out


def test_main_cap_default_is_30(world):
    mod, root = world
    assert mod.CAP_PER_QUARTER == 30


def test_main_html_outputs(world):
    mod, root = world
    mod.main()
    docs = root / "docs"
    h = (docs / "reportage.html").read_text()
    assert h.startswith("<html>") and "__ROWS__" not in h and "__POLICY__" not in h
    assert 'data-q="2025Q1"' in h and "PRID 1" in h and 'data-st="Central"' in h
    assert "(0 state)" in h
    ministry = (docs / "reportage_ministry.html").read_text()
    assert 'data-min="MeitY"' in ministry
    latest = (docs / "reportage_latest.html").read_text()
    assert "Latest Updates" in latest
    # only rows inside the 30 day window: PRIDs 6, 8, 9 are recent central items; 7 is unmapped cabinet
    assert "PRID=6" in latest and "PRID=8" in latest and "PRID=9" in latest and "PRID=7" in latest
    assert "PRID=1\"" not in latest and "PRID=5\"" not in latest
    assert "Industrial park MoU signed" in latest
    # stale RJ row (40 days) is excluded from the latest page
    assert "Policy notified" not in latest
    states = (docs / "reportage_states.html").read_text()
    assert "Industrial park MoU signed" in states and "Policy notified" in states   # whole register
    assert "<b>Investment & MoUs</b>" in states and "<b>New projects & inaugurations</b>" in states
    assert 'class="chip">ECMS</span>' in states


def test_write_html_states_missing_db(world, tmp_path, capsys):
    mod, root = world
    mod.STATE_DB = str(tmp_path / "gone.sqlite")
    mod.write_html_states()
    assert "state register missing -- skipping states html" in capsys.readouterr().out
    assert not (root / "docs/reportage_states.html").exists()


def test_write_html_latest_window_and_dedup(world):
    mod, root = world
    rows = [(1, iso(5), "Min", "ECMS news"), (1, iso(5), "Min", "ECMS news"),
            (2, iso(40), "Min", "ECMS old"), (3, None, "Min", "ECMS nodate"),
            (4, iso(2), "Cabinet", "Cabinet approves incentive"), (5, iso(2), None, "nothing")]
    mod.write_html_latest(rows, register_total=123, days=30)
    h = (root / "docs/reportage_latest.html").read_text()
    # schemes section counts unique PRIDs per scheme
    assert h.count("PRID=1") == 1
    assert "PRID=2" not in h and "PRID=3" not in h
    assert "PRID=4" in h
    assert "123 releases" in h
    assert "<b>1</b><span>central announcements</span>" in h
    assert "<b>1</b><span>unmapped Cabinet/CCEA</span>" in h


def test_state_announcements_and_states_view(world):
    mod, root = world
    l12 = root / "layers/12_state_catalog"
    l12.mkdir()
    (l12 / "gj.json").write_text(json.dumps({"states": [{"state": "GUJARAT", "policies": [
        {"name": "Semicon Policy", "status": "Notified 05-03-2024", "site_url": "http://g"},
        {"name": "Old Policy", "status": "Notified 05-03-2015"},          # before 2017 -> dropped
        {"name": "Undated"}]}]}))
    (l12 / "ocr_extracts.json").write_text(json.dumps({"states": [{"state": "X", "policies": [
        {"name": "Skipped", "status": "05-03-2024"}]}]}))
    (root / "layers/18_state_monitor.json").write_text(json.dumps({
        "headline_findings": ["Headline <one>"],
        "states": [{"state": "GUJARAT", "schemes": [
            {"scheme": "S1", "status_2025_26": "arrears pending", "funds_evidence": [
                {"date": "12 Jan 2025", "figure": "Rs 5 cr", "fact": "paid", "source_url": "http://src",
                 "source_type": "news"},
                {"date": "12 Jan 2025", "figure": "UNVERIFIED 3", "fact": "x"},        # skipped
                {"date": "12 Jan 2025", "figure": "", "fact": "no figure"}],            # skipped
             "news_articles": [{"url": "http://n", "outlet": "Hindu", "date": "2025-01-01T00:00"}]}]}]}))
    rows = mod.state_announcements()
    assert sorted(r["scheme"] for r in rows) == ["S1", "Semicon Policy"]
    sp = next(r for r in rows if r["scheme"] == "Semicon Policy")
    assert sp["date"] == "2024-03-05" and sp["state"] == "Gujarat" and sp["url"] == "http://g"
    s1 = next(r for r in rows if r["scheme"] == "S1")
    assert s1["detail"] == "Rs 5 cr -- paid" and s1["date"] == "2025-01-12"
    html = mod.render_states()
    assert "Headline &lt;one&gt;" in html and "2 catalogued instruments" not in html
    assert "3 catalogued instruments" in html           # layer 12: 3 policies listed for GUJARAT
    assert "arrears signal" in html
    assert 'href="http://src"' in html and "[news]" in html
    assert "Hindu (2025-01-01)" in html


def test_render_states_missing_layer(world):
    mod, root = world
    assert mod.render_states() == "<p>(state monitor layer not built)</p>"
    assert mod.state_announcements() == []


def test_policy_annex_and_up_ethanol(world):
    mod, root = world
    assert mod.render_policy_annex() == "" and mod.render_up_ethanol() == ""
    (root / "layers/24c_cross_verification.json").write_text(json.dumps({"companies": [
        {"company": "Small & Co", "ec_register": {"filings": 1}, "news_verdict": "QUIET"},
        {"company": "Big", "ec_register": {"filings": 9}, "fc_register": {"filings": 2},
         "pib_headlines": {"headlines": 4}, "iem_partB_sample": True, "state_govt_announcement": True,
         "pli_ebp_register": True, "credit_rating_public": True, "ibef": True,
         "news_verdict": "PARTIALLY_VISIBLE"},
        {"company": "NoIbef", "ibef": False, "news_verdict": "ANNOUNCED"},
        {"company": "Unchecked"},
    ]}))
    (root / "layers/24d_up_ethanol.json").write_text(json.dumps({
        "up_context": "ctx <b>", "register_aggregates": {"up_5g_proposals_total": 50, "live": 30, "unique_companies": 20},
        "companies": [{"company": "Dist1", "district": "D", "capacity": "100 KLPD", "feedstock": "grain",
                       "capex_rs_cr": 1234.6, "status": "QUIET builder", "note": "n"},
                      {"company": "Dist2", "district": "E", "capacity": "c", "feedstock": "f",
                       "capex_rs_cr": 0, "status": "ANNOUNCED", "note": "m"}]}))
    html = mod.render_policy_annex()
    order = [html.index(n) for n in ("Big", "Small &amp; Co", "NoIbef")]
    assert order == sorted(order)                           # by total filings desc
    assert 'class="cn">Small &amp; Co</td><td class="cv y">1</td>' in html
    assert '<td class="cv q">Quiet</td>' in html and '<td class="cv p">Partially Visible</td>' in html
    assert '<td class="cv y">✓</td>' in html and 'style="opacity:.3">·</td>' in html
    assert "ctx &lt;b&gt;" in html and "&#8377;1,235 cr" in html and "<b>50 UP distillery (5(g)) proposals</b>" in html
    assert '<td class="cv q">QUIET builder</td>' in html and '<td class="cv y">ANNOUNCED</td>' in html
    assert "—" in html
