#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import textwrap
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from linear.src.custom_agent_receiver import (
        LINEAR_WEBHOOK_SECRET_ENV,
        ReceiverConfig,
        ReceiverDecision,
        ReceiverRequest,
        plan_receiver_decision,
        verify_linear_signature,
    )
    from linear.src.engine import Action, CJ_OVERRIDE_LOGIN, GITHUB_QA_OVERRIDE_LABELS, QA_OVERRIDE_COMMAND_RE, format_actions
    from linear.src.governance import GovernancePolicy
    from linear.src.linear_executor import LinearExecutionError, LinearExecutor
    from linear.src.memory import JsonlFileStore, MemoryEvent, now_iso
    from linear.src.runtime import BotRuntime
except ModuleNotFoundError:
    from custom_agent_receiver import (
        LINEAR_WEBHOOK_SECRET_ENV,
        ReceiverConfig,
        ReceiverDecision,
        ReceiverRequest,
        plan_receiver_decision,
        verify_linear_signature,
    )
    from engine import Action, CJ_OVERRIDE_LOGIN, GITHUB_QA_OVERRIDE_LABELS, QA_OVERRIDE_COMMAND_RE, format_actions
    from governance import GovernancePolicy
    from linear_executor import LinearExecutionError, LinearExecutor
    from memory import JsonlFileStore, MemoryEvent, now_iso
    from runtime import BotRuntime




@dataclass(frozen=True)
class WebhookVerificationResult:
    ok: bool
    status_code: int
    reason: str


def env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _github_webhook_secret_from_env() -> str:
    return (
        os.getenv("GITHUB_WEBHOOK_SECRET", "").strip()
        or os.getenv("VERA_QA_GATE_WEBHOOK_SIGNING_SECRET", "").strip()
    )


def _linear_webhook_secret_from_env() -> str:
    return (
        os.getenv("LINEAR_WEBHOOK_SECRET", "").strip()
        or os.getenv("VERA_QA_GATE_LINEAR_WEBHOOK_SECRET", "").strip()
        or os.getenv("VERA_QA_GATE_WEBHOOK_SIGNING_SECRET", "").strip()
    )


def _verify_github_webhook_signature(body: bytes, signature_header: str, secret: str) -> bool:
    if not secret:
        return True
    prefix = "sha256="
    if not signature_header.startswith(prefix):
        return False
    expected = prefix + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def _verify_linear_webhook_signature(body: bytes, signature_header: str, secret: str) -> bool:
    if not secret:
        return True
    if not signature_header:
        return False
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _normalize_private_key(raw: str) -> str:
    value = raw.strip()
    if "\\n" in value and "\n" not in value:
        value = value.replace("\\n", "\n")
    match = re.search(
        r"-----BEGIN ([A-Z ]*PRIVATE KEY)-----\s*(.*?)\s*-----END \1-----",
        value,
        flags=re.S,
    )
    if match:
        key_type = match.group(1)
        body = "".join(match.group(2).split())
        value = (
            f"-----BEGIN {key_type}-----\n"
            + "\n".join(textwrap.wrap(body, 64))
            + f"\n-----END {key_type}-----\n"
        )
    return value


def _sign_rs256_with_openssl(signing_input: bytes, private_key_pem: str) -> bytes:
    key_path = ""
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
            key_path = fh.name
            os.chmod(key_path, 0o600)
            fh.write(_normalize_private_key(private_key_pem))
        proc = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            input=signing_input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            detail = proc.stderr.decode("utf-8", errors="replace").strip() or "openssl signing failed"
            raise RuntimeError(detail)
        return proc.stdout
    finally:
        if key_path:
            try:
                os.unlink(key_path)
            except FileNotFoundError:
                pass


def _github_app_jwt(app_id: str, private_key_pem: str) -> str:
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"iat": now - 60, "exp": now + 540, "iss": app_id}
    signing_input = (
        _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        + "."
        + _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    ).encode("ascii")
    signature = _sign_rs256_with_openssl(signing_input, private_key_pem)
    return signing_input.decode("ascii") + "." + _b64url(signature)


def _github_json_request(method: str, path: str, token: str, body: Optional[Dict] = None) -> Dict:
    api_url = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    data = json.dumps(body or {}).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        api_url + path,
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"GitHub API request failed: {exc}") from exc
    return json.loads(raw) if raw.strip() else {}


def github_app_installation_token_from_env() -> str:
    direct_token = os.getenv("VERA_QA_GATE_GITHUB_TOKEN", "").strip()
    if direct_token:
        return direct_token
    app_id = os.getenv("VERA_QA_GATE_GITHUB_APP_ID", "").strip()
    client_id = os.getenv("VERA_QA_GATE_GITHUB_CLIENT_ID", "").strip()
    installation_id = os.getenv("VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID", "").strip()
    private_key = os.getenv("VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY", "").strip()
    if not (app_id and installation_id and private_key):
        raise RuntimeError("missing Vera QA Gate GitHub App credentials; set VERA_QA_GATE_GITHUB_TOKEN or app id/installation id/private key")
    jwt_token = _github_app_jwt(client_id or app_id, private_key)
    result = _github_json_request("POST", f"/app/installations/{installation_id}/access_tokens", jwt_token, {})
    token = str(result.get("token") or "")
    if not token:
        raise RuntimeError("GitHub installation token response missing token")
    return token


