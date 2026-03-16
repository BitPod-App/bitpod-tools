# Linear Tooling + Process

This folder contains the Linear tool surface plus the process canon that governs how BitPod work is tracked, evidenced, and reviewed.

## Structure

- `/bitpod-tools/linear/docs/`
  - SOP and implementation references.
- `/bitpod-tools/linear/docs/process/`
  - Transitional process docs, proofs, plans, and operator notes pending protocol/temporal normalization.
- `/bitpod-tools/linear/protocol/`
  - Canonical process docs, templates, configs, and agent references.
- `/bitpod-tools/linear/src/`
  - Rule engine, webhook service, and simulator.
- `/bitpod-tools/linear/contracts/`
  - Machine-readable runtime, agent, and tool registries.
- `/bitpod-tools/linear/examples/`
  - Sample traces and delegated execution artifacts.
- `/bitpod-tools/linear/events/`
  - Sample payloads for local simulation.
- `/bitpod-tools/linear/tests/`
  - Unit tests for gate and transition behavior.

## Active canon

- `./protocol/configs/linear-operating-guide-v3.md`
- `./protocol/configs/startup-operating-model-v2.md`
- `./protocol/agent-references/taylor-orchestrator-contract-v1.md`
- `./protocol/agent-references/qa-authority-model-v1.md`
- `./protocol/configs/interim-ai-technical-qa-cj-acceptance-policy-v1.md`
- `./protocol/configs/linear-admin-change-control-v1.md`
- `./protocol/templates/linear-change-proposal-template-v1.md`
- `./protocol/configs/linear-operating-guide-changelog.md`

## Supporting SOP and references

- `./docs/linear_custom_configs_v1.md`
- `./protocol/configs/linear-bot-runbook-v1.md`
- `./docs/process/live-cutover-auth-batch.md`
- `./protocol/configs/linear-operating-guide-v1.md`
- `./protocol/configs/linear-operating-guide-v2.md`
- `./protocol/configs/linear-issue-workflow-reconfig-spec-v1.md`
- `./protocol/configs/startup-operating-model-v1.md`
- `./protocol/agent-references/ai-team-topology-raci-v1.md`
- `./protocol/agent-references/taylor-orchestrator-contract-v1.md`
- `./protocol/templates/agent-handoff-templates-v1.md`
- `./temporal/active/ticket__BIT-61/delegated-execution-sample-run-v1.md`
- `./temporal/active/ticket__BIT-84/taylor-orchestrator-operational-proof-v1.md`
- `./protocol/agent-references/specialist-agent-registry-v1.md`
- `./temporal/active/ticket__BIT-85/specialist-operating-lanes-proof-v1.md`
- `./protocol/agent-references/qa-authority-model-v1.md`
- `./protocol/agent-references/minimum-phase4-agent-team-contract-v1.md`
- `./protocol/configs/interim-ai-technical-qa-cj-acceptance-policy-v1.md`
- `./protocol/configs/agent-runtime-portability-plan-v1.md`
- `./protocol/configs/capability-state-truth-label-incident-protocol-v1.md`
- `./protocol/configs/linear-link-reference-policy-v1.md`
- `./protocol/configs/linear-operating-guide-changelog.md`
- `./temporal/active/ticket__BIT-32/post-bootstrap-hardening-runbook-v1.md`
- `./docs/process/legacy-identity-sweep-remediation-2026-03-09.md`
- `./protocol/agent-references/memory-stewardship-service-contract-v1.md`
- `./protocol/configs/governance-policy-engine-v1.md`
- `./protocol/configs/github-team-purpose-reviewer-routing-v1.md`
- `./protocol/configs/eval-regression-gate-framework-v1.md`
- `./protocol/agent-references/team-session-platform-migration-contract-v1.md`

Legacy bootstrap docs that still live in other repos should be treated as reference material only until they are either re-homed or archived. The active Linear process canon is being normalized into `./protocol/`. The remaining `./docs/process/` surface is intentionally minimal and should only hold explicitly deferred residual material.

