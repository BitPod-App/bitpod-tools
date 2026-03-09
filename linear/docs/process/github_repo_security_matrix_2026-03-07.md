# GitHub Repo Security Controls Matrix (BIT-25)

Date: 2026-03-07
Org: `BitPod-App`

## Applied baseline

- Dependabot security updates: enabled
- Secret scanning: enabled
- Secret scanning push protection: enabled
- Branch protection on `main`: enabled
  - Require pull request reviews: yes (1 approval)
  - Enforce admins: no (owner bypass allowed in Phase 1)
  - Allow force pushes: no
  - Allow deletions: no
- Rulesets: no empty/inert rulesets remaining

## Repo-by-repo final state

| Repo | Dependabot Sec Updates | Secret Scanning | Push Protection | Main protected | PR approvals required | Force push blocked | Deletion blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| `bitpod-tools` | enabled | enabled | enabled | yes | 1 | yes | yes |
| `sector-feeds` | enabled | enabled | enabled | yes | 1 | yes | yes |
| `linear` | enabled | enabled | enabled | yes | 1 | yes | yes |
| `bitpod-docs` | enabled | enabled | enabled | yes | 1 | yes | yes |
| `bitregime-core` | enabled | enabled | enabled | yes | 1 | yes | yes |
| `bitpod-taylor-runtime` | enabled | enabled | enabled | yes | 1 | yes | yes |

## Notes

- `code_security` remains disabled in API responses; treated as plan/feature-gated and excluded from Phase 1 pass criteria.
- Removed stale empty ruleset from `sector-feeds` (`Basic Main Rules`, 0 rules).

## Verification commands

```bash
repos=$(gh repo list BitPod-App --limit 200 --json name --jq '.[].name')
for r in $repos; do
  gh api /repos/BitPod-App/$r --jq '{name,security_and_analysis}'
  gh api /repos/BitPod-App/$r/branches/main/protection --jq '{allow_force_pushes,allow_deletions,enforce_admins}'
  gh api /repos/BitPod-App/$r/branches/main/protection/required_pull_request_reviews --jq '{required_approving_review_count}'
  gh api /repos/BitPod-App/$r/rulesets
 done
```
