# `taylored_linear_ops`

Status: Active canonical model
Owner: Product Development
Primary planning lane: [BIT-175 — Linear operating model v1 rollout plan](https://linear.app/bitpod-app/issue/BIT-175/linear-operating-model-v1-rollout-plan)
Replanning lane: [BIT-183 — Re-plan with CJ in order to update BIT-175 post learnings](https://linear.app/bitpod-app/issue/BIT-183/re-plan-with-cj-in-order-to-update-bit-175-post-learnings)

## Abstract

Build a full, opinionated Linear operating model that is heavily influenced by Pivotal Tracker, while adapted for AI-assisted execution.

The active v1 model remains the structural baseline: statuses, gate-driven movement, one shared board, blocker semantics, cycle cadence, estimate discipline, and the role of `Update Linear` remain canonical where still correct. This document rewrites that baseline into one complete operating doctrine.

Maintenance update — 2026-04-15:

- align risky workflow/admin/guidance changes under Control Tower validation and Taylor01 reliability guardrails
- preserve current live status and label names that are already wired into code, tests, prompts, and agent guidance
- keep GitHub-driven Linear truth, but fail closed when QA, PM, blocker, or merge-readiness truth is incomplete
- treat the current Vera-style QA surface as a truthful substitute surface, not proof of embodied independent Vera authority

Pivotal's discipline still matters:

- small scoped work
- meaningful backlog order
- explicit gates
- truthful completion
- tools that constrain behavior instead of tolerating chaos

AI changes one major thing: the smallest unit of implementation is no longer always the best unit of request. Very small tasks can complete in under a minute, so execution should remain small without forcing work to stop after every microscopic step. That is why `Plan` tickets exist. They serve the role epics normally serve, but in a more operational, chronological, and execution-aware way.

The same philosophy should be portable to other systems later, but this document is specifically for Linear. Assume the workflow automations already exist. Adapter-layer skills and HTTPS endpoints may later override parts of this model, but this document is the canonical default doctrine, not an options menu.

## Lane boundary

This document is the active BitPod-specific Linear operating overlay.

It may stay current for the BitPod execution lane while Taylor portability work is still in progress.

Do not treat this document, or current local `SKILL.md`-based operator surfaces around it, as the final Taylor capability model.

## Truth note

The original long planning paragraph that informed this lane was lost to memory compaction. This document is the truthful reconstruction from:

- surviving repo docs
- live Product Development team state
- existing Linear tickets
- the obsolete `PLAN.md`
- CJ planning decisions captured after the loss

## Purpose

Define one complete Linear operating model for a team that wants:

- one clear workflow
- one shared board per team
- strong status truth
- narrow, meaningful labels
- explicit QA and PM gates
- minimal but useful planning hierarchy
- automation-backed enforcement
- a Pivotal-style operating feel without pretending AI teams work like 2015 human-only scrum teams

## Authority boundary

Control Tower owns:

- lane creation
- lane validation
- sequencing
- blocker truth
- stale-lane retirement
- truth-surface synchronization
- final recommendation packets

Taylor01 / Product Development Linear doctrine owns:

- workflow semantics
- team-level admin config proposal
- issue/project template proposal
- status/label/automation truth model

`Update Linear` and enforcement lanes own:

- fail-closed mutation behavior
- merge-readiness checks
- gate-evidence enforcement
- skip-policy enforcement

Practical rule:

- no risky workflow/admin mutation is complete until the artifact and evidence package is validated through the Control Tower lane
- thread completion is not task completion
- any workflow/guidance rename or config change touching a live truth surface is a guarded lane, not an ad hoc tweak

## Core philosophy

### Pivotal influence, adapted

The core doctrine is:

- smaller scoped work is better
- backlog order should mean something
- `Ready` should mean actually ready
- review and acceptance should be explicit
- completion should reflect reality, not optimism
- the tool should constrain behavior instead of tolerating chaos

The smallest unit of implementation is not always the best unit of request. Execution should still happen in small pieces, but AI teams often need those pieces to live under a parent container so the system can keep moving until the full feature is meaningfully complete.

### What Plan tickets are for

`Plan` tickets serve the purpose epics normally serve.

A `Plan` ticket is:

- a parent ticket
- created through real planning
- broken into sub-issues in chronological rollout order
- used when one coherent feature or initiative should be requested as one thing, but executed as smaller nested tickets

This keeps the Pivotal instinct of smaller parts and clearer work while adapting it for agents that move fast enough that stopping after each tiny step becomes counterproductive.

Outside of `Plan` and `Release`, sub-issues should generally be avoided.

### Projects are not epics

Plans are the epic-equivalent.

Projects are for really large, long-term bodies of work such as:

- building an iOS app
- a major app rewrite
- a massive architecture overhaul
- a very large multi-month product track

Projects should not be used for ordinary features or as a second backlog.

## Canonical workflow

### Workflow map

| Stage | Status | Short description |
|---|---|---|
| Cold | `Icebox 🧊` | Parked for later; unlikely to be done soon |
| Intake | `Backlog` | Default landing place for real work that is not yet execution-ready |
| Ready lane | `Ready` | Fully shaped and allowed to start |
| Execution | `In Progress` | Active implementation or execution |
| Review gate | `In Review` | Current Product Development review gate; QA is the default meaning today |
| PM gate | `Delivered` | Review-cleared work waiting for PM acceptance or rejection |
| Accepted end-state | `Accepted` | PM accepted; work approved |
| Done end-state | `Done` | Fully complete and closed |
| Canceled | `Canceled` | Intentionally stopped without stronger semantic claim |
| Canceled | `Duplicate` | Superseded by canonical work elsewhere |
| Canceled | `Won't Do` | Explicitly understood and intentionally not implemented |
| Canceled | `Stale` | Auto-closed for inactivity; can be reopened later |
| Legacy edge-case | `Obsolete` | Context changed; no longer relevant; do not use as the primary inactivity sink |

### Path map

Standard path:
`Backlog -> Ready -> In Progress -> In Review -> Delivered -> Accepted -> Done`

Rejection loops:
`In Review --qa-failed--> In Progress`
`Delivered --pm-rejected--> In Progress`

Aging path:
`Backlog --30d inactive--> Icebox 🧊 --30d inactive--> Stale`

### Status rules

- Default issue status is `Backlog`
- `Ready` is the only canonical execution-ready status
- `Accepted` and `Done` are both real and are not duplicates
- `Accepted` means PM accepted; work is approved
- `Done` means the issue is fully complete and closed
- `Icebox 🧊` is not a default intake lane
- `Stale` is the default inactivity-close status
- `Obsolete` is a legacy edge-case status and not the primary inactivity sink
- no emoji issue statuses except `Icebox 🧊`
- assume work generally requires both QA-result truth and PM-result truth before merge-driven closure

## One shared board

There should be exactly one shared board per team.

That board is the primary operating surface. It should include the full workflow, including completed and canceled-family statuses. Personal filters are fine. Shared workflow reality stays singular.

Use:

- Layout: `Board`
- Columns: `Status`
- Rows: `None`
- one team-wide shared board
- no competing main boards

Default shared-board configuration:

- Ordering: `Updated`, descending
- Completed recently: `On`
- Completed issues window: `Last month`
- Show sub-issues: `On`
- Show empty columns: `Off`
- Project filter: blank
- Status Type filter: blank
- Assignee filter: blank
- Issue Type filter: `All`
- AI filter: blank

This board is the closest Linear equivalent to a single meaningful Pivotal board.

## Ticket types

Canonical issue types:

- `Plan`
- `Feature`
- `Bug`
- `Chore`
- `Design`
- `Release`

### Type descriptions

| Type | Short description |
|---|---|
| `Plan` | Parent planning ticket that structures one coherent rollout through chronological sub-issues |
| `Feature` | User-facing or team-facing meaningful enhancement |
| `Bug` | Broken behavior, regression, or defect fix |
| `Chore` | Maintenance, upgrades, cleanup, or non-feature technical work |
| `Design` | Standalone UI/UX or design-system work owned by design agents |
| `Release` | Large coordinated shipping object with a real release date and grouped rollout scope |

### Type rules

- No ticket can move to `Ready` without exactly one canonical type assigned
- no extra type taxonomy
- `Plan` and `Release` are the only issue types where sub-issues are generally expected
- outside of `Plan` and some `Release` tickets, sub-issues should usually be avoided

### Feature definition

Define a `Feature` as:

> A user-facing or team-facing meaningful enhancement.

## Plan tickets

Plan tickets are the epic-equivalent.

Use them when:

- one feature needs a real planning pass first
- work should be broken into 3–8 smaller steps
- a coherent rollout should be requested as one thing
- smaller nested tickets make execution more truthful and less brittle

Plan tickets should:

- be created through real planning
- act as parent tickets
- own chronological sub-issues
- stay out of cycles unless there is a very strong reason
- not be treated as normal velocity units

## Release tickets

Release tickets are like Plans, but larger, looser, and tied to actual shipping.

A Release ticket is:

- the only ticket type with a real date
- a grouped release object
- a coordinated shipping container
- likely associated with a major version bump
- expected to include a checklist of everything that must be `Done` before shipping

A Release should usually also imply:

- final verification
- release notes or announcement work
- rollout checks
- post-release checks
- version bump coordination

## Estimates

Every single ticket must have at least `1` point.

Use:

- `1`
- `2`
- `3`
- `5`
- `8`

Do not allow unestimated active work. Do not allow `0-point` philosophical exceptions.

### Who estimates what

| Type | Estimated by |
|---|---|
| `Feature` | Engineering |
| `Bug` | Engineering |
| `Chore` | Engineering |
| `Plan` | Product + Engineering |
| `Release` | Product + Engineering |
| `Design` | Design / UI-UX agents |

### Estimation policy by type

| Type | Pointed by default? | Notes |
|---|---:|---|
| `Feature` | Yes | Always pointed |
| `Bug` | Yes | Minimum 1 even when tiny |
| `Chore` | Yes | Minimum 1; chores and features can blur in practice |
| `Plan` | Yes | If acting mostly as a parent container, children carry most forecasting value |
| `Design` | Yes | Estimated by design agents based on scope |
| `Release` | Yes | Estimated as a coordination object, not pure implementation effort |

## Labels, gates, and automation

Use labels mainly as automation triggers. Labels should only stay on tickets while they still make sense.

### Canonical label groups

Use exactly four single-select label groups with short descriptions in the current live model:

- `Issue Type`
- `Blocked By`
- `QA Review`
- `PM Review`

### `Issue Type`

Description: `Primary work type`

- `Plan` — `Parent planning ticket for one coherent rollout`
- `Feature` — `Meaningful enhancement for users or the team`
- `Bug` — `Broken behavior, regression, or defect fix`
- `Chore` — `Maintenance, cleanup, upgrade, or refactor work`
- `Design` — `Standalone UX, UI, or design-system work`
- `Release` — `Coordinated shipping object with real rollout scope`

### `Blocked By`

Description: `Current generic blocker reason`

- `needs-discussion` — `Blocked pending discussion`
- `needs-pm` — `Blocked pending PM input`
- `needs-specs` — `Blocked by missing or unclear specs`
- `needs-decision` — `Blocked pending decision`
- `needs-CTO` — `Blocked pending CTO technical direction`
- `needs-type` — `Blocked by missing issue type`
- `needs-estimate` — `Blocked by missing estimate`
- `needs-other` — `Blocked for another reason; required comment explains it`

Rules:

- `Blocked By` is metadata only
- it is not a status, lane, swimlane, or gate
- use native Linear dependencies whenever one ticket is blocked by another specific ticket
- use blocker labels only for generic conditions not best represented as another issue
- keep blocker naming professional
- `needs-other` requires a comment

Near-term direction:

- prefer native Linear dependencies whenever one issue blocks another
- do not expand the blocker taxonomy
- future cleanup should converge toward native dependencies plus one generic `blocked` signal for non-ticket blockers

### `QA Review`

Description: `QA result used to unlock work out of In Review`

- `qa-passed` — `QA passed with artifact`
- `qa-failed` — `QA failed with artifact`
- `qa-skipped` — `QA skipped with explicit authorization`

### `PM Review`

Description: `PM result used to unlock work out of Delivered`

- `pm-accepted` — `PM accepted with artifact`
- `pm-rejected` — `PM rejected with artifact`
- `pm-skipped` — `PM skipped with explicit authorization`

### Gate rule summary

- `In Review` remains the current Product Development review gate
- `Delivered` means PM acceptance / rejection stage
- labels trigger automation
- stale gate labels must be cleared on re-entry to the relevant status
- labels should not linger after they stop being semantically useful
- there are no pending QA or PM labels
- current Vera-style QA prompts and review skills must describe themselves truthfully as substitute surfaces unless a stronger independent runtime exists

## Blockers vs native Linear dependencies

Use native Linear dependencies whenever a ticket is blocked by another specific issue.

Use blocker labels only when the blocker is not best represented as another issue.

Use native `blocked by` when:

- ticket A depends on ticket B
- a design issue must finish before an implementation issue
- a release gate depends on specific issue completion
- one real ticket blocks another real ticket

Use blocker labels for generic conditions such as:

- `needs-CTO`
- `needs-pm`
- `needs-specs`
- `needs-other`

Do not use blocker labels as a lazy substitute for proper issue-to-issue blocking.

## Review, acceptance, and skips

### Canonical transition table

| Current | Trigger | Evidence | Next |
|---|---|---|---|
| `In Progress` | ready for QA | execution evidence | `In Review` |
| `In Review` | `qa-passed` | QA artifact | `Delivered` |
| `In Review` | `qa-failed` | QA artifact | `In Progress` |
| `In Review` | `qa-skipped` | skip authorization + reason | `Delivered` |
| `Delivered` | `pm-accepted` | acceptance artifact | `Accepted` |
| `Delivered` | `pm-rejected` | rejection artifact + reason | `In Progress` |
| `Delivered` | `pm-skipped` | skip authorization + reason | `Accepted` |
| `Accepted` | merge to `main` with merge-ready truth satisfied | merge evidence | `Done` |

### Skip controls

Skips should be allowed through skills, either:

- per ticket
- per ticket type
- or as global toggles

These are policy controls, not excuses for workflow sloppiness.

Near-term skip rules:

- `qa-skipped` is allowed for clearly non-technical or QA-inappropriate Product Development work, especially `Design`
- `pm-skipped` is allowed only for conservative low-risk cases with explicit reason artifact
- `pm-skipped` must not bypass blocker truth, release truth, or merge-readiness truth

## Delegation

Support delegation through skills.

Delegated acceptance belongs in the enforcement layer, not in native Linear structure. PM labels and artifacts still record the truth even when a PM-role agent performs the action.

## Descriptions

Every:

- issue status
- label group
- label

should have a short description.

Keep them short. One sentence or less.

## Native Linear vs enforcement layer

### Native Linear should handle

- statuses
- board layout
- cycles
- relations
- parent / sub-issue support
- baseline workflow structure

### The enforcement layer should handle

- truth validation
- gate evidence checks
- skip authorization
- label hygiene
- status-transition enforcement
- delegated PM logic
- rejection comments
- blocker-aware merge refusal
- mutation refusal when requirements are missing
- persistence of short-lived structured operational memory if that layer exists

## `Update Linear`

`Update Linear` is the mutation contract.

Whenever an agent makes workflow changes, `Update Linear` should happen as part of that change flow, not as an afterthought.

Its job is to make the ticket more truthful and fail closed when required truth-maintenance steps are missing.

`Update Linear` must:

- validate status, labels, assignee / delegate, and relation hygiene together
- refuse moves that skip required evidence or required fields
- enforce type and estimate requirements before `Ready` and `In Progress`
- enforce gate artifacts before `qa-*` and `pm-*` labels
- leave explicit correction comments when merge, close, or skip truth is incomplete
- never silently apply partial truth updates
- leave an explicit correction comment when a mutation is rejected

Persistence notes:

- changes are recorded temporarily in the DB for 30 days
- Linear ticket history remains the permanent durable log
- QA artifacts / reviews are posted in the ticket, in the PR, and in the DB for 30 days

## Projects

Use Projects sparingly.

Projects are for big, long-term bodies of work. Do not use them for:

- normal features
- one medium release
- ordinary cleanup
- things that should just be Plans

Prefer using the Project itself rather than creating project-label sprawl.

Project rule:

- projects are coordination containers, not execution workflows
- workspace project statuses should stay coarse and non-competing with the team issue workflow
- do not mirror `In Review`, `Delivered`, `Accepted`, or other team issue states into project status design

Near-term template direction:

- prefer Product Development team issue templates for issue-shaping patterns
- use workspace project templates sparingly for coarse project scaffolding such as `PD - Standard Project` and `PD - Release Train`
