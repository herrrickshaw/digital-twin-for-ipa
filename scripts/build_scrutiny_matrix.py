#!/usr/bin/env python3
"""Scheme scrutiny matrix: cross-reference the PIB announcement register with the
Lok Sabha question registry, per scheme, to show which schemes Parliament actively
discusses and monitors and which are announced but not yet questioned in detail.

Inputs:  PIB sqlite register (announcements) + the LS and RS question registries
         (data/registers/ls_pq_registry.json, rs_pq_registry.json)
Output:  docs/SCHEME_SCRUTINY_MATRIX.md  (generated -- never hand-edit)

Buckets (tunable below), on COMBINED LS+RS questioning:
  A  actively discussed & progress-monitored : >=10 questions across both houses
     AND a question within the last 12 months
  B  some discussion                          : >=1 question but not A
  C  yet to be discussed in detail            : PIB announcements, zero captured
     questions in either house

Rerun after refreshing either registry:  python3 scripts/build_scrutiny_matrix.py
"""
import datetime, json, os, sqlite3, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_reportage import scheme_hits

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.expanduser("~/india-trade-sector-policy-recommendations/data/pib_index.sqlite")
PQ_LS = os.path.join(ROOT, "data/registers/ls_pq_registry.json")
PQ_RS = os.path.join(ROOT, "data/registers/rs_pq_registry.json")
OUT = os.path.join(ROOT, "docs/SCHEME_SCRUTINY_MATRIX.md")
ACTIVE_MIN_Q = 10
RECENT_DAYS = 365


def main():
    today = datetime.date.today()
    recent = (today - datetime.timedelta(days=RECENT_DAYS)).isoformat()

    pib = {}
    for date, title in sqlite3.connect(DB).execute("SELECT date,title FROM pib_items"):
        if not date:
            continue
        for s in set(scheme_hits(title)):
            d = pib.setdefault(s, {"n": 0, "first": date, "last": date})
            d["n"] += 1
            d["first"] = min(d["first"], date)
            d["last"] = max(d["last"], date)

    def load_house(path):
        rows = json.load(open(path))
        agg = {}
        for r in rows:
            for s in set(r["schemes"]):
                d = agg.setdefault(s, {"n": 0, "star": 0, "first": r["iso"], "last": r["iso"]})
                d["n"] += 1
                d["star"] += (r["qtype"] or "").strip() == "STARRED"
                d["first"] = min(d["first"], r["iso"])
                d["last"] = max(d["last"], r["iso"])
        return rows, agg

    ls_rows, ls = load_house(PQ_LS)
    rs_rows, rs = load_house(PQ_RS)

    rows = []
    for s in sorted(set(pib) | set(ls) | set(rs)):
        a = pib.get(s, {"n": 0, "first": "", "last": ""})
        l = ls.get(s, {"n": 0, "star": 0, "first": "", "last": ""})
        rr = rs.get(s, {"n": 0, "star": 0, "first": "", "last": ""})
        tot_n = l["n"] + rr["n"]
        last_q = max(l["last"], rr["last"])
        if tot_n >= ACTIVE_MIN_Q and last_q >= recent:
            bucket = "A"
        elif tot_n > 0:
            bucket = "B"
        else:
            bucket = "C"
        rows.append({"s": s, "bucket": bucket, "tot_n": tot_n, "last_q": last_q,
                     "first_q": min(x for x in [l["first"] or "9999", rr["first"] or "9999"]) if tot_n else "",
                     **{"pib_" + k: v for k, v in a.items()},
                     **{"ls_" + k: v for k, v in l.items()},
                     **{"rs_" + k: v for k, v in rr.items()}})

    nA = sum(r["bucket"] == "A" for r in rows)
    nB = sum(r["bucket"] == "B" for r in rows)
    nC = sum(r["bucket"] == "C" for r in rows)
    tq_ls = len(ls_rows)
    tq_rs = len(rs_rows)
    ta = sum(r["pib_n"] for r in rows)

    def table(rws, cols):
        out = ["| Scheme | PIB anns | Last ann. | LS Qs | RS Qs | ★ | First Q | Last Q |",
               "|---|---:|---|---:|---:|---:|---|---|"]
        for r in rws:
            star = (r["ls_star"] + r["rs_star"]) or ""
            out.append(f"| {r['s']} | {r['pib_n']} | {r['pib_last']} | "
                       f"{r['ls_n'] or ''} | {r['rs_n'] or ''} | {star} | "
                       f"{r['first_q'] if r['first_q']!='9999' else ''} | {r['last_q']} |")
        return "\n".join(out)

    A = sorted([r for r in rows if r["bucket"] == "A"], key=lambda x: -x["tot_n"])
    B = sorted([r for r in rows if r["bucket"] == "B"], key=lambda x: -x["tot_n"])
    C = sorted([r for r in rows if r["bucket"] == "C"], key=lambda x: -x["pib_n"])

    md = f"""# Scheme Scrutiny Matrix
### Which schemes Parliament actively discusses -- and which it has not yet questioned in detail

Generated {today} by `scripts/build_scrutiny_matrix.py`. Cross-references the PIB
announcement register ({ta:,} scheme-mapped announcements) with BOTH houses'
question registries ({tq_ls:,} Lok Sabha questions, 17th+18th LS, and {tq_rs:,}
Rajya Sabha questions since 2019), all classified by the same scheme-regex map --
one map, three registries, so the join is exact.

**{nA} schemes actively discussed & monitored** (>= {ACTIVE_MIN_Q} questions across both houses, one within
12 months) - **{nB} with some discussion** - **{nC} announced but with zero captured
questions in either house**.

## A. Actively discussed & progress-monitored ({nA})

Parliament returns to these repeatedly and recently; implementation is being
monitored on the floor.

{table(A, None)}

## B. Some discussion, not sustained ({nB})

Questions exist, but either few or without recent follow-up.

{table(B, None)}

## C. Announced, yet to be discussed in detail ({nC})

PIB carries announcements; neither house's registry captures a question. For recent
launches this is lag, not neglect -- Parliament has not had a full session cycle
since the announcement.

{table(C, None)}

## Reading the C list honestly

- **Recent launches** (MPMS Jul-2026, PM Dhan-Dhaanya, Pulses Mission, Export
  Promotion Mission, SPMEPCI, ADEETIE, National Manufacturing Mission): announced
  within the last year; zero questions mostly means *not yet*, not *ignored*.
- **PLI - White Goods**: {'STILL in C -- running since 2021 with no subject-titled question in either house; white-goods questions may hide under generic PLI subjects.' if any('White Goods' in r['s'] for r in C) else 'moved OUT of C once Rajya Sabha questions were counted -- upper-house members did ask.'}
- **Telecom PLI**: {'in C, but telecom questions are captured under generic PLI subjects -- a classification artefact more than a scrutiny gap.' if any('Telecom' in r['s'] for r in C) else 'left C once Rajya Sabha questions were counted.'}

## Method & limits

Question capture is by **subject line only** in both houses: a question whose
subject names no scheme is not counted even if its answer discusses one. Zero
captured questions is therefore an upper bound on neglect, not proof of it. PIB
counts include progress releases and Parliament-answer summaries, not only launches.
Thresholds (>= {ACTIVE_MIN_Q} questions, {RECENT_DAYS}-day recency) are stated, tunable
constants, not findings.
"""
    open(OUT, "w", encoding="utf-8").write(md)
    print(f"scrutiny matrix: {len(rows)} schemes -> A {nA} / B {nB} / C {nC} -> {OUT}")


if __name__ == "__main__":
    main()
