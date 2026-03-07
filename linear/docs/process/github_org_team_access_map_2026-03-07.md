# GitHub Org Team Access Map (BIT-24)

Date: 2026-03-07
Org: `BitPod-App`
Scope: Least-privilege team scaffolding + repo grants

## Teams created

- `core-maintainers` (closed, base permission: push)
- `automation` (closed, base permission: push)
- `readers` (closed, base permission: pull)

## Repo grant matrix

| Team | Repos | Permission |
|---|---|---|
| `core-maintainers` | all org repos (`sector-feeds`, `bitregime-core`, `bitpod-tools`, `bitpod-taylor-runtime`, `bitpod-docs`, `linear`) | push |
| `readers` | all org repos (`sector-feeds`, `bitregime-core`, `bitpod-tools`, `bitpod-taylor-runtime`, `bitpod-docs`, `linear`) | pull |
| `automation` | `sector-feeds`, `bitpod-tools`, `bitpod-taylor-runtime` | push |

## Verification commands

```bash
gh api /orgs/BitPod-App/teams --paginate --jq '.[] | {slug,name,privacy,permission}'
gh api /orgs/BitPod-App/teams/core-maintainers/repos --paginate --jq '.[].name'
gh api /orgs/BitPod-App/teams/readers/repos --paginate --jq '.[].name'
gh api /orgs/BitPod-App/teams/automation/repos --paginate --jq '.[].name'
```

## Notes

- Repo rename impact handled: `bitpod` -> `sector-feeds`.
- This is Phase 1 baseline only; user/team membership assignment is tracked separately to avoid accidental over-grant.
