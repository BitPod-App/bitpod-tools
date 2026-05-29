# Vera/Hermes Telegram QA-Repair Lane Boundary v1

Status: Active governance doc
Owner: Taylor01 / CJ
Related: BIT-398, BIT-374 (iceboxed Hermes-native orchestration proof reference)
Last updated: 2026-05-29
Scope: Defines when and how Vera/Hermes may be used as a repair and QA lane, and what that lane must not become

## Purpose

The primary Taylor01 coding runtime is Codex on `mini-01`, operated via the MacBook Codex App cockpit. Vera/Hermes and the Telegram gateway are valuable for a narrow set of QA, diagnosis, and repair scenarios — but they must not drift into becoming the primary coding runtime.

This document defines the permitted lane, the hard boundary, and the cost/spending rules.

## Permitted: Vera/Hermes QA-Repair Lane

Vera or Hermes-native sessions may be used for:

1. **Log summary and triage** — Reading and summarizing logs, error traces, or service state when Codex cockpit is not clearly in Mini-remote mode or is unavailable.
2. **Repair suggestions** — Providing bounded diagnostic or fix suggestions based on observed state, without executing changes.
3. **QA passes on delivered artifacts** — Bounded review of PRs, commits, or docs when an independent QA pass is needed and Vera is the assigned reviewer.
4. **Telegram-side diagnosis** — Confirming that Hermes/Telegram services are reachable and functioning correctly when there is reason to doubt it.
5. **Service health snapshot** — Quick `hermes status`, broker health, or route check when mini-side state is unclear.

These are **rare-use** access patterns. They supplement, not replace, the Codex cockpit.

## Forbidden: What This Lane Must Not Become

The QA-repair lane must not expand into:

- **Primary coding runtime**: Vera/Hermes must not write, commit, or push production code as the default path. Codex on mini-01 is the primary coding runtime.
- **Unbounded orchestration**: Running multi-step orchestration chains via Hermes that bypass Codex permission/approval flow.
- **Secret management**: Storing, rotating, or inspecting secrets through Telegram or Hermes sessions.
- **Production deployments**: Triggering launchctl, gateway restarts, or service config changes through Hermes without Codex oversight.
- **Persistent workaround**: Using Telegram/Hermes as a workaround when the real fix is repairing Codex cockpit access.

If a workflow is consistently being routed through Hermes/Telegram instead of Codex, treat it as a Codex cockpit health problem to fix, not a reason to expand Hermes authority.

## API Spending Rules

- Vera/Hermes QA-repair sessions must stay within bounded cost expectations.
- One-off diagnosis or QA passes are acceptable.
- Do not leave long-running Hermes sessions open for tasks that should be done through Codex.
- Cron-scheduled Hermes tasks must have explicit cost justification and be reviewed periodically.
- If Anthropic API rate limits are active (as of 2026-05-28: until 2026-06-01 00:00 UTC), route Taylor01 Hermes tasks to OpenAI-compatible models or defer — do not silently fail or burn cost trying to retry against rate-limited quota.

## Telegram/Dashboard Reachability

Telegram/dashboard reachability is useful only if it materially improves repair access.

Rules:
- The Hermes Dashboard at `https://mini-01.tail1c36c1.ts.net/` provides service status visibility — use it for status checks.
- The Telegram gateway is useful for quick pings, health checks, and short-form QA summary delivery.
- Do not use Telegram as a development terminal (long shell sessions, file mutations, extended code generation).

## Relationship to Codex Cockpit

| Scenario | Preferred surface | Escalate to Hermes/Vera if |
| -- | -- | -- |
| Code changes, PRs, commits | Codex on mini-01 | Never: use Codex or fix Codex access |
| Service health check | Codex shell | Codex cockpit unreachable |
| PR QA review | Vera via Hermes | PR ready and review is assigned to Vera |
| Log triage | Codex shell | Codex cockpit unreachable |
| Quick status ping | Either | N/A |
| Memory/context queries | Taylor01 Hermes | N/A (Hermes memory is native here) |

## Relationship to BIT-374 (Hermes-Native Orchestration)

BIT-374 (Hermes-native orchestration proof: Taylor01 cost-steward delegation) is iceboxed.

The iceboxed work explored full Hermes-native orchestration as the primary path. That is not the current operating model.

This QA-repair lane is narrower than BIT-374 envisioned: it is a diagnostic supplement, not an alternative primary runtime.

If a future decision explicitly justifies Hermes-native orchestration for a specific bounded purpose, it should be addressed as a new issue, not by re-expanding this lane.

## Operator Actions To Keep This Boundary Healthy

1. **Review cron jobs in Hermes regularly**: ensure scheduled jobs are bounded and have cost justification.
2. **Check Codex cockpit health before defaulting to Telegram**: if Telegram is being used repeatedly for tasks that Codex should handle, fix the cockpit access.
3. **Do not add new Hermes MCP toolsets for coding work**: keep the Taylor01 Hermes `platform_toolsets.telegram` list narrow.
4. **If Vera is doing repeated coding work through Hermes**: escalate to CJ — this is a drift signal.
