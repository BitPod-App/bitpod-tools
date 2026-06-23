from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

try:
    from linear.src.custom_agent_receiver import (
        REQUIRED_OAUTH_SCOPES,
        ReceiverConfig,
        ReceiverRequest,
        build_mention_delegate_canaries,
        plan_receiver_decision,
    )
except ModuleNotFoundError:
    from custom_agent_receiver import (  # type: ignore[no-redef]
        REQUIRED_OAUTH_SCOPES,
        ReceiverConfig,
        ReceiverRequest,
        build_mention_delegate_canaries,
        plan_receiver_decision,
    )


REQUIRED_ACTOR_SCOPES = REQUIRED_OAUTH_SCOPES
HUMAN_ATTRIBUTION_NAMES = {"cj", "taylor01", "taylor", "01taylorolduser"}
BLOCKED_MENTION_TERMS = ("Taylor", "Vera", "Codex", "Claude", "GPT")


@dataclass(frozen=True)
class ActorCanaryCheck:
    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


@dataclass(frozen=True)
class ActorCanarySpec:
    actor_id: str
    display_name: str
    actor_type: str
    oauth_scopes: tuple[str, ...]
    assignable: bool
    mentionable: bool
    attribution_expected: str
    route: str
    cloud_job_allowed: bool
    receiver_peer_id: str = ""
    generated_activity_bodies: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActorCanaryResult:
    actor_id: str
    display_name: str
    route: str
    checks: tuple[ActorCanaryCheck, ...]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "display_name": self.display_name,
            "route": self.route,
            "ok": self.ok,
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass(frozen=True)
class ActorCanaryReport:
    ok: bool
    issue_key: str
    actor_results: tuple[ActorCanaryResult, ...]
    gpt_result: ActorCanaryResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "issue_key": self.issue_key,
            "actor_results": [result.to_dict() for result in self.actor_results],
            "gpt_result": self.gpt_result.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def to_markdown(self) -> str:
        lines = [
            f"# BIT-600 actor canary report for {self.issue_key}",
            "",
            f"Overall: {'PASS' if self.ok else 'FAIL'}",
            "",
        ]
        for result in (*self.actor_results, self.gpt_result):
            lines.append(f"## {result.display_name}")
            lines.append("")
            lines.append(f"Route: `{result.route}`")
            lines.append(f"Result: {'PASS' if result.ok else 'FAIL'}")
            for check in result.checks:
                marker = "PASS" if check.ok else "FAIL"
                lines.append(f"- {marker}: {check.name} — {check.detail}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def build_default_actor_canary_specs() -> tuple[ActorCanarySpec, ...]:
    return (
        ActorCanarySpec(
            actor_id="taylor",
            display_name="taylor [Agent]",
            actor_type="app",
            oauth_scopes=REQUIRED_ACTOR_SCOPES,
            assignable=True,
            mentionable=True,
            attribution_expected="taylor [Agent]",
            route="app-actor",
            cloud_job_allowed=False,
        ),
        ActorCanarySpec(
            actor_id="vera",
            display_name="vera [Agent]",
            actor_type="app",
            oauth_scopes=REQUIRED_ACTOR_SCOPES,
            assignable=True,
            mentionable=True,
            attribution_expected="vera [Agent]",
            route="app-actor",
            cloud_job_allowed=False,
        ),
        ActorCanarySpec(
            actor_id="codex",
            display_name="codex [Agent]",
            actor_type="app",
            oauth_scopes=REQUIRED_ACTOR_SCOPES,
            assignable=True,
            mentionable=True,
            attribution_expected="codex [Agent]",
            route="custom-agent-receiver",
            receiver_peer_id="codex",
            cloud_job_allowed=False,
        ),
        ActorCanarySpec(
            actor_id="claude",
            display_name="claude [Agent]",
            actor_type="app",
            oauth_scopes=REQUIRED_ACTOR_SCOPES,
            assignable=True,
            mentionable=True,
            attribution_expected="claude [Agent]",
            route="custom-agent-receiver",
            receiver_peer_id="claude",
            cloud_job_allowed=False,
        ),
    )


def run_actor_canary_suite(
    *,
    specs: Sequence[ActorCanarySpec] | None = None,
    issue_key: str = "BIT-600",
    receiver_config: ReceiverConfig | None = None,
    gpt_actor_path_enabled: bool = False,
) -> ActorCanaryReport:
    actor_specs = tuple(build_default_actor_canary_specs() if specs is None else specs)
    results = tuple(_evaluate_actor_spec(spec, issue_key, receiver_config) for spec in actor_specs)
    gpt_result = _evaluate_gpt_non_actor(gpt_actor_path_enabled)
    return ActorCanaryReport(
        ok=all(result.ok for result in results) and gpt_result.ok,
        issue_key=issue_key,
        actor_results=results,
        gpt_result=gpt_result,
    )


def _evaluate_actor_spec(
    spec: ActorCanarySpec,
    issue_key: str,
    receiver_config: ReceiverConfig | None,
) -> ActorCanaryResult:
    checks = [
        _check_actor_identity(spec),
        _check_required_scopes(spec),
        ActorCanaryCheck("assignable", spec.assignable, "actor is assignable" if spec.assignable else "actor is not assignable"),
        ActorCanaryCheck("mentionable", spec.mentionable, "actor is mentionable" if spec.mentionable else "actor is not mentionable"),
        _check_attribution(spec),
        ActorCanaryCheck("no cloud job", not spec.cloud_job_allowed, "cloud_job_allowed=false" if not spec.cloud_job_allowed else "cloud_job_allowed must remain false"),
        _check_generated_mentions(spec.generated_activity_bodies),
    ]
    if spec.route == "custom-agent-receiver":
        checks.append(_check_receiver_route(spec, issue_key, receiver_config))
    else:
        checks.append(ActorCanaryCheck("route expectation", spec.route == "app-actor", f"route={spec.route}"))
    return ActorCanaryResult(spec.actor_id, spec.display_name, spec.route, tuple(checks))


def _check_actor_identity(spec: ActorCanarySpec) -> ActorCanaryCheck:
    ok = bool(spec.actor_id.strip()) and bool(spec.display_name.strip()) and spec.actor_type == "app"
    detail = f"actor_id={spec.actor_id}, display_name={spec.display_name}, actor_type={spec.actor_type}"
    if not ok:
        detail = "actor identity must include non-empty id/display name and actor_type=app"
    return ActorCanaryCheck("actor identity", ok, detail)


def _check_required_scopes(spec: ActorCanarySpec) -> ActorCanaryCheck:
    missing = sorted(set(REQUIRED_ACTOR_SCOPES) - set(spec.oauth_scopes))
    if missing:
        return ActorCanaryCheck("required OAuth scopes", False, "missing " + ", ".join(missing))
    return ActorCanaryCheck("required OAuth scopes", True, "read/write/app assignable/app mentionable present")


def _check_attribution(spec: ActorCanarySpec) -> ActorCanaryCheck:
    expected = spec.attribution_expected.strip()
    normalized = expected.lower()
    ok = bool(expected) and normalized not in HUMAN_ATTRIBUTION_NAMES and "[agent]" in normalized
    detail = f"expected attribution={expected}"
    if not ok:
        detail = f"{expected or '<missing>'} is not app/agent attribution"
    return ActorCanaryCheck("comment attribution", ok, detail)


def _check_generated_mentions(bodies: Iterable[str]) -> ActorCanaryCheck:
    for body in bodies:
        mention = _first_blocked_mention(body)
        if mention:
            return ActorCanaryCheck("no generated actor mention", False, f"generated body contains {mention}")
    return ActorCanaryCheck("no generated actor mention", True, "no blocked actor @mention text generated")


def _check_receiver_route(
    spec: ActorCanarySpec,
    issue_key: str,
    receiver_config: ReceiverConfig | None,
) -> ActorCanaryCheck:
    if not spec.receiver_peer_id:
        return ActorCanaryCheck("local receiver route", False, "missing receiver peer id")
    failures: list[str] = []
    canaries = build_mention_delegate_canaries(issue_key=issue_key, peer_id=spec.receiver_peer_id)
    for request in canaries:
        trigger = str(request.payload.get("trigger", "canary"))
        decision = plan_receiver_decision(
            ReceiverRequest(
                issue_key=request.issue_key,
                peer_id=request.peer_id,
                session_id=f"canary-{spec.receiver_peer_id}-{trigger}",
                payload=request.payload,
            ),
            receiver_config,
        )
        body = "" if not decision.first_activity else decision.first_activity.get("body", "")
        if not decision.accepted:
            failures.append(f"{trigger}: {decision.reason}")
        if decision.peer_id != spec.receiver_peer_id:
            failures.append(f"{trigger}: peer={decision.peer_id}")
        if decision.receiver_path != "shared-linear-custom-agent-receiver":
            failures.append(f"{trigger}: receiver_path={decision.receiver_path}")
        if decision.dispatch_surface != "local-receiver":
            failures.append(f"{trigger}: dispatch_surface={decision.dispatch_surface}")
        if decision.cloud_job_allowed:
            failures.append(f"{trigger}: cloud_job_allowed=true")
        mention = _first_blocked_mention(body)
        if mention:
            failures.append(f"{trigger}: generated {mention}")
    if failures:
        return ActorCanaryCheck("local receiver route", False, "; ".join(failures))
    return ActorCanaryCheck("local receiver route", True, "mention/delegate canaries use shared local receiver with cloud_job_allowed=false")


def _evaluate_gpt_non_actor(actor_path_enabled: bool) -> ActorCanaryResult:
    detail = "gpt has no actor path"
    if actor_path_enabled:
        detail = "gpt actor path must remain disabled"
    return ActorCanaryResult(
        actor_id="gpt",
        display_name="gpt (silent planner)",
        route="no-actor-path",
        checks=(ActorCanaryCheck("no actor path", not actor_path_enabled, detail),),
    )


def _first_blocked_mention(body: str) -> str:
    for term in BLOCKED_MENTION_TERMS:
        match = re.search(rf"@{re.escape(term)}(?:\b|\s|$)", body, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""
