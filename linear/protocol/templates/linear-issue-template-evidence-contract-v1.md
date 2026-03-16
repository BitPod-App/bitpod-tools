# Linear Issue Template Hardening v1 (Evidence-First)

Related issue: https://linear.app/bitpod-app/issue/BIT-27/linear-issue-template-hardening-evidence-first-completion-contract
Version: v1

## Required fields for completion claims

Every "Done" claim must include:

1. `Status line`
- Current status and transition reason.

2. `Commands/UI checks`
- Exact command(s) run or explicit UI path used.

3. `Artifacts`
- Absolute path(s) to generated docs/logs/screenshots (or PR/commit links).

4. `Pass/Fail`
- Explicit pass/fail result per check.

5. `Risk / follow-up`
- Any deferred risk and next action.

## `Needs-CJ` marker guidance

Use `Needs-CJ` only when:
- action is UI-only and cannot be performed through available API/tooling,
- or action requires CJ-controlled credentials/ownership decisions.

Do not use `Needs-CJ` for work Codex can execute directly.

When used, include:
- exact UI path
- exact expected setting/value
- one verification command/output to run afterward

## Example evidence comment format

```md
Execution update:

Status: In Progress -> Done
Transition reason: all required checks passed.

Commands/UI checks:
- `gh api /orgs/BitPod-App --jq '{two_factor_requirement_enabled,members_can_delete_repositories}'`
- GitHub UI: Org Settings -> Security -> Require 2FA = enabled

Artifacts:
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-23/github-org-baseline-evidence-2026-03-06.md`
- [BitPod-App/bitpod-tools PR #6](https://github.com/BitPod-App/bitpod-tools/pull/6)

Pass/Fail:
- Org 2FA required: PASS
- Member repo deletion blocked: PASS

Risk / follow-up:
- `code_security` feature is plan-gated; tracked separately and not blocking this issue.
```

## Suggested default issue description headings

- Objective
- Scope
- Required outputs
- Verification plan
- Rollback note

## Enforcement note

- If a completion comment omits required evidence fields, status must not move to `Done`.
- If uncertain, set/keep `In Review` and request missing evidence.
