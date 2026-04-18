# Linear Process v1.1 Control Tower Change Proposal

Use this proposal as the guarded-lane artifact for the 2026-04-15 Product Development workflow alignment pass.

## Summary

- change id: `linear-process-v1-1-control-tower-2026-04-15`
- date_utc: `2026-04-15`
- owner: `Product Development`
- mode: `high_autonomy_with_audit`

## What changes

- preserve current live workflow names: `Backlog`, `Ready`, `In Progress`, `In Review`, `Delivered`, `Accepted`, `Done`
- tighten gate semantics so `qa-*` results move `In Review` -> `Delivered`
- tighten PM semantics so `pm-accepted` and `pm-skipped` move `Delivered` -> `Accepted`
- require merge-readiness truth before merge-driven `Accepted` -> `Done`
- move inactivity closure toward `Backlog -> Icebox 🧊 -> Stale`
- keep `Obsolete` as legacy / edge-case, not the primary inactivity sink
- align active Vera-style QA guidance with truthful substitute-surface language
- add explicit Control Tower validation language to the active operating docs

## Why now

- the active docs, engine, and prompts were drifting on `pm-skipped`, merge-driven closure, and inactivity handling
- current workflow/admin/guidance changes need a stronger Control Tower-aligned validation boundary
- the active Vera prompt was overclaiming independent QA authority relative to the current runtime reality

## Temporary divergence from target state (if applicable)

- target-state rule being bypassed:
  - live Linear team/project admin config is not mutated by this repo patch alone
- reason for bypass:
  - repo-side doctrine, engine, tests, and prompt surfaces can be aligned now, while live admin mutations still require UI-level change execution plus Control Tower validation
- scope and duration:
  - until the guarded admin lanes for Product Development workflow/config are executed and evidenced
- rollback or normalization plan:
  - revert the repo patch if it proves incorrect, or complete the matching live admin/config changes under the follow-up guarded lanes

## Blast radius

- affected teams, projects, statuses, labels, templates, automations:
  - Product Development team doctrine
  - repo-side Linear engine and tests
  - Vera-style QA prompt/guidance
  - README / operator references
- estimated number of affected entities:
  - docs: 5+
  - code/test surfaces: 4+
  - live Linear config: 0 directly mutated by this patch

## Pre-change snapshot

- snapshot source or location:
  - live Product Development issue statuses observed before patch:
    - `Icebox 🧊`, `Backlog`, `Ready`, `In Progress`, `In Review`, `Delivered`, `Accepted`, `Done`, `Canceled`, `Duplicate`, `Obsolete`, `Won't Do`, `Stale`
  - live label groups observed before patch:
    - `Issue Type`
    - `Blocked By`
    - `QA Review`
    - `PM Review`
  - repo-side baseline:
    - `linear_operating_model_v1.md`
    - `linear_operating_guide_v3.md`
    - `linear/src/engine.py`
    - `linear/examples/vera_linear_pr_review_prompt_v1.md`
- key entities before change:
  - `pm-skipped` path still ended in `Done`
  - non-acceptance work still allowed `In Review` -> `Done`
  - daily aging still closed `Icebox 🧊` work into `Obsolete`
  - Vera prompt still described itself as independent QA without the substitute-surface caveat

## Rollback plan

- rollback trigger:
  - tests fail in a way that exposes invalid assumptions about current workflow semantics
  - Control Tower validation rejects the artifact package or identifies truth-surface mismatch
- rollback steps:
  - revert the affected repo files
  - restore the prior `pm-skipped`, aging, and prompt semantics
  - remove the changelog/proposal references
- estimated rollback time:
  - under 30 minutes for repo-side revert

## Post-change validation

- [x] labels and templates intact
- [x] status mappings valid in repo doctrine and tests
- [x] active issues still traceable
- [x] blocked flow intact
- [x] ownership fields intact

## Outcome notes

- this artifact documents the repo-side alignment only
- live Linear admin/config mutation still requires the guarded follow-up lanes and Control Tower validation package
