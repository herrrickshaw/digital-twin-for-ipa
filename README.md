# Digital Twin of India's Investment Promotion Apparatus (IPA)

A machine-readable model of how the Government of India promotes and incentivises investment: the central ministries and
state agencies, the incentive instruments each one offers, how those instruments stack or exclude each other, what the
budget record says about delivery, and the foreign/Indian companies and projects that could use them. It is aimed at
investment-promotion analysts and researchers. Outputs are numbered JSON "layers" (00-51) in `layers/`, a SQLite company
database (`data/companies.db`), generated Markdown/HTML reports in `docs/` and dated change snapshots in `state/`.

> Status: active (weekly refresh by scheduled job). Research use only; not investment, legal or tax advice. The
> subject is India's *investment promotion* apparatus, not an isopropyl-alcohol process model. Data come from public
> government portals, regulator filings and press; each layer records how each claim was verified.

## What it does
- Catalogues 312 incentive instruments (195 central, 117 state) in one schema (`layers/13_flat_instrument_index.json`).
- Maps scheme interlinkages (stack / exclude / converge / feed) and an 8-step investor workflow (layers 04, 10).
- Tracks scheme and state-incentive delivery (funds, arrears, open windows) and forward policy (layers 17, 18, 28).
- Builds a deduplicated company database (`data/companies.db`, layer 32) from leads, clearance filers, PLI beneficiaries and park tenants.
- Sweeps filings, news and trade-fair rosters for investment intent (EDGAR, DART, EDINET, cninfo, ESEF, SIX, Oslo, RSS).
- Renders a single-page [National Dashboard](docs/national_dashboard.html) and quarterly/state "reportage" pages.

## Quick start
```bash
git clone https://github.com/herrrickshaw/digital-twin-for-ipa.git
cd digital-twin-for-ipa
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # optional extras only; the refresh engine is stdlib-only
python3 scripts/build_national_dashboard.py   # offline: layers/*.json -> docs/national_dashboard.html
```
Try it without installing: the [Colab quickstart](notebooks/twin_quickstart.ipynb). New to the repo? See
[HOW_TO_USE_WITH_AI.md](HOW_TO_USE_WITH_AI.md).

## How it works
| Stage | Module | Output |
|---|---|---|
| Sweep sources (per layer) | `scripts/build_layerNN_*.py`, `build_*_sweep.py`, `collect_*_news.py` | `layers/NN_*.json`, `data/**` |
| Consolidate companies | `scripts/build_company_db.py` (+ `twin_common.py`) | `data/companies.db`, `layers/32_company_db.json` |
| Refresh and snapshot | `scripts/refresh_twin.py` | `state/<kind>_<date>.json`, `CHANGE` lines on stdout |
| Render | `scripts/build_national_dashboard.py`, `build_reportage.py`, `build_catalogue.py` | `docs/*.html`, `docs/*.md` |

Design decisions: every layer is plain JSON so it diffs cleanly; failures to access a source are stored as data, never
skipped; corrections are displayed, not silent; snapshots in `state/` are append-only; the weekly engine shells out to
`curl` and uses only the standard library. `scripts/twin_common.py` holds the company-name normaliser and the
"already known company" lookup shared by layers 32, 41, 42, 44 and 45.

## Repository layout
| Path | Purpose |
|---|---|
| `layers/` | The numbered data layers (00-51) (JSON; some are directories of per-cluster files) |
| `scripts/` | Layer builders, collectors, `refresh_twin.py` (scheduled entry point), shared `twin_common.py` |
| `data/` | `companies.db` (generated), registers, registry IDs, news sweeps, trade-fair rosters |
| `docs/` | Generated reports and dashboards plus hand-written notes; `docs/LAYER_NOTES.md` is the full per-layer history |
| `state/` | Dated snapshots from `refresh_twin.py` (routes, UNNATI, NSWS, RBI) and `cron.log` |
| `workflows/` | Importable n8n workflow wrapping `refresh_twin.py` |
| `notebooks/` | `twin_quickstart.ipynb` |
| `tests/` | Offline pytest characterisation tests |

Key layers: 01 ministries master (86 entities) · 02/09/12 incentive catalogues (central, other entities, states) ·
10 interlinkage graph · 13 flat instrument index · 15 portal directory (64 portals) · 16 leads (263 across 26
countries) · 26 project pipeline (12,385 NIP opportunities) · 32 company DB (1,785 companies) · 44 five-year state
MoU sweep. Full table and the history of every sweep: [docs/LAYER_NOTES.md](docs/LAYER_NOTES.md).

## Scheduled refresh (interface kept stable)
```bash
python3 scripts/refresh_twin.py weekly     # routes health + UNNATI notice diff + NSWS + RBI WSS + watchlist layers
python3 scripts/refresh_twin.py pib        # delegates to the policy repo's pib_index.py --update
python3 scripts/refresh_twin.py catalogue  # flat index view -> docs/SCHEME_CATALOGUE.md, reportage
```
Suggested crontab (not installed automatically): `17 7 * * *` for `pib`, `23 8 * * 1` for `weekly`. If run from a
virtualenv, point cron at that venv's `python3` by full path; a bare system interpreter missing a dependency can fail
silently. Script names, subcommands and output paths are relied on by scheduled jobs, so do not rename them.

## Data sources
Official ministry and state portals (PIB, NSWS, UNNATI, India Investment Grid, PARIVESH, MoSPI, RBI), PRS Legislative
Research, SEC EDGAR, Korea DART, Japan EDINET, China cninfo, ESEF/filings.xbrl.org, SIX Exchange Regulation, Oslo
NewsWeb, WAIPA, trade-fair exhibitor lists and press RSS. Each source, its access route and its caveats are recorded
in the relevant layer file and in `docs/LAYER_NOTES.md`; scraped or gated sources are labelled there.

## Configuration
- Keys are read at run time from `~/.config/market-secrets/credentials.env` (outside the repo): `EDINET_API_KEY`,
  `DART_KEY`, `NEWSAPI_KEY` and optional registry tokens (`COMPANIES_HOUSE_KEY`, `GBIZINFO_TOKEN`). No key is committed.
- `scripts/send_twin_alert.py` reads `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `MAIL_TO` from the environment.
- `requirements.txt`: optional `pypdf`, `pandas`; system tools `curl`, `poppler`, `tesseract` for PDF work.

## Testing
```bash
pip install pytest ruff
pytest -q                 # offline; the network is never touched
ruff check tests scripts/twin_common.py scripts/build_company_db.py scripts/build_national_dashboard.py scripts/refresh_twin.py
```
The tests pin the company DB, dashboard HTML and `refresh_twin.py` snapshots to the pre-refactor outputs.

## Limitations and known issues
- Many sweeps depend on live third-party sites that change layout or block bots; failures are recorded in the layer.
- Layer counts quoted in prose may lag the JSON; the files in `layers/` and `state/` are authoritative.
- Several news-search approaches (NewsAPI keyword sweeps) produced false positives; layer 42 records the verified method.
- `workflows/n8n_twin_refresh.json` hard-codes a local checkout path (`/Users/umashankar/digital-twin-for-ipa`).
- Only a subset of scripts is covered by tests and lint; the rest are legacy sweep scripts.

## Related repositories
[india-trade-sector-policy-recommendations](https://github.com/herrrickshaw/india-trade-sector-policy-recommendations)
(PIB register, bulletins) · [focus-sector-investor-map](https://github.com/herrrickshaw/focus-sector-investor-map)
(global company layer) · [global-stock-screener](https://github.com/herrrickshaw/global-stock-screener) (listed-company rosters).

## Licence
No licence file yet — all rights reserved.
