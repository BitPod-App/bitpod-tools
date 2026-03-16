# Linear Admin Change Control v1

Status: Working baseline
Owner: Product Development
Last updated: 2026-03-14

## Purpose

Define the approval and evidence bar for high-impact Linear changes so agents can move quickly without silently breaking workflow truth.

This is the active successor to the older bootstrap-era permission model. It keeps the useful safeguards without carrying forward the legacy `M-9` framing.

## Scope

Use this document for Linear changes that affect:

- workflows or statuses
- labels or templates
- project or team structure
- automations
- issue-routing behavior
- permission or integration settings tied to Linear operations

## Core rule

If a Linear change has meaningful blast radius, it must be reversible, evidenced, and explicitly approved at the right level before execution.

## Default mode

- mode: `high_autonomy_with_audit`
- expectation: reversible changes can move quickly when evidence is attached
- fail-closed rule: destructive or schema-level changes do not proceed without pre-change evidence, rollback notes, and post-change validation

## Role boundaries

### Taylor orchestration lane

- May prepare or execute reversible admin/process changes when the evidence package is complete.
- Must not treat broad admin access as permission to skip change-control artifacts.

### Vera QA lane

- May record verification, defects, and readiness outcomes tied to Linear operations.
- Must not restructure workflow/schema on its own.

### Engineering lanes

- May update issue execution details, links, and implementation evidence.
- Must not change Linear governance or workflow structure without explicit approval.

### CJ

- Approves destructive or high-blast changes.
- Decides whether residual risk is acceptable when a temporary bypass is requested.

## Approval thresholds

### Safe autonomous

Allowed with evidence attached:

- create or update non-destructive process docs
- create reports or audit artifacts
- adjust issue content without changing schema or workflow behavior

### Guarded autonomous

Allowed with Taylor approval plus evidence:

- reversible workflow/process changes in Linear
- new templates or labels with low blast radius
- dry-run automation configuration work

### CJ approval required

Blocked unless CJ explicitly approves:

- deleting a Linear team, project, workflow, or template set
- mass destructive changes affecting more than 20 entities
- irreversible data removal where rollback is not documented
- auth or permission changes outside normal issue operations

## Required artifacts for workflow or schema changes

- `linear_change_proposal_template_v1.md`
- pre-change snapshot or screenshots
- rollback note
- post-change validation evidence

## Validation checklist after workflow or schema changes

1. Core labels and templates still exist.
2. Existing active issues still map to valid statuses.
3. Blocked flows remain resolvable.
4. PM, QA, and engineering ownership fields still work.
5. No orphaned status transitions were introduced.

## Lockdown trigger

Switch to `lockdown_review_required` if any of these occur:

- unplanned schema breakage
- two failed post-change validations in a row
- loss of issue traceability

In lockdown mode:

- destructive actions are disabled except for CJ-approved runs
- further workflow/schema changes require explicit review before execution

## Temporary divergence rule

If live operation temporarily diverges from the intended model:

1. record the reason
2. define scope and duration
3. define rollback or normalization steps
4. attach the evidence in Linear
5. log the divergence in the active operating guide changelog
