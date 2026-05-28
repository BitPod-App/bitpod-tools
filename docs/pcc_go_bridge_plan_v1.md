# PCC v2/3 GO Bridge Plan v1

**Owner:** Taylor01 (Lead PM / T01 Agents Doctor)
**Created:** 2026-05-28
**Related:** BIT-463, BIT-465, BIT-466, BIT-467, BIT-468, BIT-469
**Status:** Design complete — implementation pending BIT-457 resolution

---

## Purpose

This document is the durable reference for the Prompt Command Center v2/3 safe GO-to-Codex bridge. It covers:

1. **Security and permission model** (satisfies BIT-465 AC)
2. **Validated launch request contract** (satisfies BIT-466 AC)
3. **UI state machine and audit log plan** (satisfies BIT-468 AC)
4. **End-to-end verification checklist** (satisfies BIT-469 AC)

The bridge already has a working implementation in `taylor01-runtime` at
`apps/prompt-command-center/src/app/api/launch/route.ts`. This document formalizes the security contract and acceptance criteria that gate enabling the bridge beyond fallback-only mode.

---

## Prerequisite

**BIT-457 must be resolved before any non-fallback mode is enabled.**

The Tailscale `/dashboard` serve route must be removed and permissions minimized before the GO bridge can expand its attack surface. See BIT-457 for the specific `tailscale serve --remove /dashboard` action.

---

## Section 1: Security and Permission Model (BIT-465)

### 1.1 Operator and Host Constraints

| Constraint | Required value | Enforcement |
|---|---|---|
| OS user running the bridge | `taylor01` | Server hostname check + process ownership |
| Host | `mini-01` only | `T01_PCC_MINI_HOSTNAME` env var compared to `os.hostname()` |
| Network binding | Tailnet-private or localhost only | No `0.0.0.0` binding, no Funnel, no public IP |
| Tailscale permissions | Minimized per BIT-457 | Pre-condition, see prerequisite section |

### 1.2 Threat Model

| Threat | Mitigation |
|---|---|
| Frontend submits arbitrary prompt text for execution | Server ignores `body.prompt` for assembly. Prompt is reassembled server-side from `commandId` + `threadId` + `fields`. Frontend prompt is validated against server-assembled version — mismatch → fallback. |
| Attacker on Tailnet calls bridge endpoint directly | Operator token (`T01_PCC_OPERATOR_TOKEN`) required in `x-t01-pcc-token` header. Token is never exposed to frontend. |
| Cross-origin request forgery | `isSameOrigin()` check: `origin` header must match `host` header. |
| CWD traversal / arbitrary filesystem access | Frontend never specifies raw paths. `threadId` maps to a server-side thread registry entry (`getThread`). CWD is resolved from `process.env[thread.cwdEnv]` or `thread.defaultCwd`. |
| Launch on wrong host (macOS, cloud, dev machine) | Hostname check rejects if `os.hostname()` does not include `T01_PCC_MINI_HOSTNAME`. |
| Bridge enabled on dev/staging accidentally | `T01_PCC_BRIDGE_MODE` defaults to `"fallback"`. Bridge only activates if explicitly set to `"local-mini"` or `"ssh"`. |
| Log exfiltration of secrets or sensitive prompts | Logging posture restricts to safe fields only (see Section 1.4). |
| Runaway launch / no kill switch | Feature flag (`T01_PCC_BRIDGE_MODE=fallback`) is the immediate kill switch. Restart bridge server to apply. |
| Prompt injection via crafted thread content | Prompt is assembled from structured command spec, not from free-form thread text read at runtime. |

### 1.3 Allowed Callers

