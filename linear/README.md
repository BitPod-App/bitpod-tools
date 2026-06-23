# Linear Tooling + Process

This folder contains the Linear tool surface plus the process canon that governs how BitPod work is tracked, evidenced, and reviewed.

## Structure

- `/bitpod-tools/linear/docs/`
  - SOP and implementation references.
- `/bitpod-tools/linear/docs/process/`
  - Process runbooks and operator notes.
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

- `./docs/process/linear_operating_model_v1.md`
- `./docs/process/linear_operating_guide_v3.md`
- `./docs/process/startup_operating_model_v2.md`
- `./docs/process/taylor_orchestrator_contract_v1.md`
- `./docs/process/qa_authority_model_v1.md`
- `./docs/process/interim_ai_technical_qa_cj_acceptance_policy_v1.md`
- `./docs/process/linear_admin_change_control_v1.md`
- `./docs/process/linear_change_proposal_template_v1.md`
- `./docs/process/linear_link_reference_policy_v1.md`
- `./docs/process/linear_issue_template_evidence_contract_v2.md`
- `./docs/process/linear_live_executor_rollout_path_v1.md`
- `./docs/process/linear_operating_guide_changelog.md`

## PR-to-Linear closeout enforcement

Before merge closeout, retroactive linking, or Linear normalization, read:

1. `./docs/process/linear_operating_guide_v3.md` rule 14
2. `./docs/process/linear_link_reference_policy_v1.md`
3. `./docs/process/linear_issue_template_evidence_contract_v2.md`

A closeout is not complete until the PR-to-Linear mapping, reciprocal links, project scope, status class, and labels have been verified or an explicit tooling blocker has been recorded.

## Supporting SOP and references

- `./docs/linear_custom_configs_v1.md`
- `./docs/process/linear_bot_v1_runbook.md`
- `./docs/process/live_cutover_auth_batch.md`
- `./docs/process/linear_operating_guide_v1.md`
- `./docs/process/linear_operating_guide_v2.md`
- `./docs/process/linear_issue_workflow_reconfig_spec_v1.md`
- `./docs/process/startup_operating_model_v1.md`
- `./docs/process/ai_team_topology_raci_v1.md`
- `./docs/process/taylor_orchestrator_contract_v1.md`
- `./docs/process/agent_handoff_templates_v1.md`
- `./docs/process/delegated_execution_sample_run_v1.md`
- `./docs/process/taylor_orchestrator_operational_proof_v1.md`
- `./docs/process/specialist_agent_registry_v1.md`
- `./docs/process/specialist_operating_lanes_proof_v1.md`
- `./docs/process/qa_authority_model_v1.md`
- `./docs/process/minimum_phase4_agent_team_contract_v1.md`
- `./docs/process/interim_ai_technical_qa_cj_acceptance_policy_v1.md`
- `./docs/process/agent_runtime_portability_plan_v1.md`
- `./docs/process/capability_state_truth_label_incident_protocol_v1.md`
- `./docs/process/linear_link_reference_policy_v1.md`
- `./docs/process/linear_operating_guide_changelog.md`
- `./docs/process/post_bootstrap_hardening_runbook_v1.md`
- `./docs/process/legacy_identity_sweep_remediation_2026-03-09.md`
- `./docs/process/memory_stewardship_service_contract_v1.md`
- `./docs/process/governance_policy_engine_v1.md`
- `./docs/process/github_team_purpose_reviewer_routing_v1.md`
- `./docs/process/eval_regression_gate_framework_v1.md`
- `./docs/process/team_session_platform_migration_contract_v1.md`

Legacy bootstrap docs that still live in other repos should be treated as reference material only until they are either re-homed or archived. The active Linear process canon belongs under `./docs/process/`.

## Phase 2 planning seeds

