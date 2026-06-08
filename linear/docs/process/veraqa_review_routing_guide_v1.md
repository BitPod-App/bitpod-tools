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

Live-state note — 2026-06-08:

- Active repo CODEOWNERS files should route PR review to one VeraQA gate team: `@BitPod-App/veraqa`.
- Tier-based teams (`veraqa-tier-1`, `veraqa-tier-2`, `veraqa-tier-3-audit`) are superseded as active routing concepts.
- Vera QA depth is a Vera/runtime/process decision, not a GitHub team-name decision.
- `@BitPod-App/veraqa` exists as a stable indirection layer so the concrete review identity can change later, for example from the `vera-qa` user to a verified GitHub App/bot actor, without rewriting every repo CODEOWNERS file.
- `taylor-01` and CJ/admin must not be VeraQA team members by default because PM acceptance and admin bypass are separate from code review.

If routing is found paused, commented out, or still pointing at a tier team, re-enable by restoring the active CODEOWNERS line and verifying that `@BitPod-App/veraqa` has write access on that repo.

## Default routing

Use CODEOWNERS to point PR review toward the single VeraQA gate:

```text
* @BitPod-App/veraqa
```

Maintainer teams such as `@BitPod-App/core-maintainers` or `@BitPod-App/code-maintainers` should not be the default QA review route.

`@BitPod-App/qa-reviewers` may exist as an older/general QA team, but it is not the default VeraQA CODEOWNERS route.

## QA depth

Vera decides QA depth at runtime/process level. The old T1/T2/T3 naming can remain as historical shorthand for review depth, but it must not be encoded as separate GitHub CODEOWNERS teams.

Use stronger/deeper Vera review when a PR is large, complex, risky, or touches sensitive areas such as:

- `.github/` or workflows
- deploy, infra, runtime, Cloudflare, or Terraform paths
- data, migration, security, secret, or production behavior
- broad refactors or behavior changes with high blast radius

Rare deep audits remain explicit Taylor/CJ/Vera requests or intentionally selected assurance samples, never default merge gating.

## GitHub permission note

GitHub only treats a team as a valid CODEOWNERS owner when that team has write access to the repository. For VeraQA teams, write access is a GitHub routing requirement, not implementation ownership. The role boundary remains QA review only.

## Branch protection posture

Keep GitHub branch protection strict enough to make VeraQA real, but lightweight in approval count:

```yaml
required_approving_review_count: 1
require_code_owner_reviews: true
dismiss_stale_reviews: true
require_last_push_approval: true
enforce_admins: true
restrictions: null
```

CODEOWNERS is the VeraQA routing gate. The one required approval is the lightweight merge safety baseline. Dismiss stale reviews and last-push approval prevent post-review changes from slipping through without fresh VeraQA approval; admin enforcement prevents routine admin bypass from becoming the default path.

## Bypass guidance

Admins may bypass default routing when urgency, broken tooling, or operator judgment requires it.

When a bypass skips the expected VeraQA path, leave a short visible note in the PR, issue, or follow-up thread with:

- what was bypassed
- why it was reasonable
- whether later QA/revalidation is needed

Do not build a large bypass registry unless bypasses become frequent enough to need one.

## Review expectation summary

The durable rule is simple:

> VeraQA owns technical QA review routing through the single `@BitPod-App/veraqa` gate. `sector-feeds` and `bitregime-core` default to escalated Vera review. Other repos default to baseline Vera review unless PR size, complexity, or risk justifies escalation. Rare deep audit is manual, never default.