def execute_github_check_run(action: Action) -> str:
    if not env_truthy("VERA_QA_GATE_LIVE_ENABLED"):
        raise RuntimeError("vera QA gate live switch is off; set VERA_QA_GATE_LIVE_ENABLED=true to emit GitHub check runs")
    repo = str(action.payload.get("repo_full_name") or "")
    head_sha = str(action.payload.get("head_sha") or "")
    name = str(action.payload.get("name") or "vera-qa-gate")
    status = str(action.payload.get("status") or "queued")
    if not repo or not head_sha:
        raise RuntimeError("github check_run requires repo_full_name and head_sha")
    output = {
        "title": str(action.payload.get("title") or name),
        "summary": str(action.payload.get("summary") or "Vera QA gate update."),
    }
    body: Dict[str, object] = {
        "name": name,
        "head_sha": head_sha,
        "status": status,
        "output": output,
    }
    conclusion = str(action.payload.get("conclusion") or "")
    if conclusion:
        body["conclusion"] = conclusion
    token = github_app_installation_token_from_env()

    # Check runs do not have commit-status-style latest-by-context semantics.
    # Keep the Vera gate idempotent by updating the newest same-name run for the
    # SHA when one exists; create only when this SHA has no Vera gate run yet.
    existing = _github_json_request(
        "GET",
        f"/repos/{repo}/commits/{head_sha}/check-runs?check_name={name}",
        token,
    )
    runs = existing.get("check_runs") if isinstance(existing, dict) else []
    if isinstance(runs, list) and runs:
        newest = sorted(runs, key=lambda item: int(item.get("id") or 0), reverse=True)[0]
        check_id = newest.get("id")
        patch_body = {"status": status, "output": output}
        if conclusion:
            patch_body["conclusion"] = conclusion
        result = _github_json_request("PATCH", f"/repos/{repo}/check-runs/{check_id}", token, patch_body)
        return f"github check_run update {repo}@{head_sha} {name} id={result.get('id', check_id)} status={status}"

    result = _github_json_request("POST", f"/repos/{repo}/check-runs", token, body)
    return f"github check_run create {repo}@{head_sha} {name} id={result.get('id', '')} status={status}"


def execute_github_pr_comment(action: Action) -> str:
    owner, repo, num = parse_pr_url(action.target)
    if not owner or not repo or not num:
        raise RuntimeError("invalid github target for comment")
    body = str(action.payload.get("body") or "")
    if not body:
        raise RuntimeError("github comment body is required")
    token = github_app_installation_token_from_env()
    result = _github_json_request(
        "POST",
        f"/repos/{owner}/{repo}/issues/{num}/comments",
        token,
        {"body": body},
    )
    return f"github app comment {owner}/{repo}#{num} id={result.get('id', '')}"


def _label_name(label: Any) -> str:
    if isinstance(label, dict):
        return str(label.get("name") or "")
    return str(label or "")


def _is_github_qa_override_label(name: str) -> bool:
    return str(name or "").casefold() in GITHUB_QA_OVERRIDE_LABELS


def _body_has_qa_override_command(body: str) -> bool:
    text = body or ""
    return bool(QA_OVERRIDE_COMMAND_RE.search(text))


def _github_event_may_be_qa_override(event: Dict[str, Any], event_name: str) -> bool:
    if event_name in {"issues", "pull_request"} and event.get("action") == "labeled":
        return _is_github_qa_override_label(_label_name(event.get("label")))
    if event_name == "issue_comment" and event.get("action") == "created":
        comment = event.get("comment") if isinstance(event.get("comment"), dict) else {}
        return _body_has_qa_override_command(str(comment.get("body") or ""))
    if event_name == "pull_request_review" and event.get("action") == "submitted":
        review = event.get("review") if isinstance(event.get("review"), dict) else {}
        return _body_has_qa_override_command(str(review.get("body") or ""))
    return False


def _github_repo_and_pr_number(event: Dict[str, Any]) -> Tuple[str, str]:
    repo = event.get("repository") if isinstance(event.get("repository"), dict) else {}
    repo_full_name = str(repo.get("full_name") or "")
    pr = event.get("pull_request") if isinstance(event.get("pull_request"), dict) else {}
    issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
    number = str(pr.get("number") or issue.get("number") or "")
    if repo_full_name and number:
        return repo_full_name, number
    pr_url = str(pr.get("html_url") or issue.get("html_url") or "")
    owner, repo_name, parsed_number = parse_pr_url(pr_url)
    return (f"{owner}/{repo_name}" if owner and repo_name else repo_full_name), (parsed_number or number)


