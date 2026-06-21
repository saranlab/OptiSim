import subprocess
import sys
import unittest
from pathlib import Path


class TestUsageExample(unittest.TestCase):
    def test_usage_example_runs_successfully(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        example_path = project_root / "examples" / "usage_example.py"

        completed = subprocess.run(
            [sys.executable, str(example_path)],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        self.assertIn("A/B Testing & Statistical Simulation Platform", completed.stdout)
        self.assertIn("Thompson Sampling bandit simulation", completed.stdout)


if __name__ == "__main__":
    unittest.main()
