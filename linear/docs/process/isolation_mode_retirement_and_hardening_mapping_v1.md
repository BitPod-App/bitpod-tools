# Isolation Mode Retirement and Hardening Mapping v1

Status: Retained baseline (inactive by default)  
Primary issue: [BIT-74 — Execute post-bootstrap local scope hardening window after migration closeout](https://linear.app/bitpod-app/issue/BIT-74/execute-post-bootstrap-local-scope-hardening-window-after-migration)

## Objective

Make the current truth explicit:

- BitPod Isolation Mode v1 should not be revived as an active feature in its old form
- the useful intent should be folded into real hardening and runtime-boundary work instead

## Verified current state

Policy artifacts still exist:

- `$WORKSPACE/local-workspace/local-codex/policy/isolation/enforcement_state.json`
- `$WORKSPACE/local-workspace/local-codex/policy/isolation/violation_queue.json`

Current state is dormant:

- `enforcement_active: false`
- empty violation queue
- last updated 2026-03-04

Last known implementation exists only in quarantined legacy paths:

- `$WORKSPACE/local-workspace/local-trash-delete/bitpod/scripts/isolation_ctl.py`
- `$WORKSPACE/local-workspace/local-trash-delete/bitpod/tools/isolation/cli.py`
- `$WORKSPACE/local-workspace/local-trash-delete/bitpod/tools/isolation/runtime.py`

## Retirement decision

Isolation Mode v1 is retired as an active operating feature.

Reasons:

1. it is not an active verified protection system
2. it depends on quarantined legacy `bitpod` paths
3. reviving it as-is would reintroduce obsolete local queue/enforcement mechanics
4. OpenClaw or future operator surfaces should rely on explicit runtime contracts and hardening boundaries, not this dormant legacy scaffold

## Preserve the intent, not the feature

Useful ideas worth preserving:

- strong scope boundaries
- fail-closed behavior for unsafe actions
- explicit approval thresholds
- auditability

Those ideas already fit better under:

- hardening runbooks
- governance policy
- runtime portability and adapter boundaries

They should not continue as a separate legacy queue/enforcement product inside local state.

## Mapping to current canon

### Strong local boundary / least privilege

Use:

- [post_bootstrap_hardening_runbook_v1.md](./post_bootstrap_hardening_runbook_v1.md)

### Approval thresholds and destructive-action controls

Use:

- governance policy and approval-threshold artifacts already established in the Bootstrap work

### Portable runtime / adapter boundary

Use:

- [taylor01_boundary_map_v1.md](./taylor01_boundary_map_v1.md)
- [taylor01_coupling_log_v1.md](./taylor01_coupling_log_v1.md)

## Rule for future work

If OpenClaw or another operator surface later needs stronger isolation:

- do not resurrect Isolation Mode v1 directly
- define the exact control needed
- implement it in an approved active path
- verify it in the current runtime/host model

## Authority note

This file is retained as an explanatory mapping, not as an active operating
policy. Current authority lives in the active policy registry and the approved
hardening/runtime boundary docs.

## Allowed remaining legacy state

The dormant policy files and skill may remain temporarily as historical inspection aids.

They should not be presented as active protection.
