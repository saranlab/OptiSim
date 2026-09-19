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

    def test_sidebar_presets_and_controls(self) -> None:
        from streamlit.testing.v1 import AppTest

        app_path = str(Path(__file__).resolve().parents[1] / "app.py")
        at = AppTest.from_file(app_path)
        at.run(timeout=30)
        self.assertFalse(at.exception)

        # Verify initial values
        self.assertEqual(at.number_input(key="num_cvr").value, 10.0)
        self.assertEqual(at.number_input(key="num_lift").value, 12.0)

        # Select E-Commerce preset
        at.pills(key="preset_archetype").select("E-Commerce").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.number_input(key="num_cvr").value, 3.5)
        self.assertEqual(at.number_input(key="num_lift").value, 8.0)
        self.assertEqual(at.segmented_control(key="seg_conf").value, "95%")
        self.assertEqual(at.segmented_control(key="seg_power").value, "80%")

        # Direct number input edit switches archetype to Custom
        at.number_input(key="num_cvr").set_value(5.2).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.pills(key="preset_archetype").value, "Custom")
        self.assertEqual(at.number_input(key="num_cvr").value, 5.2)


if __name__ == "__main__":
    unittest.main()
