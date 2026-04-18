# BIT-323 Workspace Project Templates v1

Date: 2026-04-16
Owner: Product Development
Primary issue: [BIT-323 -- Set up workspace project templates for Product Development standard work and release trains](https://linear.app/bitpod-app/issue/BIT-323/set-up-workspace-project-templates-for-product-development-standard)

## Objective

Define the workspace project templates that are useful for the near-term Product Development project model without trying to encode the full team issue workflow into project templates.

## Recommended near-term templates

- `PD - Standard Project`
- `PD - Release Train`

Optional later, if usage justifies it:

- `PD - Design / Brand Campaign`

## What project templates should do

Project templates should help with project scaffolding:

- title structure
- default project description fields
- default project owners / members if available
- project-level labels or links if appropriate

They should not try to act like issue workflows.

## What project templates should not do

Project templates should not become a second copy of the team issue-status system.
They should not encode QA / PM gate truth.
They should not try to replace team-specific issue workflows.

## Decision rule

Create only the templates that reflect real near-term use.
Do not create a broad template set for a future team shape that is not active yet.

## Expected artifact

- one template-setup note under `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/`
- if created live, screenshots or equivalent proof of the template surface

## Validation checklist

- confirm whether workspace project templates are available and editable
- confirm template names are clear and non-overlapping
- confirm templates do not imply issue workflow behavior

## Escalate-back conditions

- templates are not available at the workspace level
- template sprawl would create more confusion than value
- the template surface cannot express the useful project scaffolding cleanly

