import ast
import unittest
from pathlib import Path

from dashboard.services import ExperimentDashboardService


class TestStreamlitApp(unittest.TestCase):
    def test_app_syntax_and_structure(self) -> None:
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        self.assertTrue(app_path.exists(), "app.py does not exist")
        content = app_path.read_text(encoding="utf-8")
        # Ensure it parses as valid Python with no syntax errors
        ast.parse(content)

    def test_streamlit_integration_simulation(self) -> None:
        analysis = ExperimentDashboardService.run(
            baseline_conversion_rate=10.0,
            expected_lift=12.0,
            alpha=0.05,
            beta=0.20,
            posterior_samples=5000,
            bandit_rounds=1000,
            mode="simulation",
        )
        self.assertIsNotNone(analysis)
        self.assertIn("conversion_rate_a", analysis.experiment)
        self.assertIn("ci_lower", analysis.sequential)
        self.assertIn("probability_b_better", analysis.bayesian)
        self.assertIn("title", analysis.recommendation)

    def test_streamlit_integration_real(self) -> None:
        analysis = ExperimentDashboardService.run(
            real_sample_size_a=1000,
            real_conversions_a=100,
            real_sample_size_b=1000,
            real_conversions_b=120,
            alpha=0.05,
            posterior_samples=5000,
            mode="real",
        )
        self.assertIsNotNone(analysis)
        self.assertIn("ci_lower", analysis.sequential)
        self.assertIn("probability_b_better", analysis.bayesian)


if __name__ == "__main__":
    unittest.main()
