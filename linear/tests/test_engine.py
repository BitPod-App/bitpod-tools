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

    def test_linear_comment_failed(self):
        actions = self.bot.on_linear_comment("BIT-45", "QA_RESULT=FAILED\nboom", "https://pr")
        self.assertEqual(actions[0].payload["value"], "♦️ QA: Failed")

    def test_aging_scan(self):
        now = datetime(2026, 3, 4, tzinfo=timezone.utc)
        issues = [{"identifier": "BIT-1", "status": "📂 Backlog", "updatedAt": "2026-01-01T00:00:00Z"}]
        actions = self.bot.daily_aging_scan(issues, now=now)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "🧊 Icebox" for a in actions))


if __name__ == "__main__":
    unittest.main()
