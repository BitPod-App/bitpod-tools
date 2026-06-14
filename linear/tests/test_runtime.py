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
    sync_vera_qa_results_once,
    _github_webhook_secret_from_env,
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
                        "title": "Vera QA re-review: BIT-619 / PR #50",
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

    def test_vera_dispatch_uses_repo_workspace_map(self):
        old_enabled = os.environ.get("VERA_QA_DISPATCH_ENABLED")
        old_map = os.environ.get("VERA_QA_KANBAN_WORKSPACE_MAP")
        old_workspace = os.environ.get("VERA_QA_KANBAN_WORKSPACE")
        os.environ["VERA_QA_DISPATCH_ENABLED"] = "true"
        os.environ["VERA_QA_KANBAN_WORKSPACE_MAP"] = json.dumps(
            {"BitPod-App/taylor01-mind": "worktree:/Users/taylor01/BitPod-App/taylor01-mind"}
        )
        os.environ.pop("VERA_QA_KANBAN_WORKSPACE", None)
        calls = []

        def fake_run(cmd, stdout=None, stderr=None, text=None, check=None):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout='{"id":"t_1"}', stderr="")

        try:
            action = Action(
                "hermes",
                "enqueue_vera_qa",
                "BIT-619",
                {"repo_full_name": "BitPod-App/taylor01-mind", "idempotency_key": "vera-qa:BIT-619:sha"},
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

        self.assertEqual(calls[0][calls[0].index("--workspace") + 1], "worktree:/Users/taylor01/BitPod-App/taylor01-mind")

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
