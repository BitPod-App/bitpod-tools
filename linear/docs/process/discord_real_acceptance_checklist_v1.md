# Discord Real Acceptance Checklist v1

Date: 2026-03-12  
Primary issue: [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)
Related issues:
- [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform)
- [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify)
- [BIT-30 — Linear + GitHub + Discord webhook integration parity checks](https://linear.app/bitpod-app/issue/BIT-30/linear-github-discord-webhook-integration-parity-checks)
- [BIT-59 — Discord workspace + webhook prerequisites for Phase 2 parity execution](https://linear.app/bitpod-app/issue/BIT-59/discord-workspace-webhook-prerequisites-for-phase-2-parity-execution)
- [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera)

## Objective

Promote Discord from parity proof-of-concept to real acceptance surface for the team session contract and bridge command surface.

This issue is not complete when webhook parity is green. It is complete only when real team-style communication is exercised successfully in Discord with linked artifacts and a usable command/session flow.

## Promotion meaning

This issue is now a promoted closure gate, not a lightweight deferred item.

Interpretation:

- earlier Discord work proved baseline transport parity
- [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera) is now complete with `MINIMUM_TEAM_READY=true`
- therefore BIT-86 now matters more, because Phase 4 closure cannot be claimed honestly without this live acceptance gate

## Baseline checks (must already be true)

- Discord config preflight passes from clean `origin/main`
- Discord webhook smoke passes from clean `origin/main`
- Discord parity matrix passes from clean `origin/main`
- command/session contract docs exist
- bridge command cleanup baseline exists
- minimum team is real enough that Discord would test communication quality rather than only transport plumbing

Current verified baseline artifacts:

- `/Users/cjarguello/bitpod-app/local-workspace/local-working-files/discord_phase2_evidence_pack_live.md`
- `/Users/cjarguello/bitpod-app/local-workspace/local-working-files/discord_phase2_evidence_pack_live_matrix.md`
- `/Users/cjarguello/bitpod-app/local-workspace/local-working-files/discord_phase2_parity_report_live.md`
- `/Users/cjarguello/bitpod-app/local-workspace/local-working-files/discord_parity_matrix_report_current.md`
- `/Users/cjarguello/bitpod-app/bitpod-tools/.worktrees/bitpod-tools-bit92-ready/linear/docs/process/minimum_phase4_agent_team_readiness_v1.md`

## Acceptance scope

### A. Team-session usability

Pass only if all are true:

- a real Discord session thread/channel is used for intent-bearing team communication
- plans, decisions, and artifact links can be posted/read without ambiguity
- the communication surface is usable without relying on Zulip-only mental models

### B. Bridge command surface usability

Pass only if all are true:

- operator can identify which commands belong to Bridge vs Taylor runtime
- cleaned bridge command surface is understandable in practice
- no obsolete or misleading command naming blocks normal use

### C. Artifact + memory flow

Pass only if all are true:

- at least one Discord interaction links out to a real artifact
- at least one Discord interaction links back to a real Linear issue and/or PR
- resulting artifact/memory flow is durable and legible enough to support team operations

## Required live checks

1. Post one real planning/intent message in the active Discord environment.
2. Post one real decision/update message with a linked artifact.
3. Post one linked Linear issue reference.
4. Post one linked GitHub PR reference.
5. Verify the channel flow is understandable to a human operator without hidden context.
6. Verify command/session usage does not require Zulip-only mental models.
7. Capture screenshot or transcript evidence from the real Discord environment.

## Required outputs

- one acceptance note with pass/fail per section:
  - Team-session usability
  - Bridge command surface usability
  - Artifact + memory flow
- one screenshot or transcript excerpt from real Discord usage
- list of linked artifacts/Linear issues/PRs used in the acceptance run
- explicit completion verdict for:
  - [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform)
  - [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify)

## Fail conditions

Any of the following means BIT-86 remains open:

- Discord only works as a webhook sink, not a usable session surface
- command ownership between Bridge and Taylor remains confusing in practice
- the live flow cannot carry plans, decisions, and artifact links cleanly
- evidence depends on thread-local memory rather than durable references

## Completion rule

- [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform) and [BIT-39 — Bridge command surface cleanup (keep useful, remove obsolete, clarify behavior)](https://linear.app/bitpod-app/issue/BIT-39/bridge-command-surface-cleanup-keep-useful-remove-obsolete-clarify) are not truly done until this checklist passes in a real Discord environment.
