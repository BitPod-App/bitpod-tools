# Bootstrap Closure Gates Matrix v1

Status: Working baseline  
Linked issue: [BIT-95 — Define bootstrap closure gates for Taylor-real, minimum-team-ready, Discord acceptance, and startup-ready](https://linear.app/bitpod-app/issue/BIT-95/define-bootstrap-closure-gates-for-taylor-real-minimum-team-ready)

## Purpose

Separate the bootstrap proof thresholds that have been getting conflated:

- Taylor operationally real as orchestrator
- Taylor conversationally real to CJ
- Taylor implemented as a real AI agent rather than only an orchestrator contract
- at least one specialist implemented as a real AI agent rather than only a lane/skill proxy
- minimum Phase 4 team ready
- real multi-agent team loop exists in practice
- real Discord/session-surface acceptance
- overall startup-ready

## Current closure gates

| Closure event | Meaning | Current verdict | Certainty | Primary evidence | Milestone owner | Notes |
|---|---|---|---|---|---|---|
| Taylor operational orchestrator = true | Taylor decomposes, routes, and closes real work with artifact/evidence flow | `true` | Verified | [BIT-84 — Prove Taylor orchestrator in a real multi-agent execution loop](https://linear.app/bitpod-app/issue/BIT-84/prove-taylor-orchestrator-in-a-real-multi-agent-execution-loop), `taylor-orchestrator-operational-proof-v1.md` | Phase 4 | This is the narrower orchestration proof, not the full conversational-agent proof |
| Taylor embodied AI agent = true | Taylor exists as a real operator-facing AI agent with runtime embodiment beyond narrow command routing or documentation-only orchestration | `false` | Verified as not yet proven | `taylor-real-agent-acceptance-contract-v1.md`, [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) | Phase 4 | This should be read as stronger than orchestrator proof and transport-agnostic |
| First specialist embodied AI agent = true | At least one non-Taylor specialist exists as a real AI agent/runtime, not only as a lane contract, skill alias, or human-proxy execution path | `false` | Verified as not yet proven | `phase4-real-multi-agent-team-acceptance-contract-v1.md`, [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill) | Phase 4 | This is the first honest specialist embodiment threshold needed for a real AI team claim |
| Minimum team ready = true | Taylor + QA lane + engineering lane exist in practice strongly enough to make later Discord acceptance meaningful | `true` | Verified | [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera), `minimum-phase4-agent-team-readiness-v1.md` | Phase 4 | Explicit merged repo verdict already exists: `MINIMUM_TEAM_READY=true` |
| Taylor conversationally real to CJ = true | CJ can speak to Taylor naturally as an agent, not only as a command surface or narrow skill proxy, in at least one live operator surface | `false` | Verified as not yet proven | `taylor-real-agent-acceptance-contract-v1.md`, [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) | Phase 4 | This should not be claimed from orchestrator proof alone and should not be made Discord-exclusive |
| Real multi-agent team loop = true | Taylor delegates real work to one or more embodied specialist AI agents, receives outputs back, and completes team execution as a team rather than as one agent plus documentation | `false` | Verified as not yet proven | `phase4-real-multi-agent-team-acceptance-contract-v1.md`, [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist) | Phase 4 | This is the stronger Phase 4 existence proof and should not be collapsed into minimum-team-ready |
| Discord real acceptance = true | Real Discord session surface supports intent, plans, decisions, artifact-linked updates, and usable Taylor interaction in live usage | `false` | Verified | `discord-real-acceptance-status-2026-03-12.md`, live evidence pack, [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) | Phase 4 | Discord may also serve as the proving surface for Taylor-real, but it is not the only logically valid one |
| Phase 4 complete = true | A real multi-agent AI team exists in practice, including Taylor plus at least one embodied specialist agent, and at least one real operator surface is accepted | `false` | Verified | open [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command), [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface), plus still-missing embodiment/team-loop proof | Phase 4 | Minimum-team-ready is a baseline prerequisite only, not the full closure condition |
| Phase 5 complete = true | Governance, memory, QA, and review controls operate at a hardened level rather than interim baseline | `false` | Verified | [BIT-89 — Mature reviewer routing from temporary bypass policy to intended GitHub governance](https://linear.app/bitpod-app/issue/BIT-89/mature-reviewer-routing-from-temporary-bypass-policy-to-intended), [BIT-91 — Raise governance, memory, and eval baseline artifacts to production-grade operations](https://linear.app/bitpod-app/issue/BIT-91/raise-governance-memory-and-eval-baseline-artifacts-to-production) remain open | Phase 5 | [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy) is now done and no longer a blocker |
| Startup ready = true | BitPod can operate as a small AI-assisted startup with a real Taylor interface, working specialist lanes, usable communication surface, and enough polish/hardening that real user-facing feature work can be delivered smoothly by the team | `false` | Inferred | requires combined satisfaction of critical Phase 3 + 4 + 5 gates | Phase 5 | Startup-ready belongs inside Phase 5, not inside minimum-team proof |

## Recommended milestone placement

### Phase 4 should own

- Taylor operational orchestrator proof
- Taylor embodied AI-agent proof
- first specialist embodied AI-agent proof
- minimum team readiness
- Taylor conversational reality to CJ
- real multi-agent team loop proof
- real Discord/session-surface acceptance
- closure of the session-surface execution chain:
  - [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)
  - [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform)
  - [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify)

### Phase 5 should own

- reviewer-routing maturity beyond interim bypass policy:
  - [BIT-89 — Mature reviewer routing from temporary bypass policy to intended GitHub governance](https://linear.app/bitpod-app/issue/BIT-89/mature-reviewer-routing-from-temporary-bypass-policy-to-intended)
- production-grade governance/memory/eval operations:
  - [BIT-91 — Raise governance, memory, and eval baseline artifacts to production-grade operations](https://linear.app/bitpod-app/issue/BIT-91/raise-governance-memory-and-eval-baseline-artifacts-to-production)
- the startup-ready claim itself:
  - the point where the real AI team is not only operational, but also smooth, reliable, and ready for sustained user-facing feature delivery
- preservation/maturation work that strengthens future agent embodiment without being required for minimum team proof:
  - [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for)

### Phase 3 still matters for startup-ready

The following are not Phase 4 blockers, but they remain relevant to a truthful startup-ready claim:

- [BIT-49 — Lock down personal GitHub account to human-only access (remove AI/runtime paths)](https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove)
  - recommended startup-ready blocker
- [BIT-74 — Execute post-bootstrap local scope hardening window after migration closeout](https://linear.app/bitpod-app/issue/BIT-74/execute-post-bootstrap-local-scope-hardening-window-after-migration)
  - relevant hardening gate, but weaker startup-ready blocker than BIT-49

## Recommended interpretation

Use these phrases precisely:

- `Taylor operationally real`:
  - proven by Phase 4 orchestrator evidence
- `Taylor embodied AI agent`:
  - proven only when Taylor exists as a usable operator-facing runtime beyond narrow command routing
- `specialist embodied AI agent`:
  - proven only when at least one non-Taylor specialist exists as a real runtime/agent rather than only a contract, skill alias, or execution lane
- `Taylor true AI agent to CJ`:
  - proven only when CJ has a real conversational interaction and judges it usable as an agent surface
  - may be proven in Discord, Zulip, Codex chat, or another live operator surface
- `minimum team ready`:
  - proven and already separate from Taylor-conversational truth
  - not enough by itself to close Phase 4
- `real multi-agent team`:
  - proven only when Taylor plus at least one embodied specialist agent complete real delegated work as a team
- `startup ready`:
  - belongs to the successful close of Phase 5
  - requires:
    - Phase 4 closed honestly
    - Phase 5 hardening/polish gates closed
    - critical residual Phase 3 security/hardening gaps no longer undermine normal operation

## Recommended next closeout sequence

1. prove [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
2. prove [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill) and [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
3. close [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)
4. let Discord closure finish [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform) and [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify)
5. complete Phase 5 hardening blockers:
   - [BIT-89 — Mature reviewer routing from temporary bypass policy to intended GitHub governance](https://linear.app/bitpod-app/issue/BIT-89/mature-reviewer-routing-from-temporary-bypass-policy-to-intended)
   - [BIT-91 — Raise governance, memory, and eval baseline artifacts to production-grade operations](https://linear.app/bitpod-app/issue/BIT-91/raise-governance-memory-and-eval-baseline-artifacts-to-production)
6. close the strongest residual Phase 3 startup-risk item:
   - [BIT-49 — Lock down personal GitHub account to human-only access (remove AI/runtime paths)](https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove)
7. then execute the Phase 5 startup-readiness / polished-and-hardened evidence pack
