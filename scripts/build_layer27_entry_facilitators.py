#!/usr/bin/env python3
"""Layer 27 — foreign market-entry facilitators in India.

The country-wise bodies — national trade-promotion agencies and bilateral
chambers of commerce — that host events and organise B2B matchmaking to help
*their* companies enter the Indian market. This is the demand-side counterpart
to the twin's supply-side incentive catalogue: where a foreign firm eyeing an
Indian incentive/project actually goes for introductions, delegations and
market-entry support.

Examples the user anchored on: GTAI (Germany), AHK/IGCC (Indo-German Chamber),
Swissnex (Switzerland) — plus the equivalents for ~20 countries.

URLs are liveness-checked on build (HEAD/GET); each entry records last_status
so parked/moved domains surface as data (the twin's standing rule — access
failures are recorded, not skipped).

Output: layers/27_entry_facilitators.json.
"""
import json
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "layers"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

# type: agency = national trade/invest promotion body; chamber = bilateral
# chamber of commerce in India; innovation = science/innovation outpost.
FACILITATORS = [
    {"country": "Germany", "body": "Germany Trade & Invest (GTAI)",
     "type": "agency", "url": "https://www.gtai.de/",
     "events_url": "https://www.gtai.de/en/meta/events"},
    {"country": "Germany", "body": "Indo-German Chamber of Commerce (AHK India / IGCC)",
     "type": "chamber", "url": "https://indien.ahk.de/en/",
     "events_url": "https://indien.ahk.de/en/events",
     "note": "Largest bilateral chamber in India; AHK is the global German "
             "chamber network brand."},
    {"country": "Switzerland", "body": "Swissnex in India",
     "type": "innovation", "url": "https://swissnex.org/india/",
     "events_url": "https://swissnex.org/india/events/",
     "note": "Science/innovation/startup bridge, Bengaluru."},
    {"country": "Switzerland", "body": "Switzerland Global Enterprise (S-GE)",
     "type": "agency", "url": "https://www.s-ge.com/en", "events_url": None},
    {"country": "Switzerland", "body": "Swiss Business Hub India (part of S-GE)",
     "type": "agency", "url": "https://www.s-ge.com/en",
     "events_url": None,
     "note": "The former Swiss-Indian Chamber domain sicc.in is now REPURPOSED "
             "(301 -> clubfootcares.org, unrelated) — do not trust; Swiss market "
             "entry runs through swissnex + S-GE's Swiss Business Hub."},
    {"country": "United Kingdom", "body": "UK India Business Council (UKIBC)",
     "type": "chamber", "url": "https://www.ukibc.com/",
     "events_url": "https://www.ukibc.com/events/"},
    {"country": "Japan", "body": "JETRO (Japan External Trade Organization), India",
     "type": "agency", "url": "https://www.jetro.go.jp/en/",
     "events_url": "https://www.jetro.go.jp/en/events/"},
    {"country": "South Korea", "body": "KOTRA (Korea Trade-Investment Promotion Agency)",
     "type": "agency", "url": "https://www.kotra.or.kr/", "events_url": None,
     "note": "New Delhi/Mumbai Korea Business Centres."},
    {"country": "France", "body": "Business France (India)",
     "type": "agency", "url": "https://www.businessfrance.fr/en/", "events_url": None},
    {"country": "France", "body": "Indo-French Chamber of Commerce & Industry (IFCCI)",
     "type": "chamber", "url": "https://www.ifcci.org.in/",
     "events_url": "https://www.ifcci.org.in/events"},
    {"country": "Italy", "body": "Italian Trade Agency (ITA / ICE), India",
     "type": "agency", "url": "https://www.ice.it/en/markets/india/new-delhi",
     "events_url": None},
    {"country": "Italy", "body": "Indo-Italian Chamber of Commerce & Industry (IICCI)",
     "type": "chamber", "url": "https://www.indiaitaly.com/", "events_url": None},
    {"country": "United States", "body": "US-India Business Council (USIBC)",
     "type": "chamber", "url": "https://www.usibc.com/",
     "events_url": "https://www.usibc.com/events/"},
    {"country": "United States", "body": "American Chamber of Commerce in India (AMCHAM)",
     "type": "chamber", "url": "https://www.amchamindia.com/", "events_url": None},
    {"country": "Sweden", "body": "Business Sweden (India)",
     "type": "agency", "url": "https://www.business-sweden.com/markets/asia-pacific/india/",
     "events_url": None},
    {"country": "Austria", "body": "ADVANTAGE AUSTRIA (India)",
     "type": "agency", "url": "https://www.advantageaustria.org/in/", "events_url": None},
    {"country": "Netherlands", "body": "Netherlands India Chamber of Commerce & Trade (NICCT)",
     "type": "chamber", "url": "https://www.nicct.nl/", "events_url": None},
    {"country": "Australia", "body": "Austrade (India)",
     "type": "agency", "url": "https://www.austrade.gov.au/", "events_url": None},
    {"country": "Australia", "body": "Australia India Business Council (AIBC)",
     "type": "chamber", "url": "https://aibc.org.au/", "events_url": None},
    {"country": "Ireland", "body": "Enterprise Ireland (India)",
     "type": "agency", "url": "https://www.enterprise-ireland.com/en/", "events_url": None},
    {"country": "Spain", "body": "ICEX Spain Trade & Investment",
     "type": "agency", "url": "https://www.icex.es/", "events_url": None},
    {"country": "Denmark", "body": "The Trade Council (Embassy of Denmark, India)",
     "type": "agency", "url": "https://indien.um.dk/en", "events_url": None},
    {"country": "Finland", "body": "Business Finland (India)",
     "type": "agency", "url": "https://www.businessfinland.com/", "events_url": None},
    {"country": "Belgium (Flanders)", "body": "Flanders Investment & Trade (FIT)",
     "type": "agency", "url": "https://www.flandersinvestmentandtrade.com/en",
     "events_url": None},
    {"country": "Canada", "body": "Canada-India Business Council (C-IBC)",
     "type": "chamber", "url": "https://canada-indiabusiness.ca/", "events_url": None},
    {"country": "Singapore", "body": "Enterprise Singapore",
     "type": "agency", "url": "https://www.enterprisesg.gov.sg/", "events_url": None},
    {"country": "European Union", "body": "European Business & Technology Centre (EBTC)",
     "type": "agency", "url": "https://ebtc.eu/", "events_url": None,
     "note": "EU-wide business/tech gateway to India, New Delhi."},
]


