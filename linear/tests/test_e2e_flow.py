import unittest

from linear.src.runtime import BotRuntime


class E2EFlowTests(unittest.TestCase):
    def test_happy_path_to_done(self):
        rt = BotRuntime()

        opened = {
            "action": "opened",
            "pull_request": {
                "number": 7,
                "title": "BIT-45 bot happy path",
                "body": "",
                "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
                "head": {"ref": "codex/bit-45-happy"},
            },
        }
        actions_opened = rt.run_github_event(opened)
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "🏗️ In Progress" for a in actions_opened))

        review = {
            "action": "ready_for_review",
            "pull_request": {
                "number": 7,
                "title": "BIT-45 bot happy path",
                "body": "",
                "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
                "head": {"ref": "codex/bit-45-happy"},
            },
        }
        actions_review = rt.run_github_event(review)
        self.assertTrue(any(a.kind == "set_label" and a.payload.get("value") == "🔶 QA: Not Done" for a in actions_review))
        self.assertTrue(any(a.kind == "set_label_if_empty" and a.payload.get("value") == "✴️ PM: Waiting" for a in actions_review))

        qa_passed = {
            "type": "comment_created",
            "issue_key": "BIT-45",
            "comment_body": "QA_RESULT=PASSED\nall checks pass",
            "pr_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
        }
        actions_qa = rt.run_linear_event(qa_passed)
        self.assertTrue(any(a.kind == "set_label" and a.payload.get("value") == "🔷 QA: Passed" for a in actions_qa))

        pm_approved = {
            "type": "pm_label_changed",
            "issue_key": "BIT-45",
            "pm_value": "❇️ PM: Approved",
            "pr_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
        }
        actions_pm = rt.run_linear_event(pm_approved)
        self.assertTrue(any(a.system == "github" and a.kind == "comment" for a in actions_pm))

        merged = {
            "action": "closed",
            "pull_request": {
                "number": 7,
                "merged": True,
                "merge_commit_sha": "abc123",
                "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
            },
            "linear_issue": {
                "identifier": "BIT-45",
                "labels": ["🔷 QA: Passed", "❇️ PM: Approved"],
            },
        }
        actions_merged = rt.run_github_event(merged)
        self.assertTrue(any(a.kind == "set_status" and a.payload.get("status") == "✅ Done" for a in actions_merged))


if __name__ == "__main__":
    unittest.main()
