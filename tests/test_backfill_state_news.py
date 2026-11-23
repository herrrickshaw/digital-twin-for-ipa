"""backfill_state_news: resumable archive backfill (MP/MH/RJ) and the signal translation pass."""
import datetime
import re
import sys
import time

import pytest

from conftest import load_script


@pytest.fixture
def bf(fake_repo, tmp_path, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *a: None)
    before = set(sys.modules)
    m = load_script("backfill_state_news", fake_repo)
    csn = sys.modules["collect_state_news"]
    monkeypatch.setattr(csn, "DB", str(tmp_path / "state.sqlite"))
    con = m.ensure_db()
    con.execute("""create table if not exists backfill_log(
        state text not null, chunk text not null, fetched_at text, n integer, primary key(state, chunk))""")
    yield m, con
    con.close()
    for k in set(sys.modules) - before:
        if k == "collect_state_news":
            del sys.modules[k]


def _row(i, title="Hello world", date="2026-01-01"):
    return {"newsid": str(i), "date": date, "title": title, "category": "cat", "keywords": "kw", "url": f"http://u/{i}"}


@pytest.mark.parametrize("title,match", [
    ("राज्य में निवेश की घोषणा", True), ("गुंतवणूक करार", True), ("New Policy announced", True),
    ("investment in plant", True), ("MSME cluster", True), ("एमओयू पर हस्ताक्षर", True),
    ("Weather forecast for Tuesday", False), ("", False), ("cricket match", False),
])
def test_signal_native_regex(bf, title, match):
    m, _ = bf
    assert bool(m.SIGNAL_NATIVE.search(title)) is match


def test_backfill_mp_days_resume_and_failures(bf, monkeypatch, capsys):
    m, con = bf
    today = datetime.date.today()
    monkeypatch.setattr(m, "MP_START", today - datetime.timedelta(days=3))        # 4 days incl. today
    done_day = (today - datetime.timedelta(days=2)).isoformat()
    con.execute("insert into backfill_log values('MP', ?, 'x', 0)", (done_day,))
    con.commit()
    calls = []

    def fetch_mp(day):
        calls.append(day.isoformat())
        if day == today - datetime.timedelta(days=1):
            raise RuntimeError("503")
        return [_row(1, "इंडिया समाचार"), _row(2, "English title")] if day == today else []
    monkeypatch.setattr(m, "fetch_mp", fetch_mp)
    m.backfill_mp(con)
    assert done_day not in calls and len(calls) == 3
    rows = con.execute("select newsid, title_en from state_news where state='MP' order by newsid").fetchall()
    assert rows == [("1", None), ("2", "English title")]            # only English titles pre-filled
    logged = {r[0] for r in con.execute("select chunk from backfill_log where state='MP'")}
    assert today.isoformat() in logged and (today - datetime.timedelta(days=1)).isoformat() not in logged
    assert (today - datetime.timedelta(days=3)).isoformat() in logged         # empty day still logged
    cap = capsys.readouterr()
    assert "MP: 3 days to fetch (1 already logged)" in cap.out
    assert "FETCH FAILED (503) -- will retry on next run" in cap.err
    assert "MP progress: 0/3 days" in cap.out
    # second run only retries the failed day
    calls.clear()
    m.backfill_mp(con)
    assert calls == [(today - datetime.timedelta(days=1)).isoformat()]


def test_backfill_mh_pages(bf, monkeypatch, capsys):
    m, con = bf
    con.execute("insert into backfill_log values('MH','page-1','x',100)")
    con.commit()
    pages = {2: [{"id": i, "date": "2026-02-02T10:00:00", "link": f"http://m/{i}",
                  "title": {"rendered": f"<b>Post  {i}</b>\n title"}} for i in range(100)],
             3: [{"id": 500, "date": "2026-03-03", "link": None, "title": {"rendered": "  "}},       # blank title skipped
                 {"id": 501, "date": None, "link": "l", "title": {"rendered": "Last"}}]}
    seen = []

    def get_json(url, **kw):
        seen.append(url)
        n = int(re.search(r"[?&]page=(\d+)", url).group(1))
        if n == 4:
            raise RuntimeError("400 Bad Request")
        return pages[n]
    monkeypatch.setattr(m, "_get_json", get_json)
    m.backfill_mh(con)
    assert [int(re.search(r"[?&]page=(\d+)", u).group(1)) for u in seen] == [2, 3]          # page-1 skipped; short page ends the loop
    assert "per_page=100" in seen[0] and "_fields=id%2Cdate%2Clink%2Ctitle" in seen[0]
    rows = dict(((r[0]), r[1:]) for r in con.execute(
        "select newsid, date, title, title_en, category from state_news where state='MH'"))
    assert rows["0"] == ("2026-02-02", "Post 0 title", "Post 0 title", "DGIPR wire")
    assert "500" not in rows and rows["501"][0] == "" and rows["501"][1] == "Last"
    assert con.execute("select n from backfill_log where state='MH' and chunk='page-3'").fetchone() == (2,)
    assert "MH progress" not in capsys.readouterr().out


