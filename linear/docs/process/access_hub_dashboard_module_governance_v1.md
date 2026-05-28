# Access Hub Dashboard Module Governance v1

**Owner:** Taylor01 (T01 Agents Doctor)
**Created:** 2026-05-28
**Related:** BIT-438, BIT-329, BIT-463, PR #36
**Status:** Active — governs all current and future Taylor01 Dashboard module interactions with Access Hub

---

## Purpose

Define the stable consume-only boundary so future Taylor01 Dashboard modules can safely surface Access Hub diagnostics and status **without turning Access Hub into a replacement control plane or cockpit**.

This document is the canonical reference for the boundary established after PR #36 (Prompt Command Center v1) merged and the question of how dashboard surfaces should relate to Access Hub was left as a follow-up.

---

## Access Hub Scope (unchanging)

Access Hub (`tools/taylor01_control/`) is:

- **A diagnostics and recovery surface.** It surfaces health, route state, and repair actions.
- **A status-cue surface.** It provides authoritative runtime cues (SSH tunnel alive, Hermes gateway state, Honcho broker health, Tailscale route health).
- **A break-glass recovery tool.** When the normal Mini-first Codex path is unavailable, Access Hub provides a minimal recovery path.

Access Hub is **not**:

- A cockpit or primary control plane for day-to-day operator work.
- A launch surface for prompts, commands, or agent tasks.
- A replacement for the MacBook Codex App as the operator UI.
- A general dashboard product.

The Tailscale Serve route is `/access-hub` (proxied to `:28881`), intentionally separated from the root `/` (Hermes Dashboard) and `/prompt` (Prompt Command Center).

---

## Consume-Only Patterns (permitted)

Dashboard modules may consume Access Hub in the following ways:

### 1. Status badge / health widget
A module may embed or display a summary of Access Hub-reported health — for example, a compact indicator showing "Honcho: healthy | SSH: up | Gateway: running." The data source is the `/api/health` or `/api/status` endpoint of Access Hub, and the widget is read-only.

### 2. Direct link to Access Hub
Any dashboard module may include a hyperlink or button that opens the full Access Hub UI at `https://mini-01.tail1c36c1.ts.net/access-hub`. This is always acceptable — the operator navigates to Access Hub; the module does not replace it.

### 3. Show-cue surface
A module may read and display the current Taylor01 execution cue (the mini-01 execution path indicator) from Access Hub as informational context. No mutation permitted.

### 4. Error escalation pointer
When a module encounters a launch failure or runtime problem it cannot resolve, it may surface an "Open Access Hub" link or button as a recovery action. This is the correct pattern: the module escalates to Access Hub diagnostics rather than trying to diagnose inline.

---

## Forbidden Patterns (not permitted)

### 1. Using Access Hub as the command surface
Dashboard modules must not route operator commands (prompt launches, agent starts, task delegations) through Access Hub endpoints. Access Hub repair/action endpoints are scoped to Access Hub's own health remediation — not general command dispatch.

### 2. Embedding Access Hub's full UI as an iframe or panel
Embedding the full Access Hub UI inside another dashboard module scope-creeps Access Hub into a cockpit. Modules link to it; they do not host it.

### 3. Reading Access Hub state to gate prompt/launch decisions
A module must not gate its GO button, copy actions, or launch state on Access Hub health data. Access Hub is diagnostic; the PCC launch route's own mini-01 host check and bridge mode guard handle launch gating independently.

### 4. Writing to Access Hub state from another module
Access Hub maintains its own runtime state (logs, SSH probe cache, health history). No dashboard module may mutate or inject state into Access Hub from outside Access Hub's own server context.

### 5. Replacing Access Hub with a new broader control surface
If a proposed dashboard module would subsume everything Access Hub does and add command dispatch on top, that is a new product — not a dashboard module. Scope it separately and do not call it a dashboard module consuming Access Hub.

---

## PCC ↔ Access Hub Relationship

The Prompt Command Center (`/prompt`) and Access Hub (`/access-hub`) are sibling services, not a parent–child hierarchy.

| PCC | Access Hub |
|---|---|
| Operator command surface | Diagnostic / recovery surface |
| Generates prompts, copies to clipboard | Reports route health, SSH tunnel state, Honcho health |
| Mini-hosted, mini-launched | Mini-hosted, read from MacBook |
| GO bridge: future, behind operator token | Repair actions: restricted to known safe remediations |
| "What do I run next?" | "Is the runtime healthy?" |

PCC may show a compact Access Hub health indicator (consume-only pattern #1) to help the operator confirm the runtime is ready before running a prompt. That is the entire sanctioned integration between these two surfaces in v1.

---

## Future Module Guidance

When adding a new Taylor01 Dashboard module that might want to surface runtime health:

1. **Check if a consume-only pattern covers it.** Reading status and linking to Access Hub is always fine.
2. **If you want to run an action**, ask: is this action scoped to Access Hub's own health (SSH probe, gateway restart cue)? If yes, add it to Access Hub itself. If no, it does not belong in Access Hub at all.
3. **If scope ambiguity arises**, the default is: Access Hub stays diagnostics-only, and the new capability gets its own surface.
4. **Document the module's Access Hub dependency** in the relevant Linear ticket, referencing this doc and the specific consume-only pattern used.

---

## References

- [BIT-438 — Dashboard module governance: Access Hub consume-only boundary](https://linear.app/bitpod-app/issue/BIT-438/dashboard-module-governance-access-hub-consume-only-boundary)
- [BIT-329 — T01 Access Hub v1: authority boundaries and same-backend remote access](https://linear.app/bitpod-app/issue/BIT-329/t01-access-hub-v1-authority-boundaries-and-same-backend-remote-access)
- [BIT-463 — Prompt Command Center v2/3: safe GO-to-Codex App injection plan](https://linear.app/bitpod-app/issue/BIT-463/prompt-command-center-v23-safe-go-to-codex-app-injection)
- `docs/pcc_go_bridge_plan_v1.md` — PCC v2/3 bridge security and contract plan
- `linear/docs/process/taylor01_boundary_map_v1.md` — Taylor01 portable vs. adapter boundary map
