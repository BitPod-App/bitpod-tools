import os
import tempfile
import unittest
from unittest.mock import patch

from linear.src.engine import Action
from linear.src.governance import GovernancePolicy
from linear.src.linear_executor import (
    LinearActorWrong,
    LinearExecutionError,
    LinearExecutor,
    LinearExecutorConfig,
)
from linear.src.service import apply_actions


class FakeLinearTransport:
    def __init__(self, viewer=None):
        self.viewer = viewer or {"id": "actor-1", "name": "BitPod Linear Bot", "email": "bot@example.com"}
        self.calls = []
        self.last_variables = {}

    def __call__(self, query, variables):
        self.calls.append(query)
        self.last_variables = variables
        if "LinearExecutorViewer" in query:
            return {"data": {"viewer": self.viewer}}
        if "query LinearExecutorIssue(" in query:
            return {
                "data": {
                    "issue": {
                        "id": "issue-uuid",
                        "identifier": variables["id"],
                        "team": {"id": "team-1", "key": "BIT", "name": "Product Development"},
                        "state": {"id": "state-old", "name": "Backlog"},
                        "labels": {"nodes": [{"id": "label-existing", "name": "Feature", "parent": None}]},
                    }
                }
            }
        if "LinearExecutorCommentCreate" in query:
            return {
                "data": {
                    "commentCreate": {
                        "success": True,
                        "comment": {"id": "comment-1", "url": "https://linear/comment/1", "user": self.viewer},
                    }
                }
            }
        if "LinearExecutorWorkflowStates" in query:
            return {
                "data": {
                    "workflowStates": {
                        "nodes": [
                            {"id": "state-new", "name": "In Progress", "team": {"id": "team-1", "key": "BIT", "name": "Product Development"}},
                            {"id": "other-state", "name": "In Progress", "team": {"id": "team-2", "key": "OPS", "name": "Ops"}},
                        ]
                    }
                }
            }
        if "LinearExecutorIssueSetStatus" in query:
            return {"data": {"issueUpdate": {"success": True, "issue": {"id": "issue-uuid", "identifier": "BIT-505", "state": {"id": "state-new", "name": "In Progress"}}}}}
        if "LinearExecutorIssueLabels" in query:
            return {
                "data": {
                    "issueLabels": {
                        "nodes": [
                            {"id": "label-target", "name": "qa-passed", "team": {"id": "team-1", "key": "BIT"}, "parent": {"id": "parent-1", "name": "In Review - QA Gate"}},
                            {"id": "wrong-team", "name": "qa-passed", "team": {"id": "team-2", "key": "OPS"}, "parent": {"id": "parent-2", "name": "In Review - QA Gate"}},
                        ]
                    }
                }
            }
        if "LinearExecutorIssueSetLabel" in query:
            return {"data": {"issueUpdate": {"success": True, "issue": {"id": "issue-uuid", "identifier": "BIT-559", "labels": {"nodes": []}}}}}
        raise AssertionError(query)


def enabled_config(**overrides):
    base = {
        "enabled": True,
        "api_key": "",
        "oauth_access_token": "",
        "oauth_client_id": "",
        "oauth_client_secret": "",
        "expected_actor_id": "actor-1",
        "expected_actor_name": "",
        "expected_actor_email": "",
    }
    base.update(overrides)
    return LinearExecutorConfig(**base)


