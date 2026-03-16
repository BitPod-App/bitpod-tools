# Linear Temporal Layout Spec v1

Status: staging decision record

## Purpose

Define a clear filesystem layout for `bitpod-tools/linear` so active canonical process docs are separated from temporary evidence and project-bound operational residue.

This spec exists because the current `bitpod-tools/linear/docs/process/` directory mixes:

- active canonical operating docs
- temporary migration evidence
- dated checkpoints and proofs
- backup and rollback residue

The new layout separates those concerns by lifecycle instead of relying on filename guesses.

## Canonical Layout

Target structure under `bitpod-tools/linear`:

```text
linear/
  protocol/
    templates/
    configs/
    agent-references/
    ...
  temporal/
    active/
      ticket__<ticket_id>/
      project__<project_slug_id>/
    closed/
      ticket__<ticket_id>/
      project__<project_slug_id>/
    purge/
      ticket__<ticket_id>/
      project__<project_slug_id>/
      purge_ledger.md
```

## Directory Semantics

### `protocol/`

Contains active canonical docs only.

Allowed examples:

- operating guides
- admin/process change-control rules
- reusable templates
- stable configuration specs
- stable agent/process contracts
- durable reference docs still governing current behavior

Not allowed:

- dated evidence snapshots
- backup inventories
- one-off migration proofs
- closed-project status records
- temporary rollback artifacts

### `protocol/templates/`

Reusable canonical templates.

Examples:

- change proposal templates
- issue evidence templates
- handoff templates that are still active canon

### `protocol/configs/`

Stable configuration and workflow specs.

Examples:

- workflow reconfiguration specs
- status/config mapping docs
- deeplink/reference format policies

### `protocol/agent-references/`

Stable agent/process reference docs that still govern current behavior.

Examples:

- QA authority model
- orchestrator contract
- specialist registry

### `temporal/active/`

Active temporal buckets. Each bucket is named explicitly as either `ticket__<ticket_id>` or `project__<project_slug_id>`.

Examples:

- fresh evidence notes
- dated ticket snapshots
- temporary proofs
- rollback notes
- small ticket-scoped migration artifacts

### `temporal/active/project__<project_slug_id>/`

Temporary files tied to an active Linear project.

This is the default destination for temporary project-scoped material that is still operationally relevant but not canonical.

### `temporal/closed/`

Closed temporal buckets. Each bucket is named explicitly as either `ticket__<ticket_id>` or `project__<project_slug_id>`.

### `temporal/closed/project__<project_slug_id>/`

Retained temporary material for closed or deleted projects.

This is the retention stage before purge.

### `temporal/purge/`

Final pre-disposal queue.

This path keeps grouped folders plus a running purge ledger for auditability.

Chosen rule:

- keep project/ticket folders in `purge/`
- also maintain `purge_ledger.md`

Reason:

- folder structure preserves context during final review
- ledger provides one compact audit surface
- final disposal can still be manual and explicit

## Slug Rule

Project folders must use:

`<project_slug_10_chars>__<real_project_id>`

Example pattern:

`bootstrap__0727b3f56ccd`

Rules:

- slug portion should be human-readable and capped at about 10 characters
- ID portion must be the real stable Linear project ID
- if the name changes, keep the same folder unless a manual normalization pass is approved

Projectless ticket material uses:

- `temporal/active/`
- `temporal/closed/`
- `temporal/purge/`

## Lifecycle Rules

### Intake

New temporary material must start in one of:

- `temporal/active/`
- `temporal/active/project__<project_slug_id>/`

It must not be written into `protocol/`.

### Projectless ticket reassignment

If a projectless ticket later becomes part of a project:

- move its files from `temporal/active/` to `temporal/active/project__<project_slug_id>/`
- preserve filenames
- do not duplicate files across both locations

If a closed projectless ticket is later attached to a project before purge:

- move its files from `temporal/closed/` to the appropriate project folder in `temporal/active/project__<project_slug_id>/` or `temporal/closed/project__<project_slug_id>/` depending on current project status

### Active to closed

Move temporary material from `temporal/active/...` to `temporal/closed/...` when:

- the related Linear project has been completed for 15 days, or
- the related Linear project has been deleted for 15 days, or
- for projectless ticket material, the related ticket has been closed or deleted for 15 days

### Closed retention

Retain material in `temporal/closed/...` for 60 days.

After 60 days:

- move it to `temporal/purge/...`
- append an entry to `temporal/purge/purge_ledger.md`

### Purge execution

Material in `temporal/purge/...` is not auto-deleted immediately.

During T3 cleanup, a manual script or periodic job may move purge-ready contents into:

`/Users/cjarguello/BitPod-App/local-workspace/local-trash-delete/local-purge`

