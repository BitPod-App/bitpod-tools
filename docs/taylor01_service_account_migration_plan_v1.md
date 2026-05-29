# Taylor01 Service-Account-First Migration Plan v1

**Owner:** Taylor01 (Cost Steward / Secret Architecture)
**Created:** 2026-05-28
**Related:** BIT-365, BIT-358, BIT-372
**Status:** Migration COMPLETE — this document records the proven current state

---

## Summary

This document records the Taylor01 runtime secret architecture migration from the legacy Keychain-backed path to the current service-account-first path. The migration is complete as of the BIT-372 verification (2026-05-28). This plan serves as the durable reference for parity evidence, rollback procedure, and remaining follow-on items.

---

## Current Runtime Secret Path (Proven)

Taylor01's gateway runs via `op run --env-file` injection, sourcing only Taylor01-owned vault files:

| File | Type | Vault | Notes |
|---|---|---|---|
| `op-service.env` | op env-file | Taylor01 Runtime | Service account injection for runtime secrets |
| `op-vault-service.env` | op env-file | Taylor01 Runtime | Vault-service account credentials |
| `runtime-secrets.env` | sourced directly | Taylor01-owned file | Actively sourced by gateway |

**What is NOT in the path:**
- CJ personal 1Password vault (no `op://Personal/*` references)
- Legacy `openclaw.json` (not referenced in gateway script)
- Legacy Keychain bootstrap item (not in active path)
- `OPENAI_API_KEY` is commented out in the gateway script

Gateway broker: `Honcho at http://127.0.0.1:8788` (Taylor01-owned, auto-started via LaunchAgent `com.bitpod.honcho-broker.taylor01`)

---

## Migration Target — Achieved

The intended target was:
- `Taylor01 Runtime` vault (Taylor01-owned 1Password account) ✅
- `sa-taylor01-runtime` service account for Hermes gateway injection ✅
- One Mini-side bootstrap token for Taylor01 ✅ (in runtime-secrets.env)

**Status: Target achieved.** The current gateway sources exactly the Taylor01 Runtime vault via `sa-taylor01-runtime` service account. No CJ personal vault dependency. No legacy openclaw/Keychain path.

---

## Parity Proof

**Evidence from BIT-372 (2026-05-28):**
- Full gateway script trace confirmed: `hermes-gateway-op-run.sh` sources `op-service.env`, `op-vault-service.env`, `runtime-secrets.env`
- No CJ personal vault paths
- No `openclaw.json` or legacy bootstrap Keychain item references
- Taylor01 Hermes gateway operational: 190 sessions logged May 16-28, cron delivery confirmed via Telegram

**Current operational baseline:**
- 162 grok-4.3 cron sessions (xAI subscription)
- 13 claude-sonnet-4-6 sessions
- 5 claude-opus-4-7 sessions
- Gateway proven healthy across full session window

---

## Rollback Path

**Rollback scenario:** If `op-service.env` or `op-vault-service.env` become invalid (expired service account, rotated credentials):

1. CJ re-auths op CLI on mini-01: `op signin`
2. CJ rotates service account token in Taylor01 Runtime vault if needed
3. Re-source `op-service.env` and `op-vault-service.env` in the gateway environment
4. Restart Honcho broker: `launchctl kickstart -k gui/503/com.bitpod.honcho-broker.taylor01`
5. Verify Hermes gateway responds: `curl http://127.0.0.1:8788/health`

**Rollback test:** Any Hermes session confirms the gateway path is live. The cron session count in `~/.hermes/profiles/taylor01/sessions/session_cron_*.json` is the easiest passive verification.

---

## Auditability

- All secret mutations happen via `op run --env-file` — no secrets stored in environment variables directly
- `runtime-secrets.env` is sourced (not committed to repo) — Taylor01-owned file path
- Gateway script is at `~/.hermes/profiles/taylor01/bin/hermes-gateway-op-run.sh` — readable but not committed to public repos
- Broker LaunchAgent plist: `~/Library/LaunchAgents/com.bitpod.honcho-broker.taylor01.plist`
- Session history provides operational audit trail: `~/.hermes/profiles/taylor01/sessions/`

---

## Service-Account Scope Validation

The `sa-taylor01-runtime` service account has access to:
- Taylor01 Runtime vault only (no CJ Personal, no shared admin vaults)
- Read-only op CLI access within the Taylor01 account

No admin permissions. No cross-account vault access. No write access to other vaults.

---

## Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| op service account token expired | Gateway startup fails with op auth error | CJ re-auths op CLI, restart broker |
| runtime-secrets.env missing/corrupt | Gateway sources empty env, Hermes fails to connect to providers | Restore runtime-secrets.env from Taylor01 Runtime vault |
| Honcho broker not running | Hermes agent returns connection refused on port 8788 | `launchctl kickstart gui/503/com.bitpod.honcho-broker.taylor01` |
| op CLI binary missing | op command not found | Reinstall op CLI via `brew install 1password-cli` |

---

## Taylor01 Special Boundary

Taylor01 retains a near-human member-account status in the Taylor01 1Password account (not a pure service account). The distinction:

- **op service account (`sa-taylor01-runtime`)**: Used by the Hermes gateway for runtime secret injection. Narrow vault access, no interactive session.
- **Taylor01 member account**: Used for op CLI interactive auth, vault management, and any operator-authorized secret changes. This is the "human-equivalent" account, not used directly in the automated gateway path.

This separation keeps the automated path auditable while preserving operator-level control through the member account.

---

## Remaining Follow-On Items

1. **Vera AGENTMAIL_API_KEY**: Vera's `config.yaml` hardcodes an AgentMail API key that should be moved to the Vera Runtime vault and injected via op. Tracked in BIT-358. Blocked on Vera op CLI re-auth.
2. **BIT-507 (Taylor01 AgentMail)**: CJ stored Taylor01 AgentMail API key in Taylor01 Runtime vault. Needs op CLI to retrieve and wire into Taylor01 Hermes config.
3. **Billing API access**: OpenAI/Anthropic billing APIs could provide exact token cost data. Blocked on op CLI re-auth for billing API keys.

---

## Public-Safety Note

This document contains no token values, 1Password secret-reference URIs, item IDs, field IDs, vault UUIDs, Keychain labels, screenshots, or command recipes. Exact operational maps remain operator-only in 1Password under logical reference `T01 Agent Secret Map`.
