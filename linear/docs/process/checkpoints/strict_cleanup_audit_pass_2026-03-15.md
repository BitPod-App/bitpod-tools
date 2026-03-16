# Strict Cleanup Audit Pass — 2026-03-15

Primary issues:
- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)
- [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node)

## Purpose

Record the stricter post-T3 cleanup baseline after the workspace passed a full cleanup audit by the higher "nimble and uncluttered" standard, not just the operational T3 standard.

## Result

- strict full cleanup audit: `PASS`
- operational T3: `PASS`

## Current baseline

- active repos under `/Users/cjarguello/BitPod-App` are clean on their current upstream branches
- `~/.agents` no longer exists as active mirror or compatibility shim
- `local-trash-delete/` is the default quarantine/disposal intake path
- `local-trash-delete/local-purge/` is promotion-only and remains the only approved hard-delete lane
- soft purge signals are review-only high-certainty purge-candidate signals; they do not move or delete anything automatically
- live Codex app state no longer carries stale workspace roots or stale saved workspace paths outside the current workspace
- active runtime/process docs no longer foreground retired root paths as current operating truth

## What still exists, but no longer fails the audit

- live-session prompt history in local Codex app state
- quarantined residue in `/Users/cjarguello/BitPod-App/local-workspace/local-trash-delete`
- purge-ready residue in `/Users/cjarguello/BitPod-App/local-workspace/local-trash-delete/local-purge`
- deferred naming normalization work tracked separately under [BIT-103 — Defer post-T3 naming normalization for repos, packages, and artifact paths](https://linear.app/bitpod-app/issue/BIT-103/defer-post-t3-naming-normalization-for-repos-packages-and-artifact)

## Baseline rule going forward

- any new removed local item goes to `local-trash-delete/` first
- no new item should default directly into `local-purge/`
- `local-purge/` is reached only after explicit review or a soft-purge review signal plus confirmation
- future cleanup audits should treat this note as the stricter post-cleanup baseline, not the older transitional cleanup state
