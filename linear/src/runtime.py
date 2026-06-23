from __future__ import annotations

import os
from typing import Any, Dict, List

try:
    from linear.src.engine import Action, LinearBotEngine
    from linear.src.memory import InMemoryStore, JsonlFileStore, MemoryEvent, MemoryStore, now_iso
except ModuleNotFoundError:
    from engine import Action, LinearBotEngine
    from memory import InMemoryStore, JsonlFileStore, MemoryEvent, MemoryStore, now_iso


class BotRuntime:
    """Platform-agnostic orchestration layer.

    Adapters (Linear/GitHub/Discord/etc.) should only translate transport payloads
    into runtime calls and execute returned actions.
    """

    def __init__(self, engine: LinearBotEngine | None = None, store: MemoryStore | None = None) -> None:
        self.engine = engine or LinearBotEngine()
        if store is not None:
            self.store = store
        else:
            trace_path = os.getenv("RUNTIME_TRACE_PATH")
            self.store = JsonlFileStore(trace_path) if trace_path else InMemoryStore()

    def run_github_event(self, event: Dict[str, Any]) -> List[Action]:
        action = event.get("action")
        github_event = str(event.get("_github_event") or "")
        pr = event.get("pull_request", {})
        issue = event.get("issue", {}) if isinstance(event.get("issue", {}), dict) else {}
        issue_key = (
            self.engine.find_issue_key(pr.get("title", ""))
            or self.engine.find_issue_key(pr.get("body", ""))
            or self.engine.find_issue_key(pr.get("head", {}).get("ref", ""))
            or self.engine.find_issue_key(issue.get("title", ""))
            or self.engine.find_issue_key(issue.get("body", ""))
            or "UNLINKED"
        )

        if github_event == "issues" and action == "labeled":
            out = self.engine.on_github_qa_override(event)
        elif github_event == "issue_comment" and action == "created":
            out = self.engine.on_github_qa_override(event)
        elif github_event == "pull_request_review" and action == "submitted":
            out = self.engine.on_github_qa_override(event)
        elif action == "opened":
            out = self.engine.on_github_pr_opened(event)
        elif action == "ready_for_review":
            out = self.engine.on_github_pr_ready_for_review(event)
        elif action == "synchronize":
            out = self.engine.on_github_pr_synchronize(event)
        elif action == "review_requested":
            out = self.engine.on_github_pr_review_requested(event)
        elif action == "closed" and pr.get("merged") is True:
            out = self.engine.on_github_pr_merged(
                issue=event.get("linear_issue", {}),
                pr_url=pr.get("html_url", ""),
                merge_sha=pr.get("merge_commit_sha", ""),
            )
        else:
            out = []

        self.store.append(
            MemoryEvent(
                key=issue_key,
                kind=f"github:{action}",
                payload={"actions": str(len(out))},
                at=now_iso(),
            )
        )
        return out

    def run_linear_event(self, event: Dict[str, Any]) -> List[Action]:
        kind = event.get("type")
        issue_key = event.get("issue_key") or event.get("issue", {}).get("identifier") or "UNLINKED"

        if kind == "comment_created":
            out = self.engine.on_linear_comment(
                issue_key=event.get("issue_key", ""),
                comment_body=event.get("comment_body", ""),
                pr_url=event.get("pr_url", ""),
                issue_labels=event.get("issue_labels", []),
                issue_url=event.get("issue_url", ""),
            )
        elif kind == "issue_ready_gate":
            out = self.engine.on_linear_ready_gate(event.get("issue", {}))
        elif kind in ("issue_in_review", "issue_status_changed"):
            issue = event.get("issue", {})
            if issue.get("status") == self.engine.cfg.in_review_status:
                out = self.engine.on_linear_issue_in_review(issue)
            else:
                out = []
        elif kind == "vera_qa_completed":
            out = self.engine.on_vera_qa_completed(event)
        elif kind in ("pm_label_changed", "acceptance_gate_changed", "pm_review_changed"):
            out = self.engine.on_linear_acceptance_gate_change(
                issue_key=event.get("issue_key", ""),
                gate_value=event.get("pm_value", "") or event.get("gate_value", ""),
                pr_url=event.get("pr_url", ""),
                reason=event.get("reason", ""),
            )
        elif kind == "daily_aging_scan":
            out = self.engine.daily_aging_scan(event.get("issues", []))
        else:
            out = []

        self.store.append(
            MemoryEvent(
                key=issue_key,
                kind=f"linear:{kind}",
                payload={"actions": str(len(out))},
                at=now_iso(),
            )
        )
        return out
