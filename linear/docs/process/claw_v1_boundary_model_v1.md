# Claw v1 Boundary Model v1

Status: Active minimum-floor baseline
Primary issue: [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary)
Related issues:
- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)

## Objective

Define the current narrow scope of Claw v1 so Taylor01/OpenClaw work does not
drift between operator surface, runtime wrapper, embodiment floor, and future
platform aspiration.

## Current truth

- current OpenClaw reality is contract-first rather than package-first
- the active execution substrate is the live Taylor runtime on the Mini
- the active control path still begins on the personal computer and dispatches
  into the execution node
- current local `SKILL.md` surfaces are real and useful, but still local
  overlays rather than Claw's durable identity

## Claw v1 is

Claw v1 should be treated as a narrow combined surface made of:

1. operator intake and dispatch contract
2. runtime wrapper over the live Taylor execution path
3. embodiment boundary for what should count as runtime-real Taylor

This means Claw v1 is broader than only a chat surface and narrower than a full
portable Taylor platform.

## Claw v1 is not

Claw v1 should not be treated yet as:

- the final Taylor capability container
- the final dedicated Taylor repo
- proof that current `SKILL.md` compatibility surfaces are durable
- a full multi-agent team runtime
- a future dashboard/UI product that does not yet exist

## Boundary split

### Inside Claw v1

- operator intake and dispatch contract
- runtime-real floor for Taylor
- current control-console to execution-node execution shape
- truthful result handoff back to durable repo/issue surfaces

### Outside Claw v1 for now

- final capability-container choice
- broad extraction into a dedicated Taylor01 or Taylor01-Claw repo
- specialist embodiment beyond Taylor
- broad customer-neutral adapter library extraction
- full productization of the OpenClaw runtime/package

## Relationship to Taylor01

Taylor01 remains the broader portable PM + AI team operating system.

Claw v1 is the current embodiment and operator-facing boundary inside that
broader Taylor01 direction.

So the current relationship is:

- Taylor01 = broader portable system direction
- Claw v1 = current embodiment/operator boundary being locked now

## Relationship to current repos

- `taylor01-skills`
  - owns portable substrate
  - not yet the whole Claw repo

- `bitpod-tools`
  - owns current OpenClaw/Taylor doctrine and BitPod overlays
  - remains the truthful doctrine surface during v1

- `bitpod-taylor-runtime`
  - owns the live runtime substrate and runtime proof lane

## Relationship to current OpenClaw doctrine in `bitpod-tools`

- `bitpod-tools` remains the owning doctrine surface for the current
  proving-ground operator contract
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
  stays the practical OpenClaw-side contract owner for the current proof lane
- this boundary model constrains that doctrine from the Taylor01 side without
  replacing it as the Bootstrap proving-ground operator contract

## Required non-goals

Do not use Claw v1 work to:

- silently reclassify BitPod doctrine as portable core
- treat current local overlays as final capability architecture
- reopen broad extraction before runtime and boundary decisions are locked
- pull [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
  or [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
  forward prematurely

## Exit trigger

This boundary model should be revisited when one of these becomes true:

1. a dedicated OpenClaw runtime/package exists strongly enough to replace the
   current contract-first shape
2. the capability-container direction is locked
3. a dedicated repo extraction trigger is actually met
4. Claw needs to support a real non-BitPod execution context
