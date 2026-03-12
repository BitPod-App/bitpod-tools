# Taylor Real Agent Acceptance Contract v1

Date: 2026-03-12  
Primary issue: [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)  
Related issues:
- [BIT-95 — Define bootstrap closure gates for Taylor-real, minimum-team-ready, Discord acceptance, and startup-ready](https://linear.app/bitpod-app/issue/BIT-95/define-bootstrap-closure-gates-for-taylor-real-minimum-team-ready)
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)
- [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent)

## Objective

Define the minimum truthful pass/fail gate for whether Taylor is implemented strongly enough to count as a real AI agent to CJ.

This contract is necessary for Phase 4, but it is not sufficient for full Phase 4 closure by itself.

## Core rule

- Taylor-real is not transport-exclusive.
- Proof may happen in any live operator surface:
  - Discord
  - Zulip
  - Codex chat
  - another live operator surface if used honestly
- Discord remains a valid and likely preferred proving surface, but it should not be the only logically accepted one.

## Minimum pass criteria

Pass only if all are true:

- CJ has at least one real conversational exchange with Taylor in a live operator surface.
- The exchange goes beyond a narrow command/reply loop.
- Taylor responds as a grounded, continuity-bearing, useful agent.
- Taylor can handle broad BitPod-relevant conversation rather than only specialist command verbs.
- CJ can make an explicit operator judgment that Taylor felt agent-real.

## Required operator verdict

- `TAYLOR_REAL_AI_AGENT=true|false`

## Fast baseline check

A lightweight early check is desirable before deeper transport work.

Use any live operator surface and run one short exchange with:

- one open-ended planning or status question
- one follow-up clarification turn
- one judgment about whether Taylor felt like a real agent versus a narrow wrapper

This quick check does not replace the fuller acceptance note, but it is a good early truth signal.

## Relationship to Discord work

- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) remains the Discord/session-surface closure gate.
- [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent) remains the Discord-specific intake/runtime path lane.
- A Taylor-real pass in Discord may satisfy both Taylor-real and part of Discord acceptance.
- A Taylor-real pass in Zulip or Codex chat may satisfy Taylor-real without satisfying Discord acceptance.

## Relationship to Phase 4 closure

- A Taylor-real pass is only one part of honest Phase 4 closure.
- Phase 4 also requires at least one specialist embodied AI agent and a real multi-agent team loop.
- Those stronger team-existence conditions are defined separately in `phase4_real_multi_agent_team_acceptance_contract_v1.md`.

## Current truth

- `Verified`: Taylor operational orchestrator proof exists.
- `Verified`: minimum team proof exists.
- `Verified`: Taylor-real to CJ is not yet proven by an explicit acceptance artifact.
- `Verified`: Taylor-real alone would still not be enough to close Phase 4.
- `Verified`: Discord baseline transport proof exists.
- `Verified`: Discord acceptance remains open.
- `Verified`: the current `bitpod-tools/gpt_bridge` team-chat surface does not implement a Taylor responder path yet; `@taylor` is logged, but only `@gpt` is actually relayed.
- `Verified`: Zulip historical evidence proves Taylor existed as a real responding workflow bot/runtime there, but does not yet prove broad conversational agent reality to CJ.
