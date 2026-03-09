# Stage 4/5 Agent Stack Execution Plan v1

Status: Active planning baseline  
Purpose: Integrate the Taylor-hub specialist model into chronological execution with maximum autopilot throughput.

## North-Star Integration

- Taylor is central orchestrator (hub).
- Specialists are constrained execution spokes.
- Linear is execution system-of-record.
- Repo/docs are implementation memory.
- Discord is lean status surface, not primary database.

## Stage Model (chronological)

1. Stage 1 — Identity + Access Bootstrap (complete baseline)
2. Stage 2 — Integration Parity + Runtime Migration (active; Discord parity completion path)
3. Stage 3 — Retroactive Cleanup + Hardening (active after Stage 2 blockers clear)
4. Stage 4 — Orchestrator + Specialist Operating Model (baseline complete)
5. Stage 5 — Governance, Memory, Evals, and Runtime Maturity (new lane)

## Current Autopilot Priority Order

### P0: Finish Stage 2 operational blockers

- [BIT-59 — Discord workspace + webhook prerequisites for Phase 2 parity execution](https://linear.app/bitpod-app/issue/BIT-59/discord-workspace-webhook-prerequisites-for-phase-2-parity-execution)
- [BIT-30 — Linear + GitHub + Discord webhook integration parity checks](https://linear.app/bitpod-app/issue/BIT-30/linear-github-discord-webhook-integration-parity-checks)

### P1: Stage 3 hardening with low UI dependency

- [BIT-31 — Legacy identity sweep and historical ref normalization](https://linear.app/bitpod-app/issue/BIT-31/legacy-identity-sweep-and-historical-ref-normalization)
- [BIT-21 — Phase 3 planning stub: legacy cleanup + access hardening](https://linear.app/bitpod-app/issue/BIT-21/phase-3-planning-stub-legacy-cleanup-access-hardening)
- [BIT-32 — Post-bootstrap hardening plan: restricted local scope + dedicated macOS profile](https://linear.app/bitpod-app/issue/BIT-32/post-bootstrap-hardening-plan-restricted-local-scope-dedicated-macos)

### P2: Stage 5 buildout (new)

- Taylor runner runtime loop hardening
- tool permissions matrix per specialist lane
- memory write proposal and approval flow
- evaluation and regression gates
- cross-system traceability and audit dashboards

## Stage 5 Proposed Work Packages

1. Runtime core and delegation engine hardening
2. Memory stewardship service (proposal + approval + contradiction scan)
3. Governance and action policy enforcement
4. Evaluation suites and regression gates
5. Communication hygiene (summary-first Discord policy + linkage)

## CJ-Required Checkpoints (only when unavoidable)

- Discord workspace/channel/webhook creation (BIT-59)
- live webhook validation run confirmation (BIT-59/BIT-30)
- final approval for destructive hardening actions

Everything else should continue in autopilot mode.

## Evidence Rule

Every stage transition or completion claim must include:

- status line and reason
- commands/checks
- artifact links
- pass/fail outcomes
- residual risk
