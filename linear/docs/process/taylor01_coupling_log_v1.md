# Taylor01 Coupling Log v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Record current examples where reusable Taylor01 behavior is still entangled with BitPod-specific paths, tool assumptions, or product framing.

This log is meant to stay curated, not exhaustive.

Do not dump every harmless temporary shortcut here.

Use it only for couplings that:

- are likely to matter later
- could become expensive if repeated
- or need explicit future review so they do not disappear from memory

## Active coupling entries

| ID | Path or artifact | Coupling type | Verified problem | Recommended action |
| --- | --- | --- | --- | --- |
| T01-C01 | `/Users/cjarguello/bitpod-app/bitpod-docs/process/canonical-path-contract.md` | BitPod path coupling | Portable path rules and BitPod absolute paths live in one file | Split generic path policy from BitPod overlay |
| T01-C02 | `/Users/cjarguello/bitpod-app/bitpod-docs/process/local-workspace-cleanup-runbook.md` | Workspace/path coupling | Reusable cleanup norms are mixed with BitPod path conventions and command examples | Create generic Taylor01 workspace policy and keep BitPod overlay separate |
| T01-C03 | `linear/docs/process/workspace_local_state_location_policy_v1.md` | Absolute path coupling | Local state policy hardcodes `/Users/cjarguello/bitpod-app/local-workspace/local-codex/.codex/` | Replace with generic policy + workspace-specific resolved path layer |
| T01-C04 | `linear/docs/process/linear_operating_guide_v1.md` | BitPod workflow coupling | Guide explicitly defines how "BitPod agents" use Linear | Publish Taylor01-aware v2 and keep BitPod-specific examples as overlay |
| T01-C05 | `linear/docs/process/linear_issue_template_evidence_contract_v1.md` | Missing portability gate | Issue evidence template lacks Taylor01 portability fields for reusable work | Publish v2 with portability check block |
| T01-C06 | `.github/PULL_REQUEST_TEMPLATE.md` | Missing portability gate | PR template has no Taylor01 portability classification fields | Add required section for relevant PRs |
| T01-C07 | `linear/docs/process/startup_operating_model_v1.md` | Product framing coupling | Operating model treats BitPod as the primary operating system instead of Taylor01 proving ground | Publish v2 with dual-product framing |
| T01-C08 | `linear/docs/process/agent_runtime_portability_plan_v1.md` | Repo layout coupling | Portable runtime plan uses current `linear/src` and `linear/cloudflare/worker.mjs` paths as examples | Retain concept, abstract path examples into future subtree targets |
| T01-C09 | `linear/docs/process/communication_surface_portability_v1.md` | Tool/baseline coupling | Adapter contract is reusable, but Discord channel matrix is embedded into the main policy doc | Keep adapter contract; move Discord specifics into overlay examples over time |
| T01-C10 | `linear/docs/process/team_session_platform_migration_contract_v1.md` | Historical transport coupling | Taylor runtime migration story is still anchored to Zulip -> Discord transition history | Keep historical context, separate generic adapter contract from migration history |
| T01-C11 | `/Users/cjarguello/bitpod-app/bitpod-docs/process/project-sources/13_AGENT_EXECUTION_GATES_v1.md` | Product-era execution coupling | Gate model is reusable but framed as current BitPod/Codex runtime control | Normalize into Taylor01 policy layer and keep BitPod-specific execution notes separate |
| T01-C12 | `/Users/cjarguello/bitpod-app/bitpod-docs/process/read-first-protocol.md` | Workspace authority coupling | First-read behavior likely belongs to Taylor01 policy, but lives only in BitPod docs tree | Promote generic policy version once reviewed against current usage |
| T01-C13 | `linear/docs/process/linear_operating_model_v1.md` + `linear/docs/process/linear_operating_guide_v3.md` | BitPod overlay coupling | These are the active owning doctrine docs for the current BitPod lane, but they should not be mistaken for the final Taylor adapter/core specification | Keep the overlay explicit and bounded; extract only in a dedicated later lane |
| T01-C14 | `/Users/cjarguello/bitpod-app/local-workspace/local-codex/skills/isolation-mode/SKILL.md` plus dormant policy state | Legacy feature coupling | Isolation intent is valid, but the feature depends on quarantined legacy implementation and should not define future Taylor01/OpenClaw boundaries | Retire the feature and preserve only the hardening/runtime intent in active canon |
| T01-C15 | Current local `SKILL.md`-based operator surfaces used around the Linear/process lane | Transitional local-surface coupling | Current skill-backed operator surfaces are useful and real for the BitPod lane, but they are still local overlays rather than the final Taylor capability model | Keep them truthful as transitional overlays and replace only when a durable Taylor surface is actually ready |

## Working interpretation

- Product-specific artifacts are not a problem by themselves.
- Mixed artifacts are the highest priority.
- Missing portability metadata in tickets and PRs is a process gap, not just a documentation gap.
- Temporary bypasses are acceptable when explicit, scoped, and worth revisiting later.

## Next cleanup order

1. add portability gate to PR and Linear workflows
2. publish Taylor01-aware operating docs (`v2` where versioning already exists)
3. normalize mixed workspace/path policies
4. prepare subtree landing zones before moving portable content
