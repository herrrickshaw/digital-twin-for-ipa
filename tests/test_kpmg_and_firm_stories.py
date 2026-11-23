"""KPMG JP/KR leads, firm client story collector and matcher (script-style modules)."""
import csv
import json
import os

import pytest

from _fakes import completed
from conftest import copy_script, load_script

WORKBOOK = """## Sheet: Korea DART Audit Clients
Stock Code | Company (Korean) | Audit Opinion
5930 | 삼성전자 | Unqualified
999999 | 제약회사 | Unqualified

## Sheet: Japan EDINET Audit Clients
Stock Code | Company (English) | Company (Japanese) | KPMG Office (Azusa LLC) | Market Segment | Sector
72030 | Toyota Motor | トヨタ | Nagoya | Prime | Transport equipment
99990 | (not matched) | 製薬会社 | Tokyo | Standard | Misc

## Sheet: KPMG Client Stories
Country / Firm | Named Client | Client | Title | URL | Sector
Japan | Yes | Toyota Motor | A very long client story title | http://s/1 | Auto
South Korea | Yes | Hyundai | Story2 | http://s/2 | Chemicals
Germany | Yes | Siemens | Story3 | http://s/3 | Electronics
Japan | No | Anon | Story4 | http://s/4 | Auto
"""


def test_kpmg_leads(fake_repo, tmp_path, monkeypatch):
    copy_script(fake_repo, "build_leads")
    home = tmp_path / "home"
    univ = home / "repos/global-stock-screener/data/global_universe"
    univ.mkdir(parents=True)
    (univ / "KR.csv").write_text("yf_ticker,name\n005930.KS,Samsung Electronics\n", encoding="utf-8")
    (univ / "JP.csv").write_text("yf_ticker,name\n7203.T,Toyota\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    wb = tmp_path / "wb.md"
    wb.write_text(WORKBOOK, encoding="utf-8")
    quotes = tmp_path / "q.csv"
    quotes.write_text(
        "market,yf_ticker,roe,opm,market_cap\n"
        "korea,005930.KS,0.1,0.2,100\n"
        "japan,7203.T,-0.1,0.05,50\n"
        "us,AAPL,1,1,1\n", encoding="utf-8")
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(
        a, 0, "005930\tTechnology\tSemiconductors\nbad line\n", ""))
    out = tmp_path / "out"
    load_script("build_kpmg_jp_kr_leads", fake_repo, argv=[str(wb), str(quotes), str(out)])
    rows = list(csv.DictReader(open(out / "kpmg_jp_kr_leads.csv", encoding="utf-8")))
    by = {r["company"]: r for r in rows}
    assert [r["rank"] for r in rows] == [str(i) for i in range(1, len(rows) + 1)]
    scores = [int(r["lead_score"]) for r in rows]
    assert scores == sorted(scores, reverse=True)
    sam = by["Samsung Electronics"]
    # 40 base + 15 (roe>0) + 15 (opm>0) + 20 (lane found: Electronics & Semiconductors)
    assert sam["lead_score"] == "90" and sam["focus_sector"] == "Electronics & Semiconductors"
    assert sam["ticker"] == "005930.KS" and sam["market"] == "Korea"
    assert sam["roe"] == "0.1" and sam["sector_src"] == "Technology"
    assert "ECMS" in sam["central_lanes"]
    toy = by["Toyota Motor"]
    # roe negative -> no +15; opm positive +15; lane Auto: 40+0+15+20 = 75, then merged with the
    # client-story row (45): max(75, 45) + 5
    assert toy["lead_score"] == "80" and toy["focus_sector"] == "Auto, EV & Components"
    assert toy["ticker"] == "7203.T" and toy["market"] == "Japan"
    # Japanese stock code "99990" (5 chars) -> trimmed to 9999; name falls back to Japanese when '(not matched'
    jp = by["製薬会社"]
    assert jp["focus_sector"] == "Pharma & Bulk Drugs" and jp["sector_src"] == "name-inferred"
    assert jp["ticker"] == "9999" and jp["roe"] == ""
    # Korean stock code zero-padded
    kr = by["제약회사"]
    assert kr["ticker"] == "999999" and kr["focus_sector"] == "Pharma & Bulk Drugs"
    # client stories: only named JP/KR; Germany and unnamed skipped
    assert "Siemens" not in by and "Anon" not in by
    hy = by["Hyundai"]
    assert hy["lead_score"] == "45" and hy["market"] == "Korea" and hy["note"] == "http://s/2"
    assert hy["focus_sector"] == "Chemicals & Plastics"
    # Toyota listed twice (audit + story): merged links, score = max + 5
    assert " + KPMG client story: A very long client story title" in toy["kpmg_link"]


