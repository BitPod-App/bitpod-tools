# Local Remotes & Git Operations Validation (BIT-14)

Date: 2026-03-07
Workspace root: `/Users/cjarguello/BitPod-App`

## Scope checked

Local clones validated:
- `/Users/cjarguello/BitPod-App/bitpod`
- `/Users/cjarguello/BitPod-App/bitpod-docs`
- `/Users/cjarguello/BitPod-App/bitpod-taylor-runtime`
- `/Users/cjarguello/BitPod-App/bitpod-tools`
- `/Users/cjarguello/BitPod-App/bitregime-core`

## Canonical remote normalization

Applied fix:
- Updated local `bitpod` origin to canonical `sector-feeds` URL:
  - `https://github.com/BitPod-App/sector-feeds.git`

## Remote + head verification

| Local clone | Origin URL | Remote default branch |
|---|---|---|
| `bitpod` | `https://github.com/BitPod-App/sector-feeds.git` | `main` |
| `bitpod-docs` | `https://github.com/BitPod-App/bitpod-docs.git` | `main` |
| `bitpod-taylor-runtime` | `https://github.com/BitPod-App/bitpod-taylor-runtime.git` | `main` |
| `bitpod-tools` | `https://github.com/BitPod-App/bitpod-tools.git` | `main` |
| `bitregime-core` | `https://github.com/BitPod-App/bitregime-core.git` | `main` |

## Git operation validation

Performed:
- `git remote -v`
- `git fetch origin --prune`
- `git ls-remote --symref origin HEAD`
- branch/upstream/status snapshot

Result:
- Fetch succeeded in all checked clones.
- Origin HEAD resolution succeeded in all checked clones.

## Path migration impact notes

- Local folder name `bitpod` remains as-is for now but now points to canonical repo `sector-feeds`.
- No destructive local path migrations were performed.
- Existing dirty working trees were preserved (no reset/cleanup performed):
  - `bitpod`
  - `bitpod-tools`
  - `bitpod-taylor-runtime` (minor untracked `.DS_Store`)

## Verification commands

```bash
# inventory
find /Users/cjarguello/BitPod-App -maxdepth 2 -type d -name .git | sed 's#/.git$##' | sort

# canonicalize old bitpod remote
 git -C /Users/cjarguello/BitPod-App/bitpod remote set-url origin https://github.com/BitPod-App/sector-feeds.git

# verify
for r in bitpod bitpod-docs bitpod-taylor-runtime bitpod-tools bitregime-core; do
  git -C /Users/cjarguello/BitPod-App/$r remote get-url origin
  git -C /Users/cjarguello/BitPod-App/$r ls-remote --symref origin HEAD | sed -n '1,2p'
done
```
