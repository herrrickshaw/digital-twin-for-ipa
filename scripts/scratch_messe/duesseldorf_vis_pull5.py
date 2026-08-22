#!/usr/bin/env python3
"""
Pull full exhibitor rosters for 5 more Messe Duesseldorf DIMEDIS "vis"
platform fairs (boot, drupa, glasstec, A+A, Caravan Salon) and write both
JSON and CSV directly into data/trade_fairs/messe_duesseldorf/, matching
the schema used by interpack/euroshop/wire_dusseldorf
(name, country, city, location, exh, exhSeoId).

Reuses the exact fetch pattern confirmed working in
scripts/scratch_messe/duesseldorf_vis_pull.py.
"""
import csv
import json
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BUCKETS = list("abcdefghijklmnopqrstuvwxyz") + ["other"]
OUT_DIR = "/Users/umashankar/digital-twin-for-ipa/data/trade_fairs/messe_duesseldorf"

FAIRS = [
    ("boot", "www.boot.com"),
    ("drupa", "www.drupa.com"),
    ("glasstec", "www.glasstec.de"),
    ("a_a", "www.aplusa-online.com"),
    ("caravan_salon", "www.caravan-salon.com"),
]


def fetch(domain, path):
    url = f"https://{domain}/vis-api/vis/v1/en/{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "X-Vis-Domain": f"https://{domain}",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pull(domain, out_key):
    meta = fetch(domain, "directory/meta")
    filled = [b["link"] for b in meta.get("links", []) if b.get("isFilled")]
    print(f"  meta: {len(filled)} filled buckets of {len(meta.get('links', []))}")

    all_records = []
    for bucket in BUCKETS:
        if bucket not in filled:
            continue
        try:
            data = fetch(domain, f"directory/{bucket}")
        except Exception as e:
            print(f"  ERROR bucket {bucket}: {e}", file=sys.stderr)
            continue
        n = len(data) if isinstance(data, list) else 0
        print(f"  bucket {bucket}: {n} entries")
        if isinstance(data, list):
            for item in data:
                all_records.append({
                    "name": item.get("name"),
                    "country": item.get("country"),
                    "city": item.get("city"),
                    "location": item.get("location"),
                    "exh": item.get("exh"),
                    "exhSeoId": item.get("exhSeoId"),
                })
        time.sleep(0.3)

    json_path = f"{OUT_DIR}/{out_key}_exhibitors.json"
    with open(json_path, "w") as f:
        json.dump({"domain": domain, "collected": len(all_records), "records": all_records}, f, indent=2)
    print(f"Wrote {len(all_records)} records to {json_path}")

    csv_path = f"{OUT_DIR}/{out_key}_exhibitors.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "country", "city", "location", "exh", "exhSeoId"])
        writer.writeheader()
        for rec in all_records:
            writer.writerow(rec)
    print(f"Wrote {len(all_records)} records to {csv_path}")

    # country breakdown for README reporting
    from collections import Counter
    counts = Counter(r["country"] for r in all_records if r.get("country"))
    top5 = counts.most_common(5)
    india = counts.get("India", 0)
    return len(all_records), top5, india


if __name__ == "__main__":
    results = {}
    for out_key, domain in FAIRS:
        print(f"Pulling {out_key} from {domain} ...")
        try:
            total, top5, india = pull(domain, out_key)
            results[out_key] = {"domain": domain, "total": total, "top5": top5, "india": india}
        except Exception as e:
            print(f"FAILED {out_key}: {e}", file=sys.stderr)
            results[out_key] = {"domain": domain, "error": str(e)}
        print()
    print("=== SUMMARY ===")
    print(json.dumps(results, indent=2))
