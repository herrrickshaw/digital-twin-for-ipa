"""State news wire and the state / latest-updates HTML pages."""
import datetime, html as _h, os, re, sqlite3
from collections import defaultdict

from reportage.common import ROOT, STATE_DB, quarter_of
from reportage.schemes import GENERIC, scheme_hits

STATE_NAMES = {"MP": "Madhya Pradesh", "UP": "Uttar Pradesh", "GJ": "Gujarat",
               "MH": "Maharashtra", "KA": "Karnataka", "GA": "Goa", "RJ": "Rajasthan",
               "PB": "Punjab", "MZ": "Mizoram", "NL": "Nagaland", "SK": "Sikkim",
               "CH": "Chandigarh", "DD": "DNH & Daman-Diu", "KL": "Kerala",
               "TS": "Telangana", "AS": "Assam", "AP": "Andhra Pradesh"}
# state-side signal terms: industrial/investment policy language that the central
# scheme map won't catch but matters for an IPA watching state governments
STATE_SIGNAL = re.compile(
    r"invest|industrial|industry|incentive|subsid|policy|\bMoU\b|crore|manufactur|"
    r"semiconductor|solar|renewable|logistics|park\b|\bIT\b|startup|employment.{0,20}(package|scheme)|"
    r"global investors|summit", re.I)


def state_wire(days=30):
    """Recent state-government releases from the state_news register, scheme-mapped
    where the central keyword map hits, otherwise kept if they carry investment/
    industrial-policy signal language. Returns newest-first row dicts."""
    if not os.path.exists(STATE_DB):
        return []
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    scon = sqlite3.connect(STATE_DB)
    cols = [r[1] for r in scon.execute("pragma table_info(state_news)")]
    tcol = "coalesce(title_en, title)" if "title_en" in cols else "title"
    out = []
    for state, date, title, category, url in scon.execute(
            f"select state, date, {tcol}, category, url from state_news where date >= ? order by date desc", (cutoff,)):
        hits = scheme_hits(title)
        if not hits and not STATE_SIGNAL.search(title or ""):
            continue
        out.append({"state": STATE_NAMES.get(state, state), "date": date, "title": title,
                    "category": category or "", "url": url or "", "schemes": hits[:2]})
    scon.close()
    return out


# quarterly state-view buckets (classified on the English title)
STATE_BUCKETS = [
    ("investment", "Investment & MoUs",
     re.compile(r"invest|\bMoU\b|memorandum of understanding|crore.{0,50}(invest|project|industr|plant|unit)|"
                r"(plant|factory|unit|facility|data cent|semiconductor|gigafactory).{0,40}(set up|established|approved|"
                r"proposed|coming|to come)|industrial park|investors summit|global investors|incentive|subsid|"
                r"employment package|capital expenditure", re.I)),
    ("projects", "New projects & inaugurations",
     re.compile(r"inaugurat|foundation stone|bhoomi ?pujan|bhumi ?pujan|lokarpan|dedicat.{0,20}(nation|state|public)|"
                r"commission(ed|ing)|flag(ged)? off|launch(ed|es)?\b.{0,40}(project|scheme|plant|corridor|park|"
                r"expressway|metro|airport|port)|groundbreaking", re.I)),
    ("regulation", "Policy & regulation",
     re.compile(r"policy|\bact\b|\bbill\b|ordinance|amendment|regulation|\brules\b|notification|"
                r"cabinet.{0,30}(approv|decid|clear)|मंत्रि|single window|ease of doing|\bGR\b|"
                r"guidelines|framework|exemption|stamp duty|land allot", re.I)),
]


def classify_state_row(title):
    for key, label, rx in STATE_BUCKETS:
        if rx.search(title or ""):
            return key
    return None


