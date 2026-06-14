# Vera QA Lane Contract v1

Status: Working baseline  
Linked issue: [BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy)

## Objective

Define the dedicated Vera-style QA lane as a real operating lane with explicit verdict authority, explicit evidence requirements, and a durable artifact flow into Linear and PR work.

This contract is the target operating model for technical QA in BitPod Phase 4. It is not a merge-policy replacement by itself.

## Current implementation reference

This repo contract is implemented through the repo-backed `qa-specialist` skill source:

- canonical repo source:
  - `$WORKSPACE/bitpod-tools/tools/taylor01/core/agents/vera/skills/qa-specialist/SKILL.md`
  - `$WORKSPACE/bitpod-tools/tools/taylor01/core/agents/vera/skills/qa-specialist/references/QA_OUTPUT_CONTRACTS_v1.md`
  - `$WORKSPACE/bitpod-tools/tools/taylor01/core/agents/vera/skills/qa-specialist/references/QA_REVIEW_CHECKLIST_v1.md`

If this skill is installed into a local Codex or Hermes runtime, the runtime copy is an installed artifact. The repo source above remains the reviewable source of truth.

That skill should be treated as a transitional implementation surface for Vera while the dedicated QA lane is still being operationalized as a fuller agent/runtime.

The durable intent is:

- Vera = QA specialist role/lane
- `qa-specialist` = current implementation scaffold for that role

The long-term role should not be constrained to remaining only a skill.

For preserved Zulip-era QA/runtime behaviors that should not be lost during Vera migration, see:

- [vera_runtime_behavior_inventory_from_zulip_v1.md](./vera_runtime_behavior_inventory_from_zulip_v1.md)
- [vera_runtime_minimum_v1.md](./vera_runtime_minimum_v1.md)

## What Makes This A Dedicated QA Lane

The QA lane counts as dedicated only if all of the following are true:

- the lane is invoked through an explicit QA handoff, not as an afterthought in implementation notes
- the lane decides only `PASSED` or `FAILED`
- the lane produces a structured verification artifact with evidence
- the artifact is linked back to the related issue and/or PR
- the implementation lane does not self-issue the final QA verdict

If any of those are missing, the work falls back to the interim pattern rather than the dedicated QA lane.

## Role Boundaries

### Vera owns

- QA verdict only
- verification scope review against critical acceptance criteria
- evidence capture
- blocking-defect callouts
- residual-risk callouts when verdict is `PASSED`

### Vera does not own

- product priority
- scope reshaping
- implementation
- merge approval authority
- rewriting acceptance criteria after work is complete
- cross-lane orchestration workflow beyond returning the verdict artifact

## Inputs Required

Minimum handoff packet into QA:

- linked issue or PR
- system under test
- critical acceptance criteria
- commands or surfaces to verify
- expected artifact destinations
- known risks or constraints

If the handoff packet is incomplete, QA should reject the handoff and ask Taylor for a corrected packet.

## Required Output Contract

Every dedicated QA execution must produce a `verification_report.md`-style artifact with:

1. verdict: `PASSED`, `FAILED`, or `SKIPPED`
2. environment matrix
3. critical acceptance criteria with evidence per criterion
4. `this failed QA because ...` section when verdict is `FAILED`
5. `this QA was skipped because ...` section when verdict is `SKIPPED`
6. optional low-risk fix hints only when obvious
7. final line:
   - `QA_VERDICT: PASSED`, or
   - `QA_VERDICT: FAILED`, or
   - `QA_VERDICT: SKIPPED`

Allowed storage targets:

- `linear/examples/*verification_report*.md`
- issue-linked repo artifact paths under `/linear/docs/process/**` when the report is part of a process proof
- PR comments or Linear comments that link to the durable artifact rather than replacing it

Optional companion artifacts may exist when useful, but they are not required to count as Vera operating correctly:

- `test_plan.md`
- `bug_report.md`

## Required Flow

1. Taylor delegates QA with explicit acceptance criteria.
2. Engineering or prior lane provides the build/test/artifact surface.
3. Vera executes checks and writes the verification artifact.
4. Vera returns `PASSED` or `FAILED` with evidence links.
5. Taylor synthesizes the verdict into the execution spine.
6. CJ acceptance or admin bypass, if needed, remains a separate governance action.

The minimum successful QA handoff is therefore:

- Taylor or engineering supplies the verification target and criteria
- Vera returns `verification_report.md` or an official GitHub review with evidence
- Taylor or CJ decides what to do with that verdict

Taylor01 may PM-accept CJ-requested work/tickets she created or coordinated. Taylor01 may invoke Vera or require a ticket/PR to pass through VeraQA, but Taylor01 must not code-review or QA-skip as a substitute for VeraQA when VeraQA is required.


## Single-gate routing model (Hermes-aware)

Vera lane remains the dedicated QA authority. The active GitHub-native gate is the required `vera-qa-gate` check run emitted by the Vera QA Gate GitHub App/bot path. CODEOWNERS is retired as a merge gate because it routes through a paid user seat/team abstraction rather than the actor that produced the QA result.

### GitHub `vera-qa-gate` check

