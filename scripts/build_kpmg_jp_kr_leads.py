#!/usr/bin/env python3
"""KPMG-focused Japan/Korea lead list.

KPMG link (public disclosures only): Korea DART audit clients (Samjong KPMG),
Japan EDINET audit clients (KPMG AZSA), plus JP/KR named client stories from the
KPMG client-story ledger. Input is the user's compiled workbook (.md export of
KPMG_Compiled_Workbook232 from Drive research_md_corpus) -- pass its path.
Profitability/size from Cassandra herrrickshaw.stock_quotes (CSV export), sector
from Postgres market_data.stocks. Lanes reuse build_leads.LANES.
Output goes OUTSIDE tracked docs (private_kpmg/, gitignored): the repo is public.
Usage: build_kpmg_jp_kr_leads.py WORKBOOK.md QUOTES.csv [OUTDIR]
"""
import csv, os, re, subprocess, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wb, quotes = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "private_kpmg")
os.makedirs(out, exist_ok=True)
spec = importlib.util.spec_from_file_location("bl", os.path.join(ROOT, "scripts/build_leads.py"))
bl = importlib.util.module_from_spec(spec); spec.loader.exec_module(bl)

def sheet(name):
    rows, on = [], False
    for line in open(wb, encoding="utf-8"):
        if line.startswith("## Sheet:"):
            on = line.strip() == f"## Sheet: {name}"; hdr = None; continue
        if on and line.strip():
            c = [x.strip() for x in line.rstrip("\n").split(" | ")]
            if hdr is None: hdr = c
            else: rows.append(dict(zip(hdr, c)))
    return rows

UNIV = os.path.expanduser("~/repos/global-stock-screener/data/global_universe")
def load_univ(f):
    return list(csv.DictReader(open(os.path.join(UNIV, f), encoding="utf-8")))
kr_by_code = {r["yf_ticker"].split(".")[0]: r for r in load_univ("KR.csv")}
jp_by_code = {r["yf_ticker"].split(".")[0]: r for r in load_univ("JP.csv")}

q = {}
for r in csv.DictReader(open(quotes)):
    if r["market"] in ("japan", "korea"): q[(r["market"], r["yf_ticker"])] = r
sec = {}
res = subprocess.run(["psql", "-d", "market_data", "-At", "-F", "\t", "-c",
    "select s.ticker,s.sector,s.industry from stocks s join markets m using(market_id) where m.market_name in ('japan','korea')"],
    capture_output=True, text=True).stdout
for l in res.splitlines():
    p = l.split("\t")
    if len(p) == 3: sec[p[0].split(".")[0]] = (p[1], p[2])

NAME_KEY = [("Pharma & Bulk Drugs", r"제약|약품|바이오|팜|pharm|bio|製薬|薬"),
 ("Medical Devices", r"메디|의료|medi|医療"),
 ("Electronics & Semiconductors", r"전자|반도체|전기|일렉|디스플레이|semi|electr|電|半導体"),
 ("Auto, EV & Components", r"자동차|모터|오토|타이어|auto|motor|自動車"),
 ("Chemicals & Plastics", r"화학|케미칼|소재|플라스틱|페인트|chem|化学"),
 ("Specialty Steel & Metals", r"철강|금속|메탈|제강|스틸|알루미늄|steel|metal|鉄|鋼|金属"),
 ("Food Processing", r"식품|푸드|제과|음료|제당|food|食品"),
 ("Textiles & Apparel", r"섬유|방직|의류|패션|textile|繊維"),
 ("Shipbuilding & Marine", r"조선|해운|marine|ship|海運|造船"),
 ("Aerospace & Defence", r"항공|방산|aero|defen|航空"),
 ("Green Energy & Fuels", r"에너지|전력|태양광|배터리|2차전지|도시가스|energy|solar|battery|エネルギー")]
KEY = [("Electronics & Semiconductors", r"electr|semicon|precision|machinery"),
 ("Auto, EV & Components", r"auto|transport equip|vehicle|tire|rubber"),
 ("Pharma & Bulk Drugs", r"pharma|drug|bio|health"),
 ("Medical Devices", r"medical|device"),
 ("Chemicals & Plastics", r"chem|plastic|paint|material"),
 ("Specialty Steel & Metals", r"steel|metal|mining|iron|nonferr"),
 ("Food Processing", r"food|beverage|agri|fisher"),
 ("Textiles & Apparel", r"textile|apparel|fiber|fibre"),
 ("White Goods & Electricals", r"electric|appliance|home"),
 ("Aerospace & Defence", r"aero|defen|aircraft"),
 ("Shipbuilding & Marine", r"ship|marine|shipping"),
 ("Green Energy & Fuels", r"energy|oil|gas|power|solar|battery|utilit")]
