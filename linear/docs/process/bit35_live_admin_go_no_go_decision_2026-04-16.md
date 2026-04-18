# BIT-35 live Linear admin go / no-go decision — 2026-04-16

Status: active Control Tower decision note
Owner: Control Tower / Product Development
Primary issue: [BIT-35 — Reconfigure Linear Issues, Issue Status,, & Automations as per CJ's instructions](https://linear.app/bitpod-app/issue/BIT-35/reconfigure-linear-issues-issue-status-and-automations-as-per-cjs)

## Decision summary

Control Tower decision: **partial GO**.

It is okay to execute the narrow native Product Development settings already fully specified in the live admin checklist, as long as the guarded-lane evidence package is captured during execution:

- pre-change screenshots / snapshot
- exact execution record
- rollback note
- post-change validation screenshots
- validation note in BIT-35

It is **not** okay to treat the broader deferred config family as implicitly approved just because the doctrine exists.

## GO now — scoped BIT-35 native settings only

These are approved for guarded execution now because they are already explicitly specified, preserve current live workflow names, and are reversible:

1. Default issue status = `Backlog`
2. Duplicate mapping = `Duplicate`
3. Product Development status descriptions:
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
4. Auto-archive closed issues after `1 month`
5. Keep Triage = `Off`

## NOT GO yet — still separate guarded lanes

These remain deferred and should not be silently bundled into the BIT-35 live pass:

1. `Backlog -> Icebox 🧊` automation as a native Linear rule
   - stays custom enforcement, not native config
2. `Icebox 🧊 -> Stale` or `Obsolete` inactivity-close policy as if native Linear fully expresses it
   - stays custom enforcement / doctrine until separately proven
3. Blocker taxonomy cleanup / dependency cleanup
   - belongs to BIT-319
4. GitHub-triggered Linear automation alignment
   - belongs to BIT-320
5. Workspace project-status normalization
   - belongs to BIT-322
6. Workspace project-template creation
   - belongs to BIT-323

## Why project statuses and templates are still no-go

Even though they simplify the model, the current artifacts for BIT-322 and BIT-323 are still proposal/inventory notes, not validated live mutation packets. They still need:

- live availability check
- pre-change snapshot
- rollback note
- post-change validation
- Control Tower closeout on the evidence package

## Execution rule

If a fresh execution thread is opened now, it should be scoped only to the GO-now BIT-35 settings above.

It should not opportunistically mutate project statuses, project templates, blocker taxonomy, or GitHub-triggered workflow settings in the same pass.
