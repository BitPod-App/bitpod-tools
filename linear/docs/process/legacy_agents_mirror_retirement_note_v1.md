# Legacy Agents Mirror Retirement Note v1

Date: 2026-03-15  
Primary issues:
- [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
- [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)

## Purpose

Make the current `~/.agents` status explicit so it is no longer treated as mysterious hidden truth.

## Current status

- canonical local skill home for this workspace:
  - `/Users/cjarguello/bitpod-app/local-workspace/local-codex/skills/taylor`
  - `/Users/cjarguello/bitpod-app/local-workspace/local-codex/skills/qa-specialist`
- compatibility shim paths:
  - `/Users/cjarguello/.agents/skills/taylor`
  - `/Users/cjarguello/.agents/skills/qa-specialist`

Current verified implementation:

- the home-directory paths now resolve as symlinks to the `local-codex` copies
- the original duplicate directories were quarantined under:
  - `/Users/cjarguello/bitpod-app/local-workspace/local-trash-delete/agents-mirror-retirement-20260315/`

## Working interpretation

- `local-codex` is the canonical local operating surface.
- `~/.agents` is compatibility residue and historical shim state.
- repo docs and health checks should prefer `local-codex`.
- the existence of the mirror alone is not proof that it remains the correct source of truth.

## Why the mirror is not retired yet

It should not be quarantined blindly while any of the following remain true:

1. the live Codex skill inventory in the current app/session still advertises `~/.agents` paths
2. the user has not yet decided whether to tolerate the mirror for compatibility through the current transition window
3. there is no verified proof yet that removing the mirror would not disrupt active session/tooling behavior

## Retirement condition

Retire the `~/.agents` compatibility shim only when all are true:

1. active repo/runtime surfaces no longer depend on it
2. canonical local copies under `local-codex` are verified complete
3. Codex runtime/session skill inventory no longer needs the home-directory path
4. the move is done in a fresh pass where disruption can be observed honestly

## T3 implication

- demotion to legacy mirror status is required for T3 honesty
- physical deletion or quarantine of the mirror is desirable, but can remain a later step if runtime compatibility is still uncertain
