import unittest

from linear.src.runtime import BotRuntime
from linear.src.memory import InMemoryStore


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


if __name__ == "__main__":
    unittest.main()
