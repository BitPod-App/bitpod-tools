# Vera OpenClaw Closure Layer

This directory is historical and intentionally secondary.

Canonical Vera home:
- `tools/taylor01/core/agents/vera`

OpenClaw is not a fallback, alternate runtime, or future target for Vera. This adapter layer is retained only to explain older mapping assumptions and prevent stale OpenClaw residue from being mistaken for active strategy.

Current truth as of 2026-05-13:

- Vera's portable core exists independently of OpenClaw.
- Hermes-first is the preferred execution path owner.
- OpenClaw-specific embodiment is canceled unless CJ explicitly opens a new closure/cleanup ticket.
- Do not revive OpenClaw as Vera's canonical definition, runtime package, or secret boundary.

Hard closure rules:

- preserve exact verdicts if reading old mapping material: `PASSED`, `FAILED`, `NO_VERDICT`
- preserve exact artifacts if reading old mapping material: `verification_report.md`, `manifest.json`
- preserve the separate `Vera QA - Runtime` secret boundary
- do not move Vera's identity/behavior contract into an OpenClaw-only format
- do not add new OpenClaw fallback language

Read next:
- `ADAPTER.md`
