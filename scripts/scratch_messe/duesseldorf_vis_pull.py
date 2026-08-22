#!/usr/bin/env python3
"""
Pull full exhibitor rosters from the Messe Duesseldorf shared "DIMEDIS vis"
directory platform: <domain>/vis-api/vis/v1/en/directory/<a-z|other>

Confirmed 2026-08-22 via live browser network capture on interpack.com's
/vis/v1/en/directory/a page. The frontend calls the API at
https://<domain>/vis-api/vis/v1/en/directory/<index> with header
'X-Vis-Domain: https://<domain>' (plain, no API key needed). Each of the
27 index buckets (a-z + "other" for numeric-start names) returns the full
company list for that bucket in one response (no further pagination
observed/needed). The valid bucket list + fill status is confirmed via
/vis-api/vis/v1/en/directory/meta.

Usage: python3 duesseldorf_vis_pull.py <domain> <output_key>
  e.g. python3 duesseldorf_vis_pull.py www.interpack.com interpack
"""
import json
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BUCKETS = list("abcdefghijklmnopqrstuvwxyz") + ["other"]


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

    out_path = f"/Users/umashankar/digital-twin-for-ipa/scripts/scratch_messe/{out_key}_exhibitors.json"
    with open(out_path, "w") as f:
        json.dump({"domain": domain, "collected": len(all_records), "records": all_records}, f, indent=2)
    print(f"Wrote {len(all_records)} records to {out_path}")


if __name__ == "__main__":
    domain = sys.argv[1]
    out_key = sys.argv[2]
    print(f"Pulling {out_key} from {domain} ...")
    pull(domain, out_key)
