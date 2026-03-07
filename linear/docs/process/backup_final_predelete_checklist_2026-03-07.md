# Backup Final Pre-Delete Checklist (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod

## Completed gates

- [x] parity snapshot generated
- [x] uniqueness scan generated
- [x] docs/tools dedupe mapping generated
- [x] classification matrix drafted
- [x] cold archive tarball + checksum created
- [x] low-risk docs migration (`archive/learnings`) complete
- [x] low-risk docs migration (`archive/reference-candidates`) complete
- [x] preservation copy of `backup/docs/process` complete
- [x] destructive command plan drafted (not executed)

## Remaining decisions before full backup deletion

- [ ] Confirm whether `backup/tools/chatgpt-prompts/*` should be migrated into active canonical prompts path or left archived only.
- [ ] Confirm whether any remaining legacy `backup/tools/gpt_bridge/*` logs should be retained beyond cold archive.
- [ ] Explicit delete approval for full folder removal:
  - `/Users/cjarguello/bitpod-app-backup-2026-03-02`

## Immediate safe next command set (non-destructive)

```bash
# verify cold archive integrity
shasum -a 256 /Users/cjarguello/cold-archive/bitpod-backup-artifacts-2026-03-07.tgz
cat /Users/cjarguello/cold-archive/bitpod-backup-artifacts-2026-03-07.sha256
```

## Final destructive command (approval required)

```bash
rm -rf /Users/cjarguello/bitpod-app-backup-2026-03-02
```
