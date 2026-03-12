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

## Implication

- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) cannot pass honestly until `#general` conversational reality is proven.
- [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent) should carry the Discord-specific contract and implementation path for that proof.
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) should carry the transport-agnostic Taylor-real proof.

## Repo artifacts

- `linear/docs/process/taylor_discord_general_intake_contract_v1.md`
- `linear/docs/process/taylor_real_agent_acceptance_contract_v1.md`
- `linear/docs/process/discord_real_acceptance_checklist_v1.md`
- `linear/docs/process/discord_real_acceptance_status_2026-03-12.md`
- `linear/docs/process/discord_migration_architecture_v1.md`
