# local-codex App State Tolerance Note v1

Date: 2026-03-15  
Primary issues:
- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)
- [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node)

## Purpose

Make an explicit decision about stale Codex desktop app-state so it stops behaving like an undefined blocker.

## Verified current problem

`/Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex-global-state.json` still contains stale legacy values such as:

- environment label `bitpod`
- repo map `cjarguello/bitpod`
- old sidebar path `/Users/cjarguello/bitpod-app/tools`

## Decision

Treat this file as tolerated app-state residue, not canonical workspace truth.

## Rules

- do not infer current workspace truth from `.codex-global-state.json` without re-verifying
- do not hand-edit the file just to make it look clean
- prefer natural refresh by the Codex app when possible
- only reset or delete app-state in a deliberate pass if there is a concrete operational reason

## T3 implication

This file may remain stale without blocking T3, provided that:

1. active repos/docs no longer rely on its stale values
2. the team explicitly treats it as app residue rather than workspace canon
3. machine-transition work uses the explicit branch/path contracts now recorded elsewhere

## Escalation condition

Re-open this as an active blocker only if:

- the stale app-state causes incorrect runtime behavior
- it keeps resurfacing as an authority source in current work
- or the Mac Mini transition requires a clean exported app-state baseline
