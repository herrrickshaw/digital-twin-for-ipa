#!/usr/bin/env python3
"""Scheme scrutiny matrix: cross-reference the PIB announcement register with the
Lok Sabha question registry, per scheme, to show which schemes Parliament actively
discusses and monitors and which are announced but not yet questioned in detail.

Inputs:  PIB sqlite register (announcements) + data/registers/ls_pq_registry.json
Output:  docs/SCHEME_SCRUTINY_MATRIX.md  (generated -- never hand-edit)

Buckets (tunable below):
  A  actively discussed & progress-monitored : >=10 LS questions AND a question
     within the last 12 months
  B  some discussion                          : >=1 question but not A
  C  yet to be discussed in detail            : PIB announcements, zero captured
     LS questions

Rerun after refreshing either registry:  python3 scripts/build_scrutiny_matrix.py
"""
import datetime, json, os, sqlite3, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_reportage import scheme_hits

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.expanduser("~/india-trade-sector-policy-recommendations/data/pib_index.sqlite")
PQ = os.path.join(ROOT, "data/registers/ls_pq_registry.json")
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

    pq = {}
    pq_rows = json.load(open(PQ))
    for r in pq_rows:
        for s in set(r["schemes"]):
            d = pq.setdefault(s, {"n": 0, "star": 0, "first": r["iso"], "last": r["iso"]})
            d["n"] += 1
            d["star"] += r["qtype"] == "STARRED"
            d["first"] = min(d["first"], r["iso"])
            d["last"] = max(d["last"], r["iso"])

    rows = []
    for s in sorted(set(pib) | set(pq)):
        a = pib.get(s, {"n": 0, "first": "", "last": ""})
        q = pq.get(s, {"n": 0, "star": 0, "first": "", "last": ""})
        if q["n"] >= ACTIVE_MIN_Q and q["last"] >= recent:
            bucket = "A"
        elif q["n"] > 0:
            bucket = "B"
        else:
            bucket = "C"
        rows.append({"s": s, "bucket": bucket, **{"pib_" + k: v for k, v in a.items()},
                     **{"pq_" + k: v for k, v in q.items()}})

    nA = sum(r["bucket"] == "A" for r in rows)
    nB = sum(r["bucket"] == "B" for r in rows)
    nC = sum(r["bucket"] == "C" for r in rows)
    tq = len(pq_rows)
    ta = sum(r["pib_n"] for r in rows)

    def table(rs, cols):
        out = ["| Scheme | PIB anns | Last ann. | LS Qs | ★ | First Q | Last Q |",
               "|---|---:|---|---:|---:|---|---|"]
        for r in rs:
            out.append(f"| {r['s']} | {r['pib_n']} | {r['pib_last']} | "
                       f"{r['pq_n'] or ''} | {r['pq_star'] or ''} | "
                       f"{r['pq_first']} | {r['pq_last']} |")
        return "\n".join(out)

    A = sorted([r for r in rows if r["bucket"] == "A"], key=lambda x: -x["pq_n"])
    B = sorted([r for r in rows if r["bucket"] == "B"], key=lambda x: -x["pq_n"])
    C = sorted([r for r in rows if r["bucket"] == "C"], key=lambda x: -x["pib_n"])

    md = f"""# Scheme Scrutiny Matrix
### Which schemes Parliament actively discusses -- and which it has not yet questioned in detail

Generated {today} by `scripts/build_scrutiny_matrix.py`. Cross-references the PIB
announcement register ({ta:,} scheme-mapped announcements) with the Lok Sabha
question registry ({tq:,} questions, 17th+18th LS), both classified
by the same scheme-regex map -- one map, two registries, so the join is exact.

**{nA} schemes actively discussed & monitored** (>= {ACTIVE_MIN_Q} questions, one within
12 months) - **{nB} with some discussion** - **{nC} announced but with zero captured
Lok Sabha questions**.

## A. Actively discussed & progress-monitored ({nA})

Parliament returns to these repeatedly and recently; implementation is being
monitored on the floor.

{table(A, None)}

## B. Some discussion, not sustained ({nB})

Questions exist, but either few or without recent follow-up.

{table(B, None)}

## C. Announced, yet to be discussed in detail ({nC})

PIB carries announcements; the LS registry captures **no** questions. For recent
launches this is lag, not neglect -- Parliament has not had a full session cycle
since the announcement.

{table(C, None)}

## Reading the C list honestly

- **Recent launches** (MPMS Jul-2026, PM Dhan-Dhaanya, Pulses Mission, Export
  Promotion Mission, SPMEPCI, ADEETIE, National Manufacturing Mission): announced
  within the last year; zero questions mostly means *not yet*, not *ignored*.
- **PLI - White Goods**: genuinely under-scrutinised -- running since 2021 with
  {next((r['pib_n'] for r in C if 'White Goods' in r['s']), '?')} announcements and
  no subject-titled LS question captured. White-goods questions may hide under
  generic "PLI Scheme" subjects (counted under PLI (general)).
- **Telecom PLI**: telecom questions are captured under PLI (family) subjects; the
  standalone label is a classification artefact more than a scrutiny gap.

## Method & limits

LS capture is by **subject line only** (sansad.in index limitation): a question whose
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
