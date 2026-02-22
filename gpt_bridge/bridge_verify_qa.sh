#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <session_id>" >&2
  exit 2
fi

SESSION_ID="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_LOG="${SCRIPT_DIR}/logs/bridge.jsonl"
CHAT_LOG="${SCRIPT_DIR}/logs/chat.jsonl"

python3 - "$SESSION_ID" "$BRIDGE_LOG" "$CHAT_LOG" <<'PY'
import json
import pathlib
import re
import sys
from typing import Any

session_id, bridge_log, chat_log = sys.argv[1:4]

required_header = {
    "MODE": "TAYLOR_QA",
    "CONTRACT_PATH": "~/.agents/skills/taylor/SKILL.md",
}


def load_jsonl(path: str) -> list[dict[str, Any]]:
    p = pathlib.Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            out.append(row)
    return out


def parse_header(text: str) -> dict[str, str]:
    keys = ["MODE", "CONTRACT_PATH", "BUNDLE_PATH", "BUNDLE_SHA256", "SESSION"]
    out: dict[str, str] = {}
    for key in keys:
        m = re.search(rf"(?m)^{key}:\s*(.+?)\s*$", text)
        if m:
            out[key] = m.group(1).strip()
    return out


def parse_footer(text: str) -> dict[str, str]:
    keys = ["TAYLOR_QA_RESULT", "QA_RUN_ID", "QA_OUTPUT_PATH", "BUNDLE_SHA256"]
    out: dict[str, str] = {}
    for key in keys:
        m = re.search(rf"(?m)^{key}:\s*(.+?)\s*$", text)
        if m:
            out[key] = m.group(1).strip()
    return out


checks: list[tuple[bool, str]] = []

chat_events = [e for e in load_jsonl(chat_log) if e.get("session") == session_id]
bridge_events = load_jsonl(bridge_log)

req_event = None
req_header = {}
req_ts = ""
for e in chat_events:
    if e.get("actor") not in {"user", "codex", "system", "agent"}:
        continue
    text = e.get("text")
    if not isinstance(text, str):
        continue
    header = parse_header(text)
    if header.get("MODE") == "TAYLOR_QA":
        req_event = e
        req_header = header
        req_ts = str(e.get("ts", ""))
        break

checks.append((req_event is not None, "Header present in chat log request"))

if req_event:
    checks.append((req_header.get("MODE") == required_header["MODE"], "MODE: TAYLOR_QA present"))
    checks.append((req_header.get("CONTRACT_PATH") == required_header["CONTRACT_PATH"], "CONTRACT_PATH canonical"))
    sha = req_header.get("BUNDLE_SHA256", "")
    checks.append((bool(re.fullmatch(r"[a-fA-F0-9]{64}", sha)), "BUNDLE_SHA256 present and valid"))
    checks.append((req_header.get("SESSION") == session_id, "SESSION matches verifier argument"))
else:
    sha = ""

bridge_match = None
for row in bridge_events:
    meta = row.get("request", {}).get("meta", {})
    if not isinstance(meta, dict):
        continue
    if meta.get("session") != session_id:
        continue
    message = row.get("request", {}).get("message", "")
    if not isinstance(message, str):
        continue
    if "MODE: TAYLOR_QA" in message:
        bridge_match = row
        break

checks.append((bridge_match is not None, "Header present in bridge request log"))

# GPT response after request exists
gpt_events = [e for e in chat_events if e.get("actor") == "gpt" and isinstance(e.get("text"), str)]
resp_event = None
if req_event and gpt_events:
    for e in gpt_events:
        if str(e.get("ts", "")) >= req_ts:
            resp_event = e
            break
checks.append((resp_event is not None, "GPT response exists after QA request"))

footer = parse_footer(resp_event.get("text", "") if resp_event else "")
checks.append(("TAYLOR_QA_RESULT" in footer, "Result footer contains TAYLOR_QA_RESULT"))
checks.append(("QA_RUN_ID" in footer, "Result footer contains QA_RUN_ID"))
checks.append(("QA_OUTPUT_PATH" in footer, "Result footer contains QA_OUTPUT_PATH"))
checks.append(("BUNDLE_SHA256" in footer and bool(re.fullmatch(r"[a-fA-F0-9]{64}", footer.get("BUNDLE_SHA256", ""))), "Result footer contains valid BUNDLE_SHA256"))

if sha and footer.get("BUNDLE_SHA256"):
    checks.append((footer.get("BUNDLE_SHA256") == sha, "Footer hash matches request hash"))
else:
    checks.append((False, "Footer hash matches request hash"))

qa_path = pathlib.Path(footer.get("QA_OUTPUT_PATH", "")) if footer.get("QA_OUTPUT_PATH") else None
if qa_path:
    checks.append((qa_path.exists(), "QA_OUTPUT_PATH exists"))
    checks.append(((qa_path / "qa_review.md").exists(), "qa_review.md exists"))
    checks.append(((qa_path / "acceptance_criteria_checklist.md").exists(), "acceptance_criteria_checklist.md exists"))
    checks.append(((qa_path / "risk_notes.md").exists(), "risk_notes.md exists"))
else:
    checks.append((False, "QA_OUTPUT_PATH exists"))
    checks.append((False, "qa_review.md exists"))
    checks.append((False, "acceptance_criteria_checklist.md exists"))
    checks.append((False, "risk_notes.md exists"))

all_ok = True
for ok, label in checks:
    print(f"{'OK' if ok else 'FAIL'}: {label}")
    if not ok:
        all_ok = False

if req_header:
    print(f"INFO: Request bundle path = {req_header.get('BUNDLE_PATH', '<missing>')}")
    print(f"INFO: Request bundle sha256 = {req_header.get('BUNDLE_SHA256', '<missing>')}")
if footer:
    print(f"INFO: QA result = {footer.get('TAYLOR_QA_RESULT', '<missing>')}")
    print(f"INFO: QA output path = {footer.get('QA_OUTPUT_PATH', '<missing>')}")

sys.exit(0 if all_ok else 1)
PY
