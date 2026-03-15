# Local Codex App-State Reset Plan v1

Issue: [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)

## Purpose

Provide a restart-safe procedure for resetting local Codex desktop app state without guessing mid-session or corrupting active runtime state.

## Why this exists

The live local app-state file:

- `/Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex-global-state.json`

is actively rewritten by the desktop app. It still contains stale migration-era fields such as:

- environment label `bitpod`
- repo metadata for `cjarguello/bitpod`
- historical thread root hints for `/Users/cjarguello/bitpod-app/bitpod`

The active workspace roots are already current:

- `/Users/cjarguello/bitpod-app`

So the remaining problem is not workspace breakage. It is stale UI/app metadata.

## Current rule

- Do not hand-edit or remove `.codex-global-state.json` during an active session.
- Reset or regenerate it only in a fresh session window.

## Reset window prerequisites

1. No active Codex work that depends on restoring the current desktop thread state.
2. Current workspace changes committed or otherwise intentionally preserved.
3. User accepts that recent local UI history, pinned thread state, and historical root hints may be lost.

## Safe reset procedure

1. Close the active Codex desktop session or app window cleanly.
2. Backup the current file to a dated local-only path.
3. Reopen Codex with the same workspace root:
   - `/Users/cjarguello/bitpod-app`
4. Let Codex regenerate the file naturally.
5. Verify the regenerated file no longer points at:
   - `/Users/cjarguello/bitpod-app/bitpod`
   - `/Users/cjarguello/bitpod-app/tools`
   - `cjarguello/bitpod`
6. If regeneration is worse or breaks expected desktop behavior, restore from backup.

## Verification checklist

- `active-workspace-roots` contains only `/Users/cjarguello/bitpod-app`
- `electron-saved-workspace-roots` contains only `/Users/cjarguello/bitpod-app`
- no stale `thread-workspace-root-hints` remain for `/Users/cjarguello/bitpod-app/bitpod`
- no stale repo metadata remains for `cjarguello/bitpod`
- no stale sidebar or tool path references remain for `/Users/cjarguello/bitpod-app/tools`

## T3 interpretation

- Before reset: tolerated residue, but still a cleanliness objection
- After successful reset: this blocker can be treated as resolved for T3

## Non-goals

- This does not rename repos or package identifiers.
- This does not affect Git history, workspace files, or `local-trash-delete`.
- This does not unblock [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) by itself; it only removes one remaining T3 cleanliness concern.
