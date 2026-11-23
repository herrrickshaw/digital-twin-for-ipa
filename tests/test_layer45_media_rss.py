import json
import sqlite3

import pytest

from conftest import copy_script, load_script

RSS = """<?xml version="1.0"?><rss><channel>
<item><title><![CDATA[Zorbex Industries to invest Rs 500 crore in Pune plant]]></title>
<description><![CDATA[Expansion by Zorbex Industries]]></description>
<link>https://news.example/a1</link><pubDate>Mon, 02 Nov 2026</pubDate></item>
<item><title>Weather is nice today</title><description>no intent</description>
<link>https://news.example/a2</link><pubDate>Tue, 03 Nov 2026</pubDate></item>
<item><title>Zorbex Industries invests again</title><link>https://news.example/a1</link></item>
<item><title>Qwerty Motors JV announced</title><description></description>
<link>https://news.example/a3</link><pubDate>Wed, 04 Nov 2026</pubDate></item>
<item></item>
</channel></rss>"""

ARTICLE = ('<html><script>{"articleBody": "Zorbex will invest \\u20b9500 crore &amp; hire", "x": 1}</script></html>')


@pytest.fixture
def l45(fake_repo, monkeypatch):
    home = fake_repo / "home"
    uni = home / "repos" / "global-stock-screener" / "data" / "global_universe"
    uni.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    (uni / "US.csv").write_text(
        "name,yf_ticker,exchange\n"
        "Zorbex Industries Inc,ZRB,NYSE\n"
        "Qwerty Motors Ltd,QWM,NYSE\n"
        "Launch Two Acquisition Corp,LTWO,NYSE\n"          # SPAC noise
        "Hong Kong Ferry,HKF,HKEX\n"
        "Hong Kong Robotics,HKR,HKEX\n"
        "Hong Kong Exchanges,HKE,HKEX\n")
    (uni / "ZZ.csv").write_text("name,yf_ticker,exchange\nIgnored Co,I,X\n")  # not a roster country
    (fake_repo / "layers" / "16_leads.json").write_text(json.dumps({"leads": [{"company": " Zorbex Industries "}]}))
    mod = load_script("build_layer45_media_rss_sweep", fake_repo)
    return mod


def test_strip_cdata(l45):
    assert l45.strip_cdata("<![CDATA[ hi ]]>") == "hi"
    assert l45.strip_cdata("  plain ") == "plain"
    assert l45.strip_cdata(None) == ""
    assert l45.strip_cdata("<![CDATA[multi\nline]]>") == "multi\nline"


def test_parse_feed(l45):
    items = l45.parse_feed(RSS)
    assert len(items) == 5
    assert items[0] == {"title": "Zorbex Industries to invest Rs 500 crore in Pune plant",
                        "description": "Expansion by Zorbex Industries",
                        "link": "https://news.example/a1", "pubDate": "Mon, 02 Nov 2026"}
    assert items[2]["description"] == "" and items[2]["pubDate"] == ""
    assert items[4] == {"title": "", "description": "", "link": "", "pubDate": ""}


def test_extract_body_json_ld(l45):
    assert l45.extract_body(ARTICLE) == "Zorbex will invest ₹500 crore & hire"


def test_extract_body_contentbody_paragraphs(l45):
    page = ('<div class="x contentbody y"><p>One <b>two</b></p><p> three &amp; four </p>'
            '<div class="share-box">skip</div><p>after</p></div>')
    assert l45.extract_body(page) == "One two three & four"


def test_extract_body_contentbody_stops_at_script_and_ignores_lookalike(l45):
    page = '<div class="contentbody"><p>A</p><script>x</script><p>B</p></div>'
    assert l45.extract_body(page) == "A"
    assert l45.extract_body('<div class="mycontentbodyx"><p>A</p><script>') == ""
    assert l45.extract_body("<html>nothing</html>") == ""


def test_extract_body_bad_unicode_escape_falls_back(l45):
    # invalid \u escape -> decode error -> raw (unescaped) text returned
    assert l45.extract_body('"articleBody": "bad \\u12 &amp; x", ') == "bad \\u12 & x"


