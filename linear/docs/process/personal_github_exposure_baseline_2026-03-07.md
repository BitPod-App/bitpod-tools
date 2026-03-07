# Personal GitHub Exposure Baseline (BIT-49)

Related issue: https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove
Date: 2026-03-07

## Verified baseline (now)

- Active CLI auth account: `cjarguello`
- Token scopes: `admin:org`, `repo`, `workflow`, `user`, `gist`
- Org-level installed app on `BitPod-App`:
  - `chatgpt-codex-connector`
  - repository selection: `all`
  - permissions: actions/checks/contents/issues/metadata/pull_requests/statuses/workflows
- Org hardening controls confirmed:
  - `two_factor_requirement_enabled=true`
  - `members_can_delete_repositories=false`
  - `default_repository_permission=none`
  - `members_can_create_repositories=false`

## API limitation encountered

- `GET /user/installations` returned HTTP 403 with PAT auth context:
  - "You must authenticate with an access token authorized to a GitHub App..."
- Meaning: personal-account app-install inventory cannot be fully extracted with current PAT; use GitHub UI for complete personal authorized apps/OAuth review.

## UI checklist for final lock-down (Phase 3)

1. Personal account -> Settings -> Applications:
- Review **Authorized GitHub Apps**
- Review **Authorized OAuth Apps**
- Revoke entries not required for personal-only use.

2. Personal account -> Settings -> Developer settings -> Personal access tokens:
- Revoke tokens used by runtime/automation paths.
- Keep only human-required tokens (if any), with least scopes.

3. Org sanity check after each revoke:
```bash
gh repo list BitPod-App --limit 200 --json name,viewerPermission,url --jq '.[] | {name,viewerPermission,url}'
```

4. If org automation breaks:
- restore via org-scoped app/service identity instead of personal token.

## Completion gate for BIT-49

- No AI/runtime credential remains tied to personal GitHub account for BitPod operations.
- Evidence includes revoked app/token identifiers + timestamps.
- Core org automation smoke checks still pass.
