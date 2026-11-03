"""Characterisation of build_layer41_association_leads_crossref.load_raw_sources on synthetic exhibitor files."""
import json
import os

import build_layer41_association_leads_crossref as l41
from conftest import sha

GOLDEN = ('c2e9a24035d86955e82695100466991cd63e6db3ba4e24bda61a039d1b9432be', 13)


def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_load_raw_sources_identical(tmp_path, monkeypatch):
    scratch, root = tmp_path / "scratch", tmp_path / "root"
    _w(f"{scratch}/pdfs/aeroindia2019_foreign.txt", "  1  Airbus Defence*   FRANCE   \nheader line\n  2  Saab AB    SWEDEN  \n")
    _w(f"{scratch}/semicon_india_2025_names.txt", "Applied Materials\n\n  Lam Research \n")
    _w(f"{scratch}/pdfs/aahar2024.txt", "junk\nHALL NO. 1\n 1  Barilla   Italy\n 2  Nestle  CH\n  HALL 2 GROUND FLOOR\n 3  Other  X\n")
    _w(f"{scratch}/textile_pdfs/india_itme_2022_exhibitors.txt", "INTERNATIONAL Rieter AG   Winterthur\nINTERNATIONAL SPINNING\nINTERNATIONAL  Ab\nlocal Co\n")
    tf = f"{root}/data/trade_fairs"
    _w(f"{tf}/railways/innotrans_2026_exhibitors.csv", "company,country\nSiemens Mobility,Germany\nAlstom,France\n")
    _w(f"{tf}/railways/iree_2025_key_exhibitors.json", json.dumps([
        {"company": "Wabtec", "origin_flag": "FOREIGN_PARENT"}, {"company": "Merged", "origin_flag": "FOREIGN", "possible_merge_artifact": True},
        {"company": "Local", "origin_flag": "INDIAN"}]))
    _w(f"{tf}/messe_frankfurt/ish_exhibitors.csv", "name,country_label\nGrohe,Germany\n,Nowhere\n")
    _w(f"{tf}/messe_duesseldorf/drupa_exhibitors.csv", "name,country\nHeidelberg,Germany\n")
    _w(f"{tf}/india_domestic/iijs/iijs_participants.json", json.dumps([{"name": "Tiffany", "country_or_origin": "US", "origin_flag": "FOREIGN"}, {"name": "Desi", "origin_flag": "INDIAN"}]))
    _w(f"{tf}/india_domestic/convergence_india/convergence_india_participants_foreign_only.json", json.dumps({"participants": [{"name": "Huawei", "country_origin": "China"}]}))
    _w(f"{tf}/india_domestic/iitf/iitf_participants.json", json.dumps({"company_level_exhibitors": {"records": [{"name": "Iran Carpet", "country_origin": "Iran"}]}}))
    _w(f"{tf}/india_domestic/cement_expo/cement_expo_participants.json", json.dumps({"participants": [{"name": "FLSmidth", "origin_flag": "FOREIGN_PARENT"}, {"name": "X", "origin_flag": "INDIAN"}]}))
    _w(f"{tf}/india_domestic/india_mobile_congress/india_mobile_congress_participants.json", json.dumps({"participants": [{"name": "Ericsson", "country_origin": "SE", "flag_basis": "FOREIGN name"}, {"name": "Y", "flag_basis": "none"}]}))
    monkeypatch.setattr(l41, "ROOT", str(root))
    monkeypatch.setattr(l41, "SCRATCH", str(scratch))
    rows = l41.load_raw_sources()
    blob = json.dumps(list(rows.items()), ensure_ascii=False)
    assert (sha(blob), len(rows)) == GOLDEN
