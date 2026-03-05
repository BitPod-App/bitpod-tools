# Linear Bot (v1) Bootstrap

This folder contains the initial scaffold for Linear + GitHub workflow-enforcement automation.

## Structure

- `/bitpod-tools/linear/docs/`
  - SOP and implementation references.
- `/bitpod-tools/linear/docs/process/`
  - Process runbooks and operator notes (placeholder for now).

## Primary SOP

- `./docs/linear_custom_configs_v1.md`

## How to run

1. Implement bot runtime (GitHub Actions workflow or webhook service) under this folder.
2. Start in dry-run mode (`DRY_RUN=true`) and simulate events before enabling mutations.
3. Enable live mutations only after attribution checks pass for both GitHub and Linear actors.

## Configure secrets

Recommended required secrets/env vars (exact names can be adapted to implementation):

- `GITHUB_APP_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `GITHUB_WEBHOOK_SECRET`
- `LINEAR_API_KEY` (or OAuth app credentials for app-actor mutations)
- `LINEAR_WEBHOOK_SECRET`
- `DRY_RUN` (default: `true`)

## Configure webhooks

GitHub webhook events:
- `pull_request` (opened, ready_for_review, closed)

Linear webhook events:
- issue updated (state and labels)
- comment created

Schedule:
- daily aging scan for backlog/icebox transitions.

## Attribution guardrails (fail-closed)

- If GitHub actions appear as CJ instead of bot/app identity: stop and report `AUTH ATTRIBUTION WRONG`.
- If Linear mutations appear as CJ instead of app actor: stop and report `LINEAR ACTOR WRONG`.

## Simulation runner

Run sample event simulations locally:

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools/linear/src
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
python3 simulate.py --mode linear_comment --event ../events/sample_linear_comment_passed.json
python3 simulate.py --mode aging_scan --event ../events/sample_aging_scan.json
```

## Test

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools
python3 -m unittest linear/tests/test_engine.py
```

## Webhook service (dry-run default)

Run local service:

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools/linear/src
cp ../config.example.env ../.env  # optional
python3 service.py --dry-run
```

POST sample events:

```bash
curl -sS -X POST http://127.0.0.1:8787/github \
  -H 'content-type: application/json' \
  --data @../events/sample_pr_opened.json

curl -sS -X POST http://127.0.0.1:8787/linear \
  -H 'content-type: application/json' \
  --data '{"type":"comment_created","issue_key":"BIT-45","comment_body":"QA_RESULT=PASSED","pr_url":"https://github.com/BitPod-App/bitpod-tools/pull/17"}'
```

Service is fail-closed for live mode until explicit API executor wiring is added.
