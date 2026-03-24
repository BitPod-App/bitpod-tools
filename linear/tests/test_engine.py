import unittest
from datetime import datetime, timezone

from linear.src.engine import LinearBotEngine


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
            "description": "Objective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "Backlog" for a in actions))
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))

    def test_ready_gate_missing_estimate(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Feature"],
            "description": "Objective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-estimate" for a in actions))

    def test_ready_gate_plan_parent_requires_estimate(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Plan"],
            "description": "Objective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-estimate" for a in actions))

    def test_ready_gate_multiple_types_fails_closed(self):
        issue = {
            "identifier": "BIT-45",
            "status": "Ready",
            "labels": ["Feature", "Bug"],
            "estimate": 3,
            "description": "Objective\nScope\nRequired outputs\nVerification plan\nRollback note\nAcceptance / closure criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_label" and a.payload["value"] == "needs-type" for a in actions))

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

    def test_linear_comment_passed_non_acceptance_work_goes_to_done(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=PASSED\nok",
            "https://pr",
            issue_labels=["Chore"],
        )
        self.assertEqual(actions[1].payload["status"], "Done")

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
        actions = self.bot.on_linear_acceptance_gate_change("BIT-45", "pm-rejected", "https://pr")
        self.assertEqual(actions[0].payload["status"], "In Progress")

    def test_acceptance_accepted(self):
        actions = self.bot.on_linear_acceptance_gate_change("BIT-45", "pm-accepted", "https://pr")
        self.assertEqual(actions[0].payload["status"], "Accepted")

    def test_acceptance_skipped(self):
        actions = self.bot.on_linear_acceptance_gate_change("BIT-45", "pm-skipped", "https://pr")
        self.assertEqual(actions[0].payload["status"], "Done")

    def test_merge_gate_fail_closed_for_feature_without_acceptance_gate(self):
        issue = {"identifier": "BIT-45", "labels": ["Feature", "qa-passed"]}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].kind, "comment")
        self.assertIn("workflow gates are incomplete", actions[0].payload["body"])

    def test_merge_gate_pass_for_feature_with_acceptance_gate_sets_done(self):
        issue = {"identifier": "BIT-45", "labels": ["Feature", "qa-passed", "pm-accepted"]}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "set_status")
        self.assertEqual(actions[0].payload["status"], "Done")
        self.assertEqual(actions[1].kind, "comment")
        self.assertIn("Merged recorded", actions[1].payload["body"])

    def test_merge_gate_pass_for_chore_with_qa_gate_only(self):
        issue = {"identifier": "BIT-45", "labels": ["Chore", "qa-passed"]}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].kind, "comment")
        self.assertIn("Merged recorded", actions[0].payload["body"])

    def test_aging_scan(self):
        now = datetime(2026, 3, 4, tzinfo=timezone.utc)
        issues = [{"identifier": "BIT-1", "status": "Backlog", "updatedAt": "2026-01-01T00:00:00Z"}]
        actions = self.bot.daily_aging_scan(issues, now=now)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "Icebox 🧊" for a in actions))


if __name__ == "__main__":
    unittest.main()
