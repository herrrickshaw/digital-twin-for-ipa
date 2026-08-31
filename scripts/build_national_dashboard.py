#!/usr/bin/env python3
"""National dashboard — one page combining all 44 layers, with a featured
MoU news-wire section up top (per explicit request: focus on MoU-related
news articles).

Two tiers, deliberately different treatment:
  1. FEATURED MoU news wire (layer 44) -- rendered as real article cards
     (company, state, sector, headline figure, date, follow-through status,
     source link), sortable/filterable, sorted newest-first. This is the
     centerpiece.
  2. Workstream tiles -- curated groups of the twin's other layers, each a
     one-line headline stat + link to that layer's own detailed doc/HTML
     where one exists. A generic best-effort summarizer covers every layer
     file in a compact index at the bottom so nothing is hidden, even layers
     with no hand-written description.

Usage: python3 scripts/build_national_dashboard.py
Output: docs/national_dashboard.html
"""
import datetime as dt
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS_DIR = os.path.join(ROOT, "layers")
OUT_HTML = os.path.join(ROOT, "docs", "national_dashboard.html")


def _esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load(name):
    p = os.path.join(LAYERS_DIR, f"{name}.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def generic_summary(path):
    try:
        d = json.load(open(path))
    except Exception as e:
        return f"error: {e}"
    if not isinstance(d, dict):
        return f"{type(d).__name__}, {len(d)} items"
    # layer 32's most representative number lives under counts.companies, not
    # its longest list -- override before falling through to generic logic
    if os.path.basename(path) == "32_company_db.json" and isinstance(d.get("counts"), dict):
        return f"companies: {d['counts'].get('companies', '—')} (deduped, all layers)"
    for k in ["count", "total_findings", "total_new_flagged", "total_new_to_twin", "total_mous",
              "known_company_count", "total_records_available"]:
        if k in d:
            return f"{k.replace('_', ' ')}: {d[k]}"
    best = None
    for k, v in d.items():
        if isinstance(v, list) and (best is None or len(v) > best[1]):
            best = (k, len(v))
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, list) and (best is None or len(v2) > best[1]):
                    best = (f"{k}.{k2}", len(v2))
    return f"{best[0]}: {best[1]} items" if best else "—"


# -- curated workstream groups: (label, [(layer_num_name, one-line desc, optional link)]) --
FEATURED_GROUPS = [
    ("Company Database & Leads", [
        ("16_leads", "Foreign-company leads, expansion-signal scored", None),
        ("24_clearance_leads", "Clearance-committee-visible leads (FIPB/CCI successors)", None),
        ("32_company_db", "Unified company DB — every company the twin has touched, deduped", None),
        ("37_global_sweep_targets", "Filing-sweep consolidation (DART/cninfo/Oslo/EDINET/ESEF)", None),
    ]),
    ("Land, Policy & Incentives", [
        ("02_incentive_catalog_v1", "Central incentive scheme catalog by ministry", None),
        ("25_land_incentive_linkages", "Vacant developed land × open incentive windows, joined", None),
        ("28_policy_watchlist", "Forward-looking: new policy before it's in force (973 PRS bills)", None),
        ("33_policy_finance_extensions", "Policy/finance extensions (CBG-GOBARdhan, bulk-sale notices)", None),
        ("35_capital_cost_arbitrage_lens", "Policy-rate arbitrage: cheaper capital abroad vs. India", None),
    ]),
    ("Trade & Macro", [
        ("29_mospi_data_sources", "25 MoSPI datasets, tagged for investment relevance", None),
        ("30_trade_deficit_map", "Which import chapters an incentive actually addresses", None),
    ]),
    ("Associations, Events & Trade Fairs", [
        ("39_textile_associations", "Global textile trade association membership map", "ASSOCIATION_EVENT_REGISTRY.md"),
        ("40_association_event_registry", "33 associations, 64 events — durable monitoring registry", "ASSOCIATION_EVENT_REGISTRY.md"),
        ("41_association_leads_crossref", "Exhibitor/member rosters cross-checked against known leads", "ASSOCIATION_LEADS_CROSSREF.md"),
    ]),
    ("Investment News & State Convergence", [
        ("42_sector_investment_news_sweep", "12-sector India-investment news sweep, verified findings", "SECTOR_INVESTMENT_NEWS_SWEEP.md"),
        ("43_state_sector_convergence", "Which states are becoming multi-sector investment hubs", "reportage_state_sector.html"),
        ("44_state_mou_5yr_sweep", "5-year state-MoU sweep — see the featured wire above", "STATE_MOU_5YR_SWEEP.md"),
    ]),
    ("Sector Deep-Dives", [
        ("38_textile_sector_targets", "Textiles & Apparel sector filter + live re-sweep", None),
    ]),
]