def test_firm_stories_collector_resume_and_blocking(tmp_path, monkeypatch, capsys):
    import subprocess
    import time
    urls = tmp_path / "urls.txt"
    urls.write_text("\n".join([
        "https://www.deloitte.com/uk/en/case-study-a",
        "https://www.deloitte.com/uk/en/case-study-b",
        "https://www.accenture.com/us-en/case-c",
        "https://www.bdo.com/work/d",
        "https://www.ey.com/blog/skipme",
        "https://www.ey.com/careers/skipme2",
        "https://www.ey.com/e",
        "https://www.ey.com/already-done",
        "", ]), encoding="utf-8")
    out = tmp_path / "out.csv"
    out.write_text("firm,region,url,title,description,status\n"
                   "ey,us,https://www.ey.com/already-done,t,d,200\n", encoding="utf-8")
    calls = []
    page_ok = ('<html><head><meta property="og:title" content="A &amp; B Story">'
               '<meta content="Nice desc" name="description"></head></html>')
    def fake_run(cmd, **kw):
        u = cmd[-1]
        calls.append(u)
        if "deloitte.com/uk/en/case-study-a" in u:
            return completed((page_ok + "\n200").encode())
        if "deloitte" in u:      # unreachable if host blocked after 403... first is 200
            return completed(b"\n403")
        if "accenture" in u:
            return completed(b"<title>Plain Title</title>\n200")
        if "bdo" in u:
            return completed(b"\n403")
        return completed(b"\n429")
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    load_script("collect_firm_client_stories", None, argv=[str(urls), str(out)])
    rows = list(csv.DictReader(open(out, encoding="utf-8")))
    by = {r["url"]: r for r in rows}
    assert "https://www.ey.com/blog/skipme" not in by and "https://www.ey.com/careers/skipme2" not in by
    a = by["https://www.deloitte.com/uk/en/case-study-a"]
    assert (a["firm"], a["region"], a["status"]) == ("deloitte", "uk", "200")
    assert a["title"] == "A & B Story" and a["description"] == "Nice desc"
    # deloitte b is a 403 -> recorded then host blocked (no further deloitte calls)
    assert by["https://www.deloitte.com/uk/en/case-study-b"]["status"] == "403"
    ac = by["https://www.accenture.com/us-en/case-c"]
    assert ac["region"] == "us-en" and ac["title"] == "Plain Title"
    bdo = by["https://www.bdo.com/work/d"]
    assert bdo["region"] == "us" and bdo["status"] == "403"
    assert by["https://www.ey.com/e"]["status"] == "429"
    # already-done URL not re-fetched; header not duplicated
    assert "https://www.ey.com/already-done" not in calls
    assert open(out, encoding="utf-8").read().count("firm,region,url") == 1
    assert "blocked deloitte 403 -- stopping this host" in capsys.readouterr().out


def test_firm_stories_collector_blocked_host_skips_rest(tmp_path, monkeypatch):
    import subprocess
    import time
    urls = tmp_path / "u.txt"
    urls.write_text("https://www.bdo.com/1\nhttps://www.bdo.com/2\n", encoding="utf-8")
    out = tmp_path / "o.csv"
    n = []
    monkeypatch.setattr(subprocess, "run", lambda c, **k: (n.append(c[-1]), completed(b"\n403"))[1])
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    load_script("collect_firm_client_stories", None, argv=[str(urls), str(out)])
    assert n == ["https://www.bdo.com/1"]


def test_match_firm_stories(fake_repo):
    p = fake_repo / "private_kpmg"
    p.mkdir()
    json.dump({"leads": [
        {"company": "Acme Widgets Ltd", "sector": "Chem"},
        {"company": "Energy Inc", "sector": "X"},          # single generic word -> dropped
        {"company": "Zymurgy Corp", "sector": "Food"},     # distinctive single token (>=6) kept
        {"company": "Shorty SA", "sector": "Y"},           # single token < 6 chars -> dropped
    ]}, open(fake_repo / "layers/16_leads.json", "w"))
    (p / "kpmg_jp_kr_leads.csv").write_text(
        "company,market,focus_sector\nKorea Zinc,Korea,\nToyota Motor,Japan,Auto\n", encoding="utf-8")
    hdr = "firm,region,url,title,description,status\n"
    (p / "firm_client_stories.csv").write_text(hdr + "\n".join([
        "deloitte,uk,https://x/acme-widgets-story,How Acme Widgets scaled,,200",
        "bdo,us,https://x/a,Zymurgy Corporation case,desc,200",
        "ey,us,https://x/b,About Our Acme Widgets,desc,200",          # title prefix skipped
        "ey,us,https://x/c,Corporate Sustainability for Acme Widgets,,200",
        "ey,us,https://x/d,Acme Widgets,,404",                        # non-200 skipped
        "ey,us,https://x/e,energy matters,,200",
        "ey,us,https://x/f,Toyota Motor and Korea Zinc,,200",
        "ey,us,https://x/g,Acme Widgetsx,,200",                        # no word boundary
    ]) + "\n", encoding="utf-8")
    load_script("match_firm_stories_to_leads", fake_repo)
    rows = list(csv.DictReader(open(p / "firm_stories_lead_matches.csv", encoding="utf-8")))
    got = sorted((r["url"], r["matched_company"]) for r in rows)
    assert got == sorted([
        ("https://x/acme-widgets-story", "Acme Widgets Ltd"),
        ("https://x/a", "Zymurgy Corp"),
        ("https://x/f", "Toyota Motor"),
        ("https://x/f", "Korea Zinc"),
    ])
    ctx = {r["matched_company"]: r["lead_context"] for r in rows}
    assert ctx["Acme Widgets Ltd"] == "twin lead (Chem)"
    assert ctx["Toyota Motor"] == "KPMG-audited Japan (Auto)"
    assert ctx["Korea Zinc"] == "KPMG-audited Korea (no lane)"
