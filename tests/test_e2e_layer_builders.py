"""End-to-end: run the offline layer builders on a copy of the repo's real inputs
and check the JSON they write is structurally sound (non-empty lists, counts
that equal list lengths). Network is blocked by the autouse fixture."""
import glob
import json
import os

import pytest

from conftest import load_script

BUILDERS = [
    "build_layer46_pli_bulk_drugs",
    "build_layer47_telangana_pharma_cluster",
    "build_layer48_state_pharma_clusters",
    "build_layer49_medical_devices_parks",
    "build_layer50_textile_defence_parks",
    "build_layer51_semiconductor_parks",
]


def _jsons(root):
    return {p: os.stat(p).st_mtime_ns
            for p in glob.glob(os.path.join(str(root), "layers", "*.json"))}


@pytest.mark.parametrize("name", BUILDERS)
def test_builder_writes_wellformed_layer(name, work_repo):
    before = _jsons(work_repo)
    load_script(name, work_repo, run_name="__main__")
    after = _jsons(work_repo)
    written = [p for p, m in after.items() if before.get(p) != m]
    assert written, f"{name} wrote no layer JSON"
    for p in written:
        data = json.load(open(p, encoding="utf-8"))
        assert isinstance(data, dict) and data
        lists = {k: v for k, v in data.items() if isinstance(v, list)}
        assert lists, f"{p} has no list payload"
        assert any(v for v in lists.values()), f"{p} payload lists are all empty"
        for k, v in data.items():
            if isinstance(v, int) and not isinstance(v, bool) and k.endswith("count"):
                stem = k[: -len("count")].rstrip("_")
                for lk, lv in lists.items():
                    if lk == stem or lk == stem + "s":
                        assert v == len(lv), f"{p}: {k}={v} != len({lk})={len(lv)}"
