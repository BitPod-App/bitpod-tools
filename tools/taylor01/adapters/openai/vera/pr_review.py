#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CURRENT = Path(__file__).resolve()
for parent in CURRENT.parents:
    if (parent / 'AGENTS.md').exists() and (parent / 'tools' / 'taylor01').exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

from tools.taylor01.core.agents.vera.contract import (
    PortableReviewResult,
    PortableReviewTarget,
    build_manifest,
    build_system_prompt,
    render_verification_report,
    utc_now_iso,
)

DEFAULT_MODEL = 'gpt-5.4'
MAX_DIFF_CHARS = 18000
MAX_FILE_CHARS = 12000


@dataclass(frozen=True)
class PRRef:
    owner: str
    repo: str
    number: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run Vera against a GitHub PR URL via the OpenAI Agents SDK.')
    parser.add_argument('pr_url', help='GitHub PR URL to review')
    parser.add_argument('--output-dir', required=True, help='Directory for verification_report.md + manifest.json')
    parser.add_argument('--model', default=DEFAULT_MODEL, help=f'Agent model (default: {DEFAULT_MODEL})')
    return parser.parse_args()


def parse_pr_url(pr_url: str) -> PRRef:
    match = re.match(r'^https://github\.com/([^/]+)/([^/]+)/pull/(\d+)(?:/.*)?$', pr_url.strip())
    if not match:
        raise ValueError(f'Unsupported PR URL: {pr_url}')
    return PRRef(owner=match.group(1), repo=match.group(2), number=int(match.group(3)))


def run_json(cmd: list[str]) -> dict[str, Any] | list[Any]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f'exit {proc.returncode}'
        raise RuntimeError(f"Command failed: {' '.join(cmd)} :: {detail}")
    return json.loads(proc.stdout)


def run_text(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f'exit {proc.returncode}'
        raise RuntimeError(f"Command failed: {' '.join(cmd)} :: {detail}")
    return proc.stdout


def _workspace_root() -> Path:
    env_root = os.environ.get('BITPOD_WORKSPACE_ROOT')
    if env_root:
        return Path(env_root).expanduser().resolve()
    for parent in CURRENT.parents:
        if (parent / 'bitpod-tools').exists():
            return parent
    raise RuntimeError('Could not locate BitPod workspace root; set BITPOD_WORKSPACE_ROOT')


def load_reference_materials() -> str:
    workspace_root = _workspace_root()
    pieces: list[str] = []
    donor_zip = Path(os.environ.get('VERA_REFERENCE_PACK_ZIP', workspace_root / 'local-workspace' / 'local-working-files' / 'vera_pack_v1.zip')).expanduser()
    if donor_zip.exists():
        with zipfile.ZipFile(donor_zip) as zf:
            for name in ('VERA_PERSONA_PROFILE_v1.md', 'QA_CHECKLIST_TEMPLATE_v2.md'):
                if name in zf.namelist():
                    pieces.append(f'[{name}]\n' + zf.read(name).decode('utf-8', 'replace')[:5000])
    for path in (
        workspace_root / 'bitpod-tools' / 'linear' / 'docs' / 'process' / 'vera_qa_lane_contract_v1.md',
        workspace_root / 'bitpod-tools' / 'linear' / 'docs' / 'process' / 'vera_runtime_minimum_v1.md',
        workspace_root / '.codex' / 'skills' / 'qa-specialist' / 'SKILL.md',
    ):
        if path.exists():
            pieces.append(f'[{path.name}]\n' + path.read_text(encoding='utf-8', errors='replace')[:6000])
    return '\n\n'.join(pieces)


def build_instructions() -> str:
    return build_system_prompt(
        additional_sections=[
            '## OpenAI-native adapter stance\n- Adapter: OpenAI Agents SDK PR reviewer\n- Primary input: GitHub PR URL\n- Infer scope from the PR unless doing so would be dishonest.\n- Return structured QA output only.\n- Preserve Vera\'s exact verdict tokens and canonical artifact names.',
            f'## Reference materials\n{load_reference_materials()}',
        ]
    )


def _load_agents_sdk() -> tuple[Any, Any, Any, Any, Any, Any]:
    try:
        from pydantic import BaseModel, Field
        from agents import Agent, ModelSettings, Runner, function_tool
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            'OpenAI Agents SDK is required. Set OPENAI_AGENTS_EXTRA_PATH or install openai-agents for python3.11.'
        ) from exc
    return BaseModel, Field, Agent, ModelSettings, Runner, function_tool


