"""Characterisation of collect_state_news.main with stub fetchers and a temp register (no network)."""
import datetime
import sqlite3
import sys
import types

import collect_state_news as csn
from conftest import sha

GOLDEN = {'out': 'aa722b744610eacf533174686a300136a11e921119b9ccf29fd1233054f80af8', 'err': 'd839fe624b9aabb07e3750f9e5e62f0067c1b0c08f3c4f106c23d973bd97a39d', 'db': 'a30cf747ce9e7e6f59d625c2243c615064583242917e97729acd7af87a501f1f'}


class _Date(datetime.date):
    @classmethod
    def today(cls):
        return cls(2026, 1, 10)


class _DateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 1, 10, 12, 0, 0)


def _rows(tag, n):
    return [{"newsid": f"{tag}{i}", "date": f"2026-01-0{i + 1}", "title": f"{tag} investment MoU {i}" if i % 2 else f"{tag} नमस्ते {i}",
             "category": "news", "keywords": "", "url": f"http://{tag}/{i}"} for i in range(n)]


def _boom():
    raise OSError("down")


def test_main_register_is_identical(tmp_path, monkeypatch, capsys):
    db = tmp_path / "state_news.sqlite"
    monkeypatch.setattr(csn, "DB", str(db))
    monkeypatch.setattr(csn, "SOURCES", {
        "MP": {"state": "Madhya Pradesh", "mode": "daily", "fetch": lambda day: _rows("mp" + str(day.day), 2)},
        "GJ": {"state": "Gujarat", "mode": "latest", "fetch": lambda: _rows("gj", 3) + _rows("gj", 1)},
        "XX": {"state": "Broken", "mode": "latest", "fetch": _boom}})
    monkeypatch.setattr(csn, "translate_en", lambda t: "translated " + t[:12])
    monkeypatch.setattr(csn.time, "sleep", lambda s: None)
    monkeypatch.setattr(csn, "datetime", types.SimpleNamespace(date=_Date, datetime=_DateTime, timedelta=datetime.timedelta))
    monkeypatch.setattr(sys, "argv", ["collect_state_news.py", "--days", "2"])
    csn.main()
    cap = capsys.readouterr()
    con = sqlite3.connect(db)
    dump = "\n".join(con.iterdump())
    con.close()
    got = {"out": sha(cap.out), "err": sha(cap.err), "db": sha(dump)}
    assert got == GOLDEN, got
