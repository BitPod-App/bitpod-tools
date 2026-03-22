# Pre-Rename Execution Branch Map v1

Date: 2026-03-15  
Primary issue: [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)  
Related issue: [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)

## Purpose

Define the exact GitHub branches that should be treated as the current execution baseline before any later rename or final branch normalization work.

This is not the final forever branch strategy.
It is the explicit pre-rename branch map that removes ambiguity for machine transition work.

## Current execution branch map

| Repo | Execution branch | Reason |
|---|---|---|
| `bitpod-assets` | `main` | Already clean and in sync; no migration-prep branch is needed |
| `bitpod-docs` | `codex/cleanup-zone-policy-docs` | Contains the active cleanup/policy/project-source truth, not just historical main |
| `bitpod-tools` | `codex/migration-prep-bitpod-tools-mainline` | Contains the active process/bridge/T3 machine-transition truth |
| `sector-feeds` | `codex/migration-prep-sector-feeds` | Canonical feed/transcription repo with current cleanup and command-surface truth |
| `bitpod-taylor-runtime` | `codex/migration-prep-taylor-runtime` | Current preserved runtime baseline |
| `bitregime-core` | `codex/migration-prep-bitregime-core` | Current preserved baseline for core contract/readme truth |

## Rules

- Treat the branch listed above as the current truthful branch for that repo.
- Do not pull machine-transition state from quarantined legacy roots.
- Do not infer that `main` is always the correct branch during this pre-rename window.
- Do not treat this map as permanent naming or permanent branching policy.

## Mac Mini implication

Until repo rename / branch normalization is explicitly completed:

- the Mac Mini should clone from GitHub
- and use the execution branches listed above

That is cleaner than depending on retired local roots and more truthful than pretending all repos are already normalized to `main`.

## Exit condition

This map should be retired only when:

1. final canonical branch strategy is explicitly chosen
2. the repos are normalized accordingly
3. the Mac Mini no longer depends on this temporary execution-branch map
