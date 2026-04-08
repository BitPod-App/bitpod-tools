#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import shlex
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SECTION_NAMES = {
    "Result",
    "Verification",
    "Parity summary",
    "Workspace hygiene",
    "Queue health",
    "Cleanup plan",
    "Tier-specific checks",
    "Next action",
    "Registry",
}


@dataclass
class Alert:
    code: str
    severity: str
    category: str
    message: str
    subject_type: str
    subject_path: str = ""
    subject_ref: str = ""
    recommended_action: str = ""
    policy_rule_ids: list[str] = field(default_factory=list)


@dataclass
class CompletedEngineRun:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    command: list[str]
    duration_ms: int


class BitPodAuditAdapter:
    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        workspace_root = Path(
            os.getenv("BITPOD_APP_ROOT", "").strip()
            or os.getenv("WORKSPACE", "").strip()
            or str(repo_root.parent)
        ).expanduser()
        self.workspace_root = workspace_root
        self.repo_root = repo_root
        self.timeout_seconds = int(os.getenv("BITPOD_AUDIT_ADAPTER_TIMEOUT_SECONDS", "120"))
        self.audit_script = repo_root / "audit_ctl.sh"
        self.registry_file = repo_root / "config" / "repo_registry.tsv"
        self.zone_policy_file = repo_root / "config" / "cleanup_zones_policy.tsv"
        self.contract_file = workspace_root / "bitpod-docs" / "process" / "local-workspace-skeleton-contract.toml"

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        if request.get("kind") == "capabilities":
            return {
                "contract_versions": ["v1", "v2"],
                "actions": ["cleanup-audit", "parity-pulse", "cleanup", "assessment"],
                "effects": {"planned": [], "applied": [], "highest_authority_used": "none"},
            }

        alerts: list[Alert] = []
        try:
            engine_run = self._execute(request)
        except Exception as exc:
            return {
                "result": "DEGRADED",
                "verification": "NOT VERIFIED",
                "summary": {"detail": str(exc)},
                "findings": [],
                "alerts": [
                    asdict(
                        Alert(
                            code="ASVC-001",
                            severity="high",
                            category="engine_failure",
                            message=f"BitPod adapter failed before execution: {exc}",
                            subject_type="adapter",
                            subject_path=str(self.audit_script),
                            recommended_action="Verify workspace root and adapter configuration.",
                        )
                    )
                ],
                "engine": {
                    "name": "bitpod-audit-legacy-shell",
                    "adapter": "bitpod",
                    "status": "degraded",
                    "command": [],
                    "exit_code": None,
                    "timed_out": False,
                    "duration_ms": 0,
                },
            }

        parsed = self._parse_markdown(engine_run.stdout)

        if engine_run.timed_out:
            alerts.append(
                Alert(
                    code="ASVC-002",
                    severity="high",
                    category="engine_timeout",
                    message=f"BitPod audit engine timed out after {self.timeout_seconds}s.",
                    subject_type="engine",
                    subject_path=str(self.audit_script),
                    recommended_action="Inspect the underlying engine hang before trusting fallback output.",
                )
            )
        if not parsed["result"]:
            alerts.append(
                Alert(
                    code="ASVC-003",
                    severity="high",
                    category="parse_failure",
                    message="BitPod adapter could not parse a valid result from engine output.",
                    subject_type="engine_output",
                    recommended_action="Inspect stdout/stderr and update the parser.",
                )
            )
        if parsed["result"] == "FRACTURED":
            alerts.append(
                Alert(
                    code="ASVC-100",
                    severity="medium",
                    category="cleanup_failure",
                    message="cleanup-audit did not achieve PORCELAIN.",
                    subject_type="cleanup_run",
                    recommended_action="Review findings and remediate until a fresh T3 passes.",
                )
            )
        elif parsed["result"] in {"INFERRED", "ASSUMED", "UNSURE", "DIVERGED", "UNKNOWN"}:
            alerts.append(
                Alert(
                    code="ASVC-101",
                    severity="medium",
                    category="parity_degraded",
                    message=f"parity-pulse returned {parsed['result']}.",
                    subject_type="parity_run",
                    recommended_action="Inspect non-1:1 findings before treating parity as trustworthy.",
                )
            )

        engine = {
            "name": "bitpod-audit-legacy-shell",
            "adapter": "bitpod",
            "status": "degraded" if engine_run.timed_out else "completed",
            "command": engine_run.command,
            "exit_code": engine_run.exit_code,
            "timed_out": engine_run.timed_out,
            "duration_ms": engine_run.duration_ms,
            "stderr": engine_run.stderr.strip(),
            "stdout_chars": len(engine_run.stdout),
        }
        effects = parsed["effects"]
        if request.get("phase") == "apply":
            effects = {
                "planned": [],
                "applied": effects.get("planned", []),
                "highest_authority_used": effects.get("highest_authority_used", "none"),
            }
        return {
            "result": parsed["result"] or "DEGRADED",
            "verification": parsed["verification"] or "NOT VERIFIED",
            "summary": parsed["summary"],
            "findings": parsed["findings"],
            "alerts": [asdict(alert) for alert in alerts],
            "effects": effects,
            "plan_id": parsed["plan_id"],
            "engine": engine,
        }

    def _execute(self, request: dict[str, Any]) -> CompletedEngineRun:
        command_request = self._request_to_phrase(request)
        env = os.environ.copy()
        env["BITPOD_APP_ROOT"] = str(self.workspace_root)
        env["WORKSPACE"] = str(self.workspace_root)
        env["BITPOD_CLEANUP_ZONE_POLICY_FILE"] = str(self.zone_policy_file)
        env["BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE"] = str(self.contract_file)

        if request.get("profile"):
            env["BITPOD_LOCAL_WORKSPACE_PROFILE"] = str(request["profile"])

        temp_registry: tempfile.NamedTemporaryFile | None = None
        repo_scope = request.get("repo_scope", "all")
        if isinstance(repo_scope, list) and repo_scope and repo_scope != ["all"]:
            temp_registry = self._build_filtered_registry(repo_scope)
            env["BITPOD_REPO_REGISTRY_FILE"] = temp_registry.name
        else:
            env["BITPOD_REPO_REGISTRY_FILE"] = str(self.registry_file)

        command = [str(self.audit_script), command_request]
        start = time.time()
        try:
            proc = subprocess.run(
                command,
                cwd=str(self.workspace_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            exit_code = 124
            timed_out = True
        finally:
            if temp_registry is not None:
                temp_registry.close()

        return CompletedEngineRun(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=timed_out,
            command=command,
            duration_ms=int((time.time() - start) * 1000),
        )

    def _build_filtered_registry(self, repo_scope: list[str]) -> tempfile.NamedTemporaryFile:
        wanted = {item.strip() for item in repo_scope if item.strip()}
        tmp = tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv")
        with self.registry_file.open("r", encoding="utf-8") as src:
            for raw in src:
                if raw.startswith("#") or not raw.strip():
                    tmp.write(raw)
                    continue
                parts = next(csv.reader([raw], delimiter="|"))
                if parts and parts[0] in wanted:
                    tmp.write(raw)
        tmp.flush()
        return tmp

    def _request_to_phrase(self, request: dict[str, Any]) -> str:
        if request.get("surface") == "cleanup-audit" or (
            request.get("family") == "execution" and request.get("action") == "cleanup"
        ):
            tier = request.get("tier") or "T1"
            tokens = ["run", tier, "cleanup", "audit"]
            if request.get("phase") == "apply":
                tokens.extend(["execute", "local-workspace"])
            if request.get("force"):
                tokens.extend(["force", "full"])
            if request.get("include_local_workspace") is False:
                tokens.extend(["only", "repos"])
            return " ".join(tokens)

        tokens = ["parity-pulse", f"event={request.get('event_name') or request.get('mode') or 'manual'}"]
        if request.get("fresh"):
            tokens.append("fresh")
        return " ".join(tokens)

    def _parse_markdown(self, text: str) -> dict[str, Any]:
        sections: dict[str, list[str]] = {}
        current: str | None = None
        findings: list[dict[str, Any]] = []
        section_order: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if not line:
                continue
            if line in SECTION_NAMES:
                current = line
                sections.setdefault(current, [])
                section_order.append(current)
                continue
            if current is None:
                sections.setdefault("__preamble__", []).append(line)
            else:
                sections[current].append(line)

        result_data = self._parse_key_value_lines(sections.get("Result", []))
        verification_data = self._parse_key_value_lines(sections.get("Verification", []))
        parity_data, parity_findings = self._parse_parity_summary(sections.get("Parity summary", []))
        findings.extend(parity_findings)
        cleanup_plan_data, cleanup_plan_findings = self._parse_cleanup_plan(sections.get("Cleanup plan", []))
        findings.extend(cleanup_plan_findings)
        tier_checks, tier_findings = self._parse_tier_specific(sections.get("Tier-specific checks", []))
        findings.extend(tier_findings)

        summary: dict[str, Any] = {
            "result_section": result_data,
            "verification_section": verification_data,
            "parity_summary": parity_data,
            "workspace_hygiene": self._parse_key_value_lines(sections.get("Workspace hygiene", [])),
            "queue_health": self._parse_key_value_lines(sections.get("Queue health", [])),
            "cleanup_plan": cleanup_plan_data,
            "tier_specific": tier_checks,
            "next_action": [line[2:] if line.startswith("- ") else line for line in sections.get("Next action", [])],
            "sections_present": section_order,
        }
        effects = self._effects_from_cleanup_plan(sections.get("Cleanup plan", []))
        return {
            "result": result_data.get("result", parity_data.get("overall", "")),
            "verification": verification_data.get("overall", verification_data.get("verification", "")),
            "summary": summary,
            "findings": findings,
            "effects": effects,
            "plan_id": result_data.get("plan_id"),
        }

    def _parse_key_value_lines(self, lines: list[str]) -> dict[str, Any]:
        data: dict[str, Any] = {}
        extras: list[str] = []
        for line in lines:
            bullet = line[2:] if line.startswith("- ") else line
            if "=" in bullet:
                key, value = bullet.split("=", 1)
                data[key.strip()] = value.strip()
            else:
                extras.append(bullet)
        if extras:
            data["_lines"] = extras
        return data

    def _parse_parity_summary(self, lines: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        data: dict[str, Any] = {}
        findings: list[dict[str, Any]] = []
        for line in lines:
            bullet = line[2:] if line.startswith("- ") else line
            if re.match(r"1:\d+\s+\|", bullet):
                findings.append(self._parse_repo_finding(bullet))
                continue
            if "=" in bullet:
                key, value = bullet.split("=", 1)
                data[key.strip()] = value.strip()
            else:
                data.setdefault("_lines", []).append(bullet)
        return data, findings

    def _parse_cleanup_plan(self, lines: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        data: dict[str, Any] = {}
        findings: list[dict[str, Any]] = []
        for line in lines:
            bullet = line[2:] if line.startswith("- ") else line
            if bullet.startswith("finding_id="):
                findings.append(self._parse_field_series("cleanup_plan", bullet))
                continue
            if "=" in bullet:
                key, value = bullet.split("=", 1)
                data[key.strip()] = value.strip()
            else:
                data.setdefault("_lines", []).append(bullet)
        return data, findings

    def _effects_from_cleanup_plan(self, lines: list[str]) -> dict[str, Any]:
        planned: list[dict[str, Any]] = []
        for line in lines:
            bullet = line[2:] if line.startswith("- ") else line
            if not bullet.startswith("finding_id="):
                continue
            item = self._parse_field_series("cleanup_plan", bullet)
            if item.get("execution_allowed") != "true":
                continue
            action = item.get("action", "")
            authority = "delete" if action == "os_trash_candidate" else "write"
            planned.append(
                {
                    "kind": action,
                    "authority": authority,
                    "scope": item.get("scope", ""),
                    "path": item.get("path", ""),
                    "destination": item.get("destination", ""),
                    "policy_rule": item.get("policy_rule", ""),
                    "files": item.get("files", "0"),
                }
            )
        highest = "none"
        if any(item.get("authority") == "delete" for item in planned):
            highest = "delete"
        elif planned:
            highest = "write"
        return {"planned": planned, "applied": [], "highest_authority_used": highest}

    def _parse_repo_finding(self, line: str) -> dict[str, Any]:
        parts = [part.strip() for part in line.split("|")]
        result: dict[str, Any] = {"kind": "repo_finding", "raw": line}
        if len(parts) >= 6:
            result.update(
                {
                    "code": parts[0],
                    "subject": parts[1],
                    "label": parts[2],
                    "verification": parts[3].replace("verification=", "", 1),
                    "detail": parts[4].replace("detail=", "", 1),
                    "note": parts[5].replace("note=", "", 1),
                }
            )
        return result

    def _parse_tier_specific(self, lines: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        data: dict[str, Any] = {}
        findings: list[dict[str, Any]] = []
        for line in lines:
            bullet = line[2:] if line.startswith("- ") else line
            if bullet.startswith(("stale_ref=", "open_pr=", "zone=", "network_probe_failure=")):
                findings.append(self._parse_field_series(bullet.split("=", 1)[0], bullet))
                continue
            if "=" in bullet:
                key, value = bullet.split("=", 1)
                data[key.strip()] = value.strip()
            else:
                data.setdefault("_lines", []).append(bullet)
        return data, findings

    def _parse_field_series(self, kind: str, bullet: str) -> dict[str, Any]:
        result: dict[str, Any] = {"kind": kind, "raw": bullet}
        try:
            tokens = shlex.split(bullet)
        except ValueError:
            tokens = bullet.split()
        for token in tokens:
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            result[key] = value
        return result


def main() -> int:
    request = json.loads(os.fdopen(0, "r", encoding="utf-8").read() or "{}")
    payload = BitPodAuditAdapter().run(request)
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