def check(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def build():
    rows = []
    for f in FACILITATORS:
        f = dict(f)
        f["last_status"] = check(f["url"])
        f["live"] = f["last_status"] in (200, 301, 302, 403)  # 403 = WAF, site exists
        rows.append(f)
    live = sum(r["live"] for r in rows)
    by_country = {}
    for r in rows:
        by_country.setdefault(r["country"], 0)
        by_country[r["country"]] += 1

    layer = {
        "layer": 27,
        "title": "Foreign market-entry facilitators in India "
                 "(trade-promotion agencies & bilateral chambers)",
        "built": date.today().isoformat(),
        "purpose": "The demand-side counterpart to the incentive catalogue: the "
                   "country-wise bodies that host events and B2B matchmaking to "
                   "bring foreign companies into India. Where a firm eyeing an "
                   "Indian incentive (layers 02/17), project (layer 26) or site "
                   "(layer 25) goes for introductions and delegations.",
        "coverage": {"bodies": len(rows), "countries": len(by_country),
                     "live_on_build": live,
                     "with_events_page": sum(1 for r in rows if r.get("events_url"))},
        "types": {"agency": "national trade/investment-promotion body",
                  "chamber": "bilateral chamber of commerce operating in India",
                  "innovation": "science/innovation/startup bridge"},
        "facilitators": rows,
        "linkage": {
            "to_layer_04": "These bodies are the real-world on-ramp for the "
                           "investor workflow (sector→scheme→NSWS→sanction).",
            "to_layer_06_07": "They convene the foreign company pools the "
                              "investor map/pairings identify — the matchmaking "
                              "venue for outreach.",
            "to_layer_16": "Lead outreach (layer 16) can route through the "
                           "relevant country's chamber/agency event calendar "
                           "rather than cold contact.",
        },
        "caveat": "Directory of official bodies; verify each event's specifics "
                  "on the linked site. last_status is a build-time liveness "
                  "check (403 = live behind a WAF).",
    }
    out = LAYERS / "27_entry_facilitators.json"
    out.write_text(json.dumps(layer, indent=1, ensure_ascii=False))
    print(f"layer 27: {len(rows)} bodies across {len(by_country)} countries, "
          f"{live} live, {layer['coverage']['with_events_page']} with events "
          f"pages -> {out}")
    dead = [r for r in rows if not r["live"]]
    if dead:
        print("  NOT live (check):", ", ".join(
            f"{r['body']} ({r['last_status']})" for r in dead))


if __name__ == "__main__":
    build()
