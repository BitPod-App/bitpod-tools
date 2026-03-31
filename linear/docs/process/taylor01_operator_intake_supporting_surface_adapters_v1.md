# Taylor01 Operator Intake And Supporting Surface Adapters v1

Status: Active minimum-floor baseline
Primary issue: [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
Related issues:
- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
- [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract)
- [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary)
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
- [BIT-110 — Validate first AI HQ runtime path and complete first truthful smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/validate-first-ai-hq-runtime-path-and-complete-first-truthful-smoke)

## Objective

Define the Taylor01-side operator intake surface and supporting adapter
boundary strongly enough to constrain the first honest proof lane without
pretending the current BitPod/OpenClaw proving-ground contract is already the
final Taylor01 adapter system.

## Current truth

- the personal computer remains the operator control console
- the current execution boundary remains the Mini runtime under the `taylor01`
  execution account
- Linear and repo surfaces remain the durable truth anchors
- the current OpenClaw operator contract is practical proof-lane canon, not the
  full Taylor01 architecture owner
- supporting chat transports remain useful, but they are not the primary truth
  surface

## Taylor01 operator entry model

Taylor01 v1 should use this operator path:

1. operator starts from the personal computer control console
2. operator anchors work in Linear
3. operator reaches the HQ runtime through the intended remote path
4. HQ executes inside the Taylor runtime boundary
5. durable outcomes return to Linear and repo-owned truth surfaces

This means Taylor01 operator intake is defined first by:

- control-console origin
- issue-anchored intent
- real remote execution boundary
- durable result materialization

It is not defined first by:

- a transport-specific bot surface
- local overlay behavior inside Codex chat alone
- a dashboard or package that does not yet exist

## Supporting surface adapter model

Supporting adapters may exist for:

- Discord
- other chat transports
- future Taylor01-facing product surfaces

In this phase they count as supporting only if they preserve all of:

1. operator request entry with issue/context linkback
2. non-ambiguous handoff into the HQ runtime boundary
3. durable result return to Linear or repo truth
4. explicit non-primary status relative to the control-console to HQ path

## Adapter requirements

Every supporting adapter must carry:

- target issue or explicit execution lane
- operator request
- constraints or guardrails
- returned durable link or artifact

Every supporting adapter must not become:

- the only place work scope lives
- the only continuity source when Linear or repo truth exists
- the only place decisions are recorded
- the claimed execution boundary

## Relationship to OpenClaw doctrine

[BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
remains the practical proving-ground operator contract owner in `bitpod-tools`.

This Taylor01-side artifact uses that proving-ground contract as input and
imposes these constraints:

- preserve the personal-computer to HQ-runtime split
- preserve Linear and repo durable truth ownership
- keep supporting transports non-primary
- do not harden the current proving-ground transport details into the final
  Taylor01 adapter architecture

## What this constrains

### For [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)

- the proof path must start on the personal computer
- the proof path must anchor in Linear
- the proof path must execute in the HQ runtime boundary
- the proof must end with durable repo or Linear evidence

### For [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)

- a supporting transport may host the proving interaction
- but the proving interaction must still be backed by the real runtime boundary
- local overlay behavior by itself does not satisfy the Taylor01 operator
  contract

## Explicit non-goals

- no final capability-container decision
- no claim that Discord is the primary Taylor01 operator surface
- no requirement for a final dashboard before proving the first honest loop
- no forced extraction into a dedicated Taylor01/Claw repo yet
- no claim that current BitPod-local overlays are the durable Taylor01 adapter
  library

## Closeout read for BIT-205

BIT-205 can move toward closeout when this artifact and the current
OpenClaw-side contract agree on the following minimum floor:

- one primary operator path exists
- supporting adapters are explicitly non-primary
- durable truth ownership is explicit
- the first proof lane can execute without waiting on final packaging decisions
