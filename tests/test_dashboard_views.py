from django.test import TestCase, Client
from django.urls import reverse


class TestExperimentDashboardViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("dashboard:experiment-dashboard")

    def test_get_dashboard_loads_correctly(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OptiSim")
        self.assertContains(response, "Plan & Simulate")
        self.assertContains(response, "Analyze Real Data")
        self.assertContains(response, "Methodology Guide")
        self.assertContains(response, "Frequentist Z-Test for Proportions")
        self.assertContains(response, "Interactive Sandbox: CTA Button Color Case Study")
        self.assertContains(response, "sandbox-btn-a")
        self.assertContains(response, "sandbox-btn-b")
        self.assertContains(response, "sandbox-apply")

    def test_post_simulation_mode_calculates_results(self) -> None:
        data = {
            "mode": "simulation",
            "baseline_conversion_rate": "10.0",
            "expected_lift": "12.0",
            "alpha": "0.05",
            "beta": "0.20",
            "posterior_samples": "2000",
            "bandit_rounds": "200",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Required Sample Size")
        self.assertContains(response, "Bandit Simulation")

    def test_post_real_mode_calculates_results(self) -> None:
        data = {
            "mode": "real",
            "real_sample_size_a": "1000",
            "real_conversions_a": "100",
            "real_sample_size_b": "1000",
            "real_conversions_b": "150",
            "alpha": "0.05",
            "posterior_samples": "2000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Sample Size")
        self.assertContains(response, "Observed CVR A")
        self.assertContains(response, "Decision Engine")
        self.assertContains(response, "Deploy Variant B")
        self.assertNotContains(response, "Dynamic Traffic Allocation")  # Hidden in real mode

    def test_post_real_mode_validation_errors(self) -> None:
        data = {
            "mode": "real",
            "real_sample_size_a": "1000",
            "real_conversions_a": "1500",  # Conversions > sample size
            "real_sample_size_b": "1000",
            "real_conversions_b": "120",
            "alpha": "0.05",
            "posterior_samples": "2000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conversions cannot exceed users.")

    def test_post_real_mode_calculates_financials(self) -> None:
        data = {
            "mode": "real",
            "real_sample_size_a": "1000",
            "real_conversions_a": "100",
            "real_sample_size_b": "1000",
            "real_conversions_b": "150",
            "alpha": "0.05",
            "posterior_samples": "2000",
            "revenue_per_conversion": "50.0",
            "implementation_cost": "2000.0",
            "projected_traffic": "100000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Financial Impact Studio")
        self.assertContains(response, "Expected Gross Uplift")
        self.assertContains(response, "$2,000.00")
        self.assertContains(response, "12,400.0%")

    def test_report_view_renders_correctly(self) -> None:
        report_url = reverse("dashboard:experiment-report")
        query_params = {
            "mode": "real",
            "real_sample_size_a": "1000",
            "real_conversions_a": "100",
            "real_sample_size_b": "1000",
            "real_conversions_b": "150",
            "alpha": "0.05",
            "posterior_samples": "2000",
            "revenue_per_conversion": "50.0",
            "implementation_cost": "2000.0",
            "projected_traffic": "100000",
        }
        response = self.client.get(report_url, query_params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Methodology Verification Report")
        self.assertContains(response, "Two-Proportion Wald Z-Test")
        self.assertContains(response, "Observed Statistical Power (1 - &beta;):")
        self.assertContains(response, "Conjugate Beta-Binomial Inference")
        self.assertContains(response, "Financial Impact &amp; ROI Projections")
        self.assertContains(response, "12,400.0%")
