#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent
TOOLS_ROOT = ROOT.parent
DEFAULT_CONTRACT = Path.home() / ".agents" / "skills" / "taylor" / "SKILL.md"
DEFAULT_ARTIFACT_ROOT = TOOLS_ROOT.parent / "artifacts"


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_bytes(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_tools_commit() -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(TOOLS_ROOT), "rev-parse", "--short", "HEAD"], text=True)
        return out.strip()
    except Exception:
        return "unknown"


def bridge_available() -> bool:
    return (TOOLS_ROOT / "gpt_bridge" / "bridge_chat.sh").exists()


def contract_refs(contract_path: Path) -> list[tuple[str, str]]:
    refs_dir = contract_path.parent / "references"
    if not refs_dir.exists():
        return []
    out: list[tuple[str, str]] = []
    for p in sorted(refs_dir.glob("*.md")):
        try:
            out.append((p.name, sha256_bytes(p)))
        except Exception:
            out.append((p.name, "unreadable"))
    return out


@dataclass
class QAResult:
    result: str
    defects: list[str]
    required_changes: list[str]
    checklist: list[tuple[str, bool]]
    risks: list[str]


def run_local_qa(bundle_path: Path) -> QAResult:
    defects: list[str] = []
    required_changes: list[str] = []
    risks: list[str] = []

    if not bundle_path.exists():
        return QAResult(
            result="FAIL",
            defects=[f"Bundle file not found: {bundle_path}"],
            required_changes=["Provide a valid --bundle-path."],
            checklist=[],
            risks=["No review possible without bundle."],
        )

    text = bundle_path.read_text(encoding="utf-8", errors="replace")
    required_sections = [
        "## A) Context",
        "## B) git diff --stat",
        "## C) full git diff",
        "## D) verification outputs",
        "## E) decisions needed",
    ]
    section_ok = all(s in text for s in required_sections)
    if not section_ok:
        defects.append("Bundle missing one or more required A-E sections.")
        required_changes.append("Regenerate bundle via scripts/make_review_bundle.sh.")

    has_diff = "diff --git" in text
    if not has_diff:
        defects.append("Bundle contains no full diff payload.")
        required_changes.append("Ensure full diff section includes `git diff base...HEAD` output.")

    has_verify = "verification" in text.lower()
    if not has_verify:
        risks.append("Verification output section may be empty or omitted.")

    result = "PASS"
    if defects:
        result = "FAIL"
    elif risks:
        result = "DEGRADED"

    checklist = [
        ("Bundle has required section order A-E", section_ok),
        ("Bundle includes full git diff payload", has_diff),
        ("Bundle includes verification output section", has_verify),
    ]

    if not risks:
        risks.append("No material determinism/drift risks identified from static bundle scan.")

    return QAResult(
        result=result,
        defects=defects,
        required_changes=required_changes,
        checklist=checklist,
        risks=risks,
    )


