#!/usr/bin/env python3
"""Collect client-story / case-study pages from professional-services firm sites
(Deloitte, Accenture, BDO, EY) -- the non-KPMG counterpart of the KPMG ledger.

Method: URLs come from each firm's own sitemap (listed in robots.txt), filtered to
case-study paths; each page is fetched politely (1 req/s, browser UA, resumable) and
only og:title / description / JSON-LD headline are kept. No WAF bypass: PwC, BCG and
Bain return 403 bot walls and are skipped.
Usage: collect_firm_client_stories.py URLS.txt OUT.csv
"""
import csv, html, os, re, subprocess, sys, time

urls_f, out = sys.argv[1], sys.argv[2]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
BAD = re.compile(r"/blogs?/|careers|interview|jobpostings|/events?/|/about/company/integrated", re.I)
urls = [u.strip() for u in open(urls_f) if u.strip() and not BAD.search(u)]
done = set()
if os.path.exists(out):
    done = {r["url"] for r in csv.DictReader(open(out, encoding="utf-8"))}
new = not os.path.exists(out)
fh = open(out, "a", newline="", encoding="utf-8")
w = csv.DictWriter(fh, fieldnames=["firm", "region", "url", "title", "description", "status"])
if new: w.writeheader()

def meta(page, prop):
    for pat in (rf'<meta[^>]+(?:property|name)=["\']{prop}["\'][^>]+content=["\']([^"\']*)',
                rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']{prop}["\']'):
        m = re.search(pat, page, re.I)
        if m: return html.unescape(m.group(1)).strip()
    return ""

blocked = set()
for u in urls:
    if u in done: continue
    firm = re.search(r"//(?:www\.)?([a-z]+)\.", u).group(1)
    if firm in blocked: continue
    m = re.search(r"deloitte\.com/([a-z]+)/|accenture\.com/([a-z]{2}-[a-z]{2})/", u)
    region = (m.group(1) or m.group(2)) if m else ("us" if firm in ("bdo", "ey") else "")
    r = subprocess.run(["curl", "-s", "-L", "-m", "30", "-A", UA, "--compressed", "-w", "\n%{http_code}", u], capture_output=True)
    body, _, code = r.stdout.decode("utf-8", "replace").rpartition("\n")
    title = description = ""
    if code == "200":
        title = meta(body, "og:title") or (re.search(r"<title>([^<]*)", body, re.I) or [None, ""])[1]
        description = meta(body, "og:description") or meta(body, "description")
    w.writerow(dict(firm=firm, region=region, url=u, title=html.unescape(title).strip(), description=description, status=code))
    fh.flush(); time.sleep(1)
    if code in ("403", "429"):
        print("blocked", firm, code, "-- stopping this host"); blocked.add(firm)
print("done", len(urls))