def _latest_commit_date(commits: Any) -> str:
    if not isinstance(commits, list) or not commits:
        return ""
    latest = commits[-1]
    commit = latest.get("commit") if isinstance(latest, dict) else {}
    committer = commit.get("committer") if isinstance(commit.get("committer"), dict) else {}
    author = commit.get("author") if isinstance(commit.get("author"), dict) else {}
    return str(committer.get("date") or author.get("date") or "")


def _find_override_label_actor(events: Any) -> Tuple[str, str]:
    if not isinstance(events, list):
        return "", ""
    for item in reversed(events):
        if not isinstance(item, dict) or item.get("event") != "labeled":
            continue
        if not _is_github_qa_override_label(_label_name(item.get("label"))):
            continue
        actor = item.get("actor") if isinstance(item.get("actor"), dict) else {}
        return str(actor.get("login") or ""), str(item.get("created_at") or "")
    return "", ""


def _find_override_reason(comments: Any, reviews: Any, head_current_at: str) -> Dict[str, str]:
    candidates: List[Dict[str, str]] = []
    if isinstance(comments, list):
        for item in comments:
            if not isinstance(item, dict):
                continue
            user = item.get("user") if isinstance(item.get("user"), dict) else {}
            body = str(item.get("body") or "")
            created = str(item.get("created_at") or "")
            if user.get("login") == CJ_OVERRIDE_LOGIN and _body_has_qa_override_command(body):
                candidates.append({
                    "source": "comment",
                    "actor": CJ_OVERRIDE_LOGIN,
                    "body": body,
                    "html_url": str(item.get("html_url") or ""),
                    "created_at": created,
                })
    if isinstance(reviews, list):
        for item in reviews:
            if not isinstance(item, dict) or str(item.get("state") or "").casefold() != "approved":
                continue
            user = item.get("user") if isinstance(item.get("user"), dict) else {}
            body = str(item.get("body") or "")
            submitted = str(item.get("submitted_at") or "")
            if user.get("login") == CJ_OVERRIDE_LOGIN and _body_has_qa_override_command(body):
                candidates.append({
                    "source": "review",
                    "actor": CJ_OVERRIDE_LOGIN,
                    "body": body,
                    "html_url": str(item.get("html_url") or ""),
                    "submitted_at": submitted,
                    "created_at": submitted,
                })
    if head_current_at:
        candidates = [c for c in candidates if str(c.get("created_at") or c.get("submitted_at") or "") >= head_current_at]
    if not candidates:
        return {}
    return sorted(candidates, key=lambda c: str(c.get("created_at") or c.get("submitted_at") or ""))[-1]


def enrich_github_override_event(event: Dict[str, Any], event_name: str) -> Dict[str, Any]:
    """Add PR head, labels, label actor, and prior reason evidence for CJ QA overrides."""
    if not _github_event_may_be_qa_override(event, event_name):
        return event
    repo_full_name, pr_number = _github_repo_and_pr_number(event)
    if not repo_full_name or not pr_number:
        event["override_enrichment_error"] = "missing repo or PR number"
        return event
    try:
        token = github_app_installation_token_from_env()
        pr = _github_json_request("GET", f"/repos/{repo_full_name}/pulls/{pr_number}", token)
        issue = _github_json_request("GET", f"/repos/{repo_full_name}/issues/{pr_number}", token)
        events = _github_json_request("GET", f"/repos/{repo_full_name}/issues/{pr_number}/events?per_page=100", token)
        commits = _github_json_request("GET", f"/repos/{repo_full_name}/pulls/{pr_number}/commits?per_page=100", token)
        comments = _github_json_request("GET", f"/repos/{repo_full_name}/issues/{pr_number}/comments?per_page=100", token)
        reviews = _github_json_request("GET", f"/repos/{repo_full_name}/pulls/{pr_number}/reviews?per_page=100", token)
    except Exception as exc:
        event["override_enrichment_error"] = str(exc)
        return event

    existing_pr = event.get("pull_request") if isinstance(event.get("pull_request"), dict) else {}
    merged_pr = dict(pr)
    merged_pr.update({k: v for k, v in existing_pr.items() if v not in (None, "", [], {})})
    event["pull_request"] = merged_pr

    existing_issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
    merged_issue = dict(existing_issue)
    if isinstance(issue, dict) and issue.get("labels") is not None:
        merged_issue["labels"] = issue.get("labels")
    event["issue"] = merged_issue

    label_actor, label_created_at = _find_override_label_actor(events)
    if label_actor:
        event["override_label_actor"] = label_actor
        event["override_label_created_at"] = label_created_at

    head_current_at = _latest_commit_date(commits)
    if head_current_at:
        event["head_current_at"] = head_current_at

    if not isinstance(event.get("comment"), dict) and not isinstance(event.get("review"), dict):
        reason = _find_override_reason(comments, reviews, head_current_at)
        if reason:
            event["override_reason"] = reason
    return event


