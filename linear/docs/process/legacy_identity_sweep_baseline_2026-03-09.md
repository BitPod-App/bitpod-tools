# Legacy Identity Sweep Baseline — 2026-03-09

Issue: https://linear.app/bitpod-app/issue/BIT-31/legacy-identity-sweep-and-historical-ref-normalization

## Scope
- Active repos only (`bitpod`, `bitpod-tools`, `bitpod-docs`, `bitpod-taylor-runtime`, `bitregime-core`)
- Excluded generated/vendor dirs (`.git`, `node_modules`, cache/build dirs)

## Baseline counts
- `bitipod.com`: 2 files
- `bitipod`: 2 files
- `bitpod-public-permalinks`: 7 files

## Sample hits (first 25 each)
### bitipod.com
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md`
- `/Users/cjarguello/BitPod-App/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md`

### bitipod
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md`
- `/Users/cjarguello/BitPod-App/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md`

### bitpod-public-permalinks
- `/Users/cjarguello/BitPod-App/bitpod/CLOUDFLARE_PARANOID_PUBLIC_CHECKLIST.md`
- `/Users/cjarguello/BitPod-App/bitpod/bitpod/storage.py`
- `/Users/cjarguello/BitPod-App/bitpod/scripts/deploy_public_permalinks_pages.sh`
- `/Users/cjarguello/BitPod-App/bitpod/scripts/smoke_public.sh`
- `/Users/cjarguello/BitPod-App/bitpod/tests/test_storage.py`
- `/Users/cjarguello/BitPod-App/bitpod/transcripts/jack_mallers_show/jack_mallers_gpt_review_request.md`
- `/Users/cjarguello/BitPod-App/bitpod/transcripts/jack_mallers_show/jack_mallers_status.json`

## Handling policy
- Do not bulk-rewrite historical evidence docs.
- Prioritize active runtime/deploy/process docs that influence current behavior.
- Preserve historical references when they document true past state; annotate if needed.

