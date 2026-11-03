"""State-announcement, policy-annex and UP-ethanol HTML fragments."""
import datetime, html as _h, os, re

from reportage.common import ROOT

MONTHS={m:i+1 for i,m in enumerate(["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"])}
def _extract_date(text):
    """Find the first plausible dd-mm-yyyy / dd Month yyyy / Month-yyyy date in text; return ISO or None."""
    t=text or ""
    m=re.search(r"\b(\d{1,2})[-./](\d{1,2})[-./](20[12]\d)\b", t)
    if m:
        d,mo,y=int(m.group(1)),int(m.group(2)),int(m.group(3))
        if 1<=mo<=12 and 1<=d<=31: return f"{y:04d}-{mo:02d}-{d:02d}"
    m=re.search(r"\b(\d{1,2})[- ]([A-Za-z]{3,9})[- ,]*(20[12]\d)\b", t)
    if m and m.group(2)[:3].lower() in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(2)[:3].lower()]:02d}-{min(int(m.group(1)),28):02d}"
    m=re.search(r"\b([A-Za-z]{3,9})[- ](20[12]\d)\b", t)
    if m and m.group(1)[:3].lower() in MONTHS:
        return f"{int(m.group(2)):04d}-{MONTHS[m.group(1)[:3].lower()]:02d}-15"
    return None


def state_announcements():
    """Dated state-scheme events from layers 12 (policy GR/notification dates) and 18 (funds evidence)."""
    import json as _j, glob as _g
    rows=[]
    for f in _g.glob(os.path.join(ROOT, "layers/12_state_catalog/*.json")):
        if "ocr_extracts" in f: continue
        d=_j.load(open(f))
        for s in d.get("states", []):
            for p in s.get("policies", []):
                blob=" ".join(str(p.get(k,"")) for k in ("name","status","site_notes","what_companies_get"))
                iso=_extract_date(blob)
                if iso and iso>="2017-01-01":
                    rows.append({"date":iso,"state":s["state"].title(),"scheme":p.get("name","")[:110],
                                 "detail":(p.get("status") or p.get("site_notes") or "")[:150],
                                 "url":p.get("site_url","")})
    try:
        mon=_j.load(open(os.path.join(ROOT, "layers/18_state_monitor.json")))
        for s in mon["states"]:
            for sc in s["schemes"]:
                for e in sc.get("funds_evidence", []):
                    iso=_extract_date(str(e.get("date","")))
                    if iso and e.get("figure") and "UNVERIFIED" not in e.get("figure",""):
                        rows.append({"date":iso,"state":s["state"].title(),"scheme":sc["scheme"][:110],
                                     "detail":(e.get("figure","")+" -- "+e.get("fact",""))[:170],
                                     "url":e.get("source_url","")})
    except FileNotFoundError:
        pass
    return rows