## Phase 2 planning seeds

- `./temporal/active/ticket__BIT-28/discord-migration-architecture-v1.md`
- `./temporal/active/ticket__BIT-29/discord-command-parity-matrix-v1.md`
- `./temporal/active/ticket__BIT-30/discord-webhook-parity-checks-v1.md`
- `./temporal/active/ticket__BIT-59/discord-phase2-prereq-execution-runbook-v1.md`
- `./temporal/active/ticket__BIT-59/discord-phase2-cj-ui-quickstart-v1.md`
- `./temporal/active/project__bootstrap__0727b3f56ccd/stage4-5-agent-stack-execution-plan-v1.md`
- `./protocol/configs/communication-surface-portability-v1.md`
- `./protocol/agent-references/taylor-runtime-core-contract-v1.md`
- `../bitpod-docs/process/global-artifact-naming-policy-v1.md`
- `./protocol/configs/long-thread-checkpoint-protocol-v1.md`
- `./temporal/active/ticket__BIT-87/durable-artifact-memory-flow-proof-v1.md`
- `./temporal/active/ticket__BIT-88/checkpoint-protocol-adoption-note-2026-03-11.md`
- `./protocol/templates/thread-checkpoint-template-v1.md`
- `./temporal/active/ticket__BIT-77/checkpoint-sector-feeds-bit77-2026-03-11.md`
- `./temporal/active/ticket__BIT-83/checkpoint-phase4-operating-model-2026-03-11.md`
- `./protocol/configs/workspace-local-state-location-policy-v1.md`

## Current implementation coverage (v1)

Important truth note:

- this section describes the currently checked-in engine/service behavior
- it does not fully represent the preferred future Linear acceptance workflow
- current real governance still relies on the temporary [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)
- where the engine behavior and the CJ-approved operating model differ, treat the engine as transitional

Implemented in engine/service:
- GitHub events:
  - `pull_request.opened`
  - `pull_request.ready_for_review`
  - `pull_request.closed` with merged=true (fail-closed gate check)
- Linear events:
  - ready-gate enforcement trigger
  - comment-created QA token parser (`QA_RESULT=PASSED|FAILED`)
  - PM label changed (`Approved` / `Rejected`)
  - daily aging scan payload handler
- Gating behavior:
  - Ready gate (required Type + required headings)
  - QA/PM label defaults in review flow (older transitional behavior)
  - merge gate requires QA Passed + PM Approved
  - fail-closed comments when gates are not met
- Dry-run default and simulation runner

## Preferred workflow note

The preferred operating model is:

- engineering moves work into `In Review`
- QA runs in `In Review`
- `QA: Passed` should move work to `In Acceptance`
- PM labels should belong to `In Acceptance`
- `PM: Approved` should establish merge readiness
- `PM: Rejected` should send work back to `In Progress`

That model is not yet fully represented in the checked-in engine and simulation files, so treat it as the target workflow rather than the current implementation truth.

## Status model note (important)

SOP expects emoji statuses (`☑️ Ready`, `🏗️ In Progress`, `🧪 In Review`, etc).
Current BIT workspace still uses mixed/non-emoji statuses (`Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Icebox 🧊`, `Obsolete`).

This implementation includes fallback handling for current statuses where safe, but full parity requires final Linear status normalization.

Canonical target for the Product Development team workflow reconfiguration:
- `./protocol/configs/linear-issue-workflow-reconfig-spec-v1.md`

