# Governance Parity Checklist (BIT-26)

Date: 2026-03-07
Org: `BitPod-App`

## Target files

- `.github/CODEOWNERS`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`

## Result matrix

| Repo | CODEOWNERS | SECURITY.md | CONTRIBUTING.md | PR template | bug template | feature template |
|---|---|---|---|---|---|---|
| `bitpod-tools` | yes | yes | yes | yes | yes | yes |
| `sector-feeds` | yes | yes | yes (pre-existing retained) | yes (pre-existing retained) | yes | yes |
| `linear` | yes | yes | yes | yes | yes | yes |
| `bitpod-docs` | yes | yes | yes | yes | yes | yes |
| `bitregime-core` | yes | yes | yes | yes | yes | yes |
| `bitpod-taylor-runtime` | yes | yes | yes | yes | yes | yes |

## Execution notes

- Applied **missing-only** policy to avoid overwriting existing governance customizations.
- Created baseline files directly via GitHub Contents API on `main` (admin bypass enabled in Phase 1 branch policy).
- Existing files in `sector-feeds` were intentionally preserved.

## Verification command

```bash
repos=$(gh repo list BitPod-App --limit 200 --json name --jq '.[].name')
for r in $repos; do
  for p in .github/CODEOWNERS SECURITY.md CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/bug_report.md .github/ISSUE_TEMPLATE/feature_request.md; do
    gh api /repos/BitPod-App/$r/contents/$p >/dev/null 2>&1 && echo "OK $r $p" || echo "MISS $r $p"
  done
done
```
