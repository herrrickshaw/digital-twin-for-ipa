#!/usr/bin/env python3
"""
Pull full exhibitor rosters from the Messe Frankfurt shared exhibitor-search
platform (api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search).

Confirmed 2026-08-22 via live browser network capture on Automechanika Frankfurt's
exhibitor-search.html?country=IND page: the frontend calls this API with a
public apikey header baked into the SPA's main.js bundle (client-side, not secret --
same access any site visitor's browser gets). This works for ANY Messe Frankfurt fair
that runs on the same "mf-ex-root" widget -- just swap findEventVariable to the fair's
API_EVENT_ID (found in the <div id="mf-ex-root" data-config='{...API_EVENT_ID...}'>
attribute of that fair's own exhibitor-search.html page).

Usage: python3 mf_exhibitor_pull.py <FAIR_KEY>
"""
import json
import sys
import time
import urllib.parse
import urllib.request

APIKEY = "LXnMWcYQhipLAS7rImEzmZ3CkrU033FMha9cwVSngG4vbufTsAOCQQ=="
BASE = "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

FAIRS = {
    "lightbuilding": "LIGHTBUILDING",
    "ish": "ISH",
    "heimtextil": "HEIMTEXTIL",
}

PAGE_SIZE = 200


def fetch_page(event_id, page):
    params = {
        "language": "en-GB",
        "q": "",
        "orderBy": "name",
        "pageNumber": page,
        "pageSize": PAGE_SIZE,
        "orSearchFallback": "false",
        "showJumpLabels": "false",
        "findEventVariable": event_id,
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"apikey": APIKEY, "User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pull_fair(key):
    event_id = FAIRS[key]
    all_hits = []
    page = 1
    total = None
    while True:
        data = fetch_page(event_id, page)
        if not data.get("success"):
            print(f"  ERROR on page {page}: {data.get('message')}", file=sys.stderr)
            break
        result = data["result"]
        meta = result["metaData"]
        total = meta["hitsTotal"]
        hits = result["hits"]
        all_hits.extend(hits)
        print(f"  page {page}: got {len(hits)} (total so far {len(all_hits)} / {total})")
        if len(all_hits) >= total or not hits:
            break
        page += 1
        time.sleep(0.4)

    records = []
    for h in all_hits:
        ex = h.get("exhibitor", {})
        addr = ex.get("address") or {}
        country = (addr.get("country") or {})
        records.append({
            "name": ex.get("name"),
            "rewriteId": ex.get("rewriteId"),
            "city": addr.get("city"),
            "country_iso3": country.get("iso3"),
            "country_label": country.get("label"),
            "email": addr.get("email"),
            "homepage": ex.get("homepage"),
            "id": ex.get("id"),
        })
    return event_id, total, records


if __name__ == "__main__":
    key = sys.argv[1]
    print(f"Pulling {key} ({FAIRS[key]}) ...")
    event_id, total, records = pull_fair(key)
    out_path = f"/Users/umashankar/digital-twin-for-ipa/scripts/scratch_messe/{key}_exhibitors.json"
    with open(out_path, "w") as f:
        json.dump({"event_id": event_id, "hitsTotal": total, "collected": len(records), "records": records}, f, indent=2)
    print(f"Wrote {len(records)} records (declared total {total}) to {out_path}")
