"""Helpers shared by the layer-building scripts (stdlib only).

Kept deliberately small: repo paths, company-name normalisation and the
"which companies does the twin already know" lookup that layers 41/42/44/45
each used to carry their own copy of.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_LEGAL_SUFFIXES = re.compile(
    r"\b(private|pvt|limited|ltd|llp|llc|inc|incorporated|corp|corporation|plc|"
    r"co|company|gmbh|ag|sa|nv|bv|ab|as|asa|oyj|spa|kk|pte|sdn bhd|holdings?)\b\.?",
    re.I,
)


def norm_company(name: str | None) -> str:
    """Dedup key for a company name: lowercase, no "M/s" prefix, punctuation or legal suffixes."""
    s = (name or "").lower()
    s = re.sub(r"^m\s*/\s*s\.?\s+", "", s)  # strip "M/s " register prefix
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = _LEGAL_SUFFIXES.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def known_company_names(root: str = ROOT, tolerate_db_errors: bool = False) -> set:
    """Lower-cased names of every company in layer 16 leads plus data/companies.db (if present)."""
    names = set()
    leads_path = os.path.join(root, "layers", "16_leads.json")
    if os.path.exists(leads_path):
        for lead in json.load(open(leads_path))["leads"]:
            names.add(lead["company"].strip().lower())
    db = os.path.join(root, "data", "companies.db")
    if os.path.exists(db):
        try:
            con = sqlite3.connect(db)
            for (n,) in con.execute("SELECT name FROM companies"):
                if n:
                    names.add(n.strip().lower())
            con.close()
        except sqlite3.Error:
            if not tolerate_db_errors:
                raise
    return names
