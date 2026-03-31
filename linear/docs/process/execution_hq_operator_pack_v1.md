# Execution HQ Operator Pack v1

Status: supporting operator detail, partially superseded for current setup truth

Current decision/sequence source of truth:
- [AI HQ Semi-Initial Setup Plan v2](../../../../bitpod-docs/process/ai-hq-semi-initial-setup-plan-v2.md)

Archived original preserved at:
- `../../../../bitpod-docs/archive/legacy-context/execution-hq/execution_hq_operator_pack_v1.md`

Use this v1 pack only where it stays consistent with the v2 setup plan. If
there is any conflict on sequence, blockers, or boundary interpretation, v2
wins.

Drift corrections applied to this live v1 copy:
- treat the repo clone list below as a 2026-03-22 snapshot, not as current
  canonical workspace composition
- do not treat `python3 -m taylor --help` as the locked smoke command without
  re-validating it against the active runtime surface
- use the current [BIT-139 — Stage legacy secret retirement and 1Password cutover for AI HQ agent operations](https://linear.app/bitpod-app/issue/BIT-139/stage-legacy-secret-retirement-and-1password-cutover-for-ai-hq-agent) framing from v2, not the older wording preserved in the archived copy

Date: 2026-03-22
Primary issue: [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)

## Purpose

Give the operator a single practical pack for the semi-initial Mac Mini /
Execution HQ bootstrap pass.

Use this note for the actual step order. Use
`execution_hq_architecture_decisions_v1.md` for the boundary and policy
decisions.

For the Phase 4 operator-side contract that sits on top of this machine
bootstrap lane, use:

- `openclaw_operator_intake_dispatch_contract_v1.md`

## Machine Split

### MacBook control console

What stays here:

- terminal shell used to reach the Mac Mini
- GitHub and PR management
- human-facing 1Password access
- planning, review, and remote-control coordination

What does not stay here:

- the primary Execution HQ workspace
- the primary NemoClaw runtime
- machine-local runtime state that belongs to the Mac Mini execution account

### Mac Mini admin account

Default account:

- `cjarguello`

What it is for:

- maintenance
- account creation
- recovery
- machine-level admin tasks

What it is not for:

- normal Taylor01 execution work
- primary HQ workspace ownership

### Mac Mini execution account

Default account:

- `taylorhq`

Acceptable alternate only if already chosen on-machine:

- `taylor01`

What lives here:

- rebuilt `bitpod-app` workspace cloned from GitHub
- NemoClaw/OpenShell runtime
- machine-local env files and runtime dependencies
- the active execution path for Taylor01 and related HQ work

## Minimal MacBook Tooling

Required:

1. Terminal or iTerm2
2. `ssh`
3. `git`
4. `gh`
5. 1Password

Helpful:

- `tmux`
- `rsync`
- Tailscale

## Scripted Entry Points

Use these helpers from the MacBook control console:

1. Preflight the local operator surface:

```bash
bash bitpod-tools/linear/scripts/execution_hq_preflight.sh
```

2. Probe remote reachability once an AI HQ host or ssh alias exists:

```bash
AI_HQ_HOST="<host-or-alias>" \
bash bitpod-tools/linear/scripts/execution_hq_remote_bootstrap.sh probe
```

3. Reset the execution-account workspace from GitHub:

```bash
AI_HQ_HOST="<host-or-alias>" \
AI_HQ_EXEC_USER="taylorhq" \
bash bitpod-tools/linear/scripts/execution_hq_remote_bootstrap.sh reset-workspace
```

4. Verify the rebuilt execution-account workspace:

```bash
AI_HQ_HOST="<host-or-alias>" \
AI_HQ_EXEC_USER="taylorhq" \
bash bitpod-tools/linear/scripts/execution_hq_remote_bootstrap.sh verify-workspace
```

5. Run the first remote smoke command once the runtime exists:

```bash
AI_HQ_HOST="<host-or-alias>" \
AI_HQ_EXEC_USER="taylorhq" \
AI_HQ_SMOKE_CMD="python3 -m taylor --help" \
bash bitpod-tools/linear/scripts/execution_hq_remote_bootstrap.sh smoke
```

Treat the smoke command above as a historical example only. Reconcile it
against the active NemoClaw/OpenShell runtime surface before use.

The scripts are intentionally honest:

- they do not invent a host target
- they do not fake account creation
- they fail closed if ssh reachability or the workspace shape is not real yet

## Workspace Variables

Use these defaults inside the execution-account shell unless a ticket says
otherwise:

```bash
export WORKSPACE="${WORKSPACE:-$HOME/bitpod-app}"
```

On the Mac Mini execution account, this means the rebuilt workspace normally
lives at:

```bash
$HOME/bitpod-app
```

Do not hard-code `/Users/cjarguello/...` in new live operator steps unless the
step is explicitly recording a current-machine fact tied to the maintenance
account.

## First Bootstrap Sequence

1. Confirm the MacBook source workspace already passed full forced
   `cleanup-audit T3` with `result=PORCELAIN`.
2. Open a remote shell from the MacBook to the Mac Mini admin account.
3. Create or verify the dedicated execution account.
4. Open the actual working shell in the execution account.
5. Delete the stale workspace under the execution account only.
6. Rebuild the execution-account workspace only from GitHub clones.
7. Confirm the new workspace exists and is separate from the MacBook
   `local-workspace/`.
8. Install the runtime dependencies and only the minimal temporary secret
   baseline needed for first smoke proof.
9. Install or validate NemoClaw/OpenShell under the execution account.
10. Run the first simple HQ smoke workflow inside NemoClaw.
11. Only after the first smoke proof, advance to the final 1Password cutover
    gate before Taylor01 team bring-up.

## Paste-Ready Reset Block

Run this inside the Mac Mini execution-account shell after connecting remotely:

```bash
set -euo pipefail
export WORKSPACE="${WORKSPACE:-$HOME/bitpod-app}"
echo "resetting workspace at $WORKSPACE"
rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"
for repo in bitpod-assets bitpod-docs bitpod-taylor-runtime bitpod-tools bitregime-core sector-feeds; do
  echo "cloning $repo"
  git clone "https://github.com/BitPod-App/${repo}.git"
done
ls "$WORKSPACE"
```

Treat the repo list above as a 2026-03-22 workspace snapshot only. Reconcile it
against the current active workspace composition before using it as a live
bootstrap block.

If SSH-backed clones are preferred, replace the clone line with:

```bash
git clone "git@github.com:BitPod-App/${repo}.git"
```

## Secrets Flow

Use this sequence:

1. retrieve or authorize retrieval from 1Password
2. materialize the secret on the Mac Mini execution account only where needed
3. keep it in env vars or ignored local config files
4. keep the temporary secret set minimal before the first smoke proof
5. do not copy secrets through GitHub, `local-shared-dropoff/`, macOS shared
   mounts, or ad hoc notes

## Shared-Storage Rule

- broad shared mounts are off by default
- use them only for narrow temporary transfer cases
- do not treat them as the default sync model
- do not use them as a secret lane
- `local-shared-dropoff/` is allowed only as a short-lived exchange lane inside
  local-workspace, not as the default operating surface

## Verification Checklist

Minimum proof before calling the first bootstrap pass successful:

- remote shell from MacBook to Mac Mini admin account works
- remote shell into the execution account works
- fresh GitHub clones exist in the execution-account workspace
- Mac Mini workspace root is separate from the MacBook workspace
- NemoClaw/OpenShell can be invoked under the execution account
- one real smoke workflow ran inside the HQ runtime

## Ticket Split

- [BIT-105 — Execution HQ architecture decisions and boundary guardrails](https://linear.app/bitpod-app/issue/BIT-105/execution-hq-architecture-decisions-and-boundary-guardrails)
  - lock the dedicated execution-account model and remaining guardrails
- [BIT-106 — Mac Mini remote access and execution-HQ foundation](https://linear.app/bitpod-app/issue/BIT-106/mac-mini-remote-access-and-execution-hq-foundation)
  - create or verify the account split and prove the remote shell/admin path
- [BIT-108 — Execution-HQ workspace bootstrap and lightweight local-workspace profile](https://linear.app/bitpod-app/issue/BIT-108/execution-hq-workspace-bootstrap-and-lightweight-local-workspace)
  - delete stale workspace and rebuild from GitHub under the execution account
- [BIT-109 — Execution-HQ runtime, integrations, secrets, and dependency setup](https://linear.app/bitpod-app/issue/BIT-109/execution-hq-runtime-integrations-secrets-and-dependency-setup)
  - dependency install and temporary secret baseline for smoke proof
- [BIT-110 — NemoClaw/OpenShell installation, validation, and first HQ smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/nemoclawopenshell-installation-validation-and-first-hq-smoke-workflow)
  - runtime validation and first smoke proof
- [BIT-139 — Stage legacy secret retirement and 1Password cutover for AI HQ agent operations](https://linear.app/bitpod-app/issue/BIT-139/stage-legacy-secret-retirement-and-1password-cutover-for-ai-hq-agent)
  - staged secrets transition and final cutover gate before Taylor01 team
    bring-up
- [BIT-98 — Stand up Taylor01 minimal team inside NemoClaw execution HQ](https://linear.app/bitpod-app/issue/BIT-98/stand-up-taylor01-minimal-team-inside-nemoclaw-execution-hq)
  - blocked until the final 1Password cutover gate is complete
