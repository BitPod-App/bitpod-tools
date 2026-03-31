# Vera QA Lane Contract v1

Status: Working baseline  
Linked issue: [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy)

## Objective

Define the dedicated Vera-style QA lane as a real operating lane with explicit verdict authority, explicit evidence requirements, and a durable artifact flow into Linear and PR work.

This contract is the target operating model for technical QA in BitPod Phase 4. It is not a merge-policy replacement by itself.

## Current implementation reference

This repo contract is currently implemented through the local `qa-specialist` skill:

- canonical local surface:
  - `$WORKSPACE/local-workspace/local-codex/skills/qa-specialist/SKILL.md`
  - `$WORKSPACE/local-workspace/local-codex/skills/qa-specialist/references/QA_OUTPUT_CONTRACTS_v1.md`
  - `$WORKSPACE/local-workspace/local-codex/skills/qa-specialist/references/QA_REVIEW_CHECKLIST_v1.md`

That skill should be treated as a transitional implementation surface for Vera while the dedicated QA lane is still being operationalized as a fuller agent/runtime.

The durable intent is:

- Vera = QA specialist role/lane
- `qa-specialist` = current implementation scaffold for that role

The long-term role should not be constrained to remaining only a skill.

For preserved Zulip-era QA/runtime behaviors that should not be lost during Vera migration, see:

- [vera_runtime_behavior_inventory_from_zulip_v1.md](./vera_runtime_behavior_inventory_from_zulip_v1.md)
- [vera_runtime_minimum_v1.md](./vera_runtime_minimum_v1.md)

## What Makes This A Dedicated QA Lane

The QA lane counts as dedicated only if all of the following are true:

- the lane is invoked through an explicit QA handoff, not as an afterthought in implementation notes
- the lane decides only `PASSED` or `FAILED`
- the lane produces a structured verification artifact with evidence
- the artifact is linked back to the related issue and/or PR
- the implementation lane does not self-issue the final QA verdict

If any of those are missing, the work falls back to the interim pattern rather than the dedicated QA lane.

## Role Boundaries

### Vera owns

- QA verdict only
- verification scope review against critical acceptance criteria
- evidence capture
- blocking-defect callouts
- residual-risk callouts when verdict is `PASSED`

### Vera does not own

- product priority
- scope reshaping
- implementation
- merge approval authority
- rewriting acceptance criteria after work is complete
- cross-lane orchestration workflow beyond returning the verdict artifact

## Inputs Required

Minimum handoff packet into QA:

- linked issue or PR
- system under test
- critical acceptance criteria
- commands or surfaces to verify
- expected artifact destinations
- known risks or constraints

If the handoff packet is incomplete, QA should reject the handoff and ask Taylor for a corrected packet.

## Required Output Contract

Every dedicated QA execution must produce a `verification_report.md`-style artifact with:

1. verdict: `PASSED` or `FAILED`
2. environment matrix
3. critical acceptance criteria with evidence per criterion
4. `this failed QA because ...` section when verdict is `FAILED`
5. optional low-risk fix hints only when obvious
6. final line:
   - `QA_VERDICT: PASSED`, or
   - `QA_VERDICT: FAILED`

Allowed storage targets:

- `linear/examples/*verification_report*.md`
- issue-linked repo artifact paths under `/linear/docs/process/**` when the report is part of a process proof
- PR comments or Linear comments that link to the durable artifact rather than replacing it

Optional companion artifacts may exist when useful, but they are not required to count as Vera operating correctly:

- `test_plan.md`
- `bug_report.md`

## Required Flow

1. Taylor delegates QA with explicit acceptance criteria.
2. Engineering or prior lane provides the build/test/artifact surface.
3. Vera executes checks and writes the verification artifact.
4. Vera returns `PASSED` or `FAILED` with evidence links.
5. Taylor synthesizes the verdict into the execution spine.
6. CJ acceptance or admin bypass, if needed, remains a separate governance action.

The minimum successful QA handoff is therefore:

- Taylor or engineering supplies the verification target and criteria
- Vera returns `verification_report.md`
- Taylor or CJ decides what to do with that verdict

## Interim Linear-first bridge

Until Vera has a fuller dedicated runtime again, a cheap interim bridge is
acceptable if it preserves the lane boundary.

### Acceptable interim shape

- the operator starts from a Linear issue or PR-linked Linear thread
- the Linear bot receives:
  - PR or issue link
  - critical acceptance criteria
  - verification target or commands when available
- the bot returns one durable QA artifact:
  - `verification_report.md`
- the bot posts a concise receipt back to:
  - the Linear issue, and
  - the PR when a PR exists

### Minimum receipt fields

The receipt may be lightweight, but it should still include:

- target PR or issue
- QA label:
  - `qa_passed` or `qa_failed`
- durable artifact link or path
- one-line reason when label is `qa_failed`

Starter prompt/example:

- `linear/examples/vera_linear_pr_review_prompt_v1.md`

### Explicit non-goals for the interim bridge

This interim Linear-first bridge does not need to recreate the full Zulip-era
runtime package yet. It may omit:

- `session_summary.md`
- `worth_remembering.json`
- conversation/window capture
- SHA receipt bundles
- multi-artifact upload cards
- Taylor-branded `qa_review.md` receipt flow

### Hard rule

Even in the cheap interim bridge, the QA lane must still:

- fail closed to `qa_failed` when context is insufficient
- avoid implementation ownership
- return an explicit verdict artifact rather than a casual chat opinion
- keep QA authority separate from Taylor planning or engineering execution

## Independence Rules

This contract inherits and operationalizes:

- [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)
- [qa_authority_model_v1.md](./qa_authority_model_v1.md)

Additional working rules:

- Taylor may route QA work, but may not overwrite a `FAILED` verdict.
- Engineering may answer QA questions, but may not publish the final QA verdict on its own work.
- CJ may override only through an explicit risk-acceptance path and rollback note.

## Relationship To Interim BIT-79 Policy

This contract changes the primary QA expectation:

- primary technical QA path: dedicated Vera lane with structured evidence artifacts
- temporary merge-governance fallback: [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)

[BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) remains active only because GitHub reviewer-routing and standalone merge authority are not yet fully aligned with the operating model.

It should no longer be treated as the primary definition of QA itself once this lane is in use.

## Completion Signal For BIT-90

[BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy) is satisfied only when:

- this lane contract exists
- at least one real verification artifact exists under this contract
- the artifact flow is linked back into real issue/PR execution
- the repo explicitly states whether [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) can be downgraded from primary reliance
