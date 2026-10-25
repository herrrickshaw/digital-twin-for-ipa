"""Every third-party package imported at module level by a script must be
declared in requirements.txt, otherwise `pip install -r requirements.txt`
yields a venv in which that script dies with ModuleNotFoundError on import
(the 2026-10-25 import smoke hit this for 9 sweep scripts + build_target_financials)."""
import ast
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STDLIB = set(sys.stdlib_module_names)
# repo-local script modules imported by other scripts (not pip packages)
LOCAL = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(ROOT, "scripts", "*.py"))}
PKG_ALIAS = {"yaml": "pyyaml", "bs4": "beautifulsoup4", "PIL": "pillow"}


def declared_requirements():
    names = set()
    with open(os.path.join(ROOT, "requirements.txt")) as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                names.add(re.split(r"[<>=!~\[ ]", line, maxsplit=1)[0].lower().replace("-", "_"))
    return names


def module_level_third_party_imports(path):
    tree = ast.parse(open(path).read())
    out = set()
    for node in tree.body:  # module level only: guarded / lazy imports are opt-in extras
        names = []
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        for n in names:
            if n not in STDLIB and n not in LOCAL:
                out.add(PKG_ALIAS.get(n, n).lower().replace("-", "_"))
    return out


def test_every_module_level_third_party_import_is_declared():
    declared = declared_requirements()
    missing = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))):
        for mod in module_level_third_party_imports(path):
            if mod not in declared:
                missing.setdefault(mod, []).append(os.path.relpath(path, ROOT))
    assert not missing, f"imported but not in requirements.txt: {missing}"
