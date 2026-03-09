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
