# Handoff Summary (2026-03-03)

## Context

Primary incident: Codex threads turning red/dead and message submit failures during a period of high task fan-out, reconnects, and integration churn.

## Verified Current State

- Linear MCP is reachable from local tooling and can read/write issues/comments.
- `BIT-33` and `BIT-38` now include incident evidence updates and test protocol comments.
- Bridge GPT endpoint is reachable at `https://gpt-bridge.bitpod.app/ask`.
- Bridge recovered after OpenAI key correction (`ack` observed).
- Taylor runtime responds in Zulip (alive, replying).
- Environment cleanup target already enforced earlier: only `bitpod-app` and `bitpod-app-backup-2026-03-02` should remain as active environments.

## New Evidence Added Tonight

- After disconnect/reconnect of Linear access, sends in an active Codex thread failed with `Error submitting message`.
- Retry of same long message also failed.
- There was ~1 hour delay between reconnect and failed send, so reconnect is likely a factor, not necessarily the sole cause.

## Working Root-Cause Model (Truth-Labeled)

- Verified: submit path can fail while compose path still works (`Error submitting message`).
- Inferred (medium-high): stale/corrupted thread client state after reconnect contributes strongly.
- Inferred (medium): connector/session mismatch after auth refresh can amplify failures.
- Inferred (medium): long payload + timing edge case can trigger or worsen failures.

## Issues Updated

- `BIT-33`: protocol + threat framing and this incident evidence.
- `BIT-38`: smoke-test extension to isolate connector vs thread-state vs payload/timing.

## Tomorrow: Fast Follow-Up Plan

1. Run pass/fail matrix in a fresh session:
   - short message in new thread
   - medium message
   - long message (similar to failing size)
2. Restart Codex app and repeat the same 3 sends.
3. Record outcomes in `BIT-38` as a table:
   - pre-restart vs post-restart
   - short/medium/long
4. If failures are thread-specific, archive/quarantine affected threads and continue in clean threads.
5. Keep capability-state declaration at top of execution threads (`FULL/DEGRADED/SEVERELY_IMPAIRED/DISCONNECTED`).

## Copy/Paste Block for New Thread

```md
Continuing incident follow-up from 2026-03-03.

Known evidence:
- Some Codex threads failed on submit with `Error submitting message` after Linear reconnect.
- Failure repeated on retry; not a single-click miss.
- Linear MCP itself could still read/write issues.

Current hypothesis: perfect storm of connector/session refresh + stale thread state + payload/timing edge case.

Today’s objective:
1) Run short/medium/long message smoke in a fresh thread.
2) Restart app and repeat.
3) Post pass/fail matrix to BIT-38 and classify root-cause bucket.
```
