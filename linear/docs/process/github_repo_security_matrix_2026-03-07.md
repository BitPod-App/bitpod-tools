# GitHub Repo Security Controls Matrix (BIT-25)

Date: 2026-03-07
Org: `BitPod-App`

## Target controls

- Dependabot security updates: enabled
- Secret scanning: enabled
- Secret scanning push protection: enabled
- Dependency graph / code security: best-effort (plan-dependent)
- Branch protection / rulesets: consistent baseline required

## Current repo-by-repo state

| Repo | Dependabot Sec Updates | Secret Scanning | Push Protection | Code Security | Branch Protection on `main` | Rulesets |
|---|---:|---:|---:|---:|---:|---|
| `bitpod-tools` | enabled | enabled | enabled | disabled | no | none |
| `sector-feeds` | enabled | enabled | enabled | disabled | no | `Basic Main Rules` (0 rules) |
| `linear` | enabled | enabled | enabled | disabled | no | none |
| `bitpod-docs` | enabled | enabled | enabled | disabled | no | none |
| `bitregime-core` | enabled | enabled | enabled | disabled | no | none |
| `bitpod-taylor-runtime` | enabled | enabled | enabled | disabled | no | none |

## Commands used

```bash
# State snapshot
gh repo list BitPod-App --limit 200 --json name --jq '.[].name'

# Apply security_and_analysis
gh api -X PATCH /repos/BitPod-App/<repo> \
  -f security_and_analysis[secret_scanning][status]=enabled \
  -f security_and_analysis[secret_scanning_push_protection][status]=enabled \
  -f security_and_analysis[dependabot_security_updates][status]=enabled

# Verify
for r in <repos>; do
  gh api /repos/BitPod-App/$r --jq '{name,security_and_analysis}'
  gh api /repos/BitPod-App/$r/branches/main/protection
  gh api /repos/BitPod-App/$r/rulesets
 done
```

## Findings

1. Security analysis controls were enabled successfully on all repos for Dependabot + Secret Scanning + Push Protection.
2. `code_security` remains disabled on all repos (likely plan/feature-level constraint).
3. Branch protection consistency is not yet established:
   - No branch protection on `main` for all repos.
   - One repo (`sector-feeds`) has an active ruleset with zero rules.

## Proposed safe next action

Define a minimal org-wide branch baseline in BIT-25 before applying:
- Require PR for `main`
- Block force-push on `main`
- Keep bypass for org owners initially (to avoid migration deadlocks)

Then apply consistently across all six repos and re-run this matrix.
