#!/usr/bin/env python3
"""Company directory, grouped by sector then state -- a row-level companion to
layer 43's aggregate convergence view (which only carries counts, not names).

Reuses layer 43's loaders directly rather than duplicating the state/city
extraction and state_landings parsing logic. Three clearly separate tiers,
never merged into one list since they mean different things:
  - REVEALED (layer 42) -- real, dated, verified investment/JV/plant events.
  - MOU-SIGNED (layer 44) -- a specific state-investor-summit MoU, tracked
    with its own follow_through_status (most MoUs never convert).
  - POLICY-ELIGIBLE (layer 16 state_landings) -- scheme-eligibility only.

Usage: python3 scripts/build_company_directory_state_sector.py
Output: docs/company_directory_state_sector.html
"""
import datetime as dt
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_layer43_state_sector_convergence import load_revealed, load_policy_eligible  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_HTML = os.path.join(ROOT, "docs", "company_directory_state_sector.html")


def load_mou():
    """layer 44 -> state -> [mou records]"""
    p = os.path.join(ROOT, "layers", "44_state_mou_5yr_sweep.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p))
    out = {}
    for st, sd in d.get("by_state", {}).items():
        out[st] = sd["mous"]
    return out


def _esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    revealed = load_revealed()
    policy = load_policy_eligible()

    sectors = sorted({r["sector"] for r in revealed} | {r["sector"] for r in policy})

    # sector -> state -> [rows]
    rev_by_sector_state = defaultdict(lambda: defaultdict(list))
    for r in revealed:
        rev_by_sector_state[r["sector"]][r["state"]].append(r)

    pol_by_sector_state = defaultdict(lambda: defaultdict(set))
    for r in policy:
        pol_by_sector_state[r["sector"]][r["state"]].add(r["company"])

    mou_by_state = load_mou()
    mou_total = sum(len(v) for v in mou_by_state.values())

    revealed_companies = len({(r["company"], r["sector"]) for r in revealed})
    policy_companies = len({(r["company"], r["sector"]) for r in policy})

    today = dt.date.today().isoformat()
    L = []
    L.append('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    L.append(f'<title>Company Directory — by Sector &amp; State ({today})</title>')
    L.append('<style>')
    L.append(':root { --bg:#fff; --fg:#1a1a1a; --mut:#666; --card:#f6f6f4; --acc:#0b5cad; --bd:#e2e2de; --hi:#1a8f4c; --hisoft:#e6f5ec; --pol:#8a5a00; --polsoft:#fbf1de; --mou:#8a2a8a; --mousoft:#f7e9f7; }')
    L.append('@media (prefers-color-scheme: dark) { :root { --bg:#14151a; --fg:#e8e8e8; --mut:#9a9a9a; --card:#1e2027; --acc:#6ab0f3; --bd:#2c2e36; --hi:#5fd08c; --hisoft:#132a1e; --pol:#e0b366; --polsoft:#2a2214; --mou:#d68ad6; --mousoft:#2a1c2a; } }')
    L.append('body { margin:0; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); }')
    L.append('.wrap { max-width:980px; margin:0 auto; padding:32px 20px 60px; }')
    L.append('h1 { font-size:1.5em; margin:0 0 4px; }')
    L.append('.sub { color:var(--mut); font-size:.9em; margin-bottom:20px; max-width:760px; }')
    L.append('.stats { display:flex; gap:12px; flex-wrap:wrap; margin:18px 0 26px; }')
    L.append('.stat { background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 18px; }')
    L.append('.stat b { font-size:1.4em; display:block; }')
    L.append('.stat span { color:var(--mut); font-size:.82em; }')
    L.append('.tabbar { display:flex; gap:8px; margin:10px 0 22px; position:sticky; top:0; background:var(--bg); padding:10px 0; z-index:5; border-bottom:1px solid var(--bd); }')
    L.append('.tab { cursor:pointer; padding:7px 16px; border-radius:20px; border:1px solid var(--bd); background:var(--card); font-size:.85em; font-weight:600; }')
    L.append('.tab.active.rev { background:var(--hisoft); color:var(--hi); border-color:var(--hi); }')
    L.append('.tab.active.mou { background:var(--mousoft); color:var(--mou); border-color:var(--mou); }')
    L.append('.tab.active.pol { background:var(--polsoft); color:var(--pol); border-color:var(--pol); }')
    L.append('.search { width:100%; box-sizing:border-box; padding:9px 12px; border-radius:8px; border:1px solid var(--bd); background:var(--card); color:var(--fg); font-size:.9em; margin:0 0 20px; }')
    L.append('details.sector { background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 16px; margin:10px 0; }')
    L.append('summary { cursor:pointer; font-weight:700; font-size:1.02em; }')
    L.append('.cnt { border-radius:10px; padding:1px 9px; font-size:.72em; margin-left:6px; font-weight:600; }')
    L.append('.cnt.rev { background:var(--hisoft); color:var(--hi); }')
    L.append('.cnt.mou { background:var(--mousoft); color:var(--mou); }')
    L.append('.cnt.pol { background:var(--polsoft); color:var(--pol); }')
    L.append('.status { font-size:.72em; border-radius:6px; padding:1px 7px; font-weight:600; white-space:nowrap; background:var(--card); border:1px solid var(--bd); color:var(--mut); }')
    L.append('.status.op { background:var(--hisoft); color:var(--hi); border-color:transparent; }')
    L.append('h3.state { font-size:.9em; text-transform:uppercase; letter-spacing:.03em; color:var(--mut); margin:16px 0 6px; border-top:1px solid var(--bd); padding-top:12px; }')
    L.append('ul.co { list-style:none; margin:0; padding:0; }')
    L.append('li.co { padding:5px 0; border-top:1px solid var(--bd); display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; }')
    L.append('li.co:first-child { border-top:none; }')
    L.append('.badge { font-size:.72em; border-radius:6px; padding:1px 7px; font-weight:600; white-space:nowrap; }')
    L.append('.badge.HIGH { background:var(--hisoft); color:var(--hi); }')
    L.append('.badge.MEDIUM { background:var(--polsoft); color:var(--pol); }')
    L.append('.badge.LOW { background:var(--card); color:var(--mut); border:1px solid var(--bd); }')
    L.append('.date { color:var(--mut); font-size:.8em; font-variant-numeric:tabular-nums; }')
    L.append('a { color:var(--acc); text-decoration:none; } a:hover { text-decoration:underline; }')
    L.append('.pol-list { color:var(--mut); font-size:.88em; }')
    L.append('.note { color:var(--mut); font-size:.82em; margin-top:34px; border-top:1px solid var(--bd); padding-top:12px; }')
    L.append('.hidden { display:none !important; }')
    L.append('</style></head><body><div class="wrap">')

    L.append('<h1>Company Directory — by Sector &amp; State</h1>')
    L.append('<p class="sub">Every company the twin has tagged to an Indian state. '
             '<b>Revealed</b> = real, dated investment/JV/plant events (layer 42) — companies that have '
             'actually chosen a state, grouped by sector. <b>MoU-signed</b> = a specific state-investor-summit '
             'MoU (layer 44, 5-year window) — tracked with its own follow-through status, since most Indian '
             'state MoUs never convert; grouped by state. <b>Policy-eligible</b> = which states\' scheme '
             'stacks make a company\'s sector eligible to land there (layer 16) — eligibility, not a '
             'confirmed choice, grouped by sector. Never merged; toggle between them below.</p>')

    L.append('<div class="stats">')
    L.append(f'<div class="stat"><b>{revealed_companies}</b><span>revealed company×sector</span></div>')
    L.append(f'<div class="stat"><b>{mou_total}</b><span>MoUs signed (5yr)</span></div>')
    L.append(f'<div class="stat"><b>{policy_companies}</b><span>policy-eligible company×sector</span></div>')
    L.append(f'<div class="stat"><b>{len(sectors)}</b><span>sectors</span></div>')
    L.append('</div>')

    L.append('<div class="tabbar">')
    L.append('<div class="tab active rev" id="tabRev" onclick="showTab(\'rev\')">Revealed</div>')
    L.append('<div class="tab mou" id="tabMou" onclick="showTab(\'mou\')">MoU-signed</div>')
    L.append('<div class="tab pol" id="tabPol" onclick="showTab(\'pol\')">Policy-eligible</div>')
    L.append('</div>')
    L.append('<input class="search" id="search" placeholder="Filter by company, state, or sector…" oninput="filterAll()">')

    # ---- Revealed section ----
    L.append('<div id="panelRev">')
    for sec in sectors:
        states = rev_by_sector_state.get(sec, {})
        n = sum(len(v) for v in states.values())
        L.append(f'<details class="sector" open data-sector="{_esc(sec.lower())}"><summary>{_esc(sec)} <span class="cnt rev">{n}</span></summary>')
        if states:
            for st in sorted(states.keys()):
                rows = sorted(states[st], key=lambda r: (r.get("date") or "", r["company"]))
                L.append(f'<h3 class="state">{_esc(st)} <span class="cnt rev">{len(rows)}</span></h3>')
                L.append('<ul class="co">')
                for r in rows:
                    link = f'<a href="{_esc(r.get("source_url",""))}" target="_blank" rel="noopener">{_esc(r["company"])}</a>' if r.get("source_url") else _esc(r["company"])
                    newtag = ' <span class="badge HIGH" style="opacity:.7">NEW</span>' if r.get("new_to_twin") else ''
                    L.append(f'<li class="co" data-txt="{_esc((r["company"]+" "+st+" "+sec).lower())}">'
                             f'<span>{link}{newtag}</span>'
                             f'<span><span class="badge {_esc(r.get("confidence") or "LOW")}">{_esc(r.get("confidence") or "—")}</span> '
                             f'<span class="date">{_esc(r.get("date") or "")}</span></span></li>')
                L.append('</ul>')
        else:
            L.append('<p class="pol-list">No revealed events for this sector yet.</p>')
        L.append('</details>')
    L.append('</div>')

    # ---- MoU-signed section (grouped by state; sector text isn't canonicalized here) ----
    L.append('<div id="panelMou" class="hidden">')
    for st in sorted(mou_by_state.keys()):
        rows = sorted(mou_by_state[st], key=lambda r: (r.get("mou_date") or ""), reverse=True)
        L.append(f'<details class="sector" data-sector="{_esc(st.lower())}"><summary>{_esc(st)} <span class="cnt mou">{len(rows)}</span></summary>')
        L.append('<ul class="co">')
        for r in rows:
            company = r.get("company", "")
            url = (r.get("source_url") or "").split(";")[0].strip()
            link = f'<a href="{_esc(url)}" target="_blank" rel="noopener">{_esc(company)}</a>' if url else _esc(company)
            newtag = ' <span class="badge HIGH" style="opacity:.7">NEW</span>' if r.get("new_to_twin") else ''
            status = (r.get("follow_through_status") or "").split(" -- ")[0].split(" (")[0].strip()
            status_cls = "op" if status.lower() in ("operational", "under construction") else ""
            sector = _esc((r.get("sector") or "")[:70])
            txt = _esc((company + " " + st + " " + (r.get("sector") or "") + " " + (r.get("country_of_headquarters") or "")).lower())
            L.append(f'<li class="co" data-txt="{txt}">'
                     f'<span>{link}{newtag}<br><span class="date">{sector} · {_esc(r.get("country_of_headquarters",""))}</span></span>'
                     f'<span><span class="status {status_cls}">{_esc(status or "—")}</span> '
                     f'<span class="badge {_esc(r.get("confidence") or "LOW")}">{_esc(r.get("confidence") or "—")}</span> '
                     f'<span class="date">{_esc(r.get("mou_date") or "")}</span></span></li>')
        L.append('</ul></details>')
    L.append('</div>')

    # ---- Policy-eligible section ----
    L.append('<div id="panelPol" class="hidden">')
    for sec in sectors:
        states = pol_by_sector_state.get(sec, {})
        companies = sorted({c for v in states.values() for c in v})
        L.append(f'<details class="sector" data-sector="{_esc(sec.lower())}"><summary>{_esc(sec)} <span class="cnt pol">{len(companies)}</span></summary>')
        if states:
            for st in sorted(states.keys()):
                cos = sorted(states[st])
                L.append(f'<h3 class="state">{_esc(st)} <span class="cnt pol">{len(cos)}</span></h3>')
                L.append('<p class="pol-list" data-txt="' + _esc((" ".join(cos) + " " + st + " " + sec).lower()) + '">' + _esc(", ".join(cos)) + '</p>')
        else:
            L.append('<p class="pol-list">No policy-eligible landings for this sector.</p>')
        L.append('</details>')
    L.append('</div>')

    L.append('<p class="note">Generated by <code>scripts/build_company_directory_state_sector.py</code> from '
             '<code>layers/42_sector_investment_news_sweep.json</code> (revealed), '
             '<code>layers/44_state_mou_5yr_sweep.json</code> (MoU-signed), and '
             '<code>layers/16_leads.json</code> (policy-eligible). See '
             '<a href="reportage_state_sector.html">reportage_state_sector.html</a> for the aggregate '
             'convergence view and <a href="STATE_MOU_5YR_SWEEP.md">STATE_MOU_5YR_SWEEP.md</a> for full '
             'MoU methodology notes.</p>')

    L.append('<script>')
    L.append('function showTab(which){')
    L.append('  document.getElementById("tabRev").classList.toggle("active", which==="rev");')
    L.append('  document.getElementById("tabMou").classList.toggle("active", which==="mou");')
    L.append('  document.getElementById("tabPol").classList.toggle("active", which==="pol");')
    L.append('  document.getElementById("panelRev").classList.toggle("hidden", which!=="rev");')
    L.append('  document.getElementById("panelMou").classList.toggle("hidden", which!=="mou");')
    L.append('  document.getElementById("panelPol").classList.toggle("hidden", which!=="pol");')
    L.append('}')
    L.append('function filterAll(){')
    L.append('  const q = document.getElementById("search").value.trim().toLowerCase();')
    L.append('  document.querySelectorAll("li.co[data-txt], p.pol-list[data-txt]").forEach(el => {')
    L.append('    el.classList.toggle("hidden", q && !el.dataset.txt.includes(q));')
    L.append('  });')
    L.append('  document.querySelectorAll("details.sector").forEach(d => {')
    L.append('    const hasVisible = !q || d.querySelector("[data-txt]:not(.hidden)") || d.dataset.sector.includes(q);')
    L.append('    d.classList.toggle("hidden", !hasVisible);')
    L.append('    if (q) d.open = true;')
    L.append('  });')
    L.append('}')
    L.append('</script>')

    L.append('</div></body></html>')
    with open(OUT_HTML, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"revealed: {revealed_companies} company×sector, policy-eligible: {policy_companies} company×sector -> {OUT_HTML}")


if __name__ == "__main__":
    main()
