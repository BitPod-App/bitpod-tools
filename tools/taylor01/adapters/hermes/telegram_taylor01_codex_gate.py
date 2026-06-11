#!/usr/bin/env python3
"""Read-only executable gate for the Telegram -> Hermes Taylor01 -> Codex route.

This preflight intentionally does not start Telegram polling, mutate Hermes home,
run Codex, or claim a working runtime. It only verifies whether the local machine
has the minimum observable pieces required before BIT-483-style heartbeat work can
truthfully proceed.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Mapping, Sequence

REQUIRED_ROUTE = "Telegram -> Hermes Agent Taylor01 -> Codex"
DEFAULT_TIMEOUT_SECONDS = 8


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class GateCheck:
    name: str
    status: str
    evidence: str
    command: str | None = None


@dataclass(frozen=True)
class GateReport:
    route: str
    verdict: str
    host: str
    user: str
    home: str
    hermes_home: str
    checks: list[GateCheck]
    manual_or_external: list[str]


def _run_command(cmd: Sequence[str], timeout: int = DEFAULT_TIMEOUT_SECONDS) -> CommandResult:
    try:
        proc = subprocess.run(
            list(cmd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return CommandResult(127, "", f"command not found: {cmd[0]}")
    except subprocess.TimeoutExpired as exc:
        return CommandResult(124, exc.stdout or "", exc.stderr or f"timed out after {timeout}s")
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def _first_line(text: str, limit: int = 240) -> str:
    line = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    return line[:limit]


def _masked_env_presence(env: Mapping[str, str], names: Sequence[str]) -> tuple[bool, str]:
    present = [name for name in names if env.get(name)]
    if present:
        return True, "present without value: " + ", ".join(present)
    return False, "missing: " + ", ".join(names)


def _command_check(name: str, cmd: Sequence[str], ok_detail: str, runner: Callable[[Sequence[str]], CommandResult]) -> GateCheck:
    result = runner(cmd)
    rendered = " ".join(cmd)
    if result.returncode == 0:
        detail = _first_line(result.stdout) or ok_detail
        return GateCheck(name, "PASS", detail, rendered)
    detail = _first_line(result.stderr) or _first_line(result.stdout) or f"exit {result.returncode}"
    return GateCheck(name, "BLOCKED", detail, rendered)


def build_report(
    *,
    env: Mapping[str, str] | None = None,
    runner: Callable[[Sequence[str]], CommandResult] = _run_command,
    hermes_home: str | None = None,
) -> GateReport:
    env = env or os.environ
    home = str(Path.home())
    resolved_hermes_home = hermes_home or env.get("HERMES_HOME") or str(Path(home) / ".hermes")
    user = env.get("USER") or env.get("LOGNAME") or "unknown"
    checks: list[GateCheck] = []

    checks.append(GateCheck(
        "route contract",
        "PASS",
        "active route is Telegram to Hermes Agent Taylor01 to Codex; OpenClaw is historical only",
    ))

    checks.append(GateCheck(
        "canonical Hermes home target",
        "PASS" if Path(resolved_hermes_home).name == ".hermes" else "BLOCKED",
        f"HERMES_HOME target: {resolved_hermes_home}",
    ))

    telegram_present, telegram_evidence = _masked_env_presence(env, ("TELEGRAM_BOT_TOKEN", "HERMES_TELEGRAM_BOT_TOKEN"))
    checks.append(GateCheck(
        "Telegram bot token injection",
        "PASS" if telegram_present else "BLOCKED",
        telegram_evidence,
    ))

    checks.append(_command_check("Hermes CLI available", ["hermes", "--version"], "hermes command returned success", runner))
    checks.append(_command_check("Hermes taylor01 profile visible", ["hermes", "-p", "taylor01", "profile", "show", "taylor01"], "taylor01 profile is addressable", runner))
    checks.append(_command_check("Codex CLI available", ["codex", "--version"], "codex command returned success", runner))

    openclaw_runtime_vars = [name for name in ("OPENCLAW_HOME", "OPENCLAW_GATEWAY_URL", "OPENCLAW_RUNTIME") if env.get(name)]
    checks.append(GateCheck(
        "OpenClaw runtime exclusion",
        "BLOCKED" if openclaw_runtime_vars else "PASS",
        "active OpenClaw runtime env vars present: " + ", ".join(openclaw_runtime_vars) if openclaw_runtime_vars else "no active OpenClaw runtime env vars detected by this gate",
    ))

    manual_or_external = [
        "Telegram bot token remains externally supplied by the operator/secret store; this gate only checks masked presence.",
        "Telegram webhook or polling delivery is not started by this gate.",
        "Hermes task execution and Taylor01 response quality still require a live runtime smoke test.",
        "Codex dispatch from Hermes remains external/manual unless a separate checked-in bridge is invoked and verified.",
    ]
    verdict = "PASS" if all(check.status == "PASS" for check in checks) else "BLOCKED"
    return GateReport(
        route=REQUIRED_ROUTE,
        verdict=verdict,
        host=socket.gethostname(),
        user=user,
        home=home,
        hermes_home=resolved_hermes_home,
        checks=checks,
        manual_or_external=manual_or_external,
    )


def render_markdown(report: GateReport) -> str:
    lines = [
        f"# Hermes-first Telegram/Codex migration gate",
        "",
        f"Route: `{report.route}`",
        f"Verdict: `{report.verdict}`",
        "",
        "## Observed local context",
        "",
        f"- Host: `{report.host}`",
        f"- OS user: `{report.user}`",
        f"- Home: `{report.home}`",
        f"- Hermes home target: `{report.hermes_home}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Evidence | Command |",
        "|---|---:|---|---|",
    ]
    for check in report.checks:
        command = f"`{check.command}`" if check.command else "—"
        evidence = check.evidence.replace("|", "\\|")
        lines.append(f"| {check.name} | `{check.status}` | {evidence} | {command} |")
    lines.extend([
        "",
        "## Still external/manual",
        "",
    ])
    lines.extend(f"- {item}" for item in report.manual_or_external)
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the read-only Hermes-first Telegram/Taylor01/Codex gate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of Markdown.")
    parser.add_argument("--hermes-home", help="Override HERMES_HOME target for preflight checks.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = build_report(hermes_home=args.hermes_home)
    if args.json:
        print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0 if report.verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
