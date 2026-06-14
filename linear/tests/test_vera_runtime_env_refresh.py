import json
import os
import subprocess
import tempfile
import unittest

from linear.scripts.refresh_vera_qa_gate_runtime_env import (
    DEFAULT_WORKSPACE_MAP,
    build_runtime_env,
    parse_env_file,
    render_shell_env,
)


class VeraRuntimeEnvRefreshTests(unittest.TestCase):
    def test_parse_env_file_accepts_export_prefix_used_by_service_account_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = os.path.join(tmp, "op-vault-service.env")
            with open(env_path, "w", encoding="utf-8") as fh:
                fh.write("export OP_SERVICE_ACCOUNT_TOKEN='secret-token'\n")

            values = parse_env_file(env_path)

        self.assertEqual(values["OP_SERVICE_ACCOUNT_TOKEN"], "secret-token")

    def test_build_runtime_env_uses_github_app_and_linear_oauth_client_credentials(self):
        env = build_runtime_env(
            github_fields={
                "VERA_QA_GATE_GITHUB_APP_ID": "app-id",
                "VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID": "install-id",
                "VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY": "private-key",
                "VERA_QA_GATE_WEBHOOK_SIGNING_SECRET": "webhook-secret",
            },
            linear_fields={
                "CLIENT_ID": "linear-client-id",
                "CLIENT_SECRET": "linear-client-secret",
            },
            linear_actor={"id": "actor-id", "name": "Vera QA Gate"},
            workspace_map={"BitPod-App/taylor01-mind": "worktree:/Users/taylor01/BitPod-App/taylor01-mind"},
        )

        self.assertEqual(env["VERA_QA_DISPATCH_ENABLED"], "true")
        self.assertEqual(env["VERA_QA_GATE_LIVE_ENABLED"], "true")
        self.assertEqual(env["VERA_QA_RESULT_SYNC_ENABLED"], "true")
        self.assertEqual(env["LINEAR_LIVE_EXECUTOR_ENABLED"], "true")
        self.assertEqual(env["LINEAR_OAUTH_CLIENT_ID"], "linear-client-id")
        self.assertEqual(env["LINEAR_OAUTH_CLIENT_SECRET"], "linear-client-secret")
        self.assertEqual(env["LINEAR_EXPECTED_ACTOR_ID"], "actor-id")
        self.assertEqual(env["GITHUB_WEBHOOK_SECRET"], "webhook-secret")
        self.assertTrue(env["HERMES_CLI_PATH"].endswith("/.local/bin/hermes"))
        self.assertTrue(env["TRACE_STORE_PATH"].startswith("/"))
        self.assertNotIn("~", env["TRACE_STORE_PATH"])
        self.assertIn("BitPod-App/taylor01-mind", env["VERA_QA_KANBAN_WORKSPACE_MAP"])
        self.assertNotIn("LINEAR_API_KEY", env)

    def test_default_workspace_map_covers_all_vera_gate_installed_repos(self):
        expected_repos = {
            "BitPod-App/.github",
            "BitPod-App/bitpod-assets",
            "BitPod-App/bitpod-docs",
            "BitPod-App/bitpod-taylor-runtime",
            "BitPod-App/bitpod-tools",
            "BitPod-App/bitregime-core",
            "BitPod-App/sector-feeds",
            "BitPod-App/taylor01-mind",
            "BitPod-App/taylor01-runtime",
        }

        env = build_runtime_env(
            github_fields={
                "VERA_QA_GATE_GITHUB_APP_ID": "app-id",
                "VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID": "install-id",
                "VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY": "private-key",
                "VERA_QA_GATE_WEBHOOK_SIGNING_SECRET": "webhook-secret",
            },
            linear_fields={
                "CLIENT_ID": "linear-client-id",
                "CLIENT_SECRET": "linear-client-secret",
            },
        )
        runtime_map = json.loads(env["VERA_QA_KANBAN_WORKSPACE_MAP"])

        self.assertEqual(set(DEFAULT_WORKSPACE_MAP), expected_repos)
        self.assertEqual(set(runtime_map), expected_repos)
        for repo, workspace in runtime_map.items():
            self.assertTrue(workspace.startswith("worktree:/Users/taylor01/BitPod-App/"), repo)

    def test_render_shell_env_round_trips_multiline_private_key_without_unquoted_expansion(self):
        source = {
            "VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nabc'$HOME\n-----END PRIVATE KEY-----\n",
            "LINEAR_OAUTH_CLIENT_SECRET": "client secret with spaces",
        }

        rendered = render_shell_env(source)

        with tempfile.TemporaryDirectory() as tmp:
            env_path = os.path.join(tmp, "runtime.env")
            with open(env_path, "w", encoding="utf-8") as fh:
                fh.write(rendered)
            script = f'. "{env_path}"; python3 - <<"PY"\nimport os\nprint(os.environ["VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY"])\nprint(os.environ["LINEAR_OAUTH_CLIENT_SECRET"])\nPY'
            proc = subprocess.run(["bash", "-lc", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("abc'$HOME", proc.stdout)
        self.assertIn("client secret with spaces", proc.stdout)


if __name__ == "__main__":
    unittest.main()
