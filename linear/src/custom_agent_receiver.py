from __future__ import annotations

import hashlib
import hmac
import json
import os
import shlex
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Optional


ACK_DEADLINE_SECONDS = 5
FIRST_ACTIVITY_DEADLINE_SECONDS = 10
LOCAL_DISPATCH_FLAG = "LINEAR_CUSTOM_AGENT_LOCAL_DISPATCH_ENABLED"
LINEAR_WEBHOOK_SECRET_ENV = "LINEAR_WEBHOOK_SECRET"
PEER_ENABLED_ENV_PREFIX = "LINEAR_CUSTOM_AGENT"
SHARED_RECEIVER_PATH = "shared-linear-custom-agent-receiver"
SUPPORTED_PEERS = ("codex", "claude")
REQUIRED_OAUTH_SCOPES = ("read", "write", "app:assignable", "app:mentionable")
WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS = 60


class ReceiverConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SignatureVerificationResult:
    ok: bool
    reason: str


@dataclass(frozen=True)
class PeerConfig:
    peer_id: str
    enabled: bool = True
    local_command: tuple[str, ...] = ()
    activity_comment_template: str = (
        "AgentSession accepted for {issue_key} by canonical peer {peer_id} "
        "through the shared local receiver."
    )

    def __post_init__(self) -> None:
        peer_id = self.peer_id.strip().lower()
        if peer_id not in SUPPORTED_PEERS:
            raise ReceiverConfigError(f"unsupported peer route: {self.peer_id}")
        object.__setattr__(self, "peer_id", peer_id)


@dataclass(frozen=True)
class ReceiverConfig:
    peers: Mapping[str, PeerConfig] = field(default_factory=dict)
    local_dispatch_enabled: bool = False
    oauth_scopes: tuple[str, ...] = REQUIRED_OAUTH_SCOPES
    ack_deadline_seconds: int = ACK_DEADLINE_SECONDS
    first_activity_deadline_seconds: int = FIRST_ACTIVITY_DEADLINE_SECONDS

    @classmethod
    def default(cls) -> "ReceiverConfig":
        return cls(
            peers={
                "codex": _peer_config_from_env("codex", default_enabled=True),
                "claude": _peer_config_from_env("claude", default_enabled=False),
            },
            local_dispatch_enabled=_env_truthy(LOCAL_DISPATCH_FLAG),
        )

    def peer(self, peer_id: str) -> Optional[PeerConfig]:
        return self.peers.get(peer_id.strip().lower())


@dataclass(frozen=True)
class ReceiverRequest:
    issue_key: str
    peer_id: str = "codex"
    session_id: str = ""
    actor_id: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReceiverDecision:
    accepted: bool
    peer_id: str
    issue_key: str
    session_id: str
    app_actor_id: str
    ack_deadline_seconds: int
    first_activity_deadline_seconds: int
    oauth_scopes: tuple[str, ...]
    dispatch_allowed: bool
    cloud_job_allowed: bool
    reason: str
    receiver_path: str = SHARED_RECEIVER_PATH
    dispatch_surface: str = "blocked"
    first_activity: Optional[Dict[str, str]] = None
    local_command: tuple[str, ...] = ()

    def ack_payload(self) -> Dict[str, Any]:
        return {
            "ok": self.accepted,
            "peer": self.peer_id,
            "issue_key": self.issue_key,
            "session_id": self.session_id,
            "ack_deadline_seconds": self.ack_deadline_seconds,
            "first_activity_deadline_seconds": self.first_activity_deadline_seconds,
            "dispatch_allowed": self.dispatch_allowed,
            "cloud_job_allowed": self.cloud_job_allowed,
            "receiver_path": self.receiver_path,
            "dispatch_surface": self.dispatch_surface,
            "reason": self.reason,
        }


