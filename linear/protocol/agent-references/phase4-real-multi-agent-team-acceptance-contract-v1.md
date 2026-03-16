# Phase 4 Real Multi-Agent Team Acceptance Contract v1

Date: 2026-03-12  
Related issues:
- [BIT-95 — Define bootstrap closure gates for Taylor-real, minimum-team-ready, Discord acceptance, and startup-ready](https://linear.app/bitpod-app/issue/BIT-95/define-bootstrap-closure-gates-for-taylor-real-minimum-team-ready)
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)

## Objective

Define the stronger Phase 4 existence proof for an AI-agent team that is real in practice, without pulling Phase 5 smoothness, hardening, or startup-ready quality into the same gate.

## Core rule

- Phase 4 is an existence proof, not a polish proof.
- Phase 4 is not complete if only Taylor is real.
- Phase 4 is not complete if specialists exist only as lane contracts, skills, or human-proxy execution paths.

## Required pass conditions

Pass only if all are true:

- `TAYLOR_EMBODIED_AI_AGENT=true`
- `AT_LEAST_ONE_SPECIALIST_EMBODIED_AI_AGENT=true`
- `REAL_MULTI_AGENT_TEAM_LOOP=true`
- `AT_LEAST_ONE_OPERATOR_SURFACE_ACCEPTED=true`

## Meaning of each condition

### `TAYLOR_EMBODIED_AI_AGENT=true`

- Taylor exists as a usable AI agent/runtime beyond documentation-only orchestration and beyond a narrow command bot.
- Taylor can be interacted with directly by CJ in at least one live operator surface.

### `AT_LEAST_ONE_SPECIALIST_EMBODIED_AI_AGENT=true`

- At least one non-Taylor specialist exists as a real AI runtime/agent.
- The specialist does more than route into a static skill or template.
- The specialist can receive a delegated task, perform bounded work, and return a result artifact or verdict.

### `REAL_MULTI_AGENT_TEAM_LOOP=true`

- Taylor delegates real work to at least one embodied specialist agent.
- The specialist returns output back into the team flow.
- Taylor uses that output to continue, verify, synthesize, or close the work.
- The observed behavior is honestly a team loop, not just one operator surface with helper documentation.

### `AT_LEAST_ONE_OPERATOR_SURFACE_ACCEPTED=true`

- At least one live operator surface is proven usable for real team operation.
- This may be Discord or another honest operator surface.
- Surface-specific quality and smoothness beyond the first accepted surface belong mostly to Phase 5.

## Explicit non-goals for this contract

This contract does not require:

- polished or delightful conversation quality
- strong reliability under repeated load
- hardened governance/reviewer routing
- startup-ready smoothness
- multiple communication surfaces all passing

Those are Phase 5 concerns unless they block the basic truth of team existence.

## Current truth

- `Verified`: Taylor operational orchestrator proof exists.
- `Verified`: minimum team readiness proof exists.
- `Verified`: Taylor embodied AI-agent truth is not yet proven.
- `Verified`: specialist embodied AI-agent truth is not yet proven.
- `Verified`: real multi-agent team-loop proof is not yet proven.
- `Verified`: Discord transport baseline exists, but Discord acceptance is still open.
