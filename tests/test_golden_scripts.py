"""End-to-end golden hashes for the long builder scripts (captured from the code before the pass-2 split)."""
import json
import os
import sqlite3

import pytest
from golden_runner import run_script

GOLDEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden_script_outputs.json")
SCRIPTS = [
    "build_company_directory_state_sector", "build_layer43_state_sector_convergence", "build_global_sweep_targets",
    "build_visibility_report", "build_layer35_capital_cost_lens", "build_layer40_association_event_registry",
    "build_layer46_pli_bulk_drugs", "build_layer47_telangana_pharma_cluster", "build_layer49_medical_devices_parks",
    "build_pq_registry", "build_rs_pq_registry", "build_scrutiny_matrix", "build_reportage",
]


def _synthetic_registers(work, home):
    """Synthetic PIB index (under the faked HOME) and state-news register so the reportage builders run offline."""
    d = os.path.join(home, "india-trade-sector-policy-recommendations", "data")
    os.makedirs(d)
    con = sqlite3.connect(os.path.join(d, "pib_index.sqlite"))
    con.execute("CREATE TABLE pib_items(id INTEGER, date TEXT, ministry TEXT, title TEXT)")
    titles = ["Cabinet approves Production Linked Incentive scheme for white goods", "PM Gati Shakti network planning meeting",
              "Cabinet approves Export Promotion Mission", "Production Linked Incentive scheme for Telecom progress", "Condolences on demise"]
    for i in range(40):
        con.execute("INSERT INTO pib_items VALUES (?,?,?,?)",
                    (i, "2025-%02d-%02d" % (1 + i % 12, 1 + i % 27), "Cabinet" if i % 3 == 0 else "Ministry of Commerce", titles[i % 5]))
    con.commit()
    con.close()
    os.makedirs(os.path.join(work, "data", "registers"), exist_ok=True)
    con = sqlite3.connect(os.path.join(work, "data", "registers", "state_news.sqlite"))
    con.execute("CREATE TABLE state_news(state TEXT, date TEXT, title TEXT, category TEXT, url TEXT)")
    for i, st in enumerate(["GJ", "MH", "TN", "AP"]):
        con.execute("INSERT INTO state_news VALUES (?,?,?,?,?)", (st, "2026-10-%02d" % (10 + i), "State investment policy MoU signed for industrial park %d" % i, "news", "http://x/%d" % i))
    con.commit()
    con.close()


PREPARE = {"build_scrutiny_matrix": _synthetic_registers, "build_reportage": _synthetic_registers}


def _golden():
    with open(GOLDEN_FILE) as f:
        return json.load(f)


@pytest.mark.parametrize("script", SCRIPTS)
def test_script_outputs_are_byte_identical(script, tmp_path):
    got = run_script(script, tmp_path, prepare=PREPARE.get(script))
    if os.environ.get("CAPTURE_GOLDEN"):  # one-off: regenerate from known-good code
        data = _golden() if os.path.exists(GOLDEN_FILE) else {}
        data[script] = got
        with open(GOLDEN_FILE, "w") as f:
            json.dump(data, f, indent=1, sort_keys=True)
        return
    assert got["<exit>"] == 0
    assert got == _golden()[script]
