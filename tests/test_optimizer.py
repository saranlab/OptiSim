import unittest

from ab_testing_platform import CandidateFeature, PortfolioOptimizer
from dashboard.services import ExperimentDashboardService


class TestPortfolioOptimizer(unittest.TestCase):
    def test_empty_features_returns_feasible_zero(self) -> None:
        res = PortfolioOptimizer.solve(
            features=[],
            max_budget=10000.0,
            max_latency_ms=30.0,
            max_effort_points=20.0,
        )
        self.assertTrue(res.is_feasible)
        self.assertEqual(res.total_value, 0.0)
        self.assertEqual(len(res.selected_features), 0)

    def test_exact_knapsack_solution(self) -> None:
        # Items:
        # F1: Val=100, Cost=10
        # F2: Val=60,  Cost=20
        # F3: Val=120, Cost=30
        # Budget = 30 -> Optimal is F1 + F2 (Val 160, Cost 30) vs F3 (Val 120, Cost 30)
        f1 = CandidateFeature("F1", "Feature 1", "Core", 100.0, 10.0, 1.0, 1.0)
        f2 = CandidateFeature("F2", "Feature 2", "Core", 60.0, 20.0, 1.0, 1.0)
        f3 = CandidateFeature("F3", "Feature 3", "Core", 120.0, 30.0, 1.0, 1.0)

        res = PortfolioOptimizer.solve(
            features=[f1, f2, f3],
            max_budget=30.0,
            max_latency_ms=100.0,
            max_effort_points=100.0,
            risk_aversion=0.0,
        )
        self.assertTrue(res.is_feasible)
        selected_ids = {f.feature_id for f in res.selected_features}
        self.assertIn("F1", selected_ids)
        self.assertIn("F2", selected_ids)
        self.assertNotIn("F3", selected_ids)
        self.assertEqual(res.total_value, 160.0)
        self.assertEqual(res.total_cost, 30.0)

    def test_multi_dimensional_constraints_respected(self) -> None:
        # F1 has high value but high latency
        f1 = CandidateFeature("F1", "Heavy Feature", "Core", 1000.0, 100.0, latency_ms=50.0, effort_points=5.0)
        f2 = CandidateFeature("F2", "Fast Feature", "Core", 500.0, 100.0, latency_ms=10.0, effort_points=5.0)

        # Latency budget = 30ms -> F1 cannot be selected even though budget is enough
        res = PortfolioOptimizer.solve(
            features=[f1, f2],
            max_budget=500.0,
            max_latency_ms=30.0,
            max_effort_points=20.0,
            risk_aversion=0.0,
        )
        self.assertTrue(res.is_feasible)
        self.assertEqual(len(res.selected_features), 1)
        self.assertEqual(res.selected_features[0].feature_id, "F2")
        self.assertLessEqual(res.total_latency_ms, 30.0)

    def test_conflict_group_mutual_exclusion(self) -> None:
        # Two mutually exclusive variants of the same redesign
        f1 = CandidateFeature("V_A", "Variant A", "Redesign", 200.0, 50.0, 5.0, 5.0, conflict_group="redesign_ui")
        f2 = CandidateFeature("V_B", "Variant B", "Redesign", 350.0, 80.0, 5.0, 5.0, conflict_group="redesign_ui")
        f3 = CandidateFeature("V_C", "Unrelated Tool", "Tool", 100.0, 20.0, 2.0, 2.0, conflict_group=None)

        res = PortfolioOptimizer.solve(
            features=[f1, f2, f3],
            max_budget=200.0,
            max_latency_ms=100.0,
            max_effort_points=100.0,
            risk_aversion=0.0,
            enforce_conflicts=True,
        )
        self.assertTrue(res.is_feasible)
        selected_ids = {f.feature_id for f in res.selected_features}
        # Cannot have both V_A and V_B
        self.assertFalse("V_A" in selected_ids and "V_B" in selected_ids)
        self.assertIn("V_B", selected_ids)
        self.assertIn("V_C", selected_ids)

    def test_efficient_frontier_monotonicity(self) -> None:
        pool = PortfolioOptimizer.get_default_candidate_pool(50000.0, 1500.0)
        res = PortfolioOptimizer.solve(
            features=pool,
            max_budget=20000.0,
            max_latency_ms=50.0,
            max_effort_points=50.0,
            frontier_steps=10,
        )
        self.assertTrue(res.is_feasible)
        self.assertGreater(len(res.efficient_frontier), 1)
        # Verify non-decreasing value as budget expands
        values = [pt["value"] for pt in res.efficient_frontier]
        for i in range(len(values) - 1):
            self.assertGreaterEqual(values[i + 1], values[i])

    def test_service_layer_portfolio_optimization(self) -> None:
        res = ExperimentDashboardService.run_portfolio_optimization(
            max_budget=15000.0,
            max_latency_ms=30.0,
            max_effort_points=30.0,
        )
        self.assertTrue(res.is_feasible)
        self.assertGreater(res.total_value, 0.0)
        self.assertLessEqual(res.total_cost, 15000.0)
        self.assertLessEqual(res.total_latency_ms, 30.0)
        self.assertLessEqual(res.total_effort_points, 30.0)


if __name__ == "__main__":
    unittest.main()
