# BIT-35 Product Development Live Admin Execution Checklist v1

Date: 2026-04-15
Owner: Product Development
Primary issue: [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)
Supporting doctrine:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_model_v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_guide_v3.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_process_v1_1_control_tower_change_proposal_2026-04-15.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_process_cj_intent_packet_2026-04-15.md`

## Purpose

Turn BIT-35 into a concrete live admin/config lane with:

- exact target settings
- exact description text
- explicit native-vs-custom automation split
- screenshot requirements
- rollback notes

This file is for the live Linear UI/admin execution pass. It does not replace the repo-side doctrine.

## Source-of-truth product constraints

Official Linear docs used for this checklist:

- Issue status: [linear.app/docs/configuring-workflows](https://linear.app/docs/configuring-workflows)
- Delete and archive issues: [linear.app/docs/delete-archive-issues](https://linear.app/docs/delete-archive-issues)
- GitHub integration: [linear.app/docs/github-integration](https://linear.app/docs/github-integration)
- Project templates: [linear.app/docs/project-templates](https://linear.app/docs/project-templates)
- Issue templates: [linear.app/docs/issue-templates](https://linear.app/docs/issue-templates)

Important implementation truth from those docs:

- team issue workflows are team-specific
- default issue status is native and should be `Backlog`
- duplicate mapping is native and should map to `Duplicate`
- auto-close only closes into a closed status and does not implement arbitrary open-status aging transitions
- auto-archive is native
- project statuses are workspace-level
- project templates can be workspace-level or team-level
- issue templates can be workspace-level or team-level, but workspace templates cannot preset team-specific labels/statuses

## Current live Product Development snapshot

Observed live statuses:

- `Backlog`
- `Icebox 🧊`
- `Ready`
- `In Progress`
- `In Review`
- `Delivered`
- `Accepted`
- `Done`
- `Canceled`
- `Duplicate`
- `Won't Do`
- `Obsolete`
- `Stale`

Observed live label groups:

- `Issue Type`
- `Delivered - PM Gate`
- `In Review - QA Gate`
- `Blocked By`

Observed live type labels:

- `🏁 Release`
- `📄 Plan`
- `⚙️ Chore`
- `🐞 Bug`
- `🎨 Design`
- `⭐️ Feature`

## Execution rule

Do not claim BIT-35 complete unless both are true:

1. the live Product Development UI/admin state matches the agreed target closely enough
2. the change is evidenced with screenshots, rollback note, and post-change validation

## Native Linear settings to change now

These are the changes that belong in the Linear UI itself.

### 1. Team workflow names

Keep the current live names:

- `Backlog`
- `Icebox 🧊`
- `Ready`
- `In Progress`
- `In Review`
- `Delivered`
- `Accepted`
- `Done`
- `Canceled`
- `Duplicate`
- `Won't Do`
- `Obsolete`
- `Stale`

Do not rename `In Review`, `Delivered`, `Accepted`, or the current PM/QA result labels in this pass.

### 2. Default status

Set default issue status to:

- `Backlog`

Validation:

- confirm the status row shows `Default`
- create or simulate a new issue and verify it lands in exact status `Backlog`

### 3. Duplicate mapping

Set duplicate issue status mapping to:

- `Duplicate`

Validation:

- mark a test issue duplicate of another issue
- verify the issue lands in `Duplicate`, not generic `Canceled`

### 4. Status descriptions

Apply these short descriptions in Product Development issue statuses:

- `Icebox 🧊`: `Parked for later - unlikely soon. (30d inactive -> Stale)`
- `Backlog`: `Default for planned work, not ready to start. (30d inactive -> 🧊)`
- `Ready`: `All set, ready to start`
- `In Progress`: `Being worked on now`
- `In Review`: `Current review gate for Product Development`
- `Delivered`: `Waiting on PM acceptance`
- `Accepted`: `PM accepted; work approved`
- `Done`: `Fully complete and closed`
- `Canceled`: `Stopped / aborted`
- `Duplicate`: `Covered by another issue`
- `Won't Do`: `Decided not worth doing`
- `Obsolete`: `No longer relevant`
- `Stale`: `Inactive too long; closed but can reopen`

### 5. Auto-archive

Set:

- auto-archive closed issues after `1 month`

Reason:

- this is natively supported
- it matches the current doctrine well enough

Validation:

