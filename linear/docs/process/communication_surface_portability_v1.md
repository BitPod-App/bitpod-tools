# Communication Surface Portability v1

Status: Active design guardrail  
Scope: Prevent lock-in to Discord while preserving current execution velocity.

## Rule

Discord is a transport adapter, not a system-of-record and not a permanent dependency.

## Source-of-Record Boundaries

- Linear = execution truth (issues, status, ownership, dependencies)
- Repo/docs = implementation truth and durable memory
- Communication surface (Discord today, dashboard later) = notification + interaction layer only

## Adapter Contract

All operational notifications should be emitted through a canonical event envelope:

- event type
- summary text
- severity
- links (Linear issue / PR / artifact)
- actor/source
- timestamp

Transport adapters then map this envelope to:

- Discord messages
- future internal dashboard feed
- future additional channels if required

## Anti-Lock-In Requirements

- No business logic should depend on Discord channel IDs directly.
- No irreversible workflow should require Discord-only features.
- Every Discord-posting workflow should have a no-discord fallback path.
- Channel naming maps live in config, not hardcoded.

## Migration Readiness Criteria

Before declaring communication layer mature:

- transport-agnostic event schema documented
- Discord adapter implementation documented
- dashboard adapter plan stubbed with same schema
- verification checklist confirms equal payload fidelity across adapters

## Practical Current Stance

- Keep completing Phase 2 parity via Discord because it is the active path now.
- Build all new communication work so it can switch transports with minimal refactor.

## Discord Baseline Matrix

| Canonical intent | Current Discord channel | Payload focus | Required links | Dashboard-ready mapping |
| --- | --- | --- | --- | --- |
| ops_status | `ops-status` | deploy state, health state, non-interactive automation summaries | Linear issue or artifact | operational feed / status rail |
| build | `build` | implementation progress, PR-level execution summaries, smoke outcomes | PR + Linear issue | build stream |
| review_qa | `review-qa` | QA verdicts, review blockers, pass/fail summaries | PR + artifact + Linear issue | review queue |
| release | `release` | merge-ready state, release cut notes, rollout checkpoints | PR + release artifact | release board |
| incidents | `incidents` | degraded capability, outage notices, incident containment updates | incident issue + artifact | incident console |

Rules for all rows:

- Only summary-first messages belong in the transport adapter.
- Raw execution traces stay in repo artifacts or linked systems.
- Every post must include at least one durable reference: Linear issue, PR, or artifact path/link.
- Channel routing must be config-driven, never hardcoded into business logic.

## Migration-Readiness Checklist

- Canonical event envelope documented and adapter-agnostic.
- Discord baseline matrix defined with stable intent names.
- Dashboard destination names can be mapped 1:1 from canonical intents.
- No workflow requires Discord-specific metadata to preserve correctness.
- Every transport post has a no-Discord fallback path via repo artifact and Linear link.
