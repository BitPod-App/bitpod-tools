# BIT-28 Discord Migration Architecture v1 (Draft)

Date: 2026-03-09
Issue: https://linear.app/bitpod-app/issue/BIT-28/discord-migration-architecture-and-channel-topology

## Objective
Define a Discord workspace topology and integration model that preserves operational parity with current Zulip-based flows while enabling future runtime agent expansion.

## Channel Topology (v1)
- #00-ops-status (read-only; automated broadcast sink)
- #10-plan
- #20-decide
- #30-build
- #40-review-qa
- #50-release
- #60-incidents
- #70-memory-log

## Role/Permission Model (minimum)
- owner: full admin
- core-maintainers: manage channels/webhooks, post everywhere
- automation-bots: post to status/release/incidents/memory-log
- read-only: consume status/release updates only

## Integration Matrix (target)
- GitHub -> Discord
  - PR opened/merged
  - check failures
  - release tags
- Linear -> Discord
  - urgent status changes
  - blockers/priority changes
  - milestone update broadcasts
- Runtime agents -> Discord
  - command receipts
  - QA summaries
  - incident/event logs

## Migration Guardrails
- Preserve one source-of-truth for issue status in Linear.
- Discord mirrors status; it does not become canonical state.
- Keep fail-closed behavior for mutation actions.
- Keep rollback path to Zulip until parity checks pass.

## Deliverables for BIT-28 completion
- channel + role map diagram/table
- webhook routes table (source -> channel -> payload)
- command parity matrix with existing Zulip commands
- cutover + rollback runbook
