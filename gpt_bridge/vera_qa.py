#!/usr/bin/env python3
"""Compatibility wrapper for the canonical Vera GPT Bridge adapter."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.taylor01.adapters.openai.vera.bridge_runtime import *  # noqa: F401,F403
from tools.taylor01.adapters.openai.vera.bridge_runtime import main


if __name__ == '__main__':
    raise SystemExit(main())
