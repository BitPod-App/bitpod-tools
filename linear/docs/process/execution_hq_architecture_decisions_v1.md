# Execution HQ Architecture Decisions and Boundary Guardrails v1

Date: 2026-03-22
Primary issue: [BIT-105 — Execution HQ architecture decisions and boundary guardrails](https://linear.app/bitpod-app/issue/BIT-105/execution-hq-architecture-decisions-and-boundary-guardrails)

## Purpose

Make the Mac Mini Execution HQ operating assumptions explicit enough that the
semi-initial bootstrap can proceed without guessing.

This note locks the account split, path strategy, remote-control tooling,
secret-flow boundary, shared-storage guardrails, and VM trigger for the current
bootstrap phase.

Use `execution_hq_operator_pack_v1.md` for the practical step order.

## Decision Record - Account and Path Strategy

### Decision

- Keep the existing `cjarguello` macOS account on the Mac Mini for
  admin/maintenance only.
- Create a dedicated execution account now for AI HQ runtime work.
- Default execution-account name: `taylorhq`.
- Accept `taylor01` only if that username is already chosen on the Mac Mini and
  there is a concrete reason not to use `taylorhq`.
- Rebuild the Execution HQ workspace under the execution account only.
- Prefer username-agnostic path usage in commands, scripts, and docs:
  - use `$HOME` instead of hard-coding `/Users/cjarguello`
  - use `$WORKSPACE` for the working-tree root
- Default workspace root for the execution account:
  - `export WORKSPACE="${WORKSPACE:-$HOME/bitpod-app}"`
- Continue treating GitHub as the canonical source used to rebuild the Mac Mini
  workspace.

### Rationale

- A dedicated execution account creates a real operational boundary now instead
  of deferring the most important identity split until later.
- Keeping `cjarguello` limited to maintenance avoids mixing day-to-day runtime
  state with admin recovery state.
- Username-agnostic pathing keeps the execution model portable if the machine,
  username, or host identity changes later.

### Guardrails

- New live operator docs should assume the execution account is the shell where
  runtime work happens.
- Hard-coded `/Users/cjarguello/...` paths are allowed only when recording a
  current-machine fact tied specifically to the maintenance account.
- The MacBook remains the control console; it does not become the primary
  runtime or workspace owner.

## Required Tooling - MacBook Control Console

The MacBook control console must have the following tools available:

1. Terminal or iTerm2
2. `ssh`
3. `git`
4. `gh`
5. 1Password

Helpful but optional:

- `tmux`
- `scp` / `rsync`
- Tailscale

### Tooling Boundary

- Remote interaction is expected to happen primarily through shell access,
  GitHub synchronization, and intentional secret retrieval.
- macOS shared-folder mounts are not part of the required default tooling
  model.

## Secret-Flow Note - 1Password as Source of Truth

### Decision

1Password is the source of truth for secrets used by the Mac Mini execution
environment.

### Required Flow

- Secrets are authored, rotated, and reviewed in 1Password first.
- The semi-initial bootstrap may use a minimal temporary secret baseline only
  to reach:
  - workspace bootstrap
  - runtime installation
  - first HQ smoke proof
- Secrets enter the execution environment only when needed for a specific task.
- The preferred injection pattern is:
  1. human retrieves or authorizes retrieval from 1Password
  2. secret is materialized into the Mac Mini execution account environment at
     execution time or written into an ignored local config file
  3. runtime consumes the secret from environment variables or ignored local
     config

### Guardrails

- GitHub is canonical for code and tracked docs, not for secrets.
- Neither `local-shared-dropoff/` nor macOS shared-folder mounts are approved
  secret-distribution channels.
- Final legacy secret retirement and the final 1Password cutover are a later
  gate before real AI-agent operation, not a blocker for the first HQ smoke
  proof.

## Shared-Storage Guardrail Note

### Decision

Broad shared storage is disabled by default and is not the default
synchronization model for Execution HQ.

### Allowed Use

- `local-shared-dropoff/` may exist inside the canonical local-workspace
  skeleton as a narrow short-lived exchange lane.
- macOS shared-folder mounts remain opt-in only for narrow explicit transfer
  cases.

### Guardrails

- Do not treat `local-shared-dropoff/` as a working folder, retention folder,
  or secret lane.
- Do not treat broad shared mounts as the default sync model.
- Operationally important state must live in the correct canonical surface:
  - GitHub for tracked code/docs
  - 1Password for secrets
  - documented machine-local storage for runtime state

## VM Trigger Note - When Extra Isolation Is Justified

### Decision

VM isolation is not the default assumption for the semi-initial bootstrap. It
remains a later hardening track unless NemoClaw/OpenShell alone proves
insufficient.

### Trigger Conditions

Escalate from host-only NemoClaw/OpenShell isolation to VM isolation when one
or more of the following becomes true:

1. boundary failure evidence exists
2. required policy cannot be enforced cleanly on the host
3. cross-lane contamination risk becomes material
4. evidence or compliance requirements tighten
5. recovery or destructive experimentation needs disposable isolation

### Non-Triggers

The following do not justify immediate VM adoption by themselves:

- a general preference for more security without a concrete boundary gap
- unresolved future hardening ideas
- the mere existence of a possible dedicated-user migration, since that
  migration is already part of the current bootstrap decision

## Operating Summary

For the semi-initial bootstrap, the active operating contract is:

- MacBook acts as the control console
- Mac Mini `cjarguello` account acts as admin/maintenance only
- Mac Mini `taylorhq` account acts as the execution account by default
- NemoClaw/OpenShell is the default runtime boundary
- GitHub is the canonical sync source for rebuildable workspace state
- 1Password is the canonical secret source
- `local-shared-dropoff/` is narrow exchange only
- broad shared mounts remain off unless a documented exception is needed
- VM isolation stays optional until a concrete trigger is met

These defaults should be treated as the active operating contract for the
remaining semi-initial bootstrap work unless a later decision record
explicitly supersedes them.
