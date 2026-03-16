# GitHub Team Purpose, Reviewer Routing, and CJ Role Model v1

## Purpose

Define the intended purpose of current GitHub teams, the expected role of `cjarguello`, and the reviewer-routing model that should govern BitPod-App repos.

This exists because current review requests are routed only through `@BitPod-App/core-maintainers`, which creates avoidable confusion even though `cjarguello` already has full org and repo authority.

## Verified current state

### Teams

Current teams and repo permission levels:

- `core-maintainers` -> `push`
- `automation` -> `push`
- `readers` -> `pull`

### Reviewer routing

Current CODEOWNERS pattern across active repos:

```text
# BitPod baseline CODEOWNERS
* @BitPod-App/core-maintainers
```

Verified in:

- `bitpod-tools`
- `sector-feeds`
- `bitregime-core`
- `bitpod-docs`
- `bitpod-taylor-runtime`

### Branch protection

For active code repos:

- required approving reviews: `1`
- require code owner reviews: `false`
- enforce admins: `false`
- restrictions: `null`

Implication:

- review requests are *display-routed* through the team because CODEOWNERS names the team
- review approval is not technically limited to that team because code-owner review is not required
- `cjarguello` as org owner/repo admin can bypass and merge, but the UX still implies a team gate

### CJ role

Verified current role of `cjarguello`:

- direct org admin/owner authority
- `admin` permission on all current repos
- active maintainer in all current teams:
  - `core-maintainers`
  - `automation`
  - `readers`

## Problem statement

The current model causes three kinds of confusion:

1. review requests appear team-only even when `cjarguello` is the actual human reviewer
2. team names do not yet encode a clear operating purpose
3. governance and review UX are being inferred from defaults instead of intentionally designed

## Intended team purpose model

### `core-maintainers`

Purpose:

- codebase stewardship
- default review pool for protected repos
- maintainers trusted to approve routine code changes

This team should exist to represent the stable maintainer surface, not to obscure owner/admin authority.

### `automation`

Purpose:

- bot/app/service actors and future automation-specific access mapping
- non-human or automation-adjacent integration scope
- future repo/path restrictions for operational tooling

This team should not be the default human review lane.

### `readers`

Purpose:

- read-only org visibility
- documentation/reference access without write or merge expectations

This team should never be part of required review routing.

## Intended CJ role model

`cjarguello` should be treated as:

- org owner/admin
- repo admin across the org
- valid individual reviewer on all repos
- valid merger/bypass authority when governance or routing configuration is the blocker rather than code quality
- not forced to act “as a team” in the UI in order to review or merge

## Recommended reviewer-routing model

Use a hybrid model:

- keep `core-maintainers` as the default team review surface for shared repos
- also allow explicit individual review requests for `cjarguello` where needed
- do not rely on team-only routing when the practical reviewer/merger is known to be `cjarguello`

### Recommended CODEOWNERS baseline

Preferred baseline for active repos:

```text
# BitPod baseline CODEOWNERS
* @BitPod-App/core-maintainers @cjarguello
```

Why:

- keeps team-level maintainership visible
- makes individual reviewer routing explicit
- better matches actual operating behavior
- reduces fake blockers caused by UI ambiguity

## Merge authority rule

If branch protection does **not** require code owner review and `enforce_admins=false`, then owner/admin bypass is legitimate when:

- CI is green
- the code has been inspected
- the only blocker is reviewer-routing/governance UX
- a follow-up governance cleanup issue exists

This should be documented, not improvised.

## Recommended next config changes

1. update CODEOWNERS on active repos to include `@cjarguello`
2. keep `required_approving_review_count=1`
3. continue leaving `require_code_owner_reviews=false` unless a stricter model is intentionally adopted later
4. document when admin bypass is acceptable
5. revisit team naming/purpose again once more humans or true app actors exist

## Repo scope

This v1 spec applies to:

- `bitpod-tools`
- `sector-feeds`
- `bitregime-core`
- `bitpod-docs`
- `bitpod-taylor-runtime`
- `.github` as org profile/governance repo where relevant

## Out of scope

Not covered here:

- GitHub App non-CJ attribution implementation
- branch-per-repo custom governance variations
- enterprise-level org policy design
- future multi-human reviewer matrices
