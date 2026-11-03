"""Quarterly and ministry reportage HTML pages."""
import datetime, html as _h, os
from collections import defaultdict

from reportage.annex import render_policy_annex, render_states, state_announcements
from reportage.common import ROOT, quarter_of

def write_html(by_q, total):
    """Emit docs/reportage.html -- house-style page; list pre-rendered (works without JS), filters via JS."""
    st_by_q = {}
    for r in state_announcements():
        st_by_q.setdefault(quarter_of(r["date"]), []).append(r)
    parts = []
    all_qs = sorted(set(list(by_q.keys()) + list(st_by_q.keys())), reverse=True)
    for q in all_qs:
        rows = by_q[q]["mapped"] if q in by_q else []
        strows = sorted(st_by_q.get(q, []), key=lambda r: r["date"])
        if not rows and not strows:
            continue
        n = len(rows) + len(strows)
        parts.append(f'<section class="q" data-q="{q}"><h2>{q} <span class="n">&middot; {n} announcement{"s" if n>1 else ""} ({len(strows)} state)</span></h2>')
        for date, prid, ministry, title, hits in rows:
            scheme = "; ".join(s for s, _ in hits)
            chips = "".join(f'<span class="chip">{_h.escape(s)}</span>' for s, _ in hits)
            parts.append(
                f'<div class="row" data-q="{q}" data-s="{_h.escape(scheme, quote=True)}" data-m="{_h.escape(ministry, quote=True)}" data-st="Central">'
                f'<div class="top"><span class="date">{date}</span>{chips}<span class="min">{_h.escape(ministry)}</span></div>'
                f'<div class="title"><a href="https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}" target="_blank" rel="noopener">'
                f'{_h.escape((title or "")[:160])}</a> <span class="prid">PRID {prid}</span></div></div>')
        for r in strows:
            link = (f'<a href="{r["url"]}" target="_blank" rel="noopener">' if r.get("url","").startswith("http") else "<span>")
            close = "</a>" if r.get("url","").startswith("http") else "</span>"
            parts.append(
                f'<div class="row" style="border-left-color:var(--warn);" data-q="{q}" '
                f'data-s="{_h.escape(r["scheme"][:60], quote=True)}" data-m="{_h.escape(r["state"], quote=True)}" data-st="{_h.escape(r["state"], quote=True)}">'
                f'<div class="top"><span class="date">{r["date"]}</span>'
                f'<span class="chip" style="background:#8a5a1222;color:var(--warn);">STATE · {_h.escape(r["state"])}</span>'
                f'<span class="min">{_h.escape(r["scheme"][:80])}</span></div>'
                f'<div class="title" style="font-size:.9rem;">{link}{_h.escape(r["detail"])}{close}</div></div>')
        parts.append("</section>")
    tpl = open(os.path.join(ROOT, "docs/_reportage_template.html")).read()
    html_out = tpl.replace("__ROWS__", "\n".join(parts)).replace("__STATES__", render_states()).replace("__TOTAL__", str(total)).replace(
        "__NQ__", str(len(by_q))).replace("__GEN__", datetime.date.today().isoformat()).replace("__POLICY__", render_policy_annex())
    path = os.path.join(ROOT, "docs/reportage.html")
    open(path, "w").write(html_out)
    print(f"reportage html: {sum(len(v['mapped']) for v in by_q.values())} rows pre-rendered -> {path}")


def write_html_ministry(by_q, total):
    """Emit docs/reportage_ministry.html -- MINISTRY-WISE companion view (owning ministry
    per the twin's scheme map; Cabinet/CCEA rows file under their line ministry), rows
    time-stamped with the release date, newest first. Pre-rendered (works without JS),
    filters (quarter/scheme/ministry/state/search) via JS. Does NOT replace the
    quarter-wise docs/reportage.html -- both are built every run."""
    # flatten central rows, keyed by the scheme's owning ministry from the twin map
    by_min = defaultdict(list)
    for q, d in by_q.items():
        for date, prid, ministry, title, hits in d["mapped"]:
            owner = hits[0][1] if hits else "various"
            by_min[owner].append((date, q, prid, ministry, title, hits))
    parts = []
    for owner in sorted(by_min, key=lambda k: (-len(by_min[k]), k)):
        rows = sorted(by_min[owner], reverse=True)  # newest first
        latest = rows[0][0]
        parts.append(f'<section class="q" data-min="{_h.escape(owner, quote=True)}">'
                     f'<h2>{_h.escape(owner)} <span class="n">&middot; {len(rows)} announcement{"s" if len(rows)>1 else ""}'
                     f' &middot; latest {latest}</span></h2>')
        for date, q, prid, ministry, title, hits in rows:
            scheme = "; ".join(s for s, _ in hits)
            chips = "".join(f'<span class="chip">{_h.escape(s)}</span>' for s, _ in hits)
            parts.append(
                f'<div class="row" data-q="{q}" data-s="{_h.escape(scheme, quote=True)}" data-m="{_h.escape(owner, quote=True)}" data-st="Central">'
                f'<div class="top"><span class="date">{date}</span>{chips}<span class="min">register: {_h.escape(ministry)}</span></div>'
                f'<div class="title"><a href="https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}" target="_blank" rel="noopener">'
                f'{_h.escape((title or "")[:160])}</a> <span class="prid">PRID {prid}</span></div></div>')
        parts.append("</section>")
    # dated state-scheme events: one section, grouped visually by state chips, newest first
    strows = sorted(state_announcements(), key=lambda r: r["date"], reverse=True)
    if strows:
        parts.append(f'<section class="q" data-min="State governments"><h2>State governments '
                     f'<span class="n">&middot; {len(strows)} dated scheme events &middot; latest {strows[0]["date"]}</span></h2>')
        for r in strows:
            link = (f'<a href="{r["url"]}" target="_blank" rel="noopener">' if r.get("url","").startswith("http") else "<span>")
            close = "</a>" if r.get("url","").startswith("http") else "</span>"
            parts.append(
                f'<div class="row" style="border-left-color:var(--warn);" data-q="{quarter_of(r["date"])}" '
                f'data-s="{_h.escape(r["scheme"][:60], quote=True)}" data-m="State governments" data-st="{_h.escape(r["state"], quote=True)}">'
                f'<div class="top"><span class="date">{r["date"]}</span>'
                f'<span class="chip" style="background:#8a5a1222;color:var(--warn);">STATE · {_h.escape(r["state"])}</span>'
                f'<span class="min">{_h.escape(r["scheme"][:80])}</span></div>'
                f'<div class="title" style="font-size:.9rem;">{link}{_h.escape(r["detail"])}{close}</div></div>')
        parts.append("</section>")
    tpl = open(os.path.join(ROOT, "docs/_reportage_ministry_template.html")).read()
    html_out = tpl.replace("__ROWS__", "\n".join(parts)).replace("__STATES__", render_states()).replace("__TOTAL__", str(total)).replace(
        "__NQ__", str(len(by_min))).replace("__GEN__", datetime.date.today().isoformat()).replace("__POLICY__", render_policy_annex())
    path = os.path.join(ROOT, "docs/reportage_ministry.html")
    open(path, "w").write(html_out)
    print(f"reportage ministry html: {sum(len(v) for v in by_min.values())} central rows + {len(strows)} state rows "
          f"across {len(by_min)} ministries -> {path}")
