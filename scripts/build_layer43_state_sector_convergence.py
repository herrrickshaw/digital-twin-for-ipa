#!/usr/bin/env python3
"""Layer 43 — state x sector convergence reportage.

Answers two questions the twin hadn't answered before: which Indian states
are becoming multi-sector investment hubs (many different sectors landing in
the same state), and within a given sector, which states do companies
actually prefer?

DPIIT's public "Industrial Entrepreneurs Memorandum" (IEM) data was checked
live as a candidate primary source (2026-08-24) -- confirmed real and
current (data.gov.in "Monthly Data on IEM", last updated 2026-08-15), but it
publishes only two SEPARATE one-way aggregates: state totals (144 rows: no
industry axis) and industry totals (40 rows: no state axis). DPIIT has never
published a joint state x industry cross-tabulation, in any of the sources
checked (data.gov.in, DPIIT's own monthly PDF statistics reports, NSWS).
So the joint matrix here is built from the twin's OWN state-tagged data, not
from IEM -- IEM's marginals are cited alongside as independent reference
context, not blended into the computation.

Two joint state x sector signals, genuinely different in character:
  1. REVEALED (layer 42): 76 real, dated, individually-verified company
     investment/JV/plant events, each naming a real Indian state or city.
     This is "where sectors are actually landing," company-decision level.
  2. POLICY-ELIGIBLE (layer 16 leads' state_landings field): 321 companies x
     sector, each tagged with the states whose scheme stack (PLI top-ups,
     land, capital subsidy, etc.) makes them a policy-eligible landing zone
     for that company's sector. This is "where sectors are structurally
     pulled," policy-design level -- a state appearing here for many
     companies in a sector doesn't mean any of them chose it yet.

Usage: python3 scripts/build_layer43_state_sector_convergence.py
Output: layers/43_state_sector_convergence.json + docs/STATE_SECTOR_CONVERGENCE.md
"""
import datetime as dt
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "layers", "43_state_sector_convergence.json")
OUT_DOC = os.path.join(ROOT, "docs", "STATE_SECTOR_CONVERGENCE.md")

# -- canonical India state/UT names -----------------------------------------
STATE_MAP = {
    "AP": "Andhra Pradesh", "ANDHRA PRADESH": "Andhra Pradesh",
    "ASSAM": "Assam",
    "BIHAR": "Bihar",
    "CHHATTISGARH": "Chhattisgarh",
    "GOA": "Goa",
    "GUJARAT": "Gujarat",
    "HARYANA": "Haryana",
    "HP": "Himachal Pradesh", "HIMACHAL": "Himachal Pradesh", "HIMACHAL PRADESH": "Himachal Pradesh",
    "JHARKHAND": "Jharkhand",
    "KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "MP": "Madhya Pradesh", "MADHYA PRADESH": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra",
    "ODISHA": "Odisha", "ORISSA": "Odisha",
    "PUNJAB": "Punjab",
    "RAJASTHAN": "Rajasthan",
    "SIKKIM": "Sikkim",
    "TN": "Tamil Nadu", "TAMIL NADU": "Tamil Nadu",
    "TELANGANA": "Telangana",
    "UP": "Uttar Pradesh", "UTTAR PRADESH": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "WEST BENGAL": "West Bengal", "WB": "West Bengal",
    "DELHI": "Delhi", "NEW DELHI": "Delhi", "NCT": "Delhi",
}

