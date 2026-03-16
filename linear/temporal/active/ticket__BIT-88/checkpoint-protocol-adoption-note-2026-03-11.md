# Checkpoint Protocol Adoption Note — 2026-03-11

Linked issue: [BIT-88 — Operationalize long-thread checkpoint protocol across active lanes](https://linear.app/bitpod-app/issue/BIT-88/operationalize-long-thread-checkpoint-protocol-across-active-lanes)

## Adoption evidence

Active checkpoint instances now present in repo:

1. `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-77/checkpoint-sector-feeds-bit77-2026-03-11.md`
2. `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-83/checkpoint-phase4-operating-model-2026-03-11.md`

## What this proves

- the checkpoint protocol is no longer only a baseline doc and template
- at least two live lanes now have repo-side resumable state
- one lane is data/runtime oriented
- one lane is operating-model / governance oriented

## What still drifts

- resume prompts are still mostly produced in chat, not yet persisted routinely alongside every checkpoint instance
- some active lanes still rely on ad hoc thread summaries rather than a consistent checkpoint file refresh cadence
- thread retirement is still operator-driven rather than automatically triggered by a clear threshold

## Current rule

Use repo-side checkpoints whenever:

- a lane spans multiple PRs/issues
- a lane is likely to resume in a later thread
- active context-window shrinkage is visible
- a lane reaches a stable stopping point after meaningful normalization or proof work

## Next hardening move

If this note and the second active checkpoint are accepted, the next step is to standardize:

- when resume prompts are written back into repo files
- when old checkpoints are superseded
- when a thread must be retired rather than stretched further
