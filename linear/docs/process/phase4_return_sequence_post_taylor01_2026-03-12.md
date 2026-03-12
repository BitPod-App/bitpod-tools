# Phase 4 Return Sequence Post-Taylor01 — 2026-03-12

Status: Active
Primary issue: [BIT-95 — Define bootstrap closure gates for Taylor-real, minimum-team-ready, Discord acceptance, and startup-ready](https://linear.app/bitpod-app/issue/BIT-95/define-bootstrap-closure-gates-for-taylor-real-minimum-team-ready)
Related issues:
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)
- [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for)
- [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent)
- [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)

## Purpose

Return the active bootstrap focus to the pre-Taylor01 near-term Phase 4 execution gates while preserving the new Taylor01 portability rules as operating constraints rather than as the main workstream.

## Verified starting point

- [PR #50 — [BIT-100] Implement Taylor01 co-equal product boundary BIT-100](https://github.com/BitPod-App/bitpod-tools/pull/50) is merged.
- [PR #49 — [BIT-96][BIT-97] Normalize Taylor-real vs Discord acceptance BIT-96 BIT-97](https://github.com/BitPod-App/bitpod-tools/pull/49) is merged.
- Taylor01 now exists as a separate project and policy boundary, but it is no longer the primary active execution lane.
- Phase 4 is still not complete.
- The stronger Phase 4 existence gates now on `main` are:
  - Taylor embodied AI agent
  - first specialist embodied AI agent
  - real multi-agent team loop
  - at least one accepted operator surface

## Return-to-execution sequence

### 1. Immediate active lane: Taylor-real

Make [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) the immediate active gate.

Rule:

- do not wait for Discord if another surface can prove or fail Taylor-real faster
- prove or falsify Taylor-real first in the fastest honest live surface available

Why first:

- Taylor-real is a direct missing truth gate
- current evidence still proves only Taylor operational orchestration, not embodied agent reality to CJ

### 2. First specialist embodiment: Vera path

Use Vera as the recommended first specialist embodiment path.

Primary lane:

- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)

Support lane:

- [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for)

Why Vera first:

- current QA lane already exists and is real at a lane level
- Vera has preserved skill/runtime continuity that engineering specialist lanes do not yet have as strongly
- Zulip-era behavior inventory makes Vera the fastest plausible path to first specialist embodiment

### 3. Real team proof

After Taylor-real and first specialist embodiment, prove:

- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)

Recommended first proof shape:

- Taylor delegates bounded QA-relevant work to embodied Vera
- Vera returns result artifact or verdict
- Taylor uses the returned output to synthesize or close the work

This is the first honest team-existence proof.

### 4. Discord acceptance after the above

Keep [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) active, but treat it as the session-surface gate after the stronger agent/team existence gates are materially underway.

Discord-specific intake/runtime path remains:

- [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent)

Rule:

- do not let Discord block Taylor-real if another live surface can answer the question first
- use Discord to close the session-surface proof once the underlying agent reality is closer to true

## Taylor01 constraint while executing

Use the Taylor01 rules as constraints, not as the main workstream:

- solve portability now by default when reasonable
- if not now, use explicit temporary bypass
- keep bypasses short-lived and reviewable
- do not turn temporary coupling into vague long-lived backlog

Relevant artifacts:

- `linear/docs/process/taylor01_portability_review_gate_v1.md`
- `linear/docs/process/taylor01_active_bypass_register_v1.md`

## Recommended issue states

- [BIT-95 — Define bootstrap closure gates for Taylor-real, minimum-team-ready, Discord acceptance, and startup-ready](https://linear.app/bitpod-app/issue/BIT-95/define-bootstrap-closure-gates-for-taylor-real-minimum-team-ready) -> `Done`
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) -> `In Progress`
- [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for) -> `Todo`
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill) -> `Todo`
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist) -> `Todo`
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) -> remain `In Progress`

