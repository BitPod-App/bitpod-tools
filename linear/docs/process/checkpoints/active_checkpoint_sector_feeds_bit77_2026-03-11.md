# Active Checkpoint — sector-feeds BIT-77 — 2026-03-11

## Lane

- active issue: [BIT-77 — Implement weekly run-track cleanup and operator-facing summary contract](https://linear.app/bitpod-app/issue/BIT-77/implement-weekly-run-track-cleanup-and-operator-facing-summary)
- repo/worktree: `/Users/cjarguello/BitPod-App/sector-feeds/.worktrees/sector-feeds-bit77`
- branch: `codex/bit-77-run-track-cleanup`

## Current state

- open PRs:
  - [BitPod-App/sector-feeds PR #32 — [BIT-77] Implement weekly run-track cleanup and operator-facing summary contract](https://github.com/BitPod-App/sector-feeds/pull/32)
- current issue status:
  - BIT-77 = In Progress
- latest verified findings:
  - legacy Tuesday remains the lightweight reliability/backfill lane
  - experimental remains the heavier diff/evaluation lane
  - `rss_preferred` is the correct cheaper source path when available
  - transcript input remains full transcript, not summary
  - canonical Tuesday automations were updated to `sector-feeds` and activated
  - duplicate paused `mallers-*` automation folders were archived out of the live automation directory

## Durable references

- key runbooks/specs:
  - `/Users/cjarguello/BitPod-App/sector-feeds/.worktrees/sector-feeds-bit75/docs/runbooks/weekly_run_track_audit_v1.md`
  - `/Users/cjarguello/BitPod-App/sector-feeds/.worktrees/sector-feeds-bit77/docs/runbooks/legacy_tuesday_report.md`
  - `/Users/cjarguello/BitPod-App/sector-feeds/.worktrees/sector-feeds-bit77/docs/runbooks/experimental_weekly_btc_gate.md`
- related backup archive:
  - `/Users/cjarguello/BitPod-App/local-workspace/local-working-files/automation_backups/duplicate_mallers_automations_20260311T041710Z`

## Next actions

1. review/merge [BitPod-App/sector-feeds PR #32 — [BIT-77] Implement weekly run-track cleanup and operator-facing summary contract](https://github.com/BitPod-App/sector-feeds/pull/32)
2. after merge, validate one sample legacy and experimental recurring run end-to-end against the new summary contract
3. confirm the Tuesday automations produce uniquely named useful run artifacts and explicit GPT consumption evidence

## Blockers

- PR #32 review/merge gate
