# BitPod Startup Operating Model v1

Version: v1  
Status: Working baseline only; not proof that Phase 4 is operationally complete  
Owner: CJ (final authority), Taylor (operating orchestrator)

## Purpose

Define how BitPod runs as an AI-assisted startup with clear ownership, strict execution gates, and auditable delivery.

## Scope

This document governs:

- agent/team topology and ownership boundaries
- planning/delegation/handoff flow
- QA and release authority
- evidence contract for status transitions
- operating cadence and controls

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
2. Plan: Taylor decomposes into atomic tasks with explicit dependencies.
3. Execute: specialists implement scoped changes only.
4. Verify: QA validates against acceptance criteria and evidence requirements.
5. Approve: PM/CJ gate checks pass/fail and transition rationale recorded.
6. Ship: merge/deploy with rollback note and artifact links.
7. Learn: postmortem/retro notes appended, not rewritten.

## Evidence Contract (Required Before Done)

Every completion claim must include:

- status line (`from -> to`) and transition reason
- commands/UI checks executed
- artifact path(s) or URL(s)
- pass/fail by gate
- known risks and follow-up

Status-only updates are non-authoritative without evidence.

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

## Cadence

### Daily

- blocker sweep
- dependency integrity check
- top-priority execution pull
- verification evidence sweep

### Weekly

- migration drift check
- secrets/access delta review
- backlog aging/icebox review
- retro and operating-model update append

## Phase Map (Program-Level)

- Phase 1: Critical identity/access bootstrap and safety baseline.
- Phase 2: Integration parity and runtime migration.
- Phase 3: Retroactive cleanup and hardening.
- Phase 4: AI team orchestration and specialist operating model in practice, not only in docs.
- Phase 5: governance, memory, eval, and reviewer-routing hardening after Phase 4 is operationally real.

Each phase closes only with explicit evidence pack and go/no-go decision record.

## Portability + Vendor Boundary

- Keep orchestration logic portable across providers.
- Prefer adapter-based integrations over platform-coupled business logic.
- Preserve ability to move runtime endpoints without rewriting core operating contracts.

## Linked Program Issues

- [BIT-61 — Define AI team topology and ownership model (CJ -> Taylor orchestrator -> specialists)](https://linear.app/bitpod-app/issue/BIT-61/define-ai-team-topology-and-ownership-model-cj-taylor-orchestrator)
- [BIT-62 — Taylor orchestrator contract: task decomposition, delegation, and completion criteria](https://linear.app/bitpod-app/issue/BIT-62/taylor-orchestrator-contract-task-decomposition-delegation-and)
- [BIT-64 — Agent delegation protocol and cross-agent handoff templates v1](https://linear.app/bitpod-app/issue/BIT-64/agent-delegation-protocol-and-cross-agent-handoff-templates-v1)
- [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)
- [BIT-66 — Agent runtime portability plan: Cloudflare-first execution with platform-decoupled memory/integrations](https://linear.app/bitpod-app/issue/BIT-66/agent-runtime-portability-plan-cloudflare-first-execution-with)

## Change Control

- Append updates to versioned docs; do not rewrite history in place.
- Non-trivial changes require rationale + impact note.
- If operating behavior diverges from this document, log a drift note and open follow-up ticket.
