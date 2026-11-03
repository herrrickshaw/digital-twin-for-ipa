"""Run a script end-to-end in a throw-away copy of the repo and hash everything it wrote.

Used by test_golden_scripts.py: the expected hashes in golden_script_outputs.json were captured from the
pre-pass-2 code, so these tests prove the refactor left every output file (JSON layers, markdown, HTML)
and stdout byte-identical. The copy runs with the clock frozen and sockets blocked (tests/_freeze).
"""
import hashlib
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(REPO, "tests", "_freeze")
COPY_DIRS = ("scripts", "layers", "data", "docs", "state")


def _hash_tree(root):
    out = {}
    for base, _dirs, files in os.walk(root):
        if "__pycache__" in base:
            continue
        for f in files:
            p = os.path.join(base, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def run_script(script, tmp_path, args=(), prepare=None, timeout=120):
    """Copy the repo data into tmp_path, run scripts/<script>.py there; return {changed file: sha, '<stdout>': sha, '<exit>': code}."""
    work = os.path.join(str(tmp_path), "repo")
    home = os.path.join(str(tmp_path), "home")
    os.makedirs(home)
    for d in COPY_DIRS:
        src = os.path.join(REPO, d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(work, d), ignore=shutil.ignore_patterns("__pycache__"))
    if prepare:
        prepare(work, home)
    before = _hash_tree(work)
    stubs = os.path.join(str(tmp_path), "bin")
    os.makedirs(stubs)
    with open(os.path.join(stubs, "curl"), "w") as f:
        f.write("#!/bin/sh\nexit 7\n")
    os.chmod(os.path.join(stubs, "curl"), 0o755)
    env = dict(os.environ, PYTHONHASHSEED="0", HOME=home, PYTHONPATH=FREEZE, PATH=stubs + os.pathsep + os.environ.get("PATH", ""))
    proc = subprocess.run([sys.executable, os.path.join(work, "scripts", script + ".py"), *args], cwd=work, env=env,
                          capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
    after = _hash_tree(work)
    result = {k: v for k, v in after.items() if before.get(k) != v}
    result["<stdout>"] = hashlib.sha256(proc.stdout.replace(work.encode(), b"<ROOT>")).hexdigest()
    result["<exit>"] = proc.returncode
    return result
