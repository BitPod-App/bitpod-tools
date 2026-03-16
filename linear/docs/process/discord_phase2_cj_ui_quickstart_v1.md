# Discord Phase 2 CJ UI Quickstart v1

Primary issue: [BIT-59 — Discord workspace + webhook prerequisites for Phase 2 parity execution](https://linear.app/bitpod-app/issue/BIT-59/discord-workspace-webhook-prerequisites-for-phase-2-parity-execution)
Unblocks: [BIT-30 — Linear + GitHub + Discord webhook integration parity checks](https://linear.app/bitpod-app/issue/BIT-30/linear-github-discord-webhook-integration-parity-checks)

## Objective

Complete the minimum Discord UI work needed to unblock Phase 2 parity checks in one short pass.

## Scope

Do now:
- create or confirm the BitPod Discord server
- create the required five channels
- create one incoming webhook per channel
- record channel IDs and webhook URLs in a private local config file
- run the two verification commands

Do not do now:
- outbound email setup
- full Discord permission hardening
- channel taxonomy polish
- branding polish
- multi-surface routing redesign

## Required Channels

- `00-ops-status`
- `30-build`
- `40-review-qa`
- `50-release`
- `60-incidents`

## Private Config Target

Start from:

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/config.discord.example.json`

Create a private copy outside git, for example:

- `/Users/cjarguello/BitPod-App/local-workspace/local-working-files/private.discord.config.json`

Fill in:
- `discord.server_id`
- each channel `id`
- each webhook URL

Never paste raw webhook URLs into Linear, GitHub, or tracked repo files.

## UI Steps

1. Open the BitPod Discord server.
2. Confirm or create these channels:
   - `00-ops-status`
   - `30-build`
   - `40-review-qa`
   - `50-release`
   - `60-incidents`
3. For each channel:
   - open channel settings
   - open `Integrations`
   - create one incoming webhook
   - copy the webhook URL into the private config file
4. Copy the server ID and each channel ID into the same private config file.
5. Capture one screenshot showing the final channel list.

## Verification Commands

Run these from `/Users/cjarguello/BitPod-App/bitpod-tools`:

```bash
python3 linear/scripts/discord_config_preflight.py \
  --config /Users/cjarguello/BitPod-App/local-workspace/local-working-files/private.discord.config.json
```

```bash
python3 linear/scripts/discord_webhook_smoke.py \
  --config /Users/cjarguello/BitPod-App/local-workspace/local-working-files/private.discord.config.json \
  --live
```

```bash
python3 linear/scripts/discord_phase2_evidence_pack.py \
  --config /Users/cjarguello/BitPod-App/local-workspace/local-working-files/private.discord.config.json \
  --out /Users/cjarguello/BitPod-App/local-workspace/local-working-files/discord_phase2_evidence_pack_live.md \
  --live
```

## Completion Evidence

Attach or reference:
- channel-list screenshot
- `/Users/cjarguello/BitPod-App/local-workspace/local-working-files/discord_phase2_evidence_pack_live.md`
- generated parity matrix file next to that evidence pack

## Done Condition

BIT-59 is ready to close when:
- all five channels exist
- all five webhooks are live
- smoke passes
- evidence pack is generated
- no raw secrets were posted into tracked files or tickets
