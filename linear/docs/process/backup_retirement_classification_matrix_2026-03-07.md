# Backup Retirement Classification Matrix (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod
Inputs:
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/backup_workspace_parity_snapshot_2026-03-07.md`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/backup_uniqueness_scan_2026-03-07.md`

## Action taxonomy

- **MIGRATE**: move into active canonical workspace now.
- **ARCHIVE**: keep in cold archive tarball for retention window.
- **DROP**: delete (noise/reproducible/generated).
- **REVIEW**: needs manual owner decision.

## Bucket classification

| Backup path/bucket | Signal | Proposed action | Target (if migrate) | Rationale |
|---|---|---|---|---|
| `backup/docs/archive/learnings/*` | historical docs | MIGRATE | `active/docs/archive/learnings/` | Knowledge artifacts likely still valuable. |
| `backup/docs/process/*` | process/canonical policy docs | REVIEW | `active/docs/process/` or `active/bitpod-tools/linear/docs/process/` | Potential overlap; requires dedupe to avoid conflicting canonicals. |
| `backup/tools/chatgpt-prompts/*` | prompt assets | REVIEW | `active/bitpod-tools/docs/` (or designated prompts dir) | Keep if still in use; otherwise archive. |
| `backup/tools/gpt_bridge/*` (excluding secrets) | bridge scripts/docs | REVIEW | `active/bitpod-tools/gpt_bridge/` | Some likely superseded by current branch changes. |
| `backup/tools/gpt_bridge/.env` | secret material | DROP | n/a | Never migrate raw secrets from legacy backup. |
| `backup/tools/gpt_bridge/logs/memory_store.jsonl` | runtime log artifact | ARCHIVE | n/a | Historical runtime state; keep in cold archive, do not migrate to active repo. |
| `backup/tools/artifacts/cost-meter/cost_events.jsonl` | generated metric artifact | ARCHIVE | n/a | Retain in cold archive only; avoid active-path pollution. |
| `backup/tools/costs/__pycache__/*` | compiled cache | DROP | n/a | Reproducible cache output; safe to delete. |
| `backup/taylor-runtime/artifacts/*` | runtime outputs/logs | ARCHIVE | n/a | Large historical run evidence; keep compressed if needed, not active workspace. |
| `backup/bitpod/.venv*` and `site-packages` | generated env deps | DROP | n/a | Reproducible local environments. |
| `backup/bitpod/artifacts/*` (legacy run outputs) | generated artifacts | ARCHIVE | n/a | Preserve briefly for auditability then drop. |
| `backup/bitregime-core/artifacts/*` | run artifacts | ARCHIVE | n/a | Non-source generated output. |
| `backup/App Downloads/*` | empty | DROP | n/a | No files present. |

## Proposed execution order

1. Migrate low-risk docs (`archive/learnings`) to active canonical docs path.
2. Produce dedupe review for `backup/docs/process` and `backup/tools/*` against current active files.
3. Build cold archive for runtime/artifact buckets.
4. Delete DROP buckets (`.venv*`, empty dirs, legacy secret files after secure wipe if needed).
5. Re-run parity check and finalize delete approval gate.

## Commands for archive/drop phase

```bash
# archive artifacts before deletion
cd /Users/cjarguello
mkdir -p cold-archive

tar -czf cold-archive/bitpod-backup-artifacts-2026-03-07.tgz \
  bitpod-app-backup-2026-03-02/artifacts \
  bitpod-app-backup-2026-03-02/taylor-runtime/artifacts \
  bitpod-app-backup-2026-03-02/bitpod/artifacts \
  bitpod-app-backup-2026-03-02/bitregime-core/artifacts

# sample destructive targets (after approval only)
rm -rf /Users/cjarguello/bitpod-app-backup-2026-03-02/bitpod/.venv*
rm -f  /Users/cjarguello/bitpod-app-backup-2026-03-02/tools/gpt_bridge/.env
```

## Gate before full backup removal

- Classification table approved.
- Required MIGRATE items copied and verified.
- ARCHIVE tarball exists and checksum recorded. (Done: see `backup_cold_archive_evidence_2026-03-07.md`)
- Explicit delete approval captured in BIT-50.