def _parse_vera_workspace_map(raw: str) -> Dict[str, str]:
    value = (raw or "").strip()
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        return {str(key).strip(): str(val).strip() for key, val in parsed.items() if str(key).strip() and str(val).strip()}

    mapping: Dict[str, str] = {}
    for entry in value.split(";"):
        if not entry.strip() or "=" not in entry:
            continue
        key, val = entry.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key and val:
            mapping[key] = val
    return mapping


def _vera_qa_workspace_for_action(action: Action) -> str:
    workspace_map = _parse_vera_workspace_map(os.getenv("VERA_QA_KANBAN_WORKSPACE_MAP", ""))
    if workspace_map:
        repo_full_name = str(action.payload.get("repo_full_name") or "").strip()
        if not repo_full_name:
            raise RuntimeError("missing Vera QA workspace mapping: repo_full_name is required when VERA_QA_KANBAN_WORKSPACE_MAP is set")
        workspace = workspace_map.get(repo_full_name, "")
        if not workspace:
            raise RuntimeError(f"missing Vera QA workspace mapping for repo {repo_full_name}")
        return workspace
    return str(os.getenv("VERA_QA_KANBAN_WORKSPACE", "scratch") or "scratch")


def _hermes_cli_path() -> str:
    explicit = os.getenv("HERMES_CLI_PATH", "").strip()
    if explicit:
        return os.path.expanduser(explicit)
    discovered = shutil.which("hermes")
    if discovered:
        return discovered
    for candidate in [
        Path.home() / ".local/bin/hermes",
        Path("/opt/homebrew/bin/hermes"),
        Path("/usr/local/bin/hermes"),
    ]:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return "hermes"


def _safe_path_segment(value: str, fallback: str = "unknown") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value or "").strip()).strip(".-")
    return cleaned or fallback


def _path_is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _normalize_workspace_path(workspace: str) -> str:
    """Resolve a Vera workspace string to a real filesystem path.

    Workspace-map values may carry a Hermes scheme prefix such as
    ``worktree:/abs/path`` (the exact shape this repo's Vera review path
    uses). The scheme must be stripped before any filesystem containment
    check; otherwise ``Path("worktree:/...")`` never resolves to a real
    location, ``.exists()`` is false, and safety guards silently no-op.
    Returns "" for an empty/blank workspace.
    """
    raw = str(workspace or "").strip()
    if not raw:
        return ""
    m = re.match(r"^(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*):(?P<rest>.+)$", raw)
    if m and m.group("scheme").lower() in {"worktree", "worktrees", "repo", "path", "file"}:
        raw = m.group("rest").strip()
    return os.path.expanduser(raw)


def _extract_github_pr_number(pr_url: str) -> str:
    _, _, number = parse_pr_url(pr_url)
    return number


def _vera_qa_artifact_workspace_for_action(action: Action, reviewed_workspace: str) -> str:
    """Return an out-of-repo artifact directory for Vera QA outputs.

    Vera needs a real repo workspace for review, but its generated QA files are
    runtime artifacts. Keep them outside the reviewed checkout so repeated QA
    runs cannot litter or dirty the PR worktree with ``manifest.json`` and
    ``verification_report.md``.
    """

    root = Path(os.path.expanduser(os.getenv("VERA_QA_ARTIFACT_ROOT", "~/.hermes/profiles/vera/qa-artifacts")))
    payload = action.payload
    issue = _safe_path_segment(str(payload.get("issue_key") or action.target), "issue")
    repo = _safe_path_segment(str(payload.get("repo_full_name") or "unknown-repo").replace("/", "__"), "repo")
    pr_number = _safe_path_segment(str(payload.get("pr_number") or _extract_github_pr_number(str(payload.get("pr_url") or ""))), "pr")
    head_sha = _safe_path_segment(str(payload.get("head_sha") or payload.get("idempotency_key") or "unknown-sha"), "sha")[:40]
    artifact_workspace = root / issue / repo / f"pr-{pr_number}" / head_sha

    reviewed_path = _normalize_workspace_path(reviewed_workspace)
    if reviewed_path and _path_is_within(artifact_workspace, Path(reviewed_path)):
        raise RuntimeError(
            "Vera QA artifact workspace resolves inside reviewed repo workspace; "
            "set VERA_QA_ARTIFACT_ROOT outside the repo checkout"
        )

    artifact_workspace.mkdir(parents=True, exist_ok=True)
    return str(artifact_workspace)


