# Linear Issue Type Decision Guide v1

Status: Active
Owner: Product Development
Applies to: BitPod Product Development Linear issues

## Purpose

Provide the canonical operational guide for assigning exactly one Linear `Issue Type` label.

This guide is now machine-readable-first. The operative classifier is `linear/contracts/linear_type_classifier_v1.json`; this Markdown explains the intent and edge cases. If prose and JSON disagree, update both in the same PR and treat the JSON classifier as the automation source.

Use this guide when creating, triaging, normalizing, or hygiene-auditing Linear issues. The goal is consistent evidence-based classification, not a redesigned taxonomy.

## Required machine intake

Every issue moving to `Ready` should include this compact intake block:

```md
Linear Classification:
- Output: code | docs/process | design artifact | design approval | release coordination | plan container
- Behavior change: yes | no
- Broken existing behavior: yes | no
- Evidence: short link/text
- Children expected: yes | no
- PM-testable: yes | no
```

The bot and hygiene automation should classify from this block first. Humans and agents should only reason deeply when the block is missing, invalid, contradictory, or low-confidence.

## Default rule

Assign type from the machine intake and issue evidence, not from title alone.

Evidence may include:

- stated objective and acceptance criteria
- reproduction steps, observed behavior, logs, screenshots, or failing checks
- linked PRs, commits, designs, specs, release notes, or Figma/design assets
- issue relationships and whether the issue is a parent/container
- current scope, owner, due date, rollout, and checklist

If evidence is insufficient, do not guess. Keep or add the appropriate readiness blocker such as `needs-type` and comment with the missing evidence needed to classify.

## Deterministic decision order

The machine classifier uses this order:

1. `Broken existing behavior: yes` plus evidence -> `Bug`.
2. `Output: design artifact` or `design approval` -> `Design`.
3. `Output: release coordination` -> `Release`.
4. `Output: plan container` plus `Children expected: yes` -> `Plan`.
5. `Behavior change: yes` -> `Feature`.
6. Otherwise -> `Chore`.
7. If the intake is missing or contradictory, mark `needs-type` instead of guessing.

## Type rules

### `Bug`

Use when evidence shows existing expected behavior is broken.

Typical evidence:

- reproducible failure or regression
- failing check, error log, exception, broken workflow, or incorrect output
- user-reported defect with observed/expected behavior
- fix restores intended behavior without materially expanding scope

If it did not work and there is evidence, use `Bug` even when the implementation fix is refactoring, hardening, or cleanup.

Do not use `Bug` only because the title says "fix". A cleanup, refactor, or missing feature can also use that wording.

### `Feature`

Use when the issue adds a meaningful capability or improvement for users, operators, or the team.

Typical evidence:

- new behavior, command, workflow, integration, API, UI capability, or team-facing automation
- upgrade to an existing capability that adds functionality that did not exist before and creates real value for people or agents
- acceptance criteria describe additive value rather than only restoring broken behavior
- implementation changes product or operating capability in a visible way

If the work is mostly repo/process upkeep with no meaningful new capability, prefer `Chore`.

### `Chore`

Use for maintenance or operational upkeep that is necessary but not primarily a user/team-facing enhancement.

Typical evidence:

- dependency upgrades, cleanup, refactors, migrations, or repository hygiene
- docs/process maintenance that keeps existing operations accurate
- test/build/tooling upkeep without a new workflow capability
- audit follow-up that normalizes existing state

Docs and process work are normally `Chore`, not `Plan`, unless the issue is explicitly a parent planning container with real sub-issues.

If the work creates a substantial new reusable workflow or capability, or upgrades an existing capability with new real functionality, use `Feature` instead.

### `Design`

Use narrowly. `Design` means actual GUI, graphic, UI/UX, visual branding, or design-system work.

Typical evidence:

- linked Figma or design asset
- wireframes, mocks, visual design specifications, brand assets, or design-system components
- acceptance criteria owned by UI/UX or design review
- work output is a design artifact, not merely a documentation or planning artifact

Use `Design` when the ticket output is the design itself or design approval.

If a ticket requires both serious design output and implementation, split it:

- the design ticket is `Design`
- the implementation ticket is usually `Feature`
- the implementation ticket should be blocked by the design ticket

Do not use `Design` for generic product thinking, information architecture in prose, process docs, or issues that mention UI only as implementation context.

