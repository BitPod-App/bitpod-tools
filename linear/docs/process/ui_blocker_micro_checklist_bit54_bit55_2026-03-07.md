# UI Blocker Micro-Checklist (BIT-54 + BIT-55)

Date: 2026-03-07

Related issues:
- https://linear.app/bitpod-app/issue/BIT-54/email-auth-hardening-verify-dkim-selectors-and-enforce-dmarc-policy
- https://linear.app/bitpod-app/issue/BIT-55/org-profile-cleanup-pass-readmelogo-placeholderpinsdescriptions

## Task A (BIT-54): Cloudflare token scope fix (2-3 min)

1. Cloudflare -> **My Profile** -> **API Tokens** -> **Create Token**.
2. Choose **Create Custom Token**.
3. Permissions:
   - `Zone` -> `DNS` -> `Read` (required)
   - `Zone` -> `DNS` -> `Edit` (optional, only if we will update records by API)
4. Zone Resources: restrict to `bitpod.app` only.
5. Create token and copy once.
6. Put new token where BitPod runtime reads `CLOUDFLARE_API_TOKEN`.
7. Run verifier (Task C script below).

## Task B (BIT-55): Org profile UI finish (2-3 min)

1. GitHub org page: https://github.com/BitPod-App
2. Upload temporary placeholder logo/avatar.
3. Pin exactly 2 repos:
   - `sector-feeds`
   - `bitpod-tools`
4. Confirm org bio and descriptions are still clean.

## Task C: Post-UI validation (terminal)

Run:

```bash
/Users/cjarguello/bitpod-app/bitpod-tools/linear/scripts/post_ui_blockers_verify.sh
```

Expected:
- Cloudflare DNS-record probe returns success.
- GitHub org pinned repos include the two target repos.
- Markdown report path printed for evidence posting.