Deletion remains explicit and separate from classification.


## High-Value Temporal Plans

Not all temporal material should end in purge.

Documents whose primary role is planning or scoping a major change campaign should remain temporal, but should be treated as archive-worthy rather than purge-first when they age out of active use.

Examples:

- plans
- normalization plans
- strategy notes
- change maps
- closure matrices
- major rescope records

Rule:

- keep these documents in `temporal/active/...` or `temporal/closed/...` while the related work is active or recently closed
- do not elevate them into `protocol/` unless they become standing governance
- when no longer active, review them for archive promotion instead of sending them directly to purge
- likely long-term archive destination: `bitpod-docs/archive/legacy-context/linear/`

This rule exists because these documents often preserve high-value rollback and historical context even though they are not canonical operating policy.

## Classification Rules

### Keep in `protocol/`

Only if the file:

- governs current behavior
- is reusable beyond one ticket or one dated event
- is still the active source of truth

### Keep in `temporal/*`

If the file is:

- dated
- ticket/project-scoped
- evidence of a change or claim
- rollback support material
- migration or cleanup residue still worth retaining temporarily

### Not allowed in `protocol/`

Examples:

- `backup_*`
- `*_evidence_*`
- `*_status_*`
- `*_snapshot_*`
- `active_checkpoint_*`

## Codex Prompts

These prompts are the operational layer for this spec. They are intended to be copied into Codex when performing classification, migration, or cleanup work.

### Prompt: classify existing files

```text
Classify the files under `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/` according to `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/configs/linear-temporal-layout-spec-v1.md`.

For each file, output:
- current path
- target classification: `protocol`, `temporal/active/tickets`, `temporal/active/<project_slug_id>`, `temporal/closed/tickets`, `temporal/closed/<project_slug_id>`, `temporal/purge`, or `discard-review`
- reason in one sentence
- whether the file appears canonical, transitional, historical, or residue

Do not move files yet. Produce a migration table only.
```

### Prompt: migrate canonical files

```text
Using `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/configs/linear-temporal-layout-spec-v1.md` as the source of truth, move the canonical files from `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/` into `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/`.

Rules:
- move templates into `protocol/templates/`
- move stable workflow/config/policy specs into `protocol/configs/`
- move stable agent/process contracts and reference docs into `protocol/agent-references/`
- leave non-canonical dated material unmoved
- after moves, generate a short index of what moved and why
- identify any broken references introduced by the moves
```

### Prompt: migrate temporal files

```text
Using `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/configs/linear-temporal-layout-spec-v1.md` as the source of truth, move non-canonical files from `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/` into the appropriate `temporal/` path.

Rules:
- if a file is tied to an active Linear project, move it to `temporal/active/project__<project_slug_id>/`
- if a file is tied to projectless ticket work, move it to `temporal/active/`
- if a file is tied to a project or ticket already closed/deleted long enough per spec, move it to the corresponding `temporal/closed/...` path
- if a file is already beyond retention and clearly purge-ready, move it to `temporal/purge/...` and add an entry to `purge_ledger.md`
- preserve filenames unless collision handling is required
- report ambiguous files separately instead of guessing
```

### Prompt: reconcile projectless ticket material

```text
Audit `temporal/active/` and `temporal/closed/` for files that now belong to a Linear project.

For any file whose related ticket has since been attached to a project:
- determine the stable project folder using `<project_slug_10_chars>__<real_project_id>`
- move the file into the correct project folder
- do not duplicate the file in both ticket and project paths
- produce a ledger of reassigned files
```

### Prompt: enforce lifecycle transitions

```text
Audit the contents of `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/` against `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/configs/linear-temporal-layout-spec-v1.md`.

Tasks:
- move active project/ticket material to `closed/` if the related project or ticket has been closed/deleted for at least 15 days
- move closed material to `purge/` if it has been retained for at least 60 days
- append each purge movement to `temporal/purge/purge_ledger.md`
- output a concise action report with moved items, skipped items, and ambiguities
```

### Prompt: clarify folder ownership