def _states_by_quarter():
    """Classify the state_news register into quarter -> bucket -> rows."""
    scon = sqlite3.connect(STATE_DB)
    cols = [r[1] for r in scon.execute("pragma table_info(state_news)")]
    tcol = "coalesce(title_en, title)" if "title_en" in cols else "title"
    n_total = scon.execute("select count(*) from state_news").fetchone()[0]
    by_q = defaultdict(lambda: defaultdict(list))
    counted = 0
    for state, date, title, url in scon.execute(
            f"select state, date, {tcol}, url from state_news where date >= '2017-01-01' order by date desc"):
        hits = scheme_hits(title)
        bucket = classify_state_row(title)
        if not bucket and not hits:
            continue
        counted += 1
        by_q[quarter_of(date)][bucket or "investment"].append(
            (date, STATE_NAMES.get(state, state), title, url, hits[:2]))
    scon.close()
    return n_total, by_q, counted


def _states_quarter_sections(by_q):
    """HTML sections, one per quarter, with a details block per bucket."""
    parts = []
    for q in sorted(by_q, reverse=True):
        buckets = by_q[q]
        nq = sum(len(v) for v in buckets.values())
        parts.append(f'<section><h2>{q} <span class="cnt">{nq}</span></h2>')
        for key, label, _rx in STATE_BUCKETS:
            items = buckets.get(key, [])
            if not items:
                continue
            body = []
            for date, st, title, url, hits in items:
                chips = "".join(f'<span class="chip">{_h.escape(s)}</span>' for s in hits)
                link = (f'<a href="{url}" target="_blank" rel="noopener">{_h.escape(title[:170])}</a>'
                        if (url or "").startswith("http") else _h.escape(title[:170]))
                body.append(f'<li data-st="{_h.escape(st, quote=True)}"><span class="d">{date}</span> '
                            f'<span class="m">{_h.escape(st)}</span>{chips}<br>{link}</li>')
            parts.append(f'<details {"open" if key != "projects" and len(items) <= 40 else ""}>'
                         f'<summary><b>{label}</b> <span class="cnt">{len(items)}</span></summary>'
                         f'<ul>{"".join(body)}</ul></details>')
        parts.append("</section>")
    return parts


def _states_filter_bar():
    """State filter buttons."""
    all_states = sorted({STATE_NAMES.get(s, s) for (s,) in
                         sqlite3.connect(STATE_DB).execute("select distinct state from state_news")})
    filter_bar = ('<div class="fbar"><button class="fbtn active" data-f="">All states</button>'
                  + "".join(f'<button class="fbtn" data-f="{_h.escape(s, quote=True)}">{_h.escape(s)}</button>'
                            for s in all_states) + "</div>")
    return filter_bar


def _states_filter_js():
    """Client-side state filter script."""
    filter_js = """<script>
document.querySelectorAll('.fbtn').forEach(function(b){b.addEventListener('click',function(){
  document.querySelectorAll('.fbtn').forEach(function(x){x.classList.remove('active')});
  b.classList.add('active');var f=b.getAttribute('data-f');
  document.querySelectorAll('li[data-st]').forEach(function(li){
    li.style.display=(!f||li.getAttribute('data-st')===f)?'':'none';});
  document.querySelectorAll('details').forEach(function(d){
    var vis=d.querySelectorAll('li[data-st]').length===0?null:
      Array.prototype.some.call(d.querySelectorAll('li[data-st]'),function(li){return li.style.display!=='none'});
    if(vis!==null){d.style.display=vis?'':'none';if(f&&vis)d.open=true;}});
  document.querySelectorAll('section').forEach(function(s){
    var ds=s.querySelectorAll('details');if(!ds.length)return;
    s.style.display=Array.prototype.some.call(ds,function(d){return d.style.display!=='none'})?'':'none';});
});});
</script>"""
    return filter_js


