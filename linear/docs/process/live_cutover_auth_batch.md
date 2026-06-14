# Linear Bot v1 Live Cutover: Auth Batch

Use this as a single approval batch when enabling live mode.

## GitHub

- Create/confirm GitHub App for automation actions.
- Required permissions:
  - Pull requests: Read/Write (comments)
  - Contents: Read
  - Metadata: Read
- Install app on target repos (at least `BitPod-App/bitpod-tools` for bootstrap).
- Provide:
  - `VERA_QA_GATE_GITHUB_APP_ID`
  - `VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID`
  - `VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY`
  - `VERA_QA_GATE_WEBHOOK_SIGNING_SECRET`

## Linear

- Create/confirm Linear OAuth app or service actor token for bot actions.
- Required scopes:
  - read issues/projects/labels/comments
  - write issues/status/labels/comments
- Provide:
  - `LINEAR_OAUTH_CLIENT_ID` / `LINEAR_OAUTH_CLIENT_SECRET` from the approved Linear OAuth app actor so the runtime mints tokens with `client_credentials`; `LINEAR_OAUTH_ACCESS_TOKEN` is short-lived emergency fallback only and `LINEAR_API_KEY` is legacy personal-script fallback only
  - `LINEAR_WEBHOOK_SECRET` or the shared `VERA_QA_GATE_WEBHOOK_SIGNING_SECRET` when both webhook sources are intentionally configured to use the same signing secret

## Cloudflare (if gateway enabled)

- Worker env/secrets:
  - `BOT_ORIGIN`
  - `GITHUB_WEBHOOK_SECRET`
  - `LINEAR_WEBHOOK_SECRET`
- Ensure route points to `runtime.bitpod.app` or chosen host.

## Verification bundle (single pass)

1. Trigger GitHub PR opened sample on live endpoint.
2. Trigger Linear QA comment sample on live endpoint.
3. Confirm actor attribution:
   - GitHub comment author = app/bot identity
   - Linear mutation author = app actor (not CJ)
4. If any action is attributed as CJ, stop and revert to dry-run.