- `./docs/process/discord_migration_architecture_v1.md`
- `./docs/process/discord_command_parity_matrix_v1.md`
- `./docs/process/discord_webhook_parity_checks_v1.md`
- `./docs/process/discord_phase2_prereq_execution_runbook_v1.md`
- `./docs/process/discord_phase2_cj_ui_quickstart_v1.md`
- `./docs/process/stage4_5_agent_stack_execution_plan_v1.md`
- `./docs/process/communication_surface_portability_v1.md`
- `./docs/process/taylor_runtime_core_contract_v1.md`
- `./docs/process/global_artifact_naming_policy_v1.md`
- `./docs/process/long_thread_checkpoint_protocol_v1.md`
- `./docs/process/durable_artifact_memory_flow_proof_v1.md`
- `./docs/process/checkpoints/checkpoint_protocol_adoption_note_2026-03-11.md`
- `./docs/process/checkpoints/thread_checkpoint_template_v1.md`
- `./docs/process/checkpoints/active_checkpoint_sector_feeds_bit77_2026-03-11.md`
- `./docs/process/checkpoints/active_checkpoint_phase4_operating_model_2026-03-11.md`
- `./docs/process/workspace_local_state_location_policy_v1.md`

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
  - `pull_request.review_requested` for legacy/manual VeraQA review requests (compatibility trigger, not the required merge gate)
  - CJ-authored QA override intake from `issues.labeled`, `issue_comment.created`, and `pull_request_review.submitted`
  - `pull_request.closed` with merged=true (gate-completeness check + merge record)
- Linear events:
  - `Ready` / `In Progress` readiness enforcement trigger
  - comment-created QA token parser (`QA_RESULT=PASSED|FAILED|OVERRIDE|ACTION_REQUIRED`; deprecated `SKIPPED` fails closed)
  - PM review changed (`pm-accepted` / `pm-rejected` / `pm-skipped`)
  - daily aging scan payload handler
- Gating behavior:
  - execution gate (`Issue Type` + exact-one type + estimate + required headings)
  - status-first review flow (`In Review` remains the live review gate name)
  - QA gates drive `In Review` -> `Delivered`
  - PM review labels drive `Delivered` -> `Accepted`
  - merged PRs fail closed when merge-readiness truth is incomplete
  - backlog aging drives `Backlog` -> `Icebox 🧊` -> `Stale`
  - Dry-run default and simulation runner
  - guarded live Linear executor for `comment`, `set_status`, and `set_label` only, blocked unless governance allows the action, `LINEAR_LIVE_EXECUTOR_ENABLED=true`, and Linear actor attribution matches expected config

## Preferred workflow note

The canonical operating model is:

- engineering moves work into `In Review`
- pending QA is expressed by the status itself
- `qa-passed`, `qa-failed`, and `qa-override` are terminal/authority-bearing QA labels only
- `qa-override` may be synced from a CJ-authorized GitHub `QA_OVERRIDE` / `qa-override` label plus `/qa-override <reason>` evidence; this is not Vera QA and does not imply PM acceptance
- review-cleared work moves from `In Review` to `Delivered`
- `pm-accepted`, `pm-rejected`, and `pm-skipped` are result labels only
- work moves from `Delivered` to `Accepted`, then to `Done`
- merge to `main` only closes work when `Accepted` and the rest of merge-readiness truth is already satisfied

## Status model note (important)

Canonical target for the Product Development team workflow reconfiguration:
- `./docs/process/linear_operating_model_v1.md`

## How to run

```bash
cd $WORKSPACE/bitpod-tools
python3 linear/scripts/refresh_vera_qa_gate_runtime_env.py
linear/scripts/start_vera_qa_gate_dispatcher.sh
```

## Configure secrets

Permanent Vera QA Gate runtime configuration is generated from the approved
machine-local 1Password service-account env at
`~/.hermes/profiles/vera/op-vault-service.env`:

```bash
cd $WORKSPACE/bitpod-tools
python3 linear/scripts/refresh_vera_qa_gate_runtime_env.py
```

The generated file is machine-local (`~/.hermes/profiles/vera/vera-qa-gate-runtime.env`)
and must not be committed. It contains the live GitHub App material, webhook
signing secret, Linear OAuth client credentials, actor expectation from the
Linear viewer probe, and repo-to-Vera workspace map.

Recommended env vars, when inspecting or overriding the generated runtime file:

