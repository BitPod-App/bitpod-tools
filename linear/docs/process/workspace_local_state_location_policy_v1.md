# Workspace Local State Location Policy v1

## Status

- Owner: Codex / Product Development
- Source of truth class: working decision
- Scope: local operational state, automation journals, retained runtime metadata

## Decision

Local BitPod/Codex operational state that must persist outside repo source trees should live under:

- `/Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex/`

This is the default workspace-safe destination for:

- automation journals
- retained run notes
- local runtime state
- local operational metadata
- similar hidden support files that should not live in repo roots

## Why This Location

- hidden path is appropriate for operator/runtime metadata
- remains inside the approved BitPod workspace root
- avoids polluting repository source trees
- supports later backup, audit, and cleanup as one subtree

## Policy Boundary

No local operational state should be written outside approved workspace roots.

Disallowed examples:

- `~/.codex/...`
- arbitrary home-directory scratch locations
- repo-external temp paths used as long-lived state

Allowed roots:

- `/Users/cjarguello/bitpod-app`
- migration-era dated backup workspace roots when explicitly preserved

## Repo vs Local State Split

### Repo-tracked

Keep in repo only when the output is:

- intended as institutional knowledge
- part of a runbook or policy
- required as durable evidence
- reviewed and suitable for source control

### Local workspace state

Keep under `local-workspace/local-codex/.codex/` when the output is:

- operational
- machine-maintained
- user-local
- high-churn
- not worth source control

## Migration Rule

If an existing tool writes outside allowed roots:

1. treat it as out of policy
2. migrate or hard-fail the writer
3. document any temporary compatibility exceptions explicitly

Do not silently permit legacy out-of-root writes.

## Clutter Rule

The goal is not to preserve everything.

Persist only state with clear operational value.

For low-value transient files:

- keep them ephemeral, or
- route them to a clearly disposable local subtree

## Relationship To Artifact Naming

This policy decides **where** local state may live.

The companion policy `global_artifact_naming_policy_v1.md` decides **how** persisted artifacts should be named when they are intentionally retained.

