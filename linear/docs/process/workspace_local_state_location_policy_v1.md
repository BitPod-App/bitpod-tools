# Workspace Local State Location Policy v1

## Status

- Owner: Codex / Product Development
- Source of truth class: working decision
- Scope: local operational state, automation journals, retained runtime metadata

## Decision

Primary Codex machine-local state that must persist outside repo source trees should live in a machine-local home outside the umbrella root:

- default: `~/.codex/`
- or an explicit machine-local `CODEX_HOME` outside `/Users/cjarguello/BitPod-App`

The umbrella-root `.codex/` path is reserved only for checked-in workspace compatibility metadata and narrow project-scoped overrides.

Machine-local Codex state includes:

- automation journals
- retained run notes
- local runtime state
- local operational metadata
- similar hidden support files that should not live in repo roots

## Why This Location

- machine-local app state should stay machine-local rather than project-root-local
- avoids mixing project canon with mutable app state, auth, and session history
- supports separate personal-machine and HQ guest Codex homes without shared state
- keeps checked-in workspace metadata separate from machine-maintained state

## Policy Boundary

No long-lived Codex operational state should be silently shared across machines or pushed into random scratch paths.

Disallowed examples:

- a project-root `.codex/` used as the primary machine-state home
- one shared Codex home used by both the personal machine and HQ guest
- arbitrary home-directory scratch locations
- repo-external temp paths used as long-lived state

Allowed roots:

- machine-local `~/.codex/` or explicit machine-local `CODEX_HOME`
- `/Users/cjarguello/BitPod-App/.codex/` only for checked-in compatibility metadata and narrow project-scoped overrides
- migration-era dated backup workspace roots when explicitly preserved

## Repo vs Local State Split

### Repo-tracked

Keep in repo only when the output is:

- intended as institutional knowledge
- part of a runbook or policy
- required as durable evidence
- reviewed and suitable for source control

### Local workspace state

Keep in machine-local Codex home when the output is:

- operational
- machine-maintained
- user-local
- high-churn
- not worth source control

## Migration Rule

If an existing tool still assumes project-root `.codex/` is the primary state home:

1. treat it as out of policy
2. migrate it to machine-local state or narrow checked-in override usage
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
