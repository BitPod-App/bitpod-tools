# Personal GitHub Lockdown Execution Checklist (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove

Objective: remove BitPod AI/runtime exposure from CJ personal account while preserving org functionality.

## Phase A — Pre-check

1. Confirm org-level app path is active:

```bash
gh api /orgs/BitPod-App/installations --jq '.installations[] | [.id,.app_slug,.repository_selection,.account.login] | @tsv'
```

Expected: `chatgpt-codex-connector` installed for `BitPod-App`.

2. Capture current CLI auth scopes:

```bash
gh auth status
```

## Phase B — Personal account UI cleanup

GitHub (personal account) -> Settings -> Applications

- Authorized GitHub Apps: revoke non-human app links not required for personal use.
- Authorized OAuth Apps: revoke non-human runtime/automation clients.

GitHub (personal account) -> Settings -> Developer settings -> Personal access tokens

- Revoke legacy automation PATs.
- Keep only human-needed PATs with least scope.

## Phase C — Org-only verification

Run after each revoke batch:

```bash
# org repos still reachable
gh repo list BitPod-App --limit 200 --json name,visibility,url --jq '.[] | [.name,.visibility,.url] | @tsv'

# read one PR as harmless integration proof
gh pr list -R BitPod-App/bitpod-tools --limit 5 --json number,title,state,url --jq '.[] | [.number,.state,.title,.url] | @tsv'
```

Expected: commands succeed without using personal-only app paths.

## Phase D — Final state declaration

- Personal account no longer has AI/runtime app authorizations for BitPod operations.
- Org app installation remains functional.
- Evidence posted in BIT-49 with timestamps and revoked app/token IDs (no secrets).

## Fail-safe

If org access breaks after revoke:

1. Stop further revocations.
2. Re-authorize only the minimum org-scoped integration required.
3. Re-run Phase C before proceeding.