def _append_vera_qa_artifact_contract(body: str, artifact_workspace: str, reviewed_workspace: str) -> str:
    report_path = os.path.join(artifact_workspace, "verification_report.md")
    manifest_path = os.path.join(artifact_workspace, "manifest.json")
    contract = [
        "",
        "QA artifact contract:",
        f"Artifact workspace: {artifact_workspace}",
        f"Reviewed repo workspace: {reviewed_workspace}",
        f"- Write verification_report.md to: {report_path}",
        f"- Write manifest.json to: {manifest_path}",
        "- Do not create or modify verification_report.md or manifest.json in the reviewed repo workspace.",
    ]
    return (body.rstrip() + "\n" + "\n".join(contract)).strip()


def execute_hermes_vera_dispatch(action: Action) -> str:
    if not env_truthy("VERA_QA_DISPATCH_ENABLED"):
        raise RuntimeError("vera QA dispatch switch is off; set VERA_QA_DISPATCH_ENABLED=true to enqueue Hermes Vera QA tasks")
    title = str(action.payload.get("title") or f"Vera QA review: {action.target}")
    body = str(action.payload.get("body") or "")
    assignee = str(action.payload.get("assignee") or "vera")
    idempotency_key = str(action.payload.get("idempotency_key") or f"vera-qa:{action.target}")
    workspace = _vera_qa_workspace_for_action(action)
    artifact_workspace = _vera_qa_artifact_workspace_for_action(action, workspace)
    body = _append_vera_qa_artifact_contract(body, artifact_workspace, workspace)
    cmd = [
        _hermes_cli_path(),
        "kanban",
        "create",
        title,
        "--assignee",
        assignee,
        "--body",
        body,
        "--idempotency-key",
        idempotency_key,
        "--workspace",
        workspace,
        "--json",
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("hermes CLI not found; set HERMES_CLI_PATH or include hermes on PATH") from exc
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "hermes kanban create failed"
        raise RuntimeError(detail)
    return "hermes kanban create " + (proc.stdout.strip() or idempotency_key)

def parse_pr_url(pr_url: str) -> Tuple[str, str, str]:
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url or "")
    if not m:
        return "", "", ""
    return m.group(1), m.group(2), m.group(3)


def _extract_field(text: str, label: str) -> str:
    pattern = re.compile(rf"^{re.escape(label)}:\s*(.+?)\s*$", re.MULTILINE)
    m = pattern.search(text or "")
    return m.group(1).strip() if m else ""


def _vera_qa_artifact_workspace_for_task(task: Dict[str, Any]) -> str:
    body = str(task.get("body") or "")
    artifact_workspace = _extract_field(body, "Artifact workspace")
    if artifact_workspace:
        return os.path.expanduser(artifact_workspace)
    return os.path.expanduser(str(task.get("workspace_path") or ""))


def _is_syncable_vera_qa_task(task: Dict[str, Any]) -> bool:
    """Return true only for standard auto-dispatched Vera QA gate tasks."""
    title = str(task.get("title") or "")
    return title.startswith("Vera QA review:")


