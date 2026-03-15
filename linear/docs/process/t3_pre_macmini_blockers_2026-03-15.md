# T3 Pre-Mac-Mini Blockers — 2026-03-15

Primary issues:
- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)
- [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node)

## Purpose

Record the remaining objections that still prevent an honest T3 pass before the Mac Mini lane proceeds.

This file exists because "mostly clean" is not specific enough for the current standard.

## Current blocker matrix

| Concern | Status | Current read | Next action |
|---|---|---|---|
| Active `~/.agents` dependence in live repos | `PASS` | `sector-feeds` no longer treats `~/.agents` as canonical, and its Taylor skill check now points to `local-codex` | keep removing active repo/runtime dependence where found |
| `~/.agents` mirror still exists at all | `FAIL` | home-directory mirror still exists and may still feel like hidden dependency residue | decide whether to quarantine or retire the mirror after verifying no active runtime still requires it |
| Final canonical branch strategy | `PASS_WITH_LIMITS` | final forever strategy is not done, but the exact pre-rename execution branch map is now recorded in `pre_rename_execution_branch_map_v1.md` | use the explicit pre-rename branch map for Mac Mini work until later normalization |
| Stale local Codex app metadata | `FAIL` | `local-codex/.codex-global-state.json` still says `bitpod`, `cjarguello/bitpod`, and old sidebar paths like `/Users/cjarguello/bitpod-app/tools` | decide whether to reset/refresh or explicitly accept as non-blocking app residue |
| `local-trash-delete` still physically large | `SOFT_FAIL` | quarantine is no longer active, but still contains large cooling-period residue | treat as hygiene unless user explicitly wants stronger purge posture before T3 |
| Linear truth for T3 | `FAIL` | [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename) must not remain stale/backlog theater if it is the real gate | keep ticket status/comments aligned with actual cleanup state |
| Mac Mini boundary executed | `NOT_YET` | [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) is intentionally blocked pending T3 | start only after T3 is honestly passed |
| Repo/package naming drift | `DEFERRED_FAIL` | naming normalization is still intentionally deferred | keep out of the T3 pass unless explicitly promoted back into scope |

## Important nuance

- T3 does **not** require `local-trash-delete` to be empty.
- T3 **does** require that quarantine is no longer part of the active operating surface.
- T3 can still fail honestly even if the active workspace is materially cleaner than before.

## Suggested execution order

1. Retire or quarantine `~/.agents` as a real mirror rather than only calling it legacy.
2. Keep using the explicit pre-rename execution branch map until later normalization replaces it.
3. Decide whether stale Codex app metadata should be reset or explicitly tolerated.
4. Keep [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename) aligned with reality instead of leaving it as stale planning state.
5. Only then unblock [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node).
