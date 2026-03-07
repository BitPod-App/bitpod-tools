# Post-UI Validation Command Bundle (2026-03-07)

Run after completing UI actions for:
- BIT-54 (Cloudflare token scope)
- BIT-55 (org avatar + pinned repos)

## 1) Load runtime token context

```bash
cd /Users/cjarguello/bitpod-app/bitpod
set -a; source .bitpod_runtime.env; set +a
```

## 2) Run combined verifier

```bash
/Users/cjarguello/bitpod-app/bitpod-tools/linear/scripts/post_ui_blockers_verify.sh /tmp/post_ui_blockers_verify_after_ui.md
```

## 3) Quick inspect results

```bash
sed -n '1,220p' /tmp/post_ui_blockers_verify_after_ui.md
```

## Pass criteria

- Cloudflare dns_records probe returns `"success":true`
- Pinned repos include:
  - `sector-feeds`
  - `bitpod-docs`
  - `bitpod-tools`
