# Linear Operating Guide v3 (Agents + Taylor01 Portability + Linear Change Control)

Version: v3
Status: Active
Owner: Product Development (Codex + Taylor)
Last updated: 2026-03-24
Primary issue: [BIT-22 — Versioned Linear operating guide for agents (with rollback path)](https://linear.app/bitpod-app/issue/BIT-22/versioned-linear-operating-guide-for-agents-with-rollback-path)
Supersedes: `linear_operating_guide_v2.md` as the active guide

## Purpose

Define the canonical way agents use Linear for execution tracking, evidence logging, safe status transitions, Taylor01 portability review, and reversible admin/process changes.

This guide is the active BitPod-specific Linear overlay, not the final Taylor capability model.

## Scope

- issue lifecycle handling for migration and operations work
- evidence-first completion rules
- cross-link behavior between Linear and GitHub
- degraded-capability behavior during tool outages
- Taylor01 portability classification for relevant work
- high-impact Linear admin/process change control
- explicit boundary notes for current BitPod-specific overlays and temporary Taylor portability bypasses

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

4. Issue readiness minimum
- Every actionable issue should answer:
  - what problem is being solved
  - what done looks like
  - who owns it right now
- If those are missing, the issue is not actually ready.

5. Keep issues small and action-oriented
- Prefer short acceptance checklists over long notebooks.
- If the issue needs long-form planning, link the document instead of turning the issue body into a dumping ground.
- If the checklist is too large to stay legible, split the work.

6. Statuses must reflect real state
- Do not move issues into `In Progress` unless someone is actively executing.
- If an issue is blocked, make the blocker explicit and include the next action.

7. `update Linear` means increase issue truth
- Default interpretation: make the issue materially more truthful, not merely leave a note.
- After meaningful execution or repo-thread closeout, update any clearly stale safe field when evidence is clear:
  - status/state when lifecycle actually changed
  - GitHub PR or merge links when they exist
  - project membership when obviously missing
  - related/blocked links when explicit
- Add a concise execution/progress comment with what changed, what was verified, and what remains.
- For partial shipment on a broader issue, do not move it to `Done` unless the scoped acceptance criteria are actually satisfied; still update links, comments, and any field that became more accurate.
- If a field is clearly stale and safe to update, comment-only is not enough.
- Temporary identity-safety rule: preserve the existing `assignee` and `delegate` by default.
- Change `assignee` or `delegate` only when the next responsible owner is explicit, real, and supported by clear evidence in the issue context.
- If ownership is unclear, leave `assignee` and `delegate` unchanged.
- Never assign or delegate an issue to Codex as part of routine `update Linear`.
- Do not use automatic `@Codex` mentions in Linear comments as part of routine `update Linear`.
- Do not rely on Linear triage rules or other automation that delegates issues to Codex as part of this policy.
- Treat this assignee/delegate restriction as a temporary safety rule until Codex is decoupled from the user's personal Linear identity.
- Do not casually change priority, estimate, due date, or milestone when confidence is low.
- Do not create duplicate retroactive issues when an existing issue already owns the scope.

8. Capability degradation handling
- If tool behavior is impaired, stop speculative actions and post minimal verified state.
- Continue with the smallest reversible step or park with an explicit blocker.
- Use `capability_state_truth_label_incident_protocol_v1.md` as the incident-response workflow.
- Current known degraded surface: Linear MCP read truth is not authoritative for all workspace state.
- Treat the Linear UI as the source of truth when MCP conflicts with the UI on project deletion state, blocker relations, or workspace-admin configuration.
- Current reproduced MCP failures:
  - deleted project can still read back as active
  - removed blocker relations can still read back as present
  - broad project-list queries can fail with `Query too complex`

9. Linear admin change control
- Workflow, schema, template, automation, or other meaningful admin changes must follow `linear_admin_change_control_v1.md`.
- Destructive or high-blast changes require a written proposal, a snapshot, and a rollback note before execution.

10. Taylor01 portability gate
- Any relevant issue must include a Taylor01 Portability Check block.
- Relevant means the issue touches agents, workflows, process docs, workspace policy, or tool integrations.
- Product-only BitPod work does not need the block unless it changes reusable operating behavior.
- The current primary execution goal remains building BitPod App using Taylor01 Team.
- Missing portability classification means the issue is not decision-complete unless the update explicitly declares a temporary Taylor01 bypass with reason and review trigger.
- Temporary bypass is allowed for bounded experimental work; hidden coupling is not.
- Default expectation is to solve portability now for new portable or mixed work unless there is a concrete reason not to.
- Meaningful active bypasses should be tracked in `taylor01_active_bypass_register_v1.md` and reviewed soon, not left as vague backlog residue.
- Current SKILL.md-based local operator surfaces are transitional evidence and operator overlays, not the final Taylor capability shape.
- Keep current BitPod-specific docs and workflows truthful here when they are still needed for current execution; do not silently promote them into Taylor core by implication.

11. Weekly hygiene beats backlog drift
- Keep Linear small and legible.
- Close stale tickets, merge duplicates, and normalize missing acceptance criteria before adding more structure.
- Prefer fewer labels unless a new label clearly solves repeated friction.

## Required issue evidence format

- What was changed
- Verification command(s) or UI check performed
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

- Active statuses observed: `Icebox 🧊`, `Backlog`, `Ready`, `In Progress`, `In Review`, `Delivered`, `Accepted`, `Done`, `Canceled`, `Duplicate`, `Obsolete`, `Won't Do`.
- Canonical status, label, board, gate, and automation semantics now live in `linear_operating_model_v1.md`.
- Legacy lifecycle labels and older review label groups are transitional residue and should not be expanded.

## Version to config mapping (v3)

This version corresponds to:

- evidence-first completion protocol from `v2`
- Taylor01 portability review gate from `taylor01_portability_review_gate_v1.md`
- active issue evidence contract from `linear_issue_template_evidence_contract_v2.md`
- Linear admin/process change-control from `linear_admin_change_control_v1.md`
- proposal workflow from `linear_change_proposal_template_v1.md`

Artifacts:

- `linear_operating_model_v1.md`
- `linear_operating_guide_v3.md`
- `linear_issue_template_evidence_contract_v2.md`
- `taylor01_portability_review_gate_v1.md`
- `linear_admin_change_control_v1.md`
- `linear_change_proposal_template_v1.md`
- `linear_link_reference_policy_v1.md`
- `capability_state_truth_label_incident_protocol_v1.md`

## Rollback path

If `v3` causes workflow regression:

1. Set the active guide version back to `v2` in `linear_operating_guide_changelog.md`.
2. Re-apply `v2` baseline settings from mapped artifacts.
3. Re-run verification commands from each artifact.
4. Post rollback evidence comment in the affected Linear issue(s).

Rollback does not delete later docs; it re-activates `v2` as execution policy.
