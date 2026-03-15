# Vera Runtime Minimum v1

Status: Working baseline  
Primary issue: [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for)

## Objective

Define the smallest future Vera runtime/agent surface that preserves the useful Zulip-era QA behaviors without dragging forward Taylor/Zulip-specific packaging as a permanent dependency.

This is a target minimum for Vera evolution.

It is not a claim that the current `qa-specialist` skill already implements everything below.

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

## Required verdict model

The minimum Vera runtime should support:

- `PASSED`
- `FAILED`
- `DEGRADED`

### Meaning

- `PASSED`
  - acceptance criteria have sufficient pass evidence
- `FAILED`
  - at least one critical acceptance criterion has reproducible failure evidence
- `DEGRADED`
  - Vera could not safely issue `PASSED` or `FAILED` because required context, execution quality, or runtime integrity was missing

`DEGRADED` is a required preservation from the Zulip-era runtime.

Without it, Vera would regress to a thinner and less truthful QA surface.

## Required `manifest.json` fields

Minimum required manifest fields:

- `qa_result`
- `degraded_reason`
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

## Required fail-closed behaviors

The Vera runtime minimum should fail closed in these cases:

1. missing review/verification target
2. missing PR/context when PR-bound review is required
3. malformed or unusable structured QA output
4. provider/API failure that prevents a trustworthy verdict

In those cases, Vera should prefer:

- `DEGRADED`
- explicit `degraded_reason`
- explicit `next_action`

not silent success and not vague apology text

## Required guardrails

### Context-required review guardrail

If the runtime is asked to review a PR or change surface, the target must be explicit enough to inspect.

If not, Vera should fail closed as `DEGRADED` or reject the handoff.

### High-risk review guardrail

If changed-file evidence shows high-risk patterns, Vera should record that in manifest metadata and steer toward stronger QA expectations.

This is a required preservation because the Zulip-era runtime already proved the value of file-based risk escalation.

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

Current gap:

- the skill does not yet preserve the fuller machine-readable runtime behavior defined here

So the current skill is acceptable as a transitional interface, but not as the full Vera runtime minimum by itself.

## Recommended implementation order

1. keep current skill contract active
2. add `DEGRADED` semantics to Vera runtime design
3. add `manifest.json`
4. add high-risk PR metadata
5. add optional PR receipt-post audit flow
6. only then decide whether the skill should remain a thin wrapper or disappear
