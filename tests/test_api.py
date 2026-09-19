"""Integration tests for FastAPI REST API endpoints."""

import unittest
from fastapi.testclient import TestClient

from backend.main import app


class TestFastAPIBackend(unittest.TestCase):
    """Test suite for OptiSim REST API endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "2.0.0")

    def test_sequential_stream_api(self) -> None:
        payload = {
            "control_conversions": [0, 1, 0, 0, 1, 0, 0, 1, 0, 0] * 5,
            "treatment_conversions": [1, 1, 0, 1, 1, 0, 1, 1, 0, 1] * 5,
            "alpha": 0.05,
            "v_opt": 0.05,
        }
        response = self.client.post("/api/v1/experiment/sequential", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tau_estimates", data)
        self.assertIn("ci_lowers", data)
        self.assertIn("ci_uppers", data)
        self.assertEqual(len(data["sample_sizes"]), 50)

    def test_cuped_api(self) -> None:
        y_ctrl = [1.0, 2.0, 3.0, 2.5, 3.5, 4.0]
        y_treat = [2.0, 3.0, 4.0, 3.5, 4.5, 5.0]
        x_ctrl = [0.9, 2.1, 2.9, 2.4, 3.6, 4.1]
        x_treat = [1.8, 3.2, 3.9, 3.4, 4.6, 5.1]
        payload = {
            "y_control": y_ctrl,
            "y_treatment": y_treat,
            "x_control": x_ctrl,
            "x_treatment": x_treat,
        }
        response = self.client.post("/api/v1/experiment/cuped", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("variance_reduction_pct", data)
        self.assertIn("theta", data)
        self.assertGreater(data["variance_reduction_pct"], 0.0)

    def test_delta_method_api(self) -> None:
        payload = {
            "sessions_control": [10, 20, 30, 40, 50],
            "conversions_control": [1, 2, 3, 4, 5],
            "sessions_treatment": [10, 20, 30, 40, 50],
            "conversions_treatment": [2, 4, 6, 8, 10],
            "alpha": 0.05,
        }
        response = self.client.post("/api/v1/experiment/delta-method", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertAlmostEqual(data["ratio_control"], 0.10, places=2)
        self.assertAlmostEqual(data["ratio_treatment"], 0.20, places=2)
        self.assertIn("z_statistic", data)

    def test_hte_endpoints(self) -> None:
        # Test defaults
        defaults_resp = self.client.get("/api/v1/experiment/hte/defaults")
        self.assertEqual(defaults_resp.status_code, 200)
        defaults = defaults_resp.json()
        self.assertGreaterEqual(len(defaults), 2)

        # Test analysis
        payload = {"subgroups": defaults, "alpha": 0.05}
        resp = self.client.post("/api/v1/experiment/hte", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("heterogeneity_p_value", data)
        self.assertIn("has_heterogeneity", data)
        self.assertIn("top_performing_segment", data)
        self.assertEqual(len(data["subgroups"]), len(defaults))

    def test_guardrails_endpoints(self) -> None:
        # Test defaults
        defaults_resp = self.client.get("/api/v1/experiment/guardrails/defaults")
        self.assertEqual(defaults_resp.status_code, 200)
        defaults = defaults_resp.json()
        self.assertGreaterEqual(len(defaults), 1)

        # Test audit
        payload = {"guardrails": defaults, "fdr_alpha": 0.05}
        resp = self.client.post("/api/v1/experiment/guardrails", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("has_critical_violations", data)
        self.assertIn("metrics", data)
        self.assertEqual(len(data["metrics"]), len(defaults))

    def test_portfolio_endpoints(self) -> None:
        # Test candidates default
        cand_resp = self.client.get("/api/v1/portfolio/candidates/default")
        self.assertEqual(cand_resp.status_code, 200)
        candidates = cand_resp.json()
        self.assertGreaterEqual(len(candidates), 3)

        # Test optimization in robust mode
        payload = {
            "features": candidates,
            "max_budget": 10000.0,
            "max_latency_ms": 50.0,
            "max_effort_points": 40.0,
            "robust_mode": True,
            "churn_penalty_weight": 1.0,
            "frontier_steps": 5,
        }
        opt_resp = self.client.post("/api/v1/portfolio/optimize", json=payload)
        self.assertEqual(opt_resp.status_code, 200)
        data = opt_resp.json()
        self.assertTrue(data["is_feasible"])
        self.assertGreater(len(data["selected_features"]), 0)
        self.assertGreater(len(data["efficient_frontier"]), 0)

    def test_bandit_endpoints(self) -> None:
        # Thompson Sampling
        ts_payload = {
            "true_conversion_rates": {"Arm_A": 0.10, "Arm_B": 0.18},
            "n_rounds": 200,
            "delay_rounds": 5,
        }
        ts_resp = self.client.post("/api/v1/bandit/thompson", json=ts_payload)
        self.assertEqual(ts_resp.status_code, 200)
        ts_data = ts_resp.json()
        self.assertEqual(ts_data["pulls"]["Arm_A"] + ts_data["pulls"]["Arm_B"], 200)

        # LinUCB
        lin_payload = {
            "arm_names": ["Arm_A", "Arm_B", "Arm_C"],
            "n_rounds": 100,
            "context_dim": 3,
        }
        lin_resp = self.client.post("/api/v1/bandit/linucb", json=lin_payload)
        self.assertEqual(lin_resp.status_code, 200)
        lin_data = lin_resp.json()
        self.assertIn("ctr", lin_data)

    def test_memo_endpoint(self) -> None:
        payload = {
            "experiment_name": "Checkout V2 Rollout",
            "primary_metric": "CVR",
            "control_val": 0.10,
            "treatment_val": 0.12,
            "lift_pct": 20.0,
            "ci_lower": 0.005,
            "ci_upper": 0.035,
            "sample_size": 15000,
            "is_significant": True,
            "guardrails_passed": True,
            "recommended_action": "SHIP_TO_100_PERCENT",
            "portfolio_value": 75000.0,
            "subgroups_heterogeneity": False,
        }
        resp = self.client.post("/api/v1/memo/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("markdown", data)
        self.assertIn("Executive Decision Memo", data["markdown"])
        self.assertEqual(data["executive_verdict"], "SHIP TO 100% TRAFFIC")


if __name__ == "__main__":
    unittest.main()