def render_states():
    """State-level incentives section from layers/18_state_monitor.json + instrument counts from layer 12."""
    import html as _h, json as _j, glob as _g
    try:
        mon = _j.load(open(os.path.join(ROOT, "layers/18_state_monitor.json")))
    except FileNotFoundError:
        return "<p>(state monitor layer not built)</p>"
    counts = {}
    for f in _g.glob(os.path.join(ROOT, "layers/12_state_catalog/*.json")):
        d = _j.load(open(f))
        for s in d.get("states", []):
            counts[s["state"].upper()] = len(s.get("policies", []))
    parts = ['<div style="background:var(--accent-soft);border-radius:8px;padding:12px 16px;margin-bottom:18px;'
             'font-family:-apple-system,sans-serif;font-size:.85rem;">'
             + "".join(f"<p style='margin:4px 0'>{_h.escape(h)}</p>" for h in mon.get("headline_findings", []))
             + "</div>"]
    for st in mon["states"]:
        n = counts.get(st["state"].upper(), "")
        parts.append(f'<section class="q"><h2>{_h.escape(st["state"].title())} '
                     f'<span class="n">&middot; {n} catalogued instruments</span></h2>')
        for sc in st["schemes"]:
            arrears = any("arrear" in (e.get("fact","")+sc.get("status_2025_26","")).lower() or "pending" in e.get("fact","").lower()
                          for e in sc.get("funds_evidence", []))
            flag = ' <span class="chip" style="background:#7a2e2e22;color:var(--warn);">arrears signal</span>' if arrears else ""
            parts.append(f'<div class="row" data-q="state" data-s="{_h.escape(sc["scheme"][:60], quote=True)}" data-m="State governments" data-st="{_h.escape(st["state"].title(), quote=True)}">'
                         f'<div class="top"><span class="chip">{_h.escape(sc["scheme"][:80])}</span>{flag}</div>'
                         f'<div class="title" style="font-size:.88rem;color:var(--muted);">{_h.escape(sc.get("status_2025_26","")[:260])}</div>')
            for e in sc.get("funds_evidence", [])[:4]:
                fig = _h.escape(e.get("figure",""))
                fact = _h.escape(e.get("fact","")[:200])
                url = e.get("source_url","")
                src = _h.escape(e.get("source_type",""))
                link = f' <a href="{url}" target="_blank" rel="noopener" class="prid">[{src}]</a>' if url and url.startswith("http") else f' <span class="prid">[{src}]</span>'
                parts.append(f'<div style="font-size:.85rem;margin:5px 0 0;"><b>{fig}</b> — {fact}{link}</div>')
            arts = sc.get("news_articles", [])
            if arts:
                parts.append('<div style="font-size:.78rem;color:var(--muted);margin-top:6px;font-family:-apple-system,sans-serif;">News: '
                             + " · ".join(f'<a href="{a["url"]}" target="_blank" rel="noopener" style="color:var(--accent)">{_h.escape(a["outlet"])} ({_h.escape(str(a.get("date",""))[:10])})</a>'
                                          for a in arts[:3] if a.get("url","").startswith("http")) + "</div>")
            parts.append("</div>")
        parts.append("</section>")
    return "\n".join(parts)


