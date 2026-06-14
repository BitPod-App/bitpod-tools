import unittest
from datetime import datetime, timezone

from linear.src.engine import (
    BOOLEAN_VALUES,
    CANONICAL_TYPES,
    CLASSIFICATION_FIELDS,
    CLASSIFIER_CONTRACT,
    STRICT_BOOLEAN_FIELDS,
    VALID_OUTPUTS,
    LinearBotEngine,
)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.bot = LinearBotEngine()

    def test_find_issue_key(self):
        self.assertEqual(self.bot.find_issue_key("foo BIT-45 bar"), "BIT-45")

    def test_gh_opened_sets_in_progress(self):
        ev = {
            "pull_request": {
                "number": 1,
                "title": "BIT-45 test",
                "body": "",
                "html_url": "https://x",
                "head": {"ref": "b"},
            }
        }
        actions = self.bot.on_github_pr_opened(ev)
        self.assertEqual(actions[0].kind, "set_status")
        self.assertEqual(actions[0].payload["status"], "In Progress")

    def test_gh_opened_without_link_comments(self):
        ev = {
            "pull_request": {
                "number": 1,
                "title": "no issue key",
                "body": "",
                "html_url": "https://x",
                "head": {"ref": "feature/no-key"},
            }
        }
        actions = self.bot.on_github_pr_opened(ev)
        self.assertEqual(actions[0].system, "github")
        self.assertEqual(actions[0].kind, "comment")


    def test_gh_opened_non_draft_dispatches_vera_qa_and_queues_gate(self):
        ev = {
            "action": "opened",
            "pull_request": {
                "number": 50,
                "title": "BIT-619 Retire CODEOWNERS",
                "body": "",
                "draft": False,
                "html_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                "head": {"ref": "codex/bit-619-retire-codeowners-taylor01-mind", "sha": "22cc449"},
            },
        }

        actions = self.bot.on_github_pr_opened(ev)

        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "In Review" for a in actions))
        dispatch = next(a for a in actions if a.system == "hermes" and a.kind == "enqueue_vera_qa")
        self.assertEqual(dispatch.target, "BIT-619")
        self.assertEqual(dispatch.payload["source_event"], "github_pr_opened_review_ready")
        self.assertEqual(dispatch.payload["pr_url"], "https://github.com/BitPod-App/taylor01-mind/pull/50")
        self.assertEqual(dispatch.payload["repo_full_name"], "BitPod-App/taylor01-mind")
        self.assertEqual(dispatch.payload["head_sha"], "22cc449")

        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.payload["name"], "vera-qa-gate")
        self.assertEqual(check.payload["status"], "queued")
        self.assertEqual(check.payload["repo_full_name"], "BitPod-App/taylor01-mind")
        self.assertEqual(check.payload["head_sha"], "22cc449")


    def test_gh_ready_for_review_dispatches_vera_qa_and_queues_gate(self):
        ev = {
            "action": "ready_for_review",
            "pull_request": {
                "number": 17,
                "title": "BIT-617 dispatcher proof",
                "body": "",
                "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/17",
                "head": {"ref": "codex/bit-617-proof", "sha": "abc123"},
            },
        }

        actions = self.bot.on_github_pr_ready_for_review(ev)

        dispatch = next(a for a in actions if a.system == "hermes" and a.kind == "enqueue_vera_qa")
        self.assertEqual(dispatch.target, "BIT-617")
        self.assertEqual(dispatch.payload["source_event"], "github_pr_ready_for_review")
        self.assertEqual(dispatch.payload["pr_url"], "https://github.com/BitPod-App/bitpod-tools/pull/17")
        self.assertEqual(dispatch.payload["repo_full_name"], "BitPod-App/bitpod-tools")
        self.assertEqual(dispatch.payload["head_sha"], "abc123")
        self.assertIn("vera-qa:BIT-617:BitPod-App/bitpod-tools:17:abc123", dispatch.payload["idempotency_key"])

        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.target, "https://github.com/BitPod-App/bitpod-tools/pull/17")
        self.assertEqual(check.payload["name"], "vera-qa-gate")
        self.assertEqual(check.payload["status"], "queued")
        self.assertEqual(check.payload["repo_full_name"], "BitPod-App/bitpod-tools")
        self.assertEqual(check.payload["head_sha"], "abc123")

        comment = next(
            a
            for a in actions
            if a.system == "linear" and a.kind == "comment" and "VERA_QA_RAN" in a.payload.get("body", "")
        )
        self.assertIn("VERA_QA_RAN=false", comment.payload["body"])
        self.assertIn("GITHUB_NATIVE_GATE_SATISFIED=false", comment.payload["body"])
        self.assertIn("LINEAR_QA_RESULT_SYNCED=false", comment.payload["body"])
        self.assertIn("USER_SEAT_REQUIRED=unknown", comment.payload["body"])


    def test_gh_review_requested_for_veraqa_dispatches_vera_qa(self):
        ev = {
            "action": "review_requested",
            "requested_team": {"slug": "veraqa", "name": "veraqa"},
            "pull_request": {
                "number": 18,
                "title": "BIT-617 dispatcher proof",
                "body": "",
                "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/18",
                "head": {"ref": "codex/bit-617-proof", "sha": "def4567"},
            },
        }

        actions = self.bot.on_github_pr_review_requested(ev)

        dispatch = next(a for a in actions if a.system == "hermes" and a.kind == "enqueue_vera_qa")
        self.assertEqual(dispatch.target, "BIT-617")
        self.assertEqual(dispatch.payload["source_event"], "github_pr_review_requested")
        self.assertEqual(dispatch.payload["pr_url"], "https://github.com/BitPod-App/bitpod-tools/pull/18")

    def test_linear_issue_in_review_dispatches_vera_qa_from_attached_pr(self):
        issue = {
            "identifier": "BIT-612",
            "status": "In Review",
            "url": "https://linear.app/bitpod-app/issue/BIT-612/add-claude-fable-5",
            "attachments": [
                {"url": "https://github.com/BitPod-App/taylor01-mind/pull/48", "title": "PR"}
            ],
            "github": {"head_sha": "def456"},
        }

        actions = self.bot.on_linear_issue_in_review(issue)

        dispatch = next(a for a in actions if a.system == "hermes" and a.kind == "enqueue_vera_qa")
        self.assertEqual(dispatch.target, "BIT-612")
        self.assertEqual(dispatch.payload["source_event"], "linear_issue_in_review")
        self.assertEqual(dispatch.payload["pr_url"], "https://github.com/BitPod-App/taylor01-mind/pull/48")
        self.assertEqual(dispatch.payload["repo_full_name"], "BitPod-App/taylor01-mind")
        self.assertEqual(dispatch.payload["head_sha"], "def456")

    def test_qa_passed_with_pr_sha_emits_vera_gate_success(self):
        actions = self.bot.on_linear_comment(
            issue_key="BIT-617",
            comment_body="QA_RESULT=PASSED\nQA_VERDICT: PASSED\nPR_URL=https://github.com/BitPod-App/bitpod-tools/pull/17\nHEAD_SHA=abc1234",
            issue_labels=["Chore"],
            issue_url="https://linear.app/bitpod-app/issue/BIT-617/test",
        )

        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.payload["name"], "vera-qa-gate")
        self.assertEqual(check.payload["status"], "completed")
        self.assertEqual(check.payload["conclusion"], "success")
        self.assertEqual(check.payload["repo_full_name"], "BitPod-App/bitpod-tools")
        self.assertEqual(check.payload["head_sha"], "abc1234")

    def test_vera_qa_completed_passed_syncs_linear_and_github_gate(self):
        actions = self.bot.on_vera_qa_completed(
            {
                "issue_key": "BIT-619",
                "qa_result": "PASSED",
                "qa_verdict": "PASSED",
                "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                "head_sha": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                "issue_url": "https://linear.app/bitpod-app/issue/BIT-619/test",
                "report_path": "verification_report.md",
                "summary": "Vera QA passed after CODEOWNERS retirement fixes.",
            }
        )

        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload["value"] == "qa-passed" for a in actions))
        label = next(a for a in actions if a.system == "linear" and a.kind == "set_label")
        status = next(a for a in actions if a.system == "linear" and a.kind == "set_status")
        self.assertEqual(label.payload["group"], "In Review - QA Gate")
        self.assertEqual(label.payload["source_event"], "vera_qa_completed")
        self.assertEqual(status.payload["source_event"], "vera_qa_completed")
        self.assertTrue(any(a.system == "linear" and a.kind == "set_status" and a.payload["status"] == "Delivered" for a in actions))
        comment = next(a for a in actions if a.system == "linear" and a.kind == "comment")
        self.assertIn("QA_RESULT=PASSED", comment.payload["body"])
        self.assertIn("VERA_QA_RAN=true", comment.payload["body"])
        self.assertIn("GITHUB_NATIVE_GATE_SATISFIED=true", comment.payload["body"])
        self.assertIn("LINEAR_QA_RESULT_SYNCED=true", comment.payload["body"])

        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.payload["name"], "vera-qa-gate")
        self.assertEqual(check.payload["status"], "completed")
        self.assertEqual(check.payload["conclusion"], "success")
        self.assertEqual(check.payload["repo_full_name"], "BitPod-App/taylor01-mind")
        self.assertEqual(check.payload["head_sha"], "1a1fb4e8ba14e7374c18740b655148e34579cc2c")

    def test_vera_qa_completed_failed_blocks_linear_and_github_gate(self):
        actions = self.bot.on_vera_qa_completed(
            {
                "issue_key": "BIT-619",
                "qa_result": "FAILED",
                "qa_verdict": "FAILED",
                "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                "head_sha": "22cc449cf586109d4c0f324657032781e880cd75",
                "issue_url": "https://linear.app/bitpod-app/issue/BIT-619/test",
                "report_path": "verification_report.md",
                "summary": "Test still reads deleted CODEOWNERS.",
            }
        )

        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload["value"] == "qa-failed" for a in actions))
        label = next(a for a in actions if a.system == "linear" and a.kind == "set_label")
        status = next(a for a in actions if a.system == "linear" and a.kind == "set_status")
        self.assertEqual(label.payload["group"], "In Review - QA Gate")
        self.assertEqual(label.payload["source_event"], "vera_qa_completed")
        self.assertEqual(status.payload["source_event"], "vera_qa_completed")
        self.assertTrue(any(a.system == "linear" and a.kind == "set_status" and a.payload["status"] == "In Progress" for a in actions))
        comment = next(a for a in actions if a.system == "linear" and a.kind == "comment")
        self.assertIn("QA_RESULT=FAILED", comment.payload["body"])
        self.assertIn("VERA_QA_RAN=true", comment.payload["body"])
        self.assertIn("GITHUB_NATIVE_GATE_SATISFIED=false", comment.payload["body"])
        self.assertIn("LINEAR_QA_RESULT_SYNCED=true", comment.payload["body"])

        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.payload["status"], "completed")
        self.assertEqual(check.payload["conclusion"], "failure")
        self.assertEqual(check.payload["repo_full_name"], "BitPod-App/taylor01-mind")
        self.assertEqual(check.payload["head_sha"], "22cc449cf586109d4c0f324657032781e880cd75")

    def test_ready_gate_missing_type(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": [],
            "estimate": 3,
            "description": "Linear Classification\n- Output: code\n- Behavior change: yes\n- Broken existing behavior: no\n- Evidence: acceptance criteria\n- Children expected: no\n- PM-testable: yes\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "Backlog" for a in actions))
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))

    def test_ready_gate_missing_estimate(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Feature"],
            "description": "Linear Classification\n- Output: code\n- Behavior change: yes\n- Broken existing behavior: no\n- Evidence: acceptance criteria\n- Children expected: no\n- PM-testable: yes\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-estimate" for a in actions))

    def test_ready_gate_accepts_emoji_type_label(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["⭐️ Feature"],
            "estimate": 3,
            "description": "Linear Classification\n- Output: code\n- Behavior change: yes\n- Broken existing behavior: no\n- Evidence: acceptance criteria\n- Children expected: no\n- PM-testable: yes\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "comment" and "Routing recommendation" in a.payload["body"] for a in actions))
        self.assertFalse(any(a.kind == "set_status" for a in actions))
        self.assertFalse(any(a.kind == "set_label" and a.payload.get("value") == "qa-skipped" for a in actions))

    def test_ready_gate_design_autosets_qa_skipped(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["🎨 Design"],
            "estimate": 3,
            "description": "Linear Classification\n- Output: design artifact\n- Behavior change: no\n- Broken existing behavior: no\n- Evidence: design acceptance\n- Children expected: no\n- PM-testable: yes\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload.get("value") == "qa-skipped" for a in actions))
        self.assertTrue(any(a.kind == "comment" and "QA=skip" in a.payload["body"] for a in actions))

    def test_ready_gate_plan_parent_requires_estimate(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Plan"],
            "description": "Linear Classification\n- Output: plan container\n- Behavior change: no\n- Broken existing behavior: no\n- Evidence: child-ticket rollout scope\n- Children expected: yes\n- PM-testable: no\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-estimate" for a in actions))

    def test_ready_gate_multiple_types_fails_closed(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Feature", "Bug"],
            "estimate": 3,
            "description": "Linear Classification\n- Output: code\n- Behavior change: yes\n- Broken existing behavior: no\n- Evidence: acceptance criteria\n- Children expected: no\n- PM-testable: yes\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))

    def test_ready_gate_missing_classification_block_fails_closed(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Feature"],
            "estimate": 3,
            "description": "Objective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))
        self.assertTrue(any(a.kind == "comment" and "Linear Classification" in a.payload["body"] for a in actions))

    def test_ready_gate_type_mismatch_fails_closed(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Chore"],
            "estimate": 3,
            "description": "Linear Classification\n- Output: code\n- Behavior change: yes\n- Broken existing behavior: no\n- Evidence: acceptance criteria\n- Children expected: no\n- PM-testable: yes\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))
        self.assertTrue(any(a.kind == "comment" and "classifier predicts `Feature`" in a.payload["body"] for a in actions))

    def test_ready_gate_invalid_classification_values_fail_closed(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Chore"],
            "estimate": 3,
            "description": "Linear Classification\n- Output: ???\n- Behavior change: maybe\n- Broken existing behavior: TBD\n- Evidence: acceptance criteria\n- Children expected: no\n- PM-testable: no\n\nObjective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))
        self.assertTrue(any(a.kind == "comment" and "Invalid `Linear Classification` values" in a.payload["body"] for a in actions))

    def test_ready_gate_ignores_existing_in_progress_for_migration(self):
        issue = {
            "identifier": "BIT-45",
            "status": "In Progress",
            "labels": ["Feature"],
            "estimate": 3,
            "description": "Objective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        self.assertEqual(self.bot.on_linear_ready_gate(issue), [])

    def test_classifier_contract_parity(self):
        self.assertEqual(CANONICAL_TYPES, set(CLASSIFIER_CONTRACT["canonical_types"]))
        self.assertEqual(CLASSIFICATION_FIELDS, set(CLASSIFIER_CONTRACT["required_intake_fields"]))
        self.assertEqual(VALID_OUTPUTS, set(CLASSIFIER_CONTRACT["output_values"]))
        self.assertEqual(STRICT_BOOLEAN_FIELDS, set(CLASSIFIER_CONTRACT["strict_boolean_fields"]))
        self.assertEqual(BOOLEAN_VALUES, set(CLASSIFIER_CONTRACT["boolean_values"]))
        self.assertEqual(
            [rule["type"] for rule in CLASSIFIER_CONTRACT["type_decision_order"]],
            ["Bug", "Design", "Release", "Plan", "Feature", "Chore"],
        )

    def test_classifier_routes_technical_chore_pm_skip_allowed(self):
        intake = {
            "Output": "docs/process",
            "Behavior change": "no",
            "Broken existing behavior": "no",
            "Evidence": "process maintenance",
            "Children expected": "no",
            "PM-testable": "no",
        }
        issue_type, _reason = self.bot.classify_issue_type(intake)
        self.assertEqual(issue_type, "Chore")
        self.assertEqual(self.bot.classify_route(issue_type, intake)[:2], ("required", "skip_allowed"))

    def test_linear_comment_failed(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=FAILED\nboom",
            "https://pr",
            issue_labels=["Feature"],
        )
        self.assertEqual(actions[0].payload["value"], "qa-failed")
        self.assertEqual(actions[1].payload["status"], "In Progress")

    def test_linear_comment_passed_acceptance_required_goes_to_delivered(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=PASSED\nok",
            "https://pr",
            issue_labels=["Feature"],
        )
        self.assertEqual(actions[0].payload["value"], "qa-passed")
        self.assertEqual(actions[1].payload["status"], "Delivered")

    def test_linear_comment_passed_non_acceptance_work_goes_to_delivered(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=PASSED\nok",
            "https://pr",
            issue_labels=["Chore"],
        )
        self.assertEqual(actions[1].payload["status"], "Delivered")

    def test_linear_comment_skipped_sets_skip_gate(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=SKIPPED\napproved skip",
            "",
            issue_labels=["Plan"],
        )
        self.assertEqual(actions[0].payload["value"], "qa-skipped")
        self.assertEqual(actions[1].payload["status"], "Delivered")

    def test_linear_comment_without_pr_link_still_updates_linear(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=PASSED\nok",
            "",
            issue_labels=["Chore"],
        )
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].system, "linear")
        self.assertEqual(actions[1].system, "linear")

    def test_acceptance_rejected(self):
        actions = self.bot.on_linear_acceptance_gate_change("BIT-45", "pm-rejected", "https://pr", "missing acceptance criteria")
        self.assertEqual(actions[0].payload["status"], "In Progress")
        self.assertEqual(actions[1].kind, "comment")
        self.assertIn("missing acceptance criteria", actions[1].payload["body"])

    def test_acceptance_accepted(self):
        actions = self.bot.on_linear_acceptance_gate_change("BIT-45", "pm-accepted", "https://pr")
        self.assertEqual(actions[0].payload["status"], "Accepted")

    def test_acceptance_skipped(self):
        actions = self.bot.on_linear_acceptance_gate_change("BIT-45", "pm-skipped", "https://pr")
        self.assertEqual(actions[0].payload["status"], "Accepted")

    def test_merge_gate_fail_closed_for_feature_without_acceptance_gate(self):
        issue = {"identifier": "BIT-45", "labels": ["Feature", "qa-passed"], "status": "Delivered"}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].kind, "comment")
        self.assertIn("missing pm-accepted/pm-skipped", actions[0].payload["body"])
        self.assertIn("status is not Accepted", actions[0].payload["body"])

    def test_merge_gate_pass_for_feature_with_acceptance_gate_sets_done(self):
        issue = {"identifier": "BIT-45", "labels": ["Feature", "qa-passed", "pm-accepted"], "status": "Accepted"}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "set_status")
        self.assertEqual(actions[0].payload["status"], "Done")
        self.assertEqual(actions[1].kind, "comment")
        self.assertIn("Merged recorded", actions[1].payload["body"])

    def test_merge_gate_pass_for_chore_with_pm_skip(self):
        issue = {"identifier": "BIT-45", "labels": ["Chore", "qa-passed", "pm-skipped"], "status": "Accepted"}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "set_status")
        self.assertEqual(actions[0].payload["status"], "Done")
        self.assertEqual(actions[1].kind, "comment")
        self.assertIn("Merged recorded", actions[1].payload["body"])

    def test_merge_gate_accepts_emoji_type_label(self):
        issue = {"identifier": "BIT-45", "labels": ["⚙️ Chore", "qa-passed", "pm-accepted"], "status": "Accepted"}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "set_status")
        self.assertEqual(actions[0].payload["status"], "Done")

    def test_merge_gate_fail_closed_for_release(self):
        issue = {"identifier": "BIT-45", "labels": ["Release", "qa-passed", "pm-accepted"], "status": "Accepted"}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "comment")
        self.assertIn("Release issues do not auto-close", actions[0].payload["body"])

    def test_merge_gate_fail_closed_when_blocked(self):
        issue = {"identifier": "BIT-45", "labels": ["Feature", "qa-passed", "pm-accepted", "blocked"], "status": "Accepted"}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "comment")
        self.assertIn("issue is blocked", actions[0].payload["body"])

    def test_aging_scan_backlog_to_icebox(self):
        now = datetime(2026, 3, 4, tzinfo=timezone.utc)
        issues = [{"identifier": "BIT-1", "status": "Backlog", "updatedAt": "2026-01-01T00:00:00Z"}]
        actions = self.bot.daily_aging_scan(issues, now=now)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "Icebox 🧊" for a in actions))

    def test_aging_scan_icebox_to_stale_with_reopen_comment(self):
        now = datetime(2026, 3, 4, tzinfo=timezone.utc)
        issues = [{"identifier": "BIT-2", "status": "Icebox 🧊", "updatedAt": "2026-01-01T00:00:00Z"}]
        actions = self.bot.daily_aging_scan(issues, now=now)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "Stale" for a in actions))
        self.assertTrue(any(a.kind == "comment" and "can be reopened later" in a.payload["body"] for a in actions))


if __name__ == "__main__":
    unittest.main()
