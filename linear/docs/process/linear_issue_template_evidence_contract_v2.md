# Linear Issue Template Hardening v2 (Evidence + Taylor01 Portability)

Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Supersedes: `linear_issue_template_evidence_contract_v1.md` for active use when the portability gate applies
Version: v2

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

## Taylor01 Portability Check (required when relevant)

For issues touching agents, workflows, process docs, workspace policy, or tool integrations, also include:

- `T01_LAYER`: `core | policy | adapter | bitpod-embedding | mixed`
- `T01_SPECIFICITY`: `portable | bitpod-specific | mixed`
- `T01_COUPLING`: short note on what remains too coupled
- `T01_ACTION`: `keep-local | move-later | create-generic-version-now`

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
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/github_org_baseline_evidence_2026-03-06.md`
- [PR #6](https://github.com/BitPod-App/bitpod-tools/pull/6)

Pass/Fail:
- Org 2FA required: PASS
- Member repo deletion blocked: PASS

T01_LAYER: adapter
T01_SPECIFICITY: mixed
T01_COUPLING: evidence contract still uses BitPod-specific artifact paths
T01_ACTION: move-later

Risk / follow-up:
- `code_security` feature is plan-gated; tracked separately and not blocking this issue.
```

## Suggested default issue description headings

- Objective
- Scope
- Required outputs
- Verification plan
- Rollback note
- Taylor01 Portability Check (when relevant)

## Enforcement note

- If a completion comment omits required evidence fields, status must not move to `Done`.
- If a relevant issue omits the Taylor01 portability block, status must not be treated as decision-complete.
- If uncertain, set/keep `In Review` and request missing evidence.

