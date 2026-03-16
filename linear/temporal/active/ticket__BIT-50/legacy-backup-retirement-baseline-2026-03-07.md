# Legacy Backup Retirement Baseline (BIT-50)

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod
Date: 2026-03-07

## Paths

- Active workspace: `/Users/cjarguello/BitPod-App`
- Legacy backup: `/Users/cjarguello/BitPod-App-backup-2026-03-02`

## Snapshot summary

- Both paths exist.
- File counts (quick):
  - Active: `4832`
  - Backup: `9144`
- Detailed parity artifact:
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/temporal/active/ticket__BIT-50/backup-workspace-parity-snapshot-2026-03-07.md`

## Top-level directory delta

Active-only notable dirs:
- `bitpod-docs`
- `bitpod-taylor-runtime`
- `bitpod-tools`

Backup-only notable dirs:
- `App Downloads`
- `artifacts`
- `taylor-runtime` (legacy naming)

## Git repo delta

Active git repos:
- root workspace repo
- `bitpod`
- `bitpod-docs`
- `bitpod-taylor-runtime`
- `bitpod-tools`
- `bitregime-core`

Backup git repos:
- `bitpod`
- `bitregime-core`
- `docs`
- `taylor-runtime`
- `tools`

Remote mismatch captured:
- Active `bitpod` remote now points to `BitPod-App/sector-feeds`.
- Backup `bitpod` remote still points to legacy `BitPod-App/bitpod`.

## Interpretation

- Backup contains legacy repos/paths not mirrored 1:1 by name in active workspace.
- Deletion is not yet safe without explicit parity confirmation for:
  - `backup/docs` vs active canonical docs locations
  - `backup/tools` vs active `bitpod-tools` + root `tools`
  - `backup/taylor-runtime` vs active `bitpod-taylor-runtime`
  - backup-only `artifacts` and `App Downloads`

## Safe delete gate (must pass)

1. Confirm no required files remain unique to backup-only paths.
2. Create optional cold archive (`tar`/external) if retention desired.
3. Obtain explicit delete approval.
4. Delete backup path and verify absence.

## Commands used

```bash
find /Users/cjarguello/BitPod-App -maxdepth 2 -type d -name .git
find /Users/cjarguello/BitPod-App-backup-2026-03-02 -maxdepth 2 -type d -name .git
find <path> -type f | wc -l
```
