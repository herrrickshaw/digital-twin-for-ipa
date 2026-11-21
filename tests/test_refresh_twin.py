import refresh_twin as rt


def test_strip_tags_removes_script_style_and_unescapes():
    html = "<html><style>p{}</style><script>var x=1</script><p>Scheme&nbsp;A &amp; B</p>\n<b>open</b></html>"
    assert rt.strip_tags(html) == "Scheme\xa0A & B open"


def test_snapshots_roundtrip_latest_by_date(tmp_path, monkeypatch):
    monkeypatch.setattr(rt, "STATE", str(tmp_path))
    (tmp_path / "routes_2026-01-01.json").write_text('{"v": 1}')
    monkeypatch.setattr(rt, "TODAY", "2026-02-01")
    path = rt.save_snapshot("routes", {"v": 2})
    assert path.endswith("routes_2026-02-01.json")
    assert rt.latest_snapshot("routes") == {"v": 2}
    assert rt.latest_snapshot("missing") is None


def test_curl_builds_argument_list_without_shell(monkeypatch):
    seen = {}

    class R:
        stdout = "body text\n200"

    def fake_run(cmd, **kw):
        seen["cmd"], seen["kw"] = cmd, kw
        return R()

    monkeypatch.setattr(rt.subprocess, "run", fake_run)
    code, body = rt.curl("https://example.invalid/a b;rm -rf", insecure=True)
    assert (code, body) == ("200", "body text")
    assert seen["cmd"][:2] == ["curl", "-k"] and seen["cmd"][-1] == "https://example.invalid/a b;rm -rf"
    assert "shell" not in seen["kw"]


def test_curl_failure_returns_err(monkeypatch):
    def boom(*a, **k):
        raise OSError("no curl")
    monkeypatch.setattr(rt.subprocess, "run", boom)
    assert rt.curl("https://example.invalid")[0] == "ERR"