- `DRY_RUN=true` (default)
- `BOT_HOST=127.0.0.1`
- `BOT_PORT=8787`
- `VERA_QA_GATE_GITHUB_TOKEN` short-lived installation token, or `VERA_QA_GATE_GITHUB_APP_ID` / `VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID` / `VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY` for live `vera-qa-gate` check runs
- `GITHUB_WEBHOOK_SECRET` (future live mode)
- `LINEAR_OAUTH_CLIENT_ID` / `LINEAR_OAUTH_CLIENT_SECRET` from the approved Linear OAuth app actor for guarded live Linear mutations; the runtime mints `client_credentials` access tokens. `LINEAR_OAUTH_ACCESS_TOKEN` is a short-lived emergency fallback only; `LINEAR_API_KEY` is a legacy personal-script fallback, not the preferred agent path
- `LINEAR_WEBHOOK_SECRET` (future/live webhook mode)
- `VERA_QA_DISPATCH_ENABLED=false` (hard kill switch for Hermes Vera Kanban enqueue; default off)
- `VERA_QA_GATE_LIVE_ENABLED=false` (hard kill switch for GitHub `vera-qa-gate` check runs; default off)
- `VERA_QA_RESULT_SYNC_ENABLED=false` (hard kill switch for polling completed Vera Kanban tasks and syncing PASS/FAIL/OVERRIDE/ACTION_REQUIRED to GitHub + Linear; default off)
- `LINEAR_LIVE_EXECUTOR_ENABLED=false` (hard kill switch; default off)
- `LINEAR_EXPECTED_ACTOR_ID` / `LINEAR_EXPECTED_ACTOR_NAME` / `LINEAR_EXPECTED_ACTOR_EMAIL` (at least one required before live Linear mutations)
- `VERA_QA_KANBAN_WORKSPACE_MAP` JSON mapping of GitHub repos to Vera Kanban review workspaces; when set, unmapped repos fail closed instead of silently dispatching to `scratch`
- `VERA_QA_ARTIFACT_ROOT` external runtime artifact root for Vera-generated `manifest.json` / `verification_report.md` files; default `~/.hermes/profiles/vera/qa-artifacts`. This must stay outside reviewed repo workspaces so QA runs do not dirty or litter PR checkouts.

Reference template:
- `./config.example.env`

## Configure webhooks

GitHub webhook events:
- `pull_request` (opened, ready_for_review, review_requested, closed)
  - non-draft `opened`, `ready_for_review`, and VeraQA `review_requested` now plan Vera QA dispatch and a queued `vera-qa-gate` check when the event includes a head SHA.
- `issues` (`labeled`), `issue_comment` (`created`), and `pull_request_review` (`submitted`) for CJ-approved QA override intake.
  - Scope is all BitPod GitHub repos where the GitHub App/webhook is installed and subscribed to these events; the runtime uses the webhook `repository.full_name` / PR URL and does not hard-code a single repo.
  - Canonical GitHub label: `QA_OVERRIDE`; alias accepted: `qa-override`.
  - Required CJ evidence: `/qa-override <reason>` in a PR comment or approved PR review by `cjarguello`.
  - The runtime verifies the label is attributable to `cjarguello`, the reason is for the current head, and any `HEAD_SHA=` token matches before completing `vera-qa-gate`.
  - Linear sync uses one primary issue key. If the PR title contains exactly one issue key, that key is authoritative and body issue keys are treated as related references. If the title has multiple keys, the override fails closed until the primary issue is clarified. Live Linear execution may move the issue to `Delivered` only when the issue is currently `In Review`.
  - V1 is an interim convention-based path. V2 should use GitHub-native bypass/ruleset audit signals, custom properties, or a dedicated GitHub Action/App command by `cjarguello`.

Linear webhook events:
- issue updated (state and labels), including `In Review` transitions for Vera QA dispatch
- comment created (`QA_RESULT=PASSED|FAILED|OVERRIDE|ACTION_REQUIRED` can mark `vera-qa-gate` success, mark failure, authorize override, or fail with action required when the payload/comment carries `PR_URL=` and `HEAD_SHA=`; deprecated `SKIPPED` fails closed)

Vera result sync:
- `VERA_QA_RESULT_SYNC_ENABLED=true` lets the service poll completed Vera Kanban tasks, read `manifest.json` / `verification_report.md`, and sync `QA_RESULT=PASSED|FAILED|OVERRIDE|ACTION_REQUIRED` to Linear labels/status/comments plus the GitHub `vera-qa-gate` check.

