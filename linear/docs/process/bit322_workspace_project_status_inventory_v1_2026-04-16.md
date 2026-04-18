# BIT-322 Workspace Project Status Inventory v1

Date: 2026-04-16
Owner: Product Development
Primary issue: [BIT-322 -- Inventory workspace project statuses and define the coarse canonical model](https://linear.app/bitpod-app/issue/BIT-322/inventory-workspace-project-statuses-and-define-the-coarse-canonical)

## Objective

Inventory the current workspace project-status surface and define the coarse canonical model that should remain without mirroring the full team issue workflow.

## Observed current direction

Project statuses should stay coarse and workspace-level.

Recommended canonical model:

- `Backlog`
- `Planned`
- `In Progress`
- `Completed`
- `Canceled`

## Why this stays coarse

Project statuses are portfolio / coordination truth, not execution truth.
If project statuses become as detailed as team issue workflow statuses, the system gets duplicate lifecycle truth and confusion about which surface is authoritative.

## Inventory dimensions to capture

- current workspace project statuses
- which projects actually use each status
- whether any project automation depends on a status name
- whether any project view or report assumes detailed project states

## Decision rule

Keep detailed execution semantics in issue workflows.
Use project statuses only for broad project phase truth.

## Expected artifact

- one inventory/proposal note under `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/`

## Validation checklist

- capture the live project-status list
- identify any special-case usage
- confirm the canonical coarse model does not break existing project reporting

## Escalate-back conditions

- live projects depend on detailed statuses that would be lost
- project-status cleanup would silently change reporting or automation
- workspace/project status truth conflicts between UI and MCP