# city -> state, for signals that name a location but not the state (checked
# against real, distinct cities used across layer 42's actual signal text)
CITY_TO_STATE = {
    "HYDERABAD": "Telangana", "BANGALORE": "Karnataka", "BENGALURU": "Karnataka",
    "CHENNAI": "Tamil Nadu", "PUNE": "Maharashtra", "CHAKAN": "Maharashtra",
    "GURGAON": "Haryana", "GURUGRAM": "Haryana", "MUMBAI": "Maharashtra",
    "NOIDA": "Uttar Pradesh", "GREATER NOIDA": "Uttar Pradesh",
    "KOCHI": "Kerala", "COCHIN": "Kerala", "AHMEDABAD": "Gujarat",
    "KOLKATA": "West Bengal", "JAIPUR": "Rajasthan", "NAGPUR": "Maharashtra",
    "COIMBATORE": "Tamil Nadu", "VISAKHAPATNAM": "Andhra Pradesh", "VIZAG": "Andhra Pradesh",
    "BHUBANESWAR": "Odisha", "RANCHI": "Jharkhand", "PATNA": "Bihar",
    "LUCKNOW": "Uttar Pradesh", "INDORE": "Madhya Pradesh", "BHOPAL": "Madhya Pradesh",
    "CHANDIGARH": "Chandigarh", "GUWAHATI": "Assam", "PANAJI": "Goa",
    "THIRUVANANTHAPURAM": "Kerala", "VADODARA": "Gujarat", "BARODA": "Gujarat",
    "SURAT": "Gujarat", "RAJKOT": "Gujarat", "NASHIK": "Maharashtra",
    "AURANGABAD": "Maharashtra", "LUDHIANA": "Punjab", "AMRITSAR": "Punjab",
    "DEHRADUN": "Uttarakhand", "SHIMLA": "Himachal Pradesh", "RAIPUR": "Chhattisgarh",
    "VIJAYAWADA": "Andhra Pradesh", "MYSORE": "Karnataka", "MYSURU": "Karnataka",
    "MANGALORE": "Karnataka", "MANGALURU": "Karnataka", "HOSUR": "Tamil Nadu",
    "SRIPERUMBUDUR": "Tamil Nadu", "SRI CITY": "Andhra Pradesh", "NEEMRANA": "Rajasthan",
    "BIDKIN": "Maharashtra", "RATNAGIRI": "Maharashtra", "JHAJJAR": "Haryana",
    "ANANTAPUR": "Andhra Pradesh", "SANAND": "Gujarat", "JHAGADIA": "Gujarat",
    "PANAGARH": "West Bengal", "THURAVOOR": "Kerala", "AEROCITY": "Delhi",
    "THOOTHUKUDI": "Tamil Nadu", "PENUKONDA": "Andhra Pradesh", "MANGALURU": "Karnataka",
    "UNNAO": "Uttar Pradesh", "SILVASSA": "Dadra and Nagar Haveli and Daman and Diu",
}

STATE_NAME_RE = re.compile(
    r"\b(" + "|".join(sorted((re.escape(v) for v in set(STATE_MAP.values())), key=len, reverse=True)) + r")\b")
CITY_RE = re.compile(
    r"\b(" + "|".join(sorted((re.escape(k.title()) for k in CITY_TO_STATE), key=len, reverse=True)) + r")\b",
    re.IGNORECASE)


def states_in_text(text):
    found = set(STATE_NAME_RE.findall(text))
    for m in CITY_RE.finditer(text):
        found.add(CITY_TO_STATE[m.group(1).upper()])
    return sorted(found)


def parse_state_landing(token):
    head = re.split(r"\(", token, maxsplit=1)[0].strip()
    out = []
    for part in re.split(r"[/,]", head):
        words = part.strip().split()
        for n in range(min(3, len(words)), 0, -1):
            cand = " ".join(words[:n]).upper()
            if cand in STATE_MAP:
                out.append(STATE_MAP[cand])
                break
    return out


def load_revealed():
    """layer 42 findings -> (state, sector, company, confidence, date, new_to_twin)"""
    d = json.load(open(os.path.join(ROOT, "layers", "42_sector_investment_news_sweep.json")))
    rows = []
    for sector, r in d["sectors"].items():
        short_sector = re.sub(r"\s*\(.*?\)\s*$", "", sector).strip()
        for f in r["findings"]:
            states = states_in_text(f["signal"])
            for st in states:
                rows.append({"state": st, "sector": short_sector, "company": f["company"],
                            "confidence": f.get("confidence"), "date": f.get("date"),
                            "new_to_twin": f.get("new_to_twin"), "source_url": f.get("source_url")})
    return rows


def load_policy_eligible():
    """layer 16 leads' state_landings -> (state, sector, company)"""
    d = json.load(open(os.path.join(ROOT, "layers", "16_leads.json")))
    rows = []
    for l in d["leads"]:
        sector = l.get("sector")
        if not sector:
            continue
        for sl in l.get("state_landings", []):
            for st in parse_state_landing(sl):
                rows.append({"state": st, "sector": sector, "company": l["company"]})
    return rows


