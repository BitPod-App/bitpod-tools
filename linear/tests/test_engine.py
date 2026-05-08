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
