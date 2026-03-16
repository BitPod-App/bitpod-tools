# Backup Cold Archive Evidence (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod

## Archive creation

Command outcome:

- Archive created: `/Users/cjarguello/cold-archive/bitpod-backup-artifacts-2026-03-07.tgz`
- Checksum file: `/Users/cjarguello/cold-archive/bitpod-backup-artifacts-2026-03-07.sha256`

Included source buckets:

- `bitpod-app-backup-2026-03-02/artifacts`
- `bitpod-app-backup-2026-03-02/taylor-runtime/artifacts`
- `bitpod-app-backup-2026-03-02/bitpod/artifacts`
- `bitpod-app-backup-2026-03-02/bitregime-core/artifacts`

## Integrity

- SHA256: `c8e5de000af375a6e3650ba456c54e8ede379fb695ecfa18ef96c4fc63cf3ca5`
- Archive size: `538K`

## Interpretation

- Non-destructive retention prerequisite is now satisfied for artifact-heavy backup paths.
- Destructive cleanup remains blocked until migrate/review buckets are resolved and explicit delete approval is given.
