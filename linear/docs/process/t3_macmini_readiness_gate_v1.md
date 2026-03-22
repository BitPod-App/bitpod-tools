# T3 to Mac Mini / NemoClaw Readiness Gate v1

Date: 2026-03-15  
Primary issues:
- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)
- [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node)

## Purpose

Define the simple gate that turns T3 cleanup truth into permission to start the Mac Mini / NemoClaw rollout work.

This is meant to reduce re-litigation, not add a new architecture lane.

The explicit operating defaults and boundary guardrails that govern this rollout are recorded in `linear/docs/process/execution_hq_architecture_decisions_v1.md`.

## Core rule

- [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) stays blocked until a full forced `cleanup-audit T3` honestly passes with `result=PORCELAIN`.
- T3 pass does **not** require `local-trash-delete` to be empty.
- T3 pass does require `local-trash-delete` to no longer be part of the active operating surface.
- T3 is the only authoritative cleanup tier in the active runbook.
- Local-workspace checks are included in T3 by default.
- Do not introduce `T4` cleanup language unless a new active cleanup contract explicitly adds it.

## T3 pass checklist

Mark `T3_READY_FOR_MAC_MINI=true` only if all are true:

1. Active root workspace is structurally clean.
   - No ambiguous legacy top-level working roots remain active.
   - Active repos plus `.github` and `local-workspace` are the intentional root shape.

2. Useful repo truth is preserved.
   - Useful local repo state is on GitHub branches or explicitly documented as local-only.
   - Canonical repo identity is clear enough that the Mac Mini will clone from the cleaned GitHub state, not from retired local roots.

3. Hidden local operating state is mapped.
   - checked-in repo state and root policy surfaces are truthful enough to rebuild from GitHub
   - no active machine-state dependency still requires copying old local runtime state into the Mac Mini bootstrap

4. `local-trash-delete` is no longer active.
   - Nothing in `local-trash-delete` is still required by the live workspace.
   - Remaining disposal references are policy, audit, or historical evidence only.

5. Mac Mini scope is separated from later rename work.
   - Repo/package/artifact rename work remains deferred.
   - The Mac Mini setup is allowed to proceed from the current truthful state without waiting for naming normalization.

6. Transition model is explicit.
   - MacBook is treated as the control console, not the new execution node.
   - Mac Mini is treated as Execution HQ.
   - NemoClaw/OpenShell is the intended runtime layer.
   - GitHub is the canonical sync source for the rebuilt Mac Mini workspace.

## Operational interpretation

If the checklist passes:

- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename) can be treated as no longer blocking machine transition work.
- [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) may move forward.
- `local-trash-delete` remains the inactive disposal lane, not a transition blocker.

If the checklist does not pass:

- keep [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) blocked
- record the exact failing criterion instead of speaking vaguely about “more cleanup”

## Current read on 2026-03-15

- `Verified`: active root workspace is materially clean.
- `Verified`: useful repo state has been preserved to GitHub branches.
- `Verified`: machine-state ambiguity is low enough that GitHub can serve as the clean bootstrap source.
- `Verified`: `local-trash-delete` no longer appears to be part of the active operating surface.
- `Verified`: rename work is already deferred separately under [BIT-103 — Defer post-T3 naming normalization for repos, packages, and artifact paths](https://linear.app/bitpod-app/issue/BIT-103/defer-post-t3-naming-normalization-for-repos-packages-and-artifact).

Based on that read, T3 should be judged mostly by truthfulness and transition safety, not by whether the disposal lane has been physically emptied.
