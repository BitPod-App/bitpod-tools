# BIT-30 Webhook Parity Checks v1 (Draft)

Date: 2026-03-09
Issue: https://linear.app/bitpod-app/issue/BIT-30/linear-github-discord-webhook-integration-parity-checks

## Objective
Validate end-to-end event routing parity after Discord onboarding for core systems (GitHub, Linear, runtime).

## Event matrix (target)
| Source | Event | Expected Discord channel | Expected payload fields |
|---|---|---|---|
| GitHub | PR opened | #30-build | repo, pr#, title, author, link |
| GitHub | check failed | #60-incidents | repo, check name, run URL, severity |
| GitHub | PR merged | #50-release | repo, pr#, merge SHA, link |
| Linear | issue moved to In Review | #40-review-qa | issue key, title, assignee, link |
| Linear | priority escalated | #00-ops-status | issue key, old/new priority, link |
| Runtime bot | QA summary posted | #40-review-qa | issue key, result, artifact links |
| Runtime bot | incident emitted | #60-incidents | service, symptom, next action |

## Verification plan
1. Fire synthetic webhook payload per row.
2. Confirm target channel receives exactly one message.
3. Confirm payload includes required fields.
4. Confirm idempotency (replay does not duplicate uncontrolled messages).

## Deliverables
- pass/fail table with evidence links
- mismatch list + remediation tasks
- rollback switch plan
