"""The independent challenge board is readable without pygame."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from climber import challenge


class ChallengeBoardTests(unittest.TestCase):
    def test_catalog_has_valid_distinct_goals_and_concept_hints(self):
        self.assertEqual(len(challenge.CHALLENGES), 18)
        self.assertEqual(len(challenge.CODE_DETECTIVE), 5)
        titles = []
        for level, title, goal, hints in challenge.CHALLENGES:
            self.assertIn(level, {"Starter", "Intermediate", "Advanced", "Design"})
            self.assertTrue(title)
            self.assertTrue(goal)
            self.assertTrue(hints.startswith("Things to consider:"))
            titles.append(title)
        self.assertEqual(len(titles), len(set(titles)))

    def test_running_challenge_board_does_not_require_pygame(self):
        project = Path(__file__).resolve().parents[1]
        run = subprocess.run(
            [sys.executable, "-m", "climber.challenge"],
            cwd=project, capture_output=True, text=True, check=True,
        )
        self.assertIn("INDEPENDENT CHALLENGES", run.stdout)
        self.assertIn("CODE DETECTIVE", run.stdout)
        self.assertIn("Breaking platforms", run.stdout)
        self.assertIn("A rival climber", run.stdout)


if __name__ == "__main__":
    unittest.main()
