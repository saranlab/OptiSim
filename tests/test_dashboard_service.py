import unittest
from dataclasses import asdict

from dashboard.services import ExperimentDashboardService


class TestExperimentDashboardService(unittest.TestCase):
    def test_service_returns_all_dashboard_sections(self) -> None:
        result = ExperimentDashboardService.run(
            baseline_conversion_rate=10.0,
            expected_lift=12.0,
            alpha=0.05,
            beta=0.20,
            posterior_samples=5_000,
            bandit_rounds=500,
        )

        self.assertGreater(result.required_sample_size, 0)
        self.assertIn("conversion_rate_a", result.experiment)
        self.assertIn("p_value", result.frequentist)
        self.assertIn("probability_b_better", result.bayesian)
        self.assertEqual(sum(result.bandit["pulls"].values()), 500)

    def test_service_handles_real_mode_data(self) -> None:
        result = ExperimentDashboardService.run(
            real_sample_size_a=1000,
            real_conversions_a=100,
            real_sample_size_b=1000,
            real_conversions_b=150,
            alpha=0.05,
            posterior_samples=5_000,
            mode="real",
        )

        self.assertEqual(result.experiment["sample_size_a"], 1000)
        self.assertEqual(result.experiment["conversions_a"], 100)
        self.assertEqual(result.experiment["sample_size_b"], 1000)
        self.assertEqual(result.experiment["conversions_b"], 150)
        self.assertEqual(result.experiment["conversion_rate_a"], 0.1)
        self.assertEqual(result.experiment["conversion_rate_b"], 0.15)
        
        self.assertTrue(result.frequentist["is_significant"])
        self.assertEqual(result.recommendation["status"], "success")
        self.assertEqual(result.recommendation["title"], "Deploy Variant B")
        self.assertIsNone(result.bandit)

    def test_service_financials_cvr_viability(self) -> None:
        # Case 1: Financially Viable
        result_viable = ExperimentDashboardService.run(
            real_sample_size_a=1000,
            real_conversions_a=100,
            real_sample_size_b=1000,
            real_conversions_b=150,
            alpha=0.05,
            posterior_samples=1000,
            mode="real",
            revenue_per_conversion=50.0,
            implementation_cost=1000.0,
            projected_traffic=100000,
        )
        self.assertIsNotNone(result_viable.financials)
        self.assertAlmostEqual(result_viable.financials["gross_uplift"], 250000.0)  # 100000 * 0.05 * 50
        self.assertAlmostEqual(result_viable.financials["net_benefit"], 249000.0)
        self.assertAlmostEqual(result_viable.financials["roi"], 24900.0)
        self.assertEqual(result_viable.recommendation["status"], "success")
        self.assertEqual(result_viable.recommendation["title"], "Deploy Variant B")

        # Case 2: Significant but Financially Unviable (Setup Cost > gross uplift)
        result_unviable = ExperimentDashboardService.run(
            real_sample_size_a=1000,
            real_conversions_a=100,
            real_sample_size_b=1000,
            real_conversions_b=150,
            alpha=0.05,
            posterior_samples=1000,
            mode="real",
            revenue_per_conversion=50.0,
            implementation_cost=300000.0,
            projected_traffic=100000,
        )
        self.assertAlmostEqual(result_unviable.financials["gross_uplift"], 250000.0)
        self.assertAlmostEqual(result_unviable.financials["net_benefit"], -50000.0)
        self.assertEqual(result_unviable.recommendation["status"], "warning")
        self.assertEqual(result_unviable.recommendation["title"], "Significant but Financially Unviable")


if __name__ == "__main__":
    unittest.main()