def collect_vera_qa_completed_events(tasks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    for task in tasks:
        if str(task.get("status") or "") != "done":
            continue
        if str(task.get("assignee") or "").casefold() != "vera":
            continue
        if not _is_syncable_vera_qa_task(task):
            continue
        body = str(task.get("body") or "")
        workspace = str(task.get("workspace_path") or "")
        artifact_workspace = _vera_qa_artifact_workspace_for_task(task)
        if not workspace or not artifact_workspace:
            continue
        manifest_path = os.path.join(artifact_workspace, "manifest.json")
        if not os.path.exists(manifest_path):
            continue
        try:
            with open(manifest_path, encoding="utf-8") as fh:
                manifest = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue

        qa_result = str(
            manifest.get("qa_result")
            or manifest.get("verdict")
            or manifest.get("qa_verdict")
            or ""
        ).upper()
        if qa_result not in {"PASSED", "FAILED", "OVERRIDE", "ACTION_REQUIRED"}:
            continue
        issue_key = str(manifest.get("issue") or manifest.get("issue_key") or _extract_field(body, "Issue"))
        pr_url = str(manifest.get("pr_url") or _extract_field(body, "PR"))
        head_sha = str(
            manifest.get("head_sha")
            or manifest.get("head")
            or manifest.get("sha")
            or _extract_field(body, "Head SHA")
        )
        body_head_sha = _extract_field(body, "Head SHA")
        if body_head_sha and head_sha and body_head_sha != head_sha:
            continue
        if not (issue_key and pr_url and head_sha):
            continue
        report_path = os.path.join(artifact_workspace, "verification_report.md")
        summary = str(task.get("result") or manifest.get("summary") or f"Vera QA {qa_result}.")
        events.append(
            {
                "type": "vera_qa_completed",
                "task_id": str(task.get("id") or ""),
                "issue_key": issue_key,
                "qa_result": qa_result,
                "qa_verdict": str(manifest.get("verdict") or manifest.get("qa_verdict") or qa_result).upper(),
                "pr_url": pr_url,
                "head_sha": head_sha,
                "report_path": report_path if os.path.exists(report_path) else "verification_report.md",
                "summary": summary,
            }
        )
    return events


def load_completed_vera_qa_tasks() -> List[Dict[str, Any]]:
    proc = subprocess.run(
        [_hermes_cli_path(), "kanban", "list", "--assignee", "vera", "--status", "done", "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "hermes kanban list failed")
    data = json.loads(proc.stdout or "[]")
    return data if isinstance(data, list) else []


def _filter_vera_qa_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    raw_ids = os.getenv("VERA_QA_RESULT_SYNC_TASK_ID", "")
    allowed_ids = {item.strip() for item in raw_ids.split(",") if item.strip()}
    raw_after = os.getenv("VERA_QA_RESULT_SYNC_AFTER_EPOCH", "").strip()
    after_epoch = int(raw_after) if raw_after.isdigit() else 0
    out: List[Dict[str, Any]] = []
    for task in tasks:
        task_id = str(task.get("id") or "")
        if allowed_ids and task_id not in allowed_ids:
            continue
        completed_at = int(task.get("completed_at") or 0)
        if after_epoch and completed_at and completed_at < after_epoch:
            continue
        out.append(task)
    return out


def _vera_result_synced(task_id: str, trace_store: JsonlFileStore) -> bool:
    return any(event.kind == "vera_qa_result_synced" for event in trace_store.list_for(task_id))


def _mark_vera_result_synced(task_id: str, trace_store: JsonlFileStore) -> None:
    trace_store.append(
        MemoryEvent(
            key=task_id,
            kind="vera_qa_result_synced",
            payload={"outcome": "synced"},
            at=now_iso(),
        )
    )


def _vera_result_sync_should_stop_retrying(results: Optional[List[Dict[str, str]]]) -> bool:
    return any(str(result.get("outcome")) == "executed" for result in (results or []))


def sync_vera_qa_results_once(
    tasks: Optional[List[Dict[str, Any]]] = None,
    dry_run: bool = True,
    runtime: Optional[BotRuntime] = None,
    policy: Optional[GovernancePolicy] = None,
    trace_store: Optional[JsonlFileStore] = None,
    apply_fn=None,
) -> int:
    runtime = runtime or BotRuntime()
    policy = policy or GovernancePolicy.default()
    trace_store = trace_store or get_trace_store()
    apply_fn = apply_fn or apply_actions
    task_list = _filter_vera_qa_tasks(tasks if tasks is not None else load_completed_vera_qa_tasks())
    synced = 0
    for event in collect_vera_qa_completed_events(task_list):
        task_id = event.get("task_id", "")
        if task_id and _vera_result_synced(task_id, trace_store):
            continue
        actions = runtime.run_linear_event(event)
        if not actions:
            continue
        results = apply_fn(actions, dry_run=dry_run, policy=policy)
        if not dry_run and task_id and _vera_result_sync_should_stop_retrying(results):
            _mark_vera_result_synced(task_id, trace_store)
        synced += 1
    return synced


def start_vera_qa_result_sync_thread(dry_run: bool, policy: GovernancePolicy) -> None:
    interval = int(os.getenv("VERA_QA_RESULT_SYNC_INTERVAL_SECONDS", "10"))

    def loop() -> None:
        while True:
            try:
                count = sync_vera_qa_results_once(dry_run=dry_run, policy=policy)
                if count:
                    print(f"[VERA_QA_RESULT_SYNC] processed={count} dry_run={dry_run}")
            except Exception as exc:
                print(f"[VERA_QA_RESULT_SYNC][FAIL-CLOSED] {exc}")
            time.sleep(max(interval, 1))

    thread = threading.Thread(target=loop, name="vera-qa-result-sync", daemon=True)
    thread.start()


def get_trace_store() -> JsonlFileStore:
    return JsonlFileStore(os.getenv("TRACE_STORE_PATH", "/tmp/bitpod_linear_runtime_trace.jsonl"))


def trace_action(
    action: Action,
    outcome: str,
    detail: str,
    policy_class: str,
    actor: Optional[Dict[str, str]] = None,
) -> None:
    payload = {
        "outcome": outcome,
        "detail": detail,
        "policy_class": policy_class,
    }
    if actor:
        payload["actor_id"] = actor.get("id", "")
        payload["actor_name"] = actor.get("name", "")
    get_trace_store().append(
        MemoryEvent(
            key=action.target,
            kind=f"action:{action.system}:{action.kind}",
            payload=payload,
            at=now_iso(),
        )
    )


def apply_actions(
    actions: List[Action],
    dry_run: bool = True,
    policy: Optional[GovernancePolicy] = None,
    linear_executor: Optional[LinearExecutor] = None,
) -> List[Dict[str, str]]:
    policy = policy or GovernancePolicy.default()
    results: List[Dict[str, str]] = []
    if dry_run:
        print("[DRY_RUN] would apply actions:")
        print(format_actions(actions))
        for a in actions:
            decision = policy.decide(a, dry_run=True)
            trace_action(a, "dry-run", decision.reason, decision.policy_class)
            results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "dry-run", "detail": decision.reason})
        return results

    # Live mode is still fail-closed: governance must allow the action first,
    # then Linear live execution must pass its own kill switch + actor checks.
    for a in actions:
        decision = policy.decide(a, dry_run=False)
        if not decision.allowed:
            print(f"[LIVE][FAIL-CLOSED] governance blocked {a.kind} {a.target}: {decision.reason}")
            trace_action(a, "blocked", decision.reason, decision.policy_class)
            results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "blocked", "detail": decision.reason})
            continue
        if a.system == "github" and a.kind == "comment":
            try:
                detail = execute_github_pr_comment(a)
            except Exception as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] github comment {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "blocked", "detail": detail})
                continue
            print(f"[LIVE] github comment {a.target}: {detail}")
            trace_action(a, "executed", detail, decision.policy_class)
            results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "executed", "detail": detail})
            continue

        if a.system == "github" and a.kind == "check_run":
            try:
                detail = execute_github_check_run(a)
            except Exception as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] github check_run {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "blocked", "detail": detail})
                continue
            print(f"[LIVE] github check_run {a.target}: {detail}")
            trace_action(a, "executed", detail, decision.policy_class)
            results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "executed", "detail": detail})
            continue

        if a.system == "hermes" and a.kind == "enqueue_vera_qa":
            try:
                detail = execute_hermes_vera_dispatch(a)
            except Exception as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] hermes enqueue_vera_qa {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "blocked", "detail": detail})
                continue
            print(f"[LIVE] hermes enqueue_vera_qa {a.target}: {detail}")
            trace_action(a, "executed", detail, decision.policy_class)
            results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "executed", "detail": detail})
            continue

        if a.system == "linear":
            executor = linear_executor or LinearExecutor.from_env()
            try:
                result = executor.execute(a)
            except LinearExecutionError as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] linear {a.kind} {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "blocked", "detail": detail})
                continue
            print(f"[LIVE] linear {a.kind} {a.target}: {result.detail}")
            trace_action(a, result.outcome, result.detail, decision.policy_class, actor=result.actor)
            results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": result.outcome, "detail": result.detail})
            continue

        print(f"[LIVE][SKIP] unknown action: {a}")
        trace_action(a, "skipped", "unknown action", decision.policy_class)
        results.append({"system": a.system, "kind": a.kind, "target": a.target, "outcome": "skipped", "detail": "unknown action"})
    return results


