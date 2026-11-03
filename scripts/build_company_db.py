#!/usr/bin/env python3
"""Layer 32 — company database.

Consolidates every company the twin has touched — scattered across seven
layers with no unified view — into one queryable SQLite database with
per-record provenance, then writes a summary layer JSON.

Sources merged (all local, no network):
  16_leads.json                321 foreign/listed leads (scored, ticker, lanes)
  16_target_shortlist.json     136 shortlisted targets (tiered)
  24_clearance_leads.json       98 India EC/FC filers (news verdict, credit ratings)
  24b_pool_policy_triage.json 1384 EC-filer pool mapped to policy programs
  24e_pool_visibility_sweep.json 1343 pool visibility verdicts
  21_indian_entity_alias_check.json 18 foreign-parent alias probes
  07_investor_pairings.json     19 verified/prospective initiative pairings
  46_pli_bulk_drugs_commercial.json 51 PLI Bulk Drugs company-level projects (capacity, commercial status)
  47_telangana_pharma_cluster.json 35 plant-location resolutions for layer 46 (Telangana cross-ref)
  49_medical_devices_parks.json 22 PLI Medical Devices approved projects + park occupancy cross-ref
  50_textile_defence_parks.json 8 PLI Textiles foreign companies + PM MITRA/defence corridor tenants

Identity: companies are deduped on a normalized name (legal suffixes stripped)
+ country. Every source row is kept verbatim in company_sources (payload JSON),
so nothing is flattened away — the companies table is a join key, not a
replacement for the layer evidence.

Usage:  python3 scripts/build_company_db.py
Output: data/companies.db + layers/32_company_db.json
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date

from twin_common import norm_company

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, "layers")
DATA = os.path.join(ROOT, "data")
DB_PATH = os.path.join(DATA, "companies.db")
OUT_LAYER = os.path.join(LAYERS, "32_company_db.json")

SCHEMA_SQL = """
        CREATE TABLE companies (
            company_id   INTEGER PRIMARY KEY,
            name         TEXT NOT NULL,      -- best display name seen
            name_norm    TEXT NOT NULL,      -- dedup key (suffixes stripped)
            country      TEXT,               -- ISO-ish country, 'India' for domestic filers
            sector       TEXT,
            ticker       TEXT,
            market       TEXT,
            is_india_entity INTEGER,         -- 1 = domestic EC/FC filer pool
            UNIQUE(name_norm, country)
        );
        CREATE TABLE company_sources (       -- provenance: one row per (company, layer-role)
            company_id  INTEGER REFERENCES companies(company_id),
            layer       TEXT NOT NULL,       -- e.g. '16_leads', '24_clearance_leads'
            role        TEXT NOT NULL,       -- foreign_lead | shortlist_target | clearance_lead |
                                             -- pool_policy | pool_visibility | alias_check | pairing
            as_of       TEXT,                -- layer build date
            payload     TEXT NOT NULL        -- the source record, verbatim JSON
        );
        CREATE TABLE credit_ratings (        -- layer 24 rating-rationale channel
            company_id  INTEGER REFERENCES companies(company_id),
            agency      TEXT,                -- CARE | CRISIL | ICRA | India Ratings | UNRATED
            rating      TEXT,
            rating_date TEXT,
            rated_by_care INTEGER,
            capex_disclosure TEXT,
            rationale_url TEXT,
            adds_beyond_news TEXT,
            care_check  TEXT                 -- tier-3 care_check block, JSON
        );
        CREATE TABLE clearance_activity (    -- PARIVESH EC/FC footprint
            company_id  INTEGER REFERENCES companies(company_id),
            filings     INTEGER,
            states      TEXT,                -- JSON list
            activity    TEXT,
            policy_program TEXT,
            latest      TEXT,
            visibility_verdict TEXT,         -- ANNOUNCED | PARTIALLY_VISIBLE | QUIET
            pool_score  REAL
        );
        CREATE TABLE lead_scores (
            company_id  INTEGER REFERENCES companies(company_id),
            layer       TEXT,
            score       REAL,
            tier        TEXT
        );
        CREATE VIEW company_card AS
            SELECT c.company_id, c.name, c.country, c.sector, c.ticker,
                   c.is_india_entity,
                   group_concat(DISTINCT s.layer)  AS layers,
                   group_concat(DISTINCT s.role)   AS roles,
                   (SELECT COALESCE(rating, agency)
                      FROM credit_ratings r WHERE r.company_id = c.company_id
                     LIMIT 1)                      AS credit_rating,
                   (SELECT visibility_verdict FROM clearance_activity a
                     WHERE a.company_id = c.company_id
                       AND a.visibility_verdict IS NOT NULL LIMIT 1) AS visibility,
                   (SELECT MAX(score) FROM lead_scores l
                     WHERE l.company_id = c.company_id) AS best_score
              FROM companies c
              LEFT JOIN company_sources s USING (company_id)
             GROUP BY c.company_id;
        """

norm = norm_company  # kept under its historical name for importers of this module


def load(fname):
    """Parse ``layers/<fname>`` (JSON)."""
    with open(os.path.join(LAYERS, fname)) as f:
        return json.load(f)


class CompanyStore:
    """Thin wrapper over the SQLite cursor: identity upsert + provenance rows."""

    def __init__(self, cur):
        self.cur = cur

    def upsert(self, name, country=None, sector=None, ticker=None, market=None, india=0):
        """Return the company_id for (normalised name, country), creating/filling the row."""
        cur = self.cur
        key = (norm(name), country or "")
        cur.execute(
            "SELECT company_id, name FROM companies WHERE name_norm=? AND COALESCE(country,'')=?",
            key,
        )
        row = cur.fetchone()
        if row:
            cid = row[0]
            # fill blanks, keep longest display name
            if len(name) > len(row[1]):
                cur.execute("UPDATE companies SET name=? WHERE company_id=?", (name, cid))
            for col, val in (("sector", sector), ("ticker", ticker), ("market", market)):
                if val:
                    cur.execute(
                        f"UPDATE companies SET {col}=COALESCE({col},?) WHERE company_id=?",
                        (val, cid),
                    )
            if india:
                cur.execute(
                    "UPDATE companies SET is_india_entity=1 WHERE company_id=?", (cid,)
                )
            return cid
        cur.execute(
            "INSERT INTO companies(name,name_norm,country,sector,ticker,market,is_india_entity)"
            " VALUES (?,?,?,?,?,?,?)",
            (name, key[0], country, sector, ticker, market, india),
        )
        return cur.lastrowid

    def source(self, cid, layer, role, as_of, rec):
        """Record the verbatim source record ``rec`` as provenance for company ``cid``."""
        self.cur.execute(
            "INSERT INTO company_sources VALUES (?,?,?,?,?)",
            (cid, layer, role, as_of, json.dumps(rec, ensure_ascii=False)),
        )


# ---- one ingester per source layer (run in this order; order fixes company_id) ----

def ingest_leads(st):
    """16_leads: foreign/listed scored leads."""
    d = load("16_leads.json")
    for r in d["leads"]:
        cid = st.upsert(r["company"], r.get("country"), r.get("sector"),
                        r.get("ticker"), r.get("market"))
        st.source(cid, "16_leads", "foreign_lead", d.get("built"), r)
        if r.get("lead_score") is not None:
            st.cur.execute("INSERT INTO lead_scores VALUES (?,?,?,?)",
                           (cid, "16_leads", r["lead_score"], None))


def ingest_shortlist(st):
    """16_target_shortlist."""
    d = load("16_target_shortlist.json")
    for r in d["targets"]:
        cid = st.upsert(r["company"], r.get("country"), r.get("sector"), r.get("ticker"))
        st.source(cid, "16_target_shortlist", "shortlist_target", d.get("built"), r)
        st.cur.execute("INSERT INTO lead_scores VALUES (?,?,?,?)",
                       (cid, "16_target_shortlist", r.get("target_score"), r.get("tier")))


def ingest_clearance_leads(st):
    """24_clearance_leads: India filers + credit ratings."""
    d = load("24_clearance_leads.json")
    for r in d["leads"]:
        cid = st.upsert(r["company"], "India", india=1)
        st.source(cid, "24_clearance_leads", "clearance_lead", d.get("built"), r)
        cr = r.get("credit_rating")
        if cr:
            rating = cr.get("rating") or cr.get("care_rating")
            agency = ("CARE" if cr.get("rated_by_care")
                      else (rating or "").split()[0] if rating else
                      ("UNRATED" if cr.get("unrated") else None))
            st.cur.execute(
                "INSERT INTO credit_ratings VALUES (?,?,?,?,?,?,?,?,?)",
                (cid, agency, rating, cr.get("rating_date"),
                 1 if cr.get("rated_by_care") else 0,
                 cr.get("rationale_capex_disclosure"),
                 cr.get("rationale_url"), cr.get("adds_beyond_news"),
                 json.dumps(cr.get("care_check"), ensure_ascii=False)
                 if cr.get("care_check") else None),
            )
        st.cur.execute(
            "INSERT INTO clearance_activity(company_id,visibility_verdict,policy_program)"
            " VALUES (?,?,?)",
            (cid, r.get("news_verdict"), r.get("policy_program")),
        )


def ingest_pool_policy(st):
    """24b pool: policy triage."""
    d = load("24b_pool_policy_triage.json")
    for r in d["companies"]:
        cid = st.upsert(r["company"], "India", india=1)
        st.source(cid, "24b_pool_policy_triage", "pool_policy", d.get("built"), r)
        st.cur.execute(
            "INSERT INTO clearance_activity"
            "(company_id,filings,states,activity,policy_program,latest,pool_score)"
            " VALUES (?,?,?,?,?,?,?)",
            (cid, r.get("filings"),
             json.dumps(r.get("states"), ensure_ascii=False),
             r.get("activity"), r.get("policy_program"), r.get("latest"),
             r.get("score")),
        )


def ingest_pool_visibility(st):
    """24e pool: visibility sweep."""
    d = load("24e_pool_visibility_sweep.json")
    for r in d["companies"]:
        cid = st.upsert(r["company"], "India", india=1)
        st.source(cid, "24e_pool_visibility_sweep", "pool_visibility", d.get("built"), r)
        st.cur.execute(
            "UPDATE clearance_activity SET visibility_verdict=COALESCE(visibility_verdict,?)"
            " WHERE company_id=?",
            (r.get("verdict"), cid),
        )


def ingest_alias_check(st):
    """21 alias check."""
    d = load("21_indian_entity_alias_check.json")
    for r in d["companies"]:
        cid = st.upsert(r["parent"])
        st.source(cid, "21_indian_entity_alias_check", "alias_check", d.get("built"), r)


def ingest_pairings(st):
    """07 pairings."""
    d = load("07_investor_pairings.json")
    for role, key in (("pairing_verified", "verified_pairs"),
                      ("pairing_prospective", "prospective_pairs")):
        for r in d.get(key, []):
            cid = st.upsert(r["company"], sector=r.get("sector"), ticker=r.get("ticker"))
            st.source(cid, "07_investor_pairings", role, d.get("retrieved"), r)


def ingest_pli_bulk_drugs(st):
    """46 PLI Bulk Drugs: company-level approved projects."""
    d = load("46_pli_bulk_drugs_commercial.json")
    for r in d["company_projects"]:
        cid = st.upsert(r["company"], "India", sector="Pharma & Bulk Drugs", india=1)
        st.source(cid, "46_pli_bulk_drugs_commercial", "pli_bulk_drugs_beneficiary", d.get("built"), r)


def ingest_telangana_pharma(st):
    """47 Telangana pharma cluster: plant-location cross-reference."""
    d = load("47_telangana_pharma_cluster.json")
    for r in d["company_locations"]:
        cid = st.upsert(r["company"], "India", sector="Pharma & Bulk Drugs", india=1)
        st.source(cid, "47_telangana_pharma_cluster", "plant_location_check", d.get("built"), r)


def ingest_medical_devices(st):
    """49 PLI Medical Devices + parks cross-reference."""
    d = load("49_medical_devices_parks.json")
    for r in d["pli_medical_devices_approved"]:
        cid = st.upsert(r["company"], "India", sector="Medical Devices", india=1)
        st.source(cid, "49_medical_devices_parks", "pli_medical_devices_beneficiary", d.get("built"), r)


def ingest_textile_defence(st):
    """50 PM MITRA + Defence Corridors cross-reference."""
    d = load("50_textile_defence_parks.json")
    for r in d["pli_textiles_foreign_corrected_roster"]:
        cid = st.upsert(r["company"], r.get("country"), sector="Textiles & Apparel")
        st.source(cid, "50_textile_defence_parks", "pli_textiles_foreign_beneficiary", d.get("built"), r)
    for corridor in d["defence_industrial_corridors"]:
        for tenant in corridor["named_tenants"]:
            name = tenant.split(" (")[0].split(" --")[0].strip()
            cid = st.upsert(name, "India", sector="Defence")
            st.source(cid, "50_textile_defence_parks", "defence_corridor_tenant", d.get("built"),
                      {"corridor": corridor["corridor"], "raw": tenant})


INGESTERS = (
    ingest_leads, ingest_shortlist, ingest_clearance_leads, ingest_pool_policy,
    ingest_pool_visibility, ingest_alias_check, ingest_pairings, ingest_pli_bulk_drugs,
    ingest_telangana_pharma, ingest_medical_devices, ingest_textile_defence,
)

SOURCE_LAYERS = ["16_leads", "16_target_shortlist", "24_clearance_leads",
                 "24b_pool_policy_triage", "24e_pool_visibility_sweep",
                 "21_indian_entity_alias_check", "07_investor_pairings",
                 "46_pli_bulk_drugs_commercial", "47_telangana_pharma_cluster",
                 "49_medical_devices_parks", "50_textile_defence_parks"]


def build_database(db_path=None):
    """(Re)create the SQLite database from the source layers; returns the open connection."""
    db_path = db_path or DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.cursor().executescript(SCHEMA_SQL)
    store = CompanyStore(con.cursor())
    for ingest in INGESTERS:
        ingest(store)
    con.commit()
    return con


def build_summary(cur, built):
    """Layer-32 summary dict (counts, schema notes, sources) computed from the database."""
    q = lambda sql: cur.execute(sql).fetchall()  # noqa: E731
    n_companies = q("SELECT COUNT(*) FROM companies")[0][0]
    multi = q("SELECT COUNT(*) FROM (SELECT company_id FROM company_sources"
              " GROUP BY company_id HAVING COUNT(DISTINCT layer)>1)")[0][0]
    return {
        "layer": 32,
        "name": "company_db",
        "built": built,
        "what": ("Unified company database: every company the twin has touched, "
                 "deduped on normalized-name+country, with per-record provenance "
                 "(company_sources keeps each source layer's record verbatim). "
                 "SQLite at data/companies.db; company_card view = one row per company."),
        "db_path": "data/companies.db",
        "counts": {
            "companies": n_companies,
            "in_more_than_one_layer": multi,
            "by_role": {r: c for r, c in q(
                "SELECT role, COUNT(DISTINCT company_id) FROM company_sources GROUP BY role")},
            "india_entities": q("SELECT COUNT(*) FROM companies WHERE is_india_entity=1")[0][0],
            "credit_rated": q("SELECT COUNT(DISTINCT company_id) FROM credit_ratings"
                              " WHERE rating IS NOT NULL")[0][0],
            "by_country_top10": {k or "?": v for k, v in q(
                "SELECT country, COUNT(*) FROM companies GROUP BY country"
                " ORDER BY 2 DESC LIMIT 10")},
        },
        "schema": {
            "companies": "canonical identity (name, name_norm, country, sector, ticker, is_india_entity)",
            "company_sources": "provenance — (layer, role, as_of, payload verbatim JSON)",
            "credit_ratings": "layer-24 rating channel (agency, rating, capex disclosure, rationale URL, care_check)",
            "clearance_activity": "PARIVESH footprint (filings, states, activity, policy program, visibility verdict)",
            "lead_scores": "scores from 16/16ts",
            "company_card": "VIEW — one row per company joining all of the above",
        },
        "identity_rule": ("dedup key = lowercased name with legal suffixes stripped "
                          "(Ltd/Pvt/GmbH/Inc/...) + country; overlaps across layers "
                          "merge, same-name different-country stay separate"),
        "sources": list(SOURCE_LAYERS),
        "enrichment_next": ("layer 31 catalogs the external IPA/NDAP sources whose "
                            "company-level material (Invest India sector pages, IIG "
                            "project sponsors, state-IPA investor lists) can be joined "
                            "onto company_id"),
    }


def main():
    con = build_database()
    summary = build_summary(con.cursor(), date.today().isoformat())
    with open(OUT_LAYER, "w") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    con.close()
    print(json.dumps(summary["counts"], indent=1))
    print("wrote", DB_PATH, "and", OUT_LAYER)


if __name__ == "__main__":
    main()
