#!/usr/bin/env python3
import csv
import json
import os

SCRATCH = "/Users/umashankar/digital-twin-for-ipa/scripts/scratch_messe"

MF_FAIRS = {  # Messe Frankfurt (exhibitor-service API schema)
    "lightbuilding": ("Light + Building", "messe_frankfurt"),
    "ish": ("ISH", "messe_frankfurt"),
    "heimtextil": ("Heimtextil", "messe_frankfurt"),
}

MD_FAIRS = {  # Messe Duesseldorf (vis/v1 API schema)
    "interpack": ("interpack", "messe_duesseldorf"),
    "euroshop": ("EuroShop", "messe_duesseldorf"),
    "wire_dusseldorf": ("wire & Tube Duesseldorf (combined roster)", "messe_duesseldorf"),
}

OUT_BASE = "/Users/umashankar/digital-twin-for-ipa/data/trade_fairs"


def export_mf(key, label, subdir):
    d = json.load(open(f"{SCRATCH}/{key}_exhibitors.json"))
    recs = d["records"]
    out_csv = f"{OUT_BASE}/{subdir}/{key}_exhibitors.csv"
    out_json = f"{OUT_BASE}/{subdir}/{key}_exhibitors.json"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "country_iso3", "country_label", "city", "email", "homepage", "rewriteId"])
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    with open(out_json, "w") as f:
        json.dump(d, f, indent=2)
    print(f"{label}: {len(recs)} rows -> {out_csv}")


def export_md(key, label, subdir):
    d = json.load(open(f"{SCRATCH}/{key}_exhibitors.json"))
    recs = d["records"]
    out_csv = f"{OUT_BASE}/{subdir}/{key}_exhibitors.csv"
    out_json = f"{OUT_BASE}/{subdir}/{key}_exhibitors.json"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "country", "city", "location", "exh", "exhSeoId"])
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    with open(out_json, "w") as f:
        json.dump(d, f, indent=2)
    print(f"{label}: {len(recs)} rows -> {out_csv}")


if __name__ == "__main__":
    for key, (label, subdir) in MF_FAIRS.items():
        export_mf(key, label, subdir)
    for key, (label, subdir) in MD_FAIRS.items():
        export_md(key, label, subdir)
    # tube is identical to wire -- copy under its own filename too, noted in README
    d = json.load(open(f"{SCRATCH}/tube_dusseldorf_exhibitors.json"))
    recs = d["records"]
    out_csv = f"{OUT_BASE}/messe_duesseldorf/tube_dusseldorf_exhibitors.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "country", "city", "location", "exh", "exhSeoId"])
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    print(f"tube (identical to wire): {len(recs)} rows -> {out_csv}")
