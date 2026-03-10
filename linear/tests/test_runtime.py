import os
import tempfile
import unittest

from linear.src.engine import Action
from linear.src.governance import GovernancePolicy
from linear.src.runtime import BotRuntime
from linear.src.memory import InMemoryStore, JsonlFileStore
from linear.src.service import apply_actions


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


if __name__ == "__main__":
    unittest.main()
