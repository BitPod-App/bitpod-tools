# Templates Registry (Canonical Index)

This registry is the single source of truth for templates across BitPod repos.

## Rules

- A document is a **template** only if it is reused frequently (default threshold: >= 2 uses/month).
- If it is not frequent, store it as a **process doc** (`runbook`, `playbook`, `SOP`) instead.
- Prefer updating existing templates over creating new variants.
- Keep reciprocal pointers:
  - Registry points to template file.
  - Template file header points back to this registry.

## Category Index

1. Linear templates
2. Agent templates
3. Planning and proposal templates
4. Retrospective templates
5. Artifact templates
6. Handoff templates
7. Process docs (non-template)
8. Learnings ledger

## 1) Linear Templates (High Frequency)

- **Active**: Technical project template
  - Path: `/Users/cjarguello/bitpod-app/bitpod-tools/linear/projects/technical_project_template.md`
  - Use: project technical briefs and project setup docs

- **Planned (create only if usage confirms need)**:
  - `linear_issue_template.md`
  - `linear_project_update_template.md`
  - `linear_incident_update_template.md`

## 2) Agent Templates (Lean Set)

- **Active**: Verification report
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/proving-run/templates/verification_report_template_v1.md`
  - Use: evidence-first QA/result reporting

- **Active**: Execution notes
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/proving-run/templates/execution_notes_template_v1.md`
  - Use: short execution logs

## 3) Planning and Proposal Templates

- **Active**: Plan template
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/proving-run/templates/plan_template_v1.md`
  - Use: scoped plan before execution

- **Active**: Linear change proposal
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/linear/templates/linear_change_proposal_template_v1.md`
  - Use: workflow/status/automation change proposals

## 4) Retrospective Templates (Max 2)

- **Active**: Standard retrospective
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/proving-run/templates/retrospective_template_v1.md`
  - Use: regular retrospectives

- **Active**: Incident/capability regression retro
  - Path: `/Users/cjarguello/bitpod-app/bitpod-docs/archive/learnings/retro-2026-03-02-capability-regression-protocol.md`
  - Use: outage/failure analysis and protocol updates

## 5) Artifact Templates

- **Active**: Verification report (artifact-oriented)
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/proving-run/templates/verification_report_template_v1.md`

- **Active**: Result template
  - Path: `/Users/cjarguello/bitpod-app/sector-feeds/docs/agents/proving-run/templates/result_template_v1.md`

## 6) Handoff Templates

- **Planned (single universal handoff first)**:
  - `handoff_universal_template.md` (Product<->Design<->Engineering<->QA<->Ops)
- Do not create role-specific variants until universal template shows repeated gaps.

## 7) Process Docs (Non-Template)

These are runbooks/SOPs and should not be treated as templates:

- `/Users/cjarguello/bitpod-app/sector-feeds/docs/runbooks/show_onboarding_template.md` (operational onboarding doc)
- Migration runbooks, cleanup audits, parity checks, and outage procedures

## 8) Learnings Ledger

Retrospective takeaways should be appended to one ledger (not separate template sprawl):

- Ledger path: `/Users/cjarguello/bitpod-app/bitpod-docs/archive/learnings/learnings_ledger.md`
- Suggested columns:
  - date
  - source retro/doc
  - team/department
  - role
  - category
  - learning
  - action
  - owner
  - status

## Current Proposed Template Additions (Minimal)

Create only these next, in order:

1. `handoff_universal_template.md`
2. `linear_issue_template.md` (only if repeated issue-authoring friction persists)
3. `linear_project_update_template.md` (only if weekly updates are inconsistent)

## Intake Email Note (Linear)

Team intake email can be used for quick issue creation:

- `product-development-5b52a7f8725e@intake.linear.app`

Policy suggestion:

- Route intake-created issues to `Backlog` + `needs-triage` label by default.
- Require normalization within 24h into canonical issue format.