def is_custom_agent_event(data: Dict) -> bool:
    kind = str(data.get("type", "")).lower()
    has_agent_session = any(str(key).lower() == "agentsession" for key in data)
    return has_agent_session or kind in {"agent_session.created", "agentsessionevent", "agent_session_event"}


def custom_agent_actions(
    data: Dict,
    config: Optional[ReceiverConfig] = None,
) -> Tuple[ReceiverDecision, List[Action]]:
    session = data.get("agentSession") or {}
    issue = data.get("issue") or session.get("issue") or {}
    request = ReceiverRequest(
        issue_key=str(data.get("issue_key") or issue.get("identifier") or issue.get("key") or ""),
        peer_id=str(data.get("peer_id") or data.get("peer") or "codex"),
        session_id=str(data.get("session_id") or session.get("id") or ""),
        actor_id=str(data.get("actor_id") or session.get("appUserId") or ""),
        payload=data,
    )
    decision = plan_receiver_decision(request, config)
    actions: List[Action] = []
    if decision.first_activity:
        activity = decision.first_activity
        if activity["kind"] == "agent_activity":
            actions.append(
                Action(
                    activity["system"],
                    activity["kind"],
                    activity["target"],
                    {"content": {"type": activity["content_type"], "body": activity["body"]}},
                )
            )
        else:
            actions.append(Action(activity["system"], activity["kind"], activity["target"], {"body": activity["body"]}))
    return decision, actions


def verify_linear_webhook_request(
    *,
    raw_body: bytes,
    headers: Mapping[str, str],
    signing_secret: Optional[str] = None,
    now_ms: Optional[int] = None,
) -> WebhookVerificationResult:
    secret = _linear_webhook_secret_from_env() if signing_secret is None else signing_secret
    signature = _header_value(headers, "Linear-Signature")
    if not secret:
        return WebhookVerificationResult(True, 200, "signature not configured")
    result = verify_linear_signature(
        raw_body=raw_body,
        header_signature=signature,
        signing_secret=secret,
        now_ms=now_ms,
    )
    return WebhookVerificationResult(result.ok, 200 if result.ok else 401, result.reason)


def _header_value(headers: Mapping[str, str], name: str) -> str:
    if hasattr(headers, "get"):
        direct = headers.get(name)  # type: ignore[arg-type]
        if direct:
            return str(direct)
    wanted = name.lower()
    for key, value in headers.items():
        if str(key).lower() == wanted:
            return str(value)
    return ""


