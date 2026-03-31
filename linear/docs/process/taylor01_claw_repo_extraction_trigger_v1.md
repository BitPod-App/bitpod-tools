# Taylor01 Claw Repo Extraction Trigger v1

Status: Working baseline
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Related issues:
- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)

## Objective

Define when a dedicated Taylor01 or Taylor01-Claw repo becomes justified, while
keeping the final repo name and exact package split open until the architecture
is more mature.

## Current truth

- `taylor01-skills` is the strongest current center for portable substrate
- `bitpod-taylor-runtime` is the current embodiment lane
- `bitpod-tools` still owns active BitPod/OpenClaw doctrine and overlay truth
- current Claw shape is still contract-first and proof-driven rather than
  package-final

## Extraction is not justified yet

A dedicated repo is not justified yet if the main motivation is only:

- wanting a cleaner name
- wanting the architecture to feel more real
- discomfort with current multi-repo staging
- a desire to move BitPod-local doctrine out before substrate and runtime
  boundaries are locked

## Extraction trigger

Treat dedicated repo creation as justified only when at least three of these are
true:

1. the runtime minimum for "real Taylor" is locked and stable enough to use as
   a live reference point
2. the Claw v1 boundary model is locked strongly enough that it is not changing
   every few days
3. the capability-container direction is stable enough to define what belongs
   in portable core versus compatibility surfaces
4. the current three-way split (`taylor01-skills`, `bitpod-taylor-runtime`,
   `bitpod-tools`) is materially slowing or distorting execution
5. a real non-BitPod context, client, or product needs the same Claw surface
6. there is a clear move set that can be extracted without pulling active
   BitPod doctrine and overlays into the new repo by accident

## Content that should move when the trigger is met

- durable Claw boundary canon
- durable runtime-boundary and embodiment contracts
- durable capability-container canon
- future portable operator-surface contracts that are no longer BitPod-local

## Content that should stay out by default

- active BitPod Linear doctrine
- BitPod checkpoints and closeout overlays
- BitPod-local process truth
- current proving-ground overlays that are still intentionally local

## Working interpretation

Until the trigger is met:

- use the current three-lane split intentionally
- keep substrate, runtime, and doctrine truth separated
- avoid creating a dedicated repo just to make the architecture look settled

After the trigger is met:

- create the new repo with an explicit move set
- move only durable Claw-owned content first
- leave BitPod-local overlays behind unless a separate decision says otherwise