def write_local_qa_artifacts(
    out_dir: Path,
    qa: QAResult,
    *,
    commit_sha: str,
    bundle_path: Path,
    bundle_sha256: str,
    contract_path: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    qa_review = [
        "# Taylor Local QA Review",
        "",
        f"- Result: `{qa.result}`",
        f"- Commit SHA: `{commit_sha}`",
        f"- Bundle Path: `{bundle_path}`",
        f"- Bundle SHA256: `{bundle_sha256}`",
        f"- Contract Path: `{contract_path}`",
        "",
        "## Defects",
    ]
    if qa.defects:
        qa_review.extend([f"- {d}" for d in qa.defects])
    else:
        qa_review.append("- None.")
    qa_review.append("")
    qa_review.append("## Required Changes")
    if qa.required_changes:
        qa_review.extend([f"- {d}" for d in qa.required_changes])
    else:
        qa_review.append("- None.")
    (out_dir / "qa_review.md").write_text("\n".join(qa_review) + "\n", encoding="utf-8")

    checklist = ["# Acceptance Criteria Checklist", ""]
    for label, ok in qa.checklist:
        checklist.append(f"- [{'x' if ok else ' '}] {label}")
    (out_dir / "acceptance_criteria_checklist.md").write_text("\n".join(checklist) + "\n", encoding="utf-8")

    risk_notes = ["# Risk Notes", ""] + [f"- {r}" for r in qa.risks]
    (out_dir / "risk_notes.md").write_text("\n".join(risk_notes) + "\n", encoding="utf-8")

    manifest = {
        "commit_sha": commit_sha,
        "bundle_path": str(bundle_path),
        "bundle_sha256": bundle_sha256,
        "contract_path": str(contract_path),
        "mode": "LOCAL",
        "footer_compliant": False,
        "footer_synthetic": False,
        "timestamp": utc_ts(),
        "result": qa.result,
    }
    (out_dir / "qa_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def cmd_whoami(args: argparse.Namespace) -> int:
    contract = Path(args.contract).expanduser()
    refs = contract_refs(contract)
    print(f"Taylor version: {VERSION}")
    print(f"Contract path: {contract}")
    print("Loaded references:")
    if refs:
        for name, digest in refs:
            print(f"- {name} sha256={digest}")
    else:
        print("- none")
    print("Runtime mode availability:")
    print("- LOCAL: available")
    print(f"- BRIDGE: {'available' if bridge_available() else 'unavailable'}")
    print(f"Tools commit: {git_tools_commit()}")
    return 0


def cmd_qa(args: argparse.Namespace) -> int:
    bundle = Path(args.bundle_path).expanduser()
    if not bundle.is_absolute():
        bundle = (Path.cwd() / bundle).resolve()
    out_dir = Path(args.out).expanduser()
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()
    contract = Path(args.contract).expanduser()

    qa = run_local_qa(bundle)
    bundle_sha = sha256_bytes(bundle) if bundle.exists() else "missing"
    commit = git_tools_commit()
    write_local_qa_artifacts(
        out_dir,
        qa,
        commit_sha=commit,
        bundle_path=bundle,
        bundle_sha256=bundle_sha,
        contract_path=contract,
    )
    print(f"Taylor QA result: {qa.result}")
    print(f"QA output path: {out_dir}")
    return 0 if qa.result == "PASS" else 1


def _respond(question: str, contexts: list[Path], contract: Path) -> str:
    ctx_lines = [f"- {p}" for p in contexts] if contexts else ["- none"]
    return (
        "Taylor response\n"
        f"Contract: {contract}\n"
        f"Question: {question.strip()}\n"
        "Context files:\n"
        + "\n".join(ctx_lines)
        + "\n"
    )


def _save_chat_artifact(root: Path, mode: str, content: str) -> Path:
    run_dir = root / "taylor_chat" / utc_ts()
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "conversation.md").write_text(content, encoding="utf-8")
    manifest = {"mode": mode, "timestamp": utc_ts(), "path": str(run_dir / "conversation.md")}
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return run_dir


def cmd_ask(args: argparse.Namespace) -> int:
    contract = Path(args.contract).expanduser()
    contexts = [Path(p).expanduser().resolve() for p in args.context]
    text = _respond(args.question, contexts, contract)
    print(text.rstrip())
    if args.save:
        out_root = Path(args.artifact_root).expanduser()
        if not out_root.is_absolute():
            out_root = (Path.cwd() / out_root).resolve()
        run_dir = _save_chat_artifact(out_root, "ASK", text)
        print(f"Artifact path: {run_dir}")
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    contract = Path(args.contract).expanduser()
    out_lines = [f"Taylor chat started (contract={contract})", "Type /exit to quit."]
    print(out_lines[0])
    print(out_lines[1])
    while True:
        try:
            line = input("you> ").strip()
        except EOFError:
            break
        if line in {"/exit", "/quit"}:
            break
        if not line:
            continue
        response = _respond(line, [], contract).strip()
        print(f"taylor> {response}")
        out_lines.append(f"you: {line}")
        out_lines.append(f"taylor: {response}")
    if args.save:
        out_root = Path(args.artifact_root).expanduser()
        if not out_root.is_absolute():
            out_root = (Path.cwd() / out_root).resolve()
        run_dir = _save_chat_artifact(out_root, "CHAT", "\n".join(out_lines) + "\n")
        print(f"Artifact path: {run_dir}")
    return 0


def cmd_self_test(args: argparse.Namespace) -> int:
    contract = Path(args.contract).expanduser()
    if not contract.exists():
        print(f"FAIL: missing contract: {contract}")
        return 1

    out_root = Path(args.out_root).expanduser()
    if not out_root.is_absolute():
        out_root = (Path.cwd() / out_root).resolve()
    run_dir = out_root / "self_test" / utc_ts()
    run_dir.mkdir(parents=True, exist_ok=True)

    sample_bundle = run_dir / "sample_bundle.md"
    sample_bundle.write_text(
        """# Review Bundle\n\n## A) Context\n- Repo: sample\n\n## B) git diff --stat (`base...HEAD`)\n```text\n 1 file changed\n```\n\n## C) full git diff (`base...HEAD`)\n```diff\ndiff --git a/a b/a\n+ok\n```\n\n## D) verification outputs\n```text\nsmoke pass\n```\n\n## E) decisions needed\n- None.\n""",
        encoding="utf-8",
    )

    qa = run_local_qa(sample_bundle)
    write_local_qa_artifacts(
        run_dir,
        qa,
        commit_sha=git_tools_commit(),
        bundle_path=sample_bundle,
        bundle_sha256=sha256_bytes(sample_bundle),
        contract_path=contract,
    )

    print("PASS" if qa.result == "PASS" else qa.result)
    print(f"Artifacts: {run_dir}")
    return 0 if qa.result == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Taylor local runtime")
    sub = p.add_subparsers(dest="cmd", required=True)

    who = sub.add_parser("whoami", help="Show Taylor runtime identity and loaded contract references")
    who.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    who.set_defaults(fn=cmd_whoami)

    qa = sub.add_parser("qa", help="Run deterministic local QA against a review bundle")
    qa.add_argument("--bundle-path", required=True)
    qa.add_argument("--out", required=True)
    qa.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    qa.set_defaults(fn=cmd_qa)

    ask = sub.add_parser("ask", help="Ask Taylor a single question")
    ask.add_argument("question")
    ask.add_argument("--context", action="append", default=[])
    ask.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    ask.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    ask.add_argument("--save", action=argparse.BooleanOptionalAction, default=True)
    ask.set_defaults(fn=cmd_ask)

    chat = sub.add_parser("chat", help="Interactive chat with local Taylor runtime")
    chat.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    chat.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    chat.add_argument("--save", action=argparse.BooleanOptionalAction, default=True)
    chat.set_defaults(fn=cmd_chat)

    st = sub.add_parser("self-test", help="Run deterministic self-test and write artifacts")
    st.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    st.add_argument("--out-root", default="/tmp")
    st.set_defaults(fn=cmd_self_test)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
