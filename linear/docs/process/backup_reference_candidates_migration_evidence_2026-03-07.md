# Backup Reference-Candidates Migration Evidence (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod

## Scope

Non-destructive migration of backup reference-candidates docs into active workspace namespaced archive path.

- Source: `/Users/cjarguello/BitPod-App-backup-2026-03-02/docs/archive/reference-candidates`
- Destination: `/Users/cjarguello/BitPod-App/docs/archive/backup-2026-03-02/reference-candidates`

## Method

```bash
mkdir -p /Users/cjarguello/BitPod-App/docs/archive/backup-2026-03-02/reference-candidates
rsync -av --ignore-existing \
  /Users/cjarguello/BitPod-App-backup-2026-03-02/docs/archive/reference-candidates/ \
  /Users/cjarguello/BitPod-App/docs/archive/backup-2026-03-02/reference-candidates/
```

## Result

- Source file count: `1`
- Destination file count: `1`
- Rsync log: `/tmp/bit50_reference_candidates_rsync.log`

## Notes

- No overwrite (`--ignore-existing`).
- Namespaced destination preserves provenance and avoids canonical-path collisions.