def test_strong_fragment_ok_boundaries(l45):
    assert l45.strong_fragment_ok("acme corp", 2) is True
    assert l45.strong_fragment_ok("acme corp", 3) is False   # shared by 3 companies
    assert l45.strong_fragment_ok("bank of", 1) is False     # 'of' < 3 chars
    assert l45.strong_fragment_ok("abc def", 1) is True      # exactly 3 chars ok


def test_two_token_fragment_counts(l45):
    idx = [("hong kong ferry", {}), ("hong kong robotics", {}), ("zorbex industries", {}),
           ("zorbex", {}), ("abc", {})]
    counts = l45.two_token_fragment_counts(idx)
    assert counts["hong kong"] == 2
    assert counts["zorbex industries"] == 0 or "zorbex industries" not in counts  # full name is not counted
    assert "zorbex" not in counts  # single token is weak, not strong


def test_is_new(l45):
    known = {"zorbex industries private limited", "other"}
    assert l45.is_new("Zorbex Industries Inc", known) is False
    assert l45.is_new("Qwerty Motors Ltd", known) is True
    assert l45.is_new("Zorbex", known) is False        # weak only -> no strong fragment -> not 'new'


def test_known_names_reads_leads_and_db(l45, fake_repo):
    con = sqlite3.connect(fake_repo / "data" / "companies.db")
    con.execute("CREATE TABLE companies(name TEXT)")
    con.executemany("INSERT INTO companies VALUES (?)", [(" ACME ",), (None,), ("",)])
    con.commit()
    con.close()
    assert l45.known_names() == {"zorbex industries", "acme"}


def test_known_names_missing_files(l45, fake_repo):
    (fake_repo / "layers" / "16_leads.json").unlink()
    assert l45.known_names() == set()


def test_load_all_rosters_only_roster_countries(l45):
    r = l45.load_all_rosters()
    assert set(r) == {"US"}
    assert r["US"][0] == {"name": "Zorbex Industries Inc", "ticker": "ZRB", "exchange": "NYSE", "country": "US"}


def test_sh_curl(l45, monkeypatch):
    import subprocess

    class P:
        stdout = "body\n200"

    seen = {}
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: seen.update(k=k, cmd=cmd) or P())
    assert l45.sh_curl("u", timeout=7) == ("200", "body")
    assert seen["k"]["timeout"] == 17 and "7" in seen["cmd"]
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: (_ for _ in ()).throw(OSError("x")))
    assert l45.sh_curl("u") == ("ERR", "x")


def test_intent_and_spac_regexes(l45):
    assert l45.INTENT_KEYWORDS.search("Firm will INVEST big")
    assert l45.INTENT_KEYWORDS.search("निवेश योजना")
    assert not l45.INTENT_KEYWORDS.search("weather today")
    assert l45.SPAC_NOISE.search("Foo Acquisition Corp")
    assert l45.SPAC_NOISE.search("Bar Class A Ordinary Shares")
    assert not l45.SPAC_NOISE.search("Classic Motors")


def _fake_fetch(l45, monkeypatch, feeds_ok):
    calls = []

    def curl(url, timeout=20):
        calls.append(url)
        if url.startswith("https://news.example/a1"):
            return "200", ARTICLE
        if url.startswith("https://news.example/"):
            return "404", ""
        return ("200", RSS) if url in feeds_ok else ("503", "")

    monkeypatch.setattr(l45, "sh_curl", curl)
    return calls


