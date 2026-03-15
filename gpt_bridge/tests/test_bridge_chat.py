from __future__ import annotations

import argparse
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bridge_chat  # noqa: E402


class BridgeChatRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.log_file = Path(self.tmpdir.name) / "chat.jsonl"
        self.memory_store = Path(self.tmpdir.name) / "memory.jsonl"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _args(self, text: str) -> argparse.Namespace:
        return argparse.Namespace(
            text=text,
            session="team",
            from_actor="cj",
            log_file=str(self.log_file),
            memory_store=str(self.memory_store),
            memory_items=0,
            max_tokens=400,
            model=None,
            show_raw=False,
        )

    def test_taylor_mention_routes_with_persona_override(self):
        captured: dict[str, object] = {}
        ref_file = Path(self.tmpdir.name) / "taylor-reference.md"
        ref_file.write_text("Taylor canonical context", encoding="utf-8")

        def _fake_run_ask_once(**kwargs: object) -> dict[str, object]:
            captured.update(kwargs)
            return {"answer": {"json": {"reply": "Taylor is online."}}}

        stdout = io.StringIO()
        with (
            patch.object(bridge_chat, "DEFAULT_TAYLOR_REFERENCE_FILES", (ref_file,)),
            patch.object(bridge_chat, "_run_ask_once", side_effect=_fake_run_ask_once),
            patch.object(bridge_chat, "_set_active_session", return_value=None),
            contextlib.redirect_stdout(stdout),
        ):
            rc = bridge_chat.run_team(self._args("@taylor can you sanity-check this?"))

        self.assertEqual(rc, 0)
        self.assertEqual(captured["message"], "can you sanity-check this?")
        self.assertEqual(captured["meta"]["route_actor"], "taylor")
        self.assertIn("Taylor, CJ's senior product architect", captured["meta"]["system_prompt"])
        self.assertIn("[Reference: taylor-reference.md]", captured["context_text"])
        self.assertIn("Taylor canonical context", captured["context_text"])
        self.assertIn("taylor: Taylor is online.", stdout.getvalue())

    def test_gpt_mention_keeps_default_route(self):
        captured: dict[str, object] = {}

        def _fake_run_ask_once(**kwargs: object) -> dict[str, object]:
            captured.update(kwargs)
            return {"answer": {"json": {"reply": "Generic GPT reply."}}}

        stdout = io.StringIO()
        with (
            patch.object(bridge_chat, "_run_ask_once", side_effect=_fake_run_ask_once),
            patch.object(bridge_chat, "_set_active_session", return_value=None),
            contextlib.redirect_stdout(stdout),
        ):
            rc = bridge_chat.run_team(self._args("@gpt summarize this"))

        self.assertEqual(rc, 0)
        self.assertEqual(captured["message"], "summarize this")
        self.assertEqual(captured["meta"]["route_actor"], "gpt")
        self.assertNotIn("system_prompt", captured["meta"])
        self.assertIn("gpt: Generic GPT reply.", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
