#!/usr/bin/env python3
"""Rajya Sabha Question Registry: every RS Q&A on investment policies, schemes and
incentives, organised scheme x date x ministry -- the upper-house companion to the
Lok Sabha registry (build_pq_registry.py).

Source: the per-question backend behind sansad.in's RS pages lives on a DIFFERENT
host -- rsdoc.nic.in -- found in the site's client JS chunks (the sansad.in api_rs
endpoints are a dead end that only lists consolidated daily PDFs):

  https://rsdoc.nic.in/Question/Search_Questions?whereclause=<SQL>

It accepts a raw parametrised SQL where-clause (ses_no, qtype as the STRING
'STARRED'/'UNSTARRED', qno, min_code, adate, qtitle like '%kw%'). There is no
Lok-Sabha-style house number; adate filters work WITHOUT ses_no, so this script
harvests by `qtitle like '%<keyword>%' and adate >= '2019-01-01'` -- the same
date floor and the same keyword lists as the LS harvester, classified by the same
scheme_hits() map, so all three registries (PIB, LS, RS) filter identically.
Each record's `files` field carries the official answer PDF on sansad.in.

Outputs:
  docs/rs_pq_registry.html            -- standalone browsable registry
  data/registers/rs_pq_cache.json     -- raw harvest cache (--refresh re-fetches)
  data/registers/rs_pq_registry.json  -- classified rows for downstream builds

Rerun after each parliament session:  python3 scripts/build_rs_pq_registry.py --refresh
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_reportage import scheme_hits
from build_pq_registry import KEYWORDS, KEYWORDS_SUPPLEMENTARY, iso, quarter, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data/registers/rs_pq_cache.json")
OUT_HTML = os.path.join(ROOT, "docs/rs_pq_registry.html")
OUT_JSON = os.path.join(ROOT, "data/registers/rs_pq_registry.json")
API = "https://rsdoc.nic.in/Question/Search_Questions"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
DATE_FLOOR = "2019-01-01"   # match the LS registry's coverage start


def fetch(where):
    url = f"{API}?whereclause={urllib.parse.quote(where)}"
    req = urllib.request.Request(url, headers=UA)
    raw = urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")
    return json.loads(raw, strict=False)


def harvest():
    seen, rows = set(), []
    # keyword LIKE-escape: the clause is SQL, so quote single quotes
    for kw in KEYWORDS + KEYWORDS_SUPPLEMENTARY:
        safe = kw.replace("'", "''")
        where = f"qtitle like '%{safe}%' and adate >= '{DATE_FLOOR}'"
        try:
            recs = fetch(where)
        except Exception as e:
            print(f"  ! '{kw}': {e}", file=sys.stderr)
            continue
        for r in recs:
            key = r.get("files") or f"{r.get('ses_no')}-{r.get('qno')}"
            if key in seen:
                continue
            seen.add(key)
            name = " ".join(x for x in [(r.get("shri") or "").strip(),
                                        (r.get("name") or "").strip()] if x)
            rows.append({
                "session": r.get("ses_no"),
                "qno": int(r.get("qno") or 0),
                "qtype": (r.get("qtype") or "").strip(),
                "subject": (r.get("qtitle") or "").strip(),
                "ministry": (r.get("min_name") or "").strip().title(),
                "members": [name] if name else [],
                "iso_date": (r.get("adate") or "")[:10],
                "pdf": r.get("files"),
            })
        print(f"  RS '{kw}': {len(recs)} rows", file=sys.stderr)
        time.sleep(0.3)
    return rows


def classify(rows):
    out = []
    for r in rows:
        hits = scheme_hits(r["subject"])
        if not hits or not r["iso_date"]:
            continue
        dedup, seen_norm = [], set()
        for h in sorted(set(hits)):
            norm = re.sub(r"[^a-z]", "", h.lower())
            if norm in seen_norm:
                continue
            seen_norm.add(norm)
            dedup.append(h)
        out.append({**r, "iso": r["iso_date"], "q": quarter(r["iso_date"]),
                    "schemes": dedup})
    out.sort(key=lambda x: (x["iso"], x["qno"]), reverse=True)
    return out


def write_html(rows):
    by_q = defaultdict(list)
    for r in rows:
        by_q[r["q"]].append(r)
    gen = time.strftime("%Y-%m-%d")
    parts = [f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rajya Sabha Question Registry — schemes &amp; incentives</title>
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
<header><h1>Rajya Sabha Question Registry</h1>
<div class="sub">{len(rows):,} Rajya Sabha questions on investment policies, schemes and
incentives since {DATE_FLOOR[:4]}, classified by the same scheme map as the
<a href="pq_registry.html" style="color:var(--acc)">Lok Sabha registry</a> and the
<a href="reportage.html" style="color:var(--acc)">Quarterly Reportage</a>. Each row links
to the official answer PDF on sansad.in. Generated {gen} by
<code>scripts/build_rs_pq_registry.py</code>.</div></header>
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
            mem = esc(", ".join(r["members"][:3]))
            qt = (r["qtype"] or "?").strip()
            parts.append(
                f'<div class="row" data-q="{q}" data-s="{esc("; ".join(r["schemes"]))}" '
                f'data-m="{esc(r["ministry"])}" data-t="{esc(qt)}">'
                f'<div class="top"><span class="date">{r["iso"]}</span>{chips}'
                f'<span class="min">{esc(r["ministry"])}</span>'
                f'<span class="qn">RS Sess.{r["session"]} &middot; {esc(qt)} '
                f'Q.{r["qno"]}</span></div>'
                f'<div class="title"><a href="{esc(r["pdf"])}" target="_blank" '
                f'rel="noopener">{esc(r["subject"])}</a></div>'
                f'<div class="mem">Asked by {mem}</div></div>')
        parts.append("</section>")
    parts.append("""</main>
