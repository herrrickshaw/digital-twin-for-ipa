"""Shared fixtures: a miniature, offline copy of the layer files the builders read."""
import json
import os
import sys

import pytest

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS)


def write_mini_layers(layers_dir):
    """Write the smallest layer set that exercises every ingester and dashboard section."""
    layers = {
        "16_leads.json": {"built": "2026-01-01", "count": 3, "leads": [
            {"company": "Acme Holdings GmbH", "country": "Germany", "sector": "Auto", "ticker": "ACM", "market": "XETRA", "lead_score": 7.5},
            {"company": "Acme Holdings", "country": "Germany", "sector": None, "ticker": None, "market": None},
            {"company": "Acme Holdings", "country": "France"}]},
        "16_target_shortlist.json": {"built": "2026-01-02", "targets": [
            {"company": "Acme Holdings Gmbh", "country": "Germany", "target_score": 4.0, "tier": "T1"}]},
        "24_clearance_leads.json": {"built": "2026-01-03", "leads": [
            {"company": "M/s Bharat Steel Ltd.", "news_verdict": "ANNOUNCED", "policy_program": "PLI",
             "credit_rating": {"rating": "CRISIL AA", "rated_by_care": False, "rating_date": "2025-12-01"}},
            {"company": "Desi Foods Pvt Ltd", "credit_rating": {"unrated": True}}]},
        "24b_pool_policy_triage.json": {"built": "2026-01-04", "companies": [
            {"company": "Bharat Steel Limited", "filings": 3, "states": ["GJ", "MH"], "activity": "expansion",
             "policy_program": "PLI", "latest": "2025-11-01", "score": 2.5}]},
        "24e_pool_visibility_sweep.json": {"built": "2026-01-05", "companies": [
            {"company": "Bharat Steel Ltd", "verdict": "QUIET"}]},
        "21_indian_entity_alias_check.json": {"built": "2026-01-06", "companies": [{"parent": "Acme Corp"}]},
        "07_investor_pairings.json": {"retrieved": "2026-01-07",
                                      "verified_pairs": [{"company": "Zeta Inc", "sector": "Chips", "ticker": "ZT"}],
                                      "prospective_pairs": [{"company": "Zeta Incorporated"}]},
        "46_pli_bulk_drugs_commercial.json": {"built": "2026-01-08", "company_projects": [{"company": "PharmaOne Ltd"}]},
        "47_telangana_pharma_cluster.json": {"built": "2026-01-09", "company_locations": [{"company": "PharmaOne Limited"}]},
        "49_medical_devices_parks.json": {"built": "2026-01-10", "pli_medical_devices_approved": [{"company": "MedDev Pvt Ltd"}]},
        "50_textile_defence_parks.json": {
            "built": "2026-01-11",
            "pli_textiles_foreign_corrected_roster": [{"company": "Fabric AG", "country": "Switzerland"}],
            "defence_industrial_corridors": [{"corridor": "UP", "named_tenants": ["Tenant One (JV) x", "Tenant Two -- note"]}]},
        "44_state_mou_5yr_sweep.json": {
            "total_mous": 2, "total_new_to_twin": 1,
            "follow_through_breakdown": {"no follow-up news found": 1},
            "by_state": {"Gujarat": {"mous": [
                {"company": "Acme <Co>", "state": "Gujarat", "sector": "Auto", "country_of_headquarters": "Germany",
                 "follow_through_status": "operational -- plant live", "source_url": "https://e.x/a;https://e.x/b",
                 "mou_date": "2025-01-10", "proposed_investment": "INR 100 cr", "confidence": "HIGH"},
                {"company": "Old Co", "state": "Gujarat", "mou_date": "2021-03-01",
                 "follow_through_status": "no follow-up news found"}]}}},
        "40_association_event_registry.json": {"events": [1, 2], "associations": [1]},
        "42_sector_investment_news_sweep.json": {"total_findings": 5},
        "43_state_sector_convergence.json": {"state_convergence": [1, 2, 3]},
        "02_incentive_catalog_v1.json": {"items": [1, 2, 3, 4]},
        "99_scalar_list.json": [1, 2, 3],
    }
    os.makedirs(layers_dir, exist_ok=True)
    for name, doc in layers.items():
        with open(os.path.join(layers_dir, name), "w") as f:
            json.dump(doc, f)


@pytest.fixture
def mini_root(tmp_path):
    """A temp repo root with miniature layers/ (and data/ to be filled by the builders)."""
    write_mini_layers(str(tmp_path / "layers"))
    return tmp_path