class LinearExecutorTests(unittest.TestCase):
    def test_config_supports_oauth_bearer_token_from_env(self):
        with patch.dict(
            os.environ,
            {
                "LINEAR_LIVE_EXECUTOR_ENABLED": "true",
                "LINEAR_OAUTH_ACCESS_TOKEN": "oauth-token",
                "LINEAR_EXPECTED_ACTOR_ID": "actor-1",
            },
            clear=False,
        ):
            config = LinearExecutorConfig.from_env()

        self.assertEqual(config.oauth_access_token, "oauth-token")
        executor = LinearExecutor(config, transport=FakeLinearTransport())
        self.assertEqual(executor._authorization_header(), "Bearer oauth-token")

    def test_config_supports_client_credentials_from_env(self):
        with patch.dict(
            os.environ,
            {
                "LINEAR_LIVE_EXECUTOR_ENABLED": "true",
                "LINEAR_OAUTH_CLIENT_ID": "client-id",
                "LINEAR_OAUTH_CLIENT_SECRET": "client-secret",
                "LINEAR_EXPECTED_ACTOR_ID": "actor-1",
            },
            clear=False,
        ):
            config = LinearExecutorConfig.from_env()

        self.assertEqual(config.oauth_client_id, "client-id")
        self.assertEqual(config.oauth_client_secret, "client-secret")
        executor = LinearExecutor(config, transport=FakeLinearTransport())
        with patch.object(executor, "_fetch_client_credentials_access_token", return_value=("minted-token", 2591999)):
            self.assertEqual(executor._authorization_header(), "Bearer minted-token")

    def test_kill_switch_blocks_live_linear_comment(self):
        executor = LinearExecutor(LinearExecutorConfig(enabled=False), transport=FakeLinearTransport())
        with self.assertRaises(LinearExecutionError) as ctx:
            executor.execute(Action("linear", "comment", "BIT-505", {"body": "rollout note"}))
        self.assertIn("kill switch is off", str(ctx.exception))

    def test_actor_mismatch_reports_linear_actor_wrong(self):
        executor = LinearExecutor(
            enabled_config(expected_actor_id="expected-actor"),
            transport=FakeLinearTransport(viewer={"id": "cj-user", "name": "CJ", "email": "cj@example.com"}),
        )
        with self.assertRaises(LinearActorWrong) as ctx:
            executor.execute(Action("linear", "comment", "BIT-505", {"body": "rollout note"}))
        self.assertIn("LINEAR ACTOR WRONG", str(ctx.exception))

    def test_missing_actor_expectation_fails_closed(self):
        executor = LinearExecutor(
            enabled_config(expected_actor_id="", expected_actor_name="", expected_actor_email=""),
            transport=FakeLinearTransport(),
        )
        with self.assertRaises(LinearExecutionError) as ctx:
            executor.execute(Action("linear", "comment", "BIT-505", {"body": "rollout note"}))
        self.assertIn("actor attribution check is not configured", str(ctx.exception))

    def test_comment_create_supported(self):
        executor = LinearExecutor(enabled_config(), transport=FakeLinearTransport())
        result = executor.execute(Action("linear", "comment", "BIT-505", {"body": "rollout note"}))
        self.assertEqual(result.outcome, "executed")
        self.assertIn("commentCreate BIT-505", result.detail)

    def test_set_status_supported_by_executor(self):
        transport = FakeLinearTransport()
        executor = LinearExecutor(enabled_config(), transport=transport)
        result = executor.execute(Action("linear", "set_status", "BIT-505", {"status": "In Progress"}))
        self.assertEqual(result.outcome, "executed")
        self.assertIn("status BIT-505 -> In Progress", result.detail)
        self.assertEqual(transport.last_variables, {"id": "issue-uuid", "stateId": "state-new"})

    def test_set_label_supported_by_executor_and_preserves_existing_labels(self):
        transport = FakeLinearTransport()
        executor = LinearExecutor(enabled_config(), transport=transport)
        result = executor.execute(Action("linear", "set_label", "BIT-559", {"group": "In Review - QA Gate", "value": "qa-passed"}))
        self.assertEqual(result.outcome, "executed")
        self.assertIn("label BIT-559 += In Review - QA Gate/qa-passed", result.detail)
        self.assertEqual(transport.last_variables, {"id": "issue-uuid", "labelIds": ["label-existing", "label-target"]})

    def test_unsupported_linear_action_fails_closed(self):
        executor = LinearExecutor(enabled_config(), transport=FakeLinearTransport())
        with self.assertRaises(LinearExecutionError) as ctx:
            executor.execute(Action("linear", "delete", "BIT-505", {}))
        self.assertIn("unsupported linear action", str(ctx.exception))

    def test_service_traces_kill_switch_block_for_governance_allowed_comment(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = os.path.join(tmp, "service_trace.jsonl")
            old = os.environ.get("TRACE_STORE_PATH")
            os.environ["TRACE_STORE_PATH"] = trace_path
            try:
                action = Action("linear", "comment", "BIT-505", {"body": "rollout note"})
                apply_actions([action], dry_run=False, policy=GovernancePolicy.default())
                with open(trace_path, "r", encoding="utf-8") as fh:
                    payload = fh.read()
                self.assertIn('"outcome": "blocked"', payload)
                self.assertIn("kill switch is off", payload)
                self.assertIn('"policy_class": "A"', payload)
            finally:
                if old is None:
                    os.environ.pop("TRACE_STORE_PATH", None)
                else:
                    os.environ["TRACE_STORE_PATH"] = old


if __name__ == "__main__":
    unittest.main()
