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

Identity: companies are deduped on a normalized name (legal suffixes stripped)
+ country. Every source row is kept verbatim in company_sources (payload JSON),
so nothing is flattened away — the companies table is a join key, not a
replacement for the layer evidence.

Usage:  python3 scripts/build_company_db.py
Output: data/companies.db + layers/32_company_db.json
"""
import json
import os
import re
import sqlite3
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, "layers")
DATA = os.path.join(ROOT, "data")
DB_PATH = os.path.join(DATA, "companies.db")
OUT_LAYER = os.path.join(LAYERS, "32_company_db.json")

SUFFIXES = re.compile(
    r"\b(private|pvt|limited|ltd|llp|llc|inc|incorporated|corp|corporation|plc|"
    r"co|company|gmbh|ag|sa|nv|bv|ab|as|asa|oyj|spa|kk|pte|sdn bhd|holdings?)\b\.?",
    re.I,
)


def norm(name: str) -> str:
    s = (name or "").lower()
    s = re.sub(r"^m\s*/\s*s\.?\s+", "", s)  # strip "M/s " register prefix
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = SUFFIXES.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def load(fname):
    with open(os.path.join(LAYERS, fname)) as f:
        return json.load(f)


def main():
    os.makedirs(DATA, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(
        """
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
    )

    def upsert(name, country=None, sector=None, ticker=None, market=None, india=0):
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

    def src(cid, layer, role, as_of, rec):
        cur.execute(
            "INSERT INTO company_sources VALUES (?,?,?,?,?)",
            (cid, layer, role, as_of, json.dumps(rec, ensure_ascii=False)),
        )

    # ---- 16_leads: foreign/listed scored leads -------------------------------
    d = load("16_leads.json")
    for r in d["leads"]:
        cid = upsert(r["company"], r.get("country"), r.get("sector"),
                     r.get("ticker"), r.get("market"))
        src(cid, "16_leads", "foreign_lead", d.get("built"), r)
        if r.get("lead_score") is not None:
            cur.execute("INSERT INTO lead_scores VALUES (?,?,?,?)",
                        (cid, "16_leads", r["lead_score"], None))

    # ---- 16_target_shortlist -------------------------------------------------
    d = load("16_target_shortlist.json")
    for r in d["targets"]:
        cid = upsert(r["company"], r.get("country"), r.get("sector"), r.get("ticker"))
        src(cid, "16_target_shortlist", "shortlist_target", d.get("built"), r)
        cur.execute("INSERT INTO lead_scores VALUES (?,?,?,?)",
                    (cid, "16_target_shortlist", r.get("target_score"), r.get("tier")))

    # ---- 24_clearance_leads: India filers + credit ratings -------------------
    d = load("24_clearance_leads.json")
    for r in d["leads"]:
        cid = upsert(r["company"], "India", india=1)
        src(cid, "24_clearance_leads", "clearance_lead", d.get("built"), r)
        cr = r.get("credit_rating")
        if cr:
            rating = cr.get("rating") or cr.get("care_rating")
            agency = ("CARE" if cr.get("rated_by_care")
                      else (rating or "").split()[0] if rating else
                      ("UNRATED" if cr.get("unrated") else None))
            cur.execute(
                "INSERT INTO credit_ratings VALUES (?,?,?,?,?,?,?,?,?)",
                (cid, agency, rating, cr.get("rating_date"),
                 1 if cr.get("rated_by_care") else 0,
                 cr.get("rationale_capex_disclosure"),
                 cr.get("rationale_url"), cr.get("adds_beyond_news"),
                 json.dumps(cr.get("care_check"), ensure_ascii=False)
                 if cr.get("care_check") else None),
            )
        cur.execute(
            "INSERT INTO clearance_activity(company_id,visibility_verdict,policy_program)"
            " VALUES (?,?,?)",
            (cid, r.get("news_verdict"), r.get("policy_program")),
        )

    # ---- 24b pool: policy triage --------------------------------------------
    d = load("24b_pool_policy_triage.json")
    for r in d["companies"]:
        cid = upsert(r["company"], "India", india=1)
        src(cid, "24b_pool_policy_triage", "pool_policy", d.get("built"), r)
        cur.execute(
            "INSERT INTO clearance_activity"
            "(company_id,filings,states,activity,policy_program,latest,pool_score)"
            " VALUES (?,?,?,?,?,?,?)",
            (cid, r.get("filings"),
             json.dumps(r.get("states"), ensure_ascii=False),
             r.get("activity"), r.get("policy_program"), r.get("latest"),
             r.get("score")),
        )

    # ---- 24e pool: visibility sweep -----------------------------------------
    d = load("24e_pool_visibility_sweep.json")
    for r in d["companies"]:
        cid = upsert(r["company"], "India", india=1)
        src(cid, "24e_pool_visibility_sweep", "pool_visibility", d.get("built"), r)
        cur.execute(
            "UPDATE clearance_activity SET visibility_verdict=COALESCE(visibility_verdict,?)"
            " WHERE company_id=?",
            (r.get("verdict"), cid),
        )

    # ---- 21 alias check ------------------------------------------------------
    d = load("21_indian_entity_alias_check.json")
    for r in d["companies"]:
        cid = upsert(r["parent"])
        src(cid, "21_indian_entity_alias_check", "alias_check", d.get("built"), r)

    # ---- 07 pairings ---------------------------------------------------------
    d = load("07_investor_pairings.json")
    for role, key in (("pairing_verified", "verified_pairs"),
                      ("pairing_prospective", "prospective_pairs")):
        for r in d.get(key, []):
            cid = upsert(r["company"], sector=r.get("sector"), ticker=r.get("ticker"))
            src(cid, "07_investor_pairings", role, d.get("retrieved"), r)

    con.commit()

    # ---- summary layer -------------------------------------------------------
    q = lambda sql: cur.execute(sql).fetchall()
    n_companies = q("SELECT COUNT(*) FROM companies")[0][0]
    multi = q("SELECT COUNT(*) FROM (SELECT company_id FROM company_sources"
              " GROUP BY company_id HAVING COUNT(DISTINCT layer)>1)")[0][0]
    summary = {
        "layer": 32,
        "name": "company_db",
        "built": date.today().isoformat(),
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
        "sources": ["16_leads", "16_target_shortlist", "24_clearance_leads",
                    "24b_pool_policy_triage", "24e_pool_visibility_sweep",
                    "21_indian_entity_alias_check", "07_investor_pairings"],
        "enrichment_next": ("layer 31 catalogs the external IPA/NDAP sources whose "
                            "company-level material (Invest India sector pages, IIG "
                            "project sponsors, state-IPA investor lists) can be joined "
                            "onto company_id"),
    }
    with open(OUT_LAYER, "w") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    con.close()
    print(json.dumps(summary["counts"], indent=1))
    print("wrote", DB_PATH, "and", OUT_LAYER)


if __name__ == "__main__":
    main()
