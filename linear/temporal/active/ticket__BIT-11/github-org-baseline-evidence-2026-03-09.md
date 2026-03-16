# GitHub Org Baseline Evidence (Snapshot)

Timestamp (UTC): 2026-03-09T08:03:29Z
Org: BitPod-App
Implements: BIT-11
Spec reference: `linear/protocol/configs/github-org-baseline-policy-v1.md`

## Org Controls Snapshot

| Control | Observed Value | Source |
|---|---|---|
| default_repository_permission | none | `gh api /orgs/BitPod-App` |
| members_can_create_repositories | false | `gh api /orgs/BitPod-App` |
| members_allowed_repository_creation_type | none | `gh api /orgs/BitPod-App` |
| members_can_delete_repositories | false | `gh api /orgs/BitPod-App` |
| two_factor_requirement_enabled | true | `gh api /orgs/BitPod-App` |
| dependabot_alerts_enabled_for_new_repositories | true | `gh api /orgs/BitPod-App` |
| dependabot_security_updates_enabled_for_new_repositories | true | `gh api /orgs/BitPod-App` |
| dependency_graph_enabled_for_new_repositories | true | `gh api /orgs/BitPod-App` |
| advanced_security_enabled_for_new_repositories | false | `gh api /orgs/BitPod-App` |
| secret_scanning_enabled_for_new_repositories | false | `gh api /orgs/BitPod-App` |
| secret_scanning_push_protection_enabled_for_new_repositories | false | `gh api /orgs/BitPod-App` |

## Baseline Assessment

| Control | Target | Observed | Result |
|---|---|---|---|
| default repository permission | none | none | PASS |
| member repo creation disabled | false | false | PASS |
| member repo deletion disabled | false | false | PASS |
| org-wide 2FA | true | true | PASS |
| private-by-default policy | yes | yes | PASS |
| public repo exception policy | explicit approvals only | `sector-feeds`, `bitpod-tools`, `.github`, `bitpod-assets` are public by owner decision | PASS |

## Teams Snapshot

| Team | Permission | Privacy |
|---|---|---|
| automation | push | closed |
| core-maintainers | push | closed |
| readers | pull | closed |

## Repositories Snapshot

| Repo | Visibility |
|---|---|
| sector-feeds | public |
| bitpod-tools | public |
| .github | public |
| bitpod-assets | public |
| bitpod-docs | private |
| bitpod-taylor-runtime | private |
| bitregime-core | private |
| linear | private |
| demo-repository | private |

## Notes

- This snapshot supersedes the 2026-03-06 evidence file for current org state.
- Public repos are intentional and policy-compliant under explicit exception approval.
- Advanced Security / secret scanning org defaults are plan-dependent and not required for current Phase 1 minimum baseline.
