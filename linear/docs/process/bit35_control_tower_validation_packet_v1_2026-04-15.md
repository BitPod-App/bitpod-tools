# BIT-35 Control Tower Validation Packet v1

Date: 2026-04-15
Status: Active validation packet
Owner: Control Tower / Product Development
Primary issue: [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)

## Purpose

Provide the Control Tower validation artifact for the BIT-35 live Linear admin/config lane.

This packet exists because:

- repo-side doctrine and enforcement are now aligned
- live Product Development admin/config mutation is still not validated end to end
- Control Tower policy requires completion to be validated, not inferred

## Lane ledger

Lane name:
- `BIT-35 live Product Development workflow/admin execution`

Owner:
- `Control Tower` for validation
- `Product Development` for the admin mutation artifact

Objective:
- align the live Product Development Linear issue workflow/settings with the current approved doctrine as far as the native Linear surface can truthfully express

Permission level:
- guarded mutation

Expected artifact:
- pre-change snapshot
- exact checklist execution record
- rollback note
- post-change validation screenshots
- explicit note of what remained custom enforcement vs native Linear config

Current state:
- `DONE_UNVALIDATED` for repo-side alignment
- `NOT_STARTED` for the live admin mutation pass unless and until screenshots/proof are attached

Auto-chain:
- only after `DONE_VALIDATED`

Linear impact:
- team config
- issue statuses
- status descriptions
- duplicate mapping
- auto-close / auto-archive settings
- GitHub automation notes

Truth surfaces touched:
- team config
- project config references
- agent / awareness surfaces
- `Update Linear` doctrine

Escalate-back conditions:
- live UI and repo doctrine diverge in a material way
- native Linear cannot express a requested rule and the lane is about to pretend otherwise
- blocker/dependency truth is unclear
- GitHub / Linear automation truth conflicts with the repo enforcement layer
- screenshots or rollback notes are missing

Next step if done:
- auto-chain into only the next already-approved guarded lane that depends on the validated live state

Last validated outcome:
- repo-side implementation validated
- live Product Development admin/config mutation not yet validated in this packet

## What Control Tower must validate

Control Tower should not accept BIT-35 as complete until all of these are true:

1. Artifact exists
- the live admin execution artifact exists:
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/bit35_product_development_live_admin_execution_checklist_v1_2026-04-15.md`

2. Scope was respected
- no hidden renames beyond the agreed current-name-preserving plan
- no speculative project-status redesign slipped into the team workflow lane
- no blocker cleanup beyond the approved BIT-35 scope

3. Permission level was respected
- high-blast or cross-surface changes were not made without the documented guarded artifact package

4. Blockers and uncertainty were labeled truthfully
- native-vs-custom automation limits were named explicitly
- if a requested rule could not be implemented natively, the record says so
- no fake “done” claim was made because a similar but weaker setting exists

5. Any mutation was explicitly authorized and evidenced
- pre-change screenshots exist
- post-change screenshots exist
- rollback note exists
- validation note exists

## Validation checklist

### Required live proof

- [ ] Product Development issue-status page screenshot before changes
- [ ] Product Development issue-status page screenshot after changes
- [ ] screenshot showing default status is `Backlog`
- [ ] screenshot showing duplicate mapping is `Duplicate`
- [ ] screenshot showing auto-archive setting
- [ ] if any native auto-close is enabled, screenshot and explanation of what it actually does
- [ ] validation note posted in `BIT-35`

### Required truth checks

- [ ] workflow names remain intact: `Backlog`, `Ready`, `In Progress`, `In Review`, `Delivered`, `Accepted`, `Done`
- [ ] `Stale` remains the intended inactivity-close status in doctrine
- [ ] `Obsolete` is not falsely presented as the primary inactivity sink
- [ ] no claim that native Linear alone now expresses `Backlog -> Icebox 🧊 -> Stale`
- [ ] no claim that native Linear alone now enforces fail-closed merge readiness

### Required operator-surface checks

- [ ] BIT-35 references the current doctrine artifacts
- [ ] BIT-35 references the CJ intent artifact
- [ ] BIT-35 notes which remaining changes still belong to guarded child lanes

## Continuous validation loop

This loop should continue only while the lane is unvalidated.

### Loop state machine

Allowed states for this packet:

- `NOT_STARTED`
- `RUNNING`
- `DONE_UNVALIDATED`
- `DONE_VALIDATED`
- `BLOCKED`
- `PAUSED_BY_CJ`
- `CLOSED`

### Loop rule

Control Tower repeats the following until `DONE_VALIDATED`, `BLOCKED`, `PAUSED_BY_CJ`, or `CLOSED`:

1. check whether the required artifact bundle exists
2. check whether the live screenshots/proof are present
3. check whether the mutation matched scope
4. check whether any native-vs-custom truth was overstated
5. either:
   - mark `DONE_VALIDATED`, or
   - return `BLOCKED` with explicit missing artifact / mismatch, or
   - continue if a currently owned follow-up step is still executing

### No-longer-than-needed rule

This validation loop must stop as soon as one of these is true:

- `DONE_VALIDATED`
- `BLOCKED`
- `PAUSED_BY_CJ`
- `CLOSED_AS_SUPERSEDED`

It must not remain as a vague perpetual supervision thread once the lane state is clear.

## Current truthful status

As of this packet:

- repo doctrine: aligned
- repo enforcement/tests: aligned
- live Product Development admin truth: not yet validated here
- Control Tower completion loop: now defined, but not yet satisfied because the live admin evidence package is still incomplete

## Recommended next action

Use this packet together with:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/bit35_product_development_live_admin_execution_checklist_v1_2026-04-15.md`

Then execute or validate the live Product Development admin/config pass and close this packet only when the required screenshots and notes exist.
