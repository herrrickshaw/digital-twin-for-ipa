# n8n workflow — Digital Twin auto-refresh

`n8n_twin_refresh.json` is an importable [n8n](https://n8n.io) workflow that wraps the same
`scripts/refresh_twin.py` engine the crontab runs, and adds what plain cron can't:

```
Daily 07:17 ──▶ refresh_twin.py pib
Weekly Mon 08:23 ─┐
Manual trigger ───┴▶ refresh_twin.py weekly ─▶ Detect CHANGE lines ─▶ Any changes?
                                                                        ├─ yes ─▶ Email alert ─▶ Commit snapshots
                                                                        └─ no ──────────────────▶ Commit snapshots
```

- **CHANGE detection**: the Code node parses the script output for `CHANGE` / `DOWN` lines and
  raises a synthetic alert if the UNNATI notice ever flips to `registration_stopped=False`
  (the resumption signal worth acting on same-day).
- **Email alert**: credential-free by design — the node shells out to
  `scripts/send_twin_alert.py`, which sources Gmail creds at runtime from the machine's
  existing dailybrief launchd plist. No SMTP credential is ever stored in n8n or the repo.
- **Snapshot commits**: every weekly run commits `state/` locally (no push — pushing stays a
  human/main-session action per program convention).

## Import & run

```bash
npm install -g n8n                 # one-time
n8n import:workflow --input=workflows/n8n_twin_refresh.json
n8n                                # UI at http://localhost:5678 — attach SMTP cred, toggle Active
```

## Scheduler overlap

The crontab installed 2026-07-20 runs the same two cadences. Run ONE scheduler:
- keep **cron** (zero-dependency, survives without n8n running) and use this workflow only via
  its Manual trigger for on-demand runs with alerting, **or**
- activate the n8n schedules and remove the two crontab lines (`crontab -e`) — n8n only fires
  while the n8n process is running, so pair it with a launchd/pm2 keep-alive if you go this way.

Timezone is pinned to Asia/Kolkata in workflow settings.