```text
Create or update folder-level README files under `/Users/cjarguello/BitPod-App/bitpod-tools/linear/` so the new structure is self-explanatory.

Required coverage:
- `protocol/` explains what canonical material belongs there and what does not
- each `protocol/*` subfolder explains its scope
- `temporal/` explains lifecycle-based storage rules
- `temporal/active/`, `temporal/closed/`, and `temporal/purge/` explain transition rules and retention windows

Do not restate the entire spec. Each README should be short and point back to the spec when needed.
```

### Prompt: validate references after migration

```text
After migrating files out of `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/`, scan the workspace for stale references to the old paths.

Check at minimum:
- `/Users/cjarguello/BitPod-App/bitpod-tools/`
- `/Users/cjarguello/BitPod-App/bitpod-docs/`
- `/Users/cjarguello/BitPod-App/local-workspace/local-working-files/`

For each stale reference found:
- report file path
- report old reference
- suggest the correct new path

Do not rewrite references automatically unless explicitly asked.
```

## File Naming Standard

Use separate naming rules for:

- protocol documents
- temporal document files
- temporal project and ticket folders

### Folder naming for temporal material

Use stable ID-based folders plus a capture date so retained ticket/project history can preserve rollback states across scope changes.

#### Project folders

Project folders under `temporal/active/`, `temporal/closed/`, and `temporal/purge/` should use:

`project__<shortname_10_chars>__<project_id>`

Example:

- `bootstrap__0727b3f56ccd__2026-03-12`

Rules:

- shortname should be human-readable and capped at about 10 characters
- project ID must be the real stable Linear project ID
- capture date should use `yyyy-mm-dd`
- if the project name changes, keep the existing folder unless a manual normalization pass is approved
- create a new capture-dated folder only when preserving a meaningfully new retained state, not for trivial edits

#### Ticket folders

Projectless ticket material should use explicit per-ticket folders directly under the lifecycle stage:

`ticket__<ticket_id>`

Examples:

- `BIT-127__2026-03-16`
- `BIT-212__2026-03-20`

Rules:

- do not store multiple unrelated ticket artifacts flat at the lifecycle-stage root
- each projectless ticket preservation set gets its own folder
- ticket title changes do not require folder renames
- if a ticket later becomes attached to a project, move its folder into the correct project area and preserve the existing capture date unless a manual consolidation pass is approved

Resulting paths look like:

```text
linear/
  temporal/
    active/
      ticket__BIT-127/
      project__bootstrap__0727b3f56ccd/
    closed/
      ticket__BIT-212/
    purge/
      ticket__BIT-044/
```

### Canonical protocol file naming

Canonical files under `protocol/` should use:

`<scope>-<subject>-<doc-type>-v<major>.md`

Examples:

- `linear-change-control-policy-v1.md`
- `linear-change-proposal-template-v1.md`
- `qa-authority-model-reference-v1.md`
- `taylor-orchestrator-contract-v1.md`
- `workspace-local-state-policy-v1.md`

Recommended doc types:

- `policy`
- `spec`
- `guide`
- `runbook`
- `template`
- `contract`
- `reference`
- `model`
- `registry`

### Temporal file naming

Files inside ticket/project temporal folders should use:

`<scope>-<subject>-<artifact-type>-<yyyy-mm-dd>.md`

Examples:

- `closure-gates-checkpoint-2026-03-12.md`
- `acceptance-status-2026-03-12.md`
- `org-baseline-evidence-2026-03-09.md`
- `workspace-rebuild-checkpoint-2026-03-16.md`

Recommended temporal artifact types:

- `evidence`
- `checkpoint`
- `status`
- `snapshot`
- `inventory`
- `audit`
- `proof`
- `checklist`
- `ledger`
- `handoff`

### Versioning rule

- canonical docs use semantic major versions in filename, for example `v1`, `v2`, `v3`
- temporal docs do not use semantic versions unless multiple documents with the same scope, subject, artifact type, and date are unavoidable
- if multiple same-day temporal variants are unavoidable, append a short suffix such as `-a`, `-b`, or a precise time

### Rename guidance

When migrating old files into the new layout:

- create stable ticket/project folders first
- move files into those folders before doing deeper filename cleanup
- rename files into the normalized scheme as part of the move when the target meaning is clear
- if the target meaning is ambiguous, move first and rename in a follow-up pass
- do not preserve misleading prefixes like `backup_` unless the file is truly a backup inventory or rollback artifact
- do not create duplicate canonical docs just to preserve old names; preserve history in git and in temporal storage instead

## Codex Prompt: normalize filenames

```text
Normalize folder and file names under `/Users/cjarguello/BitPod-App/bitpod-tools/linear/` according to the naming rules in `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/configs/linear-temporal-layout-spec-v1.md`.

Rules:
- canonical files in `protocol/` must use `<scope>-<subject>-<doc-type>-v<major>.md`
- project folders in `temporal/*/` must use `project__<shortname_10_chars>__<project_id>`
- projectless ticket folders in `temporal/*/` must use `ticket__<ticket_id>`
- temporal files inside those folders must use `<scope>-<subject>-<artifact-type>-<yyyy-mm-dd>.md`
- keep document meaning intact
- do not rename files whose meaning is still ambiguous; report them instead
- generate a before/after rename ledger
- identify references that will need updating after renames
```
