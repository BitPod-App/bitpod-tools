# VeraQA Review Governance Reference v1

Status: Active rule-of-record  
Owner: BitPod GitHub governance / Vera QA lane  
Org: `BitPod-App`  
Source companions:

- [github_team_purpose_reviewer_routing_v1.md](./github_team_purpose_reviewer_routing_v1.md)
- [vera_qa_lane_contract_v1.md](./vera_qa_lane_contract_v1.md)

## Scope

This rule-of-record applies to active repositories in the `BitPod-App` GitHub org and to the main-branch pull-request review flow only.

It governs default reviewer routing, VeraQA tier-team membership expectations, main-branch review protection, and explicit temporary owner/admin bypass handling.

It does not replace product acceptance, implementation ownership, or the dedicated QA verdict contract in `vera_qa_lane_contract_v1.md`.

## Default reviewer routing

Default CODEOWNERS routing for active repos must be exactly:

```text
* @BitPod-App/veraqa-tier-1
```

Default reviewer routing must not point to:

- `@BitPod-App/core-maintainers`
- `@BitPod-App/code-maintainers`, if that team exists
- `@BitPod-App/qa-reviewers`

`veraqa-tier-1` is the default reviewer lane. `veraqa-tier-2` and `veraqa-tier-3-audit` are escalation lanes, not default routing targets.

## Default behavior

- T1 is the baseline/default PR review route.
- T2 is used only for score-based or manually approved escalation.
- T3 is used only for score-based high-risk escalation or periodic deep-audit sampling.
- Static branch protection should enforce code-owner review and one approving review; it should not encode maintainer teams as review gates.

## Team membership expectations

Expected VeraQA membership baseline:

- `vera-qa` is active in `veraqa-tier-1`.
- `vera-qa` is active in `veraqa-tier-2`.
- `vera-qa` is active in `veraqa-tier-3-audit`.

Maintainer-team review-gating constraints:

- `vera-qa` must not be active in `core-maintainers` as a review-gating workaround.
- `vera-qa` must not be active in `code-maintainers` if that team exists.
- `core-maintainers` and `code-maintainers` must not be used as default reviewer routing teams.

## Governance baseline

For every active repo main branch, branch protection should match:

```yaml
require_code_owner_reviews: true
required_approving_review_count: 1
restrictions: null
```

Ruleset baseline:

- Org rulesets are expected to be empty unless intentionally changed in this document.
- Repo rulesets are expected to be empty unless intentionally changed in this document.
- If org or repo rulesets are introduced, this file must be updated in the same change to state the intended ruleset names, targets, enforcement state, and VeraQA routing semantics.

## Override and bypass policy

Owner/admin bypass is allowed only as an explicit, temporary override.

Every bypass must be logged inline in this file before or immediately after use with:

- repo
- PR
- reason
- approver
- expected revalidation date
- closeout condition

A bypass is not closed until the closeout condition has been satisfied and the affected repo has been revalidated against this rule-of-record.

## Bypass log

No active bypasses are currently recorded.

| repo | PR | reason | approver | expected revalidation date | closeout condition | status |
|---|---|---|---|---|---|---|
| _none_ | _none_ | _none_ | _none_ | _none_ | _none_ | _closed_ |

## Validation command contract

Validation should check, in order:

1. CODEOWNERS default routing across all active repos.
2. VeraQA team membership and maintainer-team non-membership for `vera-qa`.
3. Main branch protection and org/repo ruleset drift.

Any failure must report the exact repo, branch, API path, or team membership endpoint that failed.
