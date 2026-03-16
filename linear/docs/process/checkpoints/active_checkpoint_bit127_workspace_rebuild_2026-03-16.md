# Active Checkpoint — BIT-127 workspace rebuild — 2026-03-16

## Lane

- active issue:
  - [BIT-127 — Rebuild Codex environment model, clean local org workspace, and execute repo-name normalization](https://linear.app/bitpod-app/issue/BIT-127/rebuild-codex-environment-model-clean-local-org-workspace-and-execute)
- canonical active root:
  - `/Users/cjarguello/BitPod-App`
- retired root:
  - `/Users/cjarguello/bitpod-app-retired-2026-03-16`
- primary active repo for this checkpoint artifact:
  - `/Users/cjarguello/BitPod-App/bitpod-tools`
- branch:
  - `codex/bit-127-retire-local-codex-architecture`

## Current state

- `demo-repository` retirement is complete locally and on GitHub.
- the active repo set is now `8` repos.
- cutover is complete:
  - old root archived read-only at `/Users/cjarguello/bitpod-app-retired-2026-03-16`
  - rebuild root moved into canonical `/Users/cjarguello/BitPod-App`
- the umbrella root is intentionally local-only and is **not** a git repo.
- full cleanup audit at the canonical root currently returns `T3 = PORCELAIN`.
- active workspace docs/scripts were normalized to canonical `BitPod-App` path casing after cutover.
- the stale Taylor handoff path bug was fixed so active runtime references point at `bitpod-taylor-runtime`, not the older `taylor-runtime` path.

## Explicit truth to preserve

- do **not** recreate a root `.git` at `/Users/cjarguello/BitPod-App`
- do **not** re-open `demo-repository` as part of the active repo set
- do **not** repeat cutover, archive creation, or GitHub deletion steps that are already done
- treat `local-codex` as historical state belonging to the retired root, not the active workspace model
- treat lowercase `/Users/cjarguello/bitpod-app` path references as historical drift unless intentionally preserved in archive/history artifacts

## Durable references

- recovered delete/retirement thread:
  - `/Users/cjarguello/bitpod-app-retired-2026-03-16/local-workspace/local-codex/sessions/2026/03/14/rollout-2026-03-14T18-58-29-019cef00-72ce-7b03-89d4-6a0de9d7a845.jsonl`
- key recovery anchors inside that thread:
  - delete instruction at line `14799`
  - BIT-127 follow-up verification comment save at line `14821`
  - final "fully retired from the active system" wrap-up at line `14825`
- BIT-127 comment proving GitHub-side deletion completed:
  - `comment-b685a594`
- post-cleanup baseline:
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/checkpoints/strict_cleanup_audit_pass_2026-03-15.md`
- pre-rename execution guidance:
  - `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/pre_rename_execution_branch_map_v1.md`
- canonical path contract:
  - `/Users/cjarguello/BitPod-App/bitpod-docs/process/canonical-path-contract.md`
- active repo registry:
  - `/Users/cjarguello/BitPod-App/bitpod-tools/config/repo_registry.tsv`

## Verified current state

- root `git status` failure is correct because `/Users/cjarguello/BitPod-App` is not meant to be a git repo
- `bitpod-tools` cleanup audit from the canonical root returns `PORCELAIN`
- current active registry aligns with the post-`demo-repository` 8-repo set
- only historical/archive artifacts should still mention `demo-repository` or old `local-codex` state
- repo-name normalization is **not** complete; no approved full rename map has been recorded yet

## Next actions

1. record the approved repo-name normalization map before renaming any additional GitHub repo slugs or local clone folders
2. keep BIT-127 focused on the remaining rename-normalization lane and any path/config cleanup that still affects the active operating surface
3. leave historical/archive evidence intact while updating only active docs, scripts, and config when drift is found
4. use this checkpoint plus the recovered March 14 delete thread as the starting context for any new Codex thread on BIT-127

## Blockers

- the remaining rename-normalization work is blocked on an explicit approved rename map
- do not guess canonical non-`bitpod-` target names where evidence is incomplete

## Resume prompt

```md
Resume from `/Users/cjarguello/BitPod-App`.

Active lane:
- [BIT-127 — Rebuild Codex environment model, clean local org workspace, and execute repo-name normalization](https://linear.app/bitpod-app/issue/BIT-127/rebuild-codex-environment-model-clean-local-org-workspace-and-execute)

Checkpoint artifact:
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/checkpoints/active_checkpoint_bit127_workspace_rebuild_2026-03-16.md`

Recovered thread to trust for the last pre-misconfiguration handoff:
- `/Users/cjarguello/bitpod-app-retired-2026-03-16/local-workspace/local-codex/sessions/2026/03/14/rollout-2026-03-14T18-58-29-019cef00-72ce-7b03-89d4-6a0de9d7a845.jsonl`

Verified current state:
- `demo-repository` retirement is complete locally and on GitHub
- active repo set is 8 repos
- cutover to `/Users/cjarguello/BitPod-App` is complete
- old root is archived read-only
- root is intentionally not a git repo
- current cleanup audit from the canonical root returns `T3 = PORCELAIN`
- active path/casing drift cleanup after cutover has already been applied

Next actions:
1. recover or approve the repo-name normalization map
2. execute only the approved rename work
3. keep historical/archive artifacts untouched unless the task is explicitly archival cleanup

Do not recreate a root `.git`, do not reintroduce `demo-repository`, and do not repeat already-completed cutover steps unless explicitly asked.
```
