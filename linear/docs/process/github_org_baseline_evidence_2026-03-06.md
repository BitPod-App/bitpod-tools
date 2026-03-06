# GitHub Org Baseline Evidence (Snapshot)

Timestamp (UTC): 2026-03-06T05:48:25Z
Org: BitPod-App

## Org Controls Snapshot

| Control | Observed Value | Source |
|---|---|---|
| default_repository_permission | none | gh api /orgs/BitPod-App |
| members_can_create_repositories | unknown | gh api /orgs/BitPod-App |
| members_can_delete_repositories | true | gh api /orgs/BitPod-App |
| two_factor_requirement_enabled | unknown | gh api /orgs/BitPod-App |
| actions.enabled_repositories | all | gh api /orgs/BitPod-App/actions/permissions |
| actions.allowed_actions | all | gh api /orgs/BitPod-App/actions/permissions |

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
- Any unknown values require manual owner verification in GitHub UI.
