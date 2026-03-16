# Active Checkpoint — phase4-engineering-lane — 2026-03-12

## Lane

- active issues:
  - [BIT-93 — Stand up first engineering specialist lane under Taylor-led delegation](https://linear.app/bitpod-app/issue/BIT-93/stand-up-first-engineering-specialist-lane-under-taylor-led-delegation)
  - [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera)
  - [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy)
- repo/worktree at checkpoint time (retired): `/Users/cjarguello/bitpod-app/bitpod-tools/.worktrees/bitpod-tools-bit93`
- current surviving repo path: `/Users/cjarguello/bitpod-app/bitpod-tools`
- branch: `codex/bit-93-engineering-lane`

## Current state

- merged before this lane:
  - [PR #42 — [BIT-92] Add minimum Phase 4 agent team contract BIT-92](https://github.com/BitPod-App/bitpod-tools/pull/42)
- in-review QA lane package:
  - [PR #43 — [BIT-90] Stand up dedicated Vera QA lane BIT-90](https://github.com/BitPod-App/bitpod-tools/pull/43)
- repo-side BIT-93 package added:
  - `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/engineering_specialist_lane_contract_v1.md`
  - `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/engineering_specialist_lane_operational_proof_v1.md`

## Explicit current truth

- first engineering specialist lane = present at working-baseline level
- one engineering lane plus explicit fallback model = enough for current bootstrap minimum-team proof
- stronger multi-engineering specialization = later maturity work, not required right now

## Durable references

- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/engineering_specialist_lane_contract_v1.md`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/engineering_specialist_lane_operational_proof_v1.md`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/minimum_phase4_agent_team_contract_v1.md`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/taylor_orchestrator_operational_proof_v1.md`

## Next actions

1. validate the BIT-93 branch with `bash linear/scripts/local_smoke.sh`
2. open the BIT-93 PR with linked engineering-lane proof artifacts
3. fold the updated BIT-90 and BIT-93 truth back into BIT-92
4. keep [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) deferred until minimum-team readiness is explicit

## Blockers

- BIT-90 PR still needs to land before the minimum-team package is fully coherent on `main`
- Discord acceptance remains a later proving gate, not the next implementation step
