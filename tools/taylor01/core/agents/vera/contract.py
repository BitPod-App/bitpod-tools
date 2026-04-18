from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

VERA_NAME = "Vera"
VERA_ROLE = "QA Agent"
VERA_VERDICTS = ("PASSED", "FAILED", "NO_VERDICT")
VERA_ARTIFACTS = ("verification_report.md", "manifest.json")
PORTABLE_DOCS = ("AGENTS.md", "IDENTITY.md", "SOUL.md", "OUTPUT_CONTRACT.md", "SECRETS.md")


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists() and (parent / "tools" / "taylor01").exists():
            return parent
    raise RuntimeError("Could not locate repo root for Vera portable core")


REPO_ROOT = _find_repo_root()
PORTABLE_HOME = Path(__file__).resolve().parent


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_verdict(value: str | None) -> str:
    verdict = (value or "").strip().upper()
    if verdict not in VERA_VERDICTS:
        return "NO_VERDICT"
    return verdict


def load_portable_documents() -> dict[str, str]:
    return {
        name: (PORTABLE_HOME / name).read_text(encoding="utf-8", errors="replace").strip()
        for name in PORTABLE_DOCS
    }


def build_system_prompt(*, additional_sections: Iterable[str] = ()) -> str:
    docs = load_portable_documents()
    sections = [docs[name] for name in PORTABLE_DOCS]
    for section in additional_sections:
        cleaned = section.strip()
        if cleaned:
            sections.append(cleaned)
    return "\n\n".join(sections).strip()


@dataclass(frozen=True)
class PortableReviewTarget:
    target_type: str
    target_ref: str
    repository: str = ""
    branch: str = ""


@dataclass(frozen=True)
class PortableReviewResult:
    verdict: str
    scope: Sequence[str]
    evidence: Sequence[str]
    checks_run: Sequence[str]
    findings: Sequence[str]
    open_questions: Sequence[str]
    recommendation: str
    notes: Sequence[str] = ()

    def normalized(self) -> "PortableReviewResult":
        return PortableReviewResult(
            verdict=normalize_verdict(self.verdict),
            scope=tuple(_normalize_lines(self.scope)),
            evidence=tuple(_normalize_lines(self.evidence)),
            checks_run=tuple(_normalize_lines(self.checks_run)),
            findings=tuple(_normalize_lines(self.findings)),
            open_questions=tuple(_normalize_lines(self.open_questions)),
            recommendation=_normalize_single_line(self.recommendation) or "No recommendation provided.",
            notes=tuple(_normalize_lines(self.notes)),
        )


def _normalize_single_line(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_lines(values: Sequence[str] | None) -> list[str]:
    lines: list[str] = []
    for value in values or ():
        text = _normalize_single_line(value)
        if text is not None:
            lines.append(text)
    return lines


def _render_section(lines: list[str], title: str, items: Sequence[str], *, fallback: str) -> None:
    lines.append(f"## {title}")
    normalized = _normalize_lines(items)
    if normalized:
        for item in normalized:
            lines.append(f"- {item}")
    else:
        lines.append(f"- {fallback}")
    lines.append("")


def render_verification_report(result: PortableReviewResult) -> str:
    normalized = result.normalized()
    lines: list[str] = ["# verification_report", ""]
    _render_section(lines, "Verdict", [normalized.verdict], fallback="NO_VERDICT")
    _render_section(lines, "Scope", normalized.scope, fallback="Scope not captured.")
    _render_section(lines, "Evidence", normalized.evidence, fallback="No evidence recorded.")
    _render_section(lines, "Checks Run", normalized.checks_run, fallback="No checks were recorded.")
    _render_section(lines, "Findings", normalized.findings, fallback="No findings recorded.")
    _render_section(lines, "Open Questions", normalized.open_questions, fallback="None.")
    _render_section(lines, "Recommendation", [normalized.recommendation], fallback="No recommendation provided.")
    return "\n".join(lines).strip() + "\n"


def build_manifest(target: PortableReviewTarget, result: PortableReviewResult, *, timestamp: str | None = None) -> dict:
    normalized = result.normalized()
    return {
        "schemaVersion": "1.0",
        "agent": {"name": VERA_NAME, "role": VERA_ROLE},
        "review": {
            "targetType": target.target_type,
            "targetRef": target.target_ref,
            "repository": target.repository,
            "branch": target.branch,
            "verdict": normalized.verdict,
            "timestamp": timestamp or utc_now_iso(),
        },
        "evidence": list(normalized.evidence),
        "checks": list(normalized.checks_run),
        "artifacts": {"verificationReport": "verification_report.md"},
        "notes": list(normalized.notes),
        "openQuestions": list(normalized.open_questions),
    }


def write_artifacts(output_dir: Path, result: PortableReviewResult, target: PortableReviewTarget) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "verification_report.md"
    manifest_path = output_dir / "manifest.json"
    report_path.write_text(render_verification_report(result), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(build_manifest(target, result), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report_path, manifest_path
