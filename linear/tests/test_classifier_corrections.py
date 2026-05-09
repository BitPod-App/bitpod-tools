import json
import unittest
from pathlib import Path

from linear.src.engine import LinearBotEngine


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "linear_type_classifier_corrections_v1.json"


class TestClassifierCorrections(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = LinearBotEngine()

    def test_corrections_fixture_enforces_expected_types(self):
        if not FIXTURE_PATH.exists():
            self.fail(f"missing fixture: {FIXTURE_PATH}")

        rows = json.loads(FIXTURE_PATH.read_text(encoding="utf-8") or "[]")
        self.assertIsInstance(rows, list)

        for idx, row in enumerate(rows, start=1):
            intake = row.get("intake")
            expected = row.get("expected_type")
            self.assertIsInstance(intake, dict, f"row {idx}: intake must be an object")
            self.assertIsInstance(expected, str, f"row {idx}: expected_type must be a string")
            predicted, reason = self.bot.classify_issue_type(intake)
            self.assertEqual(
                expected,
                predicted,
                f"row {idx}: expected {expected!r} but got {predicted!r}. reason={reason}",
            )

