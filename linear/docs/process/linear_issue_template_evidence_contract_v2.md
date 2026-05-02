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

6. `PR-to-Linear closeout check` (required when a GitHub PR or Linear normalization is involved)
- GitHub PR link(s) using `linear_link_reference_policy_v1.md` format.
- Linear issue link(s) using canonical full-title format.
- Project scope check: correct project, standalone issue, or explicit blocker if tooling cannot remove a wrong project.
- Issue Type decision: evidence-based selection or correction using `linear_issue_type_decision_guide_v1.md`.
- Status class check: implementation, docs/design/audit, or future/unstarted.
- Label check: finalized labels applied only to finalized items; future items do not receive completion labels.
- Bidirectional linking check: PR comment plus Linear issue comment/link verified, with no duplicate link-spam.

## Taylor01 Portability Check (required when relevant)

For issues touching agents, workflows, process docs, workspace policy, or tool integrations, also include:

- `T01_LAYER`: `core | policy | adapter | bitpod-embedding | mixed`
- `T01_SPECIFICITY`: `portable | bitpod-specific | mixed`
- `T01_COUPLING`: short note on what remains too coupled
- `T01_ACTION`: `keep-local | move-later | create-generic-version-now`

If portability is intentionally deferred for now, also include:

- `T01_BYPASS`: `none | temporary-coupling`
- `T01_BYPASS_REASON`
- `T01_REVIEW_TRIGGER`

Default expectation:

- use `T01_ACTION: create-generic-version-now` unless there is a real reason not to
- use bypass only as a bounded exception

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
T01_BYPASS: temporary-coupling
T01_BYPASS_REASON: issue template is still evolving quickly and immediate generic refactor would slow current migration work
T01_REVIEW_TRIGGER: revisit when the next reusable adapter template is introduced outside BitPod

PR-to-Linear closeout check:
- PR: [BitPod-App/repo-name PR #123 — PR Title](https://github.com/BitPod-App/repo-name/pull/123)
- Linear: [BIT-000 — Full Issue Title](https://linear.app/bitpod-app/issue/BIT-000/issue-slug)
- Project scope: correct / standalone / blocked by tooling limitation
- Issue Type decision: Feature / Bug / Chore / Design / Plan / Release / left ambiguous; evidence source noted
- Status class: implementation / docs-design-audit / future-unstarted
- Labels: domain label + qa/pm result labels verified where finalized
- Bidirectional links: PR comment verified; Linear attachment/comment verified; no duplicate retroactive comments

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
- If a relevant issue omits the Taylor01 portability block, status must not be treated as decision-complete unless an explicit temporary-bypass note is present in the same update.
- If uncertain, set/keep `In Review` and request missing evidence.
- If a meaningful temporary bypass is used, add or update the active bypass register entry instead of silently relying on memory.
- If a PR-to-Linear closeout check is required and missing, do not claim the issue/project/PR history is normalized.
- If project membership cannot be corrected through available tooling, record that as an explicit blocker rather than marking the project cleanup fully complete.
