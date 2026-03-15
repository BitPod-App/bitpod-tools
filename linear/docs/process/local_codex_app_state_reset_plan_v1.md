# Local Codex App-State Reset Plan v1

Issue: [BIT-102 — Complete T3 workspace parity, legacy root retirement, and repo-rename preparation](https://linear.app/bitpod-app/issue/BIT-102/complete-t3-workspace-parity-legacy-root-retirement-and-repo-rename)

## Purpose

Provide a restart-safe procedure for resetting local Codex desktop app state without guessing mid-session or corrupting active runtime state.

## Why this exists

The live local app-state file:

- `/Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex-global-state.json`

is actively rewritten by the desktop app. It still contains stale migration-era fields such as:

- environment label `bitpod`
- repo metadata for `cjarguello/bitpod`
- historical thread root hints for `/Users/cjarguello/bitpod-app/bitpod`

The active workspace roots are already current:

- `/Users/cjarguello/bitpod-app`

So the remaining problem is not workspace breakage. It is stale UI/app metadata.

## Current rule

- Do not hand-edit or remove `.codex-global-state.json` during an active session.
- Reset or regenerate it only in a fresh session window.

## Reset window prerequisites

1. No active Codex work that depends on restoring the current desktop thread state.
2. Current workspace changes committed or otherwise intentionally preserved.
3. User accepts that recent local UI history, pinned thread state, and historical root hints may be lost.

## Safe reset procedure

1. Close the active Codex desktop session or app window cleanly.
2. Backup the current file to a dated local-only path.
3. Reopen Codex with the same workspace root:
   - `/Users/cjarguello/bitpod-app`
4. Let Codex regenerate the file naturally.
5. Verify the regenerated file no longer points at:
   - `/Users/cjarguello/bitpod-app/bitpod`
   - `/Users/cjarguello/bitpod-app/tools`
   - `cjarguello/bitpod`
6. If regeneration is worse or breaks expected desktop behavior, restore from backup.

## Strong reset procedure

Use this only when the softer in-session cleanup is not enough and strict T3 cleanliness is required.

1. Close the active Codex desktop session or app window fully.
2. Backup the current file:

```bash
ts=$(date +%Y%m%d-%H%M%S)
backup_dir=/Users/cjarguello/bitpod-app/local-workspace/local-working-files/local-codex-app-state-backups
mkdir -p "$backup_dir"
cp /Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex-global-state.json \
  "$backup_dir/.codex-global-state.$ts.pre-strong-reset.json"
```

3. Remove the live app-state file:

```bash
rm /Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex-global-state.json
```

4. Reopen Codex on the workspace root:

```text
/Users/cjarguello/bitpod-app
```

5. Let Codex recreate the file naturally.
6. Re-check the recreated file with:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex-global-state.json')
obj=json.loads(p.read_text())
text=json.dumps(obj)
for n in ['cjarguello/bitpod','/Users/cjarguello/bitpod-app/bitpod','/Users/cjarguello/bitpod-app/tools']:
    print(n, text.count(n))
print('active-workspace-roots=', obj.get('active-workspace-roots'))
print('electron-saved-workspace-roots=', obj.get('electron-saved-workspace-roots'))
print('thread-workspace-root-hints=', obj.get('thread-workspace-root-hints'))
PY
```

7. If the recreated file still contains stale `environment.repo_map` metadata for `cjarguello/bitpod`, record that exact residue and do not pretend the strong reset succeeded fully.
8. If the recreated file is worse or the app behaves unexpectedly, restore the backup.

## Verification checklist

- `active-workspace-roots` contains only `/Users/cjarguello/bitpod-app`
- `electron-saved-workspace-roots` contains only `/Users/cjarguello/bitpod-app`
- no stale `thread-workspace-root-hints` remain for `/Users/cjarguello/bitpod-app/bitpod`
- no stale repo metadata remains for `cjarguello/bitpod`
- no stale sidebar or tool path references remain for `/Users/cjarguello/bitpod-app/tools`

## Current known residue after soft cleanup

As of the latest in-session cleanup:

- stale `thread-workspace-root-hints` for `/Users/cjarguello/bitpod-app/bitpod` were removed
- stale `sidebar-collapsed-groups` entry for `/Users/cjarguello/bitpod-app/tools` was removed
- the remaining meaningful stale item is the app-managed old repo metadata in:
  - `electron-persisted-atom-state.environment.repo_map`

## T3 interpretation

- Before reset: tolerated residue, but still a cleanliness objection
- After successful reset: this blocker can be treated as resolved for T3

## Non-goals

- This does not rename repos or package identifiers.
- This does not affect Git history, workspace files, or `local-trash-delete`.
- This does not unblock [BIT-104 — Execute Mac Mini guest-boundary bootstrap for OpenClaw execution node](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-guest-boundary-bootstrap-for-openclaw-execution-node) by itself; it only removes one remaining T3 cleanliness concern.
