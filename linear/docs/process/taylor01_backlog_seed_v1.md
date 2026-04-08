# Taylor01 Backlog Seed v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Seed the future Taylor01 backlog without forcing immediate execution.

## Candidate workstreams

1. Normalize mixed workspace policies into Taylor01 policy + BitPod overlay
   - split generic path/cleanup/state rules from BitPod absolute paths

2. Move portable agent contracts into `tools/taylor01/core`
   - Taylor orchestrator contract
   - specialist registry
   - runtime portability contract

3. Move reusable operating norms into `tools/taylor01/policy`
   - anti-drift
   - certainty/provenance
   - artifact naming
   - retrospectives

4. Move adapter contracts into `tools/taylor01/adapters`
   - Linear
   - GitHub
   - Discord

5. Define Slack adapter scaffold
   - map current Discord interaction model to Slack-capable abstractions

6. Define Jira adapter scaffold
   - map current Linear workflow/evidence contracts to Jira-capable abstractions

7. Contractor packaging for Taylor01
   - define external-facing service packaging for CJ + Taylor01 Team

8. Taylor01 extraction readiness review
   - periodic review of whether repo split is justified yet

9. Lock minimum real-Taylor runtime contract
   - define the minimum active runtime required to count as "real Taylor"
   - keep pure local skill-overlay behavior out of the durable runtime contract

10. Decide Claw v1 scope and boundary
   - lock whether Claw v1 is an operator surface, runtime wrapper, embodiment
     contract, or a narrow combination

11. Decide Taylor capability container direction
   - evaluate `SKILL.md`, `sould.md`, manifest-first package, or another
     explicit alternative without overhardening the current compatibility
     surface

12. Classify current Taylor artifacts by durability
   - classify active work across `bitpod-tools`, `bitpod-taylor-runtime`, and
     `taylor01-skills` into durable substrate, transitional compatibility, and
     BitPod/local overlay

13. Define future dedicated repo extraction trigger for Taylor01 Claw
   - keep repo name open until runtime and container boundaries are clearer
   - define what content moves when the trigger is met

## Suggested future ticket titles

- Taylor01: normalize workspace path policy into portable base + BitPod overlay
- Taylor01: move portable agent contracts into `tools/taylor01/core`
- Taylor01: define Slack adapter scaffold from current Discord contract
- Taylor01: define Jira adapter scaffold from current Linear contract
- Taylor01: package contractor-facing Taylor01 offer narrative and operating artifacts
- Taylor01: lock minimum real-Taylor runtime contract
- Taylor01: decide Claw v1 scope and non-goals
- Taylor01: decide capability container direction beyond current `SKILL.md`
- Taylor01: classify current Taylor artifacts by durability
- Taylor01: define future Taylor01 Claw repo extraction trigger

## Current stance

These are seed items only.

Items 9 through 13 are now live as:

- [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract)
- [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary)
- [BIT-216 — Taylor01: decide capability container direction beyond current `SKILL.md`](https://linear.app/bitpod-app/issue/BIT-216/taylor01-decide-capability-container-direction-beyond-current-skillmd)
- [BIT-217 — Taylor01: classify current artifacts by durability and overlay status](https://linear.app/bitpod-app/issue/BIT-217/taylor01-classify-current-artifacts-by-durability-and-overlay-status)
- [BIT-218 — Taylor01: define future dedicated repo extraction trigger for Claw](https://linear.app/bitpod-app/issue/BIT-218/taylor01-define-future-dedicated-repo-extraction-trigger-for-claw)

Current ordering is minimum-floor-first:

- first [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract),
  [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary),
  and [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
- then the first real proof lane in Bootstrap
- then the later refinement lanes

They should influence new work immediately, but they should not become a migration program unless explicitly promoted.

Temporary bypasses should not be dumped here by default.

Use the active bypass register first and only promote items here when they have become important enough to deserve a real Taylor01 follow-up lane.
