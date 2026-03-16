# Long-Thread Checkpoint Protocol v1

## Purpose

Use repo-side checkpoints when execution is long-running, multi-lane, or operationally critical so that chat-thread shrinkage does not become a hidden failure mode.

This protocol treats chat as a temporary execution surface, not the primary memory system.

## When checkpointing is required

Create or refresh a checkpoint when any of the following are true:

- the thread is materially long and prior decisions are no longer easy to inspect
- work spans multiple repos, lanes, or phases
- there is an active PR stack or merge gate that must not be forgotten
- the user is about to leave and work must resume later without relying on thread memory
- there is an incident, blocker, or capability impairment that may recur
- a lane is handed off from one thread to another

## Minimum checkpoint structure

Every checkpointed lane must have:

- one active checkpoint file
- one durable decisions log
- one incident log only if failures or impairments occurred
- one resume prompt that references repo-side artifacts instead of chat memory

## File roles

### Active checkpoint

Contains only current truth:

- active lane
- current repo/worktree/branch
- open PRs
- current issue state
- verified findings still relevant to immediate next moves
- next actions in order
- known blockers

This file should stay short and be replaced as the lane evolves.

### Decisions log

Contains durable decisions only:

- decision
- reason
- scope
- date
- related issue/PR/doc

Do not use the decisions log as a status board.

### Incident log

Use only when something failed, drifted, or required diagnosis:

- symptom
- verified facts
- incorrect assumptions to avoid repeating
- root cause if known
- workaround
- follow-up issue/doc

If there was no incident, do not create or update this file.

## Lane separation rule

Do not mix unrelated lanes into one checkpoint.

Preferred lane split:

- migration/admin
- runtime/agents
- sector-feeds/data
- branding/assets
- incidents/recovery

If a thread spans multiple lanes, checkpoint them separately.

## Naming and location

Static protocol docs and templates keep stable names.

Recurring or historical checkpoint instances should use unique names with a date or timestamp.

Recommended repo-side locations in `bitpod-tools`:

- checkpoint template:
  - `linear/protocol/templates/thread-checkpoint-template-v1.md`
- active checkpoint instances:
  - `linear/temporal/active/ticket__<ticket_id>/`
  - `linear/temporal/active/project__<project_slug>__<project_id>/`
- active stage ledger:
  - `linear/temporal/active/checkpoint_ledger.md`

Recommended file set for checkpoint instances:

- `checkpoint-<lane>-<yyyy-mm-dd>.md`
- `decisions_log_<lane>.md`
- `incident_log_<lane>.md` (only if needed)
- `resume_prompt_<lane>_<yyyy-mm-dd>.md`

## Update cadence

Refresh a checkpoint at:

- stable stopping points
- before switching lanes
- before handing off to a new thread
- after major PR/issue normalization changes
- after incident diagnosis or resolution

Do not churn checkpoints on every small command.

## Resume prompt standard

A resume prompt must:

- state cwd/repo/worktree
- identify the active issue/lane
- link open PRs
- point to the active checkpoint file
- point to any relevant decisions/incident logs
- list only the next actions that are still valid
- explicitly forbid re-opening retired noise or stale debates unless requested

## Retirement rule

Retire a thread and resume in a fresh one when:

- the thread context is visibly shrinking or drifting
- repeated re-anchoring is needed
- multiple unrelated lanes are contaminating each other
- the user asks to continue later from a clean state

When retiring a thread, produce:

- refreshed checkpoint file
- refreshed resume prompt
- one concise statement of what should happen next

## Adoption rule

A protocol doc alone is not enough.

At least one live lane must adopt:

- an active checkpoint instance
- a repo-side resume prompt

## Anti-patterns

Do not:

- rely on chat history as the sole source of truth
- mix durable decisions with ephemeral status notes
- overwrite useful historical checkpoint instances without a new dated file
- create giant monolithic handoff files spanning unrelated lanes
- pretend a lane is resumable if the checkpoint is stale
