#!/usr/bin/env python3
"""
Bonus pull: Messe Frankfurt's exhibitor-service/api/2.1/public/exhibitor/search
endpoint is NOT scoped to a single fair when 'findEventVariable' is omitted --
it searches across ALL Messe Frankfurt shows globally (confirmed 2026-08-22:
q="" with no findEventVariable returned hitsTotal=49665 spanning Beautyworld
Japan Fukuoka, Interior Lifestyle Tokyo, Arminera 2025 (Argentina), Interpets
Tokyo, etc. in a single result set). Combined with country=IND this is a
single unified query surfacing every India-HQ'd exhibitor across the ENTIRE
Messe Frankfurt global show portfolio (confirmed hitsTotal=3114), not just
the 4 fairs deep-dived individually this pass. This is the "broader Messe
Frankfurt directory" the task asked to check for.
"""
import json
import time
import urllib.parse
import urllib.request

APIKEY = "LXnMWcYQhipLAS7rImEzmZ3CkrU033FMha9cwVSngG4vbufTsAOCQQ=="
BASE = "https://api.messefrankfurt.com/service/esb_api/exhibitor-service/api/2.1/public/exhibitor/search"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
PAGE_SIZE = 200


def fetch_page(page, country=None):
    params = {
        "language": "en-GB", "q": "", "orderBy": "name",
        "pageNumber": page, "pageSize": PAGE_SIZE,
        "orSearchFallback": "true", "showJumpLabels": "false",
    }
    if country:
        params["country"] = country
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"apikey": APIKEY, "User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pull(country):
    all_hits, page, total = [], 1, None
    while True:
        data = fetch_page(page, country)
        result = data["result"]
        total = result["metaData"]["hitsTotal"]
        hits = result["hits"]
        all_hits.extend(hits)
        print(f"  page {page}: {len(hits)} (total so far {len(all_hits)} / {total})")
        if len(all_hits) >= total or not hits:
            break
        page += 1
        time.sleep(0.4)

    records = []
    for h in all_hits:
        ex = h.get("exhibitor", {})
        addr = ex.get("address") or {}
        country_obj = addr.get("country") or {}
        exhib = ex.get("exhibition") or {}
        records.append({
            "name": ex.get("name"),
            "fair": exhib.get("name"),
            "fair_id": exhib.get("id"),
            "city": addr.get("city"),
            "country_iso3": country_obj.get("iso3"),
            "email": addr.get("email"),
            "homepage": ex.get("homepage"),
        })
    return total, records


if __name__ == "__main__":
    print("Pulling ALL India-HQ exhibitors across every Messe Frankfurt global show ...")
    total, records = pull("IND")
    out_path = "/Users/umashankar/digital-twin-for-ipa/scripts/scratch_messe/messefrankfurt_global_india_exhibitors.json"
    with open(out_path, "w") as f:
        json.dump({"query": "country=IND, all Messe Frankfurt shows (no findEventVariable filter)",
                    "hitsTotal": total, "collected": len(records), "records": records}, f, indent=2)
    print(f"Wrote {len(records)} records (declared total {total}) to {out_path}")
