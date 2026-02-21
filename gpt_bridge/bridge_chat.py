#!/usr/bin/env python3
"""Chat-oriented relay for GPT Bridge with shared JSONL logging."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ASK_ONCE = SCRIPT_DIR / "ask_once.sh"
DEFAULT_LOG = SCRIPT_DIR / "logs" / "chat.jsonl"
DEFAULT_MEMORY_STORE = SCRIPT_DIR / "logs" / "memory_store.jsonl"
DEFAULT_SESSION_STATE = SCRIPT_DIR / "logs" / "session_state.json"
DEFAULT_MEMORY_POINTER = "memory://bitpod-app/memory_store.jsonl"
IMPORTANT_MEMORY_SUFFIX = "Important BitPod App data: Update your memory"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(log_file: Path, event: dict[str, Any]) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=True) + "\n")


def print_timeline_line(ts: str, speaker: str, text: str) -> None:
    _ = ts  # Timestamp is retained in JSONL logs but hidden from chat output.
    print(f"{speaker}: {text}")


def parse_json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {label} JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} must decode to a JSON object")
    return data


def _load_session_state(state_file: Path = DEFAULT_SESSION_STATE) -> dict[str, Any]:
    if not state_file.exists():
        return {}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _save_session_state(state: dict[str, Any], state_file: Path = DEFAULT_SESSION_STATE) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, ensure_ascii=True), encoding="utf-8")


def _resolve_session(session: str | None, fallback: str = "team") -> str:
    if isinstance(session, str) and session.strip():
        return session.strip()
    state = _load_session_state()
    active = state.get("active_session")
    if isinstance(active, str) and active.strip():
        return active.strip()
    state["active_session"] = fallback
    _save_session_state(state)
    return fallback


def _set_active_session(session: str) -> None:
    state = _load_session_state()
    state["active_session"] = session
    state["updated_ts"] = utc_now_iso()
    _save_session_state(state)


def _extract_mentions(text: str) -> list[str]:
    mentions = [m.lower() for m in re.findall(r"@([A-Za-z0-9_\\-]+)", text)]
    seen: set[str] = set()
    ordered: list[str] = []
    for mention in mentions:
        if mention in seen:
            continue
        seen.add(mention)
        ordered.append(mention)
    return ordered


def _strip_gpt_mentions(text: str) -> str:
    stripped = re.sub(r"@gpt\\b[:,]?\\s*", "", text, flags=re.IGNORECASE).strip()
    if stripped:
        return stripped
    return text.strip()


def _slugify_session_label(text: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "-", text.lower()).strip("-")
    if not base:
        base = "session"
    return f"{base[:32]}-{int(time.time())}"


def build_send_parser(subparsers: argparse._SubParsersAction) -> None:
    send = subparsers.add_parser("send", help="Log user message and call GPT via bridge")
    send.add_argument("message", help="Prompt message")
    send.add_argument("--session", default=None, help="Session id (defaults to active session)")
    send.add_argument("--from", dest="from_actor", default="user", help="Actor label")
    send.add_argument(
        "--task-type",
        default="general",
        choices=["general", "qa_check", "report", "score_check"],
        help="Task type forwarded to ask_once.sh / ask_gpt.py",
    )
    send.add_argument("--max-tokens", type=int, default=1200, help="max_output_tokens hint")
    send.add_argument(
        "--json-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Set constraints.json_only",
    )
    send.add_argument("--model", default=None, help="Optional model override")
    send.add_argument(
        "--context-file",
        action="append",
        default=[],
        help="Path to context text file; can be set multiple times",
    )
    send.add_argument(
        "--context-stdin",
        action="store_true",
        help="Append context from stdin",
    )
    send.add_argument("--meta", default="{}", help="JSON object for meta fields")
    send.add_argument("--log-file", default=str(DEFAULT_LOG), help="JSONL event log file")
    send.add_argument(
        "--memory-store",
        default=str(DEFAULT_MEMORY_STORE),
        help="Persistent memory JSONL store",
    )
    send.add_argument(
        "--memory-items",
        type=int,
        default=8,
        help="Number of latest memory items to inject",
    )
    send.add_argument(
        "--use-memory",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Inject persistent memory into context on send",
    )
    send.add_argument(
        "--show-raw",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Print raw bridge JSON response after formatted GPT text",
    )
    send.add_argument(
        "--auto-recover",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Recover stale unfinalized sessions before sending",
    )
    send.add_argument(
        "--recover-stale-seconds",
        type=int,
        default=900,
        help="Only recover sessions inactive for at least this many seconds",
    )
    send.add_argument(
        "--recover-max-sessions",
        type=int,
        default=8,
        help="Maximum number of stale sessions to recover per send",
    )
    send.add_argument(
        "--recover-extract-max-tokens",
        type=int,
        default=1000,
        help="Extraction max tokens used during auto-recover",
    )
    send.add_argument(
        "--recover-sync-max-tokens",
        type=int,
        default=500,
        help="Sync max tokens used during auto-recover",
    )


def build_post_parser(subparsers: argparse._SubParsersAction) -> None:
    post = subparsers.add_parser("post", help="Log a non-GPT message to the shared chat log")
    post.add_argument("text", help="Message text")
    post.add_argument("--session", default=None, help="Session id (defaults to active session)")
    post.add_argument("--from", dest="from_actor", default="agent", help="Actor label")
    post.add_argument("--log-file", default=str(DEFAULT_LOG), help="JSONL event log file")


def build_tail_parser(subparsers: argparse._SubParsersAction) -> None:
    tail = subparsers.add_parser("tail", help="Show recent chat timeline from log")
    tail.add_argument("--session", default=None, help="Optional session id filter")
    tail.add_argument("--lines", type=int, default=30, help="Number of events to show")
    tail.add_argument("--log-file", default=str(DEFAULT_LOG), help="JSONL event log file")
    tail.add_argument(
        "--follow",
        action="store_true",
        help="Continue polling and print new events",
    )
    tail.add_argument(
        "--poll-seconds",
        type=float,
        default=1.0,
        help="Poll interval for --follow",
    )


def build_end_parser(subparsers: argparse._SubParsersAction) -> None:
    end = subparsers.add_parser(
        "end",
        help="Extract remember-worthy session items, persist them, and sync to GPT",
    )
    end.add_argument("--session", default=None, help="Session id (defaults to active session)")
    end.add_argument("--log-file", default=str(DEFAULT_LOG), help="Session chat JSONL log file")
    end.add_argument(
        "--memory-store",
        default=str(DEFAULT_MEMORY_STORE),
        help="Persistent memory JSONL store",
    )
    end.add_argument(
        "--memory-items",
        type=int,
        default=12,
        help="Maximum memory items to persist from this session",
    )
    end.add_argument(
        "--extract-max-tokens",
        type=int,
        default=1000,
        help="max_output_tokens for memory extraction call",
    )
    end.add_argument(
        "--sync-max-tokens",
        type=int,
        default=500,
        help="max_output_tokens for memory sync call",
    )
    end.add_argument("--model", default=None, help="Optional model override")
    end.add_argument(
        "--sync-to-gpt",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Send extracted memory payload to GPT as a dedicated chat message",
    )
    end.add_argument(
        "--memory-pointer",
        default=DEFAULT_MEMORY_POINTER,
        help="Logical pointer included in GPT memory sync payload",
    )
    end.add_argument(
        "--show-raw",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Print raw extraction/sync JSON responses",
    )
    end.add_argument(
        "--stop-bridge",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Stop bridge after session finalization",
    )


def build_recover_parser(subparsers: argparse._SubParsersAction) -> None:
    recover = subparsers.add_parser(
        "recover",
        help="Recover stale unfinalized sessions from chat logs and sync memory",
    )
    recover.add_argument("--log-file", default=str(DEFAULT_LOG), help="Session chat JSONL log file")
    recover.add_argument(
        "--memory-store",
        default=str(DEFAULT_MEMORY_STORE),
        help="Persistent memory JSONL store",
    )
    recover.add_argument(
        "--memory-items",
        type=int,
        default=12,
        help="Maximum memory items to persist per recovered session",
    )
    recover.add_argument(
        "--extract-max-tokens",
        type=int,
        default=1000,
        help="max_output_tokens for memory extraction call",
    )
    recover.add_argument(
        "--sync-max-tokens",
        type=int,
        default=500,
        help="max_output_tokens for memory sync call",
    )
    recover.add_argument("--model", default=None, help="Optional model override")
    recover.add_argument(
        "--sync-to-gpt",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Send extracted memory payload to GPT as a dedicated chat message",
    )
    recover.add_argument(
        "--memory-pointer",
        default=DEFAULT_MEMORY_POINTER,
        help="Logical pointer included in GPT memory sync payload",
    )
    recover.add_argument(
        "--stale-seconds",
        type=int,
        default=900,
        help="Only recover sessions inactive for at least this many seconds",
    )
    recover.add_argument(
        "--max-sessions",
        type=int,
        default=20,
        help="Maximum number of sessions to recover in one run",
    )
    recover.add_argument(
        "--exclude-session",
        action="append",
        default=[],
        help="Session ids to skip (can be set multiple times)",
    )
    recover.add_argument(
        "--show-raw",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Print raw extraction/sync JSON responses",
    )


def build_team_parser(subparsers: argparse._SubParsersAction) -> None:
    team = subparsers.add_parser(
        "team",
        help="Post a team message; relay to GPT when @gpt is mentioned",
    )
    team.add_argument("text", help="Team message text")
    team.add_argument("--session", default=None, help="Session id (defaults to active session)")
    team.add_argument("--from", dest="from_actor", default="user", help="Actor label")
    team.add_argument("--log-file", default=str(DEFAULT_LOG), help="JSONL event log file")
    team.add_argument(
        "--memory-store",
        default=str(DEFAULT_MEMORY_STORE),
        help="Persistent memory JSONL store",
    )
    team.add_argument("--model", default=None, help="Optional model override")
    team.add_argument("--max-tokens", type=int, default=1200, help="max_output_tokens hint")
    team.add_argument(
        "--memory-items",
        type=int,
        default=8,
        help="Number of latest memory items to inject when relaying to GPT",
    )
    team.add_argument(
        "--show-raw",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Print raw bridge JSON response when relaying to GPT",
    )


def build_session_parser(subparsers: argparse._SubParsersAction) -> None:
    session = subparsers.add_parser(
        "session",
        help="End current session, start new session, and send kickoff prompt to GPT",
    )
    session.add_argument("kickoff_prompt", help="Kickoff prompt for the new session")
    session.add_argument(
        "--session",
        default=None,
        help="Optional explicit new session id (otherwise derived from kickoff prompt)",
    )
    session.add_argument("--log-file", default=str(DEFAULT_LOG), help="Session chat JSONL log file")
    session.add_argument(
        "--memory-store",
        default=str(DEFAULT_MEMORY_STORE),
        help="Persistent memory JSONL store",
    )
    session.add_argument(
        "--memory-items",
        type=int,
        default=12,
        help="Maximum memory items to persist/inject",
    )
    session.add_argument(
        "--extract-max-tokens",
        type=int,
        default=1000,
        help="max_output_tokens for memory extraction",
    )
    session.add_argument(
        "--sync-max-tokens",
        type=int,
        default=500,
        help="max_output_tokens for memory sync",
    )
    session.add_argument("--model", default=None, help="Optional model override")
    session.add_argument(
        "--memory-pointer",
        default=DEFAULT_MEMORY_POINTER,
        help="Logical pointer included in GPT memory sync payload",
    )
    session.add_argument(
        "--kickoff-max-tokens",
        type=int,
        default=1200,
        help="max_output_tokens for kickoff prompt send",
    )
    session.add_argument(
        "--show-raw",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Print raw kickoff response",
    )


def build_options_parser(subparsers: argparse._SubParsersAction, name: str, help_text: str) -> None:
    options = subparsers.add_parser(name, help=help_text)
    options.add_argument("--session", default=None, help="Optional session id override")
    options.add_argument("--log-file", default=str(DEFAULT_LOG), help="Session chat JSONL log file")


def build_chat_parser(subparsers: argparse._SubParsersAction) -> None:
    chat = subparsers.add_parser(
        "chat",
        help="Route one raw chat message using slash-command aliases or default team posting",
    )
    chat.add_argument("message", help="Raw message text (e.g. '/session Plan rollout' or '@gpt review this')")
    chat.add_argument("--session", default=None, help="Optional session id override")
    chat.add_argument("--from", dest="from_actor", default="user", help="Actor label")
    chat.add_argument("--log-file", default=str(DEFAULT_LOG), help="Session chat JSONL log file")
    chat.add_argument(
        "--memory-store",
        default=str(DEFAULT_MEMORY_STORE),
        help="Persistent memory JSONL store",
    )
    chat.add_argument("--model", default=None, help="Optional model override")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge chat relay with shared logging")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_send_parser(subparsers)
    build_post_parser(subparsers)
    build_tail_parser(subparsers)
    build_end_parser(subparsers)
    build_recover_parser(subparsers)
    build_team_parser(subparsers)
    build_session_parser(subparsers)
    build_options_parser(subparsers, "options", "Show available session actions")
    build_options_parser(subparsers, "help", "Alias for options")
    build_chat_parser(subparsers)
    return parser.parse_args()


def extract_gpt_text(response: dict[str, Any]) -> str:
    answer = response.get("answer", {})
    if not isinstance(answer, dict):
        return json.dumps(response, ensure_ascii=True)

    markdown = answer.get("markdown")
    if isinstance(markdown, str) and markdown.strip():
        return markdown.strip()

    answer_json = answer.get("json")
    if isinstance(answer_json, dict):
        if isinstance(answer_json.get("reply"), str):
            return answer_json["reply"]
        if isinstance(answer_json.get("summary"), str):
            return answer_json["summary"]
        return json.dumps(answer_json, ensure_ascii=True)

    return json.dumps(response, ensure_ascii=True)


def _run_ask_once(
    message: str,
    task_type: str,
    max_tokens: int,
    json_only: bool,
    meta: dict[str, Any],
    model: str | None = None,
    context_files: list[str] | None = None,
    context_text: str | None = None,
) -> dict[str, Any]:
    cmd = [
        str(ASK_ONCE),
        message,
        "--task-type",
        task_type,
        "--max-tokens",
        str(max_tokens),
        "--json-only" if json_only else "--no-json-only",
        "--meta",
        json.dumps(meta, ensure_ascii=True),
    ]
    if model and model.strip():
        cmd.extend(["--model", model.strip()])
    for path in context_files or []:
        cmd.extend(["--context-file", path])

    stdin_text = context_text
    if context_text is not None:
        cmd.append("--context-stdin")

    proc = subprocess.run(
        cmd,
        cwd=str(SCRIPT_DIR),
        input=stdin_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit code {proc.returncode}"
        raise RuntimeError(f"Bridge request failed: {detail}")

    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Bridge returned invalid JSON: {exc}") from exc
    if not isinstance(response, dict):
        raise RuntimeError("Bridge response must be a JSON object")
    return response


def _load_memory_context(memory_store: Path, limit: int) -> str:
    if limit <= 0:
        return ""
    events = iter_events(memory_store)
    if not events:
        return ""
    snippets: list[str] = []
    for event in events[::-1]:
        memory = event.get("memory")
        if not isinstance(memory, str) or not memory.strip():
            continue
        category = str(event.get("category", "general"))
        scope = str(event.get("scope", "project"))
        confidence = event.get("confidence", 0.5)
        snippets.append(
            f"- [{scope}/{category}, confidence={confidence}] {memory.strip()}"
        )
        if len(snippets) >= limit:
            break
    if not snippets:
        return ""
    snippets.reverse()
    return "Persistent memory for BitPod decisions:\n" + "\n".join(snippets)


def call_bridge_via_ask_once(
    args: argparse.Namespace,
    injected_context: str | None = None,
) -> dict[str, Any]:
    meta = parse_json_object(args.meta, "--meta")
    context_parts: list[str] = []
    if injected_context and injected_context.strip():
        context_parts.append(injected_context.strip())
    if args.context_stdin:
        if sys.stdin.isatty():
            raise ValueError("--context-stdin was set but no stdin pipe was provided")
        stdin_text = sys.stdin.read()
        if stdin_text.strip():
            context_parts.append(stdin_text)
    context_text = "\n\n".join(context_parts) if context_parts else None
    return _run_ask_once(
        message=args.message,
        task_type=args.task_type,
        max_tokens=args.max_tokens,
        json_only=bool(args.json_only),
        meta=meta,
        model=args.model,
        context_files=list(args.context_file),
        context_text=context_text,
    )


def _as_float(value: Any, fallback: float = 0.5) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        out = fallback
    if out < 0:
        return 0.0
    if out > 1:
        return 1.0
    return out


def _extract_items_from_answer(answer_json: Any) -> list[dict[str, Any]]:
    if not isinstance(answer_json, dict):
        return []
    raw_items = answer_json.get("items")
    if not isinstance(raw_items, list):
        return []
    items: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        memory = item.get("memory") or item.get("fact") or item.get("text")
        if not isinstance(memory, str) or not memory.strip():
            continue
        entry = {
            "memory": memory.strip(),
            "category": str(item.get("category", "general")),
            "scope": str(item.get("scope", "project")),
            "confidence": _as_float(item.get("confidence", 0.5)),
        }
        rationale = item.get("rationale")
        if isinstance(rationale, str) and rationale.strip():
            entry["rationale"] = rationale.strip()
        items.append(entry)
    return items


def _append_memory_items(memory_store: Path, session: str, items: list[dict[str, Any]]) -> int:
    count = 0
    base = int(time.time())
    for i, item in enumerate(items):
        event = {
            "ts": utc_now_iso(),
            "memory_id": f"{base}-{i+1}",
            "session": session,
            "memory": item["memory"],
            "category": item["category"],
            "scope": item["scope"],
            "confidence": item["confidence"],
            "source": "bridge_chat.end",
        }
        if "rationale" in item:
            event["rationale"] = item["rationale"]
        append_event(memory_store, event)
        count += 1
    return count


def _parse_iso_ts(ts: Any) -> datetime | None:
    if not isinstance(ts, str) or not ts.strip():
        return None
    raw = ts.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _log_status(log_file: Path, session: str, text: str) -> None:
    ts = utc_now_iso()
    append_event(
        log_file,
        {"ts": ts, "session": session, "actor": "system", "kind": "status", "text": text},
    )
    print_timeline_line(ts, "system", text)


def _log_error(log_file: Path, session: str, text: str) -> None:
    ts = utc_now_iso()
    append_event(
        log_file,
        {"ts": ts, "session": session, "actor": "system", "kind": "error", "text": text},
    )
    print_timeline_line(ts, "system", text)


def _get_transcript_and_last_ts(events: list[dict[str, Any]], session: str) -> tuple[str, datetime | None]:
    lines: list[str] = []
    last_ts: datetime | None = None
    for event in events:
        if event.get("session") != session:
            continue
        ts = _parse_iso_ts(event.get("ts"))
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
        if event.get("kind") != "message":
            continue
        actor = str(event.get("actor", "unknown"))
        text = event.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        lines.append(f"{actor}: {text.strip()}")
    if not lines:
        return "", last_ts
    return "\n".join(lines[-300:]), last_ts


def _transcript_digest(transcript: str) -> str:
    return hashlib.sha256(transcript.encode("utf-8")).hexdigest()


def _is_digest_finalized(events: list[dict[str, Any]], session: str, digest: str) -> bool:
    for event in events:
        if event.get("session") != session:
            continue
        if event.get("kind") != "session_finalize":
            continue
        if event.get("digest") == digest:
            return True
    return False


def _append_finalize_marker(
    log_file: Path,
    session: str,
    digest: str,
    reason: str,
    items_saved: int,
    synced_to_gpt: bool,
) -> None:
    append_event(
        log_file,
        {
            "ts": utc_now_iso(),
            "session": session,
            "actor": "system",
            "kind": "session_finalize",
            "digest": digest,
            "reason": reason,
            "items_saved": items_saved,
            "synced_to_gpt": synced_to_gpt,
        },
    )


def _extract_memory_items_for_session(
    session: str,
    transcript: str,
    memory_items: int,
    extract_max_tokens: int,
    model: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    extract_prompt = (
        "From the session transcript context, extract durable remember-worthy items for BitPod app "
        "decisions outside this session. Return JSON object with keys: "
        "items (array of {memory, category, scope, confidence, rationale}) and summary (string). "
        "Only include non-sensitive, durable facts or preferences."
    )
    extract_meta = {"workflow": "bridge_chat_end_extract", "session": session}
    extract_response = _run_ask_once(
        message=extract_prompt,
        task_type="report",
        max_tokens=extract_max_tokens,
        json_only=True,
        meta=extract_meta,
        model=model,
        context_text=transcript,
    )
    answer = extract_response.get("answer", {})
    answer_json = answer.get("json", {}) if isinstance(answer, dict) else {}
    items = _extract_items_from_answer(answer_json)[: max(memory_items, 0)]
    return items, extract_response


def _sync_memory_items_to_gpt(
    session: str,
    items: list[dict[str, Any]],
    sync_max_tokens: int,
    model: str | None,
    memory_pointer: str,
) -> dict[str, Any]:
    sync_payload = {
        "session": session,
        "memory_items": items,
        "instruction": IMPORTANT_MEMORY_SUFFIX,
        "memory_pointer": memory_pointer,
    }
    sync_message = (
        "Please ingest these long-term BitPod memory updates for future decisions.\n"
        + json.dumps(sync_payload, ensure_ascii=True)
        + f"\n\nMemory pointer: {memory_pointer}"
        + f"\n\n{IMPORTANT_MEMORY_SUFFIX}"
    )
    sync_meta = {"workflow": "bridge_chat_end_sync", "session": session}
    return _run_ask_once(
        message=sync_message,
        task_type="report",
        max_tokens=sync_max_tokens,
        json_only=True,
        meta=sync_meta,
        model=model,
    )


def _finalize_session_memory(
    *,
    session: str,
    log_file: Path,
    memory_store: Path,
    memory_items: int,
    extract_max_tokens: int,
    sync_max_tokens: int,
    model: str | None,
    sync_to_gpt: bool,
    memory_pointer: str,
    show_raw: bool,
    reason: str,
    cached_events: list[dict[str, Any]] | None = None,
) -> tuple[bool, str]:
    events = cached_events if cached_events is not None else iter_events(log_file)
    transcript, _last_ts = _get_transcript_and_last_ts(events, session)
    if not transcript:
        return False, f"No messages found for session '{session}'."

    digest = _transcript_digest(transcript)
    if _is_digest_finalized(events, session, digest):
        return False, f"Session '{session}' is already finalized for current transcript."

    _log_status(log_file, session, "Bridge GPT | Ending session and extracting memory...")
    try:
        items, extract_response = _extract_memory_items_for_session(
            session=session,
            transcript=transcript,
            memory_items=memory_items,
            extract_max_tokens=extract_max_tokens,
            model=model,
        )
    except RuntimeError as exc:
        _log_error(log_file, session, f"Bridge GPT | Error: {exc}")
        return False, str(exc)

    if not items:
        _log_status(log_file, session, "Bridge GPT | No durable memory items found for this session.")
        _append_finalize_marker(
            log_file=log_file,
            session=session,
            digest=digest,
            reason=reason,
            items_saved=0,
            synced_to_gpt=False,
        )
        if show_raw:
            print(json.dumps(extract_response, ensure_ascii=True))
        return True, "No durable memory items"

    saved = _append_memory_items(memory_store, session, items)
    _log_status(log_file, session, f"Bridge GPT | Saved {saved} memory item(s).")

    synced = False
    if sync_to_gpt:
        _log_status(log_file, session, "Bridge GPT | Syncing memory to GPT...")
        try:
            sync_response = _sync_memory_items_to_gpt(
                session=session,
                items=items,
                sync_max_tokens=sync_max_tokens,
                model=model,
                memory_pointer=memory_pointer,
            )
            sync_text = extract_gpt_text(sync_response)
            ack_ts = utc_now_iso()
            append_event(
                log_file,
                {
                    "ts": ack_ts,
                    "session": session,
                    "actor": "gpt",
                    "kind": "memory_sync_ack",
                    "text": sync_text,
                    "raw": sync_response,
                },
            )
            print_timeline_line(ack_ts, "GPT", sync_text)
            synced = True
            if show_raw:
                print(json.dumps(sync_response, ensure_ascii=True))
        except RuntimeError as exc:
            _log_error(log_file, session, f"Bridge GPT | Memory sync error: {exc}")
            return False, str(exc)

    _append_finalize_marker(
        log_file=log_file,
        session=session,
        digest=digest,
        reason=reason,
        items_saved=saved,
        synced_to_gpt=synced,
    )
    if show_raw:
        print(json.dumps(extract_response, ensure_ascii=True))
    return True, f"Saved {saved} memory item(s)"


def _recover_sessions(
    *,
    log_file: Path,
    memory_store: Path,
    memory_items: int,
    extract_max_tokens: int,
    sync_max_tokens: int,
    model: str | None,
    sync_to_gpt: bool,
    memory_pointer: str,
    stale_seconds: int,
    max_sessions: int,
    exclude_sessions: set[str] | None = None,
    show_raw: bool = False,
) -> int:
    events = iter_events(log_file)
    sessions: set[str] = set()
    for event in events:
        session = event.get("session")
        if isinstance(session, str) and session:
            sessions.add(session)
    now = datetime.now(timezone.utc)
    exclude = exclude_sessions or set()
    candidates: list[tuple[datetime, str]] = []
    for session in sessions:
        if session in exclude:
            continue
        transcript, last_ts = _get_transcript_and_last_ts(events, session)
        if not transcript:
            continue
        digest = _transcript_digest(transcript)
        if _is_digest_finalized(events, session, digest):
            continue
        if last_ts is None:
            continue
        age = (now - last_ts).total_seconds()
        if age < max(stale_seconds, 0):
            continue
        candidates.append((last_ts, session))

    candidates.sort(key=lambda x: x[0])
    processed = 0
    for _last_ts, session in candidates[: max(max_sessions, 0)]:
        ok, _msg = _finalize_session_memory(
            session=session,
            log_file=log_file,
            memory_store=memory_store,
            memory_items=memory_items,
            extract_max_tokens=extract_max_tokens,
            sync_max_tokens=sync_max_tokens,
            model=model,
            sync_to_gpt=sync_to_gpt,
            memory_pointer=memory_pointer,
            show_raw=show_raw,
            reason="recover",
        )
        if ok:
            processed += 1
    return processed


def _send_to_gpt(
    *,
    log_file: Path,
    memory_store: Path,
    session: str,
    from_actor: str,
    message: str,
    task_type: str,
    max_tokens: int,
    model: str | None,
    use_memory: bool,
    memory_items: int,
    show_raw: bool,
    log_user_message: bool,
    preface_status: str | None = None,
) -> int:
    if log_user_message:
        started = utc_now_iso()
        append_event(
            log_file,
            {
                "ts": started,
                "session": session,
                "actor": from_actor,
                "kind": "message",
                "text": message,
            },
        )
        print_timeline_line(started, from_actor, message)

    memory_context = ""
    if use_memory:
        memory_context = _load_memory_context(memory_store, memory_items)

    status_steps = [
        "Bridge GPT | Checking config...",
        "Bridge GPT | Starting bridge...",
        "Bridge GPT | Authenticating...",
    ]
    if preface_status:
        status_steps.append(preface_status)
    if memory_context:
        status_steps.append("Bridge GPT | Loading memory...")
    status_steps.append("Bridge GPT | Sending prompt...")
    for status_text in status_steps:
        status_ts = utc_now_iso()
        append_event(
            log_file,
            {
                "ts": status_ts,
                "session": session,
                "actor": "system",
                "kind": "status",
                "text": status_text,
            },
        )
        print_timeline_line(status_ts, "system", status_text)

    try:
        response = _run_ask_once(
            message=message,
            task_type=task_type,
            max_tokens=max_tokens,
            json_only=True,
            meta={"session": session, "workflow": "bridge_chat_send"},
            model=model,
            context_text=memory_context if memory_context else None,
        )
    except RuntimeError as exc:
        err_ts = utc_now_iso()
        append_event(
            log_file,
            {
                "ts": err_ts,
                "session": session,
                "actor": "system",
                "kind": "error",
                "text": str(exc),
            },
        )
        print_timeline_line(err_ts, "system", f"Bridge GPT | Error: {exc}")
        return 1

    gpt_text = extract_gpt_text(response)
    reply_ts = utc_now_iso()
    append_event(
        log_file,
        {
            "ts": reply_ts,
            "session": session,
            "actor": "gpt",
            "kind": "message",
            "text": gpt_text,
            "raw": response,
        },
    )
    active_ts = utc_now_iso()
    append_event(
        log_file,
        {
            "ts": active_ts,
            "session": session,
            "actor": "system",
            "kind": "status",
            "text": "GPT Bridge | Active",
        },
    )
    print_timeline_line(active_ts, "system", "GPT Bridge | Active")
    print_timeline_line(reply_ts, "GPT", gpt_text)
    if show_raw:
        print(json.dumps(response, ensure_ascii=True))
    return 0


def run_send(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    memory_store = Path(args.memory_store)
    session = _resolve_session(args.session)
    _set_active_session(session)

    if args.auto_recover:
        recovered = _recover_sessions(
            log_file=log_file,
            memory_store=memory_store,
            memory_items=max(args.memory_items, 0),
            extract_max_tokens=max(args.recover_extract_max_tokens, 100),
            sync_max_tokens=max(args.recover_sync_max_tokens, 100),
            model=args.model,
            sync_to_gpt=True,
            memory_pointer=DEFAULT_MEMORY_POINTER,
            stale_seconds=args.recover_stale_seconds,
            max_sessions=args.recover_max_sessions,
            exclude_sessions={session},
            show_raw=False,
        )
        if recovered > 0:
            _log_status(log_file, session, f"Bridge GPT | Recovered {recovered} stale session(s).")

    return _send_to_gpt(
        log_file=log_file,
        memory_store=memory_store,
        session=session,
        from_actor=args.from_actor,
        message=args.message,
        task_type=args.task_type,
        max_tokens=args.max_tokens,
        model=args.model,
        use_memory=bool(args.use_memory),
        memory_items=args.memory_items,
        show_raw=bool(args.show_raw),
        log_user_message=True,
    )


def run_post(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    session = _resolve_session(args.session)
    _set_active_session(session)
    ts = utc_now_iso()
    mentions = _extract_mentions(args.text)
    append_event(
        log_file,
        {
            "ts": ts,
            "session": session,
            "actor": args.from_actor,
            "kind": "message",
            "text": args.text,
            "mentions": mentions,
        },
    )
    print_timeline_line(ts, args.from_actor, args.text)
    return 0


def run_end(args: argparse.Namespace) -> int:
    session = _resolve_session(args.session)
    ok, msg = _finalize_session_memory(
        session=session,
        log_file=Path(args.log_file),
        memory_store=Path(args.memory_store),
        memory_items=max(args.memory_items, 0),
        extract_max_tokens=max(args.extract_max_tokens, 100),
        sync_max_tokens=max(args.sync_max_tokens, 100),
        model=args.model,
        sync_to_gpt=bool(args.sync_to_gpt),
        memory_pointer=args.memory_pointer,
        show_raw=bool(args.show_raw),
        reason="manual_end",
    )
    if ok:
        _set_active_session(session)
        if args.stop_bridge:
            ctl = SCRIPT_DIR / "bridge_ctl.sh"
            if ctl.exists():
                proc = subprocess.run(
                    [str(ctl), "stop", "--session", session],
                    cwd=str(SCRIPT_DIR),
                    text=True,
                    capture_output=True,
                    check=False,
                )
                output = (proc.stdout or proc.stderr or "").strip()
                if output:
                    print(output)
        return 0
    if msg.startswith("No messages found"):
        _log_error(Path(args.log_file), session, msg)
        return 1
    _log_status(Path(args.log_file), session, msg)
    return 0


def run_team(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    session = _resolve_session(args.session)
    _set_active_session(session)
    ts = utc_now_iso()
    mentions = _extract_mentions(args.text)
    append_event(
        log_file,
        {
            "ts": ts,
            "session": session,
            "actor": args.from_actor,
            "kind": "message",
            "text": args.text,
            "mentions": mentions,
        },
    )
    print_timeline_line(ts, args.from_actor, args.text)

    if "codex" in mentions:
        codex_text = f"@{args.from_actor} acknowledged by Codex. I saw your message."
        codex_ts = utc_now_iso()
        append_event(
            log_file,
            {
                "ts": codex_ts,
                "session": session,
                "actor": "codex",
                "kind": "message",
                "text": codex_text,
                "mentions": [args.from_actor] if args.from_actor else [],
            },
        )
        print_timeline_line(codex_ts, "codex", codex_text)

    if "gpt" not in mentions:
        return 0

    relay_text = _strip_gpt_mentions(args.text)
    return _send_to_gpt(
        log_file=log_file,
        memory_store=Path(args.memory_store),
        session=session,
        from_actor=args.from_actor,
        message=relay_text,
        task_type="general",
        max_tokens=args.max_tokens,
        model=args.model,
        use_memory=True,
        memory_items=args.memory_items,
        show_raw=bool(args.show_raw),
        log_user_message=False,
        preface_status="Bridge GPT | @gpt mention detected, relaying...",
    )


def run_session(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    current_session = _resolve_session(None)
    new_session = args.session.strip() if isinstance(args.session, str) and args.session.strip() else _slugify_session_label(args.kickoff_prompt)

    if current_session != new_session:
        _finalize_session_memory(
            session=current_session,
            log_file=log_file,
            memory_store=Path(args.memory_store),
            memory_items=max(args.memory_items, 0),
            extract_max_tokens=max(args.extract_max_tokens, 100),
            sync_max_tokens=max(args.sync_max_tokens, 100),
            model=args.model,
            sync_to_gpt=True,
            memory_pointer=args.memory_pointer,
            show_raw=False,
            reason="session_switch",
        )

    _set_active_session(new_session)
    _log_status(log_file, new_session, f"Bridge GPT | Active session set: {new_session}")
    return _send_to_gpt(
        log_file=log_file,
        memory_store=Path(args.memory_store),
        session=new_session,
        from_actor="user",
        message=args.kickoff_prompt,
        task_type="general",
        max_tokens=args.kickoff_max_tokens,
        model=args.model,
        use_memory=True,
        memory_items=args.memory_items,
        show_raw=bool(args.show_raw),
        log_user_message=True,
        preface_status="Bridge GPT | Session kickoff...",
    )


def run_options(args: argparse.Namespace) -> int:
    session = _resolve_session(args.session)
    _set_active_session(session)
    print("system: Bridge GPT options")
    print("system: Recommended (tilde mode):")
    print("system: ~help | ~options            -> show this list")
    print("system: ~session <kickoff prompt>   -> switch session + kickoff GPT")
    print("system: ~gpt <message>              -> GPT relay")
    print("system: ~codex <message>            -> Codex mention")
    print("system: ~cj <message>               -> mention cj in team chat")
    print("system: ~taylor <message>           -> mention taylor in team chat")
    print("system: ~end                        -> finalize active session memory")
    print("system: ~recover                    -> recover stale sessions")
    print("system: Plain-text aliases:")
    print("system: help: | options:            -> show this list")
    print("system: session: <kickoff prompt>   -> switch session + kickoff GPT")
    print("system: gpt: <message>              -> GPT relay")
    print("system: codex: <message>            -> Codex mention")
    print("system: team message                -> normal team post")
    print("system: Legacy/advanced:")
    print("system: team message with @gpt      -> team post + GPT relay")
    print("system: team message with @codex    -> team post + Codex acknowledgment")
    print("system: gpt> <message>              -> GPT relay (legacy plain-text alias)")
    print("system: /gpt <message>              -> explicit GPT relay")
    print("system: /ask <message>              -> alias for /gpt")
    print("system: /codex <message>            -> explicit Codex mention")
    print("system: /session <kickoff prompt>   -> end previous session, start new one, send kickoff to GPT")
    print("system: /end                        -> finalize active session memory")
    print("system: /recover                    -> recover stale sessions after interruption")
    print(f"system: active session: {session}")
    return 0


def _chat_team_args(args: argparse.Namespace, text: str) -> argparse.Namespace:
    return argparse.Namespace(
        text=text,
        session=args.session,
        from_actor=args.from_actor,
        log_file=args.log_file,
        memory_store=args.memory_store,
        model=args.model,
        max_tokens=1200,
        memory_items=8,
        show_raw=False,
    )


def _chat_end_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        session=args.session,
        log_file=args.log_file,
        memory_store=args.memory_store,
        memory_items=12,
        extract_max_tokens=1000,
        sync_max_tokens=500,
        model=args.model,
        sync_to_gpt=True,
        memory_pointer=DEFAULT_MEMORY_POINTER,
        show_raw=False,
        stop_bridge=True,
    )


def _chat_recover_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        log_file=args.log_file,
        memory_store=args.memory_store,
        memory_items=12,
        extract_max_tokens=1000,
        sync_max_tokens=500,
        model=args.model,
        sync_to_gpt=True,
        memory_pointer=DEFAULT_MEMORY_POINTER,
        stale_seconds=900,
        max_sessions=20,
        exclude_session=[],
        show_raw=False,
    )


def run_chat(args: argparse.Namespace) -> int:
    raw = args.message.strip()
    if not raw:
        print("system: Empty message.")
        return 2

    lower = raw.lower()
    if lower in {"help:", "options:"}:
        return run_options(argparse.Namespace(session=args.session, log_file=args.log_file))

    if raw.startswith("~"):
        parts = raw[1:].split(maxsplit=1)
        tcmd = parts[0].lower() if parts and parts[0] else ""
        trest = parts[1].strip() if len(parts) > 1 else ""
        if tcmd in {"help", "options"}:
            return run_options(argparse.Namespace(session=args.session, log_file=args.log_file))
        if tcmd == "end":
            return run_end(_chat_end_args(args))
        if tcmd == "recover":
            return run_recover(_chat_recover_args(args))
        if tcmd == "session":
            if not trest:
                print("system: Usage: ~session <kickoff prompt>")
                return 2
            return run_session(
                argparse.Namespace(
                    kickoff_prompt=trest,
                    session=None,
                    log_file=args.log_file,
                    memory_store=args.memory_store,
                    memory_items=12,
                    extract_max_tokens=1000,
                    sync_max_tokens=500,
                    model=args.model,
                    memory_pointer=DEFAULT_MEMORY_POINTER,
                    kickoff_max_tokens=1200,
                    show_raw=False,
                )
            )
        if tcmd in {"gpt", "codex", "cj", "taylor"}:
            if not trest:
                print(f"system: Usage: ~{tcmd} <message>")
                return 2
            return run_team(_chat_team_args(args, f"@{tcmd} {trest}"))
        print(f"system: Unknown command: ~{tcmd}" if tcmd else "system: Unknown command: ~")
        print("system: Try ~help")
        return 2

    if lower.startswith("session:"):
        rest = raw[len("session:") :].strip()
        if not rest:
            print("system: Usage: session: <kickoff prompt>")
            return 2
        return run_session(
            argparse.Namespace(
                kickoff_prompt=rest,
                session=None,
                log_file=args.log_file,
                memory_store=args.memory_store,
                memory_items=12,
                extract_max_tokens=1000,
                sync_max_tokens=500,
                model=args.model,
                memory_pointer=DEFAULT_MEMORY_POINTER,
                kickoff_max_tokens=1200,
                show_raw=False,
            )
        )

    if lower.startswith("gpt:"):
        rest = raw[4:].strip()
        if not rest:
            print("system: Usage: gpt: <message>")
            return 2
        return run_team(_chat_team_args(args, f"@gpt {rest}"))
    if lower.startswith("codex:"):
        rest = raw[6:].strip()
        if not rest:
            print("system: Usage: codex: <message>")
            return 2
        return run_team(_chat_team_args(args, f"@codex {rest}"))
    if lower.startswith("gpt>"):
        rest = raw[4:].strip()
        if not rest:
            print("system: Usage: gpt> <message>")
            return 2
        return run_team(_chat_team_args(args, f"@gpt {rest}"))
    if lower.startswith("codex>"):
        rest = raw[6:].strip()
        if not rest:
            print("system: Usage: codex> <message>")
            return 2
        return run_team(_chat_team_args(args, f"@codex {rest}"))

    if not raw.startswith("/"):
        return run_team(_chat_team_args(args, raw))

    parts = raw.split(maxsplit=1)
    cmd = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    if cmd in {"/help", "/options"}:
        return run_options(argparse.Namespace(session=args.session, log_file=args.log_file))
    if cmd == "/end":
        return run_end(_chat_end_args(args))
    if cmd == "/recover":
        return run_recover(_chat_recover_args(args))
    if cmd == "/session":
        if not rest:
            print("system: Usage: /session <kickoff prompt>")
            return 2
        return run_session(
            argparse.Namespace(
                kickoff_prompt=rest,
                session=None,
                log_file=args.log_file,
                memory_store=args.memory_store,
                memory_items=12,
                extract_max_tokens=1000,
                sync_max_tokens=500,
                model=args.model,
                memory_pointer=DEFAULT_MEMORY_POINTER,
                kickoff_max_tokens=1200,
                show_raw=False,
            )
        )
    if cmd in {"/gpt", "/ask"}:
        if not rest:
            print("system: Usage: /gpt <message> (or /ask <message>)")
            return 2
        return run_team(_chat_team_args(args, f"@gpt {rest}"))
    if cmd == "/codex":
        if not rest:
            print("system: Usage: /codex <message>")
            return 2
        return run_team(_chat_team_args(args, f"@codex {rest}"))
    if cmd == "/team":
        if not rest:
            print("system: Usage: /team <message>")
            return 2
        return run_team(_chat_team_args(args, rest))

    print(f"system: Unknown command: {cmd}")
    print("system: Try /help")
    return 2


def run_recover(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    _log_status(log_file, "recovery", "Bridge GPT | Scanning for stale sessions to recover...")
    recovered = _recover_sessions(
        log_file=log_file,
        memory_store=Path(args.memory_store),
        memory_items=max(args.memory_items, 0),
        extract_max_tokens=max(args.extract_max_tokens, 100),
        sync_max_tokens=max(args.sync_max_tokens, 100),
        model=args.model,
        sync_to_gpt=bool(args.sync_to_gpt),
        memory_pointer=args.memory_pointer,
        stale_seconds=args.stale_seconds,
        max_sessions=args.max_sessions,
        exclude_sessions=set(args.exclude_session),
        show_raw=bool(args.show_raw),
    )
    _log_status(log_file, "recovery", f"Bridge GPT | Recovery complete. Sessions recovered: {recovered}")
    return 0


def iter_events(log_file: Path) -> list[dict[str, Any]]:
    if not log_file.exists():
        return []
    events: list[dict[str, Any]] = []
    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
    return events


def print_event(event: dict[str, Any]) -> None:
    kind = str(event.get("kind", ""))
    if kind not in {"message", "status", "error", "memory_sync_ack"}:
        return
    ts = str(event.get("ts", ""))
    actor = str(event.get("actor", "unknown"))
    text = str(event.get("text", ""))
    if not text.strip():
        return
    print_timeline_line(ts, actor, text)


def run_tail(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    session = args.session

    def filtered(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not session:
            return events
        return [e for e in events if e.get("session") == session]

    events = filtered(iter_events(log_file))
    for event in events[-args.lines :]:
        print_event(event)

    if not args.follow:
        return 0

    known = len(events)
    while True:
        time.sleep(max(args.poll_seconds, 0.2))
        new_events = filtered(iter_events(log_file))
        if len(new_events) <= known:
            continue
        for event in new_events[known:]:
            print_event(event)
        known = len(new_events)


def main() -> int:
    args = parse_args()
    if args.command == "send":
        return run_send(args)
    if args.command == "post":
        return run_post(args)
    if args.command == "team":
        return run_team(args)
    if args.command == "session":
        return run_session(args)
    if args.command == "tail":
        return run_tail(args)
    if args.command == "end":
        return run_end(args)
    if args.command == "recover":
        return run_recover(args)
    if args.command in {"help", "options"}:
        return run_options(args)
    if args.command == "chat":
        return run_chat(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
