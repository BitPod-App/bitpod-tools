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

## Auditability

- QA evidence must be attached to related Linear issue and/or PR thread.
- Status transitions to Done without QA evidence are considered invalid and must be reverted.