CENTRAL_WIRE_LINKS = [
    ("reportage.html", "PIB scheme-mapped announcements, all quarters"),
    ("reportage_latest.html", "Central + state wire, rolling 30-day window"),
    ("reportage_ministry.html", "Announcements grouped by ministry"),
    ("reportage_states.html", "State-government wire, classified"),
    ("company_directory_state_sector.html", "Every company, by sector & state — 3 tiers"),
]


def main():
    l44 = load("44_state_mou_5yr_sweep")
    l32 = load("32_company_db")
    l16 = load("16_leads")
    l40 = load("40_association_event_registry")
    l42 = load("42_sector_investment_news_sweep")
    l43 = load("43_state_sector_convergence")

    all_mous = []
    for st, sd in l44.get("by_state", {}).items():
        all_mous.extend(sd.get("mous", []))
    all_mous.sort(key=lambda r: r.get("mou_date") or "", reverse=True)

    companies_tracked = (l32.get("counts") or {}).get("companies", "—")
    foreign_leads = l16.get("count", "—")
    events_n = len(l40.get("events", []))
    assoc_n = len(l40.get("ASSOCIATIONS", l40.get("associations", [])))
    news_findings = l42.get("total_findings", "—")
    states_n = len(l43.get("state_convergence", []))
    mou_n = l44.get("total_mous", len(all_mous))
    mou_new = l44.get("total_new_to_twin", "—")
    graveyard_pct = round(100 * l44.get("follow_through_breakdown", {}).get("no follow-up news found", 0)
                          / max(l44.get("total_mous", 1), 1)) if l44 else "—"

    layer_files = sorted(glob.glob(os.path.join(LAYERS_DIR, "*.json")))
    today = dt.date.today().isoformat()

    L = []
    L.append('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    L.append(f'<title>National Dashboard — Digital Twin for IPA ({today})</title>')
    L.append('<style>')
    L.append(':root { --bg:#fff; --fg:#1a1a1a; --mut:#666; --card:#f6f6f4; --acc:#0b5cad; --bd:#e2e2de;'
             ' --hi:#1a8f4c; --hisoft:#e6f5ec; --mou:#8a2a8a; --mousoft:#f7e9f7; --warn:#a3480e; --warnsoft:#fbeade; }')
    L.append('@media (prefers-color-scheme: dark) { :root { --bg:#14151a; --fg:#e8e8e8; --mut:#9a9a9a;'
             ' --card:#1e2027; --acc:#6ab0f3; --bd:#2c2e36; --hi:#5fd08c; --hisoft:#132a1e; --mou:#d68ad6;'
             ' --mousoft:#2a1c2a; --warn:#e0a15a; --warnsoft:#2a1f14; } }')
    L.append('body { margin:0; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); }')
    L.append('.wrap { max-width:1080px; margin:0 auto; padding:32px 20px 60px; }')
    L.append('h1 { font-size:1.6em; margin:0 0 4px; }')
    L.append('h2 { font-size:1.2em; margin:38px 0 6px; display:flex; align-items:center; gap:10px; }')
    L.append('h2 .tag { font-size:.5em; background:var(--mousoft); color:var(--mou); border-radius:20px; padding:3px 12px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }')
    L.append('h3 { font-size:.95em; margin:22px 0 8px; color:var(--mut); text-transform:uppercase; letter-spacing:.03em; }')
    L.append('.sub { color:var(--mut); font-size:.92em; margin-bottom:20px; max-width:820px; }')
    L.append('.stats { display:flex; gap:12px; flex-wrap:wrap; margin:18px 0 26px; }')
    L.append('.stat { background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 18px; min-width:100px; }')
    L.append('.stat b { font-size:1.5em; display:block; font-variant-numeric:tabular-nums; }')
    L.append('.stat span { color:var(--mut); font-size:.8em; }')
    L.append('.search { width:100%; box-sizing:border-box; padding:10px 14px; border-radius:8px; border:1px solid var(--bd); background:var(--card); color:var(--fg); font-size:.92em; margin:10px 0 16px; }')
    L.append('.filters { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }')
    L.append('.chip { cursor:pointer; padding:5px 13px; border-radius:16px; border:1px solid var(--bd); background:var(--card); font-size:.78em; font-weight:600; color:var(--mut); }')
    L.append('.chip.active { background:var(--mousoft); color:var(--mou); border-color:var(--mou); }')
    L.append('.card { background:var(--card); border:1px solid var(--bd); border-radius:12px; padding:16px 18px; margin:10px 0; }')
    L.append('.card-head { display:flex; justify-content:space-between; align-items:baseline; gap:12px; flex-wrap:wrap; }')
    L.append('.card-head a { font-weight:700; font-size:1.03em; color:var(--acc); text-decoration:none; }')
    L.append('.card-head a:hover { text-decoration:underline; }')
    L.append('.card-meta { color:var(--mut); font-size:.82em; margin:4px 0 8px; }')
    L.append('.card-body { font-size:.9em; color:var(--fg); }')
    L.append('.badge { font-size:.72em; border-radius:6px; padding:2px 8px; font-weight:700; white-space:nowrap; }')
    L.append('.badge.HIGH { background:var(--hisoft); color:var(--hi); }')
    L.append('.badge.MEDIUM { background:var(--warnsoft); color:var(--warn); }')
    L.append('.badge.LOW { background:var(--card); color:var(--mut); border:1px solid var(--bd); }')
    L.append('.status { font-size:.75em; border-radius:6px; padding:2px 9px; font-weight:700; background:var(--bg); border:1px solid var(--bd); color:var(--mut); }')
    L.append('.status.op { background:var(--hisoft); color:var(--hi); border-color:transparent; }')
    L.append('.state-tag { font-size:.75em; font-weight:700; color:var(--mou); }')
    L.append('.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px; margin:10px 0 6px; }')
    L.append('.tile { background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:14px 16px; }')
    L.append('.tile b { display:block; font-size:.95em; margin-bottom:3px; }')
    L.append('.tile span { color:var(--mut); font-size:.85em; }')
    L.append('.tile a { color:var(--acc); text-decoration:none; font-size:.8em; }')
    L.append('.tile a:hover { text-decoration:underline; }')
    L.append('a.link-list { color:var(--acc); text-decoration:none; }')
    L.append('a.link-list:hover { text-decoration:underline; }')
    L.append('table.idx { width:100%; border-collapse:collapse; font-size:.85em; margin:10px 0; }')
    L.append('table.idx th, table.idx td { text-align:left; padding:5px 10px; border-bottom:1px solid var(--bd); }')
    L.append('table.idx th { color:var(--mut); font-weight:600; font-size:.85em; }')
    L.append('.note { color:var(--mut); font-size:.82em; margin-top:40px; border-top:1px solid var(--bd); padding-top:14px; }')
    L.append('.hidden { display:none !important; }')
    L.append('</style></head><body><div class="wrap">')

    L.append('<h1>Digital Twin for IPA — National Dashboard</h1>')
    L.append('<p class="sub">One page combining every layer the twin tracks — from central scheme rules '
             'to state-government press wires to live investment-news sweeps. The featured section below '
             'is the state-MoU news wire (layer 44): every individually-verified foreign-company MoU '
             'signed at a state investor summit since 2021, presented as real news articles with sources, '
             'not just aggregate counts.</p>')

    L.append('<div class="stats">')
    L.append(f'<div class="stat"><b>{companies_tracked}</b><span>companies tracked</span></div>')
    L.append(f'<div class="stat"><b>{foreign_leads}</b><span>foreign leads</span></div>')
    L.append(f'<div class="stat"><b>{mou_n}</b><span>state MoUs (5yr)</span></div>')
    L.append(f'<div class="stat"><b>{graveyard_pct}%</b><span>MoUs with no follow-up</span></div>')
    L.append(f'<div class="stat"><b>{news_findings}</b><span>investment-news findings</span></div>')
    L.append(f'<div class="stat"><b>{states_n}</b><span>states w/ any signal</span></div>')
    L.append(f'<div class="stat"><b>{events_n}</b><span>trade-fair events tracked</span></div>')
    L.append(f'<div class="stat"><b>{len(layer_files)}</b><span>layers</span></div>')
    L.append('</div>')

    # ================= FEATURED: MoU NEWS WIRE =================
    L.append('<h2>MoU News Wire <span class="tag">Featured</span></h2>')
    L.append('<p class="sub">Every verified state-investor-summit MoU, 2021–2026 — read as news, not a '
             'spreadsheet. Each card links to its real source article. Status is tracked separately from '
             'the signing: most MoUs in India never get an independent follow-up story, and that\'s shown '
             'honestly, not hidden.</p>')

    states_list = sorted({m.get("state") or "—" for m in all_mous})
    L.append('<input class="search" id="mouSearch" placeholder="Search company, state, sector, or country…" oninput="filterMou()">')
    L.append('<div class="filters" id="statusFilters">')
    for st in ["all", "operational", "under construction", "no follow-up news found", "publicly stalled/withdrawn"]:
        cls = "active" if st == "all" else ""
        L.append(f'<div class="chip {cls}" data-status="{_esc(st)}" onclick="setStatusFilter(this)">{_esc(st if st!="all" else "All statuses")}</div>')
    L.append('</div>')

    L.append('<div id="mouCards">')
    for m in all_mous:
        company = m.get("company", "")
        country = m.get("country_of_headquarters", "")
        state = m.get("state", "")
        sector = m.get("sector", "")
        raw_status = (m.get("follow_through_status") or "").strip()
        status_key = raw_status.split(" -- ")[0].split(" (")[0].strip().lower()
        status_cls = "op" if status_key in ("operational", "under construction") else ""
        detail = m.get("status_detail") or (raw_status if " -- " in raw_status or " (" in raw_status else "")
        url = (m.get("source_url") or "").split(";")[0].strip()
        event = m.get("summit_or_event", "")
        date = m.get("mou_date", "")
        inv = m.get("proposed_investment", "")
        conf = m.get("confidence", "MEDIUM")
        txt = _esc(f"{company} {state} {sector} {country} {status_key}".lower())

        L.append(f'<div class="card" data-status="{_esc(status_key)}" data-txt="{txt}">')
        L.append('<div class="card-head">')
        if url:
            L.append(f'<a href="{_esc(url)}" target="_blank" rel="noopener">{_esc(company)}</a>')
        else:
            L.append(f'<span style="font-weight:700">{_esc(company)}</span>')
        L.append(f'<span class="state-tag">{_esc(state)}</span>')
        L.append('</div>')
        L.append(f'<div class="card-meta">{_esc(country)} · {_esc(sector)} · {_esc(event)} · {_esc(date)}</div>')
        if inv:
            L.append(f'<div class="card-body"><b>{_esc(inv[:220])}</b></div>')
        if detail:
            L.append(f'<div class="card-body" style="margin-top:6px;color:var(--mut)">{_esc(detail[:320])}</div>')
        L.append(f'<div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">'
                 f'<span class="status {status_cls}">{_esc(raw_status.split(" -- ")[0].split(" (")[0] or "—")}</span>'
                 f'<span class="badge {_esc(conf)}">{_esc(conf)}</span></div>')
        L.append('</div>')
    L.append('</div>')
    L.append('<p class="sub" id="mouEmpty" class="hidden">No MoUs match this filter.</p>')

    # ================= Workstream tiles =================
    L.append('<h2>All layers, by workstream</h2>')
    for group_name, items in FEATURED_GROUPS:
        L.append(f'<h3>{_esc(group_name)}</h3><div class="grid">')
        for layer_id, desc, link in items:
            path = os.path.join(LAYERS_DIR, f"{layer_id}.json")
            stat = generic_summary(path) if os.path.exists(path) else "—"
            num = layer_id.split("_")[0]
            L.append('<div class="tile">')
            L.append(f'<b>Layer {_esc(num)}</b><span>{_esc(desc)}</span><br>')
            L.append(f'<span style="font-variant-numeric:tabular-nums">{_esc(stat)}</span>')
            if link:
                L.append(f' — <a href="{_esc(link)}">view</a>')
            L.append('</div>')
        L.append('</div>')

    L.append('<h3>Central &amp; state government wire</h3><div class="grid">')
    for href, desc in CENTRAL_WIRE_LINKS:
        L.append(f'<div class="tile"><b><a href="{_esc(href)}" style="color:var(--acc)">{_esc(href)}</a></b><span>{_esc(desc)}</span></div>')
    L.append('</div>')

    # ================= Full layer index =================
    L.append('<h2>Full layer index</h2>')
    L.append('<p class="sub">Every layer file, auto-summarized (best-effort headline stat), for the ones '
             'not called out above — mostly foundational/infrastructure layers (data model, ministry '
             'master, scheme registry, workflow scaffolding).</p>')
    featured_ids = {item[0] for _, items in FEATURED_GROUPS for item in items}
    L.append('<table class="idx"><thead><tr><th>Layer</th><th>Headline stat</th></tr></thead><tbody>')
    for p in layer_files:
        base = os.path.basename(p)[:-5]
        if base in featured_ids or base == "44_state_mou_5yr_sweep":
            continue
        L.append(f'<tr><td>{_esc(base)}</td><td>{_esc(generic_summary(p))}</td></tr>')
    L.append('</tbody></table>')

    L.append('<p class="note">Generated by <code>scripts/build_national_dashboard.py</code>. '
             'MoU data: <code>layers/44_state_mou_5yr_sweep.json</code>. Company DB: '
             '<code>layers/32_company_db.json</code> (SQLite at <code>data/companies.db</code>). '
             'See <a href="../README.md">README.md</a> for full per-layer methodology.</p>')

    L.append('<script>')
    L.append('let statusFilter = "all";')
    L.append('function setStatusFilter(el){')
    L.append('  statusFilter = el.dataset.status;')
    L.append('  document.querySelectorAll("#statusFilters .chip").forEach(c => c.classList.toggle("active", c===el));')
    L.append('  filterMou();')
    L.append('}')
    L.append('function filterMou(){')
    L.append('  const q = document.getElementById("mouSearch").value.trim().toLowerCase();')
    L.append('  let visible = 0;')
    L.append('  document.querySelectorAll("#mouCards .card").forEach(c => {')
    L.append('    const statusOk = statusFilter === "all" || c.dataset.status === statusFilter;')
    L.append('    const textOk = !q || c.dataset.txt.includes(q);')
    L.append('    const show = statusOk && textOk;')
    L.append('    c.classList.toggle("hidden", !show);')
    L.append('    if (show) visible++;')
    L.append('  });')
    L.append('  document.getElementById("mouEmpty").classList.toggle("hidden", visible > 0);')
    L.append('}')
    L.append('</script>')

    L.append('</div></body></html>')
    with open(OUT_HTML, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"{len(all_mous)} MoU cards, {len(layer_files)} layers indexed -> {OUT_HTML}")


if __name__ == "__main__":
    main()
