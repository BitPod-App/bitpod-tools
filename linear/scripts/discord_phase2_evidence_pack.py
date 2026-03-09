#!/usr/bin/env python3
"""Generate a single Phase 2 Discord evidence pack.

Runs webhook smoke + parity matrix (dry-run or live) and writes one markdown
artifact suitable for Linear issue comments/attachments.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_ROUTES = ["ops_status", "build", "review_qa", "release", "incidents"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build Discord Phase 2 evidence pack")
    ap.add_argument("--config", required=True, help="Path to Discord config JSON")
    ap.add_argument("--out", required=True, help="Markdown evidence output path")
    ap.add_argument("--live", action="store_true", help="Run live webhook checks")
    ap.add_argument("--timeout", type=float, default=8.0, help="HTTP timeout seconds")
    return ap.parse_args()


def mask_url(url: str) -> str:
    if not url:
        return "<missing>"
    if len(url) < 24:
        return "<short-url>"
    return f"{url[:22]}...{url[-6:]}"


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    data.setdefault("webhooks", {})
    data.setdefault("discord", {})
    data["discord"].setdefault("server_name", "")
    data["discord"].setdefault("server_id", "")
    data["discord"].setdefault("channels", {})
    return data


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def build_md(
    cfg_path: Path,
    cfg: dict[str, Any],
    smoke_rc: int,
    smoke_out: str,
    parity_rc: int,
    parity_out: str,
    parity_report: Path,
    live: bool,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    webhooks = cfg.get("webhooks", {})
    discord = cfg.get("discord", {})
    channels = discord.get("channels", {})

    lines: list[str] = [
        "# Discord Phase 2 Evidence Pack",
        "",
        f"- UTC: {ts}",
        f"- Mode: {'LIVE' if live else 'DRY_RUN'}",
        f"- Config: `{cfg_path}`",
        "",
        "## Discord Target Map (sanitized)",
        "",
        "| Route | Channel Name | Channel ID | Webhook |",
        "|---|---|---|---|",
    ]

    for route in REQUIRED_ROUTES:
        ch = channels.get(route, {})
        ch_name = ch.get("name", "")
        ch_id = ch.get("id", "")
        hook = mask_url(webhooks.get(route, ""))
        lines.append(f"| {route} | {ch_name or '<unset>'} | {ch_id or '<unset>'} | {hook} |")

    lines.extend(
        [
            "",
            "## Command Results",
            "",
            "### Smoke Command",
            f"- Exit code: `{smoke_rc}`",
            "```text",
            smoke_out or "<no output>",
            "```",
            "",
            "### Parity Matrix Command",
            f"- Exit code: `{parity_rc}`",
            f"- Report path: `{parity_report}`",
            "```text",
            parity_out or "<no output>",
            "```",
            "",
            "## Summary",
            "",
            f"- Smoke: {'PASS' if smoke_rc == 0 else 'FAIL'}",
            f"- Parity matrix: {'PASS' if parity_rc == 0 else 'FAIL'}",
            "- Attach this file plus channel screenshots to BIT-59/BIT-30.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    cfg_path = Path(args.config).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cfg = load_config(cfg_path)
    mode_flag = [] if args.live else ["--dry-run"]
    parity_report = out_path.with_name(out_path.stem + "_matrix.md")

    smoke_cmd = [
        "python3",
        str(root / "scripts" / "discord_webhook_smoke.py"),
        "--config",
        str(cfg_path),
        "--timeout",
        str(args.timeout),
        *mode_flag,
    ]
    parity_cmd = [
        "python3",
        str(root / "scripts" / "discord_parity_matrix_runner.py"),
        "--config",
        str(cfg_path),
        "--report",
        str(parity_report),
        "--timeout",
        str(args.timeout),
        *mode_flag,
    ]

    smoke_rc, smoke_out = run_cmd(smoke_cmd)
    parity_rc, parity_out = run_cmd(parity_cmd)

    md = build_md(cfg_path, cfg, smoke_rc, smoke_out, parity_rc, parity_out, parity_report, args.live)
    out_path.write_text(md)

    print(f"WROTE_EVIDENCE {out_path}")
    print(f"WROTE_MATRIX {parity_report}")
    print(f"SUMMARY smoke_rc={smoke_rc} parity_rc={parity_rc}")
    return 0 if smoke_rc == 0 and parity_rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
