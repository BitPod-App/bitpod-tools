# Linear Operating Guide v1 (Agents)

Version: v1
Status: Active
Owner: Product Development (Codex + Taylor)
Last updated: 2026-03-07
Related issue: https://linear.app/bitpod-app/issue/BIT-22/versioned-linear-operating-guide-for-agents-with-rollback-path

## Purpose

Define the canonical way BitPod agents use Linear for execution tracking, evidence logging, and safe status transitions.

## Scope

- Issue lifecycle handling for migration and operations work
- Evidence-first completion rules
- Cross-link behavior between Linear and GitHub
- Degraded-capability behavior during tool outages

## Operating rules

1. Evidence-first claims
- Completion claims must include commands or UI proof and artifact path(s).
- Queue status alone is not proof of completion.

2. Single source of truth
- Use issue comments for execution evidence.
- Store durable artifacts in repo under `/bitpod-tools/linear/docs/process/`.

3. Link hygiene
- Linear issue refs should be full links when posted in chat/docs.
- PR updates should include related Linear issue reference.

4. Capability degradation handling
- If tool behavior is impaired, stop speculative actions and post minimal verified state.
- Continue with smallest reversible step or park with explicit blocker.

## Current workspace status model (as of v1)

- Active statuses observed: `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate`, plus `Icebox 🧊` / `Obsolete` in some views.
- Legacy lifecycle labels (`LIFECYCLE/*`) remain acceptable during transition.

## Required issue evidence format

- What was changed
- Verification command(s) / UI check performed
- Artifact path(s)
- Pass/fail outcome
- Transition reason

## Version -> config mapping (v1)

This version corresponds to:
- GitHub org baseline controls (2FA required, member repo deletion disabled)
- Team access map baseline (`core-maintainers`, `automation`, `readers`)
- Repo security baseline (secret scanning, push protection, dependabot, branch protection)
- Governance parity baseline files across org repos

Artifacts:
- `github_org_baseline_policy_v1.md`
- `github_org_baseline_evidence_2026-03-06.md`
- `github_org_team_access_map_2026-03-07.md`
- `github_repo_security_matrix_2026-03-07.md`
- `governance_parity_checklist_2026-03-07.md`

## Rollback path

If a future v2/v3 change causes workflow regression:

1. Set active guide version back to `v1` in `linear_operating_guide_changelog.md`.
2. Re-apply v1 baseline settings from mapped artifacts.
3. Re-run verification commands from each artifact.
4. Post rollback evidence comment in the affected Linear issue(s).

Rollback does not delete later docs; it re-activates v1 as execution policy.

## Change policy

- Append-only versioning (`v1`, `v2`, ...)
- Never overwrite prior version semantics; create new version file + changelog entry
- Any version change requires explicit reasons and rollback notes
