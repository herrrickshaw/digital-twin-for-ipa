"""Shared harness: scripts are loaded from the real source file (so coverage is
attributed to it) but with ``__file__`` pointing into a throw-away copy of the
repo, so the ROOT-relative reads/writes never touch the working tree."""
import os
import shutil
import sys
import types

import pytest

REAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COPY_DIRS = ("layers", "data", "state", "docs", "scripts")


class Blocked(RuntimeError):
    """Raised by any attempt to reach the network / spawn a process."""


@pytest.fixture(scope="session")
def repo_copy(tmp_path_factory):
    root = tmp_path_factory.mktemp("repo")
    for d in _COPY_DIRS:
        src = os.path.join(REAL_ROOT, d)
        if not os.path.isdir(src):
            continue
        shutil.copytree(
            src, root / d,
            ignore=lambda _dir, names: [n for n in names if n.endswith(".html") or n == "__pycache__"],
        )
    return root


@pytest.fixture
def fake_repo(tmp_path):
    """Empty repo skeleton for tests that supply their own inputs."""
    for d in ("layers", "data", "state", "docs", "scripts"):
        (tmp_path / d).mkdir()
    return tmp_path


@pytest.fixture
def offline(monkeypatch, tmp_path):
    import subprocess
    import urllib.request

    def boom(*a, **k):
        raise Blocked("network/process access attempted")

    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return boom


def load_script(name, root, argv=None, run_name=None, globals_override=None):
    """Execute scripts/<name>.py with __file__ under *root*.

    Returns the module namespace. With run_name="__main__" the main-guard runs.
    """
    real = os.path.join(REAL_ROOT, "scripts", name + ".py")
    src = open(real, encoding="utf-8").read()
    # Keep line numbers identical. ``__file__`` stays the REAL path (coverage
    # keys on it); ROOT derivation uses ``__FAKE_FILE__`` instead. sys.path
    # bootstrap lines keep the real scripts dir so sibling imports resolve.
    src = "\n".join(
        ln if "sys.path" in ln else ln.replace("__file__", "__FAKE_FILE__")
        for ln in src.split("\n"))
    fake_file = os.path.join(str(root), "scripts", name + ".py")
    mod = types.ModuleType(run_name or name)
    mod.__file__ = real
    ns = mod.__dict__
    ns["__FAKE_FILE__"] = fake_file
    if globals_override:
        ns.update(globals_override)
    old_argv = sys.argv
    old_mod = sys.modules.get(mod.__name__)
    sys.argv = [fake_file] + list(argv or [])
    sys.modules[mod.__name__] = mod
    try:
        exec(compile(src, real, "exec"), ns)
    finally:
        sys.argv = old_argv
        if old_mod is None:
            sys.modules.pop(mod.__name__, None)
        else:
            sys.modules[mod.__name__] = old_mod
    return mod


def copy_script(root, *names):
    """Place real sibling scripts into a fake repo (for importlib-by-path users)."""
    for n in names:
        shutil.copy(os.path.join(REAL_ROOT, "scripts", n + ".py"),
                    os.path.join(str(root), "scripts", n + ".py"))


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Hard guarantee that no test reaches the network (requests/urllib/curl)."""
    import socket

    def deny(*a, **k):
        raise Blocked("socket use is forbidden in tests")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)


def _snapshot(root):
    out = {}
    for d in _COPY_DIRS:
        for dp, _, fs in os.walk(os.path.join(str(root), d)):
            for f in fs:
                p = os.path.join(dp, f)
                st = os.stat(p)
                out[p] = (st.st_size, st.st_mtime_ns)
    return out


@pytest.fixture(scope="session")
def _repo_copy(tmp_path_factory):
    """ONE throw-away copy of layers/data/state/docs per test session."""
    root = tmp_path_factory.mktemp("repo_copy") / "repo"
    root.mkdir()
    for d in _COPY_DIRS:
        src = os.path.join(REAL_ROOT, d)
        if os.path.isdir(src):
            shutil.copytree(src, root / d, ignore=shutil.ignore_patterns("__pycache__"))
    return root


@pytest.fixture
def work_repo(_repo_copy, tmp_path, monkeypatch):
    """Shared session copy of the data dirs. After each test, anything a builder
    changed, added or removed is restored from the real repo, so tests stay isolated."""
    before = _snapshot(_repo_copy)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    yield _repo_copy
    after = _snapshot(_repo_copy)
    rr = str(_repo_copy)
    for p in set(after) - set(before):
        os.remove(p)
    for p, sig in before.items():
        if after.get(p) != sig:
            src = os.path.join(REAL_ROOT, os.path.relpath(p, rr))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            shutil.copy2(src, p)
