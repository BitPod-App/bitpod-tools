import json
import subprocess
import sys
import unittest
from pathlib import Path

from linear.src.custom_agent_receiver import ReceiverConfig, PeerConfig
from linear.src.actor_canary import (
    ActorCanarySpec,
    REQUIRED_ACTOR_SCOPES,
    build_default_actor_canary_specs,
    run_actor_canary_suite,
)


class ActorCanaryTests(unittest.TestCase):
    def test_default_taylor_vera_codex_claude_specs_pass_in_inert_receiver_mode(self):
        report = run_actor_canary_suite(
            specs=build_default_actor_canary_specs(),
            issue_key="BIT-600",
            receiver_config=ReceiverConfig(
                peers={
                    "codex": PeerConfig("codex", enabled=True),
                    "claude": PeerConfig("claude", enabled=True),
                },
                local_dispatch_enabled=True,
            ),
        )

        self.assertTrue(report.ok, report.to_markdown())
        self.assertEqual([result.actor_id for result in report.actor_results], ["taylor", "vera", "codex", "claude"])
        self.assertEqual(report.gpt_result.actor_id, "gpt")
        self.assertTrue(report.gpt_result.ok)
        self.assertIn("no actor path", report.gpt_result.checks[0].detail)
        for result in report.actor_results:
            check_names = {check.name for check in result.checks}
            self.assertIn("actor identity", check_names)
            self.assertIn("required OAuth scopes", check_names)
            self.assertIn("assignable", check_names)
            self.assertIn("mentionable", check_names)
            self.assertIn("comment attribution", check_names)
            self.assertIn("no cloud job", check_names)
            self.assertIn("no generated actor mention", check_names)
        receiver_results = {result.actor_id: result for result in report.actor_results if result.route == "custom-agent-receiver"}
        self.assertEqual(set(receiver_results), {"codex", "claude"})
        for result in receiver_results.values():
            self.assertIn("local receiver route", {check.name for check in result.checks})

    def test_actor_canary_fails_missing_assignable_scope(self):
        spec = ActorCanarySpec(
            actor_id="codex",
            display_name="codex [Agent]",
            actor_type="app",
            oauth_scopes=("read", "write", "app:mentionable"),
            assignable=True,
            mentionable=True,
            attribution_expected="codex [Agent]",
            route="custom-agent-receiver",
            receiver_peer_id="codex",
            cloud_job_allowed=False,
        )

        report = run_actor_canary_suite(
            specs=(spec,),
            issue_key="BIT-600",
            receiver_config=ReceiverConfig(
                peers={"codex": PeerConfig("codex", enabled=True)},
                local_dispatch_enabled=True,
            ),
        )

        self.assertFalse(report.ok)
        failed = [check for check in report.actor_results[0].checks if not check.ok]
        self.assertEqual(failed[0].name, "required OAuth scopes")
        self.assertIn("app:assignable", failed[0].detail)

    def test_actor_canary_fails_human_attribution_and_actor_mentions(self):
        spec = ActorCanarySpec(
            actor_id="vera",
            display_name="vera [Agent]",
            actor_type="app",
            oauth_scopes=REQUIRED_ACTOR_SCOPES,
            assignable=True,
            mentionable=True,
            attribution_expected="CJ",
            route="app-actor",
            cloud_job_allowed=False,
            generated_activity_bodies=("Please handle @Vera on BIT-600",),
        )

        report = run_actor_canary_suite(specs=(spec,), issue_key="BIT-600")

        self.assertFalse(report.ok)
        failures = {check.name: check.detail for check in report.actor_results[0].checks if not check.ok}
        self.assertIn("comment attribution", failures)
        self.assertIn("not app/agent attribution", failures["comment attribution"])
        self.assertIn("no generated actor mention", failures)
        self.assertIn("@Vera", failures["no generated actor mention"])

    def test_gpt_actor_path_is_a_canary_failure(self):
        report = run_actor_canary_suite(
            specs=(),
            gpt_actor_path_enabled=True,
        )

        self.assertFalse(report.ok)
        self.assertFalse(report.gpt_result.ok)
        self.assertIn("must remain disabled", report.gpt_result.checks[0].detail)

    def test_cli_emits_secretless_json_report(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_actor_canary.py"
        result = subprocess.run(
            [sys.executable, str(script), "--enable-inert-local-dispatch", "--format", "json"],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual([item["actor_id"] for item in payload["actor_results"]], ["taylor", "vera", "codex", "claude"])
        self.assertNotIn("TOKEN", result.stdout.upper())
        self.assertNotIn("SECRET", result.stdout.upper())


if __name__ == "__main__":
    unittest.main()
