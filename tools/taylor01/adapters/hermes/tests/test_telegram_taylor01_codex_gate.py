from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "telegram_taylor01_codex_gate.py"
spec = importlib.util.spec_from_file_location("telegram_taylor01_codex_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)


def passing_runner(cmd):
    if cmd == ["hermes", "--version"]:
        return gate.CommandResult(0, "hermes 1.0\n", "")
    if cmd == ["hermes", "-p", "taylor01", "profile", "show", "taylor01"]:
        return gate.CommandResult(0, "profile: taylor01\n", "")
    if cmd == ["codex", "--version"]:
        return gate.CommandResult(0, "codex 1.0\n", "")
    return gate.CommandResult(99, "", "unexpected command")


def test_gate_passes_only_with_canonical_home_token_hermes_profile_codex_and_no_openclaw():
    report = gate.build_report(
        env={"USER": "tester", "TELEGRAM_BOT_TOKEN": "super-secret-token-value"},
        runner=passing_runner,
        hermes_home="/tmp/example/.hermes",
    )

    assert report.verdict == "PASS"
    assert report.route == "Telegram -> Hermes Agent Taylor01 -> Codex"
    assert all(check.status == "PASS" for check in report.checks)
    assert "super-secret-token-value" not in gate.render_markdown(report)


def test_gate_blocks_without_secret_and_with_openclaw_runtime_env():
    report = gate.build_report(
        env={"USER": "tester", "OPENCLAW_HOME": "/tmp/openclaw"},
        runner=passing_runner,
        hermes_home="/tmp/example/.hermes",
    )

    statuses = {check.name: check.status for check in report.checks}
    assert report.verdict == "BLOCKED"
    assert statuses["Telegram bot token injection"] == "BLOCKED"
    assert statuses["OpenClaw runtime exclusion"] == "BLOCKED"


def test_gate_blocks_ticket_shaped_hermes_home():
    report = gate.build_report(
        env={"USER": "tester", "TELEGRAM_BOT_TOKEN": "super-secret-token-value"},
        runner=passing_runner,
        hermes_home="/tmp/example/.hermes-bit472",
    )

    statuses = {check.name: check.status for check in report.checks}
    assert report.verdict == "BLOCKED"
    assert statuses["canonical Hermes home target"] == "BLOCKED"
