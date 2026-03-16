# Recovery Thread Start Templates Pack

## 1) Generic Recovery Template

```md
Recovery restart for this thread.

Context:
Prior thread(s) may be unstable/incomplete due to incident conditions (dead/disappearing/replayed outputs).

Rules:
- Declare capability state first: FULL / DEGRADED / SEVERELY_IMPAIRED / DISCONNECTED
- Truth-label capability claims: Verified / Inferred / Unknown
- Smallest reversible step first
- No external writes unless I explicitly say: POST NOW

First response must include only:
1) cwd
2) branch
3) local vs worktree mode
4) capability state

Then:
- Reconstruct thread goal from memory + pasted excerpt below
- Return: Recovered Goal, Top 3 actions, and one action to execute now

Pasted excerpt:
[PASTE EXCERPT]
```

## 2) Linear-Heavy Recovery Template

```md
Linear recovery restart.

Incident context:
Prior Linear/Codex activity may include stale or replayed outputs. Assume partial continuity loss.

Rules:
- Capability state first
- Truth labels on all capability-critical claims
- Draft-only policy for Linear updates unless I say: POST NOW

First response:
1) capability state
2) can read BIT-33? (Verified/Inferred/Unknown)
3) can read BIT-38? (Verified/Inferred/Unknown)
4) can create draft comment text without posting? (Verified/Inferred/Unknown)

Then do:
- Reconstruct objective from pasted context
- Propose one smallest reversible action
- Execute only read/summarize actions unless POST NOW

Pasted context:
[PASTE EXCERPT]
```

## 3) GitHub/PR-Heavy Recovery Template

```md
GitHub/PR recovery restart.

Context:
Prior thread continuity may be degraded. Do not assume old approvals/results are still valid.

Rules:
- Capability state first
- Truth labels required
- No push/merge/create-comment unless explicitly authorized

First response:
1) cwd
2) branch
3) repo remote URL
4) local dirty/clean status
5) open PR status availability (Verified/Inferred/Unknown)

Then:
- Reconstruct goal from pasted context
- Return one safe next action (read-only preferred first)

Pasted context:
[PASTE EXCERPT]
```

## 4) Incident-Triage Recovery Template

```md
Incident triage mode.

Start in:
- Capability state: DEGRADED (upgrade only after evidence)

Task:
- Build pass/fail matrix from current signals
- Separate Verified vs Inferred cleanly
- Recommend one immediate containment action

Output format:
1) State line
2) Incident facts (Verified)
3) Hypotheses (Inferred)
4) Unknowns
5) One containment action + one validation step
```
