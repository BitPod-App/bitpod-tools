# Taylor01 Runtime Minimum v1

Status: Active minimum-floor baseline
Primary issue: [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract)
Related issues:
- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)

## Objective

Define the smallest runtime and embodiment surface that should count as "real
Taylor" in the current Claw v1 phase.

This is a target minimum. It is not a claim that the current shape is already
the final Taylor01 or Claw runtime.

## Current truth

- the current live Taylor runtime is the launcher-backed Mini runtime under the
  `taylor01` execution account
- the MacBook remains the control console, not the primary execution host
- the current early OpenClaw reality is the operator contract layered over the
  live Taylor01 runtime path on the Mini
- current local `SKILL.md` operator surfaces are useful but transitional
- Taylor-real acceptance and OpenClaw proof remain open even though basic Mini
  bring-up is now real

## v1 embodiment rule

Taylor01 v1 does not need to be a final standalone Claw product package.

Acceptable v1 forms include:

- a live launcher-backed Taylor runtime on the execution node
- a thin runtime wrapper that exposes a real operator-facing intake path
- a current OpenClaw contract layered over the live Taylor runtime

What matters for v1 is that Taylor exists as a continuity-bearing runtime and
not only as:

- planning doctrine
- a local skill overlay
- transport-specific command plumbing
- a repo-local abstraction with no live execution boundary

## Minimum required runtime surfaces

To count as "real Taylor," all must be true:

1. there is a real execution boundary separate from the control console
2. there is a supported bring-up path for the runtime
3. there is at least one truthful live operator surface
4. the runtime can carry enough continuity to answer beyond a narrow command
   verb loop
5. durable outcomes can be written back to repo or issue truth surfaces

## Pass/fail gate

Record the floor as:

- `TAYLOR_RUNTIME_MINIMUM_V1=true` only when all five required runtime surfaces
  above are true
- `TAYLOR_RUNTIME_MINIMUM_V1=false` if any required surface fails or cannot be
  verified honestly

If the verdict is false, Taylor-real or Claw-runtime claims must downgrade with
the failing condition named explicitly.

## Required boundaries

### Execution boundary

- runtime work executes in the Taylor execution environment, not only in the
  operator's local shell/chat surface
- the execution boundary may still be thin, but it must be real

### Bring-up path

- runtime must have a supported launcher or equivalent intentional start path
- ad hoc direct invocation may remain useful for debugging, but it is not the
  durable operator contract by itself

### Operator surface

- at least one operator surface must be usable truthfully for real interaction
- the surface does not need to be final or transport-exclusive
- the operator surface must not be confused with the whole runtime boundary

### Durable truth path

- outcomes must materialize into repo-owned artifacts, issue updates, or other
  durable truth surfaces
- transport threads alone do not satisfy this requirement

## What does not count

These do not count as sufficient runtime embodiment by themselves:

- `SKILL.md` packaging alone
- a local Codex or chat skill overlay with no separate execution boundary
- a planning document that describes Taylor but does not back a live runtime
- transport-only bot plumbing without continuity-bearing runtime behavior
- a local shell sequence that can be run once but has no supported operating
  path

## Required acceptance signal

The runtime minimum is satisfied only when both are true:

- the runtime floor above is met
- a real operator acceptance pass exists strongly enough to support
  `TAYLOR_REAL_AI_AGENT=true|false`

The runtime minimum is therefore necessary but not sufficient for full Claw v1
closure.

## Constraint on active proof tickets

### For [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)

- BIT-97 must not pass from local `SKILL.md`, Codex chat, or command-only
  overlay behavior by itself
- the proving surface must be backed by a runtime that satisfies this floor

### For [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)

- BIT-115 must prove the control-console to HQ-runtime split rather than a
  local MacBook shortcut
- the proof must materialize durable outcomes back to repo or issue truth
  surfaces, not only a transport thread

## Transitional allowances

The following may remain transitional in v1:

- current `SKILL.md` compatibility installs
- current OpenClaw-over-Taylor-runtime layering
- temporary local overlays used around the operator path
- current BitPod-specific doctrine surrounding the operator contract

These may survive during v1, but they should not define the durable Taylor01
identity.

## Fail-closed cases

Do not count Taylor as runtime-real if any of these are true:

1. runtime only exists on the control console
2. bring-up requires undocumented or one-off shell memory
3. operator interaction is only a narrow command proxy with no continuity
4. durable result materialization is missing
5. the claimed runtime is only a local overlay or planning abstraction

## Relationship to Claw v1

This runtime minimum does not decide the full scope of Claw v1.

It only defines the floor below which Claw claims should not be treated as
runtime-real.

Claw v1 may still be narrower than a final Taylor platform and broader than the
runtime minimum alone.

## Recommended implementation order

1. keep the live Mini runtime truthful and stable
2. use the runtime minimum to constrain Taylor-real acceptance work
3. use the first honest OpenClaw proof to test the operator/runtime split
4. decide the broader Claw v1 boundary only after the runtime floor is locked
5. decide the final capability container later
