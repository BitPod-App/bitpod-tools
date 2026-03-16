# Taylor01 Boundary Map v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Layer definitions

### Taylor01 Portable Core

Reusable contracts and runtime concepts that should move across products and orgs:

- agent roles and authority boundaries
- orchestration logic
- certainty and provenance rules
- delegation and evidence contracts
- memory/session abstractions
- retrospectives and anti-drift patterns

### Taylor01 Workspace / Org Policy

CJ-centric operating norms and workspace rules that may travel with the team:

- approval boundaries
- trust policies
- local-vs-cloud hygiene
- cleanup rules
- collaboration habits
- operator-facing workstyle guidance

### Taylor01 Adapter Layer

Reusable interfaces and workflow contracts for third-party systems:

- Linear
- GitHub
- Discord
- future Slack/Jira equivalents

### BitPod Product Embedding

Artifacts that exist because the product is BitPod:

- product canon
- domain names and metaphors
- glossary/taxonomy
- brand assets
- app roadmap and user-facing semantics

## Current classification map

| Artifact or area | Layer | Specificity | Current action | Notes |
| --- | --- | --- | --- | --- |
| `/Users/cjarguello/BitPod-App/bitpod-docs/product-mvp/**` | BitPod Product Embedding | `bitpod-specific` | `keep-local` | Product canon should remain BitPod-owned |
| `/Users/cjarguello/BitPod-App/bitpod-assets/assets/brand/**` | BitPod Product Embedding | `bitpod-specific` | `keep-local` | Brand assets should not be normalized into Taylor01 |
| `/Users/cjarguello/BitPod-App/bitpod-docs/process/anti-drift-playbook.md` | Taylor01 Workspace / Org Policy | `portable` | `move-later` | Strong candidate for future `tools/taylor01/policy` |
| `/Users/cjarguello/BitPod-App/bitpod-docs/process/local-workspace-cleanup-runbook.md` | Taylor01 Workspace / Org Policy | `mixed` | `create-generic-version-now` | Reusable policy with BitPod path overlay currently mixed in |
| `/Users/cjarguello/BitPod-App/bitpod-docs/process/canonical-path-contract.md` | Mixed | `mixed` | `create-generic-version-now` | Needs split into portable path rules plus BitPod path map |
| `/Users/cjarguello/BitPod-App/bitpod-docs/process/project-sources/13_AGENT_EXECUTION_GATES_v1.md` | Taylor01 Workspace / Org Policy | `mixed` | `move-later` | Gate model is reusable; current framing is BitPod-era |
| `/Users/cjarguello/BitPod-App/local-workspace/local-codex/skills/qa-specialist/**` | Taylor01 Portable Core | `portable` | `keep-local-now` | Workspace-local canonical copy exists and should replace the home-directory mirror over time |
| `linear/protocol/agent-references/taylor-orchestrator-contract-v1.md` | Taylor01 Portable Core | `portable` | `move-later` | Strong core candidate once subtree is active |
| `linear/protocol/agent-references/specialist-agent-registry-v1.md` | Taylor01 Portable Core | `portable` | `move-later` | Registry semantics are reusable beyond BitPod |
| `linear/protocol/configs/agent-runtime-portability-plan-v1.md` | Taylor01 Portable Core | `mixed` | `move-later` | Concept is portable, examples are tied to current repo layout |
| `linear/protocol/agent-references/vera-runtime-minimum-v1.md` | Taylor01 Portable Core | `portable` | `keep-local-now` | Vera runtime minimum is reusable even though it was extracted from BitPod-era runtime evidence |
| `linear/protocol/configs/linear-operating-guide-v1.md` | Taylor01 Adapter Layer | `mixed` | `create-generic-version-now` | Workflow is reusable, but current language is BitPod-first |
| `linear/protocol/templates/linear-issue-template-evidence-contract-v1.md` | Taylor01 Adapter Layer | `mixed` | `create-generic-version-now` | Needs explicit portability fields |
| `.github/PULL_REQUEST_TEMPLATE.md` | Taylor01 Adapter Layer | `mixed` | `create-generic-version-now` | Template should carry Taylor01 portability check for relevant PRs |
| `linear/protocol/configs/communication-surface-portability-v1.md` | Taylor01 Adapter Layer | `mixed` | `move-later` | Adapter logic is reusable, but Discord baseline specifics remain embedded |
| `linear/protocol/agent-references/team-session-platform-migration-contract-v1.md` | Taylor01 Adapter Layer | `mixed` | `move-later` | Current transport migration story is still tied to Zulip/Discord lineage |
| `linear/protocol/configs/startup-operating-model-v1.md` | Mixed | `mixed` | `create-generic-version-now` | Needs explicit Taylor01/BitPod dual-product framing |
| `linear/protocol/configs/workspace-local-state-location-policy-v1.md` | Taylor01 Workspace / Org Policy | `mixed` | `create-generic-version-now` | Policy is reusable; current absolute path is BitPod-specific |
| `/Users/cjarguello/BitPod-App/local-workspace/local-codex/skills/isolation-mode/SKILL.md` | Taylor01 Workspace / Org Policy | `mixed` | `retire` | Preserve only the hardening intent; do not revive the dormant legacy isolation feature as portable core |

## Immediate working rule

When a new artifact is created, classify it with:

- `T01_LAYER`
- `T01_SPECIFICITY`
- `T01_ACTION`
- `T01_BYPASS` when portability is intentionally deferred for now

Do not assume generic process/workflow artifacts belong to BitPod just because they are being proven inside BitPod.

If immediate portability work is not worth the interruption, use a temporary bypass explicitly instead of silently leaving the artifact entangled.
