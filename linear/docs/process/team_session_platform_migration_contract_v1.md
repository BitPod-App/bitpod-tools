# Team Session Platform Migration Contract v1

## Purpose

Define the migration contract for BitPod team session chat after Zulip Phase 0.

This contract exists to keep command/runtime work platform-portable while still allowing an immediate proof-of-concept transport.

## Current State

- Current production/session backend is Zulip Phase 0.
- Taylor runtime semantics were originally designed around Zulip stream/topic threads.
- Bridge/Taylor command and intent behavior now needs a migration path that does not trap runtime logic inside one chat provider.

## Directional Decision

- Discord is the first proof-of-concept target for post-Zulip team session operation.
- Discord is not the permanent architectural center.
- Future migration to another communication surface must remain possible without rewriting Taylor core execution logic.

## Non-Negotiable Rule

The team session system must be split into:

- runtime/core logic
- command/intake contract
- transport adapter

Transport-specific behavior must not become the place where product/session logic lives.

## Platform Strategy

### Stage A: Current

- Zulip remains the current live backend.
- Existing Zulip command/topic semantics remain valid until replacement is proven.

### Stage B: First Proof of Concept

- Discord is the first migration target.
- Discord should prove:
  - session command intake
  - Taylor reply flow
  - durable operator-visible thread/report flow
  - artifact linkback behavior

### Stage C: Future Portability

Potential future replacements remain explicitly in scope:

- internal dashboard chat
- OpenClaw-style internal operator surface
- another team collaboration platform if Discord proves limiting

## Scope of BIT-37

BIT-37 should cover:

- define the chosen post-Zulip session transport contract
- define minimum viable command/intake behavior for that transport
- define what must stay transport-agnostic
- define migration boundaries from Zulip semantics to adapter-based semantics

BIT-37 should not:

- lock Taylor permanently to Discord
- redesign all session behavior from scratch
- expand into full internal dashboard buildout

## Command Surface Principle

The command/intake layer must remain minimal and canonical.

Transport-specific syntax may vary, but command meaning must remain stable.

Canonical meaning set:

- `chat`
- `plan`
- `decide`
- `review`
- `status`
- `end`

If aliases exist, they should be documented as aliases, not separate semantic modes.

## Runtime Boundary

Taylor core should own:

- intent handling
- session lifecycle
- artifact generation
- summary/report generation
- policy checks

Transport adapters should own:

- inbound message/event normalization
- outbound message formatting
- platform-specific thread/channel/message addressing
- attachment/link posting

## Acceptance Criteria

BIT-37 is complete when:

- the chosen next transport is stated explicitly
- Discord is treated as proof-of-concept, not permanent lock-in
- the transport/runtime boundary is documented clearly
- follow-on command cleanup work can proceed without ambiguity
- [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify) is unblocked conceptually by a stable transport contract

## Follow-On Work

After this contract is accepted:

- [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify) should clean up command surface/docs against the canonical transport-agnostic command model
- later execution work can implement the actual Discord adapter/proof-of-concept path
- future dashboard/OpenClaw migration should reuse the same runtime contract instead of forking it
