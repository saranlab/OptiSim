"""
Unit tests for Advanced Analytics:
1. Heterogeneous Treatment Effects (HTE) & Subgroup Slicing (CATE)
2. Multi-Metric Guardrails & Benjamini-Hochberg False Discovery Rate (FDR)
3. Robust 0-1 Knapsack MILP Optimization & Downstream Churn Penalties
"""

from __future__ import annotations

import unittest
import numpy as np

from ab_testing_platform.guardrails import GuardrailEngine
from ab_testing_platform.hte import HTEEngine
from ab_testing_platform.models import CandidateFeature
from ab_testing_platform.optimizer import PortfolioOptimizer


class TestHTEEngine(unittest.TestCase):
    def setUp(self) -> None:
        # 3 segments: Mobile (strong winner), Desktop (neutral), Tablet (loser)
        self.subgroup_data = [
            {
                "name": "Mobile",
                "sample_size_a": 10000,
                "conversions_a": 1000,  # 10%
                "sample_size_b": 10000,
                "conversions_b": 1250,  # 12.5% (+2.5 pp lift, strong win)
            },
            {
                "name": "Desktop",
                "sample_size_a": 8000,
                "conversions_a": 960,  # 12%
                "sample_size_b": 8000,
                "conversions_b": 970,  # 12.1% (+0.1 pp lift, neutral)
            },
            {
                "name": "Tablet",
                "sample_size_a": 2000,
                "conversions_a": 200,  # 10%
                "sample_size_b": 2000,
                "conversions_b": 160,  # 8% (-2.0 pp lift, negative)
            },
        ]

    def test_subgroup_cate_estimation(self) -> None:
        res = HTEEngine.analyze_subgroups("device", self.subgroup_data, alpha=0.05)
        self.assertEqual(res.dimension, "device")
        self.assertEqual(len(res.subgroups), 3)

        mobile = next(s for s in res.subgroups if s.segment_name == "Mobile")
        self.assertAlmostEqual(mobile.cvr_a, 0.10, places=3)
        self.assertAlmostEqual(mobile.cvr_b, 0.125, places=3)
        self.assertAlmostEqual(mobile.absolute_lift, 0.025, places=3)
        self.assertTrue(mobile.is_significant)
        self.assertGreater(mobile.z_score, 5.0)

    def test_heterogeneity_detection(self) -> None:
        res = HTEEngine.analyze_subgroups("device", self.subgroup_data, alpha=0.05)
        # Because mobile is +2.5pp and tablet is -2.0pp, heterogeneity should be detected!
        self.assertTrue(res.has_heterogeneity)
        self.assertLess(res.heterogeneity_p_value, 0.01)
        self.assertEqual(res.top_performing_segment, "Mobile")
        self.assertEqual(res.worst_performing_segment, "Tablet")

    def test_default_device_subgroups_generator(self) -> None:
        subgroups = HTEEngine.get_default_device_subgroups(10000, 10000, 0.10, 0.12)
        self.assertEqual(len(subgroups), 3)
        res = HTEEngine.analyze_subgroups("device", subgroups)
        self.assertIsNotNone(res.overall_ate)


