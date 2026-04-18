# Linear Process CJ Intent Packet

Date: 2026-04-15
Status: Active intent record
Owner: Product Development
Purpose: Capture CJ's agreed near-term Linear Process intent in one place so Control Tower can sequence, validate, and delegate the work without reconstructing it from thread history.

## Why this exists

The Control Tower-aligned v1.1 implementation intentionally split:

- repo-side doctrine and enforcement alignment
- live Linear admin/config mutation
- guarded follow-up lanes

That split reduced risk, but it also makes it easy to lose the distinction between:

- what CJ explicitly wants
- what has already been implemented in repo
- what is still deferred to guarded execution

This file records the first item directly.

## CJ intent summary

CJ wants the active Product Development Linear Process improved in a serious way, while preserving truth and avoiding fake certainty.

Near-term intent:

- improve the active Product Development team workflow in place
- preserve current live workflow names unless and until a coordinated migration is approved
- keep Control Tower as the validator and sequencing authority for risky mutations
- make GitHub and Linear truth line up more tightly
- keep project handling part of the plan
- avoid over-optimizing for a future multi-team shape before it is actually needed

## The main changes CJ wanted

### 1. Backlog vs Icebox must be clearly different

Intent:

- `Backlog` = default landing space for real work, not yet ready to start
- `Icebox 🧊` = parked for later; unlikely to be done soon
- `Backlog` should age into `Icebox 🧊`
- `Icebox 🧊` should not be used as a general intake lane

Target wording direction:

- short, blunt status descriptions
- include the practical aging rule in the description where useful

### 2. Inactivity should close into Stale, not Obsolete by default

Intent:

- `Backlog` 30d inactive -> `Icebox 🧊`
- `Icebox 🧊` 30d inactive -> `Stale`
- automated stale moves should leave a comment explaining the move
- `Obsolete` should not be the default inactivity sink

Reason:

- inactivity alone does not mean the work is no longer relevant

### 3. Preserve current live workflow names for now

Intent:

- keep `In Review`
- keep `Delivered`
- keep `Accepted`
- keep current PM label names such as `pm-accepted`

Reason:

- current code, tests, prompts, and active guidance already depend on these names
- renaming now would create unnecessary drift

### 4. Tighten the review and acceptance path

Intent:

- `In Review` remains the current Product Development review gate
- QA result labels move work out of `In Review`
- `Delivered` remains the PM gate
- `pm-rejected` should move work back to `In Progress`
- `pm-skipped` should not jump directly to `Done`
- `Accepted` should remain the checkpoint before `Done`

Target behavior:

- `qa-passed` / `qa-skipped`: `In Review` -> `Delivered`
- `qa-failed`: `In Review` -> `In Progress`
- `pm-accepted`: `Delivered` -> `Accepted`
- `pm-rejected`: `Delivered` -> `In Progress`
- `pm-skipped`: `Delivered` -> `Accepted`

### 5. GitHub should drive truthful Linear transitions where the event is objective

Intent:

- PR opened/drafted can move work to `In Progress`
- real review-ready PR state can move work to `In Review`
- merge to `main` can move `Accepted` -> `Done`

But:

- only if QA, PM, blocker, and release truth are already satisfied
- otherwise fail closed and leave a correction comment

### 6. Blockers should become simpler and more truthful

Intent:

- long-term direction is native Linear dependencies first
- generic non-ticket blockers should converge toward one `blocked` label
- blocked work should not be merge-ready

Important truth note:

- this was not canceled or reverted
- it was deferred into guarded execution because the live workspace still has a broader `Blocked By` surface and Control Tower alignment raised the bar for mutating it safely

### 7. Current Vera-style QA must be described honestly

Intent:

- do not imply stronger independent Vera authority than currently exists
- preserve the useful current QA behavior
- keep the current review surface truthful until a stronger Vera runtime actually exists

### 8. Projects should be part of the plan, but stay coarse

Intent:

- do not ignore projects
- do not make project statuses mirror the full team issue workflow
- keep workspace project statuses coarse
- use project templates only where they add real value
- near-term reality is still mostly one Product Development-centered workflow

### 9. Templates should support real current usage, not speculative schema

Intent:

- prefer practical Product Development issue/project templates
- do not explode the template surface for future teams that are not yet active enough to justify it
- keep future expansion possible

### 10. Control Tower should know the difference between CJ intent and implementation timing

Intent:

- Control Tower should know what CJ wants
- Control Tower should still decide when/how risky changes are executed
- delegation is acceptable, but the intent should not be lost or watered down

## What was aligned vs deferred

### Already implemented in repo

- doctrine and change-control language aligned to Control Tower
- current names preserved
- repo engine/tests updated for:
  - `qa-*` -> `Delivered`
  - `pm-skipped` -> `Accepted`
  - fail-closed merge readiness
  - `Backlog -> Icebox 🧊 -> Stale`
- Vera prompt language corrected to truthful substitute-surface wording

### Deferred to guarded live execution

- live Product Development status descriptions
- live team automations
- live GitHub/Linear config alignment
- live blocker taxonomy cleanup
- live workspace project-status cleanup
- live workspace project-template setup

Deferred does not mean rejected.

It means:

- the desired direction remains active
- the execution surface now needs snapshot, rollback, validation, and Control Tower signoff

## Source lanes and artifacts

Primary planning / doctrine lanes:

- [BIT-175 — Linear operating model v1 rollout plan](https://linear.app/bitpod-app/issue/BIT-175/linear-operating-model-v1-rollout-plan)
- [BIT-178 — Templates + Linear skills](https://linear.app/bitpod-app/issue/BIT-178/templates-linear-skills)
- [BIT-186 — Investigate and fix broken Update Linear enforcement path](https://linear.app/bitpod-app/issue/BIT-186/investigate-and-fix-broken-update-linear-enforcement-path)
- [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)

Guarded follow-up lanes created from this intent:

- [BIT-319 — Product Development blocker cleanup toward native dependencies + minimal blocker taxonomy](https://linear.app/bitpod-app/issue/BIT-319/product-development-blocker-cleanup-toward-native-dependencies-minimal)
- [BIT-320 — Align GitHub-triggered Linear automations with fail-closed merge readiness](https://linear.app/bitpod-app/issue/BIT-320/align-github-triggered-linear-automations-with-fail-closed-merge)
- [BIT-321 — Audit and align Vera / Linear agent guidance with truthful QA substitute language](https://linear.app/bitpod-app/issue/BIT-321/audit-and-align-vera-linear-agent-guidance-with-truthful-qa-substitute)
- [BIT-322 — Inventory workspace project statuses and define the coarse canonical model](https://linear.app/bitpod-app/issue/BIT-322/inventory-workspace-project-statuses-and-define-the-coarse-canonical)
- [BIT-323 — Set up workspace project templates for Product Development standard work and release trains](https://linear.app/bitpod-app/issue/BIT-323/set-up-workspace-project-templates-for-product-development-standard)

Repo-side aligned implementation artifacts:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_model_v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_guide_v3.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_process_v1_1_control_tower_change_proposal_2026-04-15.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/src/engine.py`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/examples/vera_linear_pr_review_prompt_v1.md`

## Operator interpretation rule

If Control Tower or another delegated lane needs a plain reading of CJ intent, use this file first.

If this file conflicts with the current live workspace state:

- treat this file as intent
- treat the live workspace as current state
- use the guarded change-control and validation lanes to close the gap
