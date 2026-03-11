# QA Authority Model v1

Status: Working baseline  
Linked issue: [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)

## Objective

Ensure QA remains an independent release gate with unambiguous pass/fail authority.

## Independence Rules

- QA cannot approve its own implementation output.
- Engineering cannot bypass QA for behavior-affecting changes.
- Taylor orchestrates flow but does not overwrite QA verdicts.
- CJ can override only with explicit risk acknowledgment and rollback plan.

## QA Verdict Contract

Every QA decision must include:

1. Verdict: `PASSED` or `FAILED`
2. Scope tested
3. Commands/checks run
4. Artifact evidence links/paths
5. Blocking defects (if failed)
6. Residual risks (if passed with caveats)

## Gate Policy

- Merge-to-done path requires:
  - QA verdict = PASSED
  - PM approval signal present
- If either is missing, gate fails closed.

## Minimal QA Artifact Template

```md
QA Verdict: PASSED|FAILED
Scope:
Checks executed:
- ...
Artifacts:
- /path/or/url
Defects (if any):
- ...
Residual risk:
- ...
```

## Exceptions

Allowed only for emergency mitigation with CJ approval:

- temporary bypass with documented rollback
- explicit post-incident QA follow-up issue opened immediately

## Temporary Staffing Gap Policy

For the current interim PR workflow while BitPod lacks a separate human technical reviewer, see:

- [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)
- `./interim_ai_technical_qa_cj_acceptance_policy_v1.md`

That policy does not replace QA independence as the target model. It only defines the temporary path where AI technical QA evidence exists, CJ performs acceptance/operational approval, and admin bypass is used honestly rather than mislabeled as technical review.

## Auditability

- QA evidence must be attached to related Linear issue and/or PR thread.
- Status transitions to Done without QA evidence are considered invalid and must be reverted.