- screenshot the team setting
- note that changes can take up to 24 hours to apply

### 6. Triage

Keep Triage:

- `Off`

Reason:

- current Product Development process is not using Triage as an intake surface

### 7. Closed-status interpretation

Document these meanings in BIT-35 validation notes:

- `Duplicate` = duplicate flow only
- `Won't Do` = explicit non-pursuit decision
- `Stale` = inactivity-close state
- `Canceled` = stopped / aborted without stronger claim
- `Obsolete` = legacy edge-case; do not use as the default inactivity sink

## Native settings to leave alone in this pass

Do not mutate these yet as part of BIT-35 unless a separate guarded child lane is being executed with matching proof:

- workspace project statuses
- workspace project templates
- team/workspace issue-template redesign
- blocker label-group redesign beyond description-level clarification
- broad label-group renames

These belong to:

- `BIT-319`
- `BIT-322`
- `BIT-323`

## Behavior that is not natively expressible and must stay in custom enforcement

The following should not be misrepresented as native Linear issue-status automation:

### 1. `Backlog -> Icebox 🧊`

Linear native auto-close closes issues into a closed status.

It does not implement:

- open-status aging from `Backlog` to `Icebox 🧊`

Therefore this behavior stays in:

- custom bot/enforcement layer
- or a future external automation surface

### 2. `Icebox 🧊 -> Stale`

If native auto-close can be configured to target `Stale`, that still does not solve the full intended path by itself, because:

- native auto-close is a closed-status automation
- it is not the same thing as the full backlog-aging policy
- it will also be affected by the cycle/project completion rules documented by Linear

Therefore the canonical truth remains:

- use custom enforcement for the intended two-step aging path
- do not claim native Linear alone now expresses the full rule

### 3. Fail-closed merge readiness

The exact rule:

- merge to `main` only closes when status is `Accepted`, QA + PM outcome labels exist, blocker truth is clear, and issue type is not `Release`

belongs in:

- repo engine
- `Update Linear`
- custom GitHub/Linear enforcement

not pure native Linear settings.

## GitHub integration target for BIT-35 notes

Native GitHub integration can stay enabled, but the strict truth rules belong in the enforcement layer.

Near-term intent:

- branch/PR open can move to `In Progress`
- review-ready PR state can move to `In Review`
- merge to `main` should not independently bypass the custom fail-closed merge-readiness rule

Operational note:

- if native GitHub automation and custom enforcement conflict, custom enforcement is authoritative
- exact live alignment work belongs in `BIT-320`

## Label-group handling in this pass

### Keep as-is now

Keep the current live groups for this pass:

- `Issue Type`
- `Delivered - PM Gate`
- `In Review - QA Gate`
- `Blocked By`

Reason:

- current code/tests/docs still couple to the current PM/QA label names
- blocker cleanup is a separate guarded lane

### Long-term intended direction

Still active, but not part of this immediate live mutation pass:

- native dependencies first
- one generic `blocked` label for non-ticket blockers

This direction was deferred, not rejected.

It belongs to:

- `BIT-319`

## Screenshots / evidence required

BIT-35 should not be marked complete without these:

1. Product Development issue-status page showing:
- all active statuses
- default `Backlog`
- status descriptions

2. Product Development issue-status automation section showing:
- duplicate mapping
- auto-archive setting
- any auto-close setting that remains enabled

3. If any native GitHub-linked workflow automation settings are changed:
- screenshot those settings too

4. One validation artifact showing:
- new issue lands in `Backlog`
- duplicate mapping lands in `Duplicate`
- no accidental rename broke the current workflow names

## Rollback note

If this live pass creates confusion or drift:

1. restore previous status descriptions from screenshot evidence
2. restore previous duplicate/auto-archive settings from screenshot evidence
3. leave workflow names unchanged
4. post rollback note in `BIT-35`
5. keep repo doctrine unchanged until the new live plan is re-validated

## Completion checklist for BIT-35

- [ ] pre-change screenshots captured
- [ ] default status verified as `Backlog`
- [ ] duplicate mapping verified as `Duplicate`
- [ ] status descriptions updated
- [ ] auto-archive set to 1 month
- [ ] Triage remains off
- [ ] any native auto-close setting is documented truthfully, including what it does not cover
- [ ] post-change screenshots captured
- [ ] validation note posted in `BIT-35`
- [ ] Control Tower validation recorded
