#!/usr/bin/env python3
"""Thin OpenAI-native Vera QA runtime on top of the GPT Bridge."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
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
)

SCRIPT_DIR = Path(__file__).resolve().parents[5] / 'gpt_bridge'
ASK_ONCE = SCRIPT_DIR / 'ask_once.sh'
DEFAULT_VERA_MODEL = 'gpt-5.2'
DEFAULT_MAX_TOKENS = 2200
MAX_CONTEXT_CHARS_PER_FILE = 6000
MAX_TOTAL_CONTEXT_CHARS = 24000

VERA_SYSTEM_PROMPT = build_system_prompt(
    additional_sections=[
        '## OpenAI bridge adapter stance\n- Adapter: GPT Bridge wrapper for Vera QA handoff review\n- Preserve the portable Vera contract as the source of truth.\n- Return JSON only for the bridge response.\n- Do not drift into generic assistant behavior.',
    ]
)


@dataclass(frozen=True)
class Criterion:
    criterion_id: str
    text: str


@dataclass(frozen=True)
class Handoff:
    source_path: Path
    target: str
    issue_url: str | None
    pr_url: str | None
    system_under_test: str
    critical_acceptance_criteria: tuple[Criterion, ...]
    commands_or_surfaces: tuple[str, ...]
    known_risks: tuple[str, ...]
    environment: dict[str, Any]
    notes: str | None
    changed_files: tuple[str, ...]
    evidence_paths: tuple[Path, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run Vera QA via the local GPT Bridge and write verification_report.md + manifest.json'
    )
    parser.add_argument('handoff_file', help='Path to QA handoff JSON')
    parser.add_argument('--output-dir', required=True, help='Directory where artifacts will be written')
    parser.add_argument('--model', default=DEFAULT_VERA_MODEL, help=f'Bridge model override (default: {DEFAULT_VERA_MODEL})')
    parser.add_argument('--max-tokens', type=int, default=DEFAULT_MAX_TOKENS, help=f'max_output_tokens hint (default: {DEFAULT_MAX_TOKENS})')
    parser.add_argument('--evidence-file', action='append', default=[], help='Additional evidence/context file path; can be repeated')
    parser.add_argument('--print-report', action=argparse.BooleanOptionalAction, default=False, help='Print verification_report.md after writing it')
    return parser.parse_args()


def _as_non_empty_string(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            return stripped
    return None


def _normalize_string_list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError('Expected a JSON array of strings')
    items: list[str] = []
    for item in value:
        text = _as_non_empty_string(item)
        if text is None:
            raise ValueError('Expected a JSON array of strings')
        items.append(text)
    return tuple(items)


def _normalize_criteria(value: Any) -> tuple[Criterion, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError('critical_acceptance_criteria must be a non-empty array')
    criteria: list[Criterion] = []
    for idx, item in enumerate(value, start=1):
        if isinstance(item, str):
            text = _as_non_empty_string(item)
            if text is None:
                raise ValueError('critical_acceptance_criteria strings must be non-empty')
            criteria.append(Criterion(criterion_id=f'AC-{idx}', text=text))
            continue
        if isinstance(item, dict):
            text = _as_non_empty_string(item.get('text') or item.get('criterion'))
            if text is None:
                raise ValueError('Each critical_acceptance_criteria item needs text')
            criterion_id = _as_non_empty_string(item.get('id')) or f'AC-{idx}'
            criteria.append(Criterion(criterion_id=criterion_id, text=text))
            continue
        raise ValueError('critical_acceptance_criteria must contain strings or objects')
    return tuple(criteria)


def load_handoff(path: Path, extra_evidence_paths: list[str]) -> Handoff:
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise ValueError(f'Handoff file not found: {path}') from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f'Invalid handoff JSON: {exc}') from exc
    if not isinstance(raw, dict):
        raise ValueError('Handoff file must decode to a JSON object')

    issue_url = _as_non_empty_string(raw.get('issue_url'))
    pr_url = _as_non_empty_string(raw.get('pr_url'))
    system_under_test = _as_non_empty_string(raw.get('system_under_test')) or ''
    target = _as_non_empty_string(raw.get('target')) or issue_url or pr_url or system_under_test
    if target is None:
        raise ValueError('Handoff must include target, issue_url, pr_url, or system_under_test')
    if not system_under_test:
        system_under_test = target

    criteria = _normalize_criteria(raw.get('critical_acceptance_criteria'))
    commands_or_surfaces = _normalize_string_list(raw.get('commands_or_surfaces') or raw.get('verification_surfaces') or [])
    known_risks = _normalize_string_list(raw.get('known_risks') or [])
    changed_files = _normalize_string_list(raw.get('changed_files') or [])
    notes = _as_non_empty_string(raw.get('notes'))
    environment = raw.get('environment') or {}
    if not isinstance(environment, dict):
        raise ValueError('environment must be an object when present')

    evidence_paths: list[Path] = []
    for raw_path in list(raw.get('evidence_paths') or []) + list(extra_evidence_paths):
        text_path = _as_non_empty_string(raw_path)
        if text_path is None:
            raise ValueError('evidence_paths must contain strings')
        candidate = Path(text_path)
        if not candidate.is_absolute():
            candidate = (path.parent / candidate).resolve()
        if not candidate.exists():
            raise ValueError(f'Evidence file not found: {candidate}')
        evidence_paths.append(candidate)

    return Handoff(
        source_path=path.resolve(),
        target=target,
        issue_url=issue_url,
        pr_url=pr_url,
        system_under_test=system_under_test,
        critical_acceptance_criteria=criteria,
        commands_or_surfaces=commands_or_surfaces,
        known_risks=known_risks,
        environment=environment,
        notes=notes,
        changed_files=changed_files,
        evidence_paths=tuple(evidence_paths),
    )


def detect_review_risk(changed_files: tuple[str, ...]) -> dict[str, Any]:
    if not changed_files:
        return {'high_risk': False, 'patterns_matched': [], 'files_matched': [], 'evidence_source': 'none'}
    pattern_groups = {
        'auth_permissions': ('auth', 'permission', 'rbac', 'acl', 'role', 'oauth'),
        'secrets_credentials': ('secret', 'token', 'credential', 'key', '.env'),
        'billing_payments': ('billing', 'payment', 'checkout', 'stripe', 'invoice'),
        'data_schema': ('migration', 'schema', 'database', 'alembic', 'prisma', 'sql'),
        'deploy_infra': ('deploy', 'infra', 'terraform', 'docker', 'k8s', 'helm', '.github/workflows'),
    }
    patterns_matched: set[str] = set()
    files_matched: set[str] = set()
    for file_path in changed_files:
        lowered = file_path.lower()
        for label, needles in pattern_groups.items():
            if any(needle in lowered for needle in needles):
                patterns_matched.add(label)
                files_matched.add(file_path)
    return {
        'high_risk': bool(files_matched),
        'patterns_matched': sorted(patterns_matched),
        'files_matched': sorted(files_matched),
        'evidence_source': 'handoff.changed_files',
    }


def build_context_text(handoff: Handoff) -> str | None:
    if not handoff.evidence_paths:
        return None
    blocks: list[str] = []
    total_chars = 0
    for path in handoff.evidence_paths:
        text = path.read_text(encoding='utf-8', errors='replace')
        excerpt = text[:MAX_CONTEXT_CHARS_PER_FILE]
        remaining = MAX_TOTAL_CONTEXT_CHARS - total_chars
        if remaining <= 0:
            break
        if len(excerpt) > remaining:
            excerpt = excerpt[:remaining]
        blocks.append(f'[Evidence: {path}]\n{excerpt}')
        total_chars += len(excerpt)
    return '\n\n'.join(blocks) if blocks else None


def build_vera_message(handoff: Handoff, review_risk: dict[str, Any]) -> str:
    packet = {
        'target': handoff.target,
        'issue_url': handoff.issue_url,
        'pr_url': handoff.pr_url,
        'system_under_test': handoff.system_under_test,
        'critical_acceptance_criteria': [{'id': item.criterion_id, 'text': item.text} for item in handoff.critical_acceptance_criteria],
        'commands_or_surfaces': list(handoff.commands_or_surfaces),
        'known_risks': list(handoff.known_risks),
        'environment': handoff.environment,
        'notes': handoff.notes,
        'review_risk': review_risk,
    }
    required_schema = {
        'overall_verdict': 'PASSED | FAILED | NO_VERDICT',
        'summary': 'string',
        'criteria_results': [
            {
                'id': 'AC-1',
                'result': 'PASS | FAIL | NO_VERDICT',
                'steps': ['string'],
                'observed': 'string',
                'expected': 'string or null',
                'actual': 'string or null',
                'environment': 'string or null',
                'references': ['string'],
                'notes': 'string or null',
            }
        ],
        'failed_because': 'string or null',
        'no_verdict_reason': 'string or null',
        'next_action': 'string',
        'residual_risks': ['string'],
        'low_risk_fix_hints': ['string'],
    }
    return (
        'Review this QA handoff packet and return JSON only.\n\n'
        'Rules:\n'
        '- Decide QA verdict only.\n'
        '- Do not change scope or priority.\n'
        '- Every critical acceptance criterion needs PASS, FAIL, or NO_VERDICT.\n'
        '- If evidence is missing or weak, fail closed with overall_verdict=NO_VERDICT.\n'
        '- Optional low-risk fix hints are allowed only if obvious and low-risk, max 3.\n\n'
        f'QA handoff packet:\n{json.dumps(packet, ensure_ascii=False, indent=2)}\n\n'
        f'Required JSON schema:\n{json.dumps(required_schema, ensure_ascii=False, indent=2)}'
    )


def run_bridge_review(*, handoff: Handoff, review_risk: dict[str, Any], model: str, max_tokens: int, context_text: str | None) -> dict[str, Any]:
    cmd = [
        str(ASK_ONCE),
        build_vera_message(handoff, review_risk),
        '--task-type', 'qa_check',
        '--max-tokens', str(max_tokens),
        '--json-only',
        '--model', model,
        '--meta', json.dumps({'route_actor': 'vera', 'workflow': 'vera_qa_v1', 'system_prompt': VERA_SYSTEM_PROMPT}, ensure_ascii=True),
    ]
    if context_text is not None:
        cmd.append('--context-stdin')
    proc = subprocess.run(cmd, cwd=str(SCRIPT_DIR), input=context_text, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f'exit code {proc.returncode}'
        raise RuntimeError(f'Bridge request failed: {detail}')
    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'Bridge returned invalid JSON: {exc}') from exc
    if not isinstance(response, dict):
        raise RuntimeError('Bridge response must be a JSON object')
    return response


def _normalize_string_sequence(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = _as_non_empty_string(item)
        if text is not None:
            out.append(text)
    return out


def normalize_model_result(raw_answer: Any, handoff: Handoff) -> dict[str, Any]:
    if not isinstance(raw_answer, dict):
        raw_answer = {}
    raw_criteria = raw_answer.get('criteria_results')
    criteria_by_id: dict[str, dict[str, Any]] = {}
    criteria_by_order: list[dict[str, Any]] = []
    if isinstance(raw_criteria, list):
        for item in raw_criteria:
            if not isinstance(item, dict):
                continue
            criteria_by_order.append(item)
            item_id = _as_non_empty_string(item.get('id'))
            if item_id is not None and item_id not in criteria_by_id:
                criteria_by_id[item_id] = item
    normalized_items: list[dict[str, Any]] = []
    any_fail = False
    any_no_verdict = False
    for idx, criterion in enumerate(handoff.critical_acceptance_criteria):
        item = criteria_by_id.get(criterion.criterion_id)
        if item is None and idx < len(criteria_by_order):
            item = criteria_by_order[idx]
        item = item or {}
        result = _as_non_empty_string(item.get('result')) or 'NO_VERDICT'
        result = result.upper()
        if result in {'PASSED', 'PASS'}:
            normalized_result = 'PASS'
        elif result in {'FAILED', 'FAIL'}:
            normalized_result = 'FAIL'
        else:
            normalized_result = 'NO_VERDICT'
        if normalized_result == 'FAIL':
            any_fail = True
        elif normalized_result == 'NO_VERDICT':
            any_no_verdict = True
        normalized_items.append(
            {
                'id': criterion.criterion_id,
                'criterion': criterion.text,
                'result': normalized_result,
                'steps': _normalize_string_sequence(item.get('steps')),
                'observed': _as_non_empty_string(item.get('observed')),
                'expected': _as_non_empty_string(item.get('expected')),
                'actual': _as_non_empty_string(item.get('actual')),
                'environment': _as_non_empty_string(item.get('environment')),
                'references': _normalize_string_sequence(item.get('references')),
                'notes': _as_non_empty_string(item.get('notes')),
            }
        )
    if any_fail:
        overall_verdict = 'FAILED'
    elif any_no_verdict:
        overall_verdict = 'NO_VERDICT'
    else:
        overall_verdict = 'PASSED'
    summary = _as_non_empty_string(raw_answer.get('summary')) or 'Vera completed the QA review.'
    failed_because = _as_non_empty_string(raw_answer.get('failed_because'))
    no_verdict_reason = _as_non_empty_string(raw_answer.get('no_verdict_reason'))
    next_action = _as_non_empty_string(raw_answer.get('next_action'))
    if overall_verdict == 'FAILED' and next_action is None:
        next_action = 'Fix the failing critical acceptance criteria and rerun Vera QA.'
    if overall_verdict == 'NO_VERDICT' and next_action is None:
        next_action = 'Provide the missing QA context or stronger verification evidence, then rerun Vera QA.'
    if overall_verdict == 'PASSED' and next_action is None:
        next_action = 'Proceed with the normal closeout or review flow.'
    if overall_verdict == 'NO_VERDICT' and no_verdict_reason is None:
        no_verdict_reason = 'model_output_incomplete_or_context_insufficient'
    return {
        'overall_verdict': overall_verdict,
        'summary': summary,
        'criteria_results': normalized_items,
        'failed_because': failed_because,
        'no_verdict_reason': no_verdict_reason,
        'next_action': next_action,
        'residual_risks': _normalize_string_sequence(raw_answer.get('residual_risks')),
        'low_risk_fix_hints': _normalize_string_sequence(raw_answer.get('low_risk_fix_hints'))[:3],
    }


def _criterion_evidence_line(item: dict[str, Any]) -> str:
    refs = item['references']
    ref_suffix = f" [refs: {', '.join(refs)}]" if refs else ''
    if item['result'] == 'PASS':
        observed = item['observed'] or 'pass evidence recorded'
        return f"{item['id']} PASS: {observed}{ref_suffix}"
    if item['result'] == 'FAIL':
        actual = item['actual'] or 'failure observed'
        expected = item['expected'] or 'expected result not provided'
        return f"{item['id']} FAIL: expected {expected}; actual {actual}{ref_suffix}"
    reason = item['notes'] or item['observed'] or 'insufficient evidence'
    return f"{item['id']} NO_VERDICT: {reason}{ref_suffix}"


def convert_to_portable(handoff: Handoff, result: dict[str, Any], review_risk: dict[str, Any], model: str) -> tuple[PortableReviewTarget, PortableReviewResult]:
    target_ref = handoff.pr_url or handoff.issue_url or handoff.target
    target_type = 'pr' if handoff.pr_url else ('issue' if handoff.issue_url else 'slice')
    scope = [
        f'System under test: {handoff.system_under_test}',
        f'Handoff source: {handoff.source_path}',
        f'Runtime: OpenAI Responses via GPT Bridge',
        f'Model: {model}',
    ]
    if handoff.pr_url:
        scope.append(f'PR: {handoff.pr_url}')
    if handoff.issue_url:
        scope.append(f'Issue: {handoff.issue_url}')
    if review_risk['high_risk']:
        scope.append(f"High-risk review: true ({', '.join(review_risk['patterns_matched'])})")
    evidence = [_criterion_evidence_line(item) for item in result['criteria_results']]
    checks_run = ['QA handoff review', *handoff.commands_or_surfaces]
    findings: list[str] = []
    if result['overall_verdict'] == 'FAILED':
        findings.append(result['failed_because'] or 'At least one critical acceptance criterion failed.')
    elif result['overall_verdict'] == 'NO_VERDICT':
        findings.append(result['no_verdict_reason'] or 'Vera could not safely issue a verdict.')
    findings.extend(result['residual_risks'])
    findings.extend(result['low_risk_fix_hints'])
    if not findings:
        findings.append(result['summary'])
    open_questions = []
    if result['overall_verdict'] == 'NO_VERDICT':
        open_questions.append(result['no_verdict_reason'] or 'Additional evidence is required before a truthful verdict is possible.')
    notes = [
        result['summary'],
        f'Next action: {result["next_action"]}',
        f"High-risk review: {'true' if review_risk['high_risk'] else 'false'}",
    ]
    if handoff.notes:
        notes.append(f'Handoff notes: {handoff.notes}')
    if handoff.known_risks:
        notes.append('Known risks: ' + '; '.join(handoff.known_risks))
    return (
        PortableReviewTarget(target_type=target_type, target_ref=target_ref or handoff.target, repository='', branch=''),
        PortableReviewResult(
            verdict=result['overall_verdict'],
            scope=scope,
            evidence=evidence,
            checks_run=checks_run,
            findings=findings,
            open_questions=open_questions,
            recommendation=result['next_action'],
            notes=notes,
        ),
    )


def write_outputs(output_dir: Path, target: PortableReviewTarget, result: PortableReviewResult) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'verification_report.md'
    manifest_path = output_dir / 'manifest.json'
    report_path.write_text(render_verification_report(result), encoding='utf-8')
    manifest_path.write_text(json.dumps(build_manifest(target, result), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return report_path, manifest_path


def main() -> int:
    args = parse_args()
    handoff_path = Path(args.handoff_file).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    try:
        handoff = load_handoff(handoff_path, list(args.evidence_file))
        review_risk = detect_review_risk(handoff.changed_files)
        context_text = build_context_text(handoff)
        bridge_response = run_bridge_review(handoff=handoff, review_risk=review_risk, model=args.model, max_tokens=args.max_tokens, context_text=context_text)
        answer_block = bridge_response.get('answer') if isinstance(bridge_response.get('answer'), dict) else {}
        raw_answer = answer_block.get('json')
        result = normalize_model_result(raw_answer, handoff)
        target, portable_result = convert_to_portable(handoff, result, review_risk, args.model)
        report_path, manifest_path = write_outputs(output_dir, target, portable_result)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1
    summary = {
        'qa_result': portable_result.verdict,
        'verification_report': str(report_path),
        'manifest': str(manifest_path),
        'next_action': result['next_action'],
    }
    print(json.dumps(summary, ensure_ascii=False))
    if args.print_report:
        print(render_verification_report(portable_result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
