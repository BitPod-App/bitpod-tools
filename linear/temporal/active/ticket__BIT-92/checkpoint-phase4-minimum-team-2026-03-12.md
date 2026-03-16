# Active Checkpoint — phase4-minimum-team — 2026-03-12

## Lane

- active issues:
  - [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera)
  - [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy)
  - [BIT-93 — Stand up first engineering specialist lane under Taylor-led delegation](https://linear.app/bitpod-app/issue/BIT-93/stand-up-first-engineering-specialist-lane-under-taylor-led-delegation)
- repo/worktree at checkpoint time (retired): `/Users/cjarguello/BitPod-App/bitpod-tools/.worktrees/bitpod-tools-bit92`
- current surviving repo path: `/Users/cjarguello/BitPod-App/bitpod-tools`
- branch: `codex/bit-90-vera-qa-lane`

## Current state

- merged just before this lane:
  - [PR #42 — [BIT-92] Add minimum Phase 4 agent team contract BIT-92](https://github.com/BitPod-App/bitpod-tools/pull/42)
- repo-side BIT-90 package added:
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/agent-references/vera-qa-lane-contract-v1.md`
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-90/vera-qa-lane-operational-proof-v1.md`
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/examples/verification_report_bit90_minimum_team_2026-03-12.md`
- current QA implementation surface:
  - canonical local surface: `/Users/cjarguello/BitPod-App/local-workspace/local-codex/skills/qa-specialist/SKILL.md`
- QA lane truth after this package:
  - dedicated Vera-style QA lane = present at working-baseline level
  - interim [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) = downgraded from primary reliance but still required as temporary merge-governance fallback

## Durable references

- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/agent-references/minimum-phase4-agent-team-contract-v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/agent-references/vera-qa-lane-contract-v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-90/vera-qa-lane-operational-proof-v1.md`
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/examples/verification_report_bit90_minimum_team_2026-03-12.md`

## Next actions

1. validate the branch with `bash linear/scripts/local_smoke.sh`
2. package BIT-90 in a PR and link the QA artifact in the PR/body or Linear comment
3. move to [BIT-93 — Stand up first engineering specialist lane under Taylor-led delegation](https://linear.app/bitpod-app/issue/BIT-93/stand-up-first-engineering-specialist-lane-under-taylor-led-delegation) as the next minimum-team implementation lane
4. keep [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) deferred until BIT-92 is truly satisfied

## Blockers

- GitHub reviewer-routing / merge-governance still not fully aligned with the QA lane model
- minimum team still needs a stronger explicit engineering-lane proof package under BIT-93 before Discord acceptance becomes meaningful
