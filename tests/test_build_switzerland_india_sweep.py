"""SIX equity-issuer news sweep for India mentions: classification, roster fix, dedup and exclusion buckets."""
import csv
import datetime as dt
import json

import pytest
import requests

from _fakes import FakeResp
from conftest import load_script


@pytest.fixture(scope="module")
def m():
    return load_script("build_switzerland_india_sweep", None)


def ms(year, month, day):
    """Midday-UTC epoch milliseconds so the local-time conversion stays on the same calendar day."""
    return int(dt.datetime(year, month, day, 12, tzinfo=dt.timezone.utc).timestamp() * 1000)


# ------------------------------------------------------------------ helpers
def test_strip_html(m):
    html = "<p>Hello <b>world</b></p><script>x()</script><style>.a{}</style>&amp; &#39; done"
    assert m.strip_html(html) == "Hello world done"
    assert m.strip_html(None) == "" and m.strip_html("") == ""


def test_fingerprint(m):
    a = m.fingerprint("Acme AG", ["India expansion, now!"])
    assert a == m.fingerprint("ACME AG", ["india   expansion now"])           # case and punctuation insensitive
    assert a != m.fingerprint("Acme AG", ["India exit"]) and len(a) == 16
    assert a != m.fingerprint("Other AG", ["India expansion, now!"])


def test_india_regex(m):
    assert m.INDIA_RE.search("plant in India.") and m.INDIA_RE.search("in Indien") and m.INDIA_RE.search("en Inde")
    assert not m.INDIA_RE.search("Indiana") and not m.INDIA_RE.search("Indonesia") and not m.INDIA_RE.search("indian")


@pytest.mark.parametrize("snippet,title,tier", [
    ("Company announces exit from India", "", "exit_or_divestment"),
    ("Divestment of Indian unit in India", "", "exit_or_divestment"),
    ("The sale of the plant in India", "", "exit_or_divestment"),
    ("Opening of a new plant in India", "", "market_entry_or_investment"),
    ("establishes a subsidiary in India", "", "market_entry_or_investment"),
    ("Acquisition of a firm in India", "", "market_entry_or_investment"),
    ("Q3 revenue grew in India", "", "business_activity"),
    ("", "", "business_activity"),
    # exit beats entry
    ("expansion in India but sold the legacy site", "", "exit_or_divestment"),
    # retrospective baseline comparison is not news
    ("Revenue fell compared to the prior period, which included a major project in India, expansion", "", "business_activity"),
    # vague multi-country expansion without a concrete action
    ("further expansion in Australia, India, Japan, and Vietnam", "", "business_activity"),
    # ... unless a concrete plant/office is named
    ("further expansion in Australia, India, Japan and Vietnam with a new plant", "", "market_entry_or_investment"),
    # third party acquiring the issuer itself
    ("acquisition of the group, with a facility in India", "Tender offer to acquire PolyPeptide", "business_activity"),
    ("acquisition of the group, with a facility in India", "Something else", "market_entry_or_investment"),
])
def test_classify(m, snippet, title, tier):
    assert m.classify(snippet, title) == tier


@pytest.mark.parametrize("text,rx,hit", [
    ("India (25%), Indonesia (10%)", "STATS_LIST_RE", True),
    ("India 25%", "STATS_LIST_RE", False),
    ("He held various roles in the group and India", "BIO_RE", True),
    ("India head with career spanning decades", "BIO_RE", True),
    ("Notification Obligation filed", "REVERSE_NOTIFY_RE", True),
    ("Country: Indien", "REVERSE_COUNTRY_RE", True),
    ("India has taken control of the issuer", "REVERSE_CONTROL_RE", True),
    ("India took control of it", "REVERSE_CONTROL_RE", False),
])
def test_hazard_regexes(m, text, rx, hit):
    assert bool(getattr(m, rx).search(text)) is hit


def test_get_json(m, monkeypatch):
    seen = {}
    monkeypatch.setattr(requests, "get", lambda url, params=None, headers=None, timeout=None: (
        seen.update(p=params, t=timeout), FakeResp(jsonobj={"a": 1}))[1])
    assert m.get_json("u", {"x": 1}, timeout=9) == {"a": 1} and seen == {"p": {"x": 1}, "t": 9}
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp(b"", status=500))
    with pytest.raises(requests.HTTPError):
        m.get_json("u")


# ------------------------------------------------------------ roster check
ISSUERS = [
    {"valorSymbol": "ABB", "company": "ABB Ltd", "isin": "CH0012221716", "country": "CH"},
    {"valorSymbol": "NOVN", "company": "Novartis AG", "isin": "CH0012005267", "country": "CH"},
    {"valorSymbol": "MMM", "company": "3M", "isin": "US88579Y1010", "country": "US"},
]


