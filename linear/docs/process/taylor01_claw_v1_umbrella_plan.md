# Taylor01 Claw v1 Umbrella Plan

Status: Active checklist plan
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

Use this as the latest active retained plan for the Bootstrap/Taylor01 Claw
reconciliation lane.

## Current truth

- `/Users/cjarguello/BitPod-App` is a local container of standalone repos.
- active repo parity is clean enough to proceed; remaining forced T3 fracture
  is review-gated PR residue, not active branch divergence
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

## New Linear lanes created

These were created from `taylor01_claw_v1_linear_issue_packet.md` on
2026-03-30:

1. [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract)
2. [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary)
3. [BIT-216 — Taylor01: decide capability container direction beyond current `SKILL.md`](https://linear.app/bitpod-app/issue/BIT-216/taylor01-decide-capability-container-direction-beyond-current-skillmd)
4. [BIT-217 — Taylor01: classify current artifacts by durability and overlay status](https://linear.app/bitpod-app/issue/BIT-217/taylor01-classify-current-artifacts-by-durability-and-overlay-status)
5. [BIT-218 — Taylor01: define future dedicated repo extraction trigger for Claw](https://linear.app/bitpod-app/issue/BIT-218/taylor01-define-future-dedicated-repo-extraction-trigger-for-claw)

## Current structure alignment

- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
  remains the single architecture owner and stays under
  [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
  plus [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract),
  [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary),
  [BIT-216 — Taylor01: decide capability container direction beyond current `SKILL.md`](https://linear.app/bitpod-app/issue/BIT-216/taylor01-decide-capability-container-direction-beyond-current-skillmd),
  [BIT-217 — Taylor01: classify current artifacts by durability and overlay status](https://linear.app/bitpod-app/issue/BIT-217/taylor01-classify-current-artifacts-by-durability-and-overlay-status),
  [BIT-218 — Taylor01: define future dedicated repo extraction trigger for Claw](https://linear.app/bitpod-app/issue/BIT-218/taylor01-define-future-dedicated-repo-extraction-trigger-for-claw),
  and [BIT-235 — Plan: Taylor01-HQ org-agnostic local environment and bootstrap boundary](https://linear.app/bitpod-app/issue/BIT-235/plan-taylor01-hq-org-agnostic-local-environment-and-bootstrap-boundary)
  are now aligned under the Taylor01 Phase 4 Claw lane
- [BIT-113 — Phase 3 evidence pack and HQ go/no-go](https://linear.app/bitpod-app/issue/BIT-113/phase-3-evidence-pack-and-hq-gono-go)
  is now the explicit Phase 3 closeout child under
  [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
- [BIT-220 — Plan: Normalize T3 local-workspace zone taxonomy and lean-profile semantics](https://linear.app/bitpod-app/issue/BIT-220/plan-normalize-t3-local-workspace-zone-taxonomy-and-lean-profile)
  and children remain Bootstrap cleanup/meta framing rather than Taylor01
  architecture work

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

1. Close Bootstrap Phase 3 truthfully through
   [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
   plus [BIT-113 — Phase 3 evidence pack and HQ go/no-go](https://linear.app/bitpod-app/issue/BIT-113/phase-3-evidence-pack-and-hq-gono-go).
2. Lock only the minimum architecture floor under
   [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture):
   [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract),
   [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary),
   and [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters).
   Current working baselines: `taylor01_runtime_minimum_v1.md` and
   `claw_v1_boundary_model_v1.md`.
3. Start the real proof lane immediately after the floor is locked through
   [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
   and [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface).
   Activate [BIT-101 — Implement Taylor as a portable embodied AI agent/runtime beyond deterministic bot flows](https://linear.app/bitpod-app/issue/BIT-101/implement-taylor-as-a-portable-embodied-ai-agentruntime-beyond)
   only if the current runtime cannot satisfy those proofs honestly.
4. Use proof results to refine the future-facing Taylor01 lanes:
   [BIT-216 — Taylor01: decide capability container direction beyond current `SKILL.md`](https://linear.app/bitpod-app/issue/BIT-216/taylor01-decide-capability-container-direction-beyond-current-skillmd),
   [BIT-217 — Taylor01: classify current artifacts by durability and overlay status](https://linear.app/bitpod-app/issue/BIT-217/taylor01-classify-current-artifacts-by-durability-and-overlay-status),
   [BIT-218 — Taylor01: define future dedicated repo extraction trigger for Claw](https://linear.app/bitpod-app/issue/BIT-218/taylor01-define-future-dedicated-repo-extraction-trigger-for-claw),
   and [BIT-235 — Plan: Taylor01-HQ org-agnostic local environment and bootstrap boundary](https://linear.app/bitpod-app/issue/BIT-235/plan-taylor01-hq-org-agnostic-local-environment-and-bootstrap-boundary).
5. Keep
   [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
   and [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
   deferred until the proof lane is strong enough and
   [BIT-173 — Final legacy secret removal and 1Password cutover gate before AI agent operability](https://linear.app/bitpod-app/issue/BIT-173/final-legacy-secret-removal-and-1password-cutover-gate-before-ai-agent)
   is complete.

## Active checklist

### Bootstrap Phase 3 closeout

- [ ] Reconcile [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
  against current `taylor01` / MacBook-control-console / Mini-runtime truth.
- [ ] Advance [BIT-113 — Phase 3 evidence pack and HQ go/no-go](https://linear.app/bitpod-app/issue/BIT-113/phase-3-evidence-pack-and-hq-gono-go)
  as the explicit closeout owner.
- [ ] Assemble evidence from
  [BIT-105 — Execution HQ architecture decisions and boundary guardrails](https://linear.app/bitpod-app/issue/BIT-105/execution-hq-architecture-decisions-and-boundary-guardrails),
  [BIT-106 — Mac Mini remote access and execution-HQ foundation](https://linear.app/bitpod-app/issue/BIT-106/mac-mini-remote-access-and-execution-hq-foundation),
  [BIT-108 — Execution-HQ workspace bootstrap and lightweight local-workspace profile](https://linear.app/bitpod-app/issue/BIT-108/execution-hq-workspace-bootstrap-and-lightweight-local-workspace),
  [BIT-109 — Execution-HQ runtime, integrations, secrets, and dependency setup](https://linear.app/bitpod-app/issue/BIT-109/execution-hq-runtime-integrations-secrets-and-dependency-setup),
  and [BIT-110 — Validate first AI HQ runtime path and complete first truthful smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/validate-first-ai-hq-runtime-path-and-complete-first-truthful-smoke).
- [ ] Disposition [BIT-49 — Lock down personal GitHub account to human-only access (remove AI/runtime paths)](https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove)
  and [BIT-74 — Execute post-bootstrap local scope hardening window after migration closeout](https://linear.app/bitpod-app/issue/BIT-74/execute-post-bootstrap-local-scope-hardening-window-after-migration)
  for truthful Phase 3 closeout.
- [ ] Record the explicit Phase 3 go/no-go verdict.

### Minimum architecture floor

- [ ] Lock [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract).
- [ ] Lock [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary).
- [ ] Lock [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters).

### First proof lane

- [ ] Run [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop).
- [ ] Run [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface).
- [ ] Activate [BIT-101 — Implement Taylor as a portable embodied AI agent/runtime beyond deterministic bot flows](https://linear.app/bitpod-app/issue/BIT-101/implement-taylor-as-a-portable-embodied-ai-agentruntime-beyond)
  only if the current runtime cannot satisfy those proofs honestly.

### Proof-informed refinement

- [ ] Refine [BIT-216 — Taylor01: decide capability container direction beyond current `SKILL.md`](https://linear.app/bitpod-app/issue/BIT-216/taylor01-decide-capability-container-direction-beyond-current-skillmd).
- [ ] Refine [BIT-217 — Taylor01: classify current artifacts by durability and overlay status](https://linear.app/bitpod-app/issue/BIT-217/taylor01-classify-current-artifacts-by-durability-and-overlay-status).
- [ ] Refine [BIT-218 — Taylor01: define future dedicated repo extraction trigger for Claw](https://linear.app/bitpod-app/issue/BIT-218/taylor01-define-future-dedicated-repo-extraction-trigger-for-claw).
- [ ] Refine [BIT-235 — Plan: Taylor01-HQ org-agnostic local environment and bootstrap boundary](https://linear.app/bitpod-app/issue/BIT-235/plan-taylor01-hq-org-agnostic-local-environment-and-bootstrap-boundary).

### Later embodiment gates

- [ ] Execute [BIT-173 — Final legacy secret removal and 1Password cutover gate before AI agent operability](https://linear.app/bitpod-app/issue/BIT-173/final-legacy-secret-removal-and-1password-cutover-gate-before-ai-agent).
- [ ] Run [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist).
- [ ] Run [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill).

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
