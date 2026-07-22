#!/usr/bin/env python3
"""Auto-update runner for the digital twin (implements layers/14_update_engine.json).

Subcommands map to the engine's cadences:
    routes     -- health-check every portal in layers/15_directory.json (weekly / before any sweep)
    unnati     -- diff the UNNATI portal notice vs last snapshot (weekly; watches for registration resumption)
    nsws       -- liveness + last-modified probe of tracked NSWS scheme pages (weekly)
    rbi        -- record the latest RBI Weekly Statistical Supplement issue (weekly)
    pib        -- delegate to the policy repo's pib_index.py --update (daily)
    catalogue  -- rebuild the flat instrument index + docs/SCHEME_CATALOGUE.md (after any layer edit)
    weekly     -- routes + unnati + nsws + rbi

Snapshots land in state/ as dated JSON; a change vs the previous snapshot prints a
CHANGE line (greppable by cron mail / launchd logs). Corrections rule: snapshots are
append-only -- nothing is overwritten.

Suggested crontab (documented, not installed by this script):
    17 7 * * *   cd ~/digital-twin-for-ipa && python3 scripts/refresh_twin.py pib
    23 8 * * 1   cd ~/digital-twin-for-ipa && python3 scripts/refresh_twin.py weekly
"""
import argparse, datetime, difflib, glob, html, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126"
TODAY = datetime.date.today().isoformat()

os.makedirs(STATE, exist_ok=True)


def curl(url, timeout=20, insecure=False):
    cmd = ["curl", "-sL", "-A", UA, "-m", str(timeout), "-w", "\n%{http_code}", url]
    if insecure:
        cmd.insert(1, "-k")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10).stdout
        body, _, code = out.rpartition("\n")
        return code.strip(), body
    except Exception as e:
        return "ERR", str(e)


def strip_tags(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))).strip()


def latest_snapshot(prefix):
    files = sorted(glob.glob(os.path.join(STATE, f"{prefix}_*.json")))
    return json.load(open(files[-1])) if files else None


def save_snapshot(prefix, data):
    path = os.path.join(STATE, f"{prefix}_{TODAY}.json")
    json.dump(data, open(path, "w"), indent=1)
    return path


def cmd_routes():
    directory = json.load(open(os.path.join(ROOT, "layers/15_directory.json")))
    targets = {}
    for tier in ("central", "state"):
        for name, info in directory[tier].items():
            targets[name] = info["url"]

    def probe(item):
        name, url = item
        insecure = "ditc.goa.gov.in" in url
        code, _ = curl(url, timeout=15, insecure=insecure)
        return name, {"url": url, "http": code}

    with ThreadPoolExecutor(max_workers=12) as ex:
        results = dict(ex.map(probe, targets.items()))

    prev = latest_snapshot("routes")
    changes = []
    for name, r in results.items():
        ok = r["http"].startswith(("2", "3"))
        r["ok"] = ok
        if prev and name in prev.get("results", {}) and prev["results"][name].get("ok") != ok:
            changes.append(f"CHANGE route {name}: ok={prev['results'][name].get('ok')} -> {ok} ({r['http']})")
    down = [n for n, r in results.items() if not r["ok"]]
    snap = {"checked": TODAY, "results": results, "down": down}
    path = save_snapshot("routes", snap)
    print(f"routes: {len(results)} checked, {len(down)} down -> {path}")
    for d in down:
        print(f"  DOWN {d} ({results[d]['http']}) {results[d]['url']}")
    for c in changes:
        print(" ", c)


def cmd_unnati():
    code, body = curl("https://unnati.dpiit.gov.in/", timeout=30)
    text = strip_tags(body)
    m = re.search(r"Important Notice.{0,1200}", text)
    notice = m.group(0) if m else "(no notice block found)"
    prev = latest_snapshot("unnati")
    snap = {"checked": TODAY, "http": code, "notice": notice}
    path = save_snapshot("unnati", snap)
    if prev and prev.get("notice") != notice:
        print("CHANGE unnati notice text differs from last snapshot:")
        for line in difflib.unified_diff(prev["notice"].split(". "), notice.split(". "), lineterm=""):
            print(" ", line)
    else:
        stopped = "has presently been stopped" in notice
        print(f"unnati: http={code}, registration_stopped={stopped} -> {path}")


def cmd_nsws():
    pages = {
        "unnati_guidelines": "https://www.nsws.gov.in/s3fs/2025-07/General_Operational_Guidelines_for_Unnati_Scheme_2024_0.pdf",
        "nsws_home": "https://www.nsws.gov.in",
    }
    snap = {"checked": TODAY, "pages": {}}
    for name, url in pages.items():
        code, body = curl(url, timeout=25)
        snap["pages"][name] = {"http": code, "bytes": len(body)}
    prev = latest_snapshot("nsws")
    path = save_snapshot("nsws", snap)
    if prev:
        for name, cur in snap["pages"].items():
            old = prev.get("pages", {}).get(name, {})
            if old.get("http") != cur["http"]:
                print(f"CHANGE nsws {name}: {old.get('http')} -> {cur['http']}")
    print(f"nsws: {len(pages)} pages -> {path}")


def cmd_rbi():
    code, body = curl("https://rbi.org.in/scripts/WSSView.aspx?Id=N", timeout=30)
    text = strip_tags(body)
    dates = re.findall(
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r"|\d{2}/\d{2}/\d{4})",
        text,
    )
    latest = dates[0] if dates else None
    prev = latest_snapshot("rbi")
    snap = {"checked": TODAY, "http": code, "latest_wss": latest}
    path = save_snapshot("rbi", snap)
    if prev and prev.get("latest_wss") != latest:
        print(f"CHANGE rbi WSS: {prev.get('latest_wss')} -> {latest}")
    print(f"rbi: latest WSS issue = {latest} -> {path}")


def cmd_pib():
    script = os.path.expanduser("~/india-trade-sector-policy-recommendations/scripts/pib_index.py")
    if not os.path.exists(script):
        sys.exit(f"pib_index.py not found at {script}")
    subprocess.run([sys.executable, script, "--update"], cwd=os.path.dirname(os.path.dirname(script)), check=False)


def cmd_catalogue():
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts/build_catalogue.py")], check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts/build_reportage.py")], check=True)


def cmd_watchlist():
    """Rebuild the live/dynamic cross-repo & watchlist layers (25-28)."""
    for s in ("build_layer25_linkages.py", "build_layer26_projects.py",
              "build_layer27_entry_facilitators.py",
              "build_layer28_policy_watchlist.py"):
        try:
            subprocess.run([sys.executable, os.path.join(ROOT, "scripts", s)],
                           check=True)
        except Exception as e:
            print(f"ERROR {s}: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["routes", "unnati", "nsws", "rbi", "pib", "catalogue", "watchlist", "weekly"])
    args = ap.parse_args()
    if args.cmd == "weekly":
        for c in (cmd_routes, cmd_unnati, cmd_nsws, cmd_rbi, cmd_watchlist):
            try:
                c()
            except Exception as e:
                print(f"ERROR {c.__name__}: {e}")
    else:
        globals()[f"cmd_{args.cmd}"]()


if __name__ == "__main__":
    main()
