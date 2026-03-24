# Linear Issue Workflow Reconfig Spec (v1)

Status: HISTORICAL / SUPERSEDED
Issue: [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)  
Owner: Taylor / Codex proposal; CJ applies UI-admin changes  
Last updated: 2026-03-22

Superseded by:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_model_v1.md`

## Purpose

Define the exact BitPod Product Development issue workflow target so team settings can be reconfigured once, verified, and versioned in repo.

This file is no longer the canonical repo-side specification. It preserves the earlier BIT-35 workflow/config target and should be read as historical planning input only. The active canonical contract is `linear_operating_model_v1.md`.

## Source instruction to preserve exactly

CJ's binding instruction for this issue was:

- Configure Issue Statuses & Automations based on **How we work at Linear** with Default Issue Status = **Backlog** upon creation:
  - [Configuring workflows / default status](https://linear.app/docs/configuring-workflows#default-status)
- `Icebox` issues should be manually moved there if they may no longer be relevant until further notice.
- Add automation: any issue in `Backlog` for more than 30 days moves to `Icebox` and posts that the move was automatic.
- Add automation: any stale issue with no activity for more than 60 days is auto-closed with status `Obsolete` and related team members are notified.
- All issues in any closed state are auto-archived after 1 month:
  - [Auto-close / archive docs](https://linear.app/docs/delete-archive-issues#auto-close)

Related general references:

- [Linear Method: Introduction](https://linear.app/method/introduction)
- [Linear Method: Build in public](https://linear.app/method/build-in-public)
- [Linear Teams](https://linear.app/docs/teams)

## Target issue workflow

### Active statuses

These are the target active statuses for the Product Development team:

1. `Backlog`
2. `Todo`
3. `In Progress`
4. `In Review`
5. `Done`
6. `Canceled`
7. `Duplicate`
8. `Icebox`
9. `Obsolete`

### Required semantics

- `Backlog`
  - Default issue status on creation.
  - Holds real queued work not yet selected for execution.

- `Todo`
  - Selected and actionable, but not actively being executed yet.

- `In Progress`
  - Active execution is happening.

- `In Review`
  - Waiting on review / QA / PM acceptance depending on the lane.

- `Done`
  - Completed work with required evidence attached.

- `Canceled`
  - Intentionally stopped; no longer pursued.

- `Duplicate`
  - Superseded by another issue.

- `Icebox`
  - Explicitly deprioritized.
  - May still become relevant later.

- `Obsolete`
  - Closed due to inactivity / irrelevance.

## Required automations

### Automation 1: default creation status

- New issues default to `Backlog`.

### Automation 2: Backlog aging to Icebox

If an issue remains in `Backlog` for more than 30 days:

- move issue to `Icebox`
- post comment:
  - `Auto-moved to Icebox after 30d inactivity.`

### Automation 3: Icebox staleness to Obsolete

If an issue remains stale for more than 60 days:

- move issue to `Obsolete`
- notify related team members if the setting supports it
- post comment:
  - `Auto-closed as Obsolete after 60d inactivity in Icebox.`

### Automation 4: archive closed issues

- Any issue in a closed state is auto-archived after 1 month.

## Native vs custom limitation note

- This spec remains the target BIT-35 workflow/configuration baseline. It is not a blanket claim that every automation here is already live.
- Team-native settings clearly cover configurable statuses/default status and closed-state auto-close or auto-archive behavior.
- Treat `Backlog` -> `Icebox` plus auto-comment and stale -> `Obsolete` plus notify behavior as requiring explicit verification or custom automation unless directly proven native.
- The checked-in runtime models some aging transitions, but live Linear mutations remain fail-closed until an app-actor executor is configured and attribution is verified.

## Explicit non-goals

- This issue does not define project statuses.
- This issue does not define custom emoji status names as the canonical requirement.
- This issue does not require broad taxonomy expansion.
- This issue does not require changing current issue content or evidence rules beyond preserving status semantics.

## Verification checklist

UI/admin verification must capture evidence for all of the following:

1. Team default issue status is `Backlog`
2. `Icebox` exists as a selectable issue status
3. `Obsolete` exists as a selectable closed issue status
4. Backlog aging automation is present and configured for 30 days
5. Obsolete aging automation is present and configured for 60 days
6. Closed issue auto-archive is configured for 1 month
7. At least one before/after screenshot or equivalent proof is attached to [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)
8. Existing active issues were checked for status normalization impact

## Migration note

Current live workspace behavior is mixed and should not be assumed to match this file until UI verification evidence is attached.

If repo docs and Linear UI ever diverge, this spec is the review baseline and a follow-up issue should record the delta.
