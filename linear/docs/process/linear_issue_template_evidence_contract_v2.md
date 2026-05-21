# Linear Issue Template Hardening v2 (Evidence + Taylor01 Portability)

Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Supersedes: `linear_issue_template_evidence_contract_v1.md` for active use when the portability gate applies
Version: v2

## Required fields for completion claims

Every "Done" claim must include:

1. `Status line`
- Current status and transition reason.

2. `Description sync`
- State whether the issue description is current after the work.
- If scope, decisions, blockers, names/IDs, intended behavior, or acceptance criteria changed, update the issue description and name the changed section.
- If the description could not be updated, include `DESCRIPTION_STALE`, quote or name the stale section, and do not treat the issue as decision-complete until corrected.
- Comments should point to what changed in the description; comments must not replace the description as the source of truth.

3. `Commands/UI checks`
- Exact command(s) run or explicit UI path used.

4. `Artifacts`
- Absolute path(s) to generated docs/logs/screenshots (or PR/commit links).

5. `Pass/Fail`
- Explicit pass/fail result per check.

6. `QA / PM gate sync`
- When a GitHub PR is involved, record the official QA reviewer identity and review outcome.
- If VeraQA is requested, the official QA identity is `vera-qa`; advisory workers or PR authors are not substitutes.
- Record the Linear translation: `qa-passed` + forward movement, `qa-failed` + back to `In Progress`, or blocked/held with evidence.
- Record Taylor01 PM acceptance separately from technical QA: accept, reject, block, or elevate to CJ, with confidence and reason when not accepting.
- Taylor01 may PM-accept CJ-requested work/tickets she created or coordinated, but must not use `qa-skipped` as a replacement for VeraQA when VeraQA is required on PR-backed work.

7. `Risk / follow-up`
- Any deferred risk and next action.

8. `PR-to-Linear closeout check` (required when a GitHub PR or Linear normalization is involved)
- GitHub PR link(s) using `linear_link_reference_policy_v1.md` format.
- Linear issue link(s) using canonical full-title format.
- Project scope check: correct project, standalone issue, or explicit blocker if tooling cannot remove a wrong project.
- Status class check: implementation, docs/design/audit, or future/unstarted.
- Label check: finalized labels applied only to finalized items; future items do not receive completion labels.
- Bidirectional linking check: PR comment plus Linear issue comment/link verified, with no duplicate link-spam.

9. `Issue Type check` (required when creating, triaging, or normalizing issue type)
- Exactly one canonical issue type is set, or `needs-type` is present with a note naming the missing evidence.
- Type choice follows `linear/contracts/linear_type_classifier_v1.json` and `linear_issue_type_decision_guide_v1.md`.
- Type is not inferred from title alone.
- Include the compact `Linear Classification` intake block when moving an issue to `Ready`:
  - `Output`
  - `Behavior change`
  - `Broken existing behavior`
  - `Evidence`
  - `Children expected`
  - `PM-testable`

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

Description sync:
- Updated description section: Done when / Acceptance criteria now reflects the verified current gate.
- No acceptance criteria are left only in comments.

Commands/UI checks:
- `gh api /orgs/BitPod-App --jq '{two_factor_requirement_enabled,members_can_delete_repositories}'`
- GitHub UI: Org Settings -> Security -> Require 2FA = enabled

Artifacts:
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/github_org_baseline_evidence_2026-03-06.md`
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
- Status class: implementation / docs-design-audit / future-unstarted
- Labels: domain label + qa/pm result labels verified where finalized
- Bidirectional links: PR comment verified; Linear attachment/comment verified; no duplicate retroactive comments

Issue Type check:
- Type: Feature / Bug / Chore / Design / Plan / Release / blocked by `needs-type`
- Evidence basis: acceptance criteria, defect evidence, design artifact, parent rollout scope, release checklist, or other current issue evidence
- Decision guide: `linear/contracts/linear_type_classifier_v1.json` and `linear_issue_type_decision_guide_v1.md`

QA / PM gate sync:
- Official QA: `vera-qa` approved / requested changes / blocked, with GitHub review link.
- Linear translation: `qa-passed` -> Delivered / `qa-failed` -> In Progress / blocked with evidence.
- Taylor01 PM acceptance: accepted / rejected / blocked / elevated to CJ, with confidence and reason.
- QA-skip check: confirm Taylor01 did not substitute `qa-skipped` for VeraQA where VeraQA was required; PM acceptance may still be valid for CJ-requested work.

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
- If material issue truth changed but the description was not updated, keep or return the issue to `In Review` / blocked state and add `DESCRIPTION_STALE` until corrected.
- If a relevant issue omits the Taylor01 portability block, status must not be treated as decision-complete unless an explicit temporary-bypass note is present in the same update.
- If uncertain, set/keep `In Review` and request missing evidence.
- If a meaningful temporary bypass is used, add or update the active bypass register entry instead of silently relying on memory.
- If a PR-to-Linear closeout check is required and missing, do not claim the issue/project/PR history is normalized.
- If project membership cannot be corrected through available tooling, record that as an explicit blocker rather than marking the project cleanup fully complete.
- If issue type evidence is missing or ambiguous, keep or add `needs-type` rather than guessing.