Schedule:
- daily aging scan for backlog/icebox transitions.

## Simulation runner

```bash
cd $WORKSPACE/bitpod-tools/linear/src
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
python3 simulate.py --mode linear_comment --event ../events/sample_linear_comment_passed.json
python3 simulate.py --mode aging_scan --event ../events/sample_aging_scan.json
python3 simulate_e2e.py
```

Additional samples:

```bash
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
# PM review change and merged gate are exercised through service payloads in ./events/
```

Runtime contract validation:

```bash
cd $WORKSPACE/bitpod-tools
python3 linear/scripts/validate_runtime_contract_artifacts.py
```

Taylor01 Claw issue-seed dry run:

```bash
cd $WORKSPACE/bitpod-tools
python3 linear/scripts/create_linear_issues_from_seed.py
```

Issue creation note (status/state):
- Linear API issue creation is deterministic when you pass a concrete `stateId` (workflow state ID).
- For Product Development (`team=BIT`), `Backlog` stateId is `162716a8-ffa4-43ea-9e0d-c48fdb8054bc` (BIT-442).

`simulate_e2e.py` runs the feature happy-path sequence:
- PR opened -> In Progress
- PR ready for review -> `In Review`, Hermes `vera` QA enqueue, and queued `vera-qa-gate` when head SHA is available
- QA comment token parse (`QA_RESULT=PASSED`) -> `Delivered` and completed successful `vera-qa-gate`; `ACTION_REQUIRED` -> completed failure with action-needed summary when `PR_URL=` and `HEAD_SHA=` are available
- PM review signal (`pm-accepted`) -> `Accepted`
- PR merged -> final closure to `Done` plus merge record comment when merge-readiness truth is satisfied

## Discord operator preflight

Validate the private Discord config before any live webhook call:

```bash
cd $WORKSPACE/bitpod-tools
python3 linear/scripts/discord_config_preflight.py \
  --config $WORKSPACE/local-workspace/local-working-files/private.discord.config.json
```

## Test

```bash
cd $WORKSPACE/bitpod-tools
python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_linear_executor.py linear/tests/test_e2e_flow.py
```

One-command local smoke:

```bash
cd $WORKSPACE/bitpod-tools
bash linear/scripts/local_smoke.sh
```

## GitHub Actions smoke

PR checks run automatically for `linear/**` via:
- `.github/workflows/linear-bot-smoke.yml`

## Memory stewardship artifacts

- contract: `./docs/process/memory_stewardship_service_contract_v1.md`
- schema: `./contracts/memory_write_proposal_schema_v1.json`
- example proposal: `./examples/memory_write_proposal_example_v1.json`
- validator: `./scripts/validate_memory_proposal.py`

## Eval regression artifacts

- contract: `./docs/process/eval_regression_gate_framework_v1.md`
- registry: `./contracts/eval_registry_v1.json`
- runner: `./scripts/run_eval_regression_bundle.sh`
- sample report: `./examples/eval_regression_report_sample_2026-03-10.md`

## Attribution guardrails

- If GitHub actions appear as CJ instead of bot/app identity: stop and report `AUTH ATTRIBUTION WRONG`.
- If Linear mutations appear as CJ instead of app actor: stop and report `LINEAR ACTOR WRONG`.

## Governance policy artifacts

- contract: `./docs/process/governance_policy_engine_v1.md`
- policy matrix: `./contracts/governance_policy_matrix_v1.json`
- audit sample: `./examples/governance_audit_trail_sample_2026-03-10.json`
- validator: `./scripts/validate_governance_policy.py`

## Live-mode safety

- Service live mode supports GitHub PR comments through the existing `gh` path.
- Linear live execution is guarded by governance plus the hard `LINEAR_LIVE_EXECUTOR_ENABLED` kill switch.
- The Linear executor supports only `comment`, `set_status`, and `set_label`; unsupported actions fail closed.
- Actor attribution must match configured expected Linear actor fields before any live Linear mutation runs.

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
cd $WORKSPACE/bitpod-tools/linear/cloudflare
wrangler deploy
```

Required Cloudflare secrets/vars:
- `BOT_ORIGIN` (backend runtime URL)
- `GITHUB_WEBHOOK_SECRET`
- `LINEAR_WEBHOOK_SECRET`
