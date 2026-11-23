import json
import smtplib
import sys

import pytest

from conftest import load_script


def _run_catalogue(root, instruments):
    (root / "layers").mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)
    (root / "layers" / "13_flat_instrument_index.json").write_text(
        json.dumps({"count": len(instruments), "instruments": instruments}))
    load_script("build_catalogue", root)
    return (root / "docs" / "SCHEME_CATALOGUE.md").read_text()


def test_catalogue_groups_flags_and_escapes(fake_repo):
    ins = [
        {"tier": "central", "offering_entity": "DPIIT", "instrument": "A|B", "instrument_type": "grant|x",
         "status": "Oversubscribed and closed", "what_companies_get": "cash|money"},
        {"tier": "central", "offering_entity": "DPIIT", "instrument": "Old", "status": "lapsed"},
        {"tier": "central", "offering_entity": "DPIIT", "instrument": "Shut", "application_status": "closed"},
        {"tier": "central", "offering_entity": "DPIIT", "instrument": "Live", "status": "Active"},
        {"tier": "central", "offering_entity": "DPIIT", "instrument": "Meh", "site_notes": "x" * 300},
        {"tier": "state", "offering_entity": "Goa", "instrument": "G1", "status": "in force"},
        {"tier": "weird"},
    ]
    md = _run_catalogue(fake_repo, ins)
    assert "## Central government (5 instruments)" in md
    assert "## States & UTs (1 instruments)" in md
    assert "### DPIIT" in md and "### Goa" in md
    assert "| A/B | grant/x | 🔴 CLOSED-OVERSUBSCRIBED | cash/money |" in md
    assert "| Old |  | ⚫ lapsed/superseded |" in md
    assert "| Shut |  | 🔒 closed |" in md
    assert "| Live |  | 🟢 open/active |" in md
    assert "| Meh |  | ▫ unspecified | " + "x" * 217 + "... |" in md
    assert "x" * 218 not in md
    # the 'weird' tier is not rendered anywhere
    assert "weird" not in md
    assert "(7 instruments)" in md  # header counts the whole index


def test_catalogue_boundary_220_chars_not_truncated(fake_repo):
    md = _run_catalogue(fake_repo, [
        {"tier": "central", "offering_entity": "E", "instrument": "I", "what_companies_get": "y" * 220}])
    assert "y" * 220 + " |" in md and "..." not in md


def test_catalogue_defaults_for_missing_fields(fake_repo):
    md = _run_catalogue(fake_repo, [{"tier": "state"}])
    assert "### ?" in md and "| ? |  | ▫ unspecified |  |" in md


@pytest.fixture
def alert(fake_repo, monkeypatch):
    for k in ("GMAIL_USER", "GMAIL_APP_PASSWORD", "MAIL_TO"):
        monkeypatch.delenv(k, raising=False)
    mod = load_script("send_twin_alert", fake_repo)
    mod.PLIST = str(fake_repo / "missing.plist")
    return mod


def test_creds_from_env_default_to_is_user(alert, monkeypatch):
    monkeypatch.setenv("GMAIL_USER", "u@x")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "pw")
    assert alert.creds() == ("u@x", "pw", "u@x")
    monkeypatch.setenv("MAIL_TO", "t@x")
    assert alert.creds() == ("u@x", "pw", "t@x")


def test_creds_fall_back_to_plist_without_overriding_env(alert, monkeypatch, tmp_path):
    import plistlib
    p = tmp_path / "a.plist"
    p.write_bytes(plistlib.dumps({"EnvironmentVariables": {
        "GMAIL_USER": "pu", "GMAIL_APP_PASSWORD": "pp", "MAIL_TO": "pt"}}))
    alert.PLIST = str(p)
    assert alert.creds() == ("pu", "pp", "pt")
    monkeypatch.setenv("GMAIL_USER", "eu")
    assert alert.creds()[0] == "eu"


def test_creds_none_when_nothing(alert):
    assert alert.creds() == (None, None, None)


def test_send_without_creds_returns_1(alert, capsys):
    assert alert.send("s", "b") == 1
    assert "no credentials" in capsys.readouterr().err


def test_send_uses_smtp_ssl(alert, monkeypatch, capsys):
    monkeypatch.setenv("GMAIL_USER", "u@x")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "pw")
    sent = {}

    class S:
        def __init__(self, host, port):
            sent["hp"] = (host, port)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def login(self, u, p):
            sent["login"] = (u, p)

        def sendmail(self, f, to, msg):
            sent["mail"] = (f, to, msg)

    monkeypatch.setattr(smtplib, "SMTP_SSL", S)
    assert alert.send("Subj", "Body") == 0
    assert sent["hp"] == ("smtp.gmail.com", 465)
    assert sent["login"] == ("u@x", "pw")
    assert sent["mail"][1] == ["u@x"] and "Subject: Subj" in sent["mail"][2]
    assert "sent 'Subj' to u@x" in capsys.readouterr().out


def _main(alert, monkeypatch, argv, stdin=""):
    import io
    monkeypatch.setattr(sys, "argv", ["x"] + argv)
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    sent = []
    alert.send = lambda s, b: sent.append((s, b)) or 0
    try:
        alert.main()
        code = None
    except SystemExit as e:
        code = e.code
    return code, sent


def test_main_test_mode(alert, monkeypatch):
    code, sent = _main(alert, monkeypatch, ["--test"])
    assert code == 0 and "test alert" in sent[0][0]


def test_main_if_changes_silent_without_changes(alert, monkeypatch):
    code, sent = _main(alert, monkeypatch, ["--if-changes"], "unnati: ok registration_stopped=True\n")
    assert code == 0 and sent == []


def test_main_if_changes_sends_with_down_lines(alert, monkeypatch):
    out = "CHANGE route A: ok=True -> False\n  DOWN A (503) u\nrouted\n"
    code, sent = _main(alert, monkeypatch, ["--if-changes"], out)
    assert code == 0 and len(sent) == 1
    subj, body = sent[0]
    assert "1 change(s) detected" in subj
    assert "Portals down:\n  DOWN A (503) u\n" in body
    assert body.endswith(out)


def test_main_if_changes_flags_resumed_registration(alert, monkeypatch):
    code, sent = _main(alert, monkeypatch, ["--if-changes"], "unnati: registration_stopped=False -> x\n")
    assert sent and "2 change" not in sent[0][0] and "1 change(s)" in sent[0][0]
    assert "RESUMED" in sent[0][1]


def test_main_raw_tail_limited_to_4000(alert, monkeypatch):
    out = "CHANGE x\n" + "z" * 6000
    _, sent = _main(alert, monkeypatch, ["--if-changes"], out)
    assert sent[0][1].split("--- raw ---\n")[1] == out[-4000:]


def test_main_explicit_subject(alert, monkeypatch):
    code, sent = _main(alert, monkeypatch, ["--subject", "S", "--body", "B"])
    assert sent == [("S", "B")] and code == 0
    code, sent = _main(alert, monkeypatch, ["--subject", "S"])
    assert sent == [("S", "")]


def test_main_without_args_prints_help(alert, monkeypatch, capsys):
    code, sent = _main(alert, monkeypatch, [])
    assert code is None and sent == [] and "usage" in capsys.readouterr().out
