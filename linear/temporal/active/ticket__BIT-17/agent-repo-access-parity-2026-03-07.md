# Agent Repo Access + Linear↔GitHub Parity Verification (BIT-17)

Date: 2026-03-07

## Verified access

- GitHub auth active (`gh auth status`)
- Token scopes include: `admin:org`, `repo`, `workflow`, `user`, `gist`
- Org repo visibility includes all private BitPod repos with `viewerPermission=ADMIN`

## Verified write-path evidence

Recent commits pushed on active branch:
- `fb39fb9` (BIT-15 evidence)
- `a86fc04` (BIT-14 evidence)
- `db7e1b4` (BIT-27 evidence)
- `b07b631` (BIT-22 evidence)

Reference PR:
- https://github.com/BitPod-App/bitpod-tools/pull/6

## Linear↔GitHub parity check

Observed:
- BIT references present in several PR titles (e.g., `BIT-45`, `BIT-43`, `BIT-33`).
- However, bidirectional auto-cross-posting reliability is still inconsistent.

## Remaining auth/parity gaps

1. Reconnect/verify ChatGPT/Codex GitHub integration path (tracked in BIT-16).
2. Confirm automatic cross-post from manual Linear comments to related PR thread is functioning (or explicitly document as unavailable).

## Conclusion

- Repo read/write access: PASS
- Baseline parity linkage: PARTIAL
- Close condition for BIT-17: after BIT-16 reconnect proof and one successful cross-post parity confirmation.

## Commands used

```bash
gh auth status
gh repo list BitPod-App --limit 200 --json name,url,isPrivate,viewerPermission
gh search prs --owner BitPod-App --state open --limit 100 --json number,title,repository,url
gh pr view 6 --repo BitPod-App/bitpod-tools --json title,body,url,headRefName,baseRefName,state,commits
```
