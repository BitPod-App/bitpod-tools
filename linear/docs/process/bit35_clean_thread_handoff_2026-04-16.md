# BIT-35 clean thread handoff — 2026-04-16

Use this as the only starting context for a fresh thread.

## Goal
Apply only the already-approved **narrow BIT-35 live Linear admin changes** for the Product Development team, with screenshot proof and rollback note.

## Canonical links
- [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)
- [BIT-319 — Product Development blocker cleanup toward native dependencies + minimal blocker taxonomy](https://linear.app/bitpod-app/issue/BIT-319/product-development-blocker-cleanup-toward-native-dependencies-minimal)
- [BIT-320 — Align GitHub-triggered Linear automations with fail-closed merge readiness](https://linear.app/bitpod-app/issue/BIT-320/align-github-triggered-linear-automations-with-fail-closed-merge)
- [BIT-322 — Inventory workspace project statuses and define the coarse canonical model](https://linear.app/bitpod-app/issue/BIT-322/inventory-workspace-project-statuses-and-define-the-coarse-canonical)
- [BIT-323 — Set up workspace project templates for Product Development standard work and release trains](https://linear.app/bitpod-app/issue/BIT-323/set-up-workspace-project-templates-for-product-development-standard)

## GO now
Apply only these live Product Development settings:
1. default issue status = `Backlog`
2. duplicate mapping = `Duplicate`
3. status descriptions:
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
4. auto-archive closed issues after `1 month`
5. keep Triage = `Off`

## NOT in scope
Do **not** change any of these in the same pass:
- `Backlog -> Icebox 🧊 -> Stale` as native Linear automation
- blocker taxonomy / `BIT-319`
- GitHub-triggered workflow config / `BIT-320`
- workspace project statuses / `BIT-322`
- workspace project templates / `BIT-323`

## Required proof
Before changes:
- screenshot Product Development workflow/settings page
- screenshot duplicate mapping
- screenshot auto-archive / triage settings
- short rollback note

After changes:
- screenshot Product Development workflow/settings page
- screenshot showing `Backlog` as default
- screenshot showing `Duplicate` mapping
- screenshot showing auto-archive `1 month`
- screenshot or note that Triage is still `Off`

## Required BIT-35 comment after execution
Post a validation comment in BIT-35 saying:
- what changed
- what was intentionally left out of scope
- where the screenshots live
- that `Backlog -> Icebox 🧊 -> Stale` remains custom enforcement, not native Linear truth

## Source docs if needed
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/bit35_live_admin_go_no_go_decision_2026-04-16.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/bit35_scoped_live_admin_execution_handoff_2026-04-16.md`
