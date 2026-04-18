# BIT-319 Product Development Blocker Cleanup Proposal v1

Date: 2026-04-15
Owner: Product Development
Primary issue: [BIT-319 — Product Development blocker cleanup toward native dependencies + minimal blocker taxonomy](https://linear.app/bitpod-app/issue/BIT-319/product-development-blocker-cleanup-toward-native-dependencies-minimal)

## Objective

Reduce blocker ambiguity in the Product Development team without causing silent breakage.

Near-term goal:

- native Linear dependencies become the default blocker surface for issue-to-issue blocking
- non-ticket blockers converge toward a much smaller taxonomy
- merge-readiness truth stops depending on a sprawling blocker-label surface

## Current live snapshot

Observed blocker label group:

- `Blocked By`

Observed live blocker labels:

- `needs-estimate`
- `needs-CTO`
- `needs-other`
- `needs-type`
- `needs-decision`
- `needs-specs`
- `needs-pm`
- `needs-discussion`

## Problem

The current blocker surface mixes together three different things:

1. readiness failures
- `needs-type`
- `needs-estimate`
- `needs-specs`

2. operator/decision dependencies
- `needs-pm`
- `needs-decision`
- `needs-discussion`
- `needs-CTO`

3. generic unresolved blockers
- `needs-other`

This creates four problems:

- issue-to-issue blockers can be hidden inside labels instead of native dependencies
- merge-readiness logic has to interpret too many blocker variants
- some labels are really intake/readiness corrections, not durable blockers
- the taxonomy invites more labels later

## Proposed target model

### A. Native dependencies first

Use native Linear `blocked by` relations whenever:

- issue A depends on issue B
- a design issue blocks an implementation issue
- a release issue depends on specific child issues
- any other blocker is best represented by another issue

### B. Keep temporary readiness labels only where they serve the Ready gate

These still have practical value at the gate:

- `needs-type`
- `needs-estimate`
- `needs-specs`

Reason:

- the current engine already uses them for fail-closed readiness rollback
- removing them immediately would create avoidable churn

### C. Collapse the rest toward one generic non-ticket blocker signal

Long-term target:

- one generic `blocked` label

Meaning:

- issue is blocked by a non-ticket condition
- required reason must be recorded in a comment

This generic label should replace:

- `needs-CTO`
- `needs-pm`
- `needs-decision`
- `needs-discussion`
- `needs-other`

## Migration shape

### Phase 1: doctrine and engine awareness

Already aligned or partially aligned:

- repo doctrine now says native dependencies should be preferred
- engine merge-readiness logic now treats blocker signals more strictly

### Phase 2: live workspace prep

Before deleting or renaming blocker labels:

1. inventory active issues currently using each blocker label
2. determine which labels are still used by bot logic vs only by humans
3. confirm no hidden automation is recreating labels
4. confirm native dependency cleanup is trustworthy enough given the current MCP/UI truth boundary

### Phase 3: live cleanup

Recommended order:

1. keep `needs-type`, `needs-estimate`, `needs-specs`
2. create one generic `blocked` label
3. move active non-ticket blockers onto `blocked` with required reason comments
4. remove or archive:
   - `needs-CTO`
   - `needs-pm`
   - `needs-decision`
   - `needs-discussion`
   - `needs-other`

### Phase 4: enforcement tightening

After the live cleanup lands:

- update engine/config to stop depending on the retired blocker labels
- make merge-readiness check:
  - native dependencies
  - `blocked`
  - readiness-failure labels only where still appropriate

## Risks

### Risk 1: hidden automation recreates old labels

Mitigation:

- inspect creation sources before deleting the labels

### Risk 2: active issues lose blocker meaning during migration

Mitigation:

- migrate active issues before label deletion
- require reason comments on new `blocked` usage

### Risk 3: readiness-failure labels are mixed up with durable blockers

Mitigation:

- explicitly keep `needs-type`, `needs-estimate`, `needs-specs` as readiness correction labels in the near term
- do not force them into the generic `blocked` bucket yet

### Risk 4: MCP/UI mismatch on blocker relations

Mitigation:

- use the Linear UI as canonical for relation cleanup
- document any mismatch explicitly in the lane evidence

## Recommendation

Do not jump straight from the current `Blocked By` group to deletion.

Recommended truthful path:

1. keep the current readiness labels
2. create one generic `blocked` label for non-ticket blockers
3. move human/operator blocker reasons onto `blocked`
4. prefer native dependencies for issue-to-issue blocking
5. retire the extra human blocker labels only after usage and recreation sources are proven safe

## Expected validation evidence

- screenshot of current blocker label group before changes
- inventory of active issues using each blocker label
- screenshot of new `blocked` label if created
- proof that at least one issue-to-issue blocker is represented natively
- proof that merge-readiness logic still fails closed when blocker truth is present
