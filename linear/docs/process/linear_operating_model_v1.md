# Linear Operating Model v1

Status: Active canonical model  
Owner: Product Development  
Primary planning lane: [BIT-175 — Linear operating model v1 rollout plan](https://linear.app/bitpod-app/issue/BIT-175/linear-operating-model-v1-rollout-plan)  
Replanning lane: [BIT-183 — Re-plan with CJ in order to update BIT-175 post learnings](https://linear.app/bitpod-app/issue/BIT-183/re-plan-with-cj-in-order-to-update-bit-175-post-learnings)

## Purpose

Define one complete Linear operating model for BitPod Product Development:

- exact statuses and status types
- exact label groups and labels
- canonical blocker and dependency semantics
- one shared board view
- gate-driven QA and acceptance transitions
- cycle and estimate expectations
- native Linear vs BitPod/Taylor automation boundary

This document supersedes older partial workflow drafts as the active contract.

## Truth note

The original long planning paragraph that informed this lane was lost to memory compaction. This document is the truthful reconstruction from:

- surviving repo docs
- live Product Development team state
- existing Linear tickets
- the obsolete `PLAN.md`
- the current planning session with CJ

## Canonical workflow

### Status order

| Status Type | Status | Meaning |
|---|---|---|
| Backlog | `Icebox 🧊` | Very cold work that is unlikely to be done and is under delete / cancel / obsolete consideration. |
| Backlog | `Backlog` | Default landing space for new or deferred work that is real but not execution-ready. |
| Unstarted | `Ready` | Execution-ready work. Minimum required fields and gates are satisfied. |
| Started | `In Progress` | Active execution or implementation. |
| Started | `In Review` | Active QA / technical review stage. Pending QA is expressed by the status itself. |
| Started | `Delivered` | QA-cleared work waiting for product / operational acceptance. Pending acceptance is expressed by the status itself. |
| Completed | `Accepted` | Explicitly accepted outcome. Normal terminal state for acceptance-required work. |
| Completed | `Done` | Fully complete and closed. Normal terminal state for work that does not need a separate acceptance end-state. |
| Canceled | `Canceled` | Intentionally stopped and no longer pursued. |
| Canceled | `Duplicate` | Closed because the canonical work exists in another issue. |
| Canceled | `Obsolete` | Closed because the context changed and the work is no longer relevant. |
| Canceled | `Won't Do` | Explicitly understood and intentionally not implemented. |

### Workflow rules

- Default issue status is `Backlog`.
- `Triage` is not part of the Product Development team workflow.
- `Ready` is the canonical unstarted execution-ready status.
- `In Acceptance` is retired and replaced by `Delivered`.
- All canceled-family statuses remain real statuses and remain visible in the canonical board model.
- `Accepted` and `Done` both remain. They are not duplicates.
- `Accepted` does not automatically mean `Done`.

### Type to path

| Issue type | Default end-state | Acceptance required by default |
|---|---|---|
| `Type: 📄 Plan` | `Accepted` | Yes |
| `Type: 🏁 Release` | `Accepted` | Yes |
| `Type: ⭐️ Feature` | `Accepted` | Yes |
| `Type: 🎨 Design` | `Accepted` | Yes |
| `Type: 🐞 Bug` | `Done` | No, unless CJ or PM explicitly requests acceptance |
| `Type: ⚙️ Chore` | `Done` | No, unless CJ or PM explicitly requests acceptance |

Default forward paths:

- Acceptance-required work: `Backlog` -> `Ready` -> `In Progress` -> `In Review` -> `Delivered` -> `Accepted`
- Non-acceptance work: `Backlog` -> `Ready` -> `In Progress` -> `In Review` -> `Done`

## Canonical labels

Use exactly four single-select label groups with no group emojis.

### `Issue Type`

Description: `Primary work type`

- `Type: 📄 Plan` — `Planned parent rollout via subticket tasklist`
- `Type: ⭐️ Feature` — `Net-new capability or enhancement`
- `Type: 🐞 Bug` — `Broken behavior, defect, or regression fix`
- `Type: ⚙️ Chore` — `Maintenance, cleanup, upgrade, or refactor work`
- `Type: 🎨 Design` — `UX, UI, visual, or design-system work`
- `Type: 🏁 Release` — `Shipping, cutover, launch, or release-readiness work`

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

- `Blocked By` is metadata only. It is not a swimlane, gate, or workflow stage.
- Every blocker label must start with `needs-`.
- `needs-other` always requires an explanatory issue comment.
- `needs-type` and `needs-estimate` should normally be resolved before `Ready`.
- `needs-CTO` is reserved for high-reasoning technical redesign or architecture direction.
- Do not add alternate blocker spellings such as `missing-specs` or `poorly-specified`.

### `QA Gate`

Description: `Formal QA verdict used to unlock work out of In Review`

- `qa-passed` — `Real QA completed; no blocking issues`
- `qa-failed` — `Real QA found blocking issues`
- `qa-skipped` — `QA bypass explicitly approved and reason recorded`

Rules:

- There is no pending QA label.
- Pending QA is expressed only by the status `In Review`.
- `qa-passed`, `qa-failed`, and `qa-skipped` are mutually exclusive.
- A QA gate label is valid only when there is a real QA artifact or explicit skip authorization on the issue.
- If a PR exists, the same artifact or a link to it should also appear in PR comments.

### `Acceptance Gate`

Description: `Formal acceptance verdict used to unlock work out of Delivered`

- `pm-accepted` — `Real acceptance review approved`
- `pm-rejected` — `Acceptance review rejected; changes required`
- `pm-skipped` — `Acceptance bypass explicitly approved and reason recorded`

Rules:

- There is no pending PM / acceptance label.
- Pending acceptance is expressed only by the status `Delivered`.
- `pm-accepted`, `pm-rejected`, and `pm-skipped` are mutually exclusive.
- Delegated acceptance to Taylor01 or another approved agent does not change taxonomy. The gate label records the verdict. Delegation belongs in the artifact comment, delegate field, or linked evidence.

### Explicit removals

- no `QA Review` group
- no `PM Review` group
- no pending review labels such as `QA: Pending` or `PM: Waiting`
- no `Needs-CJ` label
- no extra operational noun labels outside the canonical groups

## Relations and decomposition

| Need | Canonical tool | Use it when | Do not use it for |
|---|---|---|---|
| Workflow state | Status | The issue is moving through the lifecycle | Metadata, acceptance verdict, or dependency graph |
| Generic blocker reason | `Blocked By` label | The issue is blocked by a class of reason | Specific upstream issue dependency |
| Specific prerequisite issue | `Blocked by` / `Blocks` relation | A real issue must finish first | Generic missing context like missing specs |
| Context only | `Related to` relation | The issue is connected but not gated | Sequencing or decomposition |
| Decomposition | Parent / sub-issues | One piece of work should be split into children | Generic cross-ticket dependency modeling |

Operational rules:

- If an issue is blocked by a specific other issue and the reason class is known, use both the relation and the blocker label.
- Parent/sub-issues are not substitutes for blocking relations.
- `Type: 📄 Plan` issues use parent/sub-issues first and blocking relations only when one child truly depends on another.
- Duplicates always point to the canonical issue.

## Shared board

Use one single shared team board as the default operating surface:

- view URL: <https://linear.app/bitpod-app/view/proddev-team-all-issues-or-board-e33cd891cdc5>
- scope: team/global view
- workspace rule: every Product Development member favorites it manually
- admin rule: set its display options as the default for everyone on that page

### Exact display configuration

- Layout: `Board`
- Columns: `Status`
- Rows / sub-grouping: `None`
- Ordering: `Last updated`, descending
- Secondary temporary operator sort: `Priority`
- Completed recently: `On`
- Completed issues window: `Last month`
- Show sub-issues: `On`
- Show empty columns: `Off`
- Project filter: blank by default
- Status Type filter: blank by default
- Assignee filter: blank by default
- Issue Type filter: `All`
- AI filter: blank by default

Board semantics:

- The board is defined across the full workflow from `Icebox 🧊` through all completed and canceled-family statuses.
- Because `Show empty columns` is off, empty statuses may disappear visually, but the board model still includes every canonical status.
- Canceled-family columns remain part of the canonical board instead of being hidden behind a different default view.
- This is the single shared surface that everyone should look at first.

## Workflow gates and automations

### Entry gates

Before an issue can move to `Ready`, it must have:

- exactly one canonical `Issue Type` label
- a valid estimate, except for parent `Type: 📄 Plan` issues
- a minimally valid issue description using the canonical template
- no unresolved `needs-type` or `needs-estimate` blocker

Before an issue can move to `In Progress`, it must already satisfy the `Ready` requirements.

Plan-parent rules:

- `Type: 📄 Plan` issues are coordination containers, not velocity units.
- Plan parents normally do not carry cycle points.
- Child issues carry estimates, cycle commitments, and execution movement.
- Enable parent auto-close so the plan closes when its child work is complete.

### Review and acceptance transitions

| Current status | Gate / event | Required evidence | Next status |
|---|---|---|---|
| `In Progress` | ready for QA | execution evidence and work genuinely ready | `In Review` |
| `In Review` | `qa-passed` | real QA artifact | `Delivered` if acceptance-required, otherwise `Done` |
| `In Review` | `qa-failed` | real QA artifact | `In Progress` |
| `In Review` | `qa-skipped` | explicit skip authorization and reason | `Delivered` if acceptance-required, otherwise `Done` |
| `Delivered` | `pm-accepted` | real acceptance artifact | `Accepted` |
| `Delivered` | `pm-rejected` | real acceptance artifact | `In Progress` |
| `Delivered` | `pm-skipped` | explicit skip authorization and reason | `Done` |

Additional rules:

- `qa-failed` must mention the current assignee and point directly to the QA artifact.
- `pm-rejected` must point directly to the rejection artifact and return the issue to `In Progress`.
- Re-entering `In Review` clears stale prior `QA Gate` labels.
- Re-entering `Delivered` clears stale prior `Acceptance Gate` labels.
- Merge or rollout completion must not silently substitute for missing QA or acceptance evidence.

### Aging

- `Backlog` untouched for 30 days -> move to `Icebox 🧊` and add an automatic comment.
- `Icebox 🧊` untouched for 60 days -> move to `Obsolete` and add an automatic comment.
- Do not auto-obsolete `In Progress`, `In Review`, or `Delivered`.
- Auto-archive all closed statuses after 1 month.
- Enable parent auto-close and sub-issue auto-close in the workflow settings.

### Native Linear vs BitPod/Taylor layer

| Capability | Native Linear | BitPod / Taylor layer |
|---|---|---|
| Status ordering, default status, auto-archive, parent/sub-issue automation, cycles, board defaults | Yes | No |
| Backlog -> Icebox comment workflow, Icebox -> Obsolete comment workflow | Partial | Yes |
| Required type/estimate/template before `Ready` or `In Progress` | Not verified natively | Yes |
| QA or acceptance artifact validation before gate labels | No | Yes |
| Gate-driven status transitions | Partial | Yes |
| `Update Linear` fail-closed mutation enforcement | No | Yes |
| Skip authorization for QA or acceptance | No | Yes |
| Delegated acceptance to Taylor01 | No | Yes |
| GitHub PR signal consumption | Native integration exists | BitPod/Taylor wrapper is the truth-enforcing layer |

## Template, estimate, cycle, and integration policy

### Canonical issue template

All execution issues use:

- Objective
- Scope
- Required outputs
- Verification plan
- Rollback note
- Acceptance / closure criteria
- Taylor01 Portability Check when relevant

`Done` or `Accepted` claims must include:

- status line and transition reason
- commands / UI checks
- artifacts
- pass / fail
- risk / follow-up
- portability block when relevant

### Specialized templates

Plan issue template:

- requires a real planning session first
- includes goal, ordered child plan, dependencies, exit criteria, and invalidation conditions

Release issue template:

- includes cutover steps, rollback, acceptance criteria, verification artifact lane, and post-release checks

### Estimates

- enable estimates
- use Fibonacci values `1, 2, 3, 5, 8, 13`
- keep `0` disabled by default
- split issues larger than `13` before `Ready`
- do not treat unestimated issues as acceptable active work
- plan parents are exempt only when executable child issues carry the estimates

### Cycles

- cadence: `1 week`
- start day: `Monday`
- cooldown: `0 days`
- upcoming cycles visible: `2`
- cycle scope should reflect execution work, not parent plan containers
- plan parents normally stay out of cycles
- child execution issues carry cycle commitments and points

### Integrations

- GitHub: connected and authoritative for branch / PR context only, not for bypassing workflow truth
- Slack: optional for notifications and synced discussion, not for canonical workflow truth
- Google Sheets: optional after cycle and estimate hygiene is stable, for KPI and velocity analysis
- Triage Intelligence / AI suggestions: assistive only; never authoritative for status or gate truth
- additional integrations remain off by default until explicitly approved

## `Update Linear`

`Update Linear` is the required mutation contract for agent-driven Linear changes. Its job is to make the issue materially more truthful and fail closed when required truth-maintenance steps are missing.

Required behavior:

- validate status, labels, assignee/delegate, and relation hygiene together
- refuse status moves that skip required evidence or required fields
- enforce type and estimate requirements before `Ready` and `In Progress`
- enforce gate artifacts before `qa-*` and `pm-*` labels
- enforce the `needs-other` comment requirement
- never silently apply partial truth updates
- leave an explicit correction comment when a mutation is rejected

Primary implementation lanes:

- [BIT-186 — Investigate and fix broken Update Linear enforcement path](https://linear.app/bitpod-app/issue/BIT-186/investigate-and-fix-broken-update-linear-enforcement-path)
- [BIT-125 — Define and enable a safe Linear mutation executor for scheduled automations](https://linear.app/bitpod-app/issue/BIT-125/define-and-enable-a-safe-linear-mutation-executor-for-scheduled)
- [BIT-130 — Implement Linear bot rules spec with soft-gating under interim QA/CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-130/implement-linear-bot-rules-spec-with-soft-gating-under-interim-qacj)
- [BIT-121 — Mature QA/PM acceptance workflow and automation](https://linear.app/bitpod-app/issue/BIT-121/mature-qapm-acceptance-workflow-and-automation)

## Implementation notes

- Replace the description of [BIT-175 — Linear operating model v1 rollout plan](https://linear.app/bitpod-app/issue/BIT-175/linear-operating-model-v1-rollout-plan) with this operating model.
- Use [BIT-183 — Re-plan with CJ in order to update BIT-175 post learnings](https://linear.app/bitpod-app/issue/BIT-183/re-plan-with-cj-in-order-to-update-bit-175-post-learnings) to close the replanning lane once the planning evidence and related follow-ups are truthfully complete.
- Migrate live Product Development workflow and labels to match this file.
- Preserve older docs such as the workflow reconfig spec and custom config draft as historical references, not as the active contract.
