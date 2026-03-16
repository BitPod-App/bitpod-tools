#!/usr/bin/env python3
"""MCP stdio server that forwards tool calls to GPT Bridge HTTP /ask."""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

SERVER_NAME = "gpt-bridge-mcp"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL_VERSION = "2024-11-05"
DEFAULT_BRIDGE_URL = "http://127.0.0.1:8787/ask"
DEFAULT_BRIDGE_TIMEOUT_SECONDS = 20
TOOL_NAME = "gpt_bridge_ask"
VALID_TASK_TYPES = {"general", "qa_check", "report", "score_check"}


def _build_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    token = os.getenv("GPT_BRIDGE_TOKEN", "").strip()
    shared_secret = os.getenv("GPT_BRIDGE_SHARED_SECRET", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif shared_secret:
        headers["X-Bridge-Secret"] = shared_secret
    return headers


def _call_bridge(arguments: dict[str, Any]) -> dict[str, Any]:
    task_type = arguments.get("task_type", "general")
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(
            "task_type must be one of: general, qa_check, report, score_check"
        )

    message = arguments.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")

    context = arguments.get("context", [])
    if context is None:
        context = []
    if not isinstance(context, list) or not all(isinstance(item, str) for item in context):
        raise ValueError("context must be an array of strings")

    constraints = arguments.get("constraints", {})
    if constraints is None:
        constraints = {}
    if not isinstance(constraints, dict):
        raise ValueError("constraints must be an object")

    meta = arguments.get("meta", {})
    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        raise ValueError("meta must be an object")

    payload: dict[str, Any] = {
        "task_type": task_type,
        "message": message.strip(),
        "context": context,
        "constraints": constraints,
        "meta": meta,
    }

    bridge_url = os.getenv("GPT_BRIDGE_URL", DEFAULT_BRIDGE_URL)
    _enforce_allowed_bridge_url(bridge_url)
    timeout_raw = os.getenv("GPT_BRIDGE_TIMEOUT_SECONDS", str(DEFAULT_BRIDGE_TIMEOUT_SECONDS)).strip()
    try:
        bridge_timeout = float(timeout_raw)
    except ValueError:
        bridge_timeout = float(DEFAULT_BRIDGE_TIMEOUT_SECONDS)
    if bridge_timeout <= 0:
        bridge_timeout = float(DEFAULT_BRIDGE_TIMEOUT_SECONDS)

    req = Request(
        bridge_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_build_headers(),
        method="POST",
    )

    try:
        with urlopen(req, timeout=bridge_timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Bridge HTTP {exc.code}: {detail[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(
            f"Bridge connection error (timeout={bridge_timeout}s): {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Bridge returned invalid JSON: {exc}") from exc


def _enforce_allowed_bridge_url(url: str) -> None:
    allow_raw = os.getenv("GPT_BRIDGE_ALLOWED_HOSTS", "").strip()
    if not allow_raw:
        return
    allowed = {h.strip().lower() for h in allow_raw.split(",") if h.strip()}
    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()
    if not host or host not in allowed:
        raise RuntimeError(
            f"Bridge host '{host or 'unknown'}' blocked by GPT_BRIDGE_ALLOWED_HOSTS policy"
        )


def _make_tools_result() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": TOOL_NAME,
                "description": "Send a GPTRequest payload to local GPT Bridge /ask.",
                "inputSchema": {
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "task_type": {
                            "type": "string",
                            "enum": ["general", "qa_check", "report", "score_check"],
                            "default": "general",
                        },
                        "message": {"type": "string"},
                        "context": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": [],
                        },
                        "constraints": {
                            "type": "object",
                            "description": "Forwarded directly to bridge constraints.",
                            "default": {},
                        },
                        "meta": {
                            "type": "object",
                            "description": "Forwarded directly to bridge meta.",
                            "default": {},
                        },
                    },
                    "additionalProperties": False,
                },
            }
        ]
    }


def _write_message(payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    out = sys.stdout.buffer
    out.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii"))
    out.write(raw)
    out.flush()


def _read_message() -> dict[str, Any] | None:
    inp = sys.stdin.buffer
    headers: dict[str, str] = {}

    while True:
        line = inp.readline()
        if line == b"":
            return None
        if line in (b"\r\n", b"\n"):
            break
        try:
            decoded = line.decode("ascii").strip()
        except UnicodeDecodeError:
            continue
        if ":" not in decoded:
            continue
        key, value = decoded.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    length_raw = headers.get("content-length")
    if not length_raw:
        return None
    try:
        length = int(length_raw)
    except ValueError:
        return None

    body = inp.read(length)
    if len(body) != length:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _rpc_error(
    request_id: Any,
    code: int,
    message: str,
) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _handle_request(msg: dict[str, Any]) -> dict[str, Any] | None:
    request_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "notifications/initialized":
        return None

    if method == "initialize":
        requested_protocol = DEFAULT_PROTOCOL_VERSION
        if isinstance(params, dict):
            incoming = params.get("protocolVersion")
            if isinstance(incoming, str) and incoming.strip():
                requested_protocol = incoming.strip()
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": requested_protocol,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": _make_tools_result()}

    if method == "tools/call":
        if not isinstance(params, dict):
            return _rpc_error(request_id, -32602, "Invalid params")

        name = params.get("name")
        if name != TOOL_NAME:
            return _rpc_error(request_id, -32601, f"Unknown tool: {name}")

        arguments = params.get("arguments", {})
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return _rpc_error(request_id, -32602, "arguments must be an object")

        try:
            bridge_result = _call_bridge(arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(bridge_result, ensure_ascii=True),
                        }
                    ],
                    "isError": False,
                },
            }
        except (RuntimeError, ValueError) as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                },
            }

    return _rpc_error(request_id, -32601, f"Method not found: {method}")


def main() -> int:
    while True:
        msg = _read_message()
        if msg is None:
            return 0
        if not isinstance(msg, dict):
            continue
        response = _handle_request(msg)
        if response is not None:
            _write_message(response)


if __name__ == "__main__":
    raise SystemExit(main())
