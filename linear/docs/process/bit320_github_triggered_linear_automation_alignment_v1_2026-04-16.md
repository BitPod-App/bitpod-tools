# BIT-320 GitHub-Triggered Linear Automation Alignment v1

Date: 2026-04-16
Owner: Product Development
Primary issue: [BIT-320 -- Align GitHub-triggered Linear automations with fail-closed merge readiness](https://linear.app/bitpod-app/issue/BIT-320/align-github-triggered-linear-automations-with-fail-closed-merge)

## Objective

Make GitHub-triggered Linear status changes truthful and fail-closed.

Target behavior:

- PR opened or draft PR opened may move work to `In Progress`
- PR review request or review activity may move work to `In Review`
- PR ready for merge may move work to `Delivered`
- PR or commit merge may move work from `Accepted` to `Done` only when merge-readiness truth is already satisfied

## What this lane is solving

GitHub events are objective, but they do not by themselves prove that:

- QA passed
- PM accepted
- blockers are clear
- release work is safe to close

This lane exists so the automation can stay truthful instead of silently over-closing work.

## Target truth rules

### Allowed truth-forward moves

- PR open / draft -> `In Progress`
- PR review request / review activity -> `In Review`
- PR ready for merge -> `Delivered`

### Merge-close rule

Merge to `main` may move `Accepted` -> `Done` only when all of the following are already true:

- QA truth is present
- PM truth is present
- blocker truth is clear
- release truth does not block closure

If those are not true, the automation must fail closed and leave a correction comment instead of forcing closure.

## Why native Linear alone is not enough

Native Linear GitHub workflow automation can move statuses, but it does not by itself guarantee:

- merge-readiness validation
- blocker truth validation
- release-train exception handling
- comment-based correction when truth is missing

Therefore this lane should be treated as:

- native Linear configuration where possible
- custom enforcement where Linear cannot express the truth safely

## Expected artifacts

- live mapping proof for the Product Development workflow
- repo-side note documenting the final truth contract
- evidence that merges do not auto-close issues unless the guard conditions are satisfied

## Validation checklist

- confirm the default GitHub workflow mappings in Linear
- confirm merge-driven closure does not bypass QA / PM / blocker truth
- confirm any custom enforcement leaves a correction comment when it blocks closure

## Escalate-back conditions

- branch protection or reviewer-routing semantics conflict with the intended truth model
- live GitHub/Linear automation cannot express the fail-closed behavior safely
- proof of merge closure is not trustworthy enough for this lane