def plan_receiver_decision(
    request: ReceiverRequest,
    config: Optional[ReceiverConfig] = None,
) -> ReceiverDecision:
    cfg = config or ReceiverConfig.default()
    peer_id = request.peer_id.strip().lower()
    peer = cfg.peer(peer_id)

    if not request.issue_key.strip():
        return _blocked(request, cfg, peer_id, "missing issue key")
    if peer is None:
        return _blocked(request, cfg, peer_id, "unsupported peer route")
    if not peer.enabled:
        return _blocked(request, cfg, peer_id, "peer disabled")
    if not _has_required_scopes(cfg.oauth_scopes):
        return _blocked(request, cfg, peer_id, "missing required OAuth scopes")
    if not cfg.local_dispatch_enabled:
        return _blocked(request, cfg, peer_id, f"{LOCAL_DISPATCH_FLAG} is not enabled")
    if not request.session_id.strip():
        return _blocked(request, cfg, peer_id, "missing AgentSession id")

    activity = {
        "system": "linear",
        "kind": "agent_activity",
        "target": request.session_id.strip(),
        "issue_key": request.issue_key.strip(),
        "content_type": "thought",
        "body": peer.activity_comment_template.format(
            issue_key=request.issue_key.strip(),
            peer_id=peer.peer_id,
            session_id=request.session_id,
        ),
    }
    return ReceiverDecision(
        accepted=True,
        peer_id=peer.peer_id,
        issue_key=request.issue_key.strip(),
        session_id=request.session_id.strip(),
        app_actor_id=request.actor_id.strip(),
        ack_deadline_seconds=cfg.ack_deadline_seconds,
        first_activity_deadline_seconds=cfg.first_activity_deadline_seconds,
        oauth_scopes=tuple(cfg.oauth_scopes),
        dispatch_allowed=True,
        cloud_job_allowed=False,
        dispatch_surface="local-receiver",
        reason="local dispatch gate enabled",
        first_activity=activity,
        local_command=peer.local_command,
    )


def _blocked(
    request: ReceiverRequest,
    config: ReceiverConfig,
    peer_id: str,
    reason: str,
) -> ReceiverDecision:
    return ReceiverDecision(
        accepted=False,
        peer_id=peer_id,
        issue_key=request.issue_key.strip(),
        session_id=request.session_id.strip(),
        app_actor_id=request.actor_id.strip(),
        ack_deadline_seconds=config.ack_deadline_seconds,
        first_activity_deadline_seconds=config.first_activity_deadline_seconds,
        oauth_scopes=tuple(config.oauth_scopes),
        dispatch_allowed=False,
        cloud_job_allowed=False,
        dispatch_surface="blocked",
        reason=reason,
    )


def build_mention_delegate_canaries(issue_key: str, peer_id: str) -> tuple[ReceiverRequest, ReceiverRequest]:
    return (
        ReceiverRequest(issue_key=issue_key, peer_id=peer_id, payload={"trigger": "mention"}),
        ReceiverRequest(issue_key=issue_key, peer_id=peer_id, payload={"trigger": "delegate"}),
    )


def verify_linear_signature(
    *,
    raw_body: bytes,
    header_signature: str | None,
    signing_secret: str | None,
    now_ms: int | None = None,
    tolerance_seconds: int = WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS,
) -> SignatureVerificationResult:
    """Verify Linear webhook HMAC and replay timestamp without exposing secrets."""
    if not signing_secret:
        return SignatureVerificationResult(False, "missing signing secret")
    signature = (header_signature or "").strip()
    if not signature:
        return SignatureVerificationResult(False, "missing Linear-Signature header")
    if signature.lower().startswith("sha256="):
        signature = signature.split("=", 1)[1].strip()

    computed = hmac.new(signing_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, signature):
        return SignatureVerificationResult(False, "invalid webhook signature")

    try:
        body = json.loads(raw_body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return SignatureVerificationResult(False, "invalid webhook JSON")

    timestamp = _coerce_timestamp_ms(body.get("webhookTimestamp"))
    if timestamp is None:
        return SignatureVerificationResult(False, "missing webhook timestamp")

    current_ms = int(time.time() * 1000) if now_ms is None else now_ms
    if abs(current_ms - timestamp) > tolerance_seconds * 1000:
        return SignatureVerificationResult(False, "stale webhook timestamp")

    return SignatureVerificationResult(True, "signature verified")


def _has_required_scopes(scopes: Iterable[str]) -> bool:
    return set(REQUIRED_OAUTH_SCOPES).issubset(set(scopes))


def _peer_config_from_env(peer_id: str, default_enabled: bool) -> PeerConfig:
    env_prefix = f"{PEER_ENABLED_ENV_PREFIX}_{peer_id.upper()}"
    enabled_value = os.getenv(f"{env_prefix}_ENABLED")
    enabled = default_enabled if enabled_value is None else _truthy_value(enabled_value)
    return PeerConfig(
        peer_id,
        enabled=enabled,
        local_command=_env_command(f"{env_prefix}_COMMAND"),
    )


def _env_command(name: str) -> tuple[str, ...]:
    value = os.getenv(name, "").strip()
    if not value:
        return ()
    return tuple(shlex.split(value))


def _env_truthy(name: str) -> bool:
    return _truthy_value(os.getenv(name, ""))


def _truthy_value(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _coerce_timestamp_ms(value: Any) -> int | None:
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None
    if timestamp <= 0:
        return None
    return timestamp
