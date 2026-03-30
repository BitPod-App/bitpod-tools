# Taylor01 Claw v1 Umbrella Plan

Status: Active planning canon
Primary issue: [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
Related issues:
- [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Define the current umbrella-level plan for Taylor01 Claw v1 without letting
BitPod-local overlays, `bitpod-tools` scaffolding, or current `SKILL.md`
compatibility surfaces harden into the final Taylor capability model.

This is a planning surface only. The umbrella path is not a git repo.

## Current truth

- `/Users/cjarguello/BitPod-App` is a local container of standalone repos.
- active repo parity is clean enough to proceed; current forced T3 failure is
  cleanup residue, not active branch divergence
- `taylor01-skills` is the portable Taylor substrate repo
- `bitpod-tools` remains the owning repo for active BitPod-specific doctrine,
  checkpoints, overlays, and the current OpenClaw/Taylor boundary canon
- `bitpod-taylor-runtime` is the current runtime and embodiment lane
- current local `SKILL.md` operator surfaces are useful but transitional
- the Taylor01 runtime on `mini-01` is now real enough that Claw should be
  defined intentionally instead of emerging accidentally from local overlays

## Claw v1 boundary model

Claw v1 should be treated as a narrow first version made of:

- an operator intake and dispatch surface
- a runtime wrapper over the live Taylor01 execution path
- a minimum embodiment contract for what counts as "real Taylor"
- an explicit capability-container decision space that is not yet locked

Claw v1 should not be treated yet as:

- a final standalone Taylor product package
- a proof that `SKILL.md` is the durable capability container
- a reason to collapse current repo boundaries prematurely

## Durable boundary assumptions

### Portable core

- truthfulness and degraded-state semantics
- provenance and review metadata
- authority and auth boundaries
- assessment versus execution separation
- generic reference-pack support
- portable capability-package metadata

### Runtime and embodiment

- the current live Taylor01 runtime on the Mini
- the launcher-backed execution path
- the minimum runtime contract required for "real Taylor"
- the first honest OpenClaw embodiment proof

### Policy and authority

- Taylor01 operating norms that travel across products
- trust and approval boundaries
- truth-label and evidence expectations

### Adapters

- operator-surface and system-adapter contracts
- communication surface mappings
- future non-BitPod system integrations

### Customer-local overlays

- BitPod-specific Linear doctrine
- BitPod checkpoints and local execution overlays
- local workspace conventions that should not be promoted into Taylor core

## Transitional versus durable split

### Durable now

- `taylor01-skills` portable service, auth, truthfulness, and provenance
  substrate
- Taylor portability boundary framing
- OpenClaw operator truth split
- Mini execution-account runtime bring-up path

### Transitional now

- current `SKILL.md` packaging and install surfaces
- current local operator overlays
- current OpenClaw-over-Taylor-runtime shape
- Taylor-related portability scaffolding still living in `bitpod-tools`
  outside the active doctrine role

### BitPod-local overlay now

- active Linear doctrine and guide surfaces
- checkpoints and closeout packs
- local execution overlays and BitPod-specific process truth

## Existing Linear lanes to use

- [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
  owns portability boundary and future extraction trigger logic
- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
  owns the Claw v1 architecture decision pack
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
  owns Taylor-side operator surface and adapter boundary
- [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
  owns the current OpenClaw operator contract
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
  owns the first honest embodiment proof through the current MacBook-to-Mini
  path
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
  owns the minimum acceptance proof that Taylor is more than a local overlay
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
  remains deferred behind Taylor-real and OpenClaw embodiment proof
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
  remains deferred until the Claw embodiment surface is stronger

## Missing Linear lanes to create

Create these as new issues instead of overloading the current proof lanes:

Use `taylor01_claw_v1_linear_issue_packet.md` as the creation packet for the
exact issue payloads.

1. `Lock minimum real-Taylor runtime contract`
   - define the minimum active runtime required to count as "real Taylor"
   - output one explicit runtime contract with required surfaces, execution
     boundary, persistence expectations, and exclusion of pure local skill
     overlay behavior

2. `Decide Claw (v1) scope and boundary`
   - decide whether Claw v1 is primarily an operator surface contract, runtime
     wrapper, embodiment contract, or a narrow combination
   - output one short boundary model with explicit non-goals

3. `Decide Taylor capability container direction`
   - evaluate `SKILL.md`, `sould.md`, manifest-first package, or another
     explicit alternative
   - keep current `SKILL.md` surfaces marked transitional until this is locked

4. `Classify current Taylor artifacts by durability`
   - classify current work across `bitpod-tools`, `bitpod-taylor-runtime`, and
     `taylor01-skills` into durable substrate, transitional compatibility, and
     BitPod/local overlay

5. `Define future dedicated repo extraction trigger for Taylor01 Claw`
   - keep the future repo name open
   - define the extraction trigger and what content should move when the
     trigger is met

## Repo-boundary recommendation

- `taylor01-skills`
  - portable substrate repo
  - owns generic service, auth, truthfulness, provenance, and capability
    package substrate
  - should not be overclaimed yet as the full Claw repo

- `bitpod-tools`
  - BitPod-specific doctrine, checkpoints, overlays, adapter-local doctrine,
    and current OpenClaw/Taylor boundary canon
  - most Taylor-related material here should be treated as transitional unless
    it is clearly current doctrine or overlay truth

- `bitpod-taylor-runtime`
  - runtime and embodiment lane
  - owns the current live Taylor runtime and the minimum path to embodied proof

- future dedicated repo
  - justified only after runtime and container boundaries lock
  - should be used for durable Claw hardening rather than premature migration

## Minimum implementation sequence

1. Lock the minimum runtime contract for "real Taylor" under
   [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
   plus a new runtime-contract issue.
2. Lock the narrow scope and non-goals of Claw v1 in a dedicated boundary
   issue.
3. Classify current Taylor artifacts by durability before broad extraction or
   cleanup.
4. Keep the first embodiment lane on
   [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface),
   [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop),
   and [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface).
5. Keep
   [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
   and [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
   deferred until the runtime and Claw v1 boundaries are locked.
6. Use the capability-container and extraction-trigger lanes only after the
   above architecture and embodiment decisions settle.

## Decisions that must be locked before broad implementation

- the minimum runtime contract for "real Taylor"
- the exact scope of Claw v1
- whether current `SKILL.md` packaging remains only transitional
- which `bitpod-tools` artifacts are current doctrine versus portable substrate
  candidates
- the trigger for creating a dedicated Taylor01 or Taylor01-Claw repo

## Working rule

Do not let active BitPod overlays or current local compatibility surfaces
silently become Taylor defaults.
