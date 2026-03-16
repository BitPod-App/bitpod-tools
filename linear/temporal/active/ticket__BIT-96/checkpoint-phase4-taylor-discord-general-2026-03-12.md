# Active Checkpoint — Phase 4 Taylor Discord General — 2026-03-12

Primary issue: [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent)  
Related closure gate: [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)

## Verified

- Current merged Discord acceptance docs prove webhook/parity baseline only.
- Current merged Discord acceptance docs require Taylor conversational proof, but they did not previously pin `#general` as the intended operator-facing surface.
- Current Discord migration architecture emphasized structured specialist channels more than `#general`.
- Current repo search did not yet verify a live Taylor Discord intake/runtime path for `#general`.

## Corrected truth

- Taylor should be conversationally reachable in Discord `#general`.
- Taylor should be usable there for broad BitPod-relevant conversation, not only narrow commands.
- Specialist channels remain useful, but they do not replace `#general` as the primary operator-facing proof surface.
- Taylor-real should still be provable in any live operator surface, not only Discord.
- Phase 4 should not be considered complete if only Taylor reaches embodied-agent status.
- Phase 4 requires at least one additional embodied specialist AI agent and a real multi-agent team loop.

## Implication

- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) cannot pass honestly until `#general` conversational reality is proven.
- [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent) should carry the Discord-specific contract and implementation path for that proof.
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) should carry the transport-agnostic Taylor-real proof.
- A separate Phase 4 embodiment/team-loop gate is still needed so minimum-team readiness is not misread as full Phase 4 completion.

## Repo artifacts

- `linear/protocol/agent-references/taylor-discord-general-intake-contract-v1.md`
- `linear/protocol/agent-references/taylor-real-agent-acceptance-contract-v1.md`
- `linear/protocol/agent-references/phase4-real-multi-agent-team-acceptance-contract-v1.md`
- `linear/protocol/configs/discord-real-acceptance-checklist-v1.md`
- `linear/temporal/active/ticket__BIT-86/discord-real-acceptance-status-2026-03-12.md`
- `linear/temporal/active/ticket__BIT-28/discord-migration-architecture-v1.md`
