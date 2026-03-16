# Bitpod-App Master Recovery Prompt (Large Bootstrap)

```md
DO NOT TREAT THIS AS A COMMAND LIST. Treat it as context + operating rules.

Recovery Context
This thread is a controlled restart after a multi-factor incident involving Codex thread instability and connector turbulence (Linear/GitHub-triggered workflow noise, disappearing/reappearing threads, delayed outputs, and intermittent submit failures). Prior thread history may be incomplete, stale, or partially replayed.

Primary Goal
Continue execution safely from `/Users/cjarguello/BitPod-App` with strict verification discipline, while rebuilding reliable continuity for pending Linear/GitHub-heavy work.

Mandatory Operating Rules
1) Capability declaration first:
   - FULL / DEGRADED / SEVERELY_IMPAIRED / DISCONNECTED
2) Truth labels on capability-critical claims:
   - Verified / Inferred / Unknown
3) Smallest reversible action first.
4) No external writes (especially Linear comments/updates) unless I explicitly say: POST NOW.
5) If an action fails, show exact error text before proposing workaround.
6) Outputs from old/dead/reappeared threads are UNTRUSTED until re-verified here.

Incident Facts Already Established
- Dead/red thread behavior occurred.
- At least one disappeared thread later reappeared and emitted delayed output.
- Message submission failed in-thread with “Error submitting message” after reconnect period.
- Linear MCP could still read/write in separate checks, suggesting mixed-state failure modes.
- A “perfect storm” hypothesis is active: connector/session instability + stale thread/client state + heavy fan-out.

Known Reference Issues
- BIT-33: https://linear.app/bitpod-app/issue/BIT-33/implement-capability-state-truth-label-incident-protocol-for-all
- BIT-38: https://linear.app/bitpod-app/issue/BIT-38/connector-smoke-isolate-dead-codex-thread-failures

Known Reference PR
- BIT-36 merged PR: https://github.com/BitPod-App/bitpod-tools/pull/3

Known Local Artifacts to Read First
- /Users/cjarguello/BitPod-App/bitpod-tools/docs/capability_state_truth_label_incident_protocol.md
- /Users/cjarguello/BitPod-App/bitpod-tools/docs/handoff_2026-03-03_codex_linear_bridge_incident.md
- /Users/cjarguello/BitPod-App/bitpod-tools/docs/thread_restart_linear_prompts_2026-03-03.md
- /Users/cjarguello/BitPod-App/bitpod-tools/docs/thread_restart_linear_prompts_2026-03-03.md

Git/Repo Snapshot Constraints (carry forward, then re-verify)
- bitpod-tools branch context seen: codex/bit-36-bridge-taylor-runbooks
- ahead snapshots observed:
  - bitpod-tools: 0 3
  - bitpod: 0 1
  - bitpod-docs: 0 1
- WIP caution:
  - bitpod has active WIP and must not be discarded.

Execution Request
Step A) Verify environment anchors only:
- cwd
- current branch
- local vs worktree mode
- active capability state

Step B) Reconstruct and report:
- Verified table: what is proven now in this session
- Inferred table: likely but unproven
- Unknown table: missing evidence

Step C) Run minimal continuity gate:
- confirm ability to read BIT-33 and BIT-38
- confirm ability to inspect local git status (no changes yet)
- do not post externally unless POST NOW

Step D) Propose exactly ONE next action and execute it.

Deliverable format required
1) Capability state line
2) Verified/Inferred/Unknown table
3) Next single action
4) Result (or exact error + fallback)

Safety Fence
If instability recurs (submit failure/replay/disappearance), stop broad execution and switch to incident capture mode:
- record timestamp
- capture exact error string
- classify state downgrade
- request explicit operator decision before continuing.
```
