import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from linear.scripts.mint_vera_qa_gate_github_token import (
    load_runtime_env,
    shell_export_for_token,
)


class MintVeraGithubTokenTests(unittest.TestCase):
    def test_load_runtime_env_adds_values_without_writing_gh_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = os.path.join(tmp, "runtime.env")
            with open(env_path, "w", encoding="utf-8") as fh:
                fh.write("export VERA_QA_GATE_GITHUB_CLIENT_ID='Iv23client'\n")
                fh.write("export VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID='139088756'\n")

            loaded = load_runtime_env(env_path)

        self.assertEqual(loaded["VERA_QA_GATE_GITHUB_CLIENT_ID"], "Iv23client")
        self.assertEqual(loaded["VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID"], "139088756")
        self.assertNotIn("GH_TOKEN", loaded)
        self.assertNotIn("GITHUB_TOKEN", loaded)

    def test_shell_export_for_token_quotes_without_persisting(self):
        self.assertEqual(
            shell_export_for_token("ghs_example'abc"),
            "export GH_TOKEN='ghs_example'\"'\"'abc'",
        )

    def test_main_prints_shell_export_for_minted_token(self):
        from linear.scripts import mint_vera_qa_gate_github_token as script

        with tempfile.TemporaryDirectory() as tmp:
            env_path = os.path.join(tmp, "runtime.env")
            with open(env_path, "w", encoding="utf-8") as fh:
                fh.write("export VERA_QA_GATE_GITHUB_APP_ID='4007105'\n")
                fh.write("export VERA_QA_GATE_GITHUB_CLIENT_ID='Iv23client'\n")
                fh.write("export VERA_QA_GATE_GITHUB_APP_INSTALLATION_ID='139088756'\n")
                fh.write("export VERA_QA_GATE_GITHUB_APP_PRIVATE_KEY='private-key'\n")

            with patch(
                "linear.scripts.mint_vera_qa_gate_github_token.github_app_installation_token_from_env",
                return_value="ghs_minted",
            ):
                with patch("builtins.print") as mock_print:
                    code = script.main(["--runtime-env", env_path, "--format", "shell"])

        self.assertEqual(code, 0)
        mock_print.assert_called_once_with("export GH_TOKEN='ghs_minted'")

    def test_direct_script_help_runs_from_repo_root(self):
        proc = subprocess.run(
            ["python3", "linear/scripts/mint_vera_qa_gate_github_token.py", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Mint a short-lived Vera QA Gate GitHub App installation token", proc.stdout)


if __name__ == "__main__":
    unittest.main()