def test_main_end_to_end(l45, fake_repo, monkeypatch, capsys):
    l45.FEEDS = {"Src": {"a": "feedA", "b": "feedB"}, "Bad": {"c": "feedC"}}
    calls = _fake_fetch(l45, monkeypatch, {"feedA", "feedB"})
    arch = fake_repo / "state" / "news_articles.jsonl"
    arch.write_text("old\n")
    l45.main()
    out = json.loads((fake_repo / "layers" / "45_media_rss_sweep.json").read_text())
    assert out["layer"] == 45
    assert out["roster_companies_loaded"] == 5   # SPAC dropped
    assert out["known_twin_names"] == 1
    assert out["total_items_scanned"] == 10      # 5 items x 2 feeds
    # feedB repeats the same links -> deduped by seen_urls; a1 + a3 are intent hits once
    assert out["total_investment_intent_hits"] == 2
    a = out["by_source"]["Src"]["a"]
    assert a["items"] == 5 and a["intent_hits"] == 2 and a["error"] is None
    assert out["by_source"]["Src"]["b"]["intent_hits"] == 0
    assert out["by_source"]["Bad"]["c"]["error"] == "HTTP 503"
    ms = {m["company"]: m for m in a["matches"]}
    assert set(ms) == {"Zorbex Industries Inc", "Qwerty Motors Ltd"}
    z, q = ms["Zorbex Industries Inc"], ms["Qwerty Motors Ltd"]
    assert z["new_to_twin"] is False and q["new_to_twin"] is True
    assert z["full_text"] == "Zorbex will invest ₹500 crore & hire"
    assert q["full_text"] == ""                      # article fetch returned 404
    assert out["total_company_matches"] == 2 and out["total_new_to_twin"] == 1
    # article pages fetched only for roster-confirmed hits, once each
    assert calls.count("https://news.example/a1") == 1
    assert "https://news.example/a2" not in calls
    lines = arch.read_text().splitlines()
    assert lines[0] == "old" and len(lines) == 3
    rec = json.loads(lines[1])
    assert rec["source"] == "media_rss_sweep/Src/a" and rec["url"] == "https://news.example/a1"
    doc = (fake_repo / "docs" / "MEDIA_RSS_SWEEP.md").read_text()
    assert "## New-to-twin company matches" in doc
    assert "| Qwerty Motors Ltd | US | news.example |" in doc
    assert "| Bad | c | 0 | 0 | 0 | HTTP 503 |" in doc
    assert "[ERROR]" not in doc
    so = capsys.readouterr().out
    assert "[Bad/c] ERROR 503" in so and "Qwerty Motors Ltd (US) NEW" in so


def test_main_no_new_matches_and_no_archive_dir(l45, fake_repo, monkeypatch):
    import shutil
    shutil.rmtree(fake_repo / "state")
    l45.FEEDS = {"Src": {"a": "feedA"}}
    (fake_repo / "layers" / "16_leads.json").write_text(json.dumps({"leads": [
        {"company": "Zorbex Industries"}, {"company": "Qwerty Motors"}]}))
    _fake_fetch(l45, monkeypatch, {"feedA"})
    l45.main()
    doc = (fake_repo / "docs" / "MEDIA_RSS_SWEEP.md").read_text()
    assert "New-to-twin company matches" not in doc
    assert not (fake_repo / "state").exists()


def test_main_hong_kong_prefix_rejected(l45, fake_repo, monkeypatch):
    # 'hong kong' two-token fragment shared by 3 roster rows -> must not match prose
    l45.FEEDS = {"Src": {"a": "feedA"}}
    rss = ("<rss><item><title>Hong Kong firm to invest in India</title><description></description>"
           "<link>https://news.example/h</link><pubDate>x</pubDate></item></rss>")
    monkeypatch.setattr(l45, "sh_curl", lambda u, timeout=20: ("200", rss))
    l45.main()
    out = json.loads((fake_repo / "layers" / "45_media_rss_sweep.json").read_text())
    assert out["total_investment_intent_hits"] == 1 and out["total_company_matches"] == 0


def test_run_as_script(fake_repo, monkeypatch):
    home = fake_repo / "home"
    monkeypatch.setenv("HOME", str(home))
    copy_script(fake_repo, "enrich_company_db_ii_tickers")
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    with pytest.raises(SystemExit) as e:
        load_script("build_layer45_media_rss_sweep", fake_repo, run_name="__main__")
    assert e.value.code is None
    out = json.loads((fake_repo / "layers" / "45_media_rss_sweep.json").read_text())
    assert out["total_items_scanned"] == 0
    assert all(r["error"] == "HTTP ERR" for s in out["by_source"].values() for r in s.values())
