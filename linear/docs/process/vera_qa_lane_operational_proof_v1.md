# Vera QA Lane Operational Proof v1

Status: Retained proof (inactive by default)  
Linked issue: [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy)

## Objective

Prove or reject the claim that the dedicated Vera-style QA lane now exists in real work beyond the interim [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy).

## Verdict

Verdict: `PASS_WITH_LIMITS`

Interpretation:

- a dedicated QA lane now exists with a distinct contract and a real evidence artifact
- the lane is strong enough to become the primary definition of technical QA in current Phase 4 work
- GitHub merge governance is still not fully independent, so the interim [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) cannot be retired yet

## What Was Missing Before

Prior repo truth already showed:

- QA evidence existed
- QA affected closeout decisions
- the working model was still explicitly interim rather than a dedicated Vera-style lane

That gap was documented in:

- [specialist_operating_lanes_proof_v1.md](./specialist_operating_lanes_proof_v1.md)
- [interim_ai_technical_qa_cj_acceptance_policy_v1.md](./interim_ai_technical_qa_cj_acceptance_policy_v1.md)

The stronger QA behavior now lives in Vera's dedicated QA contract and is currently implemented through the local skill surface:

- canonical local surface:
  - `$WORKSPACE/local-workspace/local-codex/skills/qa-specialist/SKILL.md`

Taylor's current skill now explicitly delegates final QA verification execution to `qa-specialist`, which is why BIT-90 should anchor to Vera's artifact contract rather than Taylor-style review behavior.

That does not mean Vera should remain only a skill long-term. The skill is an acceptable transitional backing for the QA lane while a fuller Vera agent/runtime is still missing.

## Real Execution Record Used For Proof

### Chain

1. [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera) identified a remaining minimum-team blocker: no true Vera-style QA lane yet.
2. Taylor-style routing selected [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy) as the next concrete lane.
3. The repo package for BIT-90 created:
   - a dedicated QA lane contract
   - a Vera-style verification artifact
   - a checkpoint artifact tying the result back into the minimum-team lane
4. Vera issued an explicit verdict against acceptance criteria rather than generic implementation self-review.

### Durable artifacts produced in this execution

- contract:
  - `$WORKSPACE/bitpod-tools/linear/docs/process/vera_qa_lane_contract_v1.md`
- verification artifact:
  - `$WORKSPACE/bitpod-tools/linear/examples/verification_report_bit90_minimum_team_2026-03-12.md`
- lane checkpoint:
  - `$WORKSPACE/bitpod-tools/linear/docs/process/checkpoints/active_checkpoint_phase4_minimum_team_2026-03-12.md`
- validation command:
  - `bash linear/scripts/local_smoke.sh` -> `local smoke PASS`

## Authority note

This file is retained proof, not active execution policy. Treat the current
policy registry and explicitly promoted guide/contract surfaces as the active
authority layer.

## Why This Counts As A Dedicated QA Lane

The lane is no longer only an informal review style because it now has:

- a named contract with distinct boundaries
- a required evidence format aligned to `verification_report.md`
- a verdict-only identity for Vera
- a durable artifact linked to live Phase 4 work
- a transitional skill-backed implementation outside Taylor's planning lane

That crosses the line from "interim QA happens somewhere" to "the QA lane exists as an operating lane."

## Explicit Answer On Interim BIT-79 Policy

Can [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) be downgraded from primary reliance?

Answer: yes.

What changes now:

- primary technical QA definition: Vera dedicated QA lane contract + verification artifact flow
- fallback merge-governance rule: interim BIT-79 policy when GitHub reviewer-routing still requires CJ/admin bypass mechanics

What does not change yet:

- the repo still lacks a fully independent reviewer/merge authority path
- CJ acceptance and explicit risk acknowledgment may still be needed for branch-protection reality

## Limits

This proof does not claim:

- a fully separate GitHub approver identity
- automated reviewer-routing completion
- that [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera) is complete by QA alone

Remaining meaningful blockers after this lane:

- [BIT-93 — Stand up first engineering specialist lane under Taylor-led delegation](https://linear.app/bitpod-app/issue/BIT-93/stand-up-first-engineering-specialist-lane-under-taylor-led-delegation)
- later, after the minimum team is real enough, [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)

## Explicit Answer

Does a dedicated Vera-style QA lane now exist in practice beyond the interim policy?

Answer: yes, at a working-baseline level.

Can the interim policy be removed entirely?

Answer: no, not yet.

That is why the correct verdict is `PASS_WITH_LIMITS`, not `FAILED`, and not "fully independent."
