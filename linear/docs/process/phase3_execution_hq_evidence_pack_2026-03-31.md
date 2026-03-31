# Phase 3 Execution HQ Evidence Pack 2026-03-31

Status: Active retained evidence pack
Primary issue: [BIT-113 — Phase 3 evidence pack and HQ go/no-go](https://linear.app/bitpod-app/issue/BIT-113/phase-3-evidence-pack-and-hq-gono-go)
Related issues:
- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
- [BIT-105 — Execution HQ architecture decisions and boundary guardrails](https://linear.app/bitpod-app/issue/BIT-105/execution-hq-architecture-decisions-and-boundary-guardrails)
- [BIT-106 — Mac Mini remote access and execution-HQ foundation](https://linear.app/bitpod-app/issue/BIT-106/mac-mini-remote-access-and-execution-hq-foundation)
- [BIT-108 — Execution-HQ workspace bootstrap and lightweight local-workspace profile](https://linear.app/bitpod-app/issue/BIT-108/execution-hq-workspace-bootstrap-and-lightweight-local-workspace)
- [BIT-109 — Execution-HQ runtime, integrations, secrets, and dependency setup](https://linear.app/bitpod-app/issue/BIT-109/execution-hq-runtime-integrations-secrets-and-dependency-setup)
- [BIT-110 — Validate first AI HQ runtime path and complete first truthful smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/validate-first-ai-hq-runtime-path-and-complete-first-truthful-smoke)
- [BIT-49 — Lock down personal GitHub account to human-only access (remove AI/runtime paths)](https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove)
- [BIT-74 — Execute post-bootstrap local scope hardening window after migration closeout](https://linear.app/bitpod-app/issue/BIT-74/execute-post-bootstrap-local-scope-hardening-window-after-migration)

## Purpose

Record one evidence-backed Phase 3 closeout pack for the current Mac Mini
execution-HQ claim using:

- direct machine checks from the MacBook control console into `mini-01`
- current repo verification
- current Linear issue state

This pack is intentionally narrow. It is about truthful Phase 3 execution-HQ
closure, not Taylor-real, startup-ready, or full OpenClaw proof.

## Direct machine evidence captured in this turn

All checks below were run from the MacBook control console on 2026-03-31.

### Admin account reachability

Verified:

- `ssh mini-01.local` succeeded in batch mode
- remote identity returned:
  - `HOST: mini-01.local`
  - `USER: cjarguello`
- `/Users/taylor01/BitPod-App` exists from the admin account view
- `/Users/taylor01/BitPod-App/bitpod-taylor-runtime/scripts/launch_taylor.sh`
  exists from the admin account view

### Execution account reachability

Verified:

- `ssh taylor01@mini-01.local` succeeded in batch mode
- remote identity returned:
  - `HOST=mini-01.local`
  - `USER=taylor01`
  - `HOME=/Users/taylor01`
- execution workspace exists at:
  - `/Users/taylor01/BitPod-App`

### Execution workspace shape

Observed top-level entries under `/Users/taylor01/BitPod-App`:

- `artifacts`
- `bitpod-assets`
- `bitpod-docs`
- `bitpod-taylor-runtime`
- `bitpod-tools`
- `bitregime-core`
- `configs`
- `external`
- `local-workspace`
- `sector-feeds`
- `taylor01-skills`

This is sufficient to support the claim that the execution account owns a real
workspace separate from the MacBook control-console workspace.

### Runtime substrate probe

Verified under `taylor01@mini-01.local`:

- `python3 --version` = `Python 3.9.6`
- `tomli` import discovery = `yes`
- launcher exists at:
  - `/Users/taylor01/BitPod-App/bitpod-taylor-runtime/scripts/launch_taylor.sh`
- runtime repo state:
  - `bitpod-taylor-runtime` = clean on `main...origin/main`
- tools repo state:
  - `bitpod-tools` = clean on `main...origin/main`
- launcher status probe:
  - `bash scripts/launch_taylor.sh status`
  - result:
    - `status=stopped`
    - `env_file=/Users/taylor01/BitPod-App/bitpod-taylor-runtime/configs/.env`
    - `log_file=/Users/taylor01/BitPod-App/bitpod-taylor-runtime/artifacts/zulip/taylor.log`
    - `pid_file=/Users/taylor01/BitPod-App/bitpod-taylor-runtime/artifacts/zulip/taylor.pid`

### OpenClaw / NemoClaw substrate probe

Verified under `taylor01@mini-01.local`:

- `external/NemoClaw` exists as a git repo
  - branch: `main`
  - status: clean on `main...origin/main`
- `external/OpenShell` exists as a git repo
  - branch: `main`
  - status: clean on `main...origin/main`

Also verified:

- `git` exists at `/opt/homebrew/bin/git`
- `docker` is missing on the execution account
- `colima` is missing on the execution account

Current read:

- the external Claw substrate is present on disk
- the container-runtime layer required for fuller OpenShell / NemoClaw
  execution proof is not currently available from the execution account
- this makes container runtime a machine-readiness blocker for the fuller
  OpenClaw proof lane, not an architecture blocker

### Important non-claim from this turn

The following was also verified:

- `/Users/taylor01/BitPod-App/bitpod-taylor-runtime/configs/.env` was not
  present at probe time

Therefore this pack does not claim, from this turn alone:

- a live secret baseline is currently materialized in `.env`
- the runtime is currently running
- the first smoke workflow was re-proven in this turn

Those earlier claims remain anchored to prior issue completion and retained
history, not this direct probe alone.

## Current Linear state checked in this turn

- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
  = `In Progress`
- [BIT-113 — Phase 3 evidence pack and HQ go/no-go](https://linear.app/bitpod-app/issue/BIT-113/phase-3-evidence-pack-and-hq-gono-go)
  = `In Progress`
- [BIT-108 — Execution-HQ workspace bootstrap and lightweight local-workspace profile](https://linear.app/bitpod-app/issue/BIT-108/execution-hq-workspace-bootstrap-and-lightweight-local-workspace)
  = `Done`
- [BIT-109 — Execution-HQ runtime, integrations, secrets, and dependency setup](https://linear.app/bitpod-app/issue/BIT-109/execution-hq-runtime-integrations-secrets-and-dependency-setup)
  = `Done`
- [BIT-110 — Validate first AI HQ runtime path and complete first truthful smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/validate-first-ai-hq-runtime-path-and-complete-first-truthful-smoke)
  = `Done`
- [BIT-49 — Lock down personal GitHub account to human-only access (remove AI/runtime paths)](https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove)
  = `Ready`
- [BIT-74 — Execute post-bootstrap local scope hardening window after migration closeout](https://linear.app/bitpod-app/issue/BIT-74/execute-post-bootstrap-local-scope-hardening-window-after-migration)
  = `Backlog`

## Evidence-backed read

### What is now directly verified

- the MacBook still functions as the control-console path into the Mini
- the execution account is truthfully `taylor01`
- the execution account owns a real workspace on the Mini
- the launcher-backed runtime substrate exists on the execution account
- the Python 3.9 / `tomli` blocker is resolved on the execution account
- the execution workspace repos checked in this turn are clean
- the external NemoClaw/OpenShell repos are present and clean
- the fuller OpenClaw/NemoClaw path is still blocked by missing container
  runtime on the execution account

### What is supported indirectly by prior completed issues

This pack still relies on existing issue closure for the claim that the first
runtime and smoke proof already happened:

- [BIT-109 — Execution-HQ runtime, integrations, secrets, and dependency setup](https://linear.app/bitpod-app/issue/BIT-109/execution-hq-runtime-integrations-secrets-and-dependency-setup)
- [BIT-110 — Validate first AI HQ runtime path and complete first truthful smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/validate-first-ai-hq-runtime-path-and-complete-first-truthful-smoke)

This turn did not re-run a secret-backed or operator-backed smoke workflow.

## Residual blocker disposition

### [BIT-49 — Lock down personal GitHub account to human-only access (remove AI/runtime paths)](https://linear.app/bitpod-app/issue/BIT-49/lock-down-personal-github-account-to-human-only-access-remove)

Current read:

- still a real hardening and startup-readiness item
- not required to state truthfully that the execution-HQ boundary exists and is
  reachable now
- should remain explicit as deferred hardening if Phase 3 closes before it does

### [BIT-74 — Execute post-bootstrap local scope hardening window after migration closeout](https://linear.app/bitpod-app/issue/BIT-74/execute-post-bootstrap-local-scope-hardening-window-after-migration)

Current read:

- still a post-bootstrap hardening action
- not required to prove the current execution-HQ boundary exists truthfully
- should not be silently folded into the Phase 3 closeout claim

## Go / no-go read

Truth label for this pack:

- `Verified (90%)`

Interpretation:

- strong enough to support a Phase 3 execution-boundary go
- not strong enough to claim startup-ready
- not strong enough to claim the runtime is currently live in this exact turn
- not strong enough to claim Taylor-real or OpenClaw proof completion

Explicit current read:

- `PHASE_3_EXECUTION_HQ_BOUNDARY_GO=true`
- `STARTUP_READY=false`
- `LIVE_RUNTIME_REPROVED_THIS_TURN=false`

## Next required lane after this pack

If this pack is accepted, the next active blockers are not more Phase 3
planning docs. They are:

1. [BIT-214 — Taylor01: lock minimum real-Taylor runtime contract](https://linear.app/bitpod-app/issue/BIT-214/taylor01-lock-minimum-real-taylor-runtime-contract)
2. [BIT-215 — Taylor01: decide Claw v1 scope and boundary](https://linear.app/bitpod-app/issue/BIT-215/taylor01-decide-claw-v1-scope-and-boundary)
3. [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)
4. [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
5. [BIT-97 — Prove Taylor as a real AI agent in any live operator surface](https://linear.app/bitpod-app/issue/BIT-97/prove-taylor-as-a-real-ai-agent-in-any-live-operator-surface)
