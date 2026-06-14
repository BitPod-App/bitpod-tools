# VeraQA Review Routing Guide v1

Status: Historical / superseded by BIT-617 on 2026-06-14
Owner: BitPod GitHub governance / Vera QA lane
Scope: retained only to explain the former CODEOWNERS model

## Current status

CODEOWNERS-based VeraQA routing is retired as the default merge gate. Active repos should require the GitHub check run `vera-qa-gate` instead of requiring `@BitPod-App/veraqa` review.

Reasons for retirement:

- CODEOWNERS routes through a GitHub user/team review abstraction, not the bot/app actor that produced the QA verdict.
- The `vera-qa` user seat costs money and creates attribution ambiguity.
- Required CODEOWNERS review can block PRs even when the real custom Vera QA gate has passed.

## Active replacement

Use branch protection / rulesets to require:

```text
vera-qa-gate
```

Do not require CODEOWNERS / PR reviews as the default Vera QA gate. Optional human review may still be requested manually, but it must not be the merge-blocking QA lane.

## QA depth

Vera decides QA depth at runtime/process level. The old T1/T2/T3 naming can remain as historical shorthand for review depth, but it must not be encoded as separate GitHub CODEOWNERS teams.

Use stronger/deeper Vera review when a PR is large, complex, risky, or touches sensitive areas such as:

- `.github/` or workflows
- deploy, infra, runtime, Cloudflare, or Terraform paths
- data, migration, security, secret, or production behavior
- broad refactors or behavior changes with high blast radius

Rare deep audits remain explicit Taylor/CJ/Vera requests or intentionally selected assurance samples, never default merge gating.

## GitHub permission note

This section is historical. The active gate no longer depends on team write access for CODEOWNERS. Active repos should require the `vera-qa-gate` status check and keep admin enforcement enabled.

## Branch protection posture

Current desired baseline:

```yaml
required_status_checks:
  - vera-qa-gate
required_pull_request_reviews: null
enforce_admins: true
restrictions: null
```

CODEOWNERS / PR-review requirements are not the VeraQA merge gate.

## Bypass guidance

Admins may bypass the custom QA gate when urgency, broken tooling, or operator judgment requires it.

When a bypass skips the expected `vera-qa-gate` path, leave a short visible note in the PR, issue, or follow-up thread with:

- what was bypassed
- why it was reasonable
- whether later QA/revalidation is needed

Do not build a large bypass registry unless bypasses become frequent enough to need one.

## Review expectation summary

The durable rule is simple:

> VeraQA owns technical QA through the required `vera-qa-gate` check. Repos may request deeper Vera review based on risk, but GitHub team/CODEOWNERS routing is historical, not the active merge gate.