def _states_page(n_total, filter_bar, parts, filter_js):
    """The full state reportage HTML page."""
    today = datetime.date.today().isoformat()
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>State Reportage — quarterly investment, projects &amp; regulation</title>
<style>
:root {{ --bg:#fff; --fg:#1a1a1a; --mut:#666; --card:#f6f6f4; --acc:#0b5cad; --bd:#e2e2de; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14151a; --fg:#e8e8e8; --mut:#9a9a9a; --card:#1e2027; --acc:#6ab0f3; --bd:#2c2e36; }} }}
body {{ margin:0; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); }}
.wrap {{ max-width:880px; margin:0 auto; padding:32px 20px 60px; }}
h1 {{ font-size:1.5em; margin:0 0 4px; }}
h2 {{ font-size:1.15em; margin:30px 0 8px; }}
.sub {{ color:var(--mut); font-size:.9em; margin-bottom:20px; }}
details {{ background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 16px; margin:10px 0; }}
summary {{ cursor:pointer; }}
.cnt {{ background:var(--acc); color:#fff; border-radius:10px; padding:1px 9px; font-size:.78em; margin-left:6px; }}
.chip {{ background:var(--acc); color:#fff; border-radius:8px; padding:0 8px; font-size:.72em; margin-left:6px; }}
ul {{ list-style:none; padding:6px 0 2px; margin:0; }}
li {{ padding:7px 0; border-top:1px solid var(--bd); }}
.d {{ font-variant-numeric:tabular-nums; color:var(--mut); font-size:.85em; margin-right:8px; }}
.m {{ color:var(--mut); font-size:.85em; }}
a {{ color:var(--acc); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
.note {{ color:var(--mut); font-size:.82em; margin-top:34px; border-top:1px solid var(--bd); padding-top:12px; }}
.fbar {{ display:flex; gap:8px; flex-wrap:wrap; margin:14px 0 6px; position:sticky; top:0; background:var(--bg); padding:10px 0; z-index:5; }}
.fbtn {{ background:var(--card); color:var(--fg); border:1px solid var(--bd); border-radius:16px; padding:4px 14px; font-size:.85em; cursor:pointer; }}
.fbtn.active {{ background:var(--acc); color:#fff; border-color:var(--acc); }}
</style></head><body><div class="wrap">
<h1>State Reportage — investment, projects &amp; regulation by quarter</h1>
<div class="sub">State-government wire ({n_total:,} releases in the register) filtered to investment/MoU news,
new-project events and key state regulations; classified on machine-translated titles. Archive depth is
source-limited: Maharashtra from 2019Q3, Madhya Pradesh from 2020Q2; UP/Gujarat/Karnataka latest-only.
Built {today} by scripts/build_reportage.py.</div>
{filter_bar}
{"".join(parts)}
<div class="note">Register: data/registers/state_news.sqlite (collect_state_news.py daily +
backfill_state_news.py archives). Classification and scheme chips are keyword-based on machine
translations — an index into the wire, not a substitute for reading the release.</div>
</div>{filter_js}</body></html>"""
    return page


def write_html_states():
    """Emit docs/reportage_states.html -- quarterly state-wire view matching the
    PIB reportage cadence: investment/MoUs, new projects, key state regulations.
    Reads the whole state_news register (backfilled by backfill_state_news.py);
    rows classify on the machine-translated English title."""
    if not os.path.exists(STATE_DB):
        print("state register missing -- skipping states html")
        return
    n_total, by_q, counted = _states_by_quarter()
    parts = _states_quarter_sections(by_q)
    filter_bar = _states_filter_bar()
    filter_js = _states_filter_js()
    page = _states_page(n_total, filter_bar, parts, filter_js)
    path = os.path.join(ROOT, "docs/reportage_states.html")
    open(path, "w").write(page)
    print(f"reportage states html: {counted} classified rows across {len(by_q)} quarters -> {path}")


def _latest_rows(rows, days):
    """Recent central rows (scheme-mapped / unmapped Cabinet), grouped by scheme, plus the state wire."""
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    recent, cab_only = [], []
    for prid, date, ministry, title in rows:
        if (date or "") < cutoff:
            continue
        hits = scheme_hits(title)
        ministry = ministry or "(unattributed)"
        if hits:
            recent.append((date, prid, ministry, title, hits[:2]))
        elif ministry.startswith("Cabinet") and GENERIC.search(title or ""):
            cab_only.append((date, prid, ministry, title))
    recent.sort(reverse=True)
    cab_only.sort(reverse=True)
    by_scheme = defaultdict(list)
    for r in recent:
        for s in r[4]:
            by_scheme[s].append(r)
    states = state_wire(days)
    return cutoff, recent, cab_only, by_scheme, states


def _latest_central_html(by_scheme, cab_only):
    """HTML for the per-scheme sections and the unmapped Cabinet list."""
    def li(date, ministry, title, url, label):
        return (f'<li><span class="d">{date}</span> <span class="m">{_h.escape(ministry)}</span><br>'
                f'<a href="{url}" target="_blank" rel="noopener">{_h.escape((title or "")[:160])}</a></li>')

    sections = []
    for s, items in sorted(by_scheme.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        seen, uniq = set(), []
        for it in items:
            if it[1] not in seen:
                seen.add(it[1]); uniq.append(it)
        body = "".join(li(d, m, t, f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={p}", s)
                       for d, p, m, t, _hits in uniq)
        sections.append(f'<details {"open" if len(uniq) >= 4 else ""}><summary><b>{_h.escape(s)}</b> '
                        f'<span class="cnt">{len(uniq)}</span></summary><ul>{body}</ul></details>')
    cab_html = "".join(li(d, m, t, f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={p}", "")
                       for d, p, m, t in cab_only)
    return sections, cab_html


def _latest_state_items(states):
    """HTML list items for the state wire."""
    st_parts = []
    for r in states:
        chip = "".join(f'<span class="chip">{_h.escape(s)}</span>' for s in r["schemes"])
        link = (f'<a href="{r["url"]}" target="_blank" rel="noopener">{_h.escape(r["title"][:160])}</a>'
                if r["url"].startswith("http") else _h.escape(r["title"][:160]))
        st_parts.append(f'<li data-st="{_h.escape(r["state"], quote=True)}"><span class="d">{r["date"]}</span> '
                        f'<span class="m">{_h.escape(r["state"])}'
                        f'{" · " + _h.escape(r["category"]) if r["category"] else ""}</span> {chip}<br>{link}</li>')
    return st_parts


def _latest_page(register_total, cutoff, recent, cab_only, by_scheme, states, sections, cab_html, st_parts):
    """The full latest-updates HTML page."""
    n_states = len({r["state"] for r in states})
    dmin = min((r[0] for r in recent), default=cutoff)
    dmax = max((r[0] for r in recent), default=cutoff)
    today = datetime.date.today().isoformat()
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reportage — Latest Updates ({dmin} → {dmax})</title>
<style>
:root {{ --bg:#fff; --fg:#1a1a1a; --mut:#666; --card:#f6f6f4; --acc:#0b5cad; --bd:#e2e2de; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14151a; --fg:#e8e8e8; --mut:#9a9a9a; --card:#1e2027; --acc:#6ab0f3; --bd:#2c2e36; }} }}
body {{ margin:0; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--fg); }}
.wrap {{ max-width:880px; margin:0 auto; padding:32px 20px 60px; }}
h1 {{ font-size:1.5em; margin:0 0 4px; }}
.sub {{ color:var(--mut); font-size:.9em; margin-bottom:20px; }}
.stats {{ display:flex; gap:12px; flex-wrap:wrap; margin:18px 0 26px; }}
.stat {{ background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 18px; }}
.stat b {{ font-size:1.4em; display:block; }}
.stat span {{ color:var(--mut); font-size:.82em; }}
details {{ background:var(--card); border:1px solid var(--bd); border-radius:10px; padding:10px 16px; margin:10px 0; }}
summary {{ cursor:pointer; }}
.cnt {{ background:var(--acc); color:#fff; border-radius:10px; padding:1px 9px; font-size:.78em; margin-left:6px; }}
.chip {{ background:var(--acc); color:#fff; border-radius:8px; padding:0 8px; font-size:.72em; margin-left:6px; }}
ul {{ list-style:none; padding:6px 0 2px; margin:0; }}
li {{ padding:7px 0; border-top:1px solid var(--bd); }}
.d {{ font-variant-numeric:tabular-nums; color:var(--mut); font-size:.85em; margin-right:8px; }}
.m {{ color:var(--mut); font-size:.85em; }}
a {{ color:var(--acc); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
h2 {{ font-size:1.1em; margin:30px 0 8px; }}
.note {{ color:var(--mut); font-size:.82em; margin-top:34px; border-top:1px solid var(--bd); padding-top:12px; }}
.fbar {{ display:flex; gap:8px; flex-wrap:wrap; margin:14px 0 6px; }}
.fbtn {{ background:var(--card); color:var(--fg); border:1px solid var(--bd); border-radius:16px; padding:4px 14px; font-size:.85em; cursor:pointer; }}
.fbtn.active {{ background:var(--acc); color:#fff; border-color:var(--acc); }}
</style></head><body><div class="wrap">
<h1>Reportage — Latest Updates</h1>
<div class="sub">Key announcements {dmin} → {dmax}: central PIB register ({register_total:,} releases, refreshed daily)
+ state wire (mpinfo.org &amp;c. via <code>collect_state_news.py</code>). Built {today}.</div>
<div class="stats">
<div class="stat"><b>{len({r[1] for r in recent})}</b><span>central announcements</span></div>
<div class="stat"><b>{len(by_scheme)}</b><span>schemes touched</span></div>
<div class="stat"><b>{len(states)}</b><span>state-wire items ({n_states} state{"s" if n_states != 1 else ""})</span></div>
<div class="stat"><b>{len(cab_only)}</b><span>unmapped Cabinet/CCEA</span></div>
</div>
<h2>Central — by scheme</h2>
{"".join(sections)}
<h2>Cabinet / CCEA — not matched to a scheme keyword</h2>
<details><summary><b>Cabinet approvals &amp; decisions</b> <span class="cnt">{len(cab_only)}</span></summary><ul>{cab_html}</ul></details>
<h2>State wire</h2>
<div class="fbar"><button class="fbtn active" data-f="">All states</button>{"".join(
    f'<button class="fbtn" data-f="{_h.escape(s, quote=True)}">{_h.escape(s)}</button>'
    for s in sorted({r["state"] for r in states}))}</div>
<details open><summary><b>State government releases with scheme / investment-policy signal</b> <span class="cnt">{len(st_parts)}</span></summary><ul>{"".join(st_parts)}</ul></details>
<div class="note">Generated by scripts/build_reportage.py (write_html_latest). Keyword mapping is an index into the
registers, not a substitute for reading the release — every central row links its PRID on pib.gov.in; state rows
deep-link the source site. State wire register: data/registers/state_news.sqlite, refreshed by
scripts/collect_state_news.py.</div>
</div><script>
document.querySelectorAll('.fbtn').forEach(function(b){{b.addEventListener('click',function(){{
  document.querySelectorAll('.fbtn').forEach(function(x){{x.classList.remove('active')}});
  b.classList.add('active');var f=b.getAttribute('data-f');
  document.querySelectorAll('li[data-st]').forEach(function(li){{
    li.style.display=(!f||li.getAttribute('data-st')===f)?'':'none';}});
}});}});
</script></body></html>"""
    return page


def write_html_latest(rows, register_total=0, days=30):
    """Emit docs/reportage_latest.html -- self-contained latest-updates page:
    central PIB scheme-mapped + Cabinet items from the last `days` days, grouped
    by scheme, plus the state wire (collect_state_news.py register)."""
    cutoff, recent, cab_only, by_scheme, states = _latest_rows(rows, days)

    sections, cab_html = _latest_central_html(by_scheme, cab_only)
    st_parts = _latest_state_items(states)
    page = _latest_page(register_total, cutoff, recent, cab_only, by_scheme, states, sections, cab_html, st_parts)
    path = os.path.join(ROOT, "docs/reportage_latest.html")
    open(path, "w").write(page)
    print(f"reportage latest html: {len(recent)} central rows, {len(states)} state-wire rows ({days}d window) -> {path}")
