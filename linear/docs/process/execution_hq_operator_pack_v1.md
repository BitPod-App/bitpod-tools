# Execution HQ Operator Pack v1

Date: 2026-03-22  
Primary issue: [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)

## Purpose

Give the operator a single practical pack for the first Mac Mini / Execution HQ
bootstrap pass.

Use this note for the actual step order. Use
`execution_hq_architecture_decisions_v1.md` for the why and policy decisions.

## Machine Split

### MacBook control console

What stays here:

- terminal shell used to reach the Mac Mini
- GitHub and PR management
- human-facing 1Password access
- planning, review, and remote-control coordination

What does **not** stay here:

- the primary Execution HQ workspace
- the primary NemoClaw runtime
- machine-local runtime state that belongs to the Mac Mini

### Mac Mini execution HQ

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

## Workspace Variables

Use these defaults unless a ticket says otherwise:

```bash
export WORKSPACE="${WORKSPACE:-$HOME/bitpod-app}"
```

On the Mac Mini, this means the rebuilt workspace normally lives at:

```bash
$HOME/bitpod-app
```

Do not hard-code `/Users/cjarguello/...` in new live operator steps unless the
step is explicitly recording a current-machine fact.

## First Bootstrap Sequence

1. Confirm the MacBook source workspace already passed full forced
   `cleanup-audit T3` with `result=PORCELAIN`.
2. Open a remote shell from the MacBook to the Mac Mini.
3. Delete the stale Mac Mini workspace.
4. Rebuild the Mac Mini workspace only from GitHub clones.
5. Confirm the new workspace exists and is separate from the MacBook
   `local-workspace/`.
6. Install or validate NemoClaw/OpenShell on the Mac Mini.
7. Materialize only the required runtime secrets from 1Password into the Mac
   Mini environment.
8. Run the first simple HQ smoke workflow inside NemoClaw.

## Paste-Ready Reset Block

Run this inside the Mac Mini shell after connecting remotely:

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

If SSH-backed clones are preferred, replace the clone line with:

```bash
git clone "git@github.com:BitPod-App/${repo}.git"
```

## Secrets Flow

Use this sequence:

1. retrieve or authorize retrieval from 1Password
2. materialize the secret on the Mac Mini only where needed
3. keep it in env vars or ignored local config files
4. do not copy secrets through GitHub, shared folders, or ad hoc notes

## Shared-Folder Rule

- shared folders are off by default
- use them only for narrow temporary transfer cases
- do not treat them as the default sync model
- do not use them as a secret lane

## Verification Checklist

Minimum proof before calling the first bootstrap pass successful:

- remote shell from MacBook to Mac Mini works
- fresh GitHub clones exist on the Mac Mini
- Mac Mini workspace root is separate from the MacBook workspace
- NemoClaw/OpenShell can be invoked on the Mac Mini
- one real smoke workflow ran inside the HQ runtime

## Ticket Split

- [BIT-106 — Mac Mini remote access and execution-HQ foundation](https://linear.app/bitpod-app/issue/BIT-106/mac-mini-remote-access-and-execution-hq-foundation)
  - prove the remote shell/admin path
- [BIT-108 — Execution-HQ workspace bootstrap and lightweight local-workspace profile](https://linear.app/bitpod-app/issue/BIT-108/execution-hq-workspace-bootstrap-and-lightweight-local-workspace)
  - delete stale workspace and rebuild from GitHub
- [BIT-109 — Execution-HQ runtime, integrations, secrets, and dependency setup](https://linear.app/bitpod-app/issue/BIT-109/execution-hq-runtime-integrations-secrets-and-dependency-setup)
  - dependency and secrets ownership on the Mac Mini
- [BIT-110 — NemoClaw/OpenShell installation, validation, and first HQ smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/nemoclawopenshell-installation-validation-and-first-hq-smoke-workflow)
  - runtime install/validation and smoke proof
- [BIT-111 — MacBook control-console workflow and gradual cutover](https://linear.app/bitpod-app/issue/BIT-111/macbook-control-console-workflow-and-gradual-cutover)
  - steady-state MacBook operator role
