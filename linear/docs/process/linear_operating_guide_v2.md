# Linear Operating Guide v2 (Agents + Taylor01 Portability)

Version: v2
Status: Active
Owner: Product Development (Codex + Taylor)
Last updated: 2026-03-12
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Supersedes: `linear_operating_guide_v1.md` as the active guide

## Purpose

Define the canonical way agents use Linear for execution tracking, evidence logging, safe status transitions, and Taylor01 portability review.

## Scope

- Issue lifecycle handling for migration and operations work
- Evidence-first completion rules
- Cross-link behavior between Linear and GitHub
- Degraded-capability behavior during tool outages
- Taylor01 portability classification for relevant work

## Operating rules

1. Evidence-first claims
- Completion claims must include commands or UI proof and artifact path(s).
- Queue status alone is not proof of completion.

2. Single source of truth
- Use issue comments for execution evidence.
- Store durable artifacts in repo under `/bitpod-tools/linear/docs/process/`.

3. Link hygiene
- Linear issue refs and PR refs must follow `linear_link_reference_policy_v1.md`.
- If title lookup is unavailable, use degraded fallback format (ID + full URL) instead of guessing.

4. Capability degradation handling
- If tool behavior is impaired, stop speculative actions and post minimal verified state.
- Continue with smallest reversible step or park with explicit blocker.
- Use `capability_state_truth_label_incident_protocol_v1.md` as mandatory incident-response workflow.

5. Taylor01 portability gate
- Any relevant issue must include a Taylor01 Portability Check block.
- Relevant means the issue touches agents, workflows, process docs, workspace policy, or tool integrations.
- Product-only BitPod work does not need the block unless it changes reusable operating behavior.
- Missing portability classification means the issue is not decision-complete unless the update explicitly declares a temporary Taylor01 bypass with reason and review trigger.
- Temporary bypass is allowed for bounded experimental work; hidden coupling is not.
- Default expectation is to solve portability now for new portable or mixed work unless there is a concrete reason not to.
- Meaningful active bypasses should be tracked in `taylor01_active_bypass_register_v1.md` and reviewed soon, not left as vague backlog residue.

## Required issue evidence format

- What was changed
- Verification command(s) / UI check performed
- Artifact path(s)
- Pass/fail outcome
- Transition reason
- Taylor01 Portability Check (when relevant)

## Active portability fields

- `T01_LAYER`: `core | policy | adapter | bitpod-embedding | mixed`
- `T01_SPECIFICITY`: `portable | bitpod-specific | mixed`
- `T01_COUPLING`: short note on what remains too coupled
- `T01_ACTION`: `keep-local | move-later | create-generic-version-now`
- `T01_BYPASS`: `none | temporary-coupling`
- `T01_BYPASS_REASON`: why the portability fix is being deferred
- `T01_REVIEW_TRIGGER`: when the coupling must be revisited

## Current workspace status model

- Active statuses observed: `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate`, plus `Icebox 🧊` / `Obsolete` in some views.
- Legacy lifecycle labels (`LIFECYCLE/*`) remain acceptable during transition.

## Version -> config mapping (v2)

This version corresponds to:

- evidence-first completion protocol from `v1`
- Taylor01 portability review gate from `taylor01_portability_review_gate_v1.md`
- active issue evidence contract from `linear_issue_template_evidence_contract_v2.md`

Artifacts:

- `linear_operating_guide_v2.md`
- `linear_issue_template_evidence_contract_v2.md`
- `taylor01_portability_review_gate_v1.md`
- `linear_link_reference_policy_v1.md`
- `capability_state_truth_label_incident_protocol_v1.md`

## Rollback path

If `v2` causes workflow regression:

1. Set active guide version back to `v1` in `linear_operating_guide_changelog.md`.
2. Re-apply `v1` baseline settings from mapped artifacts.
3. Re-run verification commands from each artifact.
4. Post rollback evidence comment in the affected Linear issue(s).

Rollback does not delete later docs; it re-activates `v1` as execution policy.
