import json
import subprocess
import sys

import pytest

from conftest import load_script


@pytest.fixture
def rt(fake_repo):
    mod = load_script("refresh_twin", fake_repo)
    mod.TODAY = "2026-01-02"
    return mod


class _Proc:
    def __init__(self, stdout="", rc=0):
        self.stdout = stdout
        self.returncode = rc


def test_curl_parses_body_and_code(rt, monkeypatch):
    seen = {}

    def run(cmd, **kw):
        seen["cmd"], seen["kw"] = cmd, kw
        return _Proc("hello\nworld\n200")

    monkeypatch.setattr(subprocess, "run", run)
    assert rt.curl("http://x", timeout=7) == ("200", "hello\nworld")
    assert "-k" not in seen["cmd"]
    assert seen["cmd"][seen["cmd"].index("-m") + 1] == "7"
    assert seen["kw"]["timeout"] == 17  # subprocess gets +10s grace


def test_curl_insecure_inserts_k_and_error_is_swallowed(rt, monkeypatch):
    seen = {}

    def run(cmd, **kw):
        seen["cmd"] = cmd
        raise OSError("no curl")

    monkeypatch.setattr(subprocess, "run", run)
    code, body = rt.curl("http://x", insecure=True)
    assert seen["cmd"][1] == "-k"
    assert (code, body) == ("ERR", "no curl")


def test_strip_tags_removes_scripts_styles_and_unescapes(rt):
    src = "<html><style>p{x:y}</style><script>var a=1;\n</script><p>A &amp;  B</p>\n<b>c</b></html>"
    assert rt.strip_tags(src) == "A & B c"


def test_snapshots_roundtrip_and_latest_is_lexicographic(rt):
    assert rt.latest_snapshot("foo") is None
    p = rt.save_snapshot("foo", {"v": 1})
    assert p.endswith("foo_2026-01-02.json")
    rt.TODAY = "2026-01-09"
    rt.save_snapshot("foo", {"v": 2})
    rt.TODAY = "2026-01-05"
    rt.save_snapshot("foo", {"v": 3})
    assert rt.latest_snapshot("foo") == {"v": 2}
    assert rt.latest_snapshot("bar") is None  # prefix isolation


def _write_directory(root, central, state):
    (root / "layers").mkdir(exist_ok=True)
    (root / "layers" / "15_directory.json").write_text(
        json.dumps({"central": central, "state": state}))


def test_cmd_routes_records_down_and_changes(rt, fake_repo, monkeypatch, capsys):
    _write_directory(
        fake_repo,
        {"A": {"url": "http://a"}, "B": {"url": "http://b"}},
        {"C": {"url": "https://ditc.goa.gov.in/x"}},
    )
    # previous snapshot: A was down, B was up
    (fake_repo / "state" / "routes_2025-12-01.json").write_text(json.dumps(
        {"results": {"A": {"ok": False}, "B": {"ok": True}}}))
    calls = []

    def fake_curl(url, timeout=20, insecure=False):
        calls.append((url, insecure))
        return {"http://a": ("200", ""), "http://b": ("503", "")}.get(url, ("301", ""))

    monkeypatch.setattr(rt, "curl", fake_curl)
    rt.cmd_routes()
    out = capsys.readouterr().out
    snap = json.loads((fake_repo / "state" / "routes_2026-01-02.json").read_text())
    assert snap["down"] == ["B"]
    assert snap["results"]["A"]["ok"] is True  # 2xx ok
    assert snap["results"]["C"]["ok"] is True  # 3xx ok
    assert "routes: 3 checked, 1 down" in out
    assert "DOWN B (503) http://b" in out
    assert "CHANGE route A: ok=False -> True (200)" in out
    assert "CHANGE route B: ok=True -> False (503)" in out
    assert "route C" not in out  # new route is not a change
    assert ("https://ditc.goa.gov.in/x", True) in calls  # only goa insecure
    assert ("http://a", False) in calls


def test_cmd_routes_without_previous_snapshot_has_no_changes(rt, fake_repo, monkeypatch, capsys):
    _write_directory(fake_repo, {"A": {"url": "http://a"}}, {})
    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("404", ""))
    rt.cmd_routes()
    out = capsys.readouterr().out
    assert "CHANGE" not in out and "DOWN A (404)" in out


def test_cmd_unnati_first_run_then_unchanged_then_changed(rt, fake_repo, monkeypatch, capsys):
    page = "<p>Important Notice Registration has presently been stopped.</p>"
    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("200", page))
    rt.cmd_unnati()
    assert "registration_stopped=True" in capsys.readouterr().out
    rt.cmd_unnati()
    out = capsys.readouterr().out
    assert "CHANGE" not in out and "registration_stopped=True" in out

    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("200", "<p>Important Notice Registration is open now. Apply.</p>"))
    rt.TODAY = "2026-01-03"
    rt.cmd_unnati()
    out = capsys.readouterr().out
    assert "CHANGE unnati notice text differs" in out
    assert "-" in out and "+" in out


def test_cmd_unnati_missing_notice_block(rt, monkeypatch, capsys, fake_repo):
    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("500", "<p>nothing</p>"))
    rt.cmd_unnati()
    snap = json.loads((fake_repo / "state" / "unnati_2026-01-02.json").read_text())
    assert snap["notice"] == "(no notice block found)"
    assert snap["http"] == "500"
    assert "registration_stopped=False" in capsys.readouterr().out


