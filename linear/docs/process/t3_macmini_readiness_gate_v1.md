# T3 to Mac Mini / NemoClaw Readiness Gate v1

Date: 2026-03-22
Primary issues:
- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)
- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)

## Purpose

Define the cleanup gate that permits Mac Mini bootstrap work to start.

This note is only about the T3 readiness gate. It is not the operator pack and
it is not the architecture decision record.

The active operating defaults and boundary guardrails are recorded in
`linear/docs/process/execution_hq_architecture_decisions_v1.md`.
The concrete operator sequence is recorded in
`linear/docs/process/execution_hq_operator_pack_v1.md`.

## Core Rule

- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
  stays blocked until a full forced `cleanup-audit T3` honestly passes with
  `result=PORCELAIN`.
- Once that pass is verified, the remaining blockers are execution/bootstrap
  work, not more MacBook-side cleanup by default.
- T3 pass does not require `local-trash-delete` to be empty.
- T3 pass does require `local-trash-delete` to no longer be part of the active
  operating surface.
- T3 is the authoritative cleanup tier in the active runbook.

## T3 Pass Checklist

Mark `T3_READY_FOR_MAC_MINI=true` only if all are true:

1. Active root workspace is structurally clean.
2. Useful repo truth is preserved.
3. Hidden local operating state is mapped strongly enough to rebuild from
   GitHub.
4. `local-trash-delete` is no longer active.
5. Mac Mini scope is separated from later rename work.
6. Transition model is explicit:
   - MacBook is the control console
   - Mac Mini is Execution HQ
   - GitHub is the canonical sync source

## Verified Current Read on 2026-03-22

The MacBook-side gate was re-verified on 2026-03-22 with a full forced
`cleanup-audit T3` result of:

```text
Audit Control | T3 Cleanup
Timestamp: 2026-03-22T08:52:28Z
- result=PORCELAIN
- overall=VERIFIED
- repos_scanned=7
- repo_findings=none
- stale_local_codex_branches=0
- stale_remote_codex_branches=0
- open_pull_requests=0
- local_workspace_status=PASS
```

Truthful interpretation:

- the MacBook-side cleanup gate is satisfied
- bootstrap work may proceed
- if any issue relation still suggests the T3 gate is blocking, treat that as
  stale relation state until Linear blocker cleanup catches up

## Operational Interpretation

If the verified pass above remains materially true:

- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)
  is no longer the meaningful blocker for machine transition work
- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
  may move forward into account, workspace, runtime, and smoke-proof execution

If the workspace changes materially before bootstrap:

- rerun the full forced `cleanup-audit T3`
- record the exact failing criterion instead of speaking vaguely about more
  cleanup
