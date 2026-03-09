# Backup Cleanup Execution Plan (Destructive Step Prep) — 2026-03-07

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod

## Scope

This plan prepares final destructive cleanup for backup workspace after all non-destructive gates are satisfied.

Current satisfied gates:
- parity snapshot
- uniqueness scan
- dedupe mapping
- classification matrix
- cold archive + checksum
- low-risk docs migration completed

## Destructive candidates (from classification)

Drop candidates:
- `/Users/cjarguello/bitpod-app-backup-2026-03-02/bitpod/.venv*`
- `/Users/cjarguello/bitpod-app-backup-2026-03-02/tools/costs/__pycache__`
- `/Users/cjarguello/bitpod-app-backup-2026-03-02/tools/gpt_bridge/.env`
- `/Users/cjarguello/bitpod-app-backup-2026-03-02/App Downloads` (empty)

Archive-only (already covered by cold archive):
- artifacts buckets under backup root, `taylor-runtime`, `bitpod`, `bitregime-core`

## Dry-run verification (non-destructive)

```bash
# confirm targets exist before deletion
ls -ld /Users/cjarguello/bitpod-app-backup-2026-03-02/bitpod/.venv* || true
ls -ld /Users/cjarguello/bitpod-app-backup-2026-03-02/tools/costs/__pycache__ || true
ls -l  /Users/cjarguello/bitpod-app-backup-2026-03-02/tools/gpt_bridge/.env || true
ls -ld /Users/cjarguello/bitpod-app-backup-2026-03-02/App\ Downloads || true
```

## Destructive commands (execute only after explicit approval)

```bash
rm -rf /Users/cjarguello/bitpod-app-backup-2026-03-02/bitpod/.venv*
rm -rf /Users/cjarguello/bitpod-app-backup-2026-03-02/tools/costs/__pycache__
rm -f  /Users/cjarguello/bitpod-app-backup-2026-03-02/tools/gpt_bridge/.env
rmdir  /Users/cjarguello/bitpod-app-backup-2026-03-02/App\ Downloads || true
```

## Final backup removal (separate explicit approval)

Only after verifying post-cleanup parity and confirming no unresolved REVIEW items:

```bash
rm -rf /Users/cjarguello/bitpod-app-backup-2026-03-02
```

## Post-delete verification

```bash
test -d /Users/cjarguello/bitpod-app-backup-2026-03-02 && echo STILL_EXISTS || echo REMOVED
```
