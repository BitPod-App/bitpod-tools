# New Thread Prompts (Linear Recovery)

## 1) Primary Prompt (use first in new thread)

```md
Context: this is a recovery thread because prior Codex threads were damaged during a period of Linear instability/downtime and reconnect attempts. Some prior thread history may be incomplete or missing.

Goal: continue `/tools/linear` execution safely and finish incident isolation + documentation continuity.

Constraints:
- Use explicit truth labels on capability-critical claims: Verified / Inferred / Unknown.
- Declare capability state at the top: FULL / DEGRADED / SEVERELY_IMPAIRED / DISCONNECTED.
- If Linear actions fail, run a minimal smoke test first and report exact failure text before proposing fixes.
- Avoid broad speculative changes; prioritize smallest reversible step.

Immediate tasks:
1. Fetch and summarize current state of:
   - BIT-33: https://linear.app/bitpod-app/issue/BIT-33/implement-capability-state-truth-label-incident-protocol-for-all
   - BIT-38: https://linear.app/bitpod-app/issue/BIT-38/connector-smoke-isolate-dead-codex-thread-failures
2. Confirm comments posted today are present on both issues.
3. Produce a short pass/fail matrix plan for submit-path failures (`short`, `medium`, `long` message, pre/post app restart).
4. Recommend next single action and execute it.

Background evidence:
- After disconnect/reconnect of Linear access, thread sends failed with `Error submitting message`.
- Same message failed again on retry.
- There was ~1 hour between reconnect and failed send, so reconnect may be a factor but not necessarily sole cause.
```

## 2) Pending Appendix Prompt (attach after primary prompt)

```md
Appendix: pending git state snapshot to keep context aligned.

Repo: /Users/cjarguello/BitPod-App/bitpod-tools
- Branch: codex/bit-36-bridge-taylor-runbooks
- PR #3 merged
- Uncommitted files:
  - .codex/
  - docs/capability_state_truth_label_incident_protocol.md
  - docs/handoff_2026-03-03_codex_linear_bridge_incident.md
  - gpt_bridge/.env.bak.20260303-022909
  - gpt_bridge/.env.save

Cross-repo (unmerged vs local main):
- bitpod-tools: main...HEAD = 0 3
- bitpod: main...HEAD = 0 1
- bitpod-docs: main...HEAD = 0 1

Cross-repo working tree status:
- bitpod: active modified/untracked work in progress (do not discard)
- bitpod-docs: clean
- bitpod-taylor-runtime: clean
- bitregime-core: clean

Request:
- Re-verify this snapshot before taking actions.
- Do not delete or reset any non-noise changes.
```