def render_policy_annex():
    """Annex: clearance-register policy findings + the source cross-verification
    matrix (layer 24c). Injected into both reportage variants via __POLICY__.

    The point of the matrix: no committed company name rests on a single source.
    EC/FC counts are ground-truthed direct from the raw PARIVESH registers and
    are deliberately BROADER (all years/statuses) than the 2025-26 lead subset."""
    import json, os
    p = os.path.join(ROOT, "layers/24c_cross_verification.json")
    if not os.path.exists(p):
        return ""
    d = json.load(open(p))
    rows = []
    for r in sorted(d["companies"], key=lambda r: -( (r.get("ec_register") or {}).get("filings",0) + (r.get("fc_register") or {}).get("filings",0) )):
        ec = (r.get("ec_register") or {}).get("filings")
        fc = (r.get("fc_register") or {}).get("filings")
        pib = (r.get("pib_headlines") or {}).get("headlines")
        def cell(v, cls="y"):
            return f'<td class="cv {cls}">{v}</td>' if v else '<td class="cv n">—</td>'
        nv = r.get("news_verdict") or ""
        nvc = {"ANNOUNCED":"y","PARTIALLY_VISIBLE":"p","QUIET":"q"}.get(nv,"n")
        ib = r.get("ibef")   # True / False / None(=not checked)
        ibcell = ('<td class="cv y">✓</td>' if ib is True
                  else '<td class="cv n">—</td>' if ib is False
                  else '<td class="cv" style="opacity:.3">·</td>')
        rows.append(
            f'<tr><td class="cn">{_h.escape(r["company"])}</td>'
            + cell(ec) + cell(fc)
            + cell(pib)
            + cell("✓" if r.get("iem_partB_sample") else None)
            + cell("✓" if r.get("state_govt_announcement") else None)
            + cell("✓" if r.get("pli_ebp_register") else None)
            + cell("✓" if r.get("credit_rating_public") else None)
            + ibcell
            + f'<td class="cv {nvc}">{nv.replace("_"," ").title() or "—"}</td></tr>')
    return f"""
<section id="policy-annex" style="max-width:1100px;margin:40px auto 20px;padding:0 20px;">
<h2 style="font-family:Georgia,serif;font-weight:500;">Annex — what the clearance registers add (policy findings)</h2>
<div style="font-size:.92rem;max-width:80ch;line-height:1.55;">
<p><b>1. Half of India's live industrial EC pipeline is chemicals.</b> Of 1,384 live corporate industrial
filers beyond the verified leads, 51% file under synthetic-organic-chemicals — the China import-substitution
story is already the dominant physical activity in the clearance register, mostly self-funded and mostly
unannounced.</p>
<p><b>2. The API localisation wave is running outside PLI.</b> The only confirmed KSM/API-PLI beneficiary
in the 98 verified leads (Orchid Pharma, ₹600 cr 7-ACA) carries the cohort's worst execution profile
(land delays, downgrade), while IOL, Farmson, Anthem, Aarti, Piramal and Virupaksha localise the same
China-dependent chains self-funded. Land assembly, not incentive size, is the binding constraint.</p>
<p><b>3. Verified foreign capex is visible in the registers before the press.</b> Lanxess (DE), Pernod
Ricard (FR, ₹1,785 cr Nagpur), HS Hyosung (KR, ~₹3,000 cr cumulative), Kansai Nerolac (JP), Sumitomo (JP,
via TruAlt), plus SRF's Odisha filings fronting the ₹10,000 cr pledge.</p>
<p><b>4. Cross-verification: no name rests on one source.</b> All 41 headline companies ground-truth in the
raw PARIVESH registers; only 17 have <i>ever</i> appeared in a PIB headline — the registers see ~2.4× more
of these investors than PIB headlines do. IEM Part-B company data is held for only two sample months, so
absence there is weak evidence.</p>
<p><b>5. Rating darkness is a screening signal.</b> Withdrawn or issuer-not-cooperating credit ratings
cluster around exactly the companies expanding quietly — Farmson (CARE withdrawn 2023, world's largest
paracetamol maker), RSL/RSLD (CARE withdrawn 2025 after disclosing SEBI/IT/ED promoter litigations),
Bodal (CRISIL withdrawn), D&nbsp;R&nbsp;Coats and Matangi (non-cooperating, Matangi the same quarter it
filed ECs), Sandhya (non-cooperating). Announcement darkness and rating darkness travel together:
a live clearance filing plus a dead rating is itself a below-radar-expansion screen — and where the
last rationale exists, it often carries the only adverse disclosures (litigations, guarantees) no
other public source records.</p>
<p><b>6. IBEF promotes the themes, misses the executors.</b> The Commerce-Ministry trust's coverage actively
champions all four policy narratives — specialty-chem import substitution, API/KSM PLI, E20 ethanol, MMF PLI —
with the exact framing this analysis uses. But its company coverage tracks <i>listing status</i>, not
clearance activity: 20 of 37 checked names have zero IBEF footprint, including marquee FDI stories (Hyosung's
$100M spandex plant, Pernod Ricard's ₹1,785 cr distillery) and every quiet builder. The quasi-official
promotion channel validates the macro thesis while missing the specific companies executing it — the
clearance register is the earlier, more complete signal.</p></div>
<style>
#policy-annex table{{border-collapse:collapse;width:100%;font-size:.78rem}}
#policy-annex th{{font-size:.62rem;text-transform:uppercase;letter-spacing:.05em;text-align:left;padding:5px 7px;border-bottom:1px solid var(--rule,#ccc);opacity:.7}}
#policy-annex td{{padding:4px 7px;border-bottom:1px solid var(--rule,#e3e3dc)}}
#policy-annex td.cn{{white-space:nowrap;font-weight:600}}
#policy-annex td.cv{{text-align:center;font-variant-numeric:tabular-nums}}
#policy-annex td.cv.n{{opacity:.35}} #policy-annex td.cv.y{{color:#2f7d4f}} #policy-annex td.cv.p{{color:#8a5a12}} #policy-annex td.cv.q{{color:#a5402c;font-weight:600}}
#policy-annex .scroll{{overflow-x:auto}}
</style>
<div class="scroll"><table>
<thead><tr><th>Company</th><th>EC register<br>(all-time filings)</th><th>Forest reg.</th><th>PIB headlines<br>(2017-26)</th>
<th>IEM Part-B<br>(2-mo sample)</th><th>State-govt<br>announcement</th><th>PLI / EBP<br>register</th><th>Public credit<br>rating</th><th>IBEF<br>coverage</th><th>News verdict</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p style="font-size:.72rem;opacity:.65;max-width:86ch;">EC/Forest counts are ground-truthed from the raw PARIVESH
registers (all years, statuses, activities) and are deliberately broader than the 2025-26 live-manufacturing
subset used for lead scoring. PIB is a title-only index — annexure PDFs are a known blind spot. "Quiet" = live
clearance filings with zero press. Sources &amp; data: layers/24_clearance_leads.json · 24b_pool_policy_triage.json ·
24c_cross_verification.json. Generated {datetime.date.today().isoformat()}.</p>
{render_up_ethanol()}
</section>"""




