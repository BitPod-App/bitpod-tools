# Agent Delegation + Handoff Templates v1

Status: Working baseline

## Core Handoff Envelope (required)

```md
Task ID:
Linked issue:
Owner:
Delegated by:

Objective:

In-scope:
- ...

Out-of-scope:
- ...

Required outputs:
- Deliverable 1:
- Deliverable 2:

Validation plan:
- Command/UI check 1:
- Command/UI check 2:

Artifacts destination:
- /absolute/path/or/url

Rollback note:
- Revert path/command:

Escalation:
- If blocked on X, escalate to:
```

## Engineering Handoff Template

```md
Code paths in scope:
- ...

Behavioral risk:
- low|medium|high (why)

Test requirements:
- unit:
- integration:
- smoke:

Gate to pass:
- QA verdict required: yes/no
```

## QA Handoff Template

```md
System under test:
- ...

Acceptance criteria:
- ...

Verification evidence:
- command output:
- artifact link:
- pass/fail:

Final QA verdict:
- PASSED | FAILED

Blocking defects (if failed):
- ...
```

## Design/Brand Handoff Template

```md
Asset/update target:
- ...

Canonical source:
- ...

Status:
- placeholder | working | final | superseded

Preview and usage paths:
- ...

Follow-up normalization needed:
- yes/no (details)
```

## Research Handoff Template

```md
Question:
- ...

Sources and constraints:
- ...

Findings:
- ...

Recommendations:
- ...

Confidence:
- Verified/Inferred/Unknown + %
```

## Example Delegated Chain (compact)

1. Taylor -> Engineering: implement scoped change + tests.
2. Engineering -> QA: provide build/test artifacts.
3. QA -> Taylor: PASS/FAIL verdict with evidence links.
4. Taylor -> CJ: gate summary and go/no-go recommendation.

## References

- [BIT-64 — Agent delegation protocol and cross-agent handoff templates v1](https://linear.app/bitpod-app/issue/BIT-64/agent-delegation-protocol-and-cross-agent-handoff-templates-v1)
- [BIT-61 — Define AI team topology and ownership model (CJ -> Taylor orchestrator -> specialists)](https://linear.app/bitpod-app/issue/BIT-61/define-ai-team-topology-and-ownership-model-cj-taylor-orchestrator)
