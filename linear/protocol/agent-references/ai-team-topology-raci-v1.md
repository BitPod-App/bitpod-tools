# AI Team Topology + RACI v1

Status: Working baseline  
Phase: 4 (AI Agent Team Orchestration + Specialization)

## Topology

Control plane:

1. CJ (human principal)
2. Taylor (orchestrator PM)
3. Specialist lanes (engineering, QA, design/brand, research, browser ops)

Execution plane:

- Specialists run bounded tasks delegated by Taylor.
- QA lane remains independent for pass/fail authority.
- Merge/release gates require objective evidence.

## Ownership Boundaries

- CJ owns:
  - strategic priority
  - irreversible risk approval
  - final escalation decisions
- Taylor owns:
  - decomposition
  - dependency graph
  - dispatch and queue hygiene
  - completion evidence checks
- Specialists own:
  - implementation or analysis outputs in assigned lane
  - reproducible validation within lane boundaries
- QA owns:
  - independent quality verdict
  - explicit pass/fail artifact

## Escalation Model

Escalate to CJ when any of the following are true:

- irreversible/destructive action requested
- security/identity controls could be weakened
- cross-phase scope expansion is required
- unresolved capability degradation blocks critical path

Escalate to Taylor when:

- delegation payload is incomplete
- dependency ordering is unclear
- evidence is insufficient to transition status

## RACI Matrix (v1)

Legend: R = Responsible, A = Accountable, C = Consulted, I = Informed

| Workstream | CJ | Taylor | Eng | QA | Design/Brand | Research |
|---|---|---|---|---|---|---|
| Strategy and phase priority | A | C | I | I | I | C |
| Task decomposition and dependency map | C | A/R | C | C | C | C |
| Implementation changes (code/infrastructure) | I | C | A/R | C | I | I |
| QA verification and verdict | I | C | C | A/R | I | I |
| Brand/system asset changes | C | C | I | I | A/R | C |
| Research brief production | C | C | I | I | I | A/R |
| Status transition evidence check | C | A/R | C | C | C | C |
| Go/no-go and rollback trigger | A | C | C | C | I | I |

## Autonomy Rules

Autonomous allowed:

- normal implementation in approved scope
- documentation and artifact generation
- reversible automation/config updates

CJ approval required:

- billing plan changes
- ownership transfer/deletion/destructive bulk changes
- lockout/security posture changes with irreversible effect

## References

- [BIT-61 — Define AI team topology and ownership model (CJ -> Taylor orchestrator -> specialists)](https://linear.app/bitpod-app/issue/BIT-61/define-ai-team-topology-and-ownership-model-cj-taylor-orchestrator)
- [BIT-65 — QA authority model: specialist QA gate independent from orchestrator implementation](https://linear.app/bitpod-app/issue/BIT-65/qa-authority-model-specialist-qa-gate-independent-from-orchestrator)
