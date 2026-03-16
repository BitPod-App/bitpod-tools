# Vera Runtime Behavior Inventory From Zulip v1

Status: Working preservation inventory  
Linked issue: [BIT-94 — Preserve Vera QA runtime behaviors from Zulip-era implementation for dedicated agent path](https://linear.app/bitpod-app/issue/BIT-94/preserve-vera-qa-runtime-behaviors-from-zulip-era-implementation-for)

## Objective

Capture the Zulip-era Taylor QA/runtime behaviors that should not get lost while QA authority migrates toward Vera / `qa-specialist`.

This is not a claim that Vera already implements all of these behaviors. It is a preservation map so we can separate:

- already preserved
- still missing
- intentionally transitional

## Verified current sources

Primary Zulip-era implementation:

- `/Users/cjarguello/BitPod-App/bitpod-taylor-runtime/src/taylor/bot.py`
- `/Users/cjarguello/BitPod-App/bitpod-taylor-runtime/tests/test_phase0_bot.py`

Current Vera contract surface:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/vera_qa_lane_contract_v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/vera_qa_lane_operational_proof_v1.md`
- canonical local surface:
  - `/Users/cjarguello/BitPod-App/local-workspace/local-codex/skills/qa-specialist/SKILL.md`
  - `/Users/cjarguello/BitPod-App/local-workspace/local-codex/skills/qa-specialist/references/QA_OUTPUT_CONTRACTS_v1.md`
  - `/Users/cjarguello/BitPod-App/local-workspace/local-codex/skills/qa-specialist/references/QA_REVIEW_CHECKLIST_v1.md`

## Verified behavior inventory

### Already preserved in Vera contract or skill

These behaviors are already clearly preserved in the current Vera lane:

- independent QA authority separate from Taylor orchestration
- verdict-only identity
- evidence-first output contract
- `verification_report.md` as required durable artifact
- explicit `PASSED` or `FAILED` final verdict
- failure section with concrete reasons and evidence
- optional low-risk fix hints only

### Preserved in Zulip-era runtime but not yet clearly carried into Vera

These behaviors exist in the Zulip-era runtime and tests, but are not yet explicitly preserved in the current Vera contract/skill docs:

1. legacy `DEGRADED` result class
   - review can fail closed as `DEGRADED`, not just `PASSED` or `FAILED`
   - examples verified in tests:
     - missing PR context
     - malformed/irreparable review JSON
     - GitHub API failures
   - for Vera v1, the clearer future label is likely `NO_VERDICT` rather than `DEGRADED`

2. structured machine-readable receipt/manifest
   - `manifest.json`
   - includes:
     - `qa_result`
     - `degraded_reason`
     - `next_action`
     - review-risk metadata
     - repair metadata

3. sidecar structured review output
   - `qa_review.json`
   - separate from the human-readable markdown artifact

4. deterministic multi-artifact run bundle
   - `qa_review.md`
   - `qa_review.json`
   - `manifest.json`
   - `session_summary.md`
   - `worth_remembering.json`

5. explicit degraded-reason to next-action mapping
   - verified examples:
     - `pr_context_missing`
     - `repair_failed`
     - `github_api_error_403`
   - verified next actions include:
     - `rerun_or_bridge_qa`
     - context repair / PR attachment guidance

6. JSON repair path
   - runtime attempts to repair malformed model JSON before giving up
   - manifest records whether repair was attempted and whether it succeeded
   - includes `repair_sha256`

7. PR changed-file high-risk detection
   - verified runtime behavior:
     - fetch changed filenames from PR
     - detect high-risk patterns
     - warn or steer toward stronger QA when high-risk files match
   - verified manifest fields:
     - `high_risk`
     - `patterns_matched`
     - `files_matched`
     - `evidence_source`

8. receipt-card / PR posting audit trail
   - runtime can generate a receipt card and post it to the PR
   - verified artifact:
     - `pr_post.json`
   - verified state patterns:
     - latest receipt
     - last receipt by conversation
     - posted receipts by PR

9. `review:` topic and QA command guardrails
   - `review:` topic convention
   - explicit PR-link requirement for QA review paths
   - fail-closed behavior when review target is missing

## Classification

### Must preserve for Vera evolution

These are the highest-value runtime behaviors to keep:

- fail-closed no-verdict state with explicit reason and next action
- machine-readable `manifest.json` receipt
- high-risk PR detection metadata
- PR posting audit trail
- fail-closed review target guardrails

### Useful but transitional

These may survive only as long as the current QA lane still leans on Taylor-era review packaging:

- `session_summary.md`
- `worth_remembering.json`
- Taylor/Zulip `review:` topic conventions
- Taylor-branded file names like `qa_review.md`

### Intentionally not the Vera core identity

These should not be treated as the durable definition of Vera:

- Taylor ownership of QA
- Zulip-specific topic/thread assumptions
- any requirement that Vera remain only a skill rather than a fuller runtime/agent later

## Current gap statement

Current Vera contract truth is:

- role separation is preserved
- verdict discipline is preserved
- human-readable verification artifact is preserved

Current Vera contract gap is:

- the richer machine-readable runtime/audit behavior from the Zulip-era implementation is not yet fully mapped into Vera canon

So the migration risk is real, but now explicit.

## Recommended next follow-up

The next BIT-94 step should define a compact Vera runtime minimum that includes:

1. `PASSED` / `FAILED` / `NO_VERDICT` semantics that preserve the old `DEGRADED` behavior more clearly
2. `verification_report.md`
3. `manifest.json`
4. degraded reason + next action fields
5. high-risk PR metadata when PR evidence is available
6. optional PR receipt-post audit artifact

That would preserve the most useful Zulip-era QA behavior without forcing Vera to inherit all Taylor/Zulip packaging forever.