def build_agent(model: str):
    BaseModel, Field, Agent, ModelSettings, Runner, function_tool = _load_agents_sdk()

    class PRReviewResultModel(BaseModel):
        overall_verdict: str = Field(description='Final QA verdict for the PR review.')
        summary: str = Field(description='Short truthful summary for the operator.')
        review_scope: list[str] = Field(description='What Vera treated as the effective QA scope.')
        evidence: list[str] = Field(description='Concrete evidence bullets supporting the verdict.')
        blocking_findings: list[str] = Field(description='Blocking findings or reasons for failure/no verdict.')
        residual_risks: list[str] = Field(description='Residual risks that remain if verdict is PASSED.')
        next_action: str = Field(description='Smallest truthful next action.')
        concise_pr_receipt: str = Field(description='Short PR-facing receipt summary.')

    @function_tool
    def get_pull_request_overview(pr_url: str) -> str:
        """Fetch PR metadata, body, files, and commit headlines for a GitHub PR URL."""
        ref = parse_pr_url(pr_url)
        data = run_json([
            'gh', 'pr', 'view', str(ref.number), '--repo', f'{ref.owner}/{ref.repo}',
            '--json', 'number,title,body,headRefName,baseRefName,state,files,commits,author',
        ])
        return json.dumps(data, ensure_ascii=False, indent=2)

    @function_tool
    def get_pull_request_diff(pr_url: str) -> str:
        """Fetch the unified diff for a GitHub PR URL."""
        ref = parse_pr_url(pr_url)
        diff = run_text(['gh', 'pr', 'diff', str(ref.number), '--repo', f'{ref.owner}/{ref.repo}', '--patch'])
        return diff[:MAX_DIFF_CHARS]

    @function_tool
    def get_pull_request_file_content(pr_url: str, path: str) -> str:
        """Fetch the head-branch content of a changed file in a GitHub PR."""
        ref = parse_pr_url(pr_url)
        pr = run_json(['gh', 'pr', 'view', str(ref.number), '--repo', f'{ref.owner}/{ref.repo}', '--json', 'headRefName'])
        head_ref = pr['headRefName']
        api_path = f'repos/{ref.owner}/{ref.repo}/contents/{path}?ref={head_ref}'
        data = run_json(['gh', 'api', api_path])
        if not isinstance(data, dict) or 'content' not in data:
            raise RuntimeError(f'Could not fetch file contents for {path}')
        content = base64.b64decode(data['content']).decode('utf-8', 'replace')
        return content[:MAX_FILE_CHARS]

    agent = Agent(
        name='Vera',
        instructions=build_instructions(),
        model=model,
        tools=[get_pull_request_overview, get_pull_request_diff, get_pull_request_file_content],
        output_type=PRReviewResultModel,
        model_settings=ModelSettings(),
    )
    return agent, Runner


def convert_result(pr_url: str, raw_result: Any, model: str) -> tuple[PortableReviewTarget, PortableReviewResult]:
    ref = parse_pr_url(pr_url)
    verdict = str(getattr(raw_result, 'overall_verdict', 'NO_VERDICT')).upper()
    blocking_findings = list(getattr(raw_result, 'blocking_findings', []) or [])
    residual_risks = list(getattr(raw_result, 'residual_risks', []) or [])
    findings = blocking_findings or residual_risks or [getattr(raw_result, 'summary', 'No summary provided.')]
    open_questions = []
    if verdict == 'NO_VERDICT':
        open_questions.append('Additional evidence is required before a truthful verdict is possible.')
    target = PortableReviewTarget(
        target_type='pr',
        target_ref=pr_url,
        repository=f'{ref.owner}/{ref.repo}',
        branch='',
    )
    result = PortableReviewResult(
        verdict=verdict,
        scope=[
            f'PR: {pr_url}',
            'Runtime: OpenAI Agents SDK',
            f'Model: {model}',
            *list(getattr(raw_result, 'review_scope', []) or []),
        ],
        evidence=list(getattr(raw_result, 'evidence', []) or []),
        checks_run=[
            'PR metadata inspection',
            'Diff inspection',
            'Changed-file content inspection as needed',
        ],
        findings=findings,
        open_questions=open_questions,
        recommendation=str(getattr(raw_result, 'next_action', '') or 'No next action provided.'),
        notes=[
            str(getattr(raw_result, 'summary', '') or '').strip(),
            str(getattr(raw_result, 'concise_pr_receipt', '') or '').strip(),
            f'Generated at {utc_now_iso()}',
        ],
    )
    return target, result


def write_outputs(output_dir: Path, target: PortableReviewTarget, result: PortableReviewResult) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'verification_report.md'
    manifest_path = output_dir / 'manifest.json'
    report_path.write_text(render_verification_report(result), encoding='utf-8')
    manifest_path.write_text(json.dumps(build_manifest(target, result), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return report_path, manifest_path


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    pr_url = args.pr_url.strip()
    agent, Runner = build_agent(args.model)
    prompt = (
        f'Review GitHub PR {pr_url}.\n'
        'Use the PR itself as the primary input. Infer the effective QA scope from the PR unless there is a real blocker.\n'
        'For self-contained docs/script PRs, do not demand an over-structured handoff packet.\n'
        'Return a truthful QA verdict using PASSED, FAILED, or NO_VERDICT only.'
    )
    try:
        run_result = Runner.run_sync(agent, prompt)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1
    target, result = convert_result(pr_url, run_result.final_output, args.model)
    report_path, manifest_path = write_outputs(output_dir, target, result)
    print(json.dumps({'qa_result': result.verdict, 'verification_report': str(report_path), 'manifest': str(manifest_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
