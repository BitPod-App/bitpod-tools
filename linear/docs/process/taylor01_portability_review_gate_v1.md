# Taylor01 Portability Review Gate v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Require explicit Taylor01 portability classification for any work that could quietly hard-code BitPod-specific assumptions into reusable process, workflow, agent, or adapter layers.

## Gate applies when

A ticket or PR touches any of:

- agents or specialist roles
- orchestration/runtime behavior
- process docs
- workspace policy
- Linear/GitHub/Discord workflow behavior
- future adapter contracts

The gate does not apply to clearly product-only work such as BitPod brand, BitPod glossary, or user-facing product canon.

## Required fields

Every relevant Linear issue and PR must include:

- `T01_LAYER`: `core | policy | adapter | bitpod-embedding | mixed`
- `T01_SPECIFICITY`: `portable | bitpod-specific | mixed`
- `T01_COUPLING`: short note on what is still too coupled
- `T01_ACTION`: `keep-local | move-later | create-generic-version-now`

## Decision rule

- If the work creates hard future lock-in, portability work may interrupt or reshape BitPod delivery.
- If the work is acceptable for now, coupling must still be logged explicitly.
- "We'll clean it up later" is not sufficient without a `T01_COUPLING` note.

## Where to record it

### Linear tickets

Put the block in:

- the issue description, or
- the first execution comment if the issue already exists and should not be heavily rewritten

### PRs

Put the block in the PR description using the repo PR template.

## Example block

See:

- `linear/examples/taylor01_portability_check_template_v1.md`

## Current policy stance

This is a hard review gate, not a soft suggestion.

Taylor01 is important enough that avoiding bad entanglement is allowed to slow BitPod work.

