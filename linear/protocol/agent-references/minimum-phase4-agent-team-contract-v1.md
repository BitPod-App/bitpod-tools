# Minimum Phase 4 Agent Team Contract v1

Date: 2026-03-11
Primary issue: [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera)
Related issues:
- [BIT-84 — Prove Taylor orchestrator in a real multi-agent execution loop](https://linear.app/bitpod-app/issue/BIT-84/prove-taylor-orchestrator-in-a-real-multi-agent-execution-loop)
- [BIT-85 — Stand up specialist operating lanes for engineering, QA, and research/design](https://linear.app/bitpod-app/issue/BIT-85/stand-up-specialist-operating-lanes-for-engineering-qa-and)
- [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy)
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)

## Objective

Define the minimum real AI-agent team that must exist in practice before the Discord team-session surface can be treated as a meaningful Phase 4 proving environment.

This is not a documentation-only milestone. The minimum team exists only when the lanes below are used in real work with durable artifacts and clear role boundaries.

## Minimum required team

### 1. Taylor PM / orchestrator

Required reality:
- receives work at the coordination layer
- decomposes work into lane-specific tasks
- routes work to QA and engineering deliberately
- synthesizes outcomes and updates the execution spine

Not enough:
- planning docs only
- one-off proof artifacts without continued operating use

### 2. Vera-style QA lane

Required reality:
- issues explicit PASS/FAIL technical QA verdicts with evidence
- produces QA artifacts that can be linked to Linear issues and PRs
- is treated as a distinct operating lane, not just an informal comment style

Not enough:
- generic self-review by the implementation lane
- CJ acceptance standing in for technical QA
- policy docs without real QA artifact flow

### 3. Engineering specialist lane(s)

Required reality:
- at least one real engineering lane exists and is used through Taylor-led delegation
- preferred target is two engineering lanes or one engineering lane plus a clearly bounded fallback model
- engineering outputs include code/config/docs plus reproducible validation notes

Not enough:
- generic “Codex did some work” without lane framing
- docs that name engineering as a role but do not show real use

## Completion checklist

All must be true:

1. Taylor is used as the active orchestrator in at least one real execution record.
2. A QA lane produces at least one real structured QA artifact with verdict and evidence.
3. An engineering lane produces at least one real delegated output that flows back through Taylor.
4. The resulting plans, decisions, and artifacts are linked durably through repo and/or Linear artifacts.
5. The team is real enough that Discord acceptance would test communication quality rather than just webhook plumbing.

## Required outputs

- one minimum-team operating matrix with current reality vs target reality
- one real execution record showing:
  - Taylor orchestration
  - engineering participation
  - QA participation
- one explicit verdict:
  - `MINIMUM_TEAM_READY=true|false`
- one note on what still remains simulated/interim

## Completion rule

[BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera) is complete only when the minimum team exists in practice strongly enough that [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) becomes a meaningful test of team communication.

## Why this matters

If Discord acceptance is attempted before the minimum team exists, the result is a false signal: CJ talking to himself plus bots/webhooks. That proves transport plumbing, not team operations.
