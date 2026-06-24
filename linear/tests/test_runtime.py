import os
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from linear.src.engine import Action
from linear.src.governance import GovernancePolicy
from linear.src.runtime import BotRuntime
from linear.src.memory import InMemoryStore, JsonlFileStore
from linear.src.service import (
    apply_actions,
    collect_vera_qa_completed_events,
    execute_hermes_vera_dispatch,
    execute_github_check_run,
    enrich_github_override_event,
    github_app_installation_token_from_env,
    load_completed_vera_qa_tasks,
    sync_vera_qa_results_once,
    _github_webhook_secret_from_env,
    _github_event_may_be_qa_override,
    _filter_vera_qa_tasks,
    _linear_webhook_secret_from_env,
    _normalize_private_key,
    _verify_github_webhook_signature,
    _verify_linear_webhook_signature,
)


class RuntimeTests(unittest.TestCase):
    def test_runtime_records_event_memory(self):
        store = InMemoryStore()
        rt = BotRuntime(store=store)
        ev = {
            "action": "opened",
            "pull_request": {
                "title": "BIT-45 test",
                "body": "",
                "head": {"ref": "x"},
                "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/17",
            },
        }
        actions = rt.run_github_event(ev)
        self.assertTrue(len(actions) > 0)
        mem = store.list_for("BIT-45")
        self.assertEqual(len(mem), 1)
        self.assertTrue(mem[0].kind.startswith("github:"))



    def test_runtime_routes_github_review_requested_to_vera_dispatch(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "action": "review_requested",
                "requested_team": {"slug": "veraqa"},
                "pull_request": {
                    "number": 18,
                    "title": "BIT-617 dispatcher proof",
                    "body": "",
                    "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/18",
                    "head": {"ref": "codex/bit-617-proof", "sha": "def4567"},
                },
            }
        )

        self.assertTrue(any(a.system == "hermes" and a.kind == "enqueue_vera_qa" for a in actions))

    def test_runtime_routes_github_opened_non_draft_to_vera_dispatch(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
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
        )

        self.assertTrue(any(a.system == "hermes" and a.kind == "enqueue_vera_qa" for a in actions))
        self.assertTrue(any(a.system == "github" and a.kind == "check_run" and a.payload.get("status") == "queued" for a in actions))

    def test_runtime_routes_github_synchronize_to_vera_dispatch_for_review_ready_pr(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "action": "synchronize",
                "pull_request": {
                    "number": 120,
                    "title": "BIT-617 dispatcher proof",
                    "body": "",
                    "draft": False,
                    "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/120",
                    "head": {"ref": "codex/bit-617-proof", "sha": "feed617"},
                },
            }
        )

        self.assertTrue(any(a.system == "hermes" and a.kind == "enqueue_vera_qa" for a in actions))
        self.assertTrue(any(a.system == "github" and a.kind == "check_run" and a.payload.get("head_sha") == "feed617" for a in actions))

    def test_runtime_routes_github_issue_comment_override_to_vera_gate(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "_github_event": "issue_comment",
                "action": "created",
                "sender": {"login": "cjarguello"},
                "override_label_actor": "cjarguello",
                "issue": {
                    "number": 17,
                    "title": "BIT-706 override comment",
                    "labels": [{"name": "QA_OVERRIDE"}],
                    "pull_request": {},
                },
                "pull_request": {
                    "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/17",
                    "head": {"sha": "abc1234"},
                },
                "comment": {"body": "/qa-override runtime route proof", "user": {"login": "cjarguello"}},
            }
        )

        self.assertTrue(any(a.system == "github" and a.kind == "check_run" and a.payload.get("conclusion") == "success" for a in actions))
        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload.get("value") == "qa-override" for a in actions))

    def test_runtime_routes_github_labeled_override_with_discovered_reason_to_vera_gate(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "_github_event": "issues",
                "action": "labeled",
                "sender": {"login": "cjarguello"},
                "label": {"name": "QA_OVERRIDE"},
                "override_label_actor": "cjarguello",
                "head_current_at": "2026-06-23T05:20:00Z",
                "issue": {
                    "number": 77,
                    "title": "BIT-708 labeled override",
                    "labels": [{"name": "QA_OVERRIDE"}],
                    "pull_request": {},
                },
                "pull_request": {
                    "html_url": "https://github.com/BitPod-App/sector-feeds/pull/77",
                    "head": {"sha": "abc1234"},
                },
                "override_reason": {
                    "source": "comment",
                    "actor": "cjarguello",
                    "body": "/qa-override discovered reason",
                    "created_at": "2026-06-23T05:21:00Z",
                    "html_url": "https://github.com/BitPod-App/sector-feeds/pull/77#issuecomment-1",
                },
            }
        )

        self.assertTrue(any(a.system == "github" and a.kind == "check_run" and a.payload.get("conclusion") == "success" for a in actions))
        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload.get("value") == "qa-override" for a in actions))

    def test_runtime_routes_github_review_override_to_vera_gate(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "_github_event": "pull_request_review",
                "action": "submitted",
                "sender": {"login": "cjarguello"},
                "override_label_actor": "cjarguello",
                "pull_request": {
                    "number": 17,
                    "title": "BIT-707 override review",
                    "labels": [{"name": "QA_OVERRIDE"}],
                    "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/17",
                    "head": {"sha": "abc1234"},
                },
                "review": {
                    "state": "approved",
                    "body": "/qa-override runtime review proof",
                    "user": {"login": "cjarguello"},
                },
            }
        )

        self.assertTrue(any(a.system == "github" and a.kind == "check_run" and a.payload.get("conclusion") == "success" for a in actions))
        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload.get("value") == "qa-override" for a in actions))


    def test_runtime_routes_pull_request_review_ready_for_vera_gate_to_dispatch(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "_github_event": "pull_request_review",
                "action": "submitted",
                "sender": {"login": "cjarguello"},
                "review": {"state": "commented", "body": "Ready for vera-qa-gate"},
                "pull_request": {
                    "number": 68,
                    "title": "BIT-617 dispatcher proof",
                    "body": "",
                    "html_url": "https://github.com/BitPod-App/bitpod-docs/pull/68",
                    "head": {"ref": "codex/bit-617-proof", "sha": "f9619c0"},
                },
            }
        )

        self.assertTrue(any(a.system == "hermes" and a.kind == "enqueue_vera_qa" for a in actions))
        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.payload["status"], "queued")
        self.assertEqual(check.payload["head_sha"], "f9619c0")


    def test_runtime_ignores_plain_pull_request_review_without_gate_or_override_command(self):
        rt = BotRuntime()
        actions = rt.run_github_event(
            {
                "_github_event": "pull_request_review",
                "action": "submitted",
                "sender": {"login": "cjarguello"},
                "review": {"state": "approved", "body": "Looks good."},
                "pull_request": {
                    "number": 68,
                    "title": "BIT-617 dispatcher proof",
                    "body": "",
                    "html_url": "https://github.com/BitPod-App/bitpod-docs/pull/68",
                    "head": {"ref": "codex/bit-617-proof", "sha": "f9619c0"},
                },
            }
        )

        self.assertEqual(actions, [])

    def test_runtime_routes_linear_issue_in_review_to_vera_dispatch(self):
        rt = BotRuntime()
        actions = rt.run_linear_event(
            {
                "type": "issue_in_review",
                "issue": {
                    "identifier": "BIT-612",
                    "status": "In Review",
                    "attachments": [
                        {"url": "https://github.com/BitPod-App/taylor01-mind/pull/48"}
                    ],
                    "github": {"head_sha": "def456"},
                },
            }
        )

        self.assertTrue(any(a.system == "hermes" and a.kind == "enqueue_vera_qa" for a in actions))

    def test_runtime_routes_vera_qa_completed_to_gate_sync(self):
        rt = BotRuntime()
        actions = rt.run_linear_event(
            {
                "type": "vera_qa_completed",
                "issue_key": "BIT-619",
                "qa_result": "PASSED",
                "qa_verdict": "PASSED",
                "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                "head_sha": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                "summary": "Vera QA passed after CODEOWNERS retirement fixes.",
            }
        )

        self.assertTrue(any(a.system == "github" and a.kind == "check_run" and a.payload.get("conclusion") == "success" for a in actions))
        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload.get("value") == "qa-passed" for a in actions))

    def test_collects_completed_vera_qa_task_from_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = os.path.join(tmp, "verification_report.md")
            manifest_path = os.path.join(tmp, "manifest.json")
            with open(report_path, "w", encoding="utf-8") as fh:
                fh.write("QA_RESULT=PASSED\n")
            with open(manifest_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-619",
                        "pr": 50,
                        "head": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "qa_result": "PASSED",
                        "verdict": "PASSED",
                    },
                    fh,
                )

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_done",
                        "title": "Vera QA review: BIT-619 / PR #50",
                        "body": "Issue: BIT-619\nPR: https://github.com/BitPod-App/taylor01-mind/pull/50\nHead SHA: 1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "assignee": "vera",
                        "status": "done",
                        "workspace_path": tmp,
                        "result": "Vera finished.",
                    }
                ]
            )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "vera_qa_completed")
        self.assertEqual(events[0]["task_id"], "t_done")
        self.assertEqual(events[0]["issue_key"], "BIT-619")
        self.assertEqual(events[0]["qa_result"], "PASSED")
        self.assertEqual(events[0]["pr_url"], "https://github.com/BitPod-App/taylor01-mind/pull/50")
        self.assertEqual(events[0]["head_sha"], "1a1fb4e8ba14e7374c18740b655148e34579cc2c")

    def test_collect_ignores_ad_hoc_vera_smoke_task_without_dispatch_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "verification_report.md"), "w", encoding="utf-8") as fh:
                fh.write("QA_RESULT=PASSED\n")
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-653",
                        "pr": "https://github.com/BitPod-App/bitpod-docs/pull/65",
                        "head_sha": "b30d121b6cc6a9204940ea56fbe4865c9f08704e",
                        "qa_verdict": "PASSED",
                    },
                    fh,
                )

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_smoke",
                        "title": "Vera QA no-external-memory smoke: BIT-653",
                        "body": "\n".join(
                            [
                                "Vera QA no-external-memory controlled smoke.",
                                "Issue: BIT-653",
                                "PR: https://github.com/BitPod-App/bitpod-docs/pull/65",
                                "Head SHA: b30d121b6cc6a9204940ea56fbe4865c9f08704e",
                                f"Artifact workspace: {tmp}",
                            ]
                        ),
                        "assignee": "vera",
                        "status": "done",
                        "workspace_path": tmp,
                    }
                ]
            )

        self.assertEqual(events, [])

    def test_collector_reads_vera_artifacts_from_artifact_workspace_not_reviewed_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            reviewed_repo = os.path.join(tmp, "reviewed-repo")
            artifact_workspace = os.path.join(tmp, "qa-artifacts", "BIT-631", "repo", "pr-44", "abc123")
            os.makedirs(reviewed_repo)
            os.makedirs(artifact_workspace)
            with open(os.path.join(artifact_workspace, "verification_report.md"), "w", encoding="utf-8") as fh:
                fh.write("QA_RESULT=PASSED\n")
            with open(os.path.join(artifact_workspace, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-631",
                        "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/44",
                        "head": "abc123def456",
                        "qa_result": "PASSED",
                    },
                    fh,
                )

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_artifact_workspace",
                        "title": "Vera QA review: BIT-631",
                        "body": "Issue: BIT-631\nPR: https://github.com/BitPod-App/taylor01-mind/pull/44\nHead SHA: abc123def456\nArtifact workspace: "
                        + artifact_workspace,
                        "assignee": "vera",
                        "status": "done",
                        "workspace_path": reviewed_repo,
                        "result": "Vera passed.",
                    }
                ]
            )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["issue_key"], "BIT-631")
        self.assertEqual(events[0]["report_path"], os.path.join(artifact_workspace, "verification_report.md"))
        self.assertFalse(os.path.exists(os.path.join(reviewed_repo, "manifest.json")))
        self.assertFalse(os.path.exists(os.path.join(reviewed_repo, "verification_report.md")))

    def test_collector_keeps_legacy_workspace_root_manifest_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-617",
                        "pr": 120,
                        "sha": "4a2c11e4a9abcb2e24feec697c74d3564fc48168",
                        "qa_verdict": "PASSED",
                    },
                    fh,
                )

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_current_shape",
                        "title": "Vera QA review: BIT-617",
                        "body": "Issue: BIT-617\nPR: https://github.com/BitPod-App/bitpod-tools/pull/120\nHead SHA: 4a2c11e4a9abcb2e24feec697c74d3564fc48168",
                        "assignee": "vera",
                        "status": "done",
                        "workspace_path": tmp,
                        "result": "QA_RESULT=PASSED",
                    }
                ]
            )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["issue_key"], "BIT-617")
        self.assertEqual(events[0]["qa_result"], "PASSED")
        self.assertEqual(events[0]["qa_verdict"], "PASSED")
        self.assertEqual(events[0]["pr_url"], "https://github.com/BitPod-App/bitpod-tools/pull/120")
        self.assertEqual(events[0]["head_sha"], "4a2c11e4a9abcb2e24feec697c74d3564fc48168")

    def test_collector_accepts_override_and_action_required_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks = []
            for task_id, result in [("t_override", "OVERRIDE"), ("t_action", "ACTION_REQUIRED")]:
                workspace = os.path.join(tmp, task_id)
                os.mkdir(workspace)
                with open(os.path.join(workspace, "manifest.json"), "w", encoding="utf-8") as fh:
                    json.dump(
                        {
                            "issue": "BIT-620",
                            "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/51",
                            "head": "376a9b3c4e48f45cba9382ff7c8e973e5acfe68a",
                            "qa_result": result,
                        },
                        fh,
                    )
                tasks.append(
                    {
                        "id": task_id,
                        "title": "Vera QA review: BIT-620",
                        "body": "Issue: BIT-620\nPR: https://github.com/BitPod-App/taylor01-mind/pull/51\nHead SHA: 376a9b3c4e48f45cba9382ff7c8e973e5acfe68a",
                        "assignee": "vera",
                        "status": "done",
                        "workspace_path": workspace,
                        "result": f"QA_RESULT={result}",
                    }
                )

            events = collect_vera_qa_completed_events(tasks)

        self.assertEqual([event["qa_result"] for event in events], ["OVERRIDE", "ACTION_REQUIRED"])

    def test_collector_skips_stale_task_when_body_head_differs_from_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-619",
                        "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                        "head": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "qa_result": "PASSED",
                    },
                    fh,
                )

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_stale",
                        "title": "Vera QA review: BIT-619",
                        "body": "Issue: BIT-619\nPR: https://github.com/BitPod-App/taylor01-mind/pull/50\nHead SHA: 22cc449cf586109d4c0f324657032781e880cd75",
                        "assignee": "vera",
                        "status": "done",
                        "workspace_path": tmp,
                        "result": "QA_RESULT=FAILED",
                    }
                ]
            )

        self.assertEqual(events, [])

    def test_collector_finalizes_blocked_vera_task_with_failed_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            reviewed_repo = os.path.join(tmp, "reviewed-repo")
            artifact_workspace = os.path.join(tmp, "qa-artifacts", "BIT-345", "repo", "pr-11", "66bd304")
            os.makedirs(reviewed_repo)
            os.makedirs(artifact_workspace)
            with open(os.path.join(artifact_workspace, "verification_report.md"), "w", encoding="utf-8") as fh:
                fh.write("QA_RESULT=FAILED\n")
            with open(os.path.join(artifact_workspace, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-345",
                        "pr_url": "https://github.com/BitPod-App/bitregime-core/pull/11",
                        "head_sha": "66bd304434b7ec9e9d26aad21c9643dfab52de58",
                        "qa_verdict": "FAILED",
                        "error": "ModuleNotFoundError: No module named 'typer'",
                    },
                    fh,
                )

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_blocked_failed",
                        "title": "Vera QA review: BIT-345",
                        "body": (
                            "Issue: BIT-345\n"
                            "PR: https://github.com/BitPod-App/bitregime-core/pull/11\n"
                            "Head SHA: 66bd304434b7ec9e9d26aad21c9643dfab52de58\n"
                            f"Artifact workspace: {artifact_workspace}"
                        ),
                        "assignee": "vera",
                        "status": "blocked",
                        "workspace_path": reviewed_repo,
                        "result": "",
                        "events": [
                            {
                                "kind": "gave_up",
                                "payload": {"error": "worker exited cleanly without kanban_complete or kanban_block"},
                            }
                        ],
                        "runs": [{"status": "crashed", "error": "PID not alive"}],
                    }
                ]
            )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["task_id"], "t_blocked_failed")
        self.assertEqual(events[0]["issue_key"], "BIT-345")
        self.assertEqual(events[0]["qa_result"], "FAILED")
        self.assertEqual(events[0]["qa_verdict"], "FAILED")
        self.assertEqual(events[0]["pr_url"], "https://github.com/BitPod-App/bitregime-core/pull/11")
        self.assertEqual(events[0]["head_sha"], "66bd304434b7ec9e9d26aad21c9643dfab52de58")
        self.assertIn("blocked", events[0]["summary"])
        self.assertIn("ModuleNotFoundError", events[0]["summary"])

    def test_collector_finalizes_blocked_vera_task_missing_manifest_as_action_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_workspace = os.path.join(tmp, "qa-artifacts", "BIT-345", "repo", "pr-11", "66bd304")
            os.makedirs(artifact_workspace)

            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_blocked_missing_manifest",
                        "title": "Vera QA review: BIT-345",
                        "body": (
                            "Issue: BIT-345\n"
                            "PR: https://github.com/BitPod-App/bitregime-core/pull/11\n"
                            "Head SHA: 66bd304434b7ec9e9d26aad21c9643dfab52de58\n"
                            f"Artifact workspace: {artifact_workspace}"
                        ),
                        "assignee": "vera",
                        "status": "blocked",
                        "workspace_path": tmp,
                        "events": [{"kind": "protocol_violation", "payload": {"error": "missing completion marker"}}],
                    }
                ]
            )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["task_id"], "t_blocked_missing_manifest")
        self.assertEqual(events[0]["issue_key"], "BIT-345")
        self.assertEqual(events[0]["qa_result"], "ACTION_REQUIRED")
        self.assertEqual(events[0]["qa_verdict"], "ACTION_REQUIRED")
        self.assertIn("manifest.json missing", events[0]["summary"])
        self.assertIn("protocol_violation", events[0]["summary"])

    def test_collector_skips_non_terminal_vera_task_without_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = collect_vera_qa_completed_events(
                [
                    {
                        "id": "t_queued",
                        "title": "Vera QA review: BIT-345",
                        "body": (
                            "Issue: BIT-345\n"
                            "PR: https://github.com/BitPod-App/bitregime-core/pull/11\n"
                            "Head SHA: 66bd304434b7ec9e9d26aad21c9643dfab52de58\n"
                            f"Artifact workspace: {tmp}"
                        ),
                        "assignee": "vera",
                        "status": "queued",
                        "workspace_path": tmp,
                    }
                ]
            )

        self.assertEqual(events, [])

    def test_sync_vera_qa_results_once_marks_completed_task_after_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "verification_report.md"), "w", encoding="utf-8") as fh:
                fh.write("QA_RESULT=PASSED\n")
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-619",
                        "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                        "head": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "qa_result": "PASSED",
                    },
                    fh,
                )
            trace = JsonlFileStore(os.path.join(tmp, "trace.jsonl"))
            calls = []

            def fake_apply(actions, dry_run=True, policy=None, linear_executor=None):
                calls.append(actions)
                return [{"outcome": "executed", "kind": a.kind} for a in actions]

            tasks = [
                {
                    "id": "t_sync",
                    "title": "Vera QA review: BIT-619",
                    "body": "Issue: BIT-619\nPR: https://github.com/BitPod-App/taylor01-mind/pull/50\nHead SHA: 1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                    "assignee": "vera",
                    "status": "done",
                    "workspace_path": tmp,
                    "result": "Vera passed.",
                }
            ]

            first = sync_vera_qa_results_once(tasks=tasks, dry_run=False, trace_store=trace, apply_fn=fake_apply)
            second = sync_vera_qa_results_once(tasks=tasks, dry_run=False, trace_store=trace, apply_fn=fake_apply)

        self.assertEqual(first, 1)
        self.assertEqual(second, 0)
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(a.system == "github" and a.kind == "check_run" for a in calls[0]))

    def test_sync_vera_qa_results_once_marks_after_partial_apply_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "verification_report.md"), "w", encoding="utf-8") as fh:
                fh.write("QA_RESULT=PASSED\n")
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-619",
                        "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                        "head": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "qa_result": "PASSED",
                    },
                    fh,
                )
            trace = JsonlFileStore(os.path.join(tmp, "trace.jsonl"))
            calls = []

            def fake_apply(actions, dry_run=True, policy=None, linear_executor=None):
                calls.append(actions)
                return [
                    {"outcome": "blocked", "kind": "comment"},
                    {"outcome": "executed", "kind": "check_run"},
                ]

            tasks = [
                {
                    "id": "t_partial_sync",
                    "title": "Vera QA review: BIT-619",
                    "body": "Issue: BIT-619\nPR: https://github.com/BitPod-App/taylor01-mind/pull/50\nHead SHA: 1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                    "assignee": "vera",
                    "status": "done",
                    "workspace_path": tmp,
                    "result": "Vera passed.",
                }
            ]

            first = sync_vera_qa_results_once(tasks=tasks, dry_run=False, trace_store=trace, apply_fn=fake_apply)
            second = sync_vera_qa_results_once(tasks=tasks, dry_run=False, trace_store=trace, apply_fn=fake_apply)

        self.assertEqual(first, 1)
        self.assertEqual(second, 0)
        self.assertEqual(len(calls), 1)

    def test_sync_vera_qa_results_once_can_filter_to_one_task_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "issue": "BIT-619",
                        "pr_url": "https://github.com/BitPod-App/taylor01-mind/pull/50",
                        "head": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "qa_result": "PASSED",
                    },
                    fh,
                )
            trace = JsonlFileStore(os.path.join(tmp, "trace.jsonl"))
            calls = []

            def fake_apply(actions, dry_run=True, policy=None, linear_executor=None):
                calls.append(actions)
                return [{"outcome": "executed", "kind": a.kind} for a in actions]

            base_task = {
                "title": "Vera QA review: BIT-619",
                "body": "Issue: BIT-619\nPR: https://github.com/BitPod-App/taylor01-mind/pull/50\nHead SHA: 1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                "assignee": "vera",
                "status": "done",
                "workspace_path": tmp,
                "result": "Vera passed.",
            }
            tasks = [dict(base_task, id="t_skip"), dict(base_task, id="t_keep")]

            with patch.dict(os.environ, {"VERA_QA_RESULT_SYNC_TASK_ID": "t_keep"}):
                count = sync_vera_qa_results_once(tasks=tasks, dry_run=False, trace_store=trace, apply_fn=fake_apply)

        self.assertEqual(count, 1)
        self.assertEqual(len(calls), 1)

    def test_vera_qa_task_filter_tolerates_non_numeric_timestamps(self):
        old_after = os.environ.get("VERA_QA_RESULT_SYNC_AFTER_EPOCH")
        os.environ["VERA_QA_RESULT_SYNC_AFTER_EPOCH"] = "100"
        try:
            tasks = _filter_vera_qa_tasks(
                [
                    {
                        "id": "t_iso",
                        "status": "blocked",
                        "created_at": "2026-06-23T22:25:00Z",
                    }
                ]
            )
        finally:
            if old_after is None:
                os.environ.pop("VERA_QA_RESULT_SYNC_AFTER_EPOCH", None)
            else:
                os.environ["VERA_QA_RESULT_SYNC_AFTER_EPOCH"] = old_after

        self.assertEqual([task["id"] for task in tasks], ["t_iso"])

    def test_runtime_can_write_durable_trace_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "trace.jsonl")
            store = JsonlFileStore(path)
            rt = BotRuntime(store=store)
            ev = {
                "action": "opened",
                "pull_request": {
                    "title": "BIT-45 durable test",
                    "body": "",
                    "head": {"ref": "x"},
                    "html_url": "https://github.com/BitPod-App/bitpod-tools/pull/17",
                },
            }
            rt.run_github_event(ev)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(len(store.list_for("BIT-45")), 1)



    def test_github_check_run_updates_existing_same_name_run(self):
        old_enabled = os.environ.get("VERA_QA_GATE_LIVE_ENABLED")
        os.environ["VERA_QA_GATE_LIVE_ENABLED"] = "true"
        calls = []

        def fake_request(method, path, token, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return {"check_runs": [{"id": 123}]}
            if method == "PATCH":
                return {"id": 123}
            raise AssertionError(f"unexpected request: {method} {path}")

        try:
            action = Action(
                "github",
                "check_run",
                "https://github.com/BitPod-App/bitpod-tools/pull/17",
                {
                    "name": "vera-qa-gate",
                    "repo_full_name": "BitPod-App/bitpod-tools",
                    "head_sha": "abc1234",
                    "status": "completed",
                    "conclusion": "success",
                    "title": "Vera QA passed",
                    "summary": "passed",
                },
            )
            with patch("linear.src.service.github_app_installation_token_from_env", return_value="token"), patch(
                "linear.src.service._github_json_request", side_effect=fake_request
            ):
                detail = execute_github_check_run(action)
            self.assertIn("update", detail)
            self.assertEqual(calls[0][0], "GET")
            self.assertEqual(calls[1][0], "PATCH")
            self.assertEqual(calls[1][2]["conclusion"], "success")
        finally:
            if old_enabled is None:
                os.environ.pop("VERA_QA_GATE_LIVE_ENABLED", None)
            else:
                os.environ["VERA_QA_GATE_LIVE_ENABLED"] = old_enabled

    def test_private_key_normalization_repairs_one_line_pem(self):
        raw = (
            "-----BEGIN PRIVATE KEY----- "
            "YWJj ZGVm"
            " -----END PRIVATE KEY-----"
        )

        normalized = _normalize_private_key(raw)

        self.assertIn("-----BEGIN PRIVATE KEY-----\n", normalized)
        self.assertIn("\n-----END PRIVATE KEY-----", normalized)
        self.assertIn("YWJjZGVm", normalized)

    def test_github_installation_token_uses_client_id_as_jwt_issuer_when_available(self):
        seen = {}

        def fake_jwt(issuer, private_key):
            seen["issuer"] = issuer
            seen["private_key"] = private_key
            return "jwt-token"

        def fake_request(method, path, token, body=None):
            seen["request"] = (method, path, token, body)
            return {"token": "ghs_installation_token"}

        with patch.dict(
            os.environ,
            {
                "VERA_QA_GATE_GITHUB_APP_ID": "4007105",
                "VERA_QA_GATE_GITHUB_CLIENT_ID": "Iv23client",
                "VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID": "139088756",
                "VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY": "private-key",
            },
            clear=False,
        ):
            with patch("linear.src.service._github_app_jwt", side_effect=fake_jwt), patch(
                "linear.src.service._github_json_request", side_effect=fake_request
            ):
                token = github_app_installation_token_from_env()

        self.assertEqual(token, "ghs_installation_token")
        self.assertEqual(seen["issuer"], "Iv23client")
        self.assertEqual(seen["private_key"], "private-key")
        self.assertEqual(
            seen["request"],
            ("POST", "/app/installations/139088756/access_tokens", "jwt-token", {}),
        )

    def test_github_webhook_signature_requires_matching_hmac_when_secret_is_set(self):
        import hashlib
        import hmac

        body = b'{"action":"ready_for_review"}'
        secret = "shared webhook secret"
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

        self.assertTrue(_verify_github_webhook_signature(body, f"sha256={digest}", secret))
        self.assertFalse(_verify_github_webhook_signature(body, "sha256=bad", secret))

    def test_github_webhook_secret_accepts_vera_gate_field_name(self):
        old_github = os.environ.get("GITHUB_WEBHOOK_SECRET")
        old_vera = os.environ.get("VERA_QA_GATE_WEBHOOK_SIGNING_SECRET")
        os.environ.pop("GITHUB_WEBHOOK_SECRET", None)
        os.environ["VERA_QA_GATE_WEBHOOK_SIGNING_SECRET"] = "vera-gate-secret"
        try:
            self.assertEqual(_github_webhook_secret_from_env(), "vera-gate-secret")
        finally:
            if old_github is None:
                os.environ.pop("GITHUB_WEBHOOK_SECRET", None)
            else:
                os.environ["GITHUB_WEBHOOK_SECRET"] = old_github
            if old_vera is None:
                os.environ.pop("VERA_QA_GATE_WEBHOOK_SIGNING_SECRET", None)
            else:
                os.environ["VERA_QA_GATE_WEBHOOK_SIGNING_SECRET"] = old_vera

    def test_linear_webhook_signature_requires_matching_hmac_when_secret_is_set(self):
        import hashlib
        import hmac

        body = b'{"type":"Issue","webhookTimestamp":1781300000000}'
        secret = "shared webhook secret"
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

        self.assertTrue(_verify_linear_webhook_signature(body, digest, secret))
        self.assertFalse(_verify_linear_webhook_signature(body, "bad", secret))

    def test_linear_webhook_secret_accepts_vera_gate_field_name(self):
        old_linear = os.environ.get("LINEAR_WEBHOOK_SECRET")
        old_vera_linear = os.environ.get("VERA_QA_GATE_LINEAR_WEBHOOK_SECRET")
        old_vera = os.environ.get("VERA_QA_GATE_WEBHOOK_SIGNING_SECRET")
        os.environ.pop("LINEAR_WEBHOOK_SECRET", None)
        os.environ.pop("VERA_QA_GATE_LINEAR_WEBHOOK_SECRET", None)
        os.environ["VERA_QA_GATE_WEBHOOK_SIGNING_SECRET"] = "vera-gate-secret"
        try:
            self.assertEqual(_linear_webhook_secret_from_env(), "vera-gate-secret")
        finally:
            if old_linear is None:
                os.environ.pop("LINEAR_WEBHOOK_SECRET", None)
            else:
                os.environ["LINEAR_WEBHOOK_SECRET"] = old_linear
            if old_vera_linear is None:
                os.environ.pop("VERA_QA_GATE_LINEAR_WEBHOOK_SECRET", None)
            else:
                os.environ["VERA_QA_GATE_LINEAR_WEBHOOK_SECRET"] = old_vera_linear
            if old_vera is None:
                os.environ.pop("VERA_QA_GATE_WEBHOOK_SIGNING_SECRET", None)
            else:
                os.environ["VERA_QA_GATE_WEBHOOK_SIGNING_SECRET"] = old_vera

    def test_service_blocks_vera_dispatch_without_kill_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = os.path.join(tmp, "service_trace.jsonl")
            old_trace = os.environ.get("TRACE_STORE_PATH")
            old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
            os.environ["TRACE_STORE_PATH"] = trace_path
            os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
            try:
                action = Action(
                    "hermes",
                    "enqueue_vera_qa",
                    "BIT-617",
                    {
                        "title": "Vera QA review: BIT-617",
                        "body": "review this",
                        "assignee": "vera",
                        "idempotency_key": "vera-qa:BIT-617:repo:1:sha",
                    },
                )
                apply_actions([action], dry_run=False, policy=GovernancePolicy.default())
                with open(trace_path, "r", encoding="utf-8") as fh:
                    payload = fh.read()
                self.assertIn('"outcome": "blocked"', payload)
                self.assertIn("VERA_QA_DISPATCH_ENABLED", payload)
            finally:
                if old_trace is None:
                    os.environ.pop("TRACE_STORE_PATH", None)
                else:
                    os.environ["TRACE_STORE_PATH"] = old_trace
                if old_enabled is None:
                    os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
                else:
                    os.environ["VERA_QA_DISPATCH_ENABLED"] = old_enabled

    def test_service_blocks_vera_gate_check_without_kill_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = os.path.join(tmp, "service_trace.jsonl")
            old_trace = os.environ.get("TRACE_STORE_PATH")
            old_enabled = os.environ.get("VERA_QA_GATE_LIVE_ENABLED")
            os.environ["TRACE_STORE_PATH"] = trace_path
            os.environ.pop("VERA_QA_GATE_LIVE_ENABLED", None)
            try:
                action = Action(
                    "github",
                    "check_run",
                    "https://github.com/BitPod-App/bitpod-tools/pull/17",
                    {
                        "name": "vera-qa-gate",
                        "repo_full_name": "BitPod-App/bitpod-tools",
                        "head_sha": "abc1234",
                        "status": "queued",
                        "summary": "queued",
                    },
                )
                apply_actions([action], dry_run=False, policy=GovernancePolicy.default())
                with open(trace_path, "r", encoding="utf-8") as fh:
                    payload = fh.read()
                self.assertIn('"outcome": "blocked"', payload)
                self.assertIn("VERA_QA_GATE_LIVE_ENABLED", payload)
            finally:
                if old_trace is None:
                    os.environ.pop("TRACE_STORE_PATH", None)
                else:
                    os.environ["TRACE_STORE_PATH"] = old_trace
                if old_enabled is None:
                    os.environ.pop("VERA_QA_GATE_LIVE_ENABLED", None)
                else:
                    os.environ["VERA_QA_GATE_LIVE_ENABLED"] = old_enabled

    def test_github_pr_comment_uses_github_app_installation_token_not_gh_cli(self):
        calls = []

        def fake_github_request(method, path, token, body=None):
            calls.append((method, path, token, body))
            return {"id": 123}

        def fake_subprocess_run(*args, **kwargs):
            raise AssertionError("gh CLI should not be used for GitHub PR comments")

        action = Action(
            "github",
            "comment",
            "https://github.com/BitPod-App/taylor01-mind/pull/50",
            {"body": "QA_RESULT=PASSED"},
        )
        with patch("linear.src.service.github_app_installation_token_from_env", return_value="installation-token"):
            with patch("linear.src.service._github_json_request", side_effect=fake_github_request):
                with patch("linear.src.service.subprocess.run", side_effect=fake_subprocess_run):
                    results = apply_actions([action], dry_run=False, policy=GovernancePolicy.default())

        self.assertEqual(results[0]["outcome"], "executed")
        self.assertEqual(calls[0][0], "POST")
        self.assertEqual(calls[0][1], "/repos/BitPod-App/taylor01-mind/issues/50/comments")
        self.assertEqual(calls[0][2], "installation-token")
        self.assertEqual(calls[0][3]["body"], "QA_RESULT=PASSED")

    def test_github_override_enrichment_collects_repo_agnostic_label_actor_head_and_reason(self):
        calls = []

        def fake_github_request(method, path, token, body=None):
            calls.append((method, path, token, body))
            if path == "/repos/BitPod-App/sector-feeds/pulls/77":
                return {
                    "number": 77,
                    "title": "BIT-708 sector override",
                    "body": "",
                    "html_url": "https://github.com/BitPod-App/sector-feeds/pull/77",
                    "head": {"sha": "abc1234"},
                }
            if path == "/repos/BitPod-App/sector-feeds/issues/77":
                return {"labels": [{"name": "QA_OVERRIDE"}]}
            if path == "/repos/BitPod-App/sector-feeds/issues/77/events?per_page=100":
                return [
                    {
                        "event": "labeled",
                        "label": {"name": "QA_OVERRIDE"},
                        "actor": {"login": "cjarguello"},
                        "created_at": "2026-06-23T05:20:30Z",
                    }
                ]
            if path == "/repos/BitPod-App/sector-feeds/pulls/77/commits?per_page=100":
                return [{"commit": {"committer": {"date": "2026-06-23T05:20:00Z"}}}]
            if path == "/repos/BitPod-App/sector-feeds/issues/77/comments?per_page=100":
                return [
                    {
                        "body": "/qa-override CJ accepts advisory QA evidence.",
                        "html_url": "https://github.com/BitPod-App/sector-feeds/pull/77#issuecomment-1",
                        "created_at": "2026-06-23T05:21:00Z",
                        "user": {"login": "cjarguello"},
                    }
                ]
            if path == "/repos/BitPod-App/sector-feeds/pulls/77/reviews?per_page=100":
                return []
            raise AssertionError(f"unexpected path {path}")

        event = {
            "action": "labeled",
            "repository": {"full_name": "BitPod-App/sector-feeds"},
            "sender": {"login": "cjarguello"},
            "label": {"name": "QA_OVERRIDE"},
            "issue": {"number": 77, "title": "BIT-708 sector override", "pull_request": {}},
        }
        with patch("linear.src.service.github_app_installation_token_from_env", return_value="installation-token"):
            with patch("linear.src.service._github_json_request", side_effect=fake_github_request):
                enriched = enrich_github_override_event(event, "issues")

        self.assertEqual(enriched["pull_request"]["head"]["sha"], "abc1234")
        self.assertEqual(enriched["issue"]["labels"][0]["name"], "QA_OVERRIDE")
        self.assertEqual(enriched["override_label_actor"], "cjarguello")
        self.assertEqual(enriched["head_current_at"], "2026-06-23T05:20:00Z")
        self.assertIn("/qa-override", enriched["override_reason"]["body"])
        self.assertEqual(calls[0][1], "/repos/BitPod-App/sector-feeds/pulls/77")

    def test_github_override_detection_accepts_pull_request_labeled_label_event(self):
        self.assertTrue(
            _github_event_may_be_qa_override(
                {"action": "labeled", "label": {"name": "QA_OVERRIDE"}},
                "pull_request",
            )
        )

    def test_runtime_routes_pull_request_labeled_to_cj_qa_override(self):
        rt = BotRuntime()

        actions = rt.run_github_event(
            {
                "_github_event": "pull_request",
                "action": "labeled",
                "sender": {"login": "cjarguello"},
                "label": {"name": "QA_OVERRIDE"},
                "override_label_actor": "cjarguello",
                "head_current_at": "2026-06-23T05:20:00Z",
                "pull_request": {
                    "number": 77,
                    "title": "BIT-708 sector override",
                    "body": "",
                    "html_url": "https://github.com/BitPod-App/sector-feeds/pull/77",
                    "labels": [{"name": "QA_OVERRIDE"}],
                    "head": {"sha": "abc1234"},
                },
                "override_reason": {
                    "source": "comment",
                    "actor": "cjarguello",
                    "reason": "CJ accepts advisory QA evidence.",
                    "body": "/qa-override CJ accepts advisory QA evidence.",
                    "html_url": "https://github.com/BitPod-App/sector-feeds/pull/77#issuecomment-1",
                    "created_at": "2026-06-23T05:21:00Z",
                },
            }
        )

        self.assertTrue(any(a.system == "linear" and a.kind == "set_label" and a.payload["value"] == "qa-override" for a in actions))
        check = next(a for a in actions if a.system == "github" and a.kind == "check_run")
        self.assertEqual(check.payload["conclusion"], "success")

    def test_governance_blocks_live_linear_mutation_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = os.path.join(tmp, "service_trace.jsonl")
            old = os.environ.get("TRACE_STORE_PATH")
            os.environ["TRACE_STORE_PATH"] = trace_path
            try:
                action = Action("linear", "set_status", "BIT-45", {"status": "Done"})
                apply_actions([action], dry_run=False, policy=GovernancePolicy.default())
                with open(trace_path, "r", encoding="utf-8") as fh:
                    payload = fh.read()
                self.assertIn("\"outcome\": \"blocked\"", payload)
                self.assertIn("\"policy_class\": \"B\"", payload)
            finally:
                if old is None:
                    os.environ.pop("TRACE_STORE_PATH", None)
                else:
                    os.environ["TRACE_STORE_PATH"] = old

    def test_governance_allows_exact_guarded_linear_action_allowlist(self):
        old = os.environ.get("LINEAR_GUARDED_ACTION_ALLOWLIST")
        os.environ["LINEAR_GUARDED_ACTION_ALLOWLIST"] = "linear:set_status:BIT-505"
        try:
            action = Action("linear", "set_status", "BIT-505", {"status": "In Review"})
            decision = GovernancePolicy.default().decide(action, dry_run=False)
            self.assertTrue(decision.allowed)
            self.assertEqual(decision.policy_class, "B")
            self.assertIn("guarded action allowlist", decision.reason)
        finally:
            if old is None:
                os.environ.pop("LINEAR_GUARDED_ACTION_ALLOWLIST", None)
            else:
                os.environ["LINEAR_GUARDED_ACTION_ALLOWLIST"] = old

    def test_governance_guarded_allowlist_does_not_expand_to_other_targets(self):
        old = os.environ.get("LINEAR_GUARDED_ACTION_ALLOWLIST")
        os.environ["LINEAR_GUARDED_ACTION_ALLOWLIST"] = "linear:set_status:BIT-505"
        try:
            action = Action("linear", "set_status", "BIT-559", {"status": "In Progress"})
            decision = GovernancePolicy.default().decide(action, dry_run=False)
            self.assertFalse(decision.allowed)
            self.assertEqual(decision.policy_class, "B")
            self.assertIn("requires Taylor approval", decision.reason)
        finally:
            if old is None:
                os.environ.pop("LINEAR_GUARDED_ACTION_ALLOWLIST", None)
            else:
                os.environ["LINEAR_GUARDED_ACTION_ALLOWLIST"] = old

    def test_governance_allows_vera_qa_completed_linear_result_sync_without_per_ticket_allowlist(self):
        policy = GovernancePolicy.default()
        passed_label = Action(
            "linear",
            "set_label",
            "BIT-619",
            {"group": "In Review - QA Gate", "value": "qa-passed", "source_event": "vera_qa_completed"},
        )
        failed_status = Action(
            "linear",
            "set_status",
            "BIT-614",
            {"status": "In Progress", "source_event": "vera_qa_completed"},
        )

        label_decision = policy.decide(passed_label, dry_run=False)
        status_decision = policy.decide(failed_status, dry_run=False)

        self.assertTrue(label_decision.allowed)
        self.assertEqual(label_decision.policy_class, "B")
        self.assertTrue(status_decision.allowed)
        self.assertEqual(status_decision.policy_class, "B")

    def test_governance_allows_vera_override_and_action_required_blocker_sync_without_per_ticket_allowlist(self):
        policy = GovernancePolicy.default()
        override_label = Action(
            "linear",
            "set_label",
            "BIT-620",
            {"group": "In Review - QA Gate", "value": "qa-override", "source_event": "vera_qa_completed"},
        )
        action_required_blocker = Action(
            "linear",
            "set_label",
            "BIT-620",
            {"group": "Blocked By", "value": "needs-discussion", "source_event": "vera_qa_completed"},
        )

        override_decision = policy.decide(override_label, dry_run=False)
        blocker_decision = policy.decide(action_required_blocker, dry_run=False)

        self.assertTrue(override_decision.allowed)
        self.assertEqual(override_decision.policy_class, "B")
        self.assertTrue(blocker_decision.allowed)
        self.assertEqual(blocker_decision.policy_class, "B")

    def test_governance_allows_cj_github_qa_override_label_and_delivered_sync_without_per_ticket_allowlist(self):
        policy = GovernancePolicy.default()
        override_label = Action(
            "linear",
            "set_label",
            "BIT-644",
            {"group": "In Review - QA Gate", "value": "qa-override", "source_event": "github_cj_qa_override"},
        )
        delivered_status = Action(
            "linear",
            "set_status",
            "BIT-644",
            {"status": "Delivered", "source_event": "github_cj_qa_override"},
        )

        label_decision = policy.decide(override_label, dry_run=False)
        status_decision = policy.decide(delivered_status, dry_run=False)

        self.assertTrue(label_decision.allowed)
        self.assertEqual(label_decision.policy_class, "B")
        self.assertTrue(status_decision.allowed)
        self.assertEqual(status_decision.policy_class, "B")

    def test_governance_rejects_cj_github_qa_override_for_non_override_label(self):
        action = Action(
            "linear",
            "set_label",
            "BIT-644",
            {"group": "In Review - QA Gate", "value": "qa-passed", "source_event": "github_cj_qa_override"},
        )

        decision = GovernancePolicy.default().decide(action, dry_run=False)

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.policy_class, "B")

    def test_governance_rejects_non_vera_qa_source_for_same_linear_label_shape(self):
        action = Action(
            "linear",
            "set_label",
            "BIT-619",
            {"group": "In Review - QA Gate", "value": "qa-passed", "source_event": "manual"},
        )

        decision = GovernancePolicy.default().decide(action, dry_run=False)

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.policy_class, "B")

    def test_result_sync_list_uses_configured_hermes_cli_path_under_launchd_path(self):
        old_cli = os.environ.get("HERMES_CLI_PATH")
        os.environ["HERMES_CLI_PATH"] = "/tmp/bitpod-hermes-cli"
        calls = []

        def fake_run(cmd, stdout=None, stderr=None, text=None, check=None):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout="[]", stderr="")

        try:
            with patch("linear.src.service.subprocess.run", side_effect=fake_run):
                tasks = load_completed_vera_qa_tasks()
        finally:
            if old_cli is None:
                os.environ.pop("HERMES_CLI_PATH", None)
            else:
                os.environ["HERMES_CLI_PATH"] = old_cli

        self.assertEqual(tasks, [])
        self.assertEqual(calls[0][0], "/tmp/bitpod-hermes-cli")
        self.assertNotIn("--status", calls[0])
        self.assertIn("--json", calls[0])

    def test_vera_dispatch_uses_configured_hermes_cli_path_under_launchd_path(self):
        old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
        old_cli = os.environ.get("HERMES_CLI_PATH")
        os.environ["VERA_QA_DISPATCH_ENABLED"] = "true"
        os.environ["HERMES_CLI_PATH"] = "/tmp/bitpod-hermes-cli"
        calls = []

        def fake_run(cmd, stdout=None, stderr=None, text=None, check=None):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout='{ "id": "t_1" }', stderr="")

        try:
            action = Action("hermes", "enqueue_vera_qa", "BIT-617", {"idempotency_key": "vera-qa:BIT-617"})
            with patch("linear.src.service.subprocess.run", side_effect=fake_run):
                execute_hermes_vera_dispatch(action)
        finally:
            if old_enabled is None:
                os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
            else:
                os.environ["VERA_QA_DISPATCH_ENABLED"] = old_enabled
            if old_cli is None:
                os.environ.pop("HERMES_CLI_PATH", None)
            else:
                os.environ["HERMES_CLI_PATH"] = old_cli

        self.assertEqual(calls[0][0], "/tmp/bitpod-hermes-cli")

    def test_vera_dispatch_uses_repo_workspace_map_and_external_artifact_workspace(self):
        old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
        old_map = os.environ.get("VERA_QA_KANBAN_WORKSPACE_MAP")
        old_workspace = os.environ.get("VERA_QA_KANBAN_WORKSPACE")
        old_artifact_root = os.environ.get("VERA_QA_ARTIFACT_ROOT")
        calls = []

        def fake_run(cmd, stdout=None, stderr=None, text=None, check=None):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout='{"id":"t_1"}', stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            reviewed_repo = os.path.join(tmp, "reviewed-repo")
            artifact_root = os.path.join(tmp, "qa-artifacts")
            os.makedirs(reviewed_repo)
            try:
                os.environ["VERA_QA_DISPATCH_ENABLED"] = "true"
                os.environ["VERA_QA_ARTIFACT_ROOT"] = artifact_root
                os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = json.dumps(
                    {"BitPod-App/taylor01-mind": reviewed_repo}
                )
                os.environ.pop("VERA_QA_KANBAN_WORKSPACE", None)
                action = Action(
                    "hermes",
                    "enqueue_vera_qa",
                    "BIT-619",
                    {
                        "issue_key": "BIT-619",
                        "repo_full_name": "BitPod-App/taylor01-mind",
                        "pr_number": "50",
                        "head_sha": "1a1fb4e8ba14e7374c18740b655148e34579cc2c",
                        "idempotency_key": "vera-qa:BIT-619:BitPod-App/taylor01-mind:50:sha",
                    },
                )
                with patch("linear.src.service.subprocess.run", side_effect=fake_run):
                    execute_hermes_vera_dispatch(action)
            finally:
                if old_enabled is None:
                    os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
                else:
                    os.environ["VERA_QA_DISPATCH_ENABLED"] = old_enabled
                if old_map is None:
                    os.environ.pop("VERA_QA_KANBAN_WORKSPACE_MAP", None)
                else:
                    os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = old_map
                if old_workspace is None:
                    os.environ.pop("VERA_QA_KANBAN_WORKSPACE", None)
                else:
                    os.environ["VERA_QA_KANBAN_WORKSPACE"] = old_workspace
                if old_artifact_root is None:
                    os.environ.pop("VERA_QA_ARTIFACT_ROOT", None)
                else:
                    os.environ["VERA_QA_ARTIFACT_ROOT"] = old_artifact_root

            body = calls[0][calls[0].index("--body") + 1]
            artifact_line = next(line for line in body.splitlines() if line.startswith("Artifact workspace: "))
            artifact_workspace = artifact_line.split(": ", 1)[1]

            self.assertEqual(calls[0][calls[0].index("--workspace") + 1], reviewed_repo)
            self.assertTrue(artifact_workspace.startswith(artifact_root))
            self.assertFalse(artifact_workspace.startswith(reviewed_repo))
            self.assertTrue(os.path.isdir(artifact_workspace))
            self.assertIn("Do not create or modify verification_report.md or manifest.json in the reviewed repo workspace.", body)

    def test_vera_dispatch_fails_closed_when_artifact_root_is_inside_reviewed_repo(self):
        old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
        old_map = os.environ.get("VERA_QA_KANBAN_WORKSPACE_MAP")
        old_artifact_root = os.environ.get("VERA_QA_ARTIFACT_ROOT")
        with tempfile.TemporaryDirectory() as tmp:
            reviewed_repo = os.path.join(tmp, "reviewed-repo")
            os.makedirs(reviewed_repo)
            try:
                os.environ["VERA_QA_DISPATCH_ENABLED"] = "true"
                os.environ["VERA_QA_ARTIFACT_ROOT"] = os.path.join(reviewed_repo, "qa-artifacts")
                os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = json.dumps(
                    {"BitPod-App/taylor01-mind": reviewed_repo}
                )
                action = Action(
                    "hermes",
                    "enqueue_vera_qa",
                    "BIT-631",
                    {
                        "issue_key": "BIT-631",
                        "repo_full_name": "BitPod-App/taylor01-mind",
                        "pr_number": "44",
                        "head_sha": "abc123",
                    },
                )
                with self.assertRaisesRegex(RuntimeError, "artifact workspace resolves inside reviewed repo workspace"):
                    execute_hermes_vera_dispatch(action)
            finally:
                if old_enabled is None:
                    os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
                else:
                    os.environ["VERA_QA_DISPATCH_ENABLED"] = old_enabled
                if old_map is None:
                    os.environ.pop("VERA_QA_KANBAN_WORKSPACE_MAP", None)
                else:
                    os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = old_map
                if old_artifact_root is None:
                    os.environ.pop("VERA_QA_ARTIFACT_ROOT", None)
                else:
                    os.environ["VERA_QA_ARTIFACT_ROOT"] = old_artifact_root

    def test_vera_dispatch_fails_closed_when_artifact_root_inside_worktree_reviewed_repo(self):
        # Regression for BIT-631: the workspace map uses a "worktree:" scheme in
        # production. The containment guard must strip the scheme and still fail
        # closed when VERA_QA_ARTIFACT_ROOT resolves inside the reviewed repo.
        old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
        old_map = os.environ.get("VERA_QA_KANBAN_WORKSPACE_MAP")
        old_artifact_root = os.environ.get("VERA_QA_ARTIFACT_ROOT")
        with tempfile.TemporaryDirectory() as tmp:
            reviewed_repo = os.path.join(tmp, "reviewed-repo")
            os.makedirs(reviewed_repo)
            try:
                os.environ["VERA_QA_DISPATCH_ENABLED"] = "true"
                os.environ["VERA_QA_ARTIFACT_ROOT"] = os.path.join(reviewed_repo, "qa-artifacts")
                os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = json.dumps(
                    {"BitPod-App/taylor01-mind": f"worktree:{reviewed_repo}"}
                )
                action = Action(
                    "hermes",
                    "enqueue_vera_qa",
                    "BIT-631",
                    {
                        "issue_key": "BIT-631",
                        "repo_full_name": "BitPod-App/taylor01-mind",
                        "pr_number": "44",
                        "head_sha": "abc123",
                    },
                )
                with self.assertRaisesRegex(RuntimeError, "artifact workspace resolves inside reviewed repo workspace"):
                    execute_hermes_vera_dispatch(action)
            finally:
                if old_enabled is None:
                    os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
                else:
                    os.environ["VERA_QA_DISPATCH_ENABLED"] = old_enabled
                if old_map is None:
                    os.environ.pop("VERA_QA_KANBAN_WORKSPACE_MAP", None)
                else:
                    os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = old_map
                if old_artifact_root is None:
                    os.environ.pop("VERA_QA_ARTIFACT_ROOT", None)
                else:
                    os.environ["VERA_QA_ARTIFACT_ROOT"] = old_artifact_root

    def test_vera_dispatch_workspace_map_fails_closed_for_unmapped_repo(self):
        old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
        old_map = os.environ.get("VERA_QA_KANBAN_WORKSPACE_MAP")
        os.environ["VERA_QA_DISPATCH_ENABLED"] = "true"
        os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = json.dumps(
            {"BitPod-App/taylor01-mind": "worktree:/Users/taylor01/BitPod-App/taylor01-mind"}
        )
        try:
            action = Action("hermes", "enqueue_vera_qa", "BIT-617", {"repo_full_name": "BitPod-App/bitpod-tools"})
            with self.assertRaises(RuntimeError) as ctx:
                execute_hermes_vera_dispatch(action)
        finally:
            if old_enabled is None:
                os.environ.pop("VERA_QA_DISPATCH_ENABLED", None)
            else:
                os.environ["VERA_QA_DISPATCH_ENABLED"] = old_enabled
            if old_map is None:
                os.environ.pop("VERA_QA_KANBAN_WORKSPACE_MAP", None)
            else:
                os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = old_map

        self.assertIn("missing Vera QA workspace mapping", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
