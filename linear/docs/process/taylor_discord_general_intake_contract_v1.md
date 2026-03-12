# Taylor Discord General Intake Contract v1

Date: 2026-03-12  
Primary issue: [BIT-96 — Stand up Taylor Discord conversational intake path for real agent acceptance](https://linear.app/bitpod-app/issue/BIT-96/stand-up-taylor-discord-conversational-intake-path-for-real-agent)  
Related issue: [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command)

## Objective

Define the minimum truthful Discord intake contract for Taylor as a real operator-facing agent.

## Intended truth

- Taylor should be conversationally reachable in Discord `#general`.
- CJ should be able to talk to Taylor there about pretty much anything relevant to BitPod operations, planning, status, and coordination.
- Taylor should not be limited to narrow command-reply behavior to count as real enough.

## Why this matters

- [BIT-92 — Stand up minimum Phase 4 agent team in practice (Taylor + Vera + engineering lane(s))](https://linear.app/bitpod-app/issue/BIT-92/stand-up-minimum-phase-4-agent-team-in-practice-taylor-vera) already proved a minimum team baseline.
- [BIT-86 — Real Discord acceptance for team session contract and bridge command surface](https://linear.app/bitpod-app/issue/BIT-86/real-discord-acceptance-for-team-session-contract-and-bridge-command) now functions as the stronger closure gate for whether that team is actually reachable through a real session surface.
- If Taylor is not usable in `#general`, Discord risks remaining a structured event board rather than a real operator-facing agent surface.

## Minimum contract

### Surface

- Primary human-facing conversational surface: `#general`
- Structured specialist channels remain valid for follow-through:
  - `#10-plan`
  - `#20-decide`
  - `#30-build`
  - `#40-review-qa`
  - `#50-release`
  - `#60-incidents`

### Intake behavior

- Taylor should respond when directly addressed in `#general`.
- Direct address may be mention-based, name-based, or command-assisted, but plain conversational use must remain possible.
- Taylor should handle broad operator prompts, not only predeclared task verbs.
- If a request belongs in a specialist lane, Taylor may route or reframe it, but should still respond coherently in `#general`.

### Response behavior

- Taylor should answer with groundedness:
  - observed
  - inferred
  - unknown
- Taylor should maintain continuity across a short conversational exchange.
- Taylor should provide a useful next action, recommendation, or decision frame when appropriate.
- Taylor should avoid collapsing into a brittle help-menu or command list unless the user is explicitly asking for commands.

## Transitional allowance

- Specialist channels may continue to carry structured artifacts and automation output.
- Taylor may still be transitional in runtime embodiment.
- The transitional state is acceptable only if the operator-facing truth in `#general` is already real enough to use.

## Explicit non-pass conditions

This contract is not satisfied if any of the following are true:

- Discord only works as a webhook/event sink.
- Taylor can only be exercised through highly specific command syntax.
- Taylor only works in specialist channels but not `#general`.
- Taylor cannot sustain a short clarifying conversation in Discord.

## Current evidence status

- `Verified`: current live Discord config proves webhook/event routes.
- `Verified`: current repo-side Discord architecture already models structured channels.
- `Verified`: current repo-side evidence does not yet prove a live Taylor conversational intake path in `#general`.
- `Inferred`: the intended truth for closure is stronger than the currently verified runtime state.
