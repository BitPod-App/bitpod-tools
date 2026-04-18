# BIT-35 scoped live admin execution handoff — 2026-04-16

Status: ready for fresh execution thread
Owner: Product Development / Control Tower scoped handoff
Primary issue: [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-automations-as-per-cjs)

## Scope of this handoff

This handoff is intentionally narrow.

It is authorized to execute only the native Product Development settings that already have a Control Tower partial GO:

1. default issue status = `Backlog`
2. duplicate mapping = `Duplicate`
3. status descriptions exactly as listed in the live admin checklist
4. auto-archive closed issues after `1 month`
5. keep Triage = `Off`

It must **not** mutate:

- `Backlog -> Icebox 🧊 -> Stale` as if native Linear expresses that end to end
- blocker taxonomy cleanup
- GitHub-triggered workflow settings beyond notes/validation
- workspace project statuses
- workspace project templates

## Required artifacts before mutation

Capture and save or attach:

- pre-change screenshot of Product Development issue-workflow/settings page
- pre-change screenshot of duplicate mapping
- pre-change screenshot of auto-archive / triage settings if separate
- short rollback note describing how to restore prior descriptions/settings

## Exact settings to apply

### Workflow names
Leave unchanged:

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

### Default status
Set default issue status to:

- `Backlog`

### Duplicate mapping
Set duplicate issue status mapping to:

- `Duplicate`

### Status descriptions
Apply exactly:

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

### Auto-archive
Set closed issue auto-archive to:

- `1 month`

### Triage
Keep:

- `Off`

## Required post-change validation

Capture and attach:

- post-change screenshot of Product Development issue-workflow/settings page
- screenshot showing `Backlog` as default
- screenshot showing `Duplicate` mapping
- screenshot showing auto-archive setting
- screenshot or note confirming Triage remains `Off`

Then post a validation comment in BIT-35 that states:

- what changed
- what was intentionally left out of scope
- where the screenshots live
- that `Backlog -> Icebox 🧊 -> Stale` remains custom enforcement, not native Linear truth

## Close conditions for this handoff

This handoff is complete only when:

- the exact scoped settings above are applied
- the pre/post evidence package exists
- the rollback note exists
- a validation note is posted in BIT-35
- Control Tower can truthfully mark this scoped pass validated
