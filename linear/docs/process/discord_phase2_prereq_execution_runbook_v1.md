# Discord Phase 2 Prereq Execution Runbook v1

Date: 2026-03-09
Primary issue: https://linear.app/bitpod-app/issue/BIT-59/discord-workspace-webhook-prerequisites-for-phase-2-parity-execution
Dependent execution: https://linear.app/bitpod-app/issue/BIT-30/linear-github-discord-webhook-integration-parity-checks

## Objective
Unblock Phase 2 webhook parity checks with the minimum required Discord setup while explicitly deferring non-critical scope.

## Required now (execute)
1. Create/confirm Discord server for BitPod migration testing.
2. Create channel skeleton (from BIT-28 docs):
   - `#00-ops-status`
   - `#30-build`
   - `#40-review-qa`
   - `#50-release`
   - `#60-incidents`
3. Create one incoming webhook per channel.
4. Store webhook URLs only in secrets/config (never in issues/docs).
5. Run one test message per webhook.
6. Capture evidence:
   - channel list screenshot
   - webhook target map (channel names + masked token suffix only)
   - test post timestamps

## Not required now (defer)
- Outbound email delivery service setup (explicitly deferred to Phase 3).
- Full Discord role/permission hardening beyond baseline admin safety.
- Final channel taxonomy/branding polish.
- Notification copywriting optimization.
- Cross-workspace webhook fanout.

## Blocker handling rule
If a prerequisite cannot be completed without new credentials/UI access, park that exact item as blocked and continue remaining checklist items.

## Validation commands (operator-side)
Use the webhook sender script once secrets are present:

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
python3 linear/scripts/discord_webhook_smoke.py --config linear/config.discord.example.json --dry-run
```

Then run live with real config file outside git.

## Fast evidence pack (recommended)

Generate one markdown pack covering sanitized route map + smoke + parity outputs:

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
python3 linear/scripts/discord_phase2_evidence_pack.py \
  --config /ABS/PATH/private.discord.config.json \
  --out /Users/cjarguello/BitPod-App/local-workspace/local-working-files/discord_phase2_evidence_pack.md
```

Live check mode:

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
python3 linear/scripts/discord_phase2_evidence_pack.py \
  --config /ABS/PATH/private.discord.config.json \
  --out /Users/cjarguello/BitPod-App/local-workspace/local-working-files/discord_phase2_evidence_pack_live.md \
  --live
```

## Completion evidence contract for BIT-59
- Status line: `<from> -> <to> + transition reason`
- Commands/UI checks executed
- Artifact paths/screenshots
- Pass/fail per channel
- Deferred items list (explicit)
- Rollback note

## Rollback note
If parity checks cause noisy routing, disable webhook endpoints at Discord first, then remove runtime references from local config/secrets.