def render_up_ethanol():
    """Case study injected under the policy annex: UP ethanol, register x news
    (layer 24d). UP is the EBP's #1 state -- the table shows every significant
    live 5(g) filer with its news-verified project detail."""
    import json, os
    p = os.path.join(ROOT, "layers/24d_up_ethanol.json")
    if not os.path.exists(p):
        return ""
    d = json.load(open(p))
    ra = d["register_aggregates"]
    rows = "".join(
        f'<tr><td class="cn">{_h.escape(r["company"])}</td>'
        f'<td>{_h.escape(r["district"])}</td>'
        f'<td>{_h.escape(r["capacity"])}</td>'
        f'<td>{_h.escape(r["feedstock"])}</td>'
        f'<td class="cv">{("&#8377;" + format(round(r["capex_rs_cr"]), ",") + " cr") if r["capex_rs_cr"] else "—"}</td>'
        f'<td class="cv {"q" if "QUIET" in r["status"] else "y"}">{_h.escape(r["status"])}</td>'
        f'<td style="font-size:.72rem;opacity:.8">{_h.escape(r["note"])}</td></tr>'
        for r in d["companies"])
    return f"""
<h3 style="font-family:Georgia,serif;font-weight:500;margin-top:30px;">Case study — Uttar Pradesh ethanol: the register × the news</h3>
<div style="font-size:.9rem;max-width:82ch;line-height:1.5;">
<p>{_h.escape(d["up_context"])}</p>
<p>The PARIVESH register holds <b>{ra["up_5g_proposals_total"]} UP distillery (5(g)) proposals</b> —
<b>{ra["live"]} live</b> across <b>{ra["unique_companies"]} companies</b>. The {len(d["companies"])} most
significant, register-verified and news-checked:</p></div>
<div class="scroll"><table>
<thead><tr><th>Company</th><th>District</th><th>Capacity / project</th><th>Feedstock</th><th>Capex</th><th>Status</th><th>Note</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p style="font-size:.72rem;opacity:.65;max-width:86ch;">Register side = PARIVESH EC 5(g) filings (all years; live = granted
+ in-process). News side = 2024-26 sweep. Notables: Karimganj's UP-vs-Assam location discrepancy resolved (Moradabad);
TQN "Retails" verified as a genuine &#8377;224 cr ethanol proponent; Modi Illva is potable malt, not EBP — feedstock
disambiguation applied. Data: layers/24d_up_ethanol.json.</p>"""
