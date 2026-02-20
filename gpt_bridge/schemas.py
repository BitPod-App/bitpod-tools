#!/usr/bin/env python3
"""Schemas for GPT Bridge request/response payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    GENERAL = "general"
    QA_CHECK = "qa_check"
    REPORT = "report"
    SCORE_CHECK = "score_check"


class ResponseStatus(str, Enum):
    OK = "ok"
    NEEDS_INFO = "needs_info"
    BLOCKED = "blocked"


@dataclass
class GPTRequest:
    task_type: TaskType
    message: str
    context: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GPTRequest":
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")

        task_type = data.get("task_type")
        if task_type not in {t.value for t in TaskType}:
            raise ValueError("task_type must be one of: general, qa_check, report, score_check")

        message = data.get("message")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")

        context = data.get("context", [])
        if context is None:
            context = []
        if not isinstance(context, list) or not all(isinstance(i, str) for i in context):
            raise ValueError("context must be an array of strings")

        constraints = data.get("constraints", {})
        if constraints is None:
            constraints = {}
        if not isinstance(constraints, dict):
            raise ValueError("constraints must be an object")

        meta = data.get("meta", {})
        if meta is None:
            meta = {}
        if not isinstance(meta, dict):
            raise ValueError("meta must be an object")

        return cls(
            task_type=TaskType(task_type),
            message=message.strip(),
            context=context,
            constraints=constraints,
            meta=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "message": self.message,
            "context": self.context,
            "constraints": self.constraints,
            "meta": self.meta,
        }


@dataclass
class AnswerPayload:
    json: dict[str, Any]
    markdown: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"json": self.json}
        if self.markdown:
            out["markdown"] = self.markdown
        return out


@dataclass
class GPTResponse:
    status: ResponseStatus
    answer: AnswerPayload
    warnings: list[str] = field(default_factory=list)
    followups_for_codex: list[str] = field(default_factory=list)
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "answer": self.answer.to_dict(),
            "warnings": self.warnings,
            "followups_for_codex": self.followups_for_codex,
            "trace": self.trace,
        }
