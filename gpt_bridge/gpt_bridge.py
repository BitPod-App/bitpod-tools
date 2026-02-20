#!/usr/bin/env python3
"""Local HTTP bridge for GPT requests."""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from schemas import AnswerPayload, GPTRequest, GPTResponse, ResponseStatus

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
DEFAULT_MODEL = "gpt-5.2"
OPENAI_URL = "https://api.openai.com/v1/responses"
SYSTEM_IDENTITY_PROMPT = (
    "You are GPT Bridge, a pragmatic assistant for terminal workflows. "
    "Return concise, actionable outputs for automation and code tasks."
)
ROUTED_MODELS_BY_TASK = {
    "general": "gpt-5.2",
    "report": "gpt-5.2",
    "qa_check": "gpt-5-mini",
    "score_check": "gpt-5-mini",
}


class BridgeConfig:
    def __init__(self) -> None:
        self.host = os.getenv("GPT_BRIDGE_HOST", DEFAULT_HOST)
        self.port = int(os.getenv("GPT_BRIDGE_PORT", str(DEFAULT_PORT)))
        self.model = os.getenv("GPT_BRIDGE_MODEL", DEFAULT_MODEL)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.bridge_token = os.getenv("GPT_BRIDGE_TOKEN", "").strip()
        self.bridge_shared_secret = os.getenv("GPT_BRIDGE_SHARED_SECRET", "").strip()
        self.log_file = Path(os.getenv("GPT_BRIDGE_LOG_FILE", "logs/bridge.jsonl"))

    def validate_startup(self) -> None:
        if self.host != "127.0.0.1":
            raise RuntimeError("GPT_BRIDGE_HOST must be exactly 127.0.0.1")
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required")
        if not (self.bridge_token or self.bridge_shared_secret):
            raise RuntimeError(
                "Set GPT_BRIDGE_TOKEN and/or GPT_BRIDGE_SHARED_SECRET for request authentication"
            )


class BridgeHandler(BaseHTTPRequestHandler):
    config: BridgeConfig
    log_lock = threading.Lock()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _is_authorized(self) -> bool:
        auth = self.headers.get("Authorization", "")
        secret = self.headers.get("X-Bridge-Secret", "")

        token_ok = False
        secret_ok = False

        if self.config.bridge_token:
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1].strip()
                token_ok = token == self.config.bridge_token

        if self.config.bridge_shared_secret:
            secret_ok = secret == self.config.bridge_shared_secret

        if self.config.bridge_token and self.config.bridge_shared_secret:
            return token_ok or secret_ok
        if self.config.bridge_token:
            return token_ok
        return secret_ok

    def _log_jsonl(self, event: dict[str, Any]) -> None:
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, ensure_ascii=True)
        with self.log_lock:
            with self.config.log_file.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def do_POST(self) -> None:
        if self.path != "/ask":
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        request_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        if not self._is_authorized():
            self._write_json(HTTPStatus.UNAUTHORIZED, {"error": "Unauthorized", "request_id": request_id})
            return

        content_length = self.headers.get("Content-Length")
        if not content_length:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Missing Content-Length", "request_id": request_id})
            return

        try:
            body = self.rfile.read(int(content_length))
            payload = json.loads(body.decode("utf-8"))
            gpt_request = GPTRequest.from_dict(payload)
        except (ValueError, json.JSONDecodeError) as exc:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": f"Invalid request: {exc}", "request_id": request_id},
            )
            return

        selected_model = resolve_model(gpt_request, self.config)

        warnings: list[str] = []
        try:
            gpt_response = call_openai(gpt_request, request_id, self.config, selected_model)
        except RuntimeError as exc:
            warnings.append(str(exc))
            gpt_response = GPTResponse(
                status=ResponseStatus.BLOCKED,
                answer=AnswerPayload(
                    json={
                        "summary": "OpenAI call failed",
                        "reason": str(exc),
                    }
                ),
                warnings=warnings,
                followups_for_codex=[
                    "Check OPENAI_API_KEY and network access.",
                    "Retry with a smaller context or lower max_tokens.",
                ],
                trace={"request_id": request_id, "model": selected_model},
            )

        response_payload = gpt_response.to_dict()
        self._log_jsonl(
            {
                "timestamp": timestamp,
                "request_id": request_id,
                "request": gpt_request.to_dict(),
                "response": response_payload,
            }
        )
        self._write_json(HTTPStatus.OK, response_payload)


