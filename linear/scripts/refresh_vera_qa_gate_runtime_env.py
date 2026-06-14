#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Mapping, Optional


DEFAULT_SERVICE_ACCOUNT_ENV = "~/.hermes/profiles/vera/op-vault-service.env"
DEFAULT_OUTPUT_ENV = "~/.hermes/profiles/vera/vera-qa-gate-runtime.env"
DEFAULT_TRACE_STORE = "~/.hermes/profiles/vera/vera-qa-gate-runtime-trace.jsonl"
DEFAULT_VAULT = "Vera Runtime"
DEFAULT_GITHUB_ITEM = "Vera Runtime - Vera QA Gate GitHub App Private Key"
DEFAULT_LINEAR_ITEM = "Vera Runtime - Linear OAuth Apps"
DEFAULT_WORKSPACE_MAP = {
    "BitPod-App/taylor01-mind": "worktree:/Users/taylor01/BitPod-App/taylor01-mind",
    "BitPod-App/bitpod-tools": "worktree:/Users/taylor01/BitPod-App/bitpod-tools",
}


def _expand(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()


def parse_env_file(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    env_path = _expand(path)
    if not env_path.exists():
        raise FileNotFoundError(str(env_path))
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key:
            env[key] = value
    return env


def op_environment(service_account_env_path: str) -> Dict[str, str]:
    values = parse_env_file(service_account_env_path)
    token = values.get("OP_SERVICE_ACCOUNT_TOKEN", "")
    if not token:
        raise RuntimeError(f"OP_SERVICE_ACCOUNT_TOKEN missing from {service_account_env_path}")
    env = os.environ.copy()
    env["OP_SERVICE_ACCOUNT_TOKEN"] = token
    return env


def op_item_fields(vault: str, item: str, env: Mapping[str, str]) -> Dict[str, str]:
    proc = subprocess.run(
        ["op", "item", "get", item, "--vault", vault, "--format", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=dict(env),
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "op item get failed"
        raise RuntimeError(f"1Password read failed for item {item}: {detail}")
    data = json.loads(proc.stdout or "{}")
    fields: Dict[str, str] = {}
    for field in data.get("fields", []):
        if not isinstance(field, dict):
            continue
        value = field.get("value")
        if value is None:
            continue
        for name_key in ("label", "id"):
            name = str(field.get(name_key) or "").strip()
            if name:
                fields[name] = str(value)
    return fields


def _required(fields: Mapping[str, str], *names: str) -> str:
    for name in names:
        value = str(fields.get(name) or "").strip()
        if value:
            return value
    raise RuntimeError(f"missing required secret field; expected one of: {', '.join(names)}")


def fetch_linear_actor(
    *,
    client_id: str,
    client_secret: str,
    scope: str = "read write",
    token_url: str = "https://api.linear.app/oauth/token",
    api_url: str = "https://api.linear.app/graphql",
) -> Dict[str, str]:
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        token_url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        token_data = json.loads(response.read().decode("utf-8"))
    token = str(token_data.get("access_token") or "")
    if not token:
        raise RuntimeError("Linear OAuth client_credentials response missing access_token")

    query = json.dumps({"query": "query VeraQaGateViewer { viewer { id name email } }"}).encode("utf-8")
    viewer_request = urllib.request.Request(
        api_url,
        data=query,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(viewer_request, timeout=20) as response:
        viewer_data = json.loads(response.read().decode("utf-8"))
    viewer = (viewer_data.get("data") or {}).get("viewer") or {}
    actor_id = str(viewer.get("id") or "")
    if not actor_id:
        raise RuntimeError("Linear viewer probe did not return an actor id")
    return {
        "id": actor_id,
        "name": str(viewer.get("name") or ""),
        "email": str(viewer.get("email") or ""),
    }


def build_runtime_env(
    *,
    github_fields: Mapping[str, str],
    linear_fields: Mapping[str, str],
    linear_actor: Optional[Mapping[str, str]] = None,
    workspace_map: Optional[Mapping[str, str]] = None,
) -> Dict[str, str]:
    webhook_secret = _required(github_fields, "VERA_QA_GATE_WEBHOOK_SIGNING_SECRET")
    env: Dict[str, str] = {
        "DRY_RUN": "false",
        "BOT_HOST": "127.0.0.1",
        "BOT_PORT": "8796",
        "VERA_QA_DISPATCH_ENABLED": "true",
        "HERMES_CLI_PATH": str(Path.home() / ".local/bin/hermes"),
        "VERA_QA_GATE_LIVE_ENABLED": "true",
        "VERA_QA_RESULT_SYNC_ENABLED": "true",
        "VERA_QA_RESULT_SYNC_INTERVAL_SECONDS": "10",
        "VERA_QA_GATE_GITHUB_APP_ID": _required(github_fields, "VERA_QA_GATE_GITHUB_APP_ID"),
        "VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID": _required(
            github_fields, "VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID"
        ),
        "VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY": _required(github_fields, "VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY"),
        "VERA_QA_GATE_WEBHOOK_SIGNING_SECRET": webhook_secret,
        "GITHUB_WEBHOOK_SECRET": webhook_secret,
        "LINEAR_WEBHOOK_SECRET": webhook_secret,
        "LINEAR_LIVE_EXECUTOR_ENABLED": "true",
        "LINEAR_OAUTH_CLIENT_ID": _required(linear_fields, "LINEAR_OAUTH_CLIENT_ID", "CLIENT_ID"),
        "LINEAR_OAUTH_CLIENT_SECRET": _required(linear_fields, "LINEAR_OAUTH_CLIENT_SECRET", "CLIENT_SECRET"),
        "LINEAR_OAUTH_SCOPE": "read write",
        "TRACE_STORE_PATH": str(_expand(DEFAULT_TRACE_STORE)),
        "VERA_QA_KANBAN_WORKSPACE_MAP": json.dumps(dict(workspace_map or DEFAULT_WORKSPACE_MAP), sort_keys=True),
    }
    if linear_actor:
        actor_id = str(linear_actor.get("id") or "").strip()
        actor_name = str(linear_actor.get("name") or "").strip()
        actor_email = str(linear_actor.get("email") or "").strip()
        if actor_id:
            env["LINEAR_EXPECTED_ACTOR_ID"] = actor_id
        if actor_name:
            env["LINEAR_EXPECTED_ACTOR_NAME"] = actor_name
        if actor_email:
            env["LINEAR_EXPECTED_ACTOR_EMAIL"] = actor_email
    return env


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def render_shell_env(values: Mapping[str, str]) -> str:
    lines = [
        "# Generated by linear/scripts/refresh_vera_qa_gate_runtime_env.py",
        "# Machine-local runtime env; do not commit generated output.",
    ]
    for key in sorted(values):
        if not re.match(r"^[A-Z0-9_]+$", key):
            raise ValueError(f"invalid env key: {key}")
        lines.append(f"export {key}={_shell_quote(str(values[key]))}")
    return "\n".join(lines) + "\n"


def write_env_file(path: str, values: Mapping[str, str]) -> Path:
    output_path = _expand(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_shell_env(values)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(output_path.parent), delete=False) as fh:
        tmp_path = Path(fh.name)
        os.chmod(tmp_path, 0o600)
        fh.write(rendered)
    os.replace(tmp_path, output_path)
    os.chmod(output_path, 0o600)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh Vera QA Gate machine-local runtime env from 1Password.")
    parser.add_argument("--service-account-env", default=DEFAULT_SERVICE_ACCOUNT_ENV)
    parser.add_argument("--output-env", default=DEFAULT_OUTPUT_ENV)
    parser.add_argument("--vault", default=DEFAULT_VAULT)
    parser.add_argument("--github-item", default=DEFAULT_GITHUB_ITEM)
    parser.add_argument("--linear-item", default=DEFAULT_LINEAR_ITEM)
    parser.add_argument("--workspace-map-json", default="")
    parser.add_argument("--skip-linear-actor-probe", action="store_true")
    args = parser.parse_args()

    op_env = op_environment(args.service_account_env)
    github_fields = op_item_fields(args.vault, args.github_item, op_env)
    linear_fields = op_item_fields(args.vault, args.linear_item, op_env)
    client_id = _required(linear_fields, "LINEAR_OAUTH_CLIENT_ID", "CLIENT_ID")
    client_secret = _required(linear_fields, "LINEAR_OAUTH_CLIENT_SECRET", "CLIENT_SECRET")
    linear_actor = None
    if not args.skip_linear_actor_probe:
        linear_actor = fetch_linear_actor(client_id=client_id, client_secret=client_secret)
    workspace_map = json.loads(args.workspace_map_json) if args.workspace_map_json else DEFAULT_WORKSPACE_MAP
    values = build_runtime_env(
        github_fields=github_fields,
        linear_fields=linear_fields,
        linear_actor=linear_actor,
        workspace_map=workspace_map,
    )
    output = write_env_file(args.output_env, values)
    actor_summary = ""
    if linear_actor:
        actor_summary = f" linear_actor={linear_actor.get('name') or ''} ({linear_actor.get('id') or ''})"
    print(f"wrote Vera QA Gate runtime env: {output}{actor_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
