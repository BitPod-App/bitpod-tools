#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from linear.scripts.refresh_vera_qa_gate_runtime_env import (
        DEFAULT_OUTPUT_ENV,
        parse_env_file,
    )
    from linear.src.service import github_app_installation_token_from_env
except ModuleNotFoundError:
    from refresh_vera_qa_gate_runtime_env import DEFAULT_OUTPUT_ENV, parse_env_file
    from service import github_app_installation_token_from_env


def load_runtime_env(path: str) -> Dict[str, str]:
    values = parse_env_file(path)
    values.pop("GH_TOKEN", None)
    values.pop("GITHUB_TOKEN", None)
    return values


def shell_export_for_token(token: str) -> str:
    return "export GH_TOKEN=" + "'" + token.replace("'", "'\"'\"'") + "'"


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Mint a short-lived Vera QA Gate GitHub App installation token. "
            "The token is printed for caller-side process env use only; do not store it."
        )
    )
    parser.add_argument("--runtime-env", default=DEFAULT_OUTPUT_ENV)
    parser.add_argument("--format", choices=("shell", "token"), default="shell")
    args = parser.parse_args(list(argv) if argv is not None else None)

    os.environ.update(load_runtime_env(args.runtime_env))
    token = github_app_installation_token_from_env()
    if args.format == "token":
        print(token)
    else:
        print(shell_export_for_token(token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
