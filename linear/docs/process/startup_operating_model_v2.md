# BitPod Startup Operating Model v2

Version: v2
Status: Active
Owner: CJ (final authority), Taylor (operating orchestrator)
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Supersedes: `startup_operating_model_v1.md` for active use

## Purpose

Define how BitPod runs as an AI-assisted startup while explicitly recognizing Taylor01 as the reusable system being proven through BitPod execution.

## Dual-product framing

- BitPod App is the current product being built.
- Taylor01 is the reusable PM + AI team operating system being proven through BitPod.
- BitPod is the proving ground, not the owner of Taylor01 architecture.
- BitPod completion is not required to validate Taylor01's utility.

## Control rule

Taylor01 portability concerns may legitimately slow or redirect BitPod work when the alternative would create bad long-term coupling.

Taylor01 portability concerns do not require blocking all temporary coupling.

The rule is:

- portable by default
- temporary coupling only when explicit
- hidden coupling never
- solve portability now when reasonable
- if not now, review the exception soon rather than letting it become background backlog

## Scope

This document governs:

- agent/team topology and ownership boundaries
- planning/delegation/handoff flow
- QA and release authority
- evidence contract for status transitions
- operating cadence and controls
- Taylor01 portability review at BitPod decision points

This document does not define final brand canon, legal policy, or billing policy.

## Operating Topology

### Command Model

1. CJ is principal decision-maker and final approver for priority/scope shifts.
2. Taylor is lead PM orchestrator and dispatches execution work.
3. Specialists execute in bounded scopes and return evidence.
4. QA authority is independent from implementation.

### Role Contracts

- CJ (Principal Operator)
  - Sets strategy, approves non-trivial pivots, approves critical risk moves.
- Taylor (Orchestrator)
  - Decomposes work, sequences dependencies, assigns owners, enforces evidence.
- Engineering Specialist(s)
  - Implements code/infrastructure changes and produces reproducible verification.
- QA Specialist (Vera contract)
  - Produces independent PASS/FAIL verdict with explicit evidence.
- Design/Brand Specialist
  - Owns design-system and brand artifacts when explicitly in scope.
- Research/Analysis Specialist
  - Produces constrained research briefs with citations and recommendation quality bars.

## Execution Flow (Single Thread of Truth)

1. Intake: request enters Linear issue with objective, scope, required outputs.
2. Portability check: relevant issues are classified for Taylor01 portability before they are treated as ready.
   - if immediate portability work is not worth the interruption, use an explicit temporary bypass with reason and review trigger
   - significant active bypasses should be tracked in the Taylor01 active bypass register until closed or promoted
3. Plan: Taylor decomposes into atomic tasks with explicit dependencies.
4. Execute: specialists implement scoped changes only.
5. Verify: QA validates against acceptance criteria and evidence requirements.
6. Approve: PM/CJ gate checks pass/fail and transition rationale recorded.
7. Ship: merge/deploy with rollback note and artifact links.
8. Learn: postmortem/retro notes appended, not rewritten.

## Evidence Contract (Required Before Done)

Every completion claim must include:

- status line (`from -> to`) and transition reason
- commands/UI checks executed
- artifact path(s) or URL(s)
- pass/fail by gate
- known risks and follow-up
- Taylor01 Portability Check when relevant

Status-only updates are non-authoritative without evidence.

## Portability Review Gate

Use the Taylor01 portability review gate for:

- agents
- workflows
- process docs
- workspace policy
- tool integration behavior

Do not assume a reusable behavior belongs to BitPod merely because BitPod is the proving ground.

Experimental and fast-moving work may use a temporary bypass, but the bypass must be visible and reviewable.

## Delegation + Handoff Protocol

Each delegated task must contain:

- objective
- in-scope/out-of-scope
- acceptance checks
- expected artifact destination
- rollback expectation
- blocker escalation path

Handoff closes only when receiver confirms reproducibility from supplied evidence.

## QA Authority Model

- QA is an independent gate, not an implementation rubber-stamp.
- No `Done` state without QA result and PM acceptance as configured.
- Merge/deploy gates fail closed on missing QA/PM signals.

## Capability-State + Truth Labels

All critical operational claims should be classified:

- Verified: directly checked with current evidence.
- Inferred: likely true, not fully validated.
- Unknown: insufficient evidence.

When capabilities degrade (tool outage, auth drift, MCP instability), execution switches to containment mode and records degraded-state impact.

## Portability + Vendor Boundary

- Keep orchestration logic portable across providers.
- Prefer adapter-based integrations over platform-coupled business logic.
- Preserve ability to move runtime endpoints without rewriting core operating contracts.
- Preserve the ability to move Taylor01 outside BitPod when the repo boundary is mature enough.

## Linked Program Issues

- [BIT-61 — Define AI team topology and ownership model (CJ -> Taylor orchestrator -> specialists)](https://linear.app/bitpod-app/issue/BIT-61/define-ai-team-topology-and-ownership-model-cj-taylor-orchestrator)
- [BIT-62 — Taylor orchestrator contract: task decomposition, delegation, and completion criteria](https://linear.app/bitpod-app/issue/BIT-62/taylor-orchestrator-contract-task-decomposition-delegation-and)
- [BIT-64 — Agent delegation protocol and cross-agent handoff templates v1](https://linear.app/bitpod-app/issue/BIT-64/agent-delegation-protocol-and-cross-agent-handoff-templates-v1)
- [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)
- [BIT-66 — Agent runtime portability plan: Cloudflare-first execution with platform-decoupled memory/integrations](https://linear.app/bitpod-app/issue/BIT-66/agent-runtime-portability-plan-cloudflare-first-execution-with)
- [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)

## Change Control

- Append updates to versioned docs; do not rewrite history in place.
- Non-trivial changes require rationale + impact note.
- If operating behavior diverges from this document, log a drift note and open follow-up ticket.