def _csv(path, rows, fields=("yf_ticker", "name", "exchange", "market")):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def test_verify_roster_missing_csv(m, tmp_path, monkeypatch):
    monkeypatch.setattr(m, "CH_CSV", str(tmp_path / "none.csv"))
    r = m.verify_roster(ISSUERS)
    assert r["total_six_equity_issuers"] == 3 and r["live_ch_domiciled_issuers"] == 2
    assert r["status"].startswith("CH.csv not found") and "chcsv_before_count" not in r


def test_verify_roster_adds_missing_and_backfills_names(m, tmp_path, monkeypatch):
    p = tmp_path / "CH.csv"
    _csv(p, [{"yf_ticker": "ABB.SW", "name": "", "exchange": "CH", "market": "CH"},
             {"yf_ticker": "OLD.SW", "name": "Old Co", "exchange": "CH", "market": "CH"}])
    monkeypatch.setattr(m, "CH_CSV", str(p))
    r = m.verify_roster(ISSUERS)
    assert [x["ticker"] for x in r["missing_from_chcsv_added"]] == ["NOVN.SW"]
    assert r["stale_in_chcsv_not_found_live"] == ["OLD"]
    assert r["chcsv_before_count"] == 2 and r["chcsv_before_names_populated"] == 1 and r["chcsv_after_count"] == 3
    assert r["status"].startswith("UPDATED live: added 1 missing issuer(s), backfilled name for 2 rows")
    rows = list(csv.DictReader(open(p)))
    assert [(x["yf_ticker"], x["name"]) for x in rows] == [("ABB.SW", "ABB Ltd"), ("NOVN.SW", "Novartis AG"),
                                                           ("OLD.SW", "Old Co")]          # stale rows kept, sorted by symbol


def test_verify_roster_complete_csv_untouched(m, tmp_path, monkeypatch):
    p = tmp_path / "CH.csv"
    _csv(p, [{"yf_ticker": "ABB.SW", "name": "ABB", "exchange": "CH", "market": "CH"},
             {"yf_ticker": "NOVN.SW", "name": "Novartis", "exchange": "CH", "market": "CH"}])
    before = p.read_text()
    monkeypatch.setattr(m, "CH_CSV", str(p))
    r = m.verify_roster(ISSUERS)
    assert r["status"].startswith("CH.csv already complete") and p.read_text() == before


def test_check_esef_ch(m, monkeypatch):
    monkeypatch.setattr(m, "get_json", lambda url, params=None: {"data": []})
    r = m.check_esef_ch()
    assert r["ch_filings_found"] == 0 and "confirmed live -- 0 filings" in r["verdict"]
    monkeypatch.setattr(m, "get_json", lambda url, params=None: {"data": [1, 2]})
    assert m.check_esef_ch()["verdict"] == "unexpected: 2 CH filings found on filings.xbrl.org"
    monkeypatch.setattr(m, "get_json", lambda url, params=None: (_ for _ in ()).throw(OSError("x")))
    assert m.check_esef_ch()["error"] == "OSError: x"


def test_fetch_all_news_paging(m, monkeypatch):
    big = [{"id": i} for i in range(500)]
    pages = {0: big, 1: [{"id": 500}, {"id": 501}]}
    calls = []

    def get_json(url, params=None):
        calls.append((params["pageNumber"], params["pageSize"], params["from"]))
        return {"data": pages[params["pageNumber"]], "total": 502}
    monkeypatch.setattr(m, "get_json", get_json)
    items, total = m.fetch_all_news("20240101")
    assert len(items) == 502 and total == 502
    assert calls == [(0, 500, "20240101"), (1, 500, "20240101")]
    # an empty batch stops the loop even when total promises more
    monkeypatch.setattr(m, "get_json", lambda url, params=None: {"data": [], "total": 10})
    assert m.fetch_all_news() == ([], 10)
    # a missing total falls back to the number of items fetched so far
    monkeypatch.setattr(m, "get_json", lambda url, params=None: {"data": [{"id": 1}]})
    assert m.fetch_all_news() == ([{"id": 1}], 1)


# ---------------------------------------------------------------- full run
def item(i, company, isin, date_ms, contents, ad_hoc=False):
    return {"id": i, "company": {"name": company, "isin": isin}, "news_date": date_ms, "ad_hoc": ad_hoc,
            "content": [{"language": l, "title": t, "content": c} for l, t, c in contents]}