def test_cmd_nsws_reports_only_http_changes(rt, fake_repo, monkeypatch, capsys):
    (fake_repo / "state" / "nsws_2025-01-01.json").write_text(json.dumps({"pages": {
        "unnati_guidelines": {"http": "200", "bytes": 1},
        "nsws_home": {"http": "200", "bytes": 5}}}))
    monkeypatch.setattr(rt, "curl", lambda url, **k: ("404", "") if "General_Operational" in url else ("200", "abcd"))
    rt.cmd_nsws()
    out = capsys.readouterr().out
    assert "CHANGE nsws unnati_guidelines: 200 -> 404" in out
    assert "CHANGE nsws nsws_home" not in out  # bytes differ but http same
    assert "nsws: 2 pages" in out
    snap = json.loads((fake_repo / "state" / "nsws_2026-01-02.json").read_text())
    assert snap["pages"]["nsws_home"]["bytes"] == 4


@pytest.mark.parametrize("body,expected", [
    ("Issue of 17 Jul 2026 and 3 Jun 2026", "17 Jul 2026"),
    ("Posted on July 5, 2026 ...", "July 5, 2026"),
    ("as of 01/02/2026 here", "01/02/2026"),
    ("no dates here", None),
])
def test_cmd_rbi_latest_date_forms(rt, monkeypatch, capsys, body, expected):
    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("200", f"<p>{body}</p>"))
    rt.cmd_rbi()
    assert f"latest WSS issue = {expected}" in capsys.readouterr().out


def test_cmd_rbi_change_detection(rt, monkeypatch, capsys):
    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("200", "<p>1 Jan 2026</p>"))
    rt.cmd_rbi()
    assert "CHANGE" not in capsys.readouterr().out
    monkeypatch.setattr(rt, "curl", lambda *a, **k: ("200", "<p>8 Jan 2026</p>"))
    rt.TODAY = "2026-01-09"
    rt.cmd_rbi()
    assert "CHANGE rbi WSS: 1 Jan 2026 -> 8 Jan 2026" in capsys.readouterr().out


def test_cmd_pib_missing_script_exits(rt, monkeypatch, tmp_path):
    monkeypatch.setattr(rt.os.path, "expanduser", lambda p: str(tmp_path / "nope" / "scripts" / "pib_index.py"))
    with pytest.raises(SystemExit) as e:
        rt.cmd_pib()
    assert "pib_index.py not found" in str(e.value.code)


def test_cmd_pib_runs_script_in_repo_root(rt, monkeypatch, tmp_path):
    script = tmp_path / "pol" / "scripts" / "pib_index.py"
    script.parent.mkdir(parents=True)
    script.write_text("")
    monkeypatch.setattr(rt.os.path, "expanduser", lambda p: str(script))
    seen = {}
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: seen.update(cmd=cmd, kw=kw))
    rt.cmd_pib()
    assert seen["cmd"] == [sys.executable, str(script), "--update"]
    assert seen["kw"]["cwd"] == str(tmp_path / "pol")
    assert seen["kw"]["check"] is False


def test_cmd_catalogue_runs_both_builders_checked(rt, monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: calls.append((cmd[1].split("/")[-1], kw)))
    rt.cmd_catalogue()
    assert [c[0] for c in calls] == ["build_catalogue.py", "build_reportage.py"]
    assert all(c[1]["check"] is True for c in calls)


def test_cmd_watchlist_isolates_failures(rt, monkeypatch, capsys):
    calls = []
    checks = []

    def run(cmd, **kw):
        name = cmd[1].split("/")[-1]
        calls.append(name)
        checks.append(kw["check"])
        if name == "build_layer28_policy_watchlist.py":
            raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(subprocess, "run", run)
    rt.cmd_watchlist()
    assert checks == [True] * 16
    assert len(calls) == 16 and calls[0] == "build_layer25_linkages.py"
    assert calls[-1] == "build_layer45_media_rss_sweep.py"
    assert "ERROR build_layer28_policy_watchlist.py" in capsys.readouterr().out


def test_main_dispatch_single_command(rt, monkeypatch):
    hit = []
    monkeypatch.setattr(sys, "argv", ["x", "rbi"])
    rt.cmd_rbi = lambda: hit.append("rbi")
    rt.main()
    assert hit == ["rbi"]


def test_main_weekly_runs_all_and_survives_errors(rt, monkeypatch, capsys):
    hit = []
    rt.cmd_routes = lambda: hit.append("routes")
    rt.cmd_unnati = lambda: (_ for _ in ()).throw(ValueError("boom"))
    rt.cmd_nsws = lambda: hit.append("nsws")
    rt.cmd_rbi = lambda: hit.append("rbi")
    rt.cmd_watchlist = lambda: hit.append("watchlist")
    monkeypatch.setattr(sys, "argv", ["x", "weekly"])
    rt.main()
    assert hit == ["routes", "nsws", "rbi", "watchlist"]
    assert "ERROR <lambda>: boom" in capsys.readouterr().out


def test_main_rejects_unknown_command(rt, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x", "bogus"])
    with pytest.raises(SystemExit) as e:
        rt.main()
    assert e.value.code == 2


def test_run_as_main_script(fake_repo, monkeypatch, capsys):
    mod_calls = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: mod_calls.append(a))
    load_script("refresh_twin", fake_repo, argv=["catalogue"], run_name="__main__")
    assert len(mod_calls) == 2
