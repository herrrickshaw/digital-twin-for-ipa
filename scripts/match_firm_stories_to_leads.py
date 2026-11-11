#!/usr/bin/env python3
"""Match non-KPMG firm client stories to the twin's leads (name match in title/description/URL slug).
Usage: match_firm_stories_to_leads.py  (reads private_kpmg/, writes private_kpmg/firm_stories_lead_matches.csv)"""
import csv, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "private_kpmg")
SUFFIX = r"\b(inc|corp|corporation|co|ltd|limited|plc|ag|nv|n\.v|sa|se|holdings?|group|company|llc|the|and|&)\b\.?"
GENERIC = {"energy","power","global","international","general","united","national","first","china","india","japan","korea","american","bank","steel","motor","motors","industries","technologies","systems","solutions","services","capital","electric","petroleum","health","medical","pharma","chemical","chemicals","tata","apple","target","visa","shell","ford","intel","meta","amazon","microsoft","google","oracle","ibm","sap"}
def key(name):
    n = re.sub(SUFFIX, " ", name.lower()); n = re.sub(r"[^\w\s]", " ", n)
    return " ".join(n.split())
cands = {}
for l in json.load(open(os.path.join(ROOT, "layers/16_leads.json")))["leads"]:
    cands[key(l["company"])] = (l["company"], "twin lead (" + l["sector"] + ")")
for r in csv.DictReader(open(os.path.join(P, "kpmg_jp_kr_leads.csv"), encoding="utf-8")):
    cands[key(r["company"])] = (r["company"], "KPMG-audited " + r["market"] + " (" + (r["focus_sector"] or "no lane") + ")")
# single generic words are too noisy -> require 2+ tokens or a distinctive 6+ char single token
cands = {k: v for k, v in cands.items() if k and (len(k.split()) >= 2 or (len(k) >= 6 and k not in GENERIC))}
pat = {k: re.compile(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])") for k in cands}
rows = list(csv.DictReader(open(os.path.join(P, "firm_client_stories.csv"), encoding="utf-8")))
out = []
for r in rows:
    if r["status"] != "200" or r["title"].startswith(("About Our", "Corporate Sust")): continue
    hay = key(" ".join([r["title"], r["description"], r["url"].rsplit("/", 1)[-1].replace("-", " ")]))
    hits = [k for k, p in pat.items() if p.search(hay)]
    if hits:
        for k in hits:
            out.append(dict(firm=r["firm"], region=r["region"], matched_company=cands[k][0], lead_context=cands[k][1], title=r["title"], url=r["url"]))
with open(os.path.join(P, "firm_stories_lead_matches.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(len(out), "matches across", len({o["url"] for o in out}), "stories;", len({o["matched_company"] for o in out}), "companies")
