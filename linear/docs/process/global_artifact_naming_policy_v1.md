# Global Artifact Naming Policy v1

## Status

- Owner: Codex / Product Development
- Source of truth class: working policy
- Scope: BitPod workspace and repo-tracked operational artifacts

## Purpose

Define one global policy for naming persisted artifacts so that:

- historically useful outputs remain traceable
- canonical paths remain stable
- low-value clutter does not accumulate by default
- artifact writers do not invent their own naming rules ad hoc

## Core Rule

Apply this policy only to files that are:

1. generated repeatedly under known conditions, and
2. intentionally retained for historical or operational reference

Do not apply the policy blindly to every generated file.

## Artifact Classes

### `TRACKABLE_HISTORICAL`

Use for outputs that should remain available as a dated or contextual record.

Allowed examples:

- run summaries
- migration evidence packs
- QA reports
- remediation reports
- retrospective outputs

Preferred format:

- `<base>_<context>_<YYYY-MM-DD>.md`
- `<base>_<context>_<YYYY-MM-DD>.json`
- `<base>_<context>_<YYYY-MM>.jsonl`

Context should be short, deterministic, and meaningful.

Allowed context types:

- issue id
- PR number
- branch slug
- run id
- narrow execution context

### `CANONICAL_STABLE`

Use for files whose path is part of a contract, permalink, stable pointer, or agreed canonical surface.

Examples:

- stable pointer docs
- contract-bound filenames
- permalink endpoints
- repo entrypoint docs

Rule:

- do not append dates
- do not append context suffixes
- do not rename without explicit migration design and approval

### `UNIQUE_ID_ALREADY`

Use when the filename already carries a true intrinsic unique identifier.

Examples:

- artifact files keyed by episode id
- feed outputs keyed by immutable content id

Rule:

- keep the intrinsic identifier
- do not append extra context unless there is a clear collision risk

### `EPHEMERAL`

Use for temporary outputs that are only needed for immediate execution.

Examples:

- scratch exports
- temporary diagnostics
- one-off local probes

Rule:

- do not persist in repo by default
- route to approved local workspace locations only

## Required Exclusions

This policy does **not** override:

- canonical paths
- stable pointers
- permalinks
- contract-required filenames
- paths where renaming breaks links or downstream expectations

## Retention Rule

Persist only artifacts with clear historical or operational value.

If an output is not clearly worth retaining:

- do not save it in repo
- keep it local and ephemeral, or
- escalate for explicit retention decision

## Approved Naming Patterns

### Dated markdown reports

- `legacy_identity_sweep_remediation_2026-03-09.md`
- `github_org_baseline_evidence_2026-03-09.md`

### Monthly queues / rolling ledgers

- `retro_flag_queue_2026-03.jsonl`

### Context + date artifacts

- `artifact_feed-policy_2026-03-10.md`
- `artifact_pr-28_2026-03-10.md`

## Hard No Rules

- No blanket renaming of all generated files
- No renaming of canonical or contract-bound filenames without explicit migration design
- No persistence of low-value clutter by default
- No artifact persistence outside approved workspace roots

## Implementation Guidance

Artifact writers should choose one class before writing:

1. `TRACKABLE_HISTORICAL`
2. `CANONICAL_STABLE`
3. `UNIQUE_ID_ALREADY`
4. `EPHEMERAL`

If class selection is unclear, default to fail-closed:

- do not create a new naming pattern
- do not persist broadly
- escalate the ambiguity into process/docs first

## Current Workspace Boundary

Artifact persistence is only allowed inside approved workspace roots.

Current approved roots:

- `/Users/cjarguello/BitPod-App`
- dated backup workspace roots created during migration

Anything outside those roots is out of policy.

## Related Policy

See also:

- `workspace_local_state_location_policy_v1.md`