- Name: `vera-qa-gate`
- Actor/source: Vera QA Gate GitHub App / bot-owned result sync
- Trigger: Vera auto-dispatch from PR review-ready/head-update or Linear `In Review` transitions.
- Model/depth: chosen by Vera/runtime/process per change risk; not by GitHub team name.
- Goal: pass/fail/override/action-required + evidence with practical runtime checks.

### Superseded tier names

`@BitPod-App/veraqa`, `@BitPod-App/veraqa-tier-1`, `@BitPod-App/veraqa-tier-2`, and `@BitPod-App/veraqa-tier-3-audit` are historical routing concepts only. Do not use them as active CODEOWNERS routes. Escalation depth remains valid as a Vera process decision, but it must not be represented by GitHub team name.

## Dynamic escalation policy

Use the same `R` score in team/ruleset docs:

- risk label present (`risk:high`, `risk:security`, `migration`, `production`, `release`, `data`, `secrets`): `+3`
- `files_changed >= 8`: `+2`
- `lines_changed >= 500`: `+2`
- critical scope touched (`/.github/workflows/`, `migrations/`, `runtime/`, `infra/`, `cloudflare/`, `deploy/`, `terraform/`): `+2`
- blocking label: `+1`

Decision:

- `R >= 4`: move to **escalated Vera review**
- `R >= 7`: **escalated Vera review required; consider rare deep audit only by explicit Taylor/CJ/Vera request or exceptional-risk judgment**

High-impact repos (`sector-feeds`, `bitregime-core`):

- default path is always escalated Vera review.
- do not downshift these repos to baseline review solely because a PR is small.
- use rare deep audit only for exceptional risk, intentionally selected periodic deep audit, or explicit Taylor/CJ/Vera request.

Rare deep audit usage:

- Rare deep audit is manual, never default, and not normal merge gating.
- Use it for explicit Taylor/CJ/Vera request, exceptional risk, or intentionally selected assurance sampling.
- There is no fixed daily quota in this guidance.

## Retired Linear Agent / Linear-bot Vera prompt

The old built-in Linear Agent / Linear-bot prompt path is retired as an active
VeraQA execution surface. It was useful as a temporary copy-paste bridge, but it
now creates identity confusion because the intended path is a dedicated Vera
runtime/Hermes agent surface, not workspace guidance inside Linear Agent.

Current rule:

- do not use Linear Agent workspace guidance as the active VeraQA gate
- do not ask the built-in Linear Agent to impersonate Vera
- do not treat a Linear Agent response as an independent VeraQA verdict
- keep the dedicated Vera core/runtime artifacts as the preserved path for real
  VeraQA evolution

Manual workspace cleanup paired with this repo change:

- disable or neutralize the old Linear Agent workspace guidance that says Vera
  should review `In Review` issues
- keep the normal Linear GitHub integration, MCP authorization, and GitHub org
  connection separate from this retired agent prompt

Dedicated Vera/Hermes follow-up remains tracked through:

- [BIT-94 — Create Vera QA Specialist agent and make QA Review gating real](https://linear.app/bitpod-app/issue/BIT-94/create-vera-qa-specialist-agent-and-make-qa-review-gating-real)
- [BIT-99 — Embody first specialist as a real AI agent/runtime beyond lane or skill proxy](https://linear.app/bitpod-app/issue/BIT-99/embody-first-specialist-as-a-real-ai-agentruntime-beyond-lane-or-skill)
- [BIT-398 — Vera/Hermes Telegram QA-repair lane](https://linear.app/bitpod-app/issue/BIT-398/verahermes-telegram-qa-repair-lane)
- [BIT-488 — Retire stale Linear Agent Vera QA prompt and align repo guidance](https://linear.app/bitpod-app/issue/BIT-488/retire-stale-linear-agent-vera-qa-prompt-and-align-repo-guidance)

### What remains valid

The portable Vera contract and bridge/runtime code remain valid if they are used
as a dedicated Vera execution path that emits evidence-bound artifacts. The
retirement here applies to the old Linear Agent prompt, not to VeraQA as a
concept or to CODEOWNERS reviewer routing.

## Independence Rules

This contract inherits and operationalizes:

- [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)
- [qa_authority_model_v1.md](./qa_authority_model_v1.md)

Additional working rules:

- Taylor may route QA work, but may not overwrite a `FAILED` verdict.
- Engineering may answer QA questions, but may not publish the final QA verdict on its own work.
- CJ may override only through an explicit risk-acceptance path and rollback note.

## Relationship To Interim BIT-79 Policy

This contract changes the primary QA expectation:

- primary technical QA path: dedicated Vera lane with structured evidence artifacts
- temporary merge-governance fallback: [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)

[BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) remains active only because GitHub reviewer-routing and standalone merge authority are not yet fully aligned with the operating model.

It should no longer be treated as the primary definition of QA itself once this lane is in use.

## Completion Signal For BIT-90

[BIT-90 — Stand up dedicated QA lane beyond interim AI technical QA policy](https://linear.app/bitpod-app/issue/BIT-90/stand-up-dedicated-qa-lane-beyond-interim-ai-technical-qa-policy) is satisfied only when:

- this lane contract exists
- at least one real verification artifact exists under this contract
- the artifact flow is linked back into real issue/PR execution
- the repo explicitly states whether [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy) can be downgraded from primary reliance
