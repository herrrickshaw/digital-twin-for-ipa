"""Characterisation of build_switzerland_india_sweep.main with stubbed SIX endpoints (no network)."""
import datetime

import pytest

pytest.importorskip("requests")
import build_switzerland_india_sweep as sw  # noqa: E402
from conftest import sha  # noqa: E402

GOLDEN = {'out': '3016212bf921ba2014331236e0276cb0f20efff9f56f2436b5b15fcc0188b9b6', 'json': '5912d758a92efb06e6e815e0e9a5a0f0cdd0f3ef55f813d37f9a8a9bc6756644'}


def _ts(y, m, d):
    return int(datetime.datetime(y, m, d, 12).timestamp() * 1000)


def _item(i, company, isin, text, title="Update", day=1, ad_hoc=False):
    return {"id": i, "company": {"name": company, "isin": isin}, "news_date": _ts(2026, 1, day), "ad_hoc": ad_hoc,
            "content": [{"language": "en", "title": title, "content": f"<p>{text}</p>"}]}


ITEMS = [
    _item(1, "Alpha AG", "CH001", "Alpha will build a new plant in India to expand capacity. It invests CHF 50 million.", "Alpha invests in India plant", 2, True),
    _item(2, "Alpha AG", "CH001", "Alpha will build a new plant in India to expand capacity. It invests CHF 50 million.", "Alpha invests in India plant", 3),
    _item(3, "Beta SA", "CH002", "Beta sells its subsidiary in India and exits the market.", "Beta divests", 4),
    _item(4, "Gamma AG", "CH003", "Disease burden: India (12%) and China (10%).", "Stats", 5),
    _item(5, "Delta AG", "CH004", "Weather is nice.", "Nothing", 6),
    _item(6, "Eps AG", "CH005", "Sales in India grew strongly last year.", "Results", 7),
    _item(7, "Zeta AG", "CH006", "India has taken control of Zeta.", "Control", 8),
]


def test_main_identical(tmp_path, monkeypatch, capsys, frozen_today):
    out = tmp_path / "layers" / "sw.json"
    monkeypatch.setattr(sw, "OUT", str(out))
    monkeypatch.setattr(sw, "get_json", lambda url, params=None, timeout=30: {"itemList": [
        {"isin": "CH001", "valorSymbol": "ALP", "country": "CH"}, {"isin": "CH002", "valorSymbol": "BET", "country": "CH"}]})
    monkeypatch.setattr(sw, "verify_roster", lambda issuers: {"status": "ok", "n": len(issuers)})
    monkeypatch.setattr(sw, "check_esef_ch", lambda: {"verdict": "zero CH filings"})
    monkeypatch.setattr(sw, "fetch_all_news", lambda since="20150101": (ITEMS, 7))
    sw.main()
    text = capsys.readouterr().out.replace(str(tmp_path), "<TMP>")
    got = {"out": sha(text), "json": sha(out.read_bytes())}
    assert "ENTRY: Alpha AG" in text and "EXIT: Beta SA" in text
    assert got == GOLDEN