<div class="note" style="max-width:1080px;margin:0 auto;padding:0 22px 40px">
Method: harvested from the rsdoc.nic.in per-question index by subject keyword
(the same keyword lists as the Lok Sabha registry), then classified against the
reportage scheme-regex map with its acronym-veto list. Subject-line capture only:
a question whose title names no scheme is not counted even when the answer
discusses one. A mapping error is a classification bug, not a parliamentary fact.
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
function render(){
 const q=fq.value,s=fs.value,m=fm.value,t=ft.value.toLowerCase(),t2=ft2.value;let n=0;
 rows.forEach(r=>{const ok=(!q||r.dataset.q===q)&&(!s||r.dataset.s.split('; ').includes(s))
  &&(!m||r.dataset.m===m)&&(!t2||r.dataset.t===t2)
  &&(!t||r.textContent.toLowerCase().includes(t));
  r.classList.toggle('hidden',!ok);if(ok)n++;});
 secs.forEach(x=>x.classList.toggle('hidden',!x.querySelector('.row:not(.hidden)')));
 cnt.textContent=n.toLocaleString()+' of '+rows.length.toLocaleString();}
[fq,fs,fm,ft2].forEach(e=>e.addEventListener('change',render));
ft.addEventListener('input',render);render();
</script></body></html>""")
    open(OUT_HTML, "w", encoding="utf-8").write("".join(parts))


def main():
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    if "--refresh" in sys.argv or not os.path.exists(CACHE):
        rows = harvest()
        json.dump(rows, open(CACHE, "w"), ensure_ascii=False)
        print(f"harvested {len(rows)} raw RS questions -> {CACHE}")
    rows = json.load(open(CACHE))
    reg = classify(rows)
    write_html(reg)
    json.dump(reg, open(OUT_JSON, "w"), ensure_ascii=False)
    qs = sorted({r["q"] for r in reg})
    print(f"rs pq registry: {len(reg)} scheme-mapped questions "
          f"({qs[0]}..{qs[-1]}) of {len(rows)} harvested -> {OUT_HTML}")


if __name__ == "__main__":
    main()