def load_iem_reference():
    out = {"state_totals": None, "industry_totals": None}
    p1 = os.path.join(ROOT, "data", "registers", "iem_state_totals.json")
    p2 = os.path.join(ROOT, "data", "registers", "iem_industry_totals.json")
    if os.path.exists(p1):
        d = json.load(open(p1))
        # this resource is a MONTHLY time series with no month field retained in
        # the extraction (144 rows for 37 state names, i.e. ~6 duplicate rows
        # per state) -- IEM counts/investment only grow cumulatively, so the
        # row with the highest investment per state IS the latest month's
        # figure. Also drop the "GRAND TOTAL" pseudo-row from the per-state list.
        latest = {}
        for r in d["rows"]:
            name = r["state"]
            if name == "GRAND TOTAL":
                continue
            if name not in latest or (r.get("investment") or 0) > (latest[name].get("investment") or 0):
                latest[name] = r
        d["rows"] = sorted(latest.values(), key=lambda r: -(r.get("investment") or 0))
        d["dedup_note"] = (f"Source resource is a monthly time series with no month field retained; "
                           f"deduped 144 raw rows to {len(d['rows'])} states by keeping each state's "
                           f"highest (= latest) cumulative investment figure.")
        out["state_totals"] = d
    if os.path.exists(p2):
        out["industry_totals"] = json.load(open(p2))
    return out


