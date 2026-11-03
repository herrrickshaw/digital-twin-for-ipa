#!/usr/bin/env python3
"""Quarterly reportage: key announcements from the PIB register mapped to scheme + ministry.

Source: the policy repo's PIB SQL register (122k+ releases, 2017 -> today, refreshed
daily by the cron 'pib' job). "Key" = Cabinet/CCEA approvals plus line-ministry
releases whose titles hit the twin's scheme-keyword map. Every line carries its PRID
(clickable), ministry, and the scheme(s) it maps to.

Output: docs/REPORTAGE.md (generated view -- never hand-edit). Per quarter:
scheme-mapped announcements first, then unmapped Cabinet approvals, with an honest
"not shown" count when a quarter is capped.

Rerun after every PIB refresh worth reporting:  python3 scripts/build_reportage.py
"""
import datetime, os, sqlite3
from collections import defaultdict

# The implementation lives in scripts/reportage/ (schemes, wire_pages, pages, annex, common); the names
# below are re-exported so `from build_reportage import scheme_hits` and the CLI keep working.
from reportage.annex import render_policy_annex, render_states, render_up_ethanol, state_announcements  # noqa: F401
from reportage.common import CAP_PER_QUARTER, DB, ROOT, STATE_DB, quarter_of  # noqa: F401
from reportage.pages import write_html, write_html_ministry
from reportage.schemes import COMP, EXC, GENERIC, PLI_SECTORS, SCHEMES, refine_pli, scheme_hits  # noqa: F401
from reportage.wire_pages import (STATE_BUCKETS, STATE_NAMES, STATE_SIGNAL, classify_state_row, state_wire,  # noqa: F401
                                  write_html_latest, write_html_states)


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, date, ministry, title FROM pib_items ORDER BY date").fetchall()
    by_q = defaultdict(lambda: {"mapped": [], "cabinet_other": [], "dropped": 0})
    for prid, date, ministry, title in rows:
        hits = scheme_hits(title, with_ministry=True)
        ministry = ministry or "(unattributed)"
        is_cab = ministry.startswith("Cabinet")
        q = quarter_of(date)
        if hits:
            hits = [(refine_pli(s, title), m) for s, m in hits]
            by_q[q]["mapped"].append((date, prid, ministry, title, hits[:2]))
        elif is_cab and GENERIC.search(title or ""):
            by_q[q]["cabinet_other"].append((date, prid, ministry, title))

    lines = ["# Quarterly Reportage — key announcements × scheme × ministry", "",
             f"*Generated {datetime.date.today().isoformat()} by `scripts/build_reportage.py` from the PIB register "
             "(122k+ releases, refreshed daily). Every row links its PRID. Scheme mapping is keyword-based — "
             "treat as an index into the register, not a substitute for reading the release.*", ""]
    total = 0
    for q in sorted(by_q, reverse=True):
        d = by_q[q]
        n = len(d["mapped"])
        total += n
        lines += [f"## {q} — {n} scheme-mapped announcements", "",
                  "| Date | Scheme | Ministry (register) | Announcement | PRID |", "|---|---|---|---|---|"]
        shown = 0
        for date, prid, ministry, title, hits in d["mapped"]:
            if shown >= CAP_PER_QUARTER:
                break
            scheme = "; ".join(s for s, _ in hits)
            url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"
            lines.append(f"| {date} | **{scheme}** | {ministry} | {(title or '')[:120].replace('|','/')} | [{prid}]({url}) |")
            shown += 1
        if n > CAP_PER_QUARTER:
            lines.append(f"| … | | | *{n - CAP_PER_QUARTER} further scheme-mapped rows not shown (cap {CAP_PER_QUARTER}) — query the register* | |")
        oth = d["cabinet_other"]
        if oth:
            lines += ["", f"<details><summary>Other Cabinet/CCEA approvals this quarter ({len(oth)})</summary>", ""]
            for date, prid, ministry, title in oth[:15]:
                url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"
                lines.append(f"- {date} · {(title or '')[:130]} · [{prid}]({url})")
            if len(oth) > 15:
                lines.append(f"- … {len(oth) - 15} more")
            lines += ["", "</details>"]
        lines.append("")
    out = os.path.join(ROOT, "docs/REPORTAGE.md")
    open(out, "w").write("\n".join(lines))
    print(f"reportage: {total} scheme-mapped announcements across {len(by_q)} quarters -> {out}")
    write_html(by_q, total)
    write_html_ministry(by_q, total)
    write_html_latest(rows, register_total=len(rows))
    write_html_states()


if __name__ == "__main__":
    main()
