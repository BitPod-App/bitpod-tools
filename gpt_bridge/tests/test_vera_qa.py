from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import gpt_bridge.vera_qa as vera_qa  # noqa: E402
from tools.taylor01.core.agents.vera.contract import (  # noqa: E402
    PortableReviewResult,
    PortableReviewTarget,
    build_manifest,
    render_verification_report,
)


class VeraPortableContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _write_handoff(self, payload: dict[str, object]) -> Path:
        path = self.root / 'handoff.json'
        path.write_text(json.dumps(payload), encoding='utf-8')
        return path

    def test_load_handoff_resolves_relative_evidence_paths(self) -> None:
        evidence = self.root / 'notes.txt'
        evidence.write_text('sample evidence', encoding='utf-8')
        handoff_path = self._write_handoff(
            {
                'system_under_test': 'vera-runner',
                'critical_acceptance_criteria': ['AC text'],
                'evidence_paths': ['notes.txt'],
            }
        )

        handoff = vera_qa.load_handoff(handoff_path, [])

        self.assertEqual(handoff.system_under_test, 'vera-runner')
        self.assertEqual(handoff.evidence_paths, (evidence.resolve(),))
        self.assertEqual(handoff.critical_acceptance_criteria[0].criterion_id, 'AC-1')

    def test_detect_review_risk_flags_high_risk_files(self) -> None:
        risk = vera_qa.detect_review_risk(('src/auth/session.py', 'payments/stripe_checkout.ts', 'README.md'))
        self.assertTrue(risk['high_risk'])
        self.assertIn('auth_permissions', risk['patterns_matched'])
        self.assertIn('billing_payments', risk['patterns_matched'])
        self.assertIn('src/auth/session.py', risk['files_matched'])

    def test_normalize_model_result_downgrades_missing_criteria_to_no_verdict(self) -> None:
        handoff_path = self._write_handoff(
            {
                'system_under_test': 'vera-runner',
                'critical_acceptance_criteria': [
                    {'id': 'AC-1', 'text': 'First'},
                    {'id': 'AC-2', 'text': 'Second'},
                ],
            }
        )
        handoff = vera_qa.load_handoff(handoff_path, [])

        result = vera_qa.normalize_model_result(
            {
                'overall_verdict': 'PASSED',
                'summary': 'All good',
                'criteria_results': [{'id': 'AC-1', 'result': 'PASS', 'steps': ['one'], 'observed': 'ok'}],
            },
            handoff,
        )

        self.assertEqual(result['overall_verdict'], 'NO_VERDICT')
        self.assertEqual(result['criteria_results'][1]['result'], 'NO_VERDICT')

    def test_portable_artifacts_preserve_pass_case(self) -> None:
        result = PortableReviewResult(
            verdict='PASSED',
            scope=['PR: https://github.com/example/repo/pull/1'],
            evidence=['AC-1 PASS: observed expected behavior'],
            checks_run=['PR metadata inspection'],
            findings=['No blockers found.'],
            open_questions=[],
            recommendation='Proceed with the normal review flow.',
            notes=['pass case proof'],
        )
        report = render_verification_report(result)
        manifest = build_manifest(
            PortableReviewTarget(target_type='pr', target_ref='https://github.com/example/repo/pull/1', repository='example/repo', branch='feature/pass'),
            result,
        )
        self.assertIn('## Verdict', report)
        self.assertIn('- PASSED', report)
        self.assertEqual(manifest['review']['verdict'], 'PASSED')
        self.assertEqual(manifest['artifacts']['verificationReport'], 'verification_report.md')

    def test_portable_artifacts_preserve_fail_case(self) -> None:
        result = PortableReviewResult(
            verdict='FAILED',
            scope=['PR: https://github.com/example/repo/pull/2'],
            evidence=['AC-1 FAIL: expected safe auth; actual bypass'],
            checks_run=['Diff inspection'],
            findings=['Authentication bypass is a blocker.'],
            open_questions=[],
            recommendation='Fix the auth regression and rerun Vera.',
            notes=['fail case proof'],
        )
        report = render_verification_report(result)
        manifest = build_manifest(
            PortableReviewTarget(target_type='pr', target_ref='https://github.com/example/repo/pull/2', repository='example/repo', branch='feature/fail'),
            result,
        )
        self.assertIn('- FAILED', report)
        self.assertEqual(manifest['review']['verdict'], 'FAILED')
        self.assertIn('Authentication bypass is a blocker.', report)

    def test_portable_artifacts_preserve_no_verdict_case(self) -> None:
        result = PortableReviewResult(
            verdict='NO_VERDICT',
            scope=['PR: https://github.com/example/repo/pull/3'],
            evidence=['AC-1 NO_VERDICT: logs were missing'],
            checks_run=['PR metadata inspection'],
            findings=['Insufficient evidence for a truthful pass/fail verdict.'],
            open_questions=['Provide the missing test logs.'],
            recommendation='Provide stronger evidence and rerun Vera.',
            notes=['no-verdict case proof'],
        )
        report = render_verification_report(result)
        manifest = build_manifest(
            PortableReviewTarget(target_type='pr', target_ref='https://github.com/example/repo/pull/3', repository='example/repo', branch='feature/no-verdict'),
            result,
        )
        self.assertIn('- NO_VERDICT', report)
        self.assertEqual(manifest['review']['verdict'], 'NO_VERDICT')
        self.assertEqual(manifest['openQuestions'], ['Provide the missing test logs.'])


if __name__ == '__main__':
    unittest.main()
