# GitHub Org Baseline Evidence (Snapshot)

Timestamp (UTC): 2026-03-06T05:48:25Z
Refreshed (UTC): 2026-03-06T05:50:00Z
Org: BitPod-App

## Org Controls Snapshot

| Control | Observed Value | Source |
|---|---|---|
| default_repository_permission | none | gh api /orgs/BitPod-App |
| members_can_create_repositories | false | gh api /orgs/BitPod-App |
| members_can_delete_repositories | true | gh api /orgs/BitPod-App |
| members_allowed_repository_creation_type | none | gh api /orgs/BitPod-App |
| two_factor_requirement_enabled | false | gh api /orgs/BitPod-App |
| actions.enabled_repositories | all | gh api /orgs/BitPod-App/actions/permissions |
| actions.allowed_actions | all | gh api /orgs/BitPod-App/actions/permissions |

## Baseline Assessment

| Control | Target | Observed | Result |
|---|---|---|---|
| default_repository_permission | none | none | PASS |
| members_can_create_repositories | false | false | PASS |
| members_can_delete_repositories | false | true | FAIL |
| two_factor_requirement_enabled | true | false | FAIL |
| all repos private | true | true | PASS |

## Remediation Attempt Log

| UTC | Action | Result |
|---|---|---|
| 2026-03-06T05:50:xxZ | PATCH `/orgs/BitPod-App` with `members_can_delete_repositories=false` | No effective change (`true -> true`) |

## Repositories

| Repo | Private | Visibility | Archived | Default Branch |
|---|---:|---|---:|---|
| sector-feeds | true | private | false | main |
| bitregime-core | true | private | false | main |
| bitpod-tools | true | private | false | main |
| bitpod-taylor-runtime | true | private | false | main |
| bitpod-docs | true | private | false | main |
| linear | true | private | false | main |

## Notes

- This is an evidence snapshot; policy target values are defined in github_org_baseline_policy_v1.md.
- `members_can_delete_repositories` can be safely tightened without lockout risk.
- Enabling `two_factor_requirement_enabled` can remove members without 2FA and should be treated as a coordinated change.
- The API patch attempt for `members_can_delete_repositories` did not take effect; verify if this control is plan-restricted or requires UI-only path.
