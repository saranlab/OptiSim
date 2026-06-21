"""Views for the A/B testing dashboard."""

from __future__ import annotations

from typing import Any

from django.shortcuts import render
from django.views import View
from django.views.generic import FormView

from dashboard.forms import ExperimentConfigurationForm
from dashboard.services import ExperimentDashboardService


class ExperimentDashboardView(FormView):
    """Main dashboard where users configure and run analyses."""

    template_name = "dashboard/experiment_dashboard.html"
    form_class = ExperimentConfigurationForm

    def get_initial(self) -> dict[str, Any]:
        return {
            **super().get_initial(),
            "mode": "simulation",
            "baseline_conversion_rate": 10.0,
            "expected_lift": 12.0,
            "alpha": 0.05,
            "beta": 0.20,
            "posterior_samples": 100_000,
            "bandit_rounds": 20_000,
            "real_sample_size_a": 1000,
            "real_conversions_a": 100,
            "real_sample_size_b": 1000,
            "real_conversions_b": 120,
            "revenue_per_conversion": 10.0,
            "implementation_cost": 500.0,
            "projected_traffic": 100000,
        }

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form = context["form"]

        if not form.is_bound:
            form = self.form_class(initial=self.get_initial())
            context["form"] = form
            context["analysis"] = ExperimentDashboardService.run(**form.initial)

        return context

    def form_valid(self, form: ExperimentConfigurationForm):
        context = self.get_context_data(form=form)
        context["analysis"] = ExperimentDashboardService.run(**form.cleaned_data)
        return self.render_to_response(context)


class ExperimentRigorReportView(View):
    """Generates the print-optimized mathematical rigor report."""

    def get(self, request, *args, **kwargs):
        # Bind GET parameters to the configuration form
        form = ExperimentConfigurationForm(request.GET)
        
        # If the form is valid, run the service with cleaned data
        if form.is_valid():
            analysis = ExperimentDashboardService.run(**form.cleaned_data)
        else:
            # Fallback values if form is invalid or empty
            try:
                baseline_val = float(request.GET.get("baseline_conversion_rate", 10.0))
            except ValueError:
                baseline_val = 10.0
                
            try:
                lift_val = float(request.GET.get("expected_lift", 12.0))
            except ValueError:
                lift_val = 12.0

            try:
                alpha_val = float(request.GET.get("alpha", 0.05))
            except ValueError:
                alpha_val = 0.05

            try:
                beta_val = float(request.GET.get("beta", 0.20))
            except ValueError:
                beta_val = 0.20

            try:
                samples_val = int(request.GET.get("posterior_samples", 100_000))
            except ValueError:
                samples_val = 100_000

            try:
                rounds_val = int(request.GET.get("bandit_rounds", 20_000))
            except ValueError:
                rounds_val = 20_000

            try:
                size_a = int(request.GET.get("real_sample_size_a", 1000))
            except ValueError:
                size_a = 1000

            try:
                conv_a = int(request.GET.get("real_conversions_a", 100))
            except ValueError:
                conv_a = 100

            try:
                size_b = int(request.GET.get("real_sample_size_b", 1000))
            except ValueError:
                size_b = 1000

            try:
                conv_b = int(request.GET.get("real_conversions_b", 120))
            except ValueError:
                conv_b = 120

            try:
                revenue_val = float(request.GET.get("revenue_per_conversion", 10.0))
            except ValueError:
                revenue_val = 10.0

            try:
                cost_val = float(request.GET.get("implementation_cost", 500.0))
            except ValueError:
                cost_val = 500.0

            try:
                traffic_val = int(request.GET.get("projected_traffic", 100000))
            except ValueError:
                traffic_val = 100000

            initial_data = {
                "mode": request.GET.get("mode", "simulation"),
                "baseline_conversion_rate": baseline_val,
                "expected_lift": lift_val,
                "alpha": alpha_val,
                "beta": beta_val,
                "posterior_samples": samples_val,
                "bandit_rounds": rounds_val,
                "real_sample_size_a": size_a,
                "real_conversions_a": conv_a,
                "real_sample_size_b": size_b,
                "real_conversions_b": conv_b,
                "revenue_per_conversion": revenue_val,
                "implementation_cost": cost_val,
                "projected_traffic": traffic_val,
            }
            analysis = ExperimentDashboardService.run(**initial_data)
            
        context = {
            "analysis": analysis,
            "form_data": form.cleaned_data if form.is_valid() else initial_data,
        }
        return render(request, "dashboard/rigor_report.html", context)
