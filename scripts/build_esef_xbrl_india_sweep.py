#!/usr/bin/env python3
"""ESEF/UKSEF India-sweep (filings.xbrl.org) -- UK/France/Italy/Netherlands
filing discovery, sibling to build_edgar_india_sweep.py / build_dart_india_sweep.py
/ build_cninfo_india_sweep.py.

None of these four markets' NATIVE regulator has a live full-text-search API
(confirmed live 2026-08-09 by a scouting pass): the UK's FCA National Storage
Mechanism is real but not yet live ("due to go live soon"); Italy's
eMarketStorage/CONSOB and the Netherlands' AFM register are scrape-only, no
documented API; France's info-financiere.gouv.fr IS a real open API but
searches METADATA fields, not filing body text. The one thing that DOES work
across all four is a third party: filings.xbrl.org, ESMA-adjacent but
independently run, a JSON:API index of ESEF/UKSEF inline-XBRL annual reports
-- confirmed live, keyless, with a direct `report_url` to the actual
XHTML/iXBRL report text for most filings (grep-able, no PDF-download step
needed like DART/cninfo). Cumulative filing counts (2026-08-09): GB 2,897,
FR 1,178, IT 872, NL 656 -- modest, DART-scale or smaller.

Corpus/effort: unlike DART, each filing needs (a) one GET for the report
XHTML and (b) one GET for the filing entity's name (cached per LEI -- many
entities file annually, so the cache amortizes fast). No auth, no rate-limit
documented, but this script is still incremental and CHECKPOINTED (writes
the output JSON every --checkpoint-every filings, not just at exit) --
learned from the DART sweep's gap: that script only writes at the very end
of an unbounded multi-hour run, so a crash mid-run loses everything.

Usage:
    build_esef_xbrl_india_sweep.py --countries GB,FR,IT,NL --max-filings-per-country 200
Output: layers/16_enrichment/esef_xbrl_india_sweep.json (cumulative, deduped on fxo_id)
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "layers", "16_enrichment", "esef_xbrl_india_sweep.json")
BASE = "https://filings.xbrl.org"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126"

INTENT_PHRASES = [
    "expansion in India", "expand in India", "invest in India", "investment in India",
    "investments in India", "new facility in India", "manufacturing facility in India",
    "manufacturing in India", "production capacity in India", "subsidiary in India",
    "plant in India", "India expansion", "enters India", "entry into India",
]
TAG_RE = re.compile(r"<[^>]+>")


def get_json(url, params=None):
    r = requests.get(url, params=params, headers={"User-Agent": UA,
                     "Accept": "application/vnd.api+json"}, timeout=30)
    r.raise_for_status()
    return r.json()


def strip_html(html: str) -> str:
    html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", html))


def find_hits(text: str) -> list:
    hits = []
    for phrase in INTENT_PHRASES:
        if re.search(re.escape(phrase), text, re.I):
            i = text.lower().find(phrase.lower())
            hits.append({"phrase": phrase, "snippet": text[max(0, i - 40):i + 60]})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="GB,FR,IT,NL")
    ap.add_argument("--max-filings-per-country", type=int, default=200)
    ap.add_argument("--checkpoint-every", type=int, default=25)
    args = ap.parse_args()

    prior = {}
    if os.path.exists(OUT):
        prior = {r["fxo_id"]: r for r in json.load(open(OUT))["results"]}
    entity_name_cache = {}

    def save():
        out = {"layer": "16_enrichment/esef_xbrl_india_sweep", "built": dt.date.today().isoformat(),
               "method": ("filings.xbrl.org (3rd-party ESEF/UKSEF aggregator, keyless, live) -> "
                          "download report_url XHTML -> local regex sweep for INTENT_PHRASES "
                          "(English only -- non-English-only annual reports may be missed, "
                          "recorded as a scope limit, not silently)"),
               "count": len(prior), "results": list(prior.values())}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

    since_checkpoint = 0
    for cc in args.countries.split(","):
        page_url, page_params = BASE + "/api/filings", {"filter[country]": cc, "page[size]": 50}
        fetched_this_country = 0
        while page_url and fetched_this_country < args.max_filings_per_country:
            try:
                d = get_json(page_url, page_params)
            except Exception as e:
                print(f"  {cc}: list error {type(e).__name__}: {e}", file=sys.stderr)
                break
            for f in d.get("data", []):
                if fetched_this_country >= args.max_filings_per_country:
                    break
                fxo_id = f["attributes"]["fxo_id"]
                fetched_this_country += 1
                if fxo_id in prior:
                    continue
                report_url = f["attributes"].get("report_url")
                row = {"fxo_id": fxo_id, "country": cc, "period_end": f["attributes"].get("period_end"),
                       "report_url": report_url, "hits": [], "entity": None,
                       "swept": dt.date.today().isoformat()}
                if not report_url:
                    row["skipped"] = "no report_url (package-only filing, not fetched in v1)"
                else:
                    try:
                        text = strip_html(requests.get(BASE + report_url,
                                          headers={"User-Agent": UA}, timeout=30).text)
                        row["hits"] = find_hits(text)
                    except Exception as e:
                        row["error"] = f"{type(e).__name__}: {e}"
                    time.sleep(0.2)
                if row["hits"]:
                    entity_link = f["relationships"]["entity"]["links"]["related"]
                    lei = entity_link.rsplit("/", 1)[-1]
                    if lei not in entity_name_cache:
                        try:
                            ed = get_json(BASE + entity_link)
                            entity_name_cache[lei] = ed["data"]["attributes"]["name"]
                        except Exception:
                            entity_name_cache[lei] = None
                        time.sleep(0.2)
                    row["entity"] = {"lei": lei, "name": entity_name_cache[lei]}
                    print(f"  NEW-LEAD ({cc}): {row['entity']['name']} ({lei}) -- "
                          f"{row['hits'][0]['phrase']}: ...{row['hits'][0]['snippet']}...")
                prior[fxo_id] = row
                since_checkpoint += 1
                if since_checkpoint >= args.checkpoint_every:
                    save()
                    since_checkpoint = 0
            page_url = d.get("links", {}).get("next")
            page_params = None  # next link already carries params
        print(f"{cc}: fetched {fetched_this_country}")

    save()
    hits = [r for r in prior.values() if r.get("hits")]
    print(f"\ncumulative filings tracked: {len(prior)} | with India-intent hits: {len(hits)} -> {OUT}")


if __name__ == "__main__":
    main()
