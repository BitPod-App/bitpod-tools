# Vera OpenClaw Adapter Layer

This directory is intentionally secondary.

Canonical Vera home:
- `/Users/cjarguello/BitPod-App/bitpod-tools/tools/taylor01/core/agents/vera`

This adapter exists only to map the portable Vera core into a future OpenClaw-compatible runtime surface.

Current truth as of 2026-04-17:
- there is not yet a separately verified installable OpenClaw package/codebase in the active workspace
- Vera's portable core now exists independently of OpenClaw
- OpenClaw-specific embodiment remains follow-on wiring work, not Vera's canonical definition

Hard adapter rules:
- preserve exact verdicts: `PASSED`, `FAILED`, `NO_VERDICT`
- preserve exact artifacts: `verification_report.md`, `manifest.json`
- preserve the separate `Vera QA - Runtime` secret boundary
- do not move Vera's identity/behavior contract into an OpenClaw-only format

Read next:
- `ADAPTER.md`