def test_main_end_to_end(m, tmp_path, monkeypatch, capsys):
    out = tmp_path / "out/sweep.json"
    monkeypatch.setattr(m, "OUT", str(out))
    monkeypatch.setattr(m, "CH_CSV", str(tmp_path / "missing.csv"))
    news = [
        # entry (English preferred over German when both mention India)
        item(1, "ABB Ltd", "CH0012221716", ms(2025, 6, 15),
             [("de", "Neues Werk", "Wir bauen ein Werk in Indien."),
              ("en", "New plant", "<p>ABB opens a new plant in India. Other text.</p>")], ad_hoc=True),
        # boilerplate duplicate of the same facts -> collapsed
        item(2, "ABB Ltd", "CH0012221716", ms(2025, 7, 1), [("en", "New plant", "ABB opens a new plant in India.")]),
        # exit
        item(3, "Novartis AG", "CH0012005267", ms(2025, 5, 1), [("en", "Exit", "Novartis completes the sale of its India unit.")]),
        # context-only statistics list
        item(4, "Straumann", "CH0012280076", ms(2025, 4, 1), [("en", "Report", "Markets: India (25%), Brazil (10%).")]),
        # reverse direction
        item(5, "Target AG", "CH0000000001", ms(2025, 3, 1),
             [("en", "Disclosure", "Notification obligation Country: Indien.")]),
        item(6, "Reverse2 AG", None, ms(2025, 2, 1), [("en", "Control", "India has taken control of Reverse2 AG.")]),
        # no India mention anywhere / language not in priority list
        item(7, "Quiet AG", None, ms(2025, 1, 1), [("en", "Results", "Strong quarter.")]),
        item(8, "Other AG", None, None, [("es", "Informe", "Expansion en India.")]),
        # business activity, no date
        item(9, "Biz AG", None, None, [("fr", "Résultats", "Hausse des ventes en Inde.")]),
    ]
    monkeypatch.setattr(m, "get_json", lambda url, params=None, timeout=30: {"itemList": ISSUERS}
                        if "equity_issuers" in url else {"data": []})
    monkeypatch.setattr(m, "fetch_all_news", lambda since="20150101": (news, 9))
    m.main()
    d = json.load(open(out))
    assert d["corpus"]["fetched"] == 9 and d["corpus"]["total_equity_issuer_news_items"] == 9
    assert d["corpus"]["ad_hoc_flagged"] == 1 and d["corpus"]["distinct_issuers_in_window"] == 8
    assert d["corpus"]["date_range_actual"] == ["2025-01-01", "2025-07-01"]
    assert d["raw_india_mentioning_items"] == 7 and d["unique_facts_after_dedup"] == 6
    assert d["boilerplate_duplicates_collapsed"] == 1
    assert [h["news_id"] for h in d["market_entry_or_investment"]] == [1]
    e = d["market_entry_or_investment"][0]
    assert e["lang"] == "en" and e["ticker"] == "ABB" and e["news_date"] == "2025-06-15" and e["ad_hoc"] is True
    assert e["snippet"] == "ABB opens a new plant in India."
    assert [h["news_id"] for h in d["exit_or_divestment"]] == [3]
    assert [h["news_id"] for h in d["excluded_context_only"]] == [4]
    assert sorted(h["news_id"] for h in d["excluded_reverse_direction"]) == [5, 6]
    assert [h["news_id"] for h in d["business_activity"]] == [9]
    assert d["business_activity"][0]["lang"] == "fr" and d["business_activity"][0]["news_date"] is None
    assert d["esef_xbrl_check"]["ch_filings_found"] == 0 and d["roster_verification"]["live_ch_domiciled_issuers"] == 2
    text = capsys.readouterr().out
    assert "excluded context_only: 1 | excluded reverse_direction: 2" in text
    assert "market_entry_or_investment: 1 | business_activity: 1 | exit_or_divestment: 1" in text
    assert "ENTRY: ABB Ltd (ABB) -- New plant" in text and "EXIT: Novartis AG (NOVN) -- Exit" in text


def test_main_no_dates_gives_null_range(m, tmp_path, monkeypatch):
    monkeypatch.setattr(m, "OUT", str(tmp_path / "o.json"))
    monkeypatch.setattr(m, "CH_CSV", str(tmp_path / "missing.csv"))
    monkeypatch.setattr(m, "get_json", lambda url, params=None, timeout=30: {"itemList": []} if "issuers" in url else {"data": []})
    monkeypatch.setattr(m, "fetch_all_news", lambda since="20150101": ([], 0))
    m.main()
    assert json.load(open(tmp_path / "o.json"))["corpus"]["date_range_actual"] is None
