# Taylor01 Portability Review Gate v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Require explicit Taylor01 portability classification for any work that could quietly hard-code BitPod-specific assumptions into reusable process, workflow, agent, or adapter layers.

The goal is not to freeze experimentation.

The goal is to make sure change lands in the correct bucket or is explicitly marked as temporary coupling.

This gate exists to help BitPod get built with the right reusable boundaries, not to replace BitPod as the primary execution goal.

## Gate applies when

A ticket or PR touches any of:

- agents or specialist roles
- orchestration/runtime behavior
- process docs
- workspace policy
- Linear/GitHub/Discord workflow behavior
- future adapter contracts

The gate does not apply to clearly product-only work such as BitPod brand, BitPod glossary, or user-facing product canon.

## Required fields

Every relevant Linear issue and PR must include:

- `T01_LAYER`: `core | policy | adapter | bitpod-embedding | mixed`
- `T01_SPECIFICITY`: `portable | bitpod-specific | mixed`
- `T01_COUPLING`: short note on what is still too coupled
- `T01_ACTION`: `keep-local | move-later | create-generic-version-now`

Optional when bypassing portability work for now:

- `T01_BYPASS`: `none | temporary-coupling`
- `T01_BYPASS_REASON`: short reason the portability fix is not worth doing immediately
- `T01_REVIEW_TRIGGER`: the condition that should cause the coupling to be revisited

## Decision rule

- Default posture: be strict enough to notice coupling early.
- Default action for new portable or mixed work should be to solve the portability concern now.
- Do not block experimentation by default.
- Keep BitPod moving by default unless the coupling risk is large enough to justify interruption.
- If the work creates hard future lock-in, portability work may interrupt or reshape BitPod delivery.
- If the work is acceptable for now, coupling must still be logged explicitly.
- A temporary bypass is allowed when the portability fix is not worth the immediate interruption.
- "We'll clean it up later" is not sufficient without a `T01_COUPLING` note and bypass metadata when applicable.

## Temporary bypass rule

Use bypass only when all are true:

- the work is still exploratory or rapidly evolving
- the current coupling is understandable and bounded
- fixing it now would create disproportionate drag
- there is a clear future review trigger

Do not use bypass when:

- the coupling would be expensive to unwind even one or two steps later
- the decision would hard-code Taylor01 to BitPod or one tool surface in a foundational way
- nobody can explain what would trigger future cleanup

## Active bypass review rule

- Temporary bypasses should not disappear into a generic backlog.
- Record meaningful active bypasses in:
  - `linear/temporal/active/project__taylor01__b51442062c45/taylor01-active-bypass-register-v1.md`
- Review active bypasses:
  - on the next related touch, or
  - during the next weekly Taylor01 review,
  - whichever comes first
- Remove the entry when one of the following becomes true:
  - the coupling is resolved
  - the artifact is reclassified as intentionally BitPod-specific
  - the bypass is promoted into a concrete Taylor01 ticket because it now matters enough

## Backlog rule

- Do not create a future ticket for every temporary bypass.
- Only promote a bypass into backlog when it becomes important enough that not solving it soon would create real cost.
- The active bypass register is for short-lived, reviewable exceptions.
- The backlog is for items that have earned dedicated follow-up.

## Where to record it

### Linear tickets

Put the block in:

- the issue description, or
- the first execution comment if the issue already exists and should not be heavily rewritten

### PRs

Put the block in the PR description using the repo PR template.

## Example block

See:

- `linear/examples/taylor01_portability_check_template_v1.md`

## Current policy stance

This is a strict visibility gate with a controlled bypass path.

Taylor01 is important enough that avoiding bad entanglement is allowed to slow BitPod work when needed.

Taylor01 is also experimental enough that temporary coupling is acceptable when it is explicit, bounded, and reviewable.
