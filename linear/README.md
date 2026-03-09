# Linear Bot (v1) Bootstrap

This folder contains the initial scaffold for Linear + GitHub workflow-enforcement automation.

## Structure

- `/bitpod-tools/linear/docs/`
  - SOP and implementation references.
- `/bitpod-tools/linear/docs/process/`
  - Process runbooks and operator notes.
- `/bitpod-tools/linear/src/`
  - Rule engine, webhook service, and simulator.
- `/bitpod-tools/linear/events/`
  - Sample payloads for local simulation.
- `/bitpod-tools/linear/tests/`
  - Unit tests for gate and transition behavior.

## Primary SOP

- `./docs/linear_custom_configs_v1.md`
- `./docs/process/linear_bot_v1_runbook.md`
- `./docs/process/live_cutover_auth_batch.md`
- `./docs/process/linear_operating_guide_v1.md`
- `./docs/process/linear_link_reference_policy_v1.md`
- `./docs/process/linear_operating_guide_changelog.md`

## Current implementation coverage (v1)

Implemented in engine/service:
- GitHub events:
  - `pull_request.opened`
  - `pull_request.ready_for_review`
  - `pull_request.closed` with merged=true (fail-closed gate check)
- Linear events:
  - ready-gate enforcement trigger
  - comment-created QA token parser (`QA_RESULT=PASSED|FAILED`)
  - PM label changed (`Approved` / `Rejected`)
  - daily aging scan payload handler
- Gating behavior:
  - Ready gate (required Type + required headings)
  - QA/PM label defaults in review flow
  - merge gate requires QA Passed + PM Approved
  - fail-closed comments when gates are not met
- Dry-run default and simulation runner

## Status model note (important)

SOP expects emoji statuses (`☑️ Ready`, `🏗️ In Progress`, `🧪 In Review`, etc).
Current BIT workspace still uses mixed/non-emoji statuses (`Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Icebox 🧊`, `Obsolete`).

This implementation includes fallback handling for current statuses where safe, but full parity requires final Linear status normalization.

## How to run

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools/linear/src
python3 service.py --dry-run
```

## Configure secrets

Recommended env vars:

- `DRY_RUN=true` (default)
- `BOT_HOST=127.0.0.1`
- `BOT_PORT=8787`
- `GITHUB_APP_ID` (future live mode)
- `GITHUB_APP_PRIVATE_KEY` (future live mode)
- `GITHUB_WEBHOOK_SECRET` (future live mode)
- `LINEAR_API_KEY` or OAuth app creds (future live mode)
- `LINEAR_WEBHOOK_SECRET` (future live mode)

Reference template:
- `./config.example.env`

## Configure webhooks

GitHub webhook events:
- `pull_request` (opened, ready_for_review, closed)

Linear webhook events:
- issue updated (state and labels)
- comment created

Schedule:
- daily aging scan for backlog/icebox transitions.

## Simulation runner

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools/linear/src
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
python3 simulate.py --mode linear_comment --event ../events/sample_linear_comment_passed.json
python3 simulate.py --mode aging_scan --event ../events/sample_aging_scan.json
python3 simulate_e2e.py
```

Additional samples:

```bash
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
# PM label changed and merged gate are exercised through service payloads in ./events/
```

`simulate_e2e.py` runs the full happy-path sequence:
- PR opened -> In Progress
- PR ready for review -> In Review + QA/PM defaults
- QA comment token parse (`QA_RESULT=PASSED`)
- PM approval label signal
- PR merged with gates satisfied -> Done

## Test

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools
python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py
```

One-command local smoke:

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools
bash linear/scripts/local_smoke.sh
```

## GitHub Actions smoke

PR checks run automatically for `linear/**` via:
- `.github/workflows/linear-bot-smoke.yml`

## Attribution guardrails

- If GitHub actions appear as CJ instead of bot/app identity: stop and report `AUTH ATTRIBUTION WRONG`.
- If Linear mutations appear as CJ instead of app actor: stop and report `LINEAR ACTOR WRONG`.

## Live-mode safety

- Service live mode currently supports GitHub PR comments only.
- Linear live mutation executor is intentionally fail-closed until final API/actor wiring is complete.

## Portability-first architecture

- Core logic is platform-agnostic in `src/engine.py`.
- Runtime orchestration + memory abstraction lives in `src/runtime.py` + `src/memory.py`.
- Transport adapters stay thin (`src/service.py`).
- Cloudflare migration notes: `docs/cloudflare_migration_path.md`.

## Cloudflare adapter (optional now, migration-ready)

A Worker edge gateway scaffold is included at:
- `linear/cloudflare/worker.mjs`
- `linear/cloudflare/wrangler.toml`

Purpose:
- stable public webhook ingress (`/webhooks/github`, `/webhooks/linear`)
- forward events to runtime backend (`BOT_ORIGIN`)
- keep portability while enabling Cloudflare-first deployment path

Quick start:
```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools/linear/cloudflare
wrangler deploy
```

Required Cloudflare secrets/vars:
- `BOT_ORIGIN` (backend runtime URL)
- `GITHUB_WEBHOOK_SECRET`
- `LINEAR_WEBHOOK_SECRET`
