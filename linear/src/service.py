#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import subprocess
import tempfile
import textwrap
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, Optional, Tuple

try:
    from linear.src.engine import Action, format_actions
    from linear.src.governance import GovernancePolicy
    from linear.src.linear_executor import LinearExecutionError, LinearExecutor
    from linear.src.memory import JsonlFileStore, MemoryEvent, now_iso
    from linear.src.runtime import BotRuntime
except ModuleNotFoundError:
    from engine import Action, format_actions
    from governance import GovernancePolicy
    from linear_executor import LinearExecutionError, LinearExecutor
    from memory import JsonlFileStore, MemoryEvent, now_iso
    from runtime import BotRuntime




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
    installation_id = os.getenv("VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID", "").strip()
    private_key = os.getenv("VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY", "").strip()
    if not (app_id and installation_id and private_key):
        raise RuntimeError("missing Vera QA Gate GitHub App credentials; set VERA_QA_GATE_GITHUB_TOKEN or app id/installation id/private key")
    jwt_token = _github_app_jwt(app_id, private_key)
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


def execute_hermes_vera_dispatch(action: Action) -> str:
    if not env_truthy("VERA_QA_DISPATCH_ENABLED"):
        raise RuntimeError("vera QA dispatch switch is off; set VERA_QA_DISPATCH_ENABLED=true to enqueue Hermes Vera QA tasks")
    title = str(action.payload.get("title") or f"Vera QA review: {action.target}")
    body = str(action.payload.get("body") or "")
    assignee = str(action.payload.get("assignee") or "vera")
    idempotency_key = str(action.payload.get("idempotency_key") or f"vera-qa:{action.target}")
    workspace = str(os.getenv("VERA_QA_KANBAN_WORKSPACE", "scratch") or "scratch")
    cmd = [
        "hermes",
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
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "hermes kanban create failed"
        raise RuntimeError(detail)
    return "hermes kanban create " + (proc.stdout.strip() or idempotency_key)

def parse_pr_url(pr_url: str) -> Tuple[str, str, str]:
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url or "")
    if not m:
        return "", "", ""
    return m.group(1), m.group(2), m.group(3)


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
) -> None:
    policy = policy or GovernancePolicy.default()
    if dry_run:
        print("[DRY_RUN] would apply actions:")
        print(format_actions(actions))
        for a in actions:
            decision = policy.decide(a, dry_run=True)
            trace_action(a, "dry-run", decision.reason, decision.policy_class)
        return

    # Live mode is still fail-closed: governance must allow the action first,
    # then Linear live execution must pass its own kill switch + actor checks.
    for a in actions:
        decision = policy.decide(a, dry_run=False)
        if not decision.allowed:
            print(f"[LIVE][FAIL-CLOSED] governance blocked {a.kind} {a.target}: {decision.reason}")
            trace_action(a, "blocked", decision.reason, decision.policy_class)
            continue
        if a.system == "github" and a.kind == "comment":
            owner, repo, num = parse_pr_url(a.target)
            if owner and repo and num:
                subprocess.run(
                    [
                        "gh",
                        "pr",
                        "comment",
                        num,
                        "-R",
                        f"{owner}/{repo}",
                        "--body",
                        a.payload.get("body", ""),
                    ],
                    check=False,
                )
                trace_action(a, "executed", "gh pr comment", decision.policy_class)
                continue
            print(f"[LIVE][SKIP] invalid github target for comment: {a.target}")
            trace_action(a, "skipped", "invalid github target", decision.policy_class)
            continue

        if a.system == "github" and a.kind == "check_run":
            try:
                detail = execute_github_check_run(a)
            except Exception as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] github check_run {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                continue
            print(f"[LIVE] github check_run {a.target}: {detail}")
            trace_action(a, "executed", detail, decision.policy_class)
            continue

        if a.system == "hermes" and a.kind == "enqueue_vera_qa":
            try:
                detail = execute_hermes_vera_dispatch(a)
            except Exception as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] hermes enqueue_vera_qa {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                continue
            print(f"[LIVE] hermes enqueue_vera_qa {a.target}: {detail}")
            trace_action(a, "executed", detail, decision.policy_class)
            continue

        if a.system == "linear":
            executor = linear_executor or LinearExecutor.from_env()
            try:
                result = executor.execute(a)
            except LinearExecutionError as exc:
                detail = str(exc)
                print(f"[LIVE][FAIL-CLOSED] linear {a.kind} {a.target}: {detail}")
                trace_action(a, "blocked", detail, decision.policy_class)
                continue
            print(f"[LIVE] linear {a.kind} {a.target}: {result.detail}")
            trace_action(a, result.outcome, result.detail, decision.policy_class, actor=result.actor)
            continue

        print(f"[LIVE][SKIP] unknown action: {a}")
        trace_action(a, "skipped", "unknown action", decision.policy_class)


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

        if self.path == "/github":
            action = data.get("action")
            if action == "opened":
                actions = self.runtime.run_github_event(data)
            elif action == "ready_for_review":
                actions = self.runtime.run_github_event(data)
            elif action == "review_requested":
                actions = self.runtime.run_github_event(data)
            elif action == "closed" and data.get("pull_request", {}).get("merged") is True:
                actions = self.runtime.run_github_event(data)

        elif self.path == "/linear":
            kind = data.get("type")
            if kind == "comment_created":
                issue_key = data.get("issue_key", "")
                body = data.get("comment_body", "")
                pr_url = data.get("pr_url", "")
                actions = self.runtime.run_linear_event(data)
            elif kind == "issue_ready_gate":
                actions = self.runtime.run_linear_event(data)
            elif kind in ("issue_in_review", "issue_status_changed"):
                actions = self.runtime.run_linear_event(data)
            elif kind in ("pm_label_changed", "acceptance_gate_changed", "pm_review_changed"):
                actions = self.runtime.run_linear_event(data)
            elif kind == "daily_aging_scan":
                actions = self.runtime.run_linear_event(data)

        else:
            self._json(404, {"ok": False, "error": "unknown-path"})
            return

        apply_actions(actions, dry_run=self.dry_run, policy=self.policy)
        self._json(200, {"ok": True, "actions": [a.__dict__ for a in actions], "dry_run": self.dry_run})


def main() -> int:
    ap = argparse.ArgumentParser(description="Linear bot webhook service")
    ap.add_argument("--host", default=os.getenv("BOT_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("BOT_PORT", "8787")))
    ap.add_argument("--dry-run", action="store_true", default=os.getenv("DRY_RUN", "true").lower() == "true")
    args = ap.parse_args()

    Handler.dry_run = args.dry_run
    Handler.policy = GovernancePolicy.default()
    httpd = HTTPServer((args.host, args.port), Handler)
    print(f"listening on http://{args.host}:{args.port} dry_run={args.dry_run}")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
