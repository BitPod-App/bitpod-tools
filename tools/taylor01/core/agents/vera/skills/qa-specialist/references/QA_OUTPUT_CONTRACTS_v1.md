# QA Output Contracts v1

Required short-form review output:

```text
Vera QA — bounded technical review
Actor: app:vera | vera-qa
Tier: T1 | T2 | T3
Verdict: PASS | FAIL | BLOCKED
Scope reviewed:
- ...
Evidence:
- ...
Risks:
- ...
Suggested fix:
- ...
Residual risk:
- ...
```

Use `PASS` only when no blocking defect was found in the bounded reviewed scope. Use `FAIL` when there is a concrete blocker. Use `BLOCKED` when evidence, auth, repo state, checks, or acceptance criteria are insufficient.
