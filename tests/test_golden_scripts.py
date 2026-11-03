"""End-to-end golden hashes for the long builder scripts (captured from the code before the pass-2 split)."""
import json
import os

import pytest
from golden_runner import run_script

GOLDEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden_script_outputs.json")
SCRIPTS = [
    "build_company_directory_state_sector", "build_layer43_state_sector_convergence", "build_global_sweep_targets",
    "build_visibility_report", "build_layer35_capital_cost_lens", "build_layer40_association_event_registry",
    "build_layer46_pli_bulk_drugs", "build_layer47_telangana_pharma_cluster", "build_layer49_medical_devices_parks",
    "build_pq_registry", "build_rs_pq_registry",
]


def _golden():
    with open(GOLDEN_FILE) as f:
        return json.load(f)


@pytest.mark.parametrize("script", SCRIPTS)
def test_script_outputs_are_byte_identical(script, tmp_path):
    got = run_script(script, tmp_path)
    if os.environ.get("CAPTURE_GOLDEN"):  # one-off: regenerate from known-good code
        data = _golden() if os.path.exists(GOLDEN_FILE) else {}
        data[script] = got
        with open(GOLDEN_FILE, "w") as f:
            json.dump(data, f, indent=1, sort_keys=True)
        return
    assert got["<exit>"] == 0
    assert got == _golden()[script]
