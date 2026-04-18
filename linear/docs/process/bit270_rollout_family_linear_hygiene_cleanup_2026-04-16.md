# BIT-270 rollout family Linear hygiene cleanup — 2026-04-16

Status: completed retroactive metadata cleanup
Owner: Codex under CJ-directed expedited cleanup pass
Primary parent: [BIT-270 — Coordinate Tailgate/Tailscale-first Mission Control rollout for Taylor01](https://linear.app/bitpod-app/issue/BIT-270/coordinate-tailgatetailscale-first-mission-control-rollout-for)

## Why this cleanup was needed

Several rollout-family issues had reached truthful completion in code/runtime reality without equivalent Linear hygiene:

- missing canonical issue-type labels
- missing estimates on completed subtasks
- stale blocker residue on a completed parent
- missing explicit QA/PM result labels on finalized issues
- utility niceties implemented in code but not attached cleanly to the rollout family

CJ explicitly allowed expedited retroactive normalization rather than reopening a full QA/PM lane for already-shipped work.

## Issues normalized

- BIT-212
- BIT-270
- BIT-282
- BIT-283
- BIT-303
- BIT-304

## Applied normalization rules

- preserve truthful completed state when implementation and operator proof already existed
- add exactly one canonical Issue Type label where missing
- add valid estimate where missing
- use `qa-skipped` when no separate QA artifact existed for the cleanup pass
- use `pm-accepted` when CJ retroactively affirmed acceptance
- remove stale blocker residue from completed issues
- attach stray utility niceties to the parent rollout family when the relationship was obvious

## Concrete outcomes

### BIT-212
- kept `Done`
- labels normalized to `⚙️ Chore`, `pm-accepted`, `qa-skipped`

### BIT-270
- kept `Done`
- removed stale `needs-other`
- labels normalized to `⭐️ Feature`, `pm-accepted`, `qa-skipped`
- description expanded to include scope-change clarification and subtask review

### BIT-282
- kept `Done`
- added `⚙️ Chore`
- added estimate `2`
- added `pm-accepted`, `qa-skipped`

### BIT-283
- kept `Done`
- retained estimate `2`
- labels normalized to `⭐️ Feature`, `pm-accepted`, `qa-skipped`

### BIT-303
- kept `Done`
- added parent `BIT-270`
- added `⭐️ Feature`
- added estimate `1`
- added `pm-accepted`, `qa-skipped`

### BIT-304
- kept `Done`
- added parent `BIT-270`
- added `⭐️ Feature`
- added estimate `1`
- added `pm-accepted`, `qa-skipped`

## Enforcement follow-up

The local Linear engine had drifted from the live workspace because its canonical type matcher only recognized plain labels like `Feature` / `Chore`, while the actual workspace uses emoji-prefixed labels like `⭐️ Feature` / `⚙️ Chore`.

That mismatch was corrected in code during the same cleanup pass so future readiness/merge enforcement matches the real workspace labels.