Word-only UI tickets are usually not `Design`. They are usually `Feature` when they add meaningful UX/functionality, or `Chore` when they are minor visual upkeep without meaningful UX/functionality, such as a tiny color or spacing adjustment.

### `Plan`

Use when the issue is a parent planning ticket that structures multiple real sub-issues toward one precise goal. A `Plan` is closest to a mini-project or epic.

Typical evidence:

- the issue intentionally owns real sub-issues, not merely a checklist
- each sub-issue is expected to behave like a normal ticket, with its own type, PR and QA/PM route where applicable
- the issue captures a rollout or planned sequence that was actually planned beforehand
- scope needs decomposition before implementation
- acceptance criteria are about maintaining the plan, rollout shape, or child-ticket set
- parent issue is not the normal velocity unit

Do not use `Plan` as a checklist type. If work items are not real sub-issues, split them or do not call the parent a `Plan`.

Do not use `Plan` for every vague or large ticket. Vague tickets should be blocked by `needs-specs` and usually moved to `Icebox 🧊` until they become specific enough.

### `Release`

Use rarely. `Release` is a coordinated shipping object, not a synonym for "done soon".

Typical evidence:

- real release scope and target date or shipping window
- version bump, release notes, announcement, rollout, or post-release checklist
- grouped verification across multiple completed items
- explicit release owner or release coordination responsibility

Do not use `Release` for ordinary implementation, PR merge, deployment task, or milestone-like grouping without actual release mechanics.

Current operating note: `Release` tickets are not in regular use yet. Until the operating model changes, classify cautiously and prefer `Plan` unless the release mechanics above are explicit.

Like `Plan`, a `Release` is a coordinating container. The real sub-issues under it still need their own issue types and normal routing.

## Common tie-breakers

| Ambiguous case | Use this rule |
|---|---|
| Feature vs Chore | New or upgraded functionality with real value to people/agents is `Feature`; upkeep, cleanup, refactor, docs/process maintenance, or normalization is `Chore`. |
| Bug vs Chore | If expected behavior did not work and there is evidence, use `Bug`; otherwise maintenance/hardening is usually `Chore`. |
| Plan vs Chore | A parent with real sub-issues toward a precise goal is `Plan`; docs/process planning or cleanup without real subtickets is usually `Chore`. |
| Design vs Feature | Design artifact or design approval is `Design`; implemented product/UI behavior is usually `Feature`. If both are required, split the tickets. |
| Release vs Plan | Real shipping scope/date/checklist/version impact is `Release`; coordinated multi-ticket work without release mechanics is `Plan`. |
| Audit follow-up | Usually `Chore`; use `Bug` if the audit found broken expected behavior, or `Feature` if the follow-up adds real new functionality. |

## Learning loop

The hygiene audit can mutate issue type/routing and report back to CJ. If CJ corrects the logic, the correction must become durable:

1. append one short entry to `linear/docs/process/linear_type_classifier_corrections_v1.md`
2. update `linear/contracts/linear_type_classifier_v1.json` or add/update a classifier test fixture
3. include the learned rule in the next hygiene audit report

This is how the automation learns without hidden memory or long prompt reasoning.

## Routing note

Issue type is not the same as QA/PM routing.

Known routing direction:

- Highly technical chores with no product behavior change may skip PM gating when QA evidence is sufficient.
- Design tickets normally skip QA and go to PM/design acceptance.
- Tiny bugs may skip PM gating when QA evidence is sufficient and the impact is narrow.
- Plans and Releases are coordinating containers, not normal implementation tickets; their sub-issues carry the real type and QA/PM route.

Routing defaults are advisory in this PR. Detailed routing enforcement belongs in the QA/PM acceptance and Linear automation flow before automation sets or validates QA/PM labels from these defaults.

## Ambiguity rules

- Do not infer type from title alone.
- Do not retroactively reclassify ambiguous historical issues without evidence.
- Do not guess estimates while setting type.
- Preserve existing type when evidence supports it, even if a different type could also be plausible.
- When two types seem plausible, classify by the primary acceptance criteria and output.
- When evidence is missing, use `needs-type` and state the exact missing evidence.

## Hygiene audit checklist

For each issue checked:

- Exactly one canonical issue type is present.
- The type is supported by issue evidence.
- `Design` is only used for actual UI/UX/graphic/visual/design-system work.
- `Release` is only used for real coordinated shipping objects.
- Missing or ambiguous type evidence is marked with `needs-type` rather than guessed.