def main():
    revealed = load_revealed()
    policy = load_policy_eligible()
    iem = load_iem_reference()

    print(f"revealed (layer 42) state mentions: {len(revealed)}")
    print(f"policy-eligible (layer 16) state landings: {len(policy)}")
    print(f"IEM state-totals reference: {'loaded' if iem['state_totals'] else 'NOT FOUND'}")
    print(f"IEM industry-totals reference: {'loaded' if iem['industry_totals'] else 'NOT FOUND'}")

    # -- state convergence: distinct sectors touching each state ------------
    state_sectors_revealed = defaultdict(set)
    state_events_revealed = defaultdict(list)
    for r in revealed:
        state_sectors_revealed[r["state"]].add(r["sector"])
        state_events_revealed[r["state"]].append(r)

    state_sectors_policy = defaultdict(set)
    state_companies_policy = defaultdict(set)
    for r in policy:
        state_sectors_policy[r["state"]].add(r["sector"])
        state_companies_policy[r["state"]].add(r["company"])

    all_states = set(state_sectors_revealed) | set(state_sectors_policy)
    convergence = []
    for st in all_states:
        convergence.append({
            "state": st,
            "revealed_sector_count": len(state_sectors_revealed.get(st, ())),
            "revealed_sectors": sorted(state_sectors_revealed.get(st, ())),
            "revealed_event_count": len(state_events_revealed.get(st, ())),
            "policy_sector_count": len(state_sectors_policy.get(st, ())),
            "policy_sectors": sorted(state_sectors_policy.get(st, ())),
            "policy_company_count": len(state_companies_policy.get(st, ())),
        })
    convergence.sort(key=lambda x: (x["revealed_sector_count"], x["policy_sector_count"]), reverse=True)
    hubs = [c for c in convergence if c["revealed_sector_count"] >= 3 or c["policy_sector_count"] >= 5]

    # -- per-sector state ranking --------------------------------------------
    sectors = sorted({r["sector"] for r in revealed} | {r["sector"] for r in policy})
    sector_rankings = {}
    for sec in sectors:
        rev_states = defaultdict(int)
        for r in revealed:
            if r["sector"] == sec:
                rev_states[r["state"]] += 1
        pol_states = defaultdict(set)
        for r in policy:
            if r["sector"] == sec:
                pol_states[r["state"]].add(r["company"])
        sector_rankings[sec] = {
            "revealed_ranking": sorted(
                [{"state": s, "event_count": c} for s, c in rev_states.items()],
                key=lambda x: -x["event_count"]),
            "policy_ranking": sorted(
                [{"state": s, "company_count": len(c)} for s, c in pol_states.items()],
                key=lambda x: -x["company_count"]),
        }

    out = {
        "layer": 43, "name": "state_sector_convergence",
        "built": dt.date.today().isoformat(),
        "what": ("State x sector convergence reportage. DPIIT's public IEM data (checked "
                "2026-08-24) publishes only separate state-totals and industry-totals "
                "marginals -- never a joint matrix -- so the joint state x sector signal "
                "here is built from the twin's own data: REVEALED (layer 42, 76 real dated "
                "company investment events, state/city extracted from the signal text) and "
                "POLICY-ELIGIBLE (layer 16 leads' state_landings, 321 companies x sector, "
                "policy scheme stacks). IEM's state and industry totals are cited as "
                "independent reference context, not blended into the computation."),
        "methodology_note": ("revealed_sector_count/policy_sector_count are DIFFERENT "
                             "signals measuring different things -- revealed is real company "
                             "decisions (small N, high confidence), policy is scheme-design "
                             "eligibility (larger N, doesn't mean any company actually chose "
                             "that state yet). Never sum them; read side by side."),
        "iem_reference": iem,
        "state_convergence": convergence,
        "multi_sector_hubs": hubs,
        "sector_state_rankings": sector_rankings,
        "revealed_event_count": len(revealed),
        "policy_landing_count": len(policy),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    # -- doc ------------------------------------------------------------------
    L = ["# State x sector convergence — layer 43", "",
         f"*Generated {out['built']} by `scripts/build_layer43_state_sector_convergence.py`. "
         f"{len(revealed)} revealed investment-event state mentions (layer 42), "
         f"{len(policy)} policy-eligible state landings (layer 16, 321 companies). "
         "DPIIT's IEM data does not publish a joint state×sector matrix — see methodology note below.*", "",
         "## Methodology", "",
         "Two genuinely different signals, shown side by side, never summed:", "",
         "- **Revealed** — real, dated, individually-verified company investment/JV/plant events "
         "(layer 42), state/city extracted from the actual announcement text. Small N, high confidence "
         "— this is what companies have *actually done*. Caveat: a handful of MEDIUM-confidence "
         "findings describe a company still *evaluating between* multiple candidate states (e.g. LG "
         "Energy Solution's battery JV, reportedly weighing Tamil Nadu/Telangana/Andhra Pradesh) rather "
         "than a completed site decision — each candidate state is counted once, so these inflate event "
         "counts slightly versus a true one-state landing. Cross-check the `confidence` field per row "
         "in the JSON before treating any single event as a done deal.",
         "- **Policy-eligible** — which states' scheme stacks (PLI top-ups, land, capital subsidy) make "
         "a company's sector eligible to land there (layer 16 leads' `state_landings`, 321 companies). "
         "Larger N, but structural/eligibility only — a state appearing here doesn't mean any company "
         "has chosen it yet.", "",
         "DPIIT's own IEM data (data.gov.in, checked live 2026-08-24, current through Aug 2026) is cited "
         "below as independent reference — but DPIIT publishes only separate state-total and "
         "industry-total marginals, never a joint state×sector cross-tabulation, so it cannot itself "
         "answer \"which states are converging on which sectors\"; it corroborates scale/rank only.", ""]

    if iem["state_totals"]:
        rows = iem["state_totals"].get("rows", [])
        L += ["## DPIIT IEM — state totals (reference, national, cumulative)", "",
             f"*Source: {iem['state_totals'].get('source_url', 'data.gov.in')}, "
             f"as of {iem['state_totals'].get('as_of', '?')}.*", "",
             "| State | IEM count | Investment (₹ lakh) | Employment |", "|---|---|---|---|"]
        top = sorted(rows, key=lambda r: -_num(r.get("investment")))[:15]
        for r in top:
            L.append(f"| {r.get('state', '—')} | {r.get('number', '—')} | {r.get('investment', '—')} | {r.get('employment', '—')} |")
        L.append("")

    if iem["industry_totals"]:
        rows = iem["industry_totals"].get("rows", [])
        L += ["## DPIIT IEM — industry totals (reference, national, cumulative)", "",
             f"*Source: {iem['industry_totals'].get('source_url', 'data.gov.in')}, "
             f"as of {iem['industry_totals'].get('as_of', '?')}.*", "",
             "| Industry | IEM count | Investment (₹ lakh) | Employment |", "|---|---|---|---|"]
        top = sorted(rows, key=lambda r: -_num(r.get("investment")))[:15]
        for r in top:
            L.append(f"| {r.get('industry', '—')} | {r.get('number', '—')} | {r.get('investment', '—')} | {r.get('employment', '—')} |")
        L.append("")

    L += ["## Multi-sector hub states", "",
         "States where either signal shows real breadth — ≥3 distinct sectors (revealed) or "
         "≥5 distinct sectors (policy-eligible).", "",
         "| State | Revealed sectors | Revealed events | Policy sectors | Policy companies |",
         "|---|---|---|---|---|"]
    for c in hubs:
        L.append(f"| **{c['state']}** | {c['revealed_sector_count']} ({', '.join(c['revealed_sectors']) or '—'}) "
                 f"| {c['revealed_event_count']} | {c['policy_sector_count']} | {c['policy_company_count']} |")
    L.append("")

    L += ["## Full state convergence table", "",
         "| State | Revealed sectors | Revealed events | Policy sectors | Policy companies |",
         "|---|---|---|---|---|"]
    for c in convergence:
        L.append(f"| {c['state']} | {c['revealed_sector_count']} | {c['revealed_event_count']} | "
                 f"{c['policy_sector_count']} | {c['policy_company_count']} |")
    L.append("")

    L += ["## Per-sector state rankings", ""]
    for sec in sectors:
        r = sector_rankings[sec]
        L += [f"### {sec}", ""]
        if r["revealed_ranking"]:
            L += ["**Revealed (real events):** " + ", ".join(
                f"{x['state']} ({x['event_count']})" for x in r["revealed_ranking"])]
        else:
            L += ["**Revealed (real events):** *(none)*"]
        if r["policy_ranking"]:
            L += ["", "**Policy-eligible (companies):** " + ", ".join(
                f"{x['state']} ({x['company_count']})" for x in r["policy_ranking"][:10])]
        L.append("")

    with open(OUT_DOC, "w") as f:
        f.write("\n".join(L) + "\n")

    write_html(convergence, hubs, sector_rankings, sectors, iem, len(revealed), len(policy))

    print(f"\n{len(convergence)} states, {len(hubs)} multi-sector hubs -> {OUT_JSON} + {OUT_DOC}")


def _esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_html(convergence, hubs, sector_rankings, sectors, iem, revealed_n, policy_n):
    out_html = os.path.join(ROOT, "docs", "reportage_state_sector.html")
    today = dt.date.today().isoformat()
    max_rev = max((c["revealed_sector_count"] for c in convergence), default=1) or 1
    max_pol = max((c["policy_sector_count"] for c in convergence), default=1) or 1

    L = []
    L.append(f'<!doctype html><html lang="en"><head><meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    L.append(f'<title>Reportage — State × Sector Convergence ({today})</title>')
    L.append('<style>')
    L.append(':root { --bg:#fff; --fg:#1a1a1a; --mut:#666; --card:#f6f6f4; --acc:#0b5cad; --bd:#e2e2de; --hi:#1a8f4c; --hisoft:#e6f5ec; }')
    L.append('@media (prefers-color-scheme: dark) { :root { --bg:#14151a; --fg:#e8e8e8; --mut:#9a9a9a; --card:#1e2027; --acc:#6ab0f3; --bd:#2c2e36; --hi:#5fd08c; --hisoft:#132a1e; } }')
    L.append('body { margin:0; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); }')
    L.append('.wrap { max-width:980px; margin:0 auto; padding:32px 20px 60px; }')
    L.append('h1 { font-size:1.5em; margin:0 0 4px; }')
    L.append('.sub { color:var(--mut); font-size:.9em; margin-bottom:20px; max-width:760px; }')
    L.append('.stats { display:flex; gap:12px; flex-wrap:wrap; margin:18px 0 26px; }')
    L.append('.stat { background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 18px; }')
    L.append('.stat b { font-size:1.4em; display:block; }')
    L.append('.stat span { color:var(--mut); font-size:.82em; }')
    L.append('details { background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 16px; margin:10px 0; }')
    L.append('summary { cursor:pointer; font-weight:600; }')
    L.append('a { color:var(--acc); text-decoration:none; } a:hover { text-decoration:underline; }')
    L.append('h2 { font-size:1.15em; margin:34px 0 8px; }')
    L.append('h3 { font-size:1em; margin:18px 0 6px; }')
    L.append('table { width:100%; border-collapse:collapse; margin:10px 0; font-size:.92em; }')
    L.append('th, td { text-align:left; padding:6px 10px; border-bottom:1px solid var(--bd); }')
    L.append('th { color:var(--mut); font-weight:600; font-size:.82em; text-transform:uppercase; letter-spacing:.02em; }')
    L.append('td.n { font-variant-numeric:tabular-nums; text-align:right; }')
    L.append('.bar-wrap { display:flex; align-items:center; gap:8px; }')
    L.append('.bar { height:8px; border-radius:4px; background:var(--acc); }')
    L.append('.bar.pol { background:var(--mut); opacity:.5; }')
    L.append('.hub-row td:first-child { font-weight:700; color:var(--hi); }')
    L.append('.note { color:var(--mut); font-size:.82em; margin-top:34px; border-top:1px solid var(--bd); padding-top:12px; }')
    L.append('.pill { display:inline-block; background:var(--hisoft); color:var(--hi); border-radius:8px; padding:0 8px; font-size:.75em; margin-left:6px; }')
    L.append('</style></head><body><div class="wrap">')

    L.append('<h1>State × Sector Convergence</h1>')
    L.append('<p class="sub">Which Indian states are becoming multi-sector investment hubs, and within each '
             'sector, which states do companies actually prefer? Two signals shown side by side, never summed: '
             '<b>revealed</b> (real, dated company investment events) and <b>policy-eligible</b> (which states\' '
             'scheme stacks make a company\'s sector eligible to land there). DPIIT\'s own IEM data is cited as '
             'independent reference — it publishes only separate state and industry totals, never a joint matrix, '
             'so it corroborates scale/rank but cannot itself answer the convergence question.</p>')

    L.append('<div class="stats">')
    L.append(f'<div class="stat"><b>{len(convergence)}</b><span>states with any signal</span></div>')
    L.append(f'<div class="stat"><b>{len(hubs)}</b><span>multi-sector hubs</span></div>')
    L.append(f'<div class="stat"><b>{revealed_n}</b><span>revealed event mentions</span></div>')
    L.append(f'<div class="stat"><b>{policy_n}</b><span>policy-eligible landings</span></div>')
    L.append(f'<div class="stat"><b>{len(sectors)}</b><span>sectors covered</span></div>')
    L.append('</div>')

    L.append('<h2>Multi-sector hub states</h2>')
    L.append('<p class="sub">≥3 distinct sectors (revealed) or ≥5 distinct sectors (policy-eligible).</p>')
    L.append('<table><thead><tr><th>State</th><th>Revealed sectors</th><th class="n">Events</th>'
             '<th>Policy sectors</th><th class="n">Companies</th></tr></thead><tbody>')
    for c in hubs:
        L.append('<tr class="hub-row">'
                 f'<td>{_esc(c["state"])}</td>'
                 f'<td>{c["revealed_sector_count"]} — {_esc(", ".join(c["revealed_sectors"]))}</td>'
                 f'<td class="n">{c["revealed_event_count"]}</td>'
                 f'<td>{c["policy_sector_count"]}</td>'
                 f'<td class="n">{c["policy_company_count"]}</td></tr>')
    L.append('</tbody></table>')

    L.append('<h2>Full state convergence</h2>')
    L.append('<table><thead><tr><th>State</th><th>Revealed sectors</th><th class="n">Events</th>'
             '<th>Policy sectors</th><th class="n">Companies</th></tr></thead><tbody>')
    for c in convergence:
        rev_pct = round(100 * c["revealed_sector_count"] / max_rev)
        pol_pct = round(100 * c["policy_sector_count"] / max_pol)
        L.append('<tr>'
                 f'<td>{_esc(c["state"])}</td>'
                 f'<td><div class="bar-wrap"><div class="bar" style="width:{rev_pct}%"></div>{c["revealed_sector_count"]}</div></td>'
                 f'<td class="n">{c["revealed_event_count"]}</td>'
                 f'<td><div class="bar-wrap"><div class="bar pol" style="width:{pol_pct}%"></div>{c["policy_sector_count"]}</div></td>'
                 f'<td class="n">{c["policy_company_count"]}</td></tr>')
    L.append('</tbody></table>')

    if iem["state_totals"]:
        rows = sorted(iem["state_totals"]["rows"], key=lambda r: -_num(r.get("investment")))[:15]
        L.append('<h2>DPIIT IEM — state totals <span class="pill">reference</span></h2>')
        L.append(f'<p class="sub">Cumulative, national. Source: <a href="{_esc(iem["state_totals"].get("source_url"))}">'
                 f'data.gov.in</a>, as of {_esc(iem["state_totals"].get("as_of"))}. '
                 f'{_esc(iem["state_totals"].get("dedup_note", ""))}</p>')
        L.append('<table><thead><tr><th>State</th><th class="n">IEM count</th>'
                 '<th class="n">Investment (₹ lakh)</th><th class="n">Employment</th></tr></thead><tbody>')
        for r in rows:
            L.append(f'<tr><td>{_esc(r.get("state"))}</td><td class="n">{_esc(r.get("number"))}</td>'
                     f'<td class="n">{_esc(r.get("investment"))}</td><td class="n">{_esc(r.get("employment"))}</td></tr>')
        L.append('</tbody></table>')

    if iem["industry_totals"]:
        rows = sorted(iem["industry_totals"]["rows"], key=lambda r: -_num(r.get("investment")))[:15]
        L.append('<h2>DPIIT IEM — industry totals <span class="pill">reference</span></h2>')
        L.append(f'<p class="sub">Cumulative, national. Source: <a href="{_esc(iem["industry_totals"].get("source_url"))}">'
                 f'data.gov.in</a>, as of {_esc(iem["industry_totals"].get("as_of"))}.</p>')
        L.append('<table><thead><tr><th>Industry</th><th class="n">IEM count</th>'
                 '<th class="n">Investment (₹ lakh)</th><th class="n">Employment</th></tr></thead><tbody>')
        for r in rows:
            L.append(f'<tr><td>{_esc(r.get("industry"))}</td><td class="n">{_esc(r.get("number"))}</td>'
                     f'<td class="n">{_esc(r.get("investment"))}</td><td class="n">{_esc(r.get("employment"))}</td></tr>')
        L.append('</tbody></table>')

    L.append('<h2>Per-sector state rankings</h2>')
    for sec in sectors:
        r = sector_rankings[sec]
        rev_n = len(r["revealed_ranking"])
        L.append(f'<details><summary>{_esc(sec)} <span class="pill">{rev_n} revealed</span></summary>')
        if r["revealed_ranking"]:
            L.append('<h3>Revealed (real events)</h3><table><thead><tr><th>State</th><th class="n">Events</th></tr></thead><tbody>')
            for x in r["revealed_ranking"]:
                L.append(f'<tr><td>{_esc(x["state"])}</td><td class="n">{x["event_count"]}</td></tr>')
            L.append('</tbody></table>')
        else:
            L.append('<p class="sub">No revealed events yet.</p>')
        if r["policy_ranking"]:
            L.append('<h3>Policy-eligible (companies)</h3><table><thead><tr><th>State</th><th class="n">Companies</th></tr></thead><tbody>')
            for x in r["policy_ranking"][:10]:
                L.append(f'<tr><td>{_esc(x["state"])}</td><td class="n">{x["company_count"]}</td></tr>')
            L.append('</tbody></table>')
        L.append('</details>')

    L.append('<p class="note">Generated by <code>scripts/build_layer43_state_sector_convergence.py</code>. '
             'Revealed data: <code>layers/42_sector_investment_news_sweep.json</code>. Policy-eligible data: '
             '<code>layers/16_leads.json</code> (<code>state_landings</code> field). '
             'Full record: <code>layers/43_state_sector_convergence.json</code>, '
             '<a href="STATE_SECTOR_CONVERGENCE.md">STATE_SECTOR_CONVERGENCE.md</a>.</p>')

    L.append('</div></body></html>')
    with open(out_html, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"reportage html: {len(convergence)} states, {len(sectors)} sectors -> {out_html}")


def _num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
