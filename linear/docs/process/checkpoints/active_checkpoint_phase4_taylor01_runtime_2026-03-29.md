# Active Checkpoint — Phase 4 Taylor01 Runtime — 2026-03-29

Primary issues:
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist)
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)

Related context:
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)

## Verified now

- `mini-01.local` remains reachable from the control console over SSH.
- The real execution account is `taylor01`.
- The execution workspace is `/Users/taylor01/BitPod-App`.
- The Taylor runtime launcher is the supported bring-up path:
  - `/Users/taylor01/BitPod-App/bitpod-taylor-runtime/scripts/launch_taylor.sh`
- The active secret source is the env-file path, not a configured 1Password CLI path:
  - `/Users/taylor01/BitPod-App/bitpod-taylor-runtime/configs/.env`
- Direct Zulip API probes from the Mini now succeed against:
  - `GET /api/v1/users/me`
  - `POST /api/v1/register`
- At `2026-03-29T23:08:18Z`, the managed runtime was verified live through the supported background path:
  - `scripts/launch_taylor.sh background`
  - `scripts/launch_taylor.sh status` returned `status=running pid=11272`
- The running process environment showed the expected runtime tuple loaded:
  - `ZULIP_SITE`
  - `ZULIP_EMAIL`
  - `ZULIP_API_KEY`
  - `ZULIP_STREAM`
- The running process had an active established outbound HTTPS connection to Zulip.

## Important truth corrections

- Earlier `401 Invalid API key` lines in `artifacts/zulip/taylor.log` are stale historical evidence, not the best current runtime truth.
- Earlier `Missing required env vars` failures were launch-path failures from invoking `python3 -m taylor` directly without sourcing `configs/.env`.
- Current machine truth is stronger:
  - the managed Taylor01 runtime can now be started on the Mini through the supported launcher path
  - the live env tuple is loaded into the running process
  - raw Zulip auth and queue registration both succeed outside the stale historical log path

## What this unlocks

- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop) is no longer blocked by basic Mini bring-up.
- [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface) can now move from setup/debug into operator acceptance evidence.

## Still not proven

- `TAYLOR_REAL_AI_AGENT=true` is not yet proven from this checkpoint alone.
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill) remains open.
- [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist) remains open.
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) remains open.

## Fastest next sequence

1. Use the now-live Taylor01 runtime for one explicit operator quickcheck aligned to [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface).
2. Capture one retained acceptance artifact from that exchange.
3. Move immediately to the first non-Taylor specialist embodiment lane for [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill).
4. Use that specialist proof to drive the first honest team-loop artifact for [BIT-98 — Prove real multi-agent team loop with Taylor plus embodied specialist agent(s)](https://linear.app/bitpod-app/issue/BIT-98/prove-real-multi-agent-team-loop-with-taylor-plus-embodied-specialist).

## Current recommendation

- Do not reopen more Mini bootstrap or secret-path design work unless the managed runtime drops again.
- Treat the current blocker as acceptance/evidence, not bring-up.
