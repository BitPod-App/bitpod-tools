import unittest

from linear.scripts.handoff_queue_report import build_queue, render_report, scan_issue


class HandoffQueueReportTests(unittest.TestCase):
    def test_scan_issue_marks_in_review_without_qa_pass_as_qa_queue_blocker(self):
        issue = {
            "identifier": "BIT-100",
            "title": "Needs QA",
            "url": "https://linear.app/bitpod-app/issue/BIT-100",
            "status": "In Review",
            "labels": ["⚙️ Chore"],
            "assignee": "Taylor01",
            "project": "Taylor01",
            "team": "Product Development",
        }
        entry = scan_issue(issue)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.queue, "QA")
        self.assertIn("missing qa-passed", entry.blockers)

    def test_scan_issue_preserves_qa_skipped_signal(self):
        issue = {
            "identifier": "BIT-101",
            "title": "Skipped QA",
            "url": "https://linear.app/bitpod-app/issue/BIT-101",
            "status": "Delivered",
            "labels": ["🐞 Bug", "qa-skipped"],
            "assignee": "CJ Argüello",
            "project": "Taylor01",
            "team": "Product Development",
        }
        entry = scan_issue(issue)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.queue, "PM")
        self.assertIn("qa-skipped", entry.blockers)
        self.assertIn("missing pm-accepted", entry.blockers)
        self.assertNotIn("missing qa-passed", entry.blockers)

    def test_scan_issue_reuses_existing_blocked_label_logic(self):
        issue = {
            "identifier": "BIT-102",
            "title": "Blocked work",
            "url": "https://linear.app/bitpod-app/issue/BIT-102",
            "status": "Delivered",
            "labels": ["⭐️ Feature", "qa-passed", "blocked", "needs-specs"],
            "assignee": "Taylor01",
            "project": "Taylor01",
            "team": "Product Development",
        }
        entry = scan_issue(issue)
        self.assertIsNotNone(entry)
        self.assertIn("blocked", entry.blockers)
        self.assertIn("needs-specs", entry.blockers)
        self.assertIn("missing pm-accepted", entry.blockers)

    def test_build_queue_filters_team_and_project(self):
        issues = [
            {
                "identifier": "BIT-200",
                "title": "Keep me",
                "url": "https://linear.app/bitpod-app/issue/BIT-200",
                "status": "In Review",
                "labels": ["⚙️ Chore"],
                "assignee": "Taylor01",
                "project": "Taylor01",
                "team": "Product Development",
            },
            {
                "identifier": "OPS-1",
                "title": "Wrong team",
                "url": "https://linear.app/bitpod-app/issue/OPS-1",
                "status": "In Review",
                "labels": ["⚙️ Chore"],
                "assignee": "Taylor01",
                "project": "Taylor01",
                "team": "Operations",
            },
            {
                "identifier": "BIT-201",
                "title": "Wrong project",
                "url": "https://linear.app/bitpod-app/issue/BIT-201",
                "status": "In Review",
                "labels": ["⚙️ Chore"],
                "assignee": "Taylor01",
                "project": "Other",
                "team": "Product Development",
            },
        ]
        entries = build_queue(issues, team="Product Development", project="Taylor01")
        self.assertEqual([entry.identifier for entry in entries], ["BIT-200"])

    def test_render_report_is_compact_and_human_readable(self):
        issues = [
            {
                "identifier": "BIT-300",
                "title": "QA pending",
                "url": "https://linear.app/bitpod-app/issue/BIT-300",
                "status": "In Review",
                "labels": ["⚙️ Chore"],
                "assignee": "Taylor01",
                "project": "Taylor01",
                "team": "Product Development",
            },
            {
                "identifier": "BIT-301",
                "title": "PM pending",
                "url": "https://linear.app/bitpod-app/issue/BIT-301",
                "status": "Delivered",
                "labels": ["⚙️ Chore", "qa-skipped"],
                "assignee": "CJ Argüello",
                "project": "Taylor01",
                "team": "Product Development",
            },
        ]
        entries = build_queue(issues, team="Product Development")
        report = render_report(entries, team="Product Development", source="test")
        self.assertIn("Summary", report)
        self.assertIn("QA queue (In Review): 1 ticket(s)", report)
        self.assertIn("PM queue (Delivered): 1 ticket(s)", report)
        self.assertIn("missing qa-passed", report)
        self.assertIn("qa-skipped", report)


if __name__ == "__main__":
    unittest.main()
