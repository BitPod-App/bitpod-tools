# Interim AI Technical QA + CJ Acceptance Policy v1

Status: Temporary working policy  
Owner: Product Development  
Linked issue: [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)

## Objective

Define the temporary merge policy for BitPod PRs while there is no separate human technical reviewer and no standalone QA agent with independent merge authority.

## Why This Exists

- CJ can perform product acceptance testing and operational approval.
- CJ is not expected to provide deep technical review on every PR.
- Codex/ChatGPT can produce technical QA evidence, but cannot satisfy GitHub's independent reviewer gate on their own PRs.
- We need an explicit, honest policy instead of pretending CJ's merge is a technical review.

## Temporary Role Split

### AI Technical QA

AI technical QA is responsible for:

- code-path review
- test execution
- verification commands
- artifact evidence
- risk callouts
- pass/fail recommendation

AI technical QA is **not** treated as an independent GitHub approver under current branch protection.

### CJ Acceptance / Operational Approval

CJ is responsible for:

- acceptance testing where relevant
- confirming product intent and operator fit
- deciding whether residual risk is acceptable
- executing admin bypass merge when policy conditions are satisfied

CJ acceptance is **not** a fake technical review.

## Allowed Interim Merge Path

A PR may be admin-bypass merged by CJ without a separate human technical reviewer only if all of the following are present:

1. AI technical QA evidence is attached to the PR or linked Linear issue.
2. Required tests/checks pass, or failures are explicitly understood and accepted.
3. Residual risk is stated clearly.
4. The merge note states that bypass is being used because reviewer/QA staffing is not yet fully separated.
5. Follow-up work is opened if the bypass leaves any unresolved technical gap.

If any of those are missing, the merge should not proceed.

## Minimum Evidence Required Before Bypass

Every bypassed PR must include:

1. Technical QA verdict: `PASSED` or `FAILED`
2. Scope reviewed/tested
3. Commands/checks executed
4. Artifact paths or URLs
5. Residual risk statement
6. Clear note that CJ approval is acceptance/operational approval, not independent technical review

## Temporary Merge Note Template

```md
Admin-bypass merge used under temporary policy in [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy).

AI technical QA evidence has been attached.
CJ approval here represents product acceptance / operational approval, not independent technical code review.

Residual risk:
- ...

Follow-up:
- ...
```

## Exit Criteria For This Temporary Policy

This policy should be retired once one of the following is true:

- a separate human technical reviewer is active and available
- a dedicated QA/reviewer agent model is formally implemented and accepted in governance
- GitHub reviewer routing and branch-protection rules are updated to match the real operating model

## Related Governance Work

- [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)
- [BIT-78 — Define GitHub team purpose, reviewer routing, and CJ role model](https://linear.app/bitpod-app/issue/BIT-78/define-github-team-purpose-reviewer-routing-and-cj-role-model)

