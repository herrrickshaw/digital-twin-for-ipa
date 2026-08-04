#!/usr/bin/env python3
"""Lok Sabha Question Registry: every LS Q&A on investment policies, schemes and
incentives, organised scheme x date x ministry -- the parliamentary companion to
docs/reportage.html.

Source: the undocumented (but unauthenticated) sansad.in JSON API
  https://sansad.in/api_ls/question/qetFilteredQuestionsAns
which returns quesNo, subject, member, ministry, STARRED/UNSTARRED, date, session
and the full (randomly-suffixed) answer-PDF URL. The API's keyWord parameter is a
dumb case-insensitive SUBSTRING match on the subject line ("PLI" matches
"Upliftment"), so this script harvests broadly by keyword and then classifies
subjects with the same scheme-regex map + acronym-veto list the reportage uses
(imported from build_reportage). Coverage: 17th LS (2019-2024) + 18th LS (2024-).

Outputs:
  docs/pq_registry.html   -- standalone browsable registry (never hand-edit)
  data/registers/ls_pq_cache.json -- raw harvest cache (re-fetch with --refresh)

Rerun after each parliament session:  python3 scripts/build_pq_registry.py --refresh
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_reportage import scheme_hits  # scheme regexes + EXCLUDE vetoes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data/registers/ls_pq_cache.json")
OUT_HTML = os.path.join(ROOT, "docs/pq_registry.html")
API = "https://sansad.in/api_ls/question/qetFilteredQuestionsAns"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# Subject-line harvest keywords. Broad on purpose -- precision comes from the
# scheme_hits() classification pass, not from these.
KEYWORDS = [
 "PLI", "production linked", "incentive scheme", "FAME", "E-DRIVE", "electric vehicle",
 "semiconductor", "electronics component", "IT hardware", "mobile phone manufacturing",
 "green hydrogen", "KUSUM", "Surya Ghar", "rooftop solar", "solar module",
 "ethanol", "biogas", "gasification", "critical mineral", "rare earth",
 "RoDTEP", "RoSCTL", "SEZ", "MITRA", "textile park", "technical textile",
 "food processing", "Kisan Sampada", "micro food", "matsya", "animal husbandry infrastructure",
 "awas yojana", "jal jeevan", "distribution sector scheme", "apprenticeship",
 "employment linked", "ITI upgradation", "startup", "fund of funds", "seed fund",
 "interest subvention", "nutrient based", "urea", "fertilizer subsidy",
 "medical device", "bulk drug", "pharmaceutical incentive", "PRIP",
 "drone", "specialty steel", "advanced chemistry", "battery storage",
 "viability gap", "UDAN", "shipbuilding", "vishwakarma", "green credit",
 "research development and innovation", "agriculture infrastructure fund",
]

# Second-pass keywords added 2026-08-04 after the scrutiny cross-reference showed
# the first list had no subject term for several announced schemes (DevINE, eBus,
# iDEX, e-Shram, white goods, ...). Already merged into the LS cache; kept here so
# the Rajya Sabha harvester (build_rs_pq_registry.py) uses the identical set.
KEYWORDS_SUPPLEMENTARY = [
 "eBus", "e-Bus", "DevINE", "NESIDS", "UNNATI", "iDEX", "ADITI", "Shram", "IndiaAI",
 "BioE3", "Namami Gange", "Jan Vishwas", "scrapping", "Gati Shakti", "SHAKTI", "ECLGS",
 "emergency credit", "white goods", "air conditioner", "telecom manufacturing",
 "dhan-dhaanya", "pulses mission", "gokul", "dairy development", "manufacturing mission",
 "nuclear energy", "small modular", "defence corridor", "defence indigenisation",
 "skill india", "urban challenge", "EPR", "extended producer", "diamond", "BHAVYA",
 "credit guarantee", "LED light", "aviation turbine", "price stabilisation",
]


def fetch(lok, kw, page, size=200):
    q = urllib.parse.urlencode({"loksabhaNo": lok, "keyWord": kw,
                                "pageNo": page, "pageSize": size, "locale": "en"})
    req = urllib.request.Request(f"{API}?{q}", headers=UA)
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    # responses can carry raw control characters inside subject strings
    return json.loads(raw, strict=False)[0]


def harvest():
    seen, rows = set(), []
    for lok in (17, 18):
        for kw in KEYWORDS:
            page, total = 1, None
            while True:
                try:
                    d = fetch(lok, kw, page)
                except Exception as e:
                    print(f"  ! {lok}/{kw} p{page}: {e}", file=sys.stderr)
                    break
                total = d.get("totalRecordSize", 0)
                qs = d.get("listOfQuestions") or []
                for q in qs:
                    key = q.get("questionsFilePath") or f"{lok}-{q.get('sessionNo')}-{q.get('quesNo')}"
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append({
                        "lok": lok, "session": q.get("sessionNo"),
                        "qno": q.get("quesNo"), "qtype": q.get("type"),
                        "subject": (q.get("subjects") or "").strip(),
                        "ministry": (q.get("ministry") or "").strip().title(),
                        "members": q.get("member") or [],
                        "date": q.get("date"),          # dd.mm.yyyy
                        "pdf": q.get("questionsFilePath"),
                    })
                if page * 200 >= (total or 0) or not qs:
                    break
                page += 1
                time.sleep(0.25)
            print(f"  LS{lok} '{kw}': total {total}", file=sys.stderr)
            time.sleep(0.25)
    return rows


def iso(d):
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def quarter(d):
    return f"{d[:4]}Q{(int(d[5:7]) - 1)//3 + 1}" if d else "?"


def classify(rows):
    out = []
    for r in rows:
        hits = scheme_hits(r["subject"])
        if not hits:
            continue
        d = iso(r["date"])
        if not d:
            continue
        # collapse near-duplicate labels (e.g. "PLI Specialty Steel" from the
        # scheme map alongside "PLI — Specialty Steel" from the sector split)
        dedup, seen_norm = [], set()
        for h in sorted(set(hits)):
            norm = re.sub(r"[^a-z]", "", h.lower())
            if norm in seen_norm:
                continue
            seen_norm.add(norm)
            dedup.append(h)
        out.append({**r, "iso": d, "q": quarter(d), "schemes": dedup})
    # one row per question even if multiple keywords found it
    out.sort(key=lambda x: (x["iso"], x["qno"]), reverse=True)
    return out


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_html(rows):
    by_q = defaultdict(list)
    for r in rows:
        by_q[r["q"]].append(r)
    gen = time.strftime("%Y-%m-%d")
    schemes = sorted({s for r in rows for s in r["schemes"]})
    mins = sorted({r["ministry"] for r in rows})
    parts = [f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lok Sabha Question Registry — schemes &amp; incentives</title>
<style>
:root{{--pg:#eef1ea;--card:#fff;--ink:#1d2321;--mut:#5c6660;--acc:#1f5f5b;
 --accs:#e3ecea;--line:#d7ddd4}}
@media (prefers-color-scheme:dark){{:root{{--pg:#151a18;--card:#1e2522;--ink:#e6eae7;
 --mut:#98a39d;--acc:#6fb3ac;--accs:#23332f;--line:#2e3833}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--pg);color:var(--ink);
 font:16px/1.55 Georgia,serif}}
header,main{{max-width:1080px;margin:0 auto;padding:20px 22px}}
h1{{font-size:1.75rem;margin:0 0 6px}}
.sub{{color:var(--mut);font-family:-apple-system,sans-serif;font-size:.85rem;max-width:78ch}}
.controls{{position:sticky;top:0;background:var(--pg);border-bottom:1px solid var(--line);
 padding:10px 22px;z-index:5}}
.ci{{max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;gap:10px;
 font-family:-apple-system,sans-serif;font-size:.85rem;align-items:center}}
select,input[type=search]{{background:var(--card);color:var(--ink);
 border:1px solid var(--line);border-radius:6px;padding:7px 10px;font:inherit}}
input[type=search]{{flex:1;min-width:170px}}
.count{{color:var(--mut)}}
.q h2{{font-size:1.15rem;border-bottom:2px solid var(--acc);display:inline-block;
 padding-bottom:3px;margin:30px 0 12px}}
.q h2 .n{{color:var(--mut);font-family:-apple-system,sans-serif;font-size:.8rem;font-weight:400}}
.row{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);
 border-radius:8px;padding:10px 15px;margin-bottom:8px}}
.top{{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;
 font-family:-apple-system,sans-serif;font-size:.75rem;margin-bottom:4px}}
.chip{{background:var(--accs);color:var(--acc);border-radius:99px;padding:2px 10px;font-weight:600}}
.min{{color:var(--mut)}}.date{{color:var(--mut);font-variant-numeric:tabular-nums}}
.qn{{font-family:ui-monospace,monospace;font-size:.72rem;color:var(--acc)}}
.title a{{color:inherit;text-decoration:none}}.title a:hover{{text-decoration:underline}}
.mem{{color:var(--mut);font-family:-apple-system,sans-serif;font-size:.75rem;margin-top:3px}}
.hidden{{display:none}}
.note{{color:var(--mut);font-family:-apple-system,sans-serif;font-size:.8rem;
 border-top:1px dashed var(--line);margin-top:40px;padding-top:14px;max-width:82ch}}
</style></head><body>
<header><h1>Lok Sabha Question Registry</h1>
<div class="sub">{len(rows):,} Lok Sabha questions on investment policies, schemes and
incentives — 17th &amp; 18th Lok Sabha, classified by the same scheme map as the
<a href="reportage.html" style="color:var(--acc)">Quarterly Reportage</a>. Each row links
to the official answer PDF on sansad.in. Generated {gen} by
<code>scripts/build_pq_registry.py</code>.</div></header>
<div class="controls"><div class="ci">
<select id="fq"><option value="">All quarters</option></select>
<select id="fs"><option value="">All schemes</option></select>
<select id="fm"><option value="">All ministries</option></select>
<select id="ft2"><option value="">Starred + Unstarred</option>
<option>STARRED</option><option>UNSTARRED</option></select>
<input type="search" id="ft" placeholder="Search subjects…">
<span class="count" id="cnt"></span></div></div>
<main id="list">"""]
    for q in sorted(by_q, reverse=True):
        qs = by_q[q]
        parts.append(f'<section class="q" data-q="{q}"><h2>{q} '
                     f'<span class="n">&middot; {len(qs)} questions</span></h2>')
        for r in qs:
            chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in r["schemes"])
            mem = esc(", ".join(r["members"][:3])) + (" &amp; ors." if len(r["members"]) > 3 else "")
            parts.append(
                f'<div class="row" data-q="{q}" data-s="{esc("; ".join(r["schemes"]))}" '
                f'data-m="{esc(r["ministry"])}" data-t="{esc(r["qtype"] or "")}">'
                f'<div class="top"><span class="date">{r["iso"]}</span>{chips}'
                f'<span class="min">{esc(r["ministry"])}</span>'
                f'<span class="qn">LS{r["lok"]} &middot; {esc(r["qtype"] or "?")} '
                f'Q.{r["qno"]}</span></div>'
                f'<div class="title"><a href="{esc(r["pdf"])}" target="_blank" '
                f'rel="noopener">{esc(r["subject"])}</a></div>'
                f'<div class="mem">Asked by {mem}</div></div>')
        parts.append("</section>")
    parts.append(f"""</main>
<div class="note" style="max-width:1080px;margin:0 auto;padding:0 22px 40px">
Method: harvested from the sansad.in Lok Sabha Q&amp;A index by subject keyword, then
classified against the reportage scheme-regex map with its acronym-veto list. The
API matches keywords as substrings of the subject line only, so questions whose
subject names no scheme are not captured even if the answer discusses one. A
mapping error is a classification bug, not a parliamentary fact.
</div>
<script>
const fq=document.getElementById('fq'),fs=document.getElementById('fs'),
 fm=document.getElementById('fm'),ft=document.getElementById('ft'),
 ft2=document.getElementById('ft2'),cnt=document.getElementById('cnt');
const rows=[...document.querySelectorAll('.row')],secs=[...document.querySelectorAll('.q')];
const uniq=a=>[...new Set(a)].sort();
uniq(secs.map(s=>s.dataset.q)).reverse().forEach(v=>fq.add(new Option(v,v)));
uniq(rows.flatMap(r=>r.dataset.s.split('; '))).forEach(v=>fs.add(new Option(v,v)));
uniq(rows.map(r=>r.dataset.m)).forEach(v=>fm.add(new Option(v,v)));
function render(){{
 const q=fq.value,s=fs.value,m=fm.value,t=ft.value.toLowerCase(),t2=ft2.value;let n=0;
 rows.forEach(r=>{{const ok=(!q||r.dataset.q===q)&&(!s||r.dataset.s.split('; ').includes(s))
  &&(!m||r.dataset.m===m)&&(!t2||r.dataset.t===t2)
  &&(!t||r.textContent.toLowerCase().includes(t));
  r.classList.toggle('hidden',!ok);if(ok)n++;}});
 secs.forEach(x=>x.classList.toggle('hidden',!x.querySelector('.row:not(.hidden)')));
 cnt.textContent=n.toLocaleString()+' of '+rows.length.toLocaleString();}}
[fq,fs,fm,ft2].forEach(e=>e.addEventListener('change',render));
ft.addEventListener('input',render);render();
</script></body></html>""")
    open(OUT_HTML, "w", encoding="utf-8").write("".join(parts))


def main():
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    if "--refresh" in sys.argv or not os.path.exists(CACHE):
        rows = harvest()
        json.dump(rows, open(CACHE, "w"), ensure_ascii=False)
        print(f"harvested {len(rows)} raw questions -> {CACHE}")
    rows = json.load(open(CACHE))
    reg = classify(rows)
    write_html(reg)
    qs = sorted({r["q"] for r in reg})
    print(f"pq registry: {len(reg)} scheme-mapped questions "
          f"({qs[0]}..{qs[-1]}) of {len(rows)} harvested -> {OUT_HTML}")
    # rows for the blog post builder
    json.dump(reg, open(os.path.join(ROOT, "data/registers/ls_pq_registry.json"), "w"),
              ensure_ascii=False)


if __name__ == "__main__":
    main()
