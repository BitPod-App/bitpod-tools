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
        self.assertEqual(actions[0].payload["status"], "🏗️ In Progress")

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
            "status": "☑️ Ready",
            "labels": [],
            "description": "Context\nGoal\nImplementation List\nDO NOT list\nDoD / Acceptance Criteria",
        }
        actions = self.bot.on_linear_ready_gate(issue)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "📂 Backlog" for a in actions))

    def test_linear_comment_failed(self):
        actions = self.bot.on_linear_comment("BIT-45", "QA_RESULT=FAILED\nboom", "https://pr")
        self.assertEqual(actions[0].payload["value"], "♦️ QA: Failed")

    def test_linear_comment_passed(self):
        actions = self.bot.on_linear_comment("BIT-45", "QA_RESULT=PASSED\nok", "https://pr")
        self.assertEqual(actions[0].payload["value"], "🔷 QA: Passed")
        self.assertTrue(any(a.kind == "set_label" and a.payload.get("value") == "✴️ PM: Waiting" for a in actions))

    def test_linear_comment_passed_keeps_pm_decision(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=PASSED\nok",
            "https://pr",
            issue_labels=["❇️ PM: Approved"],
        )
        self.assertTrue(any(a.kind == "set_label" and a.payload.get("value") == "🔷 QA: Passed" for a in actions))
        self.assertFalse(any(a.kind == "set_label" and a.payload.get("value") == "✴️ PM: Waiting" for a in actions))

    def test_linear_comment_parses_pr_url_token(self):
        actions = self.bot.on_linear_comment(
            "BIT-45",
            "QA_RESULT=FAILED\nPR_URL=https://github.com/BitPod-App/bitpod-tools/pull/123\nboom",
            "",
        )
        gh = [a for a in actions if a.system == "github" and a.kind == "comment"][0]
        self.assertEqual(gh.target, "https://github.com/BitPod-App/bitpod-tools/pull/123")

    def test_linear_comment_without_pr_link_fails_closed(self):
        actions = self.bot.on_linear_comment("BIT-45", "QA_RESULT=PASSED\nok", "")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].system, "linear")
        self.assertEqual(actions[0].kind, "comment")
        self.assertIn("Linking incomplete", actions[0].payload.get("body", ""))

    def test_pm_rejected(self):
        actions = self.bot.on_linear_pm_label_change("BIT-45", "❌ PM: Rejected", "https://pr")
        self.assertEqual(actions[0].payload["status"], "🏗️ In Progress")

    def test_merge_gate_fail_closed(self):
        issue = {"identifier": "BIT-45", "labels": ["🔶 QA: Not Done", "✴️ PM: Waiting"]}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].kind, "comment")

    def test_merge_gate_pass(self):
        issue = {"identifier": "BIT-45", "labels": ["🔷 QA: Passed", "❇️ PM: Approved"]}
        actions = self.bot.on_github_pr_merged(issue, "https://pr", "sha")
        self.assertEqual(actions[0].payload["status"], "✅ Done")

    def test_aging_scan(self):
        now = datetime(2026, 3, 4, tzinfo=timezone.utc)
        issues = [{"identifier": "BIT-1", "status": "📂 Backlog", "updatedAt": "2026-01-01T00:00:00Z"}]
        actions = self.bot.daily_aging_scan(issues, now=now)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "🧊 Icebox" for a in actions))


if __name__ == "__main__":
    unittest.main()
