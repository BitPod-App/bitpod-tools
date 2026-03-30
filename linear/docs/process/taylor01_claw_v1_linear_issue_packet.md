# Taylor01 Claw v1 Linear Issue Packet

Status: Active creation packet
Primary issue: [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
Related issues:
- [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Provide ready-to-create Linear issue payloads for the missing Taylor01 Claw v1
architecture lanes identified in `taylor01_claw_v1_umbrella_plan.md`.

These payloads are intentionally narrow. They should create missing planning and
boundary lanes without reopening proof work or prematurely starting extraction.

## Creation notes

- milestone assignment is intentionally left unverified in this packet
- create these issues as architecture and boundary lanes, not execution-closeout
  tickets
- link each issue back to
  [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
  and [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
  where relevant

## Issue 1

### Title

Taylor01: lock minimum real-Taylor runtime contract

### Objective

Define the minimum active runtime required to count as "real Taylor" so current
local `SKILL.md` overlays, planning-only abstractions, and ad hoc local
surfaces do not get mistaken for the durable runtime boundary.

### Scope

- define the minimum runtime surfaces required for "real Taylor"
- define the execution boundary and persistence expectations
- define what does not count as sufficient runtime embodiment
- align this contract with the current Taylor runtime on the Mini and the
  OpenClaw-first proof path

### Required outputs

- one retained runtime contract artifact
- explicit pass/fail criteria for whether a runtime surface counts as "real
  Taylor"
- one short note on how this contract constrains [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
  and [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)

### Verification plan

- verify the contract is consistent with the current Mini runtime truth
- verify it excludes pure local skill-overlay behavior from counting as durable
  runtime embodiment
- verify it does not reopen unrelated OpenClaw packaging work

### Rollback note

If the contract proves too narrow or too broad, revise the retained contract
artifact before using it as a closeout gate for proof tickets.

## Issue 2

### Title

Taylor01: decide Claw v1 scope and boundary

### Objective

Define what Claw v1 actually is in the current phase so the system does not
drift between operator surface, runtime wrapper, embodiment contract, and
general product aspiration.

### Scope

- decide whether Claw v1 is primarily:
  - operator surface
  - runtime wrapper
  - embodiment contract
  - or a narrow combination
- define explicit non-goals for this phase
- keep future repo naming open until the boundary is clearer

### Required outputs

- one short retained boundary model for Claw v1
- one explicit non-goals section
- one note on how Claw v1 relates to current OpenClaw doctrine in
  `bitpod-tools`

### Verification plan

- verify the Claw v1 boundary is consistent with current OpenClaw operator
  contract truth
- verify it does not overclaim the current Taylor runtime as final Claw shape
- verify it leaves room for a future dedicated repo without forcing it now

### Rollback note

If the decision proves unstable, hold the old proof lanes open but do not use
the unstable boundary model as extraction canon.

## Issue 3

### Title

Taylor01: decide capability container direction beyond current `SKILL.md`

### Objective

Define the durable capability-container decision space for Taylor without
mistaking the current `SKILL.md` compatibility surface for the final model.

### Scope

- evaluate `SKILL.md`, `sould.md`, manifest-first package, or another explicit
  alternative
- keep current compatibility installs truthful and transitional
- define what durable metadata must survive regardless of container choice

### Required outputs

- one retained decision-space artifact
- one container-comparison table
- one recommendation on what remains transitional until the final choice is
  made

### Verification plan

- verify the decision-space stays consistent with capability provenance canon in
  `taylor01-skills`
- verify no option is treated as already locked unless current evidence supports
  that claim
- verify the output keeps current `SKILL.md` surfaces visible but non-final

### Rollback note

If no option is mature enough to lock, keep the output as a decision-space
artifact only and explicitly preserve compatibility-mode behavior.

## Issue 4

### Title

Taylor01: classify current artifacts by durability and overlay status

### Objective

Classify current Taylor-related work across `bitpod-tools`,
`bitpod-taylor-runtime`, and `taylor01-skills` so durable substrate,
transitional compatibility, and BitPod-local overlays stop blurring together.

### Scope

- classify current active artifacts by durable substrate, transitional
  compatibility, or BitPod/local overlay
- identify which `bitpod-tools` artifacts are still owning doctrine versus only
  temporary portability scaffolding
- identify which current local surfaces should not be polished as permanent

### Required outputs

- one retained artifact-classification map
- one list of top transitional artifacts that should not harden further
- one list of BitPod overlays that should remain local for now

### Verification plan

- verify the output is consistent with the current Taylor boundary map, coupling
  log, and active bypass register
- verify it does not accidentally reclassify active BitPod doctrine as portable
  core without evidence
- verify it leaves runtime proof work and doctrine work in their current owning
  repos

### Rollback note

If the first classification pass is too broad, keep only the highest-signal
artifacts and refine later instead of forcing a fake-complete inventory.

## Issue 5

### Title

Taylor01: define future dedicated repo extraction trigger for Claw

### Objective

Define the trigger for when a dedicated Taylor01 or Taylor01-Claw repo becomes
justified, while keeping the repo name and exact extraction package open for
now.

### Scope

- define extraction trigger conditions
- define what content would move when the trigger is met
- define what should stay in `bitpod-tools` or BitPod-local overlays even after
  extraction

### Required outputs

- one retained extraction-trigger artifact
- one list of move-when-triggered content classes
- one list of content classes that should remain local or doctrine-owned

### Verification plan

- verify the trigger remains consistent with the current in-repo boundary
  recommendation
- verify the trigger is not satisfied merely by interest or naming preference
- verify the plan does not force premature migration of proof or overlay lanes

### Rollback note

If the trigger definition is still too vague, keep the output as a threshold
draft and avoid using it as justification for immediate repo creation.
