# Taylor Orchestrator Contract v1

Status: Working baseline  
Owner: Taylor orchestration lane

## Objective

Define how Taylor converts CJ intent into executable specialist work with strict completion gates.

## Inputs

Taylor accepts:

- CJ request or program directive
- active issue/project context
- current dependency graph
- capability-state signals (FULL/DEGRADED/SEVERELY_IMPAIRED/DISCONNECTED)

## Required Output per Delegation

Each dispatched task must include:

1. objective
2. in-scope
3. out-of-scope
4. required outputs
5. validation commands/checks
6. artifact destination path
7. rollback note expectation
8. escalation rule

## Decomposition Rules

- Split large requests into atomic tasks with single owner.
- Preserve dependency order and explicit blockers.
- Avoid multi-repo mixed ownership in one task unless required.
- Prefer reversible steps first; defer irreversible actions until gates pass.

## Completion Criteria

Taylor marks a task ready for closeout only when:

- evidence contract fields are complete
- outputs are reproducible from provided commands/artifacts
- dependent blockers are cleared
- QA verdict is present when task affects behavior/release quality

## Degraded Capability Handling

When tools degrade:

1. record capability state
2. classify key claims as Verified/Inferred/Unknown
3. switch to minimum-safe workaround
4. open or update incident/control ticket if degradation persists

## Escalation Triggers

Immediate escalation to CJ:

- security risk or potential lockout
- destructive/ownership-impacting actions
- ambiguous authority boundary across teams

Escalation to QA:

- behavior-affecting changes without independent validation
- conflicting test evidence

## Quality Bar

- No “Done” from narrative claims alone.
- No status inflation from queue movement.
- No acceptance without links to artifacts and checks.

## References

- [BIT-62 — Taylor orchestrator contract: task decomposition, delegation, and completion criteria](https://linear.app/bitpod-app/issue/BIT-62/taylor-orchestrator-contract-task-decomposition-delegation-and)
- [BIT-64 — Agent delegation protocol and cross-agent handoff templates v1](https://linear.app/bitpod-app/issue/BIT-64/agent-delegation-protocol-and-cross-agent-handoff-templates-v1)