## How to run

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools/linear/src
python3 service.py --dry-run
```

## Configure secrets

Recommended env vars:

- `DRY_RUN=true` (default)
- `BOT_HOST=127.0.0.1`
- `BOT_PORT=8787`
- `GITHUB_APP_ID` (future live mode)
- `GITHUB_APP_PRIVATE_KEY` (future live mode)
- `GITHUB_WEBHOOK_SECRET` (future live mode)
- `LINEAR_API_KEY` or OAuth app creds (future live mode)
- `LINEAR_WEBHOOK_SECRET` (future live mode)

Reference template:
- `./config.example.env`

## Configure webhooks

GitHub webhook events:
- `pull_request` (opened, ready_for_review, closed)

Linear webhook events:
- issue updated (state and labels)
- comment created

Schedule:
- daily aging scan for backlog/icebox transitions.

## Simulation runner

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools/linear/src
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
python3 simulate.py --mode linear_comment --event ../events/sample_linear_comment_passed.json
python3 simulate.py --mode aging_scan --event ../events/sample_aging_scan.json
python3 simulate_e2e.py
```

Additional samples:

```bash
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
# PM label changed and merged gate are exercised through service payloads in ./events/
```

Runtime contract validation:

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
python3 linear/scripts/validate_runtime_contract_artifacts.py
```

`simulate_e2e.py` runs the full happy-path sequence:
- PR opened -> In Progress
- PR ready for review -> In Review + QA/PM defaults
- QA comment token parse (`QA_RESULT=PASSED`)
- PM approval label signal
- PR merged with gates satisfied -> Done

## Discord operator preflight

Validate the private Discord config before any live webhook call:

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
python3 linear/scripts/discord_config_preflight.py \
  --config /Users/cjarguello/BitPod-App/local-workspace/local-working-files/private.discord.config.json
```

## Test

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py
```

One-command local smoke:

```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools
bash linear/scripts/local_smoke.sh
```

## GitHub Actions smoke

PR checks run automatically for `linear/**` via:
- `.github/workflows/linear-bot-smoke.yml`

## Memory stewardship artifacts

- contract: `./protocol/agent-references/memory-stewardship-service-contract-v1.md`
- schema: `./contracts/memory_write_proposal_schema_v1.json`
- example proposal: `./examples/memory_write_proposal_example_v1.json`
- validator: `./scripts/validate_memory_proposal.py`

## Eval regression artifacts

- contract: `./protocol/configs/eval-regression-gate-framework-v1.md`
- registry: `./contracts/eval_registry_v1.json`
- runner: `./scripts/run_eval_regression_bundle.sh`
- sample report: `./examples/eval_regression_report_sample_2026-03-10.md`

## Attribution guardrails

- If GitHub actions appear as CJ instead of bot/app identity: stop and report `AUTH ATTRIBUTION WRONG`.
- If Linear mutations appear as CJ instead of app actor: stop and report `LINEAR ACTOR WRONG`.

## Governance policy artifacts

- contract: `./protocol/configs/governance-policy-engine-v1.md`
- policy matrix: `./contracts/governance_policy_matrix_v1.json`
- audit sample: `./examples/governance_audit_trail_sample_2026-03-10.json`
- validator: `./scripts/validate_governance_policy.py`

## Live-mode safety

- Service live mode currently supports GitHub PR comments only.
- Linear live mutation executor is intentionally fail-closed until final API/actor wiring is complete.

## Portability-first architecture

- Core logic is platform-agnostic in `src/engine.py`.
- Runtime orchestration + memory abstraction lives in `src/runtime.py` + `src/memory.py`.
- Transport adapters stay thin (`src/service.py`).
- Cloudflare migration notes: `docs/cloudflare_migration_path.md`.

## Cloudflare adapter (optional now, migration-ready)

A Worker edge gateway scaffold is included at:
- `linear/cloudflare/worker.mjs`
- `linear/cloudflare/wrangler.toml`

Purpose:
- stable public webhook ingress (`/webhooks/github`, `/webhooks/linear`)
- forward events to runtime backend (`BOT_ORIGIN`)
- keep portability while enabling Cloudflare-first deployment path

Quick start:
```bash
cd /Users/cjarguello/BitPod-App/bitpod-tools/linear/cloudflare
wrangler deploy
```

Required Cloudflare secrets/vars:
- `BOT_ORIGIN` (backend runtime URL)
- `GITHUB_WEBHOOK_SECRET`
- `LINEAR_WEBHOOK_SECRET`
