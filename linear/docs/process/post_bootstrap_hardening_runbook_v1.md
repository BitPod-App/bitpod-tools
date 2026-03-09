# Post-Bootstrap Hardening Runbook v1

Issue: https://linear.app/bitpod-app/issue/BIT-32/post-bootstrap-hardening-plan-restricted-local-scope-dedicated-macos
Date: 2026-03-09

## Objective
After migration bootstrap, reduce Codex local filesystem scope to one canonical clone path and validate least-privilege behavior.

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
Use your local launcher and set working root only to canonical clone path, with no extra add-dir paths.

Canonical launch target:
- cwd = `/Users/cjarguello/bitpod-app`
- extra writable dirs = none

### 4) Verify restricted scope
Run these checks in the new restricted session:

```bash
# inside allowed path (should succeed)
touch /Users/cjarguello/bitpod-app/.scope_write_test && rm /Users/cjarguello/bitpod-app/.scope_write_test

# outside path read probe (should fail or be denied by policy)
cat ~/.zshrc

# outside path write probe (should fail or be denied by policy)
touch ~/Documents/.scope_should_fail
```

Capture outputs and record pass/fail.

### 5) Rollback command (if immediate unrestrict is needed)
Relaunch Codex in bootstrap mode with the previous broader directory allowlist used during migration.

## Evidence contract
- Status line with transition reason.
- Commands executed.
- Output snippets (sanitized).
- Decision (keep restricted / rollback temporary).

## Risk note
If restrictions are applied too early, migration automation and cross-repo operations may fail. Keep this in Phase 3 unless explicitly accelerated.