class Handler(BaseHTTPRequestHandler):
    runtime = BotRuntime()
    dry_run = True
    policy = GovernancePolicy.default()

    def _json(self, code: int, payload: Dict):
        b = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        raw_body = b"{}"
        try:
            n = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(n) or b"{}"
            if self.path == "/github":
                secret = _github_webhook_secret_from_env()
                signature = self.headers.get("X-Hub-Signature-256", "")
                if not _verify_github_webhook_signature(raw_body, signature, secret):
                    self._json(401, {"ok": False, "error": "invalid-github-signature"})
                    return
            if self.path == "/linear":
                secret = _linear_webhook_secret_from_env()
                signature = self.headers.get("Linear-Signature", "")
                if not _verify_linear_webhook_signature(raw_body, signature, secret):
                    self._json(401, {"ok": False, "error": "invalid-linear-signature"})
                    return
            data = json.loads(raw_body)
        except Exception as e:
            self._json(400, {"ok": False, "error": f"bad-json: {e}"})
            return

        actions: List[Action] = []
        receiver_decision: Optional[ReceiverDecision] = None

        if self.path == "/github":
            event_name = self.headers.get("X-GitHub-Event", "")
            github_override_event = False
            if event_name:
                data["_github_event"] = event_name
                github_override_event = _github_event_may_be_qa_override(data, event_name)
                data = enrich_github_override_event(data, event_name)
            action = data.get("action")
            if action == "opened":
                actions = self.runtime.run_github_event(data)
            elif action == "ready_for_review":
                actions = self.runtime.run_github_event(data)
            elif action == "synchronize":
                actions = self.runtime.run_github_event(data)
            elif action == "review_requested":
                actions = self.runtime.run_github_event(data)
            elif github_override_event and event_name in {"issues", "pull_request"} and action == "labeled":
                actions = self.runtime.run_github_event(data)
            elif github_override_event and event_name == "issue_comment" and action == "created":
                actions = self.runtime.run_github_event(data)
            elif github_override_event and event_name == "pull_request_review" and action == "submitted":
                actions = self.runtime.run_github_event(data)
            elif action == "closed" and data.get("pull_request", {}).get("merged") is True:
                actions = self.runtime.run_github_event(data)

        elif self.path == "/linear":
            kind = data.get("type")
            if is_custom_agent_event(data):
                receiver_decision, actions = custom_agent_actions(data)
            elif kind == "comment_created":
                issue_key = data.get("issue_key", "")
                body = data.get("comment_body", "")
                pr_url = data.get("pr_url", "")
                actions = self.runtime.run_linear_event(data)
            elif kind == "issue_ready_gate":
                actions = self.runtime.run_linear_event(data)
            elif kind in ("issue_in_review", "issue_status_changed"):
                actions = self.runtime.run_linear_event(data)
            elif kind == "vera_qa_completed":
                actions = self.runtime.run_linear_event(data)
            elif kind in ("pm_label_changed", "acceptance_gate_changed", "pm_review_changed"):
                actions = self.runtime.run_linear_event(data)
            elif kind == "daily_aging_scan":
                actions = self.runtime.run_linear_event(data)

        else:
            self._json(404, {"ok": False, "error": "unknown-path"})
            return

        payload = {"ok": True, "actions": [a.__dict__ for a in actions], "dry_run": self.dry_run}
        if receiver_decision is not None:
            payload["receiver_ack"] = receiver_decision.ack_payload()
        apply_actions(actions, dry_run=self.dry_run, policy=self.policy)
        self._json(200, payload)


def main() -> int:
    ap = argparse.ArgumentParser(description="Linear bot webhook service")
    ap.add_argument("--host", default=os.getenv("BOT_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("BOT_PORT", "8787")))
    ap.add_argument("--dry-run", action="store_true", default=os.getenv("DRY_RUN", "true").lower() == "true")
    ap.add_argument("--sync-vera-results-once", action="store_true", help="scan completed Vera Kanban tasks once and sync QA results")
    args = ap.parse_args()

    Handler.dry_run = args.dry_run
    Handler.policy = GovernancePolicy.default()
    if args.sync_vera_results_once:
        count = sync_vera_qa_results_once(dry_run=args.dry_run, policy=Handler.policy)
        print(f"vera QA result sync processed={count} dry_run={args.dry_run}")
        return 0
    if env_truthy("VERA_QA_RESULT_SYNC_ENABLED"):
        os.environ.setdefault("VERA_QA_RESULT_SYNC_AFTER_EPOCH", str(int(time.time())))
        start_vera_qa_result_sync_thread(args.dry_run, Handler.policy)
    httpd = HTTPServer((args.host, args.port), Handler)
    print(f"listening on http://{args.host}:{args.port} dry_run={args.dry_run}")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
