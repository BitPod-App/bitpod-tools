# QA Review Checklist v1

- Identify repo, PR/diff, branch, and exact files reviewed.
- Confirm requested tier: T1 baseline, T2 stronger model/reasoning, or T3 rare manual audit.
- Inspect the diff/files directly.
- Compare against ticket/request and acceptance criteria.
- Run relevant lightweight checks when safe and available.
- Separate observed evidence from inference.
- Return exactly one verdict: `PASS`, `FAIL`, or `BLOCKED`.
- Include risks, suggested fix, and residual risk.
