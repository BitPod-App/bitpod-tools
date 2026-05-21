# VeraQA Review Routing Guide v1

Status: Active guidance  
Owner: BitPod GitHub governance / Vera QA lane  
Scope: active BitPod-App repos, main-branch PR review routing

## Purpose

Keep VeraQA review routing simple, understandable, and easy to override when operator judgment requires it.

This guide replaces the heavier rule-of-record framing. It is guidance for default routing and escalation, not a constitutional enforcement layer.

Companion context:

- [github_team_purpose_reviewer_routing_v1.md](./github_team_purpose_reviewer_routing_v1.md)
- [vera_qa_lane_contract_v1.md](./vera_qa_lane_contract_v1.md)


## Current rollout status

Status: **Active**.

Live-state note — 2026-05-21:

- Active repo CODEOWNERS files route PR review to VeraQA teams.
- `sector-feeds` and `bitregime-core` route to `@BitPod-App/veraqa-tier-2`.
- Other active repos route to `@BitPod-App/veraqa-tier-1`.
- VeraQA tier teams should contain `vera-qa` only unless CJ explicitly approves adding another reviewer.
- `taylor-01` must not be a VeraQA team member because Taylor01 PM acceptance is separate from code review.

If routing is found paused or commented out again, re-enable by restoring the active CODEOWNERS line for the correct tier and verifying that the owning VeraQA team has write access on that repo.

## Default routing

Use CODEOWNERS to point PR review toward the right VeraQA lane:

- `sector-feeds` -> `@BitPod-App/veraqa-tier-2`
- `bitregime-core` -> `@BitPod-App/veraqa-tier-2`
- all other active repos -> `@BitPod-App/veraqa-tier-1`

Maintainer teams such as `@BitPod-App/core-maintainers` or `@BitPod-App/code-maintainers` should not be the default QA review route.

`@BitPod-App/qa-reviewers` may exist as an older/general QA team, but it is not the default VeraQA CODEOWNERS route.

## Tier meaning

### T1: normal QA

Use T1 for ordinary PRs in most repos.

T1 should check the practical quality bar: does the change match the request, are tests/checks credible, and are obvious risks called out.

### T2: high-impact or complex QA

T2 must use a stronger review setting than baseline T1, such as a stronger OpenAI code-review model or a code-specific model with medium/high reasoning (for example, a verified Codex-3-style code model when available). Do not downshift T2 into the same baseline model/settings as T1.

Use T2 by default for:

- `sector-feeds`
- `bitregime-core`

Use T2 in other repos when a PR is large, complex, risky, or touches sensitive areas such as:

- `.github/` or workflows
- deploy, infra, runtime, Cloudflare, or Terraform paths
- data, migration, security, secret, or production behavior
- broad refactors or behavior changes with high blast radius

### T3: rare manual deep audit

Use T3 only for exceptional risk, periodic deep audit, or explicit Taylor/CJ/Vera request.

T3 is manual + rare, never default, and not normal merge gating.


## GitHub permission note

GitHub only treats a team as a valid CODEOWNERS owner when that team has write access to the repository. For VeraQA teams, write access is a GitHub routing requirement, not implementation ownership. The role boundary remains QA review only.

## Branch protection posture

Keep GitHub branch protection lightweight:

```yaml
required_approving_review_count: 1
require_code_owner_reviews: true
restrictions: null
```

CODEOWNERS is the VeraQA routing gate. The one required approval is the lightweight merge safety baseline.

## Bypass guidance

Admins may bypass default routing when urgency, broken tooling, or operator judgment requires it.

When a bypass skips the expected VeraQA path, leave a short visible note in the PR, issue, or follow-up thread with:

- what was bypassed
- why it was reasonable
- whether later QA/revalidation is needed

Do not build a large bypass registry unless bypasses become frequent enough to need one.

## Review expectation summary

The durable rule is simple:

> VeraQA owns technical QA review routing. `sector-feeds` and `bitregime-core` default to T2. Other repos default to T1 unless PR size, complexity, or risk justifies T2. T3 is manual + rare, never default.