class TestGuardrailEngine(unittest.TestCase):
    def test_benjamini_hochberg_fdr_control(self) -> None:
        metrics = [
            # Significant failure: latency increased by 20% (threshold 10%), p=0.001
            {
                "metric_name": "Latency p95",
                "control_value": 50.0,
                "treatment_value": 60.0,
                "raw_p_value": 0.001,
                "direction_favorable": "lower",
                "threshold_pct": 10.0,
            },
            # Trending bad (12% error increase, threshold 5%), but p=0.15 (not significant under FDR)
            {
                "metric_name": "Error Rate",
                "control_value": 1.0,
                "treatment_value": 1.12,
                "raw_p_value": 0.15,
                "direction_favorable": "lower",
                "threshold_pct": 5.0,
            },
            # Normal metric, no issue
            {
                "metric_name": "Bounce Rate",
                "control_value": 40.0,
                "treatment_value": 39.5,
                "raw_p_value": 0.80,
                "direction_favorable": "lower",
                "threshold_pct": 5.0,
            },
        ]
        res = GuardrailEngine.audit(metrics, fdr_alpha=0.05)
        self.assertTrue(res.has_critical_violations)

        # Verify BH adjustment monotonicity
        lat_metric = next(m for m in res.metrics if m.metric_name == "Latency p95")
        err_metric = next(m for m in res.metrics if m.metric_name == "Error Rate")
        bounce_metric = next(m for m in res.metrics if m.metric_name == "Bounce Rate")

        self.assertEqual(lat_metric.status, "FAIL")
        self.assertTrue(lat_metric.is_violated)
        self.assertLess(lat_metric.adjusted_p_value, 0.05)

        self.assertEqual(err_metric.status, "WARN")
        self.assertFalse(err_metric.is_violated)

        self.assertEqual(bounce_metric.status, "PASS")

    def test_all_guardrails_pass(self) -> None:
        metrics = GuardrailEngine.get_default_guardrails()
        res = GuardrailEngine.audit(metrics, fdr_alpha=0.05)
        self.assertFalse(res.has_critical_violations)
        self.assertIn("PASSED", res.summary_verdict)


class TestRobustKnapsackOptimizer(unittest.TestCase):
    def setUp(self) -> None:
        self.features = [
            # High expected value but risky / low defensible floor (e.g. naive point estimate)
            CandidateFeature(
                feature_id="F1",
                name="Aggressive Popup",
                category="CRO",
                expected_value=100000.0,
                cost=5000.0,
                latency_ms=5.0,
                effort_points=10.0,
                risk_score=0.40,
                defensible_floor_value=30000.0,  # Large winner's curse drop!
                downstream_churn_risk=0.50,  # High churn risk
            ),
            # Moderate expected value but very solid defensible floor and zero churn
            CandidateFeature(
                feature_id="F2",
                name="Performance Optimization",
                category="Infra",
                expected_value=70000.0,
                cost=4000.0,
                latency_ms=-10.0,
                effort_points=10.0,
                risk_score=0.05,
                defensible_floor_value=65000.0,  # Rock-solid lower bound
                downstream_churn_risk=0.00,
            ),
        ]

    def test_deterministic_vs_robust_mode(self) -> None:
        # In expected value mode with budget 5000, F1 is chosen because 100k > 70k
        res_det = PortfolioOptimizer.solve(
            features=self.features,
            max_budget=5000.0,
            max_latency_ms=50.0,
            max_effort_points=20.0,
            risk_aversion=0.0,
            robust_mode=False,
        )
        self.assertEqual(len(res_det.selected_features), 1)
        self.assertEqual(res_det.selected_features[0].feature_id, "F1")

        # In robust mode, F2 is chosen because its defensible floor 65k > 30k!
        res_rob = PortfolioOptimizer.solve(
            features=self.features,
            max_budget=5000.0,
            max_latency_ms=50.0,
            max_effort_points=20.0,
            risk_aversion=0.0,
            robust_mode=True,
        )
        self.assertEqual(len(res_rob.selected_features), 1)
        self.assertEqual(res_rob.selected_features[0].feature_id, "F2")
        self.assertTrue(res_rob.is_robust)

    def test_churn_penalty_deduction(self) -> None:
        # Adding churn penalty should heavily penalize F1 (churn_risk 0.50)
        res_churn = PortfolioOptimizer.solve(
            features=self.features,
            max_budget=5000.0,
            max_latency_ms=50.0,
            max_effort_points=20.0,
            risk_aversion=0.0,
            robust_mode=False,
            churn_penalty_weight=0.80,  # 80% penalty on churn risk
        )
        self.assertEqual(len(res_churn.selected_features), 1)
        self.assertEqual(res_churn.selected_features[0].feature_id, "F2")


if __name__ == "__main__":
    unittest.main()
