<!-- GENERATED FILE. DO NOT EDIT HERE. -->
<!-- CANONICAL SOURCE: bitpod-docs/process/taylored-policy-rules.md -->
<!-- MIRROR ROLE: repo packet mirror -->
# Taylored Policy Rules

CANONICAL SOURCE: `bitpod-docs/process/taylored-policy-rules.md`
LOCAL ROOT MIRROR: `$WORKSPACE/taylored-policy-rules.md` bootstrap mirror only
EDIT SURFACE: edit this file first; generated mirrors must not become parallel canon

NAME: Taylored Policy Rules
STATUS: Active
DATE: 2026-03-24
VERSION: 1.1
OWNER: Workspace / Product Development
DESCRIPTION: Enumerates prohibition IDs, enforcement states, alertability, and exception eligibility.
SCOPE: Root prohibitions for the entire workspace.
ENTRYPOINT: Referenced by repo `AGENTS.md` files and governance docs.
DEPENDENCIES: `taylored-policy.md`, `../AGENTS.md`.
OVERRIDE_POLICY: Only rules marked `exception_allowed = YES` may be declared as explicit repo exceptions.

Status: Active shared policy rules file
Owner: Workspace / Product Development
Scope: root prohibition IDs, enforcement state, override eligibility, and alert intent

## Purpose

This file is the root prohibition list for the deployed workspace.

Use it to:

- define exact rule IDs
- decide whether a prohibition is enforced, detected-only, or documented-only
- decide whether a rule may ever be excepted by repo `AGENTS.md`
- keep exception behavior non-silent and auditable

## Enforcement States

- `ENFORCED`: active policy prohibition; operators and agents must treat it as binding
- `DETECTED_ONLY`: intended prohibition; observable attempts should be surfaced, but hard enforcement may still be incomplete
- `DOCUMENTED_ONLY`: declared prohibition; tracking exists, but detection and enforcement are not yet wired

## Alertability

- `ALERT_ON_ATTEMPT`
- `ALERT_ON_SUCCESS`
- `NO_ALERT_YET`

## Exception Rule

Repo `AGENTS.md` may declare exceptions only for rules whose `exception_allowed` value is `YES`.

Every exception must include:

- exact `rule_id`
- scope
- reason
- conditions
- required owner role
- standing or temporary duration

## Root Rules

| rule_id | title | prohibition | scope | enforcement_state | alertability | exception_allowed | owner_doc |
|---|---|---|---|---|---|---|---|
| `TPR-001` | Truth First | Do not invent filesystem, Git, GitHub, Linear, auth, or integration facts. | root-wide | `ENFORCED` | `ALERT_ON_SUCCESS` | `NO` | `truthfulness-and-verification-policy.md` |
| `TPR-002` | No Silent Exception | Do not bypass or reinterpret a root prohibition without an explicit repo exception declaration. | root-wide | `ENFORCED` | `ALERT_ON_ATTEMPT` | `NO` | `taylored-policy.md` |
| `TPR-003` | Repo Instructions Only | Repo `AGENTS.md` adds instructions only and must not suspend root prohibitions unless it declares an explicit allowed exception. | repo `AGENTS.md` | `ENFORCED` | `ALERT_ON_SUCCESS` | `NO` | `taylored-policy.md` |
| `TPR-004` | Exception By ID Only | Repo `AGENTS.md` may declare an exception only by citing exact rule IDs. | repo `AGENTS.md` | `ENFORCED` | `ALERT_ON_ATTEMPT` | `YES` | `taylored-policy.md` |
| `TPR-005` | Chat First | Do not create files when chat output is sufficient. | agent output | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `file-creation-and-artifact-placement-policy.md` |
| `TPR-006` | No Default Repo Artifacts | Do not create repo artifacts by default unless the owning repo contract explicitly requires them. | repo artifacts | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `temporal-and-local-working-artifact-policy.md` |
| `TPR-007` | No Ad Hoc Root Files | Do not create ad hoc root files for convenience. | `#WORKSPACE_ROOT` | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `file-creation-and-artifact-placement-policy.md` |
| `TPR-008` | No Silent Destructive Cleanup | Do not hard-delete, purge, close PRs, or delete branches without the active policy allowing it. | cleanup and Git hygiene | `ENFORCED` | `ALERT_ON_ATTEMPT` | `YES` | `taylored-policy.md` |
| `TPR-009` | No Machine State In Repo | Do not store machine-local auth, session history, or persistent runtime state in tracked repo paths. | repo roots and `.codex/` | `ENFORCED` | `ALERT_ON_SUCCESS` | `NO` | `workspace_local_state_location_policy_v1.md` |
| `TPR-010` | No Synthetic Backfill | Do not create retrospective or process-history artifacts just to patch missing history. | docs and artifacts | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `file-creation-and-artifact-placement-policy.md` |
| `TPR-011` | GitHub-Native Minimalism | Do not rely on GitHub-native config as the main Taylor01 portability layer. | root governance | `DOCUMENTED_ONLY` | `NO_ALERT_YET` | `NO` | `taylored-policy.md` |
| `TPR-012` | Tokenized Public Root | Do not publish person-specific local paths in root public policy surfaces. | root public docs | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `taylored-policy.md` |
| `TPR-013` | Secretless Repo Trees | Do not store secrets in tracked repo files or shared handoff folders by default. | repo files and handoffs | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `taylored-policy.md` |
| `TPR-014` | Root Policy Canon | Do not create, restore, or treat legacy policy shim files as the primary policy authoring surface once `taylored-policy.md` exists. | root policy files | `ENFORCED` | `ALERT_ON_SUCCESS` | `NO` | `taylored-policy.md` |
| `TPR-015` | Temporal Is Local Until Unified | Do not treat repo-local temporal metadata as the universal artifact lifecycle contract until a shared lifecycle taxonomy is adopted. | repo temporal metadata | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `temporal-and-local-working-artifact-policy.md` |
| `TPR-016` | No Local Workspace README Docs | Do not create `README.md`, `readme.md`, or equivalent local folder documentation files anywhere under `#LOCAL_WORKSPACE`, including nested local folders. | `#LOCAL_WORKSPACE` | `ENFORCED` | `ALERT_ON_SUCCESS` | `YES` | `file-creation-and-artifact-placement-policy.md` |

Interpretation for `TPR-016`:

- local-workspace lanes are operational holding surfaces, not documentation surfaces
- canonical guidance belongs in root policy, shared process docs, owning repos, or approved external canonical systems
