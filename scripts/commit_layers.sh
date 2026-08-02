#!/bin/bash
# Commit + push refreshed layers/state after a cron run, only if something changed.
set -e
cd "$(dirname "$0")/.."
git add layers state data/companies.db data/registers docs/REPORTAGE.md docs/reportage.html docs/reportage_ministry.html docs/reportage_latest.html docs/reportage_states.html
if git diff --cached --quiet; then
    echo "$(date '+%F %T') commit_layers: no changes"
else
    git commit -q -m "auto: weekly layer/state refresh $(date '+%F')"
    git push -q && echo "$(date '+%F %T') commit_layers: pushed"
fi
