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
```

Additional samples:

```bash
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
# PM label changed and merged gate are exercised through service payloads in ./events/
```

## Test

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools
python3 -m unittest linear/tests/test_engine.py
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
