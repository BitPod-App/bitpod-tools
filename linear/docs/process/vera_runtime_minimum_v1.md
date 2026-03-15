# Vera Runtime Minimum v1

Status: Working baseline  
Primary issue: [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for)

## Objective

Define the smallest future Vera runtime/agent surface that preserves the useful Zulip-era QA behaviors without dragging forward Taylor/Zulip-specific packaging as a permanent dependency.

This is a target minimum for Vera evolution.

It is not a claim that the current `qa-specialist` skill already implements everything below.

## v1 embodiment rule

Vera v1 does not need to be a fully embodied standalone AI agent.

Acceptable v1 forms include:

- a skill-backed QA lane
- a thin runtime wrapper around the current QA contract
- a small dedicated execution surface that still relies on existing operator tooling

What matters for v1 is the QA behavior and artifact contract, not whether Vera already exists as a rich autonomous agent surface.

Fuller embodiment can come later.

That later embodiment path is explicitly still in scope, not ignored:

- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)

So the current rule is:

- do not force full Vera embodiment into v1 prematurely
- do not treat thin v1 as the permanent end state

## Inputs

This minimum is derived from:

- [vera_qa_lane_contract_v1.md](./vera_qa_lane_contract_v1.md)
- [vera_runtime_behavior_inventory_from_zulip_v1.md](./vera_runtime_behavior_inventory_from_zulip_v1.md)
- verified Zulip-era behavior in:
  - `/Users/cjarguello/bitpod-app/bitpod-taylor-runtime/src/taylor/bot.py`
  - `/Users/cjarguello/bitpod-app/bitpod-taylor-runtime/tests/test_phase0_bot.py`

## Required outputs

Every Vera runtime execution that counts as the evolved QA lane minimum should produce:

1. `verification_report.md`
2. `manifest.json`

Optional but recommended when the runtime is mature enough:

3. structured QA sidecar (`qa_review.json` or equivalent)
4. PR-post audit artifact when PR receipt posting is used

For Vera v1, only `verification_report.md` and `manifest.json` should be treated as true minimum required artifacts.

## Required verdict model

The minimum Vera runtime should support:

- `PASSED`
- `FAILED`
- `NO_VERDICT`

### Meaning

- `PASSED`
  - acceptance criteria have sufficient pass evidence
- `FAILED`
  - at least one critical acceptance criterion has reproducible failure evidence
- `NO_VERDICT`
  - Vera could not safely issue `PASSED` or `FAILED` because required context, execution quality, or runtime integrity was missing

`NO_VERDICT` preserves the useful old `DEGRADED` behavior, but says more clearly what happened.

Without it, Vera would regress to a thinner and less truthful QA surface.

### Legacy mapping

The Zulip-era Taylor runtime used the label `DEGRADED`.

For Vera v1, preserve the behavior but prefer the clearer label:

- legacy `DEGRADED` -> Vera `NO_VERDICT`

## Required `manifest.json` fields

Minimum required manifest fields:

- `qa_result`
- `no_verdict_reason`
- `next_action`
- `artifacts`

When PR evidence is available, also include:

- `review_risk.high_risk`
- `review_risk.patterns_matched`
- `review_risk.files_matched`
- `review_risk.evidence_source`

When output repair is attempted, also include:

- `repair_attempted`
- `repaired`
- `repair_sha256`

For transitional compatibility with old Taylor-era receipts, `degraded_reason` may temporarily survive as an alias, but it should not be the preferred long-term field name for Vera.

## Required fail-closed behaviors

The Vera runtime minimum should fail closed in these cases:

1. missing review/verification target
2. missing PR/context when PR-bound review is required
3. malformed or unusable structured QA output
4. provider/API failure that prevents a trustworthy verdict

In those cases, Vera should prefer:

- `NO_VERDICT`
- explicit `no_verdict_reason`
- explicit `next_action`

not silent success and not vague apology text

## Required guardrails

### Context-required review guardrail

If the runtime is asked to review a PR or change surface, the target must be explicit enough to inspect.

If not, Vera should fail closed as `NO_VERDICT` or reject the handoff.

### High-risk review guardrail

If changed-file evidence shows high-risk patterns, Vera should record that in manifest metadata and steer toward stronger QA expectations.

This is a required preservation because the Zulip-era runtime already proved the value of file-based risk escalation.

## What is probably unnecessary for Vera v1

These are useful historical behaviors, but they should not be treated as v1 requirements:

- Taylor/Zulip `review:` topic conventions
- Taylor-branded artifact names like `qa_review.md`
- `session_summary.md`
- `worth_remembering.json`
- mandatory PR receipt-post flow
- mandatory `repair_sha256` outside cases where repair tracking is actually valuable

The v1 goal is a clear QA verdict surface with durable evidence, not a full reproduction of the old Taylor runtime package.

## Transitional allowances

The following may remain transitional and do not need to be part of the durable Vera identity:

- Taylor/Zulip `review:` topic convention
- Taylor-branded artifact names like `qa_review.md`
- `session_summary.md`
- `worth_remembering.json`

Those can survive temporarily, but they should not define Vera's long-term runtime boundary.

## Relationship to current `qa-specialist` skill

Current skill truth:

- the `qa-specialist` skill is still useful as the live minimal verdict contract
- it preserves independent QA authority and evidence-first `verification_report.md`
- it can still be a valid part of Vera v1

Current gap:

- the skill does not yet preserve the fuller machine-readable runtime behavior defined here

So the current skill is acceptable as a transitional interface, but not as the full Vera runtime minimum by itself.

## Recommended implementation order

1. keep current skill contract active
2. add `NO_VERDICT` semantics to Vera runtime design while preserving compatibility with the old `DEGRADED` concept
3. add `manifest.json`
4. add high-risk PR metadata
5. add optional PR receipt-post audit flow
6. only then decide whether the skill should remain a thin wrapper or disappear

## Explicit future question

Once Vera v1 is stable, revisit whether Vera should become a more embodied agent/runtime that can:

- accumulate QA pattern memory
- improve recommendation quality over time
- suggest stronger QA coverage and low-risk improvements

That later decision belongs to the specialist-embodiment lane, not the v1 minimum lane.
