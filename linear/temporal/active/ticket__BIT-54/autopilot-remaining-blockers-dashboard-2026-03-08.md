# Autopilot Remaining Blockers Dashboard (2026-03-08)

Scope: current blockers that require UI/operator action (cannot be completed purely from code/CLI in current context).

## Blocker 1 — BIT-54 (Cloudflare token scope)

Issue:
- https://linear.app/bitpod-app/issue/BIT-54/email-auth-hardening-verify-dkim-selectors-and-enforce-dmarc-policy

Current state:
- Zone lookup works.
- `dns_records` API probe fails with auth error `10000`.

Action needed:
- Rotate/create token with `Zone -> DNS -> Read` for `bitpod.app`.

Post-action verify:
```bash
cd /Users/cjarguello/BitPod-App/bitpod
set -a; source .bitpod_runtime.env; set +a
/Users/cjarguello/BitPod-App/bitpod-tools/linear/scripts/post_ui_blockers_verify.sh /tmp/post_ui_blockers_verify_after_cf_scope.md
```

## Blocker 2 — BIT-55 (Org profile UI pin/avatar)

Issue:
- https://linear.app/bitpod-app/issue/BIT-55/org-profile-cleanup-pass-readmelogo-placeholderpinsdescriptions

Current state:
- Public profile README live.
- Org name + bio set.
- `sector-feeds` and `bitpod-tools` now public.
- Pins currently empty.

Action needed:
- In GitHub org UI, pin exactly:
  - `sector-feeds`
  - `bitpod-tools`
- Optional: upload placeholder avatar.

Post-action verify:
```bash
/Users/cjarguello/BitPod-App/bitpod-tools/linear/scripts/post_ui_blockers_verify.sh /tmp/post_ui_blockers_verify_after_pins.md
```

## Blocker 3 — BIT-50 (Final destructive approval)

Issue:
- https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod

Current state:
- Non-destructive gates are complete.
- Final backup deletion is approval-gated.

Action needed:
- Explicit approval before executing:
```bash
rm -rf /Users/cjarguello/BitPod-App-backup-2026-03-02
```

Post-action verify:
```bash
test -d /Users/cjarguello/BitPod-App-backup-2026-03-02 && echo STILL_EXISTS || echo REMOVED
```
