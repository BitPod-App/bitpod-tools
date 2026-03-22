# Execution HQ Architecture Decisions and Boundary Guardrails v1

Date: 2026-03-22  
Primary issue: [BIT-105 — Execution HQ architecture decisions and boundary guardrails](https://linear.app/bitpod-app/issue/BIT-105/execution-hq-architecture-decisions-and-boundary-guardrails)

## Purpose

Make the Mac Mini execution-HQ operating assumptions explicit enough that Phase 3 bootstrap work can proceed without guessing.

This note locks the default account/path strategy, remote-control tooling, secret flow, shared-folder policy, and VM-isolation trigger for the current bootstrap phase.

## Decision Record — Account and Path Strategy

### Decision

- Keep using the existing `cjarguello` macOS account on the Mac Mini for the current Phase 3 bootstrap.
- Do **not** block Execution HQ bootstrap on creating a separate dedicated user.
- Prefer username-agnostic path usage in commands, scripts, and docs whenever practical:
  - use `$HOME` instead of hard-coding `/Users/cjarguello`
  - use a workspace root variable such as `$WORKSPACE` when referring to the rebuilt working tree
- Continue treating GitHub as the canonical source used to rebuild the Mac Mini workspace.

### Rationale

- Reusing the existing account reduces bootstrap friction and avoids introducing a second migration axis before the execution boundary is proven.
- Username-agnostic pathing preserves portability if the Mac Mini later moves to a dedicated runtime user, a renamed account, or a replacement host.
- Keeping the path contract stable now lowers the cost of later hardening.

### Guardrails

- Hard-coded `/Users/cjarguello/...` paths are allowed only when a command must reference a known current-machine fact or an already-existing asset that cannot yet be parameterized.
- New operational docs should prefer examples such as:
  - `export WORKSPACE="$HOME/bitpod-app"`
  - `cd "$WORKSPACE/bitpod-tools"`
- A later dedicated-user migration becomes appropriate only after the Mac Mini execution flow is stable enough that identity separation can be changed without confusing the bootstrap baseline.

## Required Tooling — MacBook Control Console

The MacBook control console must have the following tools available for Phase 3 operation:

1. **Terminal or iTerm2**
   - required interactive shell surface for remote operations, recovery steps, and session management
2. **`ssh`**
   - required primary transport for command execution and administration on the Mac Mini
3. **`git`**
   - required for clone, branch, fetch, verification, and rebuild-from-GitHub workflows
4. **`gh`**
   - required for GitHub PR, branch, and repo-management workflows from the control console
5. **1Password**
   - required human-facing source of truth for secrets and credentials used by the execution environment

### Helpful but Optional Tooling

- **`tmux`** for durable terminal sessions and recovery from network interruptions
- **`scp` / `rsync`** for deliberate one-off file transfer when GitHub is not the right transport
- **Tailscale** if direct network access or local reachability proves unreliable

### Tooling Boundary

- Remote interaction is expected to happen primarily through shell access, GitHub synchronization, and intentional secret retrieval.
- Shared-folder mounts are not part of the required default tooling model.

## Secret-Flow Note — 1Password as Source of Truth

### Decision

1Password is the source of truth for secrets used by the Mac Mini execution environment.

### Required Flow

- Secrets are authored, rotated, and reviewed in 1Password first.
- Secrets enter the execution environment only when needed for a specific runtime or setup task.
- The preferred injection pattern is:
  1. human retrieves or authorizes retrieval from 1Password
  2. secret is materialized into the Mac Mini environment at execution time or written into a local env/config file that stays outside Git-tracked repo content
  3. runtime consumes the secret from environment variables or an ignored local config file
- Secrets must not become canonical in ad hoc notes, shared folders, committed files, or undocumented shell history.

### Guardrails

- GitHub is canonical for code and tracked docs, not for secrets.
- Shared folders are not an approved secret-distribution channel.
- If a runtime requires a local `.env` or equivalent file, that file must remain untracked and should be sourced from 1Password-backed values rather than hand-maintained drift.
- If automation around secret injection is introduced later, it must still preserve 1Password as the upstream system of record.

## Shared-Folder Guardrail Note

### Decision

Shared folders are disabled by default and are not the default synchronization model for Execution HQ.

### Allowed Use

Shared folders are opt-in only for narrow, explicit cases such as:

- temporary transfer of a large artifact that should not go through Git
- short-lived troubleshooting where direct inspection is necessary
- a clearly documented bridge step during migration or recovery

### Guardrails

- Shared folders must not become the silent source of truth for code, docs, runtime state, or secrets.
- Anything that becomes operationally important must be moved into the correct canonical surface:
  - GitHub for tracked code/docs
  - 1Password for secrets
  - documented local runtime storage for machine-local state
- Before enabling a shared folder, record the purpose, scope, expected duration, and cleanup path.
- Leave shared-folder access off when there is no current, specific need.

## VM-Trigger Note — When Extra Isolation Is Justified

### Decision

VM isolation is not the default Phase 3 assumption. It remains a later hardening track unless NemoClaw/OpenShell alone proves insufficient.

### Trigger Conditions

Escalate from host-only NemoClaw/OpenShell isolation to VM isolation when one or more of the following becomes true:

1. **Boundary failure evidence exists**
   - testing or real operation shows NemoClaw/OpenShell can reach data, files, network paths, or host capabilities that should remain outside the approved execution boundary
2. **Required policy cannot be enforced cleanly on the host**
   - the intended least-privilege posture depends on controls that are impractical, brittle, or unverifiable without a VM boundary
3. **Cross-lane contamination risk becomes material**
   - multiple execution lanes, secret classes, or trust tiers must coexist and host-level separation is no longer credible enough
4. **Evidence or compliance requirements tighten**
   - stakeholders need stronger isolation proof, rollback guarantees, or inspection boundaries than the host runtime can convincingly provide
5. **Recovery and experimentation need disposable isolation**
   - the team needs repeatable destructive testing or high-risk experiments that should be thrown away without trusting host cleanup alone

### Non-Triggers

The following by themselves do **not** justify immediate VM adoption:

- a general preference for “more security” without a concrete boundary gap
- unresolved future hardening ideas
- the mere existence of a possible dedicated-user migration

## Operating Summary

For Phase 3, the default execution architecture is:

- MacBook acts as the control console
- Mac Mini acts as Execution HQ
- NemoClaw/OpenShell is the default runtime boundary
- GitHub is the canonical sync source for rebuildable workspace state
- 1Password is the canonical secret source
- shared folders remain off unless a narrow, documented exception is needed
- VM isolation stays optional until a concrete trigger is met

These defaults should be treated as the active operating contract for remaining Phase 3 bootstrap work unless a later decision record explicitly supersedes them.
