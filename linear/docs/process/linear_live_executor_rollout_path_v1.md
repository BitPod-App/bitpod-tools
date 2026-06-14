# Linear Live Executor Rollout Path v1

Status: guarded rollout path  
Scope: `bitpod-tools/linear` runtime service live Linear mutations

## Purpose

This is the first live Linear executor path for the bot runtime. It exists only to unblock the minimal BIT-505 / BIT-559 action set while preserving fail-closed behavior.

Supported Linear actions:

- `comment`
- `set_status`
- `set_label`

Everything else must remain blocked until a later, reviewed rollout expands the action set.

## Safety model

Live Linear execution requires all of the following:

1. Service live mode is enabled (`DRY_RUN=false`).
2. Governance allows the action class.
   - Class A comments are allowed by the current policy matrix.
   - Class B status/label mutations require an exact rollout allowlist entry in `LINEAR_GUARDED_ACTION_ALLOWLIST`; they are not silently promoted by the executor.
   - Exception: Vera QA result sync actions carrying `source_event=vera_qa_completed` may set only `In Review - QA Gate/qa-passed`, `In Review - QA Gate/qa-failed`, `Delivered`, or `In Progress` without a per-ticket allowlist. This is the permanent Vera gate result path, not a general Linear mutation bypass.
3. The hard Linear executor kill switch is explicitly on: `LINEAR_LIVE_EXECUTOR_ENABLED=true`.
4. `LINEAR_OAUTH_CLIENT_ID` / `LINEAR_OAUTH_CLIENT_SECRET` are present in machine-local runtime configuration so the executor can mint Linear OAuth app-actor tokens with `client_credentials`. `LINEAR_OAUTH_ACCESS_TOKEN` is a short-lived emergency fallback only; `LINEAR_API_KEY` remains a legacy personal-script fallback only and should not be preferred for agent/app actors.
5. At least one expected actor field is configured:
   - `LINEAR_EXPECTED_ACTOR_ID`
   - `LINEAR_EXPECTED_ACTOR_NAME`
   - `LINEAR_EXPECTED_ACTOR_EMAIL`
6. The authenticated Linear `viewer` matches every configured expected actor field.

If any condition fails, the action is recorded as blocked in the service trace.

## Attribution check

Before each live mutation batch, the executor queries the authenticated Linear viewer. If the viewer does not match the configured expected actor, execution stops with a trace detail beginning:

```text
LINEAR ACTOR WRONG:
```

That phrase is intentional. Operators should search traces and logs for `LINEAR ACTOR WRONG` during rollout. If it appears, keep the kill switch off and fix the token/app identity before continuing.

## Environment variables

```bash
DRY_RUN=false
LINEAR_LIVE_EXECUTOR_ENABLED=true
LINEAR_OAUTH_CLIENT_ID=...
LINEAR_OAUTH_CLIENT_SECRET=...
LINEAR_OAUTH_SCOPE='read write'
# LINEAR_OAUTH_ACCESS_TOKEN=...  # short-lived emergency fallback only
# LINEAR_API_KEY=...  # legacy fallback only
# Optional for non-Vera controlled Class-B rollout actions only:
# LINEAR_GUARDED_ACTION_ALLOWLIST=linear:set_status:BIT-505
LINEAR_EXPECTED_ACTOR_ID=...
# Optional additional checks:
LINEAR_EXPECTED_ACTOR_NAME=...
LINEAR_EXPECTED_ACTOR_EMAIL=...
TRACE_STORE_PATH=/tmp/bitpod_linear_runtime_trace.jsonl
```

Do not store these values in tracked repo files.

## Rollout sequence

1. Run the test suite:

   ```bash
   cd $WORKSPACE/bitpod-tools
   python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_linear_executor.py linear/tests/test_e2e_flow.py
   ```

2. Start in dry-run and verify generated actions are correct.
3. Configure expected Linear actor fields from a known automation actor.
4. Turn on live service mode and the Linear kill switch only for a controlled window.
5. Execute a single comment action first and verify:
   - service trace outcome is `executed` and includes the matched `actor_id` / `actor_name`
   - Linear comment attribution is the automation actor, not CJ
   - no `LINEAR ACTOR WRONG` trace exists
6. Only after comment attribution is verified, set the narrowest `LINEAR_GUARDED_ACTION_ALLOWLIST` value needed for non-Vera governed status or label proofs, for example `linear:set_status:BIT-505`. Do not use wildcards. Do not use this allowlist for Vera QA result sync; Vera result sync has its own source-event-limited policy path.
7. Turn `LINEAR_LIVE_EXECUTOR_ENABLED=false` immediately after the controlled window unless the operator explicitly keeps it open.

## Rollback

Set:

```bash
LINEAR_LIVE_EXECUTOR_ENABLED=false
```

or return to:

```bash
DRY_RUN=true
```

Then preserve `TRACE_STORE_PATH` evidence and add a concise Linear/manual rollout note describing what happened, what was executed, and whether attribution matched.
