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
| `~/.agents` mirror still exists at all | `PASS_WITH_LIMITS` | home-directory paths still exist, but only as compatibility symlinks to `local-codex`; the duplicate source-of-truth problem is removed | retire the compatibility shim only once runtime/session dependence is honestly clear |
| Final canonical branch strategy | `PASS_WITH_LIMITS` | final forever strategy is not done, but the exact pre-rename execution branch map is now recorded in `pre_rename_execution_branch_map_v1.md` | use the explicit pre-rename branch map for Mac Mini work until later normalization |
| Stale local Codex app metadata | `PASS_WITH_LIMITS` | `.codex-global-state.json` has already been narrowed: stale thread root hints and the old dead `tools` sidebar entry were removed, the active workspace roots are correct, and the remaining live drift appears to be the app-managed `environment.repo_map` metadata for `cjarguello/bitpod` plus normal prompt-history retention | tolerate for T3 unless strict local app-state cleanliness is required, or perform a stronger reset only in a fresh-session window |
| `local-trash-delete` still physically large | `SOFT_FAIL` | quarantine is no longer active, but still contains large cooling-period residue | treat as hygiene unless user explicitly wants stronger purge posture before T3 |
| Linear truth for T3 | `PASS_WITH_LIMITS` | [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename) is now `In Progress`, which matches reality better than backlog; it still needs an honest final closeout call later | keep ticket status/comments aligned with actual cleanup state until final T3 decision |
| Mac Mini boundary executed | `NOT_YET` | [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) is intentionally blocked pending T3 | start only after T3 is honestly passed |
| Repo/package naming drift | `DEFERRED_FAIL` | naming normalization is still intentionally deferred | keep out of the T3 pass unless explicitly promoted back into scope |

## Important nuance

- T3 does **not** require `local-trash-delete` to be empty.
- T3 **does** require that quarantine is no longer part of the active operating surface.
- T3 can still fail honestly even if the active workspace is materially cleaner than before.

## Suggested execution order

1. Retire the `~/.agents` compatibility shim in a fresh pass once runtime/session dependence is honestly clear.
2. Keep using the explicit pre-rename execution branch map until later normalization replaces it.
3. If strict T3 cleanliness is required, use the restart-safe app-state reset plan in a fresh session instead of hand-editing live app state.
4. Keep [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename) aligned with reality instead of leaving it as stale planning state.
5. Only then unblock [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node).