def lane(text):
    t = (text or "").lower()
    for k, pat in KEY:
        if re.search(pat, t): return k
    return ""

def f(x):
    try: return float(x)
    except: return None

rows = []
def add(mkt, code, name, kpmg_link, note, hint_sector=""):
    ref = (kr_by_code if mkt == "korea" else jp_by_code).get(code)
    yft = ref["yf_ticker"] if ref else ""
    qq = q.get((mkt, yft), {})
    s, ind = sec.get(code, ("", ""))
    fs = lane(" ".join([hint_sector, s, ind]))
    src = (s or hint_sector)
    if not fs:
        for k, pat in NAME_KEY:
            if re.search(pat, name, re.I): fs, src = k, "name-inferred"; break
    roe, opm, mc = f(qq.get("roe")), f(qq.get("opm")), f(qq.get("market_cap"))
    score = 40  # KPMG audit/story relationship
    if roe is not None and roe > 0: score += 15
    if opm is not None and opm > 0: score += 15
    # market_cap from the Cassandra bridge has unverified units -> kept as a column, NOT scored
    L = bl.LANES.get(fs, {})
    if L: score += 20
    rows.append(dict(market="Korea" if mkt == "korea" else "Japan", company=name, ticker=yft or code,
        kpmg_link=kpmg_link, note=note, sector_src=src, focus_sector=fs,
        roe=roe, opm=opm, market_cap_local=mc, lead_score=score,
        central_lanes="; ".join(c[0] for c in L.get("central", [])),
        state_landings="; ".join(L.get("states", [])),
        roles_to_approach="; ".join(bl.ENRICH_ROLES)))

for r in sheet("Korea DART Audit Clients"):
    code = r["Stock Code"].zfill(6)
    name = (kr_by_code.get(code) or {}).get("name") or r["Company (Korean)"]
    add("korea", code, name, "Statutory audit client (Samjong KPMG, FY2025)", r["Audit Opinion"])
for r in sheet("Japan EDINET Audit Clients"):
    code = r["Stock Code"][:-1] if len(r["Stock Code"]) == 5 else r["Stock Code"]
    en = r["Company (English)"]
    add("japan", code, en if en and not en.startswith("(not matched") else r["Company (Japanese)"],
        "Statutory audit client (KPMG AZSA, " + r["KPMG Office (Azusa LLC)"] + ")", r["Market Segment"], r["Sector"])
for r in sheet("KPMG Client Stories"):
    ctry = r.get("Country / Firm", "")
    if r.get("Named Client") == "Yes" and ctry.startswith(("Japan", "South Korea", "Korea")):
        mk = "korea" if "Korea" in ctry else "japan"
        rows.append(dict(market="Korea" if mk == "korea" else "Japan", company=r["Client"], ticker="",
            kpmg_link="KPMG client story: " + r["Title"][:90], note=r["URL"], sector_src=r["Sector"], focus_sector=lane(r["Sector"]),
            roe=None, opm=None, market_cap_local=None, lead_score=45, central_lanes="", state_landings="",
            roles_to_approach="; ".join(bl.ENRICH_ROLES)))

# dedupe on (market,company) keeping highest score, merge links
best = {}
for r in rows:
    k = (r["market"], r["company"].lower())
    if k not in best: best[k] = r
    else:
        b = best[k]; b["kpmg_link"] += " + " + r["kpmg_link"]; b["lead_score"] = max(b["lead_score"], r["lead_score"]) + 5
rows = sorted(best.values(), key=lambda r: -r["lead_score"])
for i, r in enumerate(rows, 1): r["rank"] = i
cols = ["rank", "market", "company", "ticker", "lead_score", "kpmg_link", "focus_sector", "sector_src", "roe", "opm",
        "market_cap_local", "central_lanes", "state_landings", "roles_to_approach", "note"]
with open(os.path.join(out, "kpmg_jp_kr_leads.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
import collections
print(len(rows), collections.Counter(r["market"] for r in rows), "with lane:", sum(1 for r in rows if r["focus_sector"]))
