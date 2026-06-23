import os
import json
import hmac
import hashlib
import unittest

from linear.src.service import custom_agent_actions, is_custom_agent_event, verify_linear_webhook_request

from linear.src.custom_agent_receiver import (
    ACK_DEADLINE_SECONDS,
    FIRST_ACTIVITY_DEADLINE_SECONDS,
    LOCAL_DISPATCH_FLAG,
    PEER_ENABLED_ENV_PREFIX,
    REQUIRED_OAUTH_SCOPES,
    SHARED_RECEIVER_PATH,
    ReceiverConfig,
    ReceiverConfigError,
    ReceiverRequest,
    PeerConfig,
    build_mention_delegate_canaries,
    plan_receiver_decision,
    verify_linear_signature,
)


class CustomAgentReceiverTests(unittest.TestCase):
    def test_default_receiver_is_fail_closed_until_local_gate_enabled(self):
        old = os.environ.get(LOCAL_DISPATCH_FLAG)
        os.environ.pop(LOCAL_DISPATCH_FLAG, None)
        try:
            decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-599"))
            self.assertFalse(decision.accepted)
            self.assertFalse(decision.dispatch_allowed)
            self.assertFalse(decision.cloud_job_allowed)
            self.assertIn(LOCAL_DISPATCH_FLAG, decision.reason)
        finally:
            if old is not None:
                os.environ[LOCAL_DISPATCH_FLAG] = old

    def test_codex_route_accepts_only_when_local_gate_enabled(self):
        config = ReceiverConfig(
            peers={"codex": PeerConfig("codex", local_command=("codex", "exec"))},
            local_dispatch_enabled=True,
        )
        decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-599", session_id="session-1"), config)

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.peer_id, "codex")
        self.assertTrue(decision.dispatch_allowed)
        self.assertFalse(decision.cloud_job_allowed)
        self.assertEqual(decision.local_command, ("codex", "exec"))
        self.assertEqual(decision.ack_deadline_seconds, ACK_DEADLINE_SECONDS)
        self.assertEqual(decision.first_activity_deadline_seconds, FIRST_ACTIVITY_DEADLINE_SECONDS)
        self.assertEqual(decision.oauth_scopes, REQUIRED_OAUTH_SCOPES)
        self.assertEqual(decision.first_activity["system"], "linear")
        self.assertEqual(decision.first_activity["kind"], "agent_activity")
        self.assertEqual(decision.first_activity["target"], "session-1")
        self.assertEqual(decision.first_activity["content_type"], "thought")

    def test_claude_route_is_per_peer_configured(self):
        config = ReceiverConfig(
            peers={"claude": PeerConfig("claude", enabled=True, local_command=("claude", "--print"))},
            local_dispatch_enabled=True,
        )
        decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-560", peer_id="claude", session_id="session-claude"), config)

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.peer_id, "claude")
        self.assertEqual(decision.local_command, ("claude", "--print"))
        self.assertEqual(decision.receiver_path, SHARED_RECEIVER_PATH)
        self.assertEqual(decision.dispatch_surface, "local-receiver")
        self.assertFalse(decision.cloud_job_allowed)

    def test_default_config_can_enable_claude_actor_from_env(self):
        env = {
            LOCAL_DISPATCH_FLAG: "true",
            f"{PEER_ENABLED_ENV_PREFIX}_CLAUDE_ENABLED": "true",
            f"{PEER_ENABLED_ENV_PREFIX}_CLAUDE_COMMAND": "claude --print",
        }
        old = {key: os.environ.get(key) for key in env}
        try:
            os.environ.update(env)
            decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-560", peer_id="claude", session_id="session-claude"))
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.peer_id, "claude")
        self.assertEqual(decision.local_command, ("claude", "--print"))
        self.assertEqual(decision.receiver_path, SHARED_RECEIVER_PATH)
        self.assertFalse(decision.cloud_job_allowed)

    def test_gpt_route_is_not_supported(self):
        with self.assertRaises(ReceiverConfigError):
            PeerConfig("gpt")

        config = ReceiverConfig(peers={"codex": PeerConfig("codex")}, local_dispatch_enabled=True)
        decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-599", peer_id="gpt"), config)
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.dispatch_allowed)
        self.assertFalse(decision.cloud_job_allowed)
        self.assertEqual(decision.reason, "unsupported peer route")

    def test_required_oauth_scopes_are_explicit(self):
        self.assertEqual(REQUIRED_OAUTH_SCOPES, ("read", "write", "app:assignable", "app:mentionable"))

        config = ReceiverConfig(
            peers={"codex": PeerConfig("codex")},
            local_dispatch_enabled=True,
            oauth_scopes=("read", "write", "app:assignable"),
        )
        decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-599"), config)

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.reason, "missing required OAuth scopes")

    def test_claude_mention_and_delegate_canaries_share_receiver_without_cloud_jobs(self):
        config = ReceiverConfig(
            peers={"claude": PeerConfig("claude", enabled=True)},
            local_dispatch_enabled=True,
        )
        canaries = build_mention_delegate_canaries(issue_key="BIT-560", peer_id="claude")

        self.assertEqual([request.payload["trigger"] for request in canaries], ["mention", "delegate"])
        for request in canaries:
            request = ReceiverRequest(
                issue_key=request.issue_key,
                peer_id=request.peer_id,
                session_id=f"session-{request.payload['trigger']}",
                payload=request.payload,
            )
            decision = plan_receiver_decision(request, config)
            self.assertTrue(decision.accepted)
            self.assertEqual(decision.peer_id, "claude")
            self.assertEqual(decision.receiver_path, SHARED_RECEIVER_PATH)
            self.assertEqual(decision.dispatch_surface, "local-receiver")
            self.assertFalse(decision.cloud_job_allowed)
            self.assertNotIn("@", decision.first_activity["body"])

    def test_agent_session_payload_detection_accepts_linear_created_shape(self):
        self.assertTrue(is_custom_agent_event({"type": "created", "agentSession": {"id": "session-1"}}))

    def test_non_agent_linear_comment_payload_does_not_dispatch_custom_agent(self):
        self.assertFalse(is_custom_agent_event({"type": "comment_created", "comment_body": "ordinary update"}))
        self.assertFalse(is_custom_agent_event({"type": "issue_status_changed", "issue_key": "BIT-599"}))

    def test_service_maps_claude_agent_session_to_same_receiver_activity_action(self):
        config = ReceiverConfig(
            peers={"claude": PeerConfig("claude", enabled=True)},
            local_dispatch_enabled=True,
        )
        event = {
            "type": "agent_session.created",
            "peer_id": "claude",
            "agentSession": {
                "id": "session-1",
                "appUserId": "app-user-1",
                "issue": {"identifier": "BIT-560"},
            },
        }

        decision, actions = custom_agent_actions(event, config)

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.peer_id, "claude")
        self.assertEqual(decision.session_id, "session-1")
        self.assertEqual(decision.app_actor_id, "app-user-1")
        self.assertEqual(decision.receiver_path, SHARED_RECEIVER_PATH)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].system, "linear")
        self.assertEqual(actions[0].kind, "agent_activity")
        self.assertEqual(actions[0].target, "session-1")
        self.assertEqual(actions[0].payload["content"]["type"], "thought")
        self.assertFalse(decision.cloud_job_allowed)
        self.assertNotIn("@", actions[0].payload["content"]["body"])

    def test_ack_payload_never_promises_cloud_job(self):
        config = ReceiverConfig(peers={"codex": PeerConfig("codex")}, local_dispatch_enabled=True)
        payload = plan_receiver_decision(ReceiverRequest(issue_key="BIT-599", session_id="session-1"), config).ack_payload()

        self.assertEqual(payload["ack_deadline_seconds"], 5)
        self.assertEqual(payload["first_activity_deadline_seconds"], 10)
        self.assertFalse(payload["cloud_job_allowed"])
        self.assertNotIn("local_command", payload)

    def test_acceptance_requires_agent_session_id_for_first_activity(self):
        config = ReceiverConfig(peers={"codex": PeerConfig("codex")}, local_dispatch_enabled=True)
        decision = plan_receiver_decision(ReceiverRequest(issue_key="BIT-599"), config)

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.reason, "missing AgentSession id")

    def test_linear_signature_accepts_raw_body_hmac_and_current_timestamp(self):
        body = json.dumps({"webhookTimestamp": 1_700_000_000_000, "type": "agent_session.created"}).encode()
        secret = "test-signing-secret"
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        result = verify_linear_signature(
            raw_body=body,
            header_signature=signature,
            signing_secret=secret,
            now_ms=1_700_000_030_000,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.reason, "signature verified")

    def test_linear_signature_rejects_missing_or_invalid_signature_without_secret_leak(self):
        body = json.dumps({"webhookTimestamp": 1_700_000_000_000}).encode()
        secret = "never-print-this-secret"

        missing = verify_linear_signature(
            raw_body=body,
            header_signature="",
            signing_secret=secret,
            now_ms=1_700_000_000_000,
        )
        invalid = verify_linear_signature(
            raw_body=body,
            header_signature="00",
            signing_secret=secret,
            now_ms=1_700_000_000_000,
        )

        self.assertFalse(missing.ok)
        self.assertFalse(invalid.ok)
        self.assertNotIn(secret, missing.reason)
        self.assertNotIn(secret, invalid.reason)

    def test_linear_signature_rejects_stale_agent_session_timestamp(self):
        body = json.dumps({"webhookTimestamp": 1_700_000_000_000}).encode()
        secret = "test-signing-secret"
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        result = verify_linear_signature(
            raw_body=body,
            header_signature=signature,
            signing_secret=secret,
            now_ms=1_700_000_061_000,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "stale webhook timestamp")

    def test_service_webhook_verification_uses_linear_signature_header_fail_closed(self):
        body = json.dumps({"webhookTimestamp": 1_700_000_000_000}).encode()
        secret = "service-signing-secret"
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        ok = verify_linear_webhook_request(
            raw_body=body,
            headers={"Linear-Signature": signature},
            signing_secret=secret,
            now_ms=1_700_000_000_000,
        )
        missing = verify_linear_webhook_request(
            raw_body=body,
            headers={},
            signing_secret=secret,
            now_ms=1_700_000_000_000,
        )

        self.assertTrue(ok.ok)
        self.assertFalse(missing.ok)
        self.assertEqual(missing.status_code, 401)


if __name__ == "__main__":
    unittest.main()