- Requests from loopback (`127.x.x.x`, `::1`) — same-machine PCC server
- Requests from Tailscale-private IP range (`100.x.x.x`) — Tailnet-only
- Requests from RFC-1918 private ranges (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`) — local LAN only

All callers must also provide a valid `x-t01-pcc-token` header matching `T01_PCC_OPERATOR_TOKEN`.

### 1.4 Denied Cases

- Any request missing or with invalid `x-t01-pcc-token` → 403 fallback
- Any request where `origin` does not match `host` → 403 fallback
- Any request from a public IP (non-private, non-loopback) → fallback
- Any request with `body.prompt` that does not match server-assembled prompt → 400 fallback
- Any request with invalid `commandId`, missing `threadId`, or validation errors → 400 fallback
- Any request when `T01_PCC_BRIDGE_MODE` is not `"local-mini"` or `"ssh"` → fallback (no error, just safe fallback)
- Any request when BIT-457 is not resolved (Tailscale `/dashboard` still active) → deploy-time block, do not set `T01_PCC_BRIDGE_MODE` until BIT-457 is done

### 1.5 Logging Posture

**Safe to log:**
- `timestamp` (ISO-8601)
- `commandId`
- `threadId` / `thread.label`
- `cwd_key` (the `thread.cwdEnv` key name, not the resolved path if it contains sensitive segments)
- `prompt_hash` (SHA-256 of assembled prompt, not the prompt text)
- `bridge_mode` (`local-mini`, `ssh`, `fallback`)
- `status` (`ok`, `validation_failed`, `mismatch`, `host_refused`, `launch_failed`, `fallback`)
- `error_class` (error type without stack trace or sensitive context)

**Never log:**
- Raw prompt text
- `T01_PCC_OPERATOR_TOKEN` value
- Resolved CWD path if it contains user tokens or sensitive segments
- Full request headers
- SSH target hostname beyond `mini-01` label

### 1.6 Rollback Path

1. Set `T01_PCC_BRIDGE_MODE=fallback` (or unset it) in the PCC server environment.
2. Restart the PCC Next.js server: `pm2 restart pcc` (or equivalent).
3. Verify the GO button returns to locked/fallback state in the UI.
4. Confirm copy/paste fallback still works end-to-end.
5. File a Linear incident ticket if the rollback was triggered by a failure.

---

## Section 2: Validated Launch Request Contract (BIT-466)

### 2.1 Request Schema (POST `/api/launch`)

```typescript
type LaunchBody = {
  commandId: CommandId;        // required — must map to a known command in server command registry
  threadId: string;            // required — must map to a known thread in server thread registry
  threadConfirmed: boolean;    // required for some commands — validates user acknowledged thread target
  speed?: Speed;               // optional — "Fast" | "Balanced" | "Thorough", default: "Balanced"
  fields?: PromptFields;       // optional — structured key/value fields for prompt assembly
  prompt: string;              // required — assembled client-side, validated against server reassembly
};
```

**Key constraint:** `body.prompt` is included by the frontend as a tamper-detection signal only. The server independently reassembles the prompt from `commandId` + `threadId` + `speed` + `fields`. If they differ, the request is rejected. The frontend cannot inject arbitrary execution content.

### 2.2 Response Schema

All responses are JSON. Shape varies by status:

```typescript
// Success (real launch)
type LaunchSuccess = {
  ok: true;
  mode: "local-mini" | "ssh";
  message: string;    // human-readable confirmation, e.g. "Codex CLI startup accepted on mini-01..."
  pid?: number;       // PID of spawned Codex process (if known at response time)
};

// Fallback (validation passed but launch not enabled or not attempted)
type LaunchFallback = {
  ok: false;
  mode: "fallback";
  message: string;              // human-readable reason
  fallbackCommand: string;      // multi-line copy/paste command for manual execution
};

// Error (validation failed — bad request)
type LaunchError = {
  ok: false;
  mode: "fallback";
  message: string;
  fallbackCommand: string;
};
```

### 2.3 HTTP Status Codes

| Condition | HTTP Status | `ok` | `mode` |
|---|---|---|---|
| Invalid JSON body | 400 | false | fallback |
| Missing commandId or threadId | 400 | false | fallback |
| Validation errors (AC failures) | 400 | false | fallback |
| Prompt mismatch | 400 | false | fallback |
| Token missing/invalid | 403 | false | fallback |
| Origin mismatch | 403 | false | fallback |
| Bridge mode is fallback | 200 | false | fallback |
| Host mismatch | 200 | false | fallback |
| CWD does not exist on host | 400 | false | fallback |
| Codex process failed at startup | 502 | false | fallback |
| Launch accepted (local-mini) | 200 | true | local-mini |
| Launch accepted (ssh) | 200 | true | ssh |

### 2.4 Server-Side Validation Rules

In execution order:

1. Parse JSON body — reject 400 if malformed.
2. Require `commandId` and `threadId` — reject 400 if missing.
3. Look up thread via `getThread(threadId)` — unknown thread IDs are rejected (registry is server-side).
4. Resolve CWD from thread registry via env var or default — CWD is never from frontend.
5. Assemble expected prompt via `assemblePrompt({ commandId, thread: thread.label, speed, fields })`.
6. Run command validation via `validateCommand({ commandId, threadConfirmed, fields })` — AC checks.
7. Reject 400 if validation errors exist.
8. Compare `body.prompt` to `expectedPrompt` — reject 400 if mismatch.
9. Check `T01_PCC_BRIDGE_MODE` — return fallback 200 if not `"local-mini"` or `"ssh"`.
10. Validate operator token and origin (gate function) — reject 403 if invalid.
11. For `local-mini`: check hostname and CWD existence, then spawn Codex.
12. For `ssh`: spawn Codex via SSH with validated prompt and CWD.

### 2.5 Bridge Modes

| Mode (`T01_PCC_BRIDGE_MODE`) | Behavior |
|---|---|
| `fallback` (default) | No launch attempted. Returns fallback command. Validation still runs. |
| `dry-run` (planned) | Full validation + prompt assembly + CWD check. Returns what would have been launched without spawning. |
| `local-mini` | Real launch via `codex exec` on the local mini-01 host. |
| `ssh` | Real launch via SSH into `T01_PCC_SSH_TARGET`. |

**Note:** `dry-run` mode is the planned next step for BIT-467. The current implementation skips directly from `fallback` to `local-mini`/`ssh`. Adding `dry-run` as an explicit mode returns a structured "would launch X in Y" response without spawning.

---

## Section 3: UI States and Audit Log Plan (BIT-468)

### 3.1 UI State Machine

```
Locked
  └─► (BIT-467 complete + T01_PCC_BRIDGE_MODE=dry-run)
        └─► Dry-run only
              └─► (BIT-469 checklist passed + T01_PCC_BRIDGE_MODE=local-mini|ssh)
                    └─► Ready to launch
                          ├─► Launch submitted
                          │     ├─► Launch accepted  (ok: true)
                          │     └─► Launch failed    (ok: false, mode: fallback)
                          └─► Copy fallback available (always)
```

### 3.2 UI State Copy (Per State)

| State | Button/label copy | Status indicator copy |
|---|---|---|
| **Locked** | `Copy prompt ↗` (only) | `GO is locked — copy/paste only` |
| **Dry-run only** | `Dry-run GO` | `Dry-run mode — validates without launching` |
| **Ready to launch** | `GO →` | `Direct launch enabled` |
| **Validating** | `Validating…` (loading) | `Checking command and thread…` |
| **Launch submitted** | (spinner) | `Sending to mini-01…` |
| **Launch accepted** | `Launched ✓` | `Codex accepted on mini-01 (PID: …)` |
| **Launch failed** | `Failed — copy fallback ↗` | `Launch failed: [message]` |
| **Prompt mismatch** | `Regenerate ↺` | `Prompt changed — regenerate before launching` |
| **Fallback returned** | `Copy prompt ↗` | `[message from server]` |

**Invariant:** Copy/paste fallback command is ALWAYS accessible regardless of state. It must never be hidden when GO is locked or failed.

### 3.3 Audit Log Fields

Each launch attempt (including fallbacks) should be logged locally in browser storage or a structured log file at a safe path on mini-01 (no cloud logging required at MVP).

**Safe to log:**

```typescript
type AuditLogEntry = {
  timestamp: string;          // ISO-8601
  commandId: string;
  threadId: string;
  threadLabel: string;
  speed: string;
  promptHash: string;         // SHA-256 hex of assembled prompt
  bridgeMode: string;         // "fallback" | "dry-run" | "local-mini" | "ssh"
  status: string;             // "ok" | "fallback" | "validation_failed" | "mismatch" | "launch_failed"
  message: string;            // server message (human-readable)
  pid?: number;               // PID if launch was accepted
  errorClass?: string;        // error type if launch failed
};
```

### 3.4 Prohibited Log Fields

The following must NEVER appear in any log entry, browser storage key, or network request:

- Assembled prompt text
- Operator token
- Resolved CWD path if it contains user-identifying segments
- Full server response headers
- SSH target beyond the `mini-01` label

---

## Section 4: End-to-End Verification Checklist (BIT-469)

No GO bridge implementation may be marked ready for `local-mini` or `ssh` mode without passing every item on this checklist.

### 4.1 Infrastructure Pre-conditions

- [ ] BIT-457 is Done: Tailscale `/dashboard` serve route removed, permissions minimized
- [ ] `T01_PCC_OPERATOR_TOKEN` is set server-side and stored in Taylor01 Runtime vault (not in `.env` committed to repo)
- [ ] `T01_PCC_BRIDGE_MODE` is explicitly set to the intended mode (not left as default)
- [ ] `T01_PCC_MINI_HOSTNAME` matches actual `os.hostname()` output on mini-01
- [ ] PCC server is running as `taylor01` on mini-01 (not cjarguello, not t01agents)
- [ ] No Funnel/public exposure confirmed: `tailscale serve status` shows no public routes for PCC port

### 4.2 Security Gate Verification

- [ ] Request without `x-t01-pcc-token` → 403 response, fallback command in body
- [ ] Request with wrong `x-t01-pcc-token` → 403 response, fallback command in body
- [ ] Request with mismatched `origin`/`host` → 403 response
- [ ] Request with public IP in `x-forwarded-for` → fallback response
- [ ] Request with tampered `prompt` (differs from server-assembled) → 400 fallback
- [ ] Request with unknown `commandId` → 400 or fallback
- [ ] Request with unknown `threadId` → error/fallback (no raw CWD accepted)
- [ ] Request with raw filesystem path in body fields → rejected or ignored (CWD comes from registry)

### 4.3 Host and CWD Verification

- [ ] Launch request on wrong hostname → fallback response with host mismatch message
- [ ] Launch request with thread whose CWD env var is unset → falls back to `thread.defaultCwd`
- [ ] Launch request with CWD that does not exist on mini-01 → 400 fallback
- [ ] Launch request with valid CWD → CWD verified to exist before spawn

### 4.4 Prompt Integrity Verification

- [ ] Server-assembled prompt matches expected output for each registered command
- [ ] Frontend `body.prompt` that differs by even one character is rejected
- [ ] `validateCommand` AC checks run before prompt comparison
- [ ] Thread confirmation requirement enforced for commands that require `threadConfirmed: true`

### 4.5 Launch Behavior Verification

- [ ] Successful `local-mini` launch: returns `ok: true`, `mode: "local-mini"`, valid `pid`
- [ ] Successful `ssh` launch: returns `ok: true`, `mode: "ssh"`, valid `pid`
- [ ] Failed spawn (binary not found): returns 502 fallback with error message, no crash
- [ ] Spawned process is detached (`unref()`): PCC server does not block waiting for Codex to exit
- [ ] Prompt is delivered to Codex via stdin, stdin closed cleanly after write

### 4.6 Fallback Invariants

- [ ] Copy/paste fallback command is in every fallback response
- [ ] Fallback command includes `cd <cwd>` and `codex exec -` instructions
- [ ] UI shows fallback command text at all times, even after launch failure
- [ ] `T01_PCC_BRIDGE_MODE=fallback` (or unset) returns fallback without error to user

### 4.7 Build and Type Safety

- [ ] `npm run typecheck` passes with no errors
- [ ] `npm run build` passes
- [ ] `npm run qa:visual` passes (or visual snapshot updated intentionally)
- [ ] No `any` types introduced in `route.ts` or related files

### 4.8 Rollback Verification

- [ ] Setting `T01_PCC_BRIDGE_MODE=fallback` and restarting server reverts to locked/fallback state
- [ ] UI correctly shows fallback/locked state after rollback
- [ ] No orphaned Codex processes remain after bridge restart
- [ ] Copy/paste fallback command still works after rollback

### 4.9 Log Hygiene Verification

- [ ] No prompt text appears in server logs
- [ ] No operator token appears in any log, header echo, or error response
- [ ] No CWD containing sensitive path segments appears in client-visible responses beyond what `buildFallbackCommand` already includes

### 4.10 Release Checklist

- [ ] All items in 4.1–4.9 checked and noted with evidence
- [ ] Linear ticket for BIT-469 moved to Done with checklist results in description
- [ ] CJ sign-off received before `T01_PCC_BRIDGE_MODE` is set to anything beyond `dry-run` in production
- [ ] Rollback procedure documented and tested (Section 1.6)

---

## Public-Safety Note

This document contains no token values, secret paths, vault IDs, operator tokens, or private IP addresses. All sensitive operational values are stored in the Taylor01 Runtime vault and injected via `op run --env-file` at server startup.