def test_backfill_mh_failure_retry_then_past_last_page(bf, monkeypatch, capsys):
    m, con = bf
    state = {"n": 0}

    def get_json(url, **kw):
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("timeout")
        if state["n"] == 2:
            return []
        raise AssertionError
    monkeypatch.setattr(m, "_get_json", get_json)
    m.backfill_mh(con)
    assert state["n"] == 2                                   # transient failure retried, empty page ends the run
    assert "MH page 1: FETCH FAILED (timeout)" in capsys.readouterr().err
    assert con.execute("select count(*) from state_news").fetchone() == (0,)


def test_backfill_mh_400_ends_loop(bf, monkeypatch):
    m, con = bf
    monkeypatch.setattr(m, "_get_json", lambda url, **kw: (_ for _ in ()).throw(RuntimeError("HTTP Error 400")))
    m.backfill_mh(con)
    assert con.execute("select count(*) from backfill_log").fetchone() == (0,)


def test_backfill_rj(bf, monkeypatch, capsys):
    m, con = bf
    con.execute("insert into backfill_log values('RJ','page-2','x',1)")
    con.commit()
    calls = []

    def fetch_rj(page_size=100, page=1):
        calls.append((page_size, page))
        if page == 1:
            return [_row(1, "Rajasthan item")]
        return []
    sequence = {"failed": False}

    def wrapper(page_size=100, page=1):
        if page == 3 and not sequence["failed"]:
            sequence["failed"] = True
            raise RuntimeError("flaky")
        return fetch_rj(page_size, page)
    monkeypatch.setattr(m, "fetch_rajasthan", wrapper)
    m.backfill_rj(con)
    # page 1 has rows, page 2 already logged (skipped), page 3 fails once then is empty, pages 4 and 5 empty -> stop
    assert [c[1] for c in calls] == [1, 3, 4] and all(c[0] == 200 for c in calls)
    assert con.execute("select title_en from state_news where state='RJ'").fetchone() == ("Rajasthan item",)
    assert "RJ page 3: FETCH FAILED (flaky)" in capsys.readouterr().err


def test_translate_signal_translates_only_signal_rows_and_breaker(bf, monkeypatch, capsys):
    m, con = bf
    rows = [("MP", "1", "2026-03-01", "निवेश करार"), ("MP", "2", "2026-03-02", "बारिश"),
            ("MP", "3", "2026-03-03", "परियोजना शुरू"), ("UP", "4", "2026-03-04", "नीति घोषित")]
    con.executemany("insert into state_news(state,newsid,date,title,fetched_at) values (?,?,?,?,'x')", rows)
    con.commit()
    monkeypatch.setattr(m, "translate_en", lambda t: "EN:" + t if "परियोजना" not in t else None)
    m.translate_signal(con)
    got = dict(((r[0], r[1]), r[2]) for r in con.execute("select state, newsid, title_en from state_news"))
    assert got[("MP", "1")] == "EN:निवेश करार" and got[("UP", "4")] == "EN:नीति घोषित"
    assert got[("MP", "2")] is None and got[("MP", "3")] is None        # non-signal skipped, failed stays native
    assert "signal pass: 2 translated, 1 failures this run" in capsys.readouterr().out


def test_translate_signal_limit_and_breaker(bf, monkeypatch, capsys):
    m, con = bf
    con.executemany("insert into state_news(state,newsid,date,title,fetched_at) values ('MP',?,?,?, 'x')",
                    [(str(i), f"2026-01-{i + 1:02d}", "निवेश") for i in range(10)])
    con.commit()
    monkeypatch.setattr(m, "translate_en", lambda t: "x")
    m.translate_signal(con, limit=3)
    assert con.execute("select count(*) from state_news where title_en is not null").fetchone() == (3,)
    # circuit breaker: five consecutive failures stop the pass
    monkeypatch.setattr(m, "translate_en", lambda t: None)
    capsys.readouterr()
    m.translate_signal(con)
    cap = capsys.readouterr()
    assert "translation breaker tripped" in cap.err and "0 translated, 5 failures" in cap.out


def test_main_dispatch(bf, monkeypatch, capsys):
    m, con = bf
    order = []
    monkeypatch.setattr(m, "backfill_mh", lambda c: order.append("mh"))
    monkeypatch.setattr(m, "backfill_mp", lambda c: order.append("mp"))
    monkeypatch.setattr(m, "backfill_rj", lambda c: order.append("rj"))
    monkeypatch.setattr(m, "translate_signal", lambda c, lim: order.append(("ts", lim)))
    monkeypatch.setattr(sys, "argv", ["x"])
    m.main()
    assert order == ["mh", "mp", "rj"] and "archives collected" in capsys.readouterr().out
    order.clear()
    monkeypatch.setattr(sys, "argv", ["x", "--translate-signal", "--limit", "7"])
    m.main()
    assert order == [("ts", 7)]
