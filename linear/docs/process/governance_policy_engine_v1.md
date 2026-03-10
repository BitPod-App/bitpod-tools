# Governance Policy Engine v1

## Purpose

Define fail-closed approval thresholds for high-impact actions so the agent system can move quickly without silently crossing destructive boundaries.

## Core rule

If an action is high-impact and approval or evidence is missing, the action does not execute.

## Policy classes

### Class A — Safe autonomous

Allowed without CJ approval when evidence is attached:

- create or update docs
- create non-destructive reports
- run read-only scans
- open or update PRs without merge
- comment on Linear or GitHub with evidence

### Class B — Guarded autonomous

Allowed with Taylor approval and explicit evidence:

- change workflow policies in repo docs
- create new process contracts
- enable non-destructive automation in dry-run mode
- change issue/project structure in Linear when reversible

### Class C — CJ approval required

Blocked unless CJ explicitly approves:

- destructive delete or irreversible cleanup
- credential rotation/revocation
- permission broadening
- production deploy or cutover
- branch protection/ruleset changes
- repo visibility changes
- account/org ownership changes

### Class D — Emergency stop

Never proceed autonomously:

- bypass security controls
- disable audit trails
- execute an action known to violate policy

## Required evidence by class

- Class A: command output or artifact path
- Class B: command output or artifact path plus approval reference
- Class C: approval reference, execution evidence, rollback note
- Class D: no execution; emit blocker only

## Enforcement behavior

For every requested action, the policy engine must produce:

- `action_class`
- `allowed`
- `required_approver`
- `evidence_required`
- `decision_reason`

If `allowed=false`, the action must stop before execution.

## Audit trail minimum

Every high-impact evaluation must leave a trace with:

- timestamp
- actor
- action id
- action summary
- policy class
- approval state
- decision
- evidence links

## Initial implementation artifacts

- policy matrix: `linear/contracts/governance_policy_matrix_v1.json`
- audit sample: `linear/examples/governance_audit_trail_sample_2026-03-10.json`
- validator: `linear/scripts/validate_governance_policy.py`
