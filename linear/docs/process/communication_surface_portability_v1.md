# Communication Surface Portability v1

Status: Active design guardrail  
Scope: Prevent lock-in to Discord while preserving current execution velocity.

Related contract:

- `openclaw_operator_intake_dispatch_contract_v1.md`

## Rule

Discord is a transport adapter, not a system-of-record and not a permanent dependency.

The primary operator surface is defined separately in
`openclaw_operator_intake_dispatch_contract_v1.md`. This document only defines
the portability and anti-lock-in rules for supporting transports.

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

Supporting transports must preserve the intake/result behavior defined in the
operator contract, not invent a separate durable truth model.

## Anti-Lock-In Requirements

- No business logic should depend on Discord channel IDs directly.
- No irreversible workflow should require Discord-only features.
- Every Discord-posting workflow should have a no-discord fallback path.
- Channel naming maps live in config, not hardcoded.

## Required Parity Behaviors

Any supporting chat adapter worth keeping during bootstrap must preserve these
behaviors:

- operator request entry can be mapped back to the owning Linear issue or
  execution lane
- progress or result messages can carry durable references back to Linear, PRs,
  and artifacts
- result or status return can be delivered without making the transport the only
  durable record
- operator can tell whether the message is a request, status summary, review
  note, or final result
- the adapter preserves the rule that HQ remains primary and the transport
  remains secondary

If a candidate adapter cannot preserve the above without bespoke logic or
durability drift, it should not be treated as parity-critical.

## Optional Adapter Behaviors

These may improve UX, but are not required for bootstrap parity:

- rich embeds or custom formatting
- mentions, slash commands, or thread-specific UX
- reactions, acknowledgements, or presence indicators
- mobile-first notifications
- transport-specific shortcuts that do not change durable truth

## Supporting-Surface Recommendation During Bootstrap

Keep the supporting-surface set intentionally narrow:

- keep Discord as the only actively supported chat adapter during the current
  bootstrap window because it already has relevant history and existing related
  tickets
- treat any additional messaging surface as deferred unless it can reuse the
  same event envelope and operator contract with near-zero new bespoke logic
- do not let supporting-adapter work outrun the primary HQ operator-loop proof

## Migration Readiness Criteria

Before declaring communication layer mature:

- transport-agnostic event schema documented
- Discord adapter implementation documented
- dashboard adapter plan stubbed with same schema
- verification checklist confirms equal payload fidelity across adapters

## Practical Current Stance

- Keep completing Phase 2 parity via Discord because it is the active path now.
- Build all new communication work so it can switch transports with minimal refactor.
- In Phase 4, preserve Discord only as a supporting adapter and avoid
  multiplying adapter surfaces before the primary HQ loop is fully proven.

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
