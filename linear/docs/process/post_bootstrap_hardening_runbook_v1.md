# Post-Bootstrap Hardening Runbook v1

Issue: https://linear.app/bitpod-app/issue/BIT-32/post-bootstrap-hardening-plan-restricted-local-scope-dedicated-macos
Date: 2026-03-09

## Objective
After migration bootstrap, reduce Codex local filesystem scope to one canonical clone path and validate least-privilege behavior.

## Security reality check
- `codex app /Users/cjarguello/bitpod-app` is a valid workspace relaunch command.
- Opening Codex on one workspace path is a convenience boundary, not a strong local read-isolation boundary by itself.
- The strong boundary is a dedicated macOS user/profile for Codex, with no personal iCloud mounts or unrelated working directories exposed.
- Do not execute this runbook until CJ explicitly says: `START HARDENING`.

## Phase boundary
- Do **not** execute this during active bootstrap/migration cutover windows.
- Execute only after migration owner approves hardening window.

## Inputs
- Canonical clone path (example):
  - `/Users/cjarguello/bitpod-app`

## Procedure

### 1) Snapshot current capability state
```bash
pwd
codex mcp list
gh auth status
```

### 2) Stop active Codex desktop sessions
- Close current Codex app windows/sessions.
- Ensure no background task is still executing migration edits.

### 3) Relaunch Codex with restricted local scope
Use the verified CLI launcher:

```bash
codex app /Users/cjarguello/bitpod-app
```

Target state:
- workspace root = `/Users/cjarguello/bitpod-app`
- extra allowed directories = none
- current migration/bootstrap session closed before relaunch

### 3.1) Strong-isolation upgrade path
If post-relaunch probes still show outside-path access, move Codex into a dedicated macOS user/profile before resuming normal work.

Minimum dedicated-user requirements:
- no personal iCloud/Docs/Desktop mounts
- no non-BitPod repo clones in the home directory
- Codex launched only against `/Users/cjarguello/bitpod-app`

### 4) Verify restricted scope
Run the automated probe in the new restricted session:

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools
bash linear/scripts/post_bootstrap_scope_probe.sh \
  /Users/cjarguello/bitpod-app \
  /tmp/post_bootstrap_scope_probe.md
```

Expected interpretation:
- write inside clone root = `allowed`
- read `~/.zshrc` = `denied`
- write `~/Documents` = `denied`

Artifact:
- `/tmp/post_bootstrap_scope_probe.md`

### 5) Rollback command (if immediate unrestrict is needed)
Relaunch Codex in bootstrap mode against the broader BitPod workspace root:

```bash
codex app /Users/cjarguello/bitpod-app
```

If dedicated-user mode was enabled for hardening, rollback means returning to the original migration user/profile temporarily.

## Evidence contract
- Status line with transition reason.
- Commands executed.
- Output snippets or probe artifact (sanitized).
- Decision (keep restricted / rollback temporary).

## Risk note
If restrictions are applied too early, migration automation and cross-repo operations may fail. Keep this in Phase 3 unless explicitly accelerated.