def resolve_model(gpt_request: GPTRequest, config: BridgeConfig) -> str:
    override_model = gpt_request.constraints.get("model")
    if isinstance(override_model, str) and override_model.strip():
        return override_model.strip()

    routed = ROUTED_MODELS_BY_TASK.get(gpt_request.task_type.value)
    if routed:
        return routed
    return config.model


def _extract_output_text(data: dict[str, Any]) -> str:
    output = data.get("output", [])
    chunks: list[str] = []
    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if chunks:
        return "\n".join(chunks).strip()
    if isinstance(data.get("output_text"), str):
        return data["output_text"].strip()
    return ""


def _extract_first_json(raw_text: str) -> dict[str, Any] | None:
    raw_text = raw_text.strip()
    if not raw_text:
        return None

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start >= 0 and end > start:
        candidate = raw_text[start : end + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
    return None


def call_openai(
    gpt_request: GPTRequest,
    request_id: str,
    config: BridgeConfig,
    selected_model: str,
) -> GPTResponse:
    json_only = bool(gpt_request.constraints.get("json_only", True))
    max_tokens = int(gpt_request.constraints.get("max_tokens", 1200))

    context_block = "\n".join(gpt_request.context) if gpt_request.context else "(none)"
    user_instructions = {
        "task_type": gpt_request.task_type.value,
        "message": gpt_request.message,
        "context": context_block,
        "constraints": gpt_request.constraints,
        "meta": gpt_request.meta,
        "required_response_shape": {
            "status": "ok | needs_info | blocked",
            "answer": {"json": "object", "markdown": "optional string"},
            "warnings": ["string"],
            "followups_for_codex": ["string"],
        },
    }

    format_instruction = (
        "Return strictly valid JSON matching required_response_shape."
        if json_only
        else "Return JSON first; markdown may follow if useful."
    )

    payload = {
        "model": selected_model,
        "max_output_tokens": max_tokens,
        "input": [
            {
                "role": "system",
                "content": [
                    {"type": "input_text", "text": SYSTEM_IDENTITY_PROMPT},
                    {"type": "input_text", "text": format_instruction},
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(user_instructions)}],
            },
        ],
    }

    req = Request(
        OPENAI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json",
            "X-Request-ID": request_id,
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=90) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(f"OpenAI API connection error: {exc}") from exc

    raw_text = _extract_output_text(response_data)
    parsed_json = _extract_first_json(raw_text)
    warnings: list[str] = []
    followups: list[str] = []
    markdown: str | None = None

    if parsed_json is None:
        parsed_json = {
            "summary": "Model did not return valid JSON",
            "raw_output": raw_text,
        }
        warnings.append("Model output was not valid JSON; wrapped raw output in answer.json.raw_output")
        status = ResponseStatus.BLOCKED
    else:
        status_value = parsed_json.get("status", "ok")
        status = ResponseStatus(status_value) if status_value in {s.value for s in ResponseStatus} else ResponseStatus.OK

        answer_block = parsed_json.get("answer", {})
        if isinstance(answer_block, dict):
            answer_json = answer_block.get("json")
            if not isinstance(answer_json, dict):
                answer_json = {"model_answer": answer_block}
                warnings.append("answer.json was missing or invalid; coerced to object")
            markdown_value = answer_block.get("markdown")
            if isinstance(markdown_value, str):
                markdown = markdown_value
        else:
            answer_json = {"model_answer": parsed_json}
        warnings_value = parsed_json.get("warnings", [])
        if isinstance(warnings_value, list):
            warnings.extend([w for w in warnings_value if isinstance(w, str)])
        followups_value = parsed_json.get("followups_for_codex", [])
        if isinstance(followups_value, list):
            followups.extend([f for f in followups_value if isinstance(f, str)])

        parsed_json = answer_json

    usage = response_data.get("usage", {}) if isinstance(response_data.get("usage"), dict) else {}

    return GPTResponse(
        status=status,
        answer=AnswerPayload(json=parsed_json, markdown=markdown),
        warnings=warnings,
        followups_for_codex=followups,
        trace={
            "request_id": request_id,
            "model": selected_model,
            "token_usage": usage,
        },
    )


def main() -> None:
    config = BridgeConfig()
    config.validate_startup()
    BridgeHandler.config = config

    server = ThreadingHTTPServer((config.host, config.port), BridgeHandler)
    print(f"GPT Bridge listening on http://{config.host}:{config.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
