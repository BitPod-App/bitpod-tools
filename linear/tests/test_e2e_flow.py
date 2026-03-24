import unittest

from linear.src.runtime import BotRuntime


class E2EFlowTests(unittest.TestCase):
    def test_feature_happy_path_to_accepted(self):
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
        self.assertTrue(any(a.kind == "set_status" and a.payload["status"] == "In Progress" for a in actions_opened))

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
        self.assertTrue(any(a.kind == "set_status" and a.payload.get("status") == "In Review" for a in actions_review))
        self.assertFalse(any(a.kind == "set_label" for a in actions_review))

        qa_passed = {
            "type": "comment_created",
            "issue_key": "BIT-45",
            "comment_body": "QA_RESULT=PASSED\nall checks pass",
            "pr_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
            "issue_labels": ["Type: ⭐️ Feature"],
        }
        actions_qa = rt.run_linear_event(qa_passed)
        self.assertTrue(any(a.kind == "set_label" and a.payload.get("value") == "qa-passed" for a in actions_qa))
        self.assertTrue(any(a.kind == "set_status" and a.payload.get("status") == "Delivered" for a in actions_qa))

        accepted = {
            "type": "acceptance_gate_changed",
            "issue_key": "BIT-45",
            "gate_value": "pm-accepted",
            "pr_url": "https://github.com/BitPod-App/bitpod-tools/pull/7",
        }
        actions_accept = rt.run_linear_event(accepted)
        self.assertTrue(any(a.kind == "set_status" and a.payload.get("status") == "Accepted" for a in actions_accept))

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
                "labels": ["Type: ⭐️ Feature", "qa-passed", "pm-accepted"],
            },
        }
        actions_merged = rt.run_github_event(merged)
        self.assertTrue(any(a.kind == "comment" and "Merged recorded" in a.payload.get("body", "") for a in actions_merged))


if __name__ == "__main__":
    unittest.main()
