import os
import tempfile
import unittest
from unittest.mock import patch

from linear.src.engine import Action
from linear.src.governance import GovernancePolicy
from linear.src.runtime import BotRuntime
from linear.src.memory import InMemoryStore, JsonlFileStore
from linear.src.service import apply_actions, execute_github_check_run, _normalize_private_key


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


if __name__ == "__main__":
    unittest.main()
