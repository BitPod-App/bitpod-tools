# Specialist Operating Lanes Proof v1

Status: Working proof  
Linked issue: [BIT-85 — Stand up specialist operating lanes for engineering, QA, and research/design](https://linear.app/bitpod-app/issue/BIT-85/stand-up-specialist-operating-lanes-for-engineering-qa-and)

Historical note:

- this proof records the state at BIT-85 completion time
- later QA-lane status should be read from `./vera-qa-lane-operational-proof-v1.md`

## Objective

Show which specialist lanes are already functioning in real work, which are only interim, and which still require a blocker note rather than a false completion claim.

## Verdict

Verdict: `PASS_WITH_LIMITS`

Interpretation:

- Engineering lane is operational in real work.
- QA lane exists in an interim but real operating form.
- Research lane exists in a real but lightweight operating form.
- Design remains defined but not yet meaningfully exercised as part of the active AI-team execution loop.

This is enough to prove specialist lanes are not purely theoretical, but not enough to claim a mature AI-agent team.

## Operating-Lane Matrix

| Lane | Current state | Input contract | Output contract | Real exercised example | Remaining gap |
|---|---|---|---|---|---|
| Engineering | Operational | delegated task packet, acceptance checks, artifact target | code/docs/config changes, PR, validation output | [BitPod-App/sector-feeds PR #32 — [BIT-77] Implement weekly run-track cleanup and operator-facing summary contract](https://github.com/BitPod-App/sector-feeds/pull/32) | still centered on Codex execution rather than separate specialist runtime |
| QA | Interim but real | build artifacts, sample run targets, acceptance checks | PASS/FAIL evidence, residual-risk note, verification artifacts | [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) plus merged-main Tuesday run verification from [BIT-80 — Fix sector-feeds runtime OpenAI credential source for Tuesday track verification](https://linear.app/bitpod-app/issue/BIT-80/fix-sector-feeds-runtime-openai-credential-source-for-tuesday-track) | no fully separated Vera-style agent lane yet |
| Research | Operational (lightweight) | question, constraints, source targets, operator intent | source-grounded recommendation or comparison note | GPT-supported consumer-model check in [BIT-75 — Audit weekly run-track automations: dedupe jobs, fix repo target, and define useful artifacts](https://linear.app/bitpod-app/issue/BIT-75/audit-weekly-run-track-automations-dedupe-jobs-fix-repo) | still lightweight and not yet formalized as a dedicated runtime/service |
| Design | Defined only | design scope packet, brand constraints | assets/spec/provenance | blocker: no strong recent design-lane execution used in current Phase 4 operating loop | requires real exercised work product before counted as operational |

## Real Exercised Examples

### Engineering Lane

Representative chain:

- [BIT-75 — Audit weekly run-track automations: dedupe jobs, fix repo target, and define useful artifacts](https://linear.app/bitpod-app/issue/BIT-75/audit-weekly-run-track-automations-dedupe-jobs-fix-repo)
- [BIT-77 — Implement weekly run-track cleanup and operator-facing summary contract](https://linear.app/bitpod-app/issue/BIT-77/implement-weekly-run-track-cleanup-and-operator-facing-summary)
- [BitPod-App/sector-feeds PR #32 — [BIT-77] Implement weekly run-track cleanup and operator-facing summary contract](https://github.com/BitPod-App/sector-feeds/pull/32)

Real outputs used by the workflow:

- recurring per-run status artifacts:
  - `/Users/cjarguello/BitPod-App/sector-feeds/artifacts/runs/legacy_tuesday_track/jack_mallers_show/20260311T065208Z__status.json`
  - `/Users/cjarguello/BitPod-App/sector-feeds/artifacts/runs/experimental_track/jack_mallers_show/20260311T065224Z__status.json`
- recurring per-run operator summaries:
  - `/Users/cjarguello/BitPod-App/sector-feeds/artifacts/runs/legacy_tuesday_track/jack_mallers_show/20260311T065208Z__summary.md`
  - `/Users/cjarguello/BitPod-App/sector-feeds/artifacts/runs/experimental_track/jack_mallers_show/20260311T065224Z__summary.md`

These outputs were actually used to decide when the weekly lanes were healthy enough to normalize as complete.

### QA Lane

Representative chain:

- [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)
- [BitPod-App/bitpod-tools PR #34 — [BIT-79] Add interim AI technical QA and CJ acceptance policy](https://github.com/BitPod-App/bitpod-tools/pull/34)
- [BIT-80 — Fix sector-feeds runtime OpenAI credential source for Tuesday track verification](https://linear.app/bitpod-app/issue/BIT-80/fix-sector-feeds-runtime-openai-credential-source-for-tuesday-track-verification)
- [BIT-81 — Harden sector-feeds Tuesday transcription against OpenAI 500 retries/timeouts](https://linear.app/bitpod-app/issue/BIT-81/harden-sector-feeds-tuesday-transcription-against-openai-500)
- [BIT-82 — Narrow transcription model-fallback detection for Tuesday track runs](https://linear.app/bitpod-app/issue/BIT-82/narrow-transcription-model-fallback-detection-for-tuesday-track-runs)

Real outputs used by the workflow:

- explicit sample-run success/failure artifacts
- `bash linear/scripts/local_smoke.sh` validations on merged policy/runtime changes
- pass/fail interpretation preserved in issue comments and status changes

What is real:

- QA evidence exists and affects closeout decisions
- CJ is explicitly treated as acceptance/operational approval, not fake deep technical reviewer

What is still interim:

- QA is not yet a fully separate Vera-run agent lane with its own independent runtime identity

### Research Lane

Representative chain:

- [BIT-75 — Audit weekly run-track automations: dedupe jobs, fix repo target, and define useful artifacts](https://linear.app/bitpod-app/issue/BIT-75/audit-weekly-run-track-automations-dedupe-jobs-fix-repo)
- [BitPod-App/sector-feeds PR #31 — [BIT-75] Audit weekly run-track automations and useful artifacts](https://github.com/BitPod-App/sector-feeds/pull/31)

Real outputs used by the workflow:

- `/Users/cjarguello/BitPod-App/sector-feeds/docs/runbooks/weekly_run_track_audit_v1.md`

That audit incorporated external/GPT-supported consumer reasoning to answer:

- why the weekly tracks exist
- whether GPT is actually the consumer
- which outputs matter
- whether the weekly tasks are justified or are tech debt

That research output directly shaped the surviving implementation in [BIT-77 — Implement weekly run-track cleanup and operator-facing summary contract](https://linear.app/bitpod-app/issue/BIT-77/implement-weekly-run-track-cleanup-and-operator-facing-summary).

## Routing Through Taylor

The routing model is real enough to trace:

1. CJ supplies intent and scope correction.
2. Taylor-style orchestration chooses bounded lanes:
   - research/evidence first
   - engineering implementation second
   - QA/verification before closeout
3. Evidence returns into Linear/project status and repo-side artifacts.

Supporting control-plane references:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/agent-references/taylor-orchestrator-contract-v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/templates/agent-handoff-templates-v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-84/taylor-orchestrator-operational-proof-v1.md`

## Explicit Gaps

This proof is intentionally not overstated.

Still missing before a stronger Phase 4 completion claim:

- a truly separate QA specialist runtime lane
- a clearly exercised design lane in active work
- real Discord team-session acceptance:
  - [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)
- stronger live multi-agent memory/artifact flow:
  - [BIT-87 — Prove durable decision, memory, and artifact flow in live AI-team operations](https://linear.app/bitpod-app/issue/BIT-87/prove-durable-decision-memory-and-artifact-flow-in-live-ai-team)

## Explicit Answer

Are specialist lanes functioning in real work?

Answer: yes, but unevenly.

- Engineering: yes
- QA: yes, interim
- Research: yes, lightweight
- Design: not yet proven in the active operating loop

That is enough for `PASS_WITH_LIMITS`, and not enough for “Phase 4 complete.”
