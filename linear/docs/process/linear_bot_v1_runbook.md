# Linear Bot v1 Runbook

Current truth note:

- this runbook is for the bot/runtime draft surface
- it does not replace the temporary live governance path in [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)
- until the richer acceptance workflow is actually implemented and verified, operators should rely on the interim policy first and treat this bot path as supporting automation

This runbook is the operator path for local dry-run, CI validation, and first live wiring.

## 1) Local dry-run startup

```bash
cd $WORKSPACE/bitpod-tools
python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py
cd linear/src
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
python3 simulate.py --mode linear_comment --event ../events/sample_linear_comment_passed.json
python3 simulate.py --mode aging_scan --event ../events/sample_aging_scan.json
python3 simulate_e2e.py
python3 service.py --dry-run
```

Expected:
- tests pass
- simulations emit JSON actions
- service starts on `http://127.0.0.1:8787`

## 2) Environment setup

For the Vera QA Gate dispatcher, do not create a repo-local `.env` as the
primary runtime secret mechanism. Refresh the machine-local runtime env from the
approved 1Password service-account item instead:

```bash
cd $WORKSPACE/bitpod-tools
python3 linear/scripts/refresh_vera_qa_gate_runtime_env.py
linear/scripts/start_vera_qa_gate_dispatcher.sh
```

The generated env file lives at
`~/.hermes/profiles/vera/vera-qa-gate-runtime.env` and must not be committed.
It includes GitHub App credentials, webhook signing secret, Linear OAuth client
credentials, expected Linear actor fields, and the Vera workspace map.

Populate only required values for non-Vera modes or controlled overrides:

- Required now:
  - `DRY_RUN=true|false`
  - `BOT_HOST`
  - `BOT_PORT`
  - `RUNTIME_TRACE_PATH` (durable runtime event sink, example: `/tmp/bitpod_runtime_events.jsonl`)
  - `TRACE_STORE_PATH` (service action trace sink, example: `/tmp/bitpod_linear_runtime_trace.jsonl`)
- Required for live Vera GitHub gate check runs:
  - `VERA_QA_GATE_GITHUB_TOKEN` short-lived installation token, or `VERA_QA_GATE_GITHUB_APP_ID` / `VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID` / `VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY`
  - `GITHUB_WEBHOOK_SECRET`
- Required for Linear live mutation wiring (guarded/fail-closed):
  - `LINEAR_OAUTH_CLIENT_ID` / `LINEAR_OAUTH_CLIENT_SECRET` from the approved Linear OAuth app actor so the runtime mints tokens with `client_credentials`; `LINEAR_OAUTH_ACCESS_TOKEN` is short-lived emergency fallback only and `LINEAR_API_KEY` is legacy personal-script fallback only
  - `LINEAR_WEBHOOK_SECRET`
  - `LINEAR_LIVE_EXECUTOR_ENABLED=false|true` (hard kill switch; default false)
  - at least one of `LINEAR_EXPECTED_ACTOR_ID`, `LINEAR_EXPECTED_ACTOR_NAME`, or `LINEAR_EXPECTED_ACTOR_EMAIL`
  - `VERA_QA_KANBAN_WORKSPACE_MAP` when dispatching Vera QA from GitHub PRs across repos; unmapped repos fail closed when the map is present

## 3) Webhook wiring

GitHub webhook:
- URL: `POST /github` on bot runtime service, or `POST /webhooks/github` on Cloudflare gateway.
- Events: `pull_request`; `ready_for_review` and VeraQA `review_requested` enqueue Vera QA and queue `vera-qa-gate` when head SHA is present.

Linear webhook:
- URL: `POST /linear` on runtime service, or `POST /webhooks/linear` on Cloudflare gateway.
- Events: issue updated/state changed, label updates, comment created. `issue_in_review` / `issue_status_changed` with status `In Review` enqueues Vera QA; `QA_RESULT=PASSED|FAILED|OVERRIDE|ACTION_REQUIRED` plus `PR_URL=` and `HEAD_SHA=` updates `vera-qa-gate`.

## 4) Cloudflare gateway (optional)

```bash
cd $WORKSPACE/bitpod-tools/linear/cloudflare
wrangler deploy
```

Set Worker secrets/vars:
- `BOT_ORIGIN`
- `GITHUB_WEBHOOK_SECRET`
- `LINEAR_WEBHOOK_SECRET`

## 5) Safety checks before live mode

1. Confirm dry-run action output first.
2. Confirm PR comments are posted by automation actor (not CJ).  
3. Keep `VERA_QA_DISPATCH_ENABLED=false`, `VERA_QA_GATE_LIVE_ENABLED=false`, and `LINEAR_LIVE_EXECUTOR_ENABLED=false` until the controlled rollout window.
4. Enable `VERA_QA_DISPATCH_ENABLED=true` only after a dry-run event shows the exact Hermes `vera` Kanban card that would be created.
5. Enable `VERA_QA_GATE_LIVE_ENABLED=true` only when Vera QA Gate app credentials are injected from a secret store and the target PR head SHA is known.
6. Keep `LINEAR_LIVE_EXECUTOR_ENABLED=false` until the expected Linear actor is configured.
7. Turn each kill switch on only for a controlled rollout window.
8. If logs or traces contain `LINEAR ACTOR WRONG`, turn the kill switch off and fix identity before continuing.
9. Confirm trace artifacts are being written:
   - runtime events: path from `RUNTIME_TRACE_PATH`
   - service action traces: path from `TRACE_STORE_PATH`

## 6) Live Linear rollout path

Use [linear_live_executor_rollout_path_v1.md](./linear_live_executor_rollout_path_v1.md) for the guarded BIT-505 / BIT-559 rollout. The only supported Linear live actions are `comment`, `set_status`, and `set_label`; all other Linear actions fail closed.

## 7) Incident fallback

If external integration is degraded:
- keep bot in dry-run
- keep CI/tests running
- collect action output JSON as evidence
- defer live mutation until upstream stability is restored
