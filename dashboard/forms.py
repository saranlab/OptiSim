"""Forms for configuring A/B testing analyses from the web UI."""

from __future__ import annotations

from django import forms


class ExperimentConfigurationForm(forms.Form):
    """Validated inputs for the dashboard experiment run."""

    mode = forms.ChoiceField(
        choices=[("simulation", "Plan & Simulate"), ("real", "Analyze Real Data")],
        initial="simulation",
        widget=forms.HiddenInput(),
    )
    baseline_conversion_rate = forms.FloatField(
        required=False,
        min_value=0.01,
        max_value=99.99,
        initial=10.0,
        label="Baseline CVR",
        help_text="Group A conversion probability as a percentage (e.g. 10.0 for 10%).",
    )
    expected_lift = forms.FloatField(
        required=False,
        min_value=-99.9,
        max_value=1000.0,
        initial=12.0,
        label="Expected lift",
        help_text="Relative lift for B as a percentage (e.g. 12.0 for 12%).",
    )
    alpha = forms.FloatField(
        min_value=0.0001,
        max_value=0.50,
        initial=0.05,
        label="Alpha",
    )
    beta = forms.FloatField(
        required=False,
        min_value=0.0001,
        max_value=0.9999,
        initial=0.20,
        label="Beta",
        help_text="Power is 1 - beta.",
    )
    posterior_samples = forms.IntegerField(
        min_value=1_000,
        max_value=1_000_000,
        initial=100_000,
        label="Posterior samples",
    )
    bandit_rounds = forms.IntegerField(
        required=False,
        min_value=100,
        max_value=1_000_000,
        initial=20_000,
        label="Bandit rounds",
    )
    real_sample_size_a = forms.IntegerField(
        required=False,
        min_value=1,
        label="Group A Users",
    )
    real_conversions_a = forms.IntegerField(
        required=False,
        min_value=0,
        label="Group A Conversions",
    )
    real_sample_size_b = forms.IntegerField(
        required=False,
        min_value=1,
        label="Group B Users",
    )
    real_conversions_b = forms.IntegerField(
        required=False,
        min_value=0,
        label="Group B Conversions",
    )
    revenue_per_conversion = forms.FloatField(
        required=False,
        min_value=0.0,
        initial=10.0,
        label="Revenue per Conversion ($)",
        help_text="Expected revenue value per conversion.",
    )
    implementation_cost = forms.FloatField(
        required=False,
        min_value=0.0,
        initial=500.0,
        label="Variant B Setup Cost ($)",
        help_text="One-time fixed cost to deploy Variant B.",
    )
    projected_traffic = forms.IntegerField(
        required=False,
        min_value=1,
        initial=100000,
        label="Projected Traffic",
        help_text="Volume of users to scale conversions over a business horizon.",
    )

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        
        # Fill default values for optional financial fields if omitted
        if cleaned_data.get("revenue_per_conversion") is None:
            cleaned_data["revenue_per_conversion"] = 0.0
        if cleaned_data.get("implementation_cost") is None:
            cleaned_data["implementation_cost"] = 0.0
        if cleaned_data.get("projected_traffic") is None:
            cleaned_data["projected_traffic"] = 100000

        mode = cleaned_data.get("mode")

        if mode == "real":
            sa = cleaned_data.get("real_sample_size_a")
            ca = cleaned_data.get("real_conversions_a")
            sb = cleaned_data.get("real_sample_size_b")
            cb = cleaned_data.get("real_conversions_b")

            if sa is None:
                self.add_error("real_sample_size_a", "This field is required.")
            if ca is None:
                self.add_error("real_conversions_a", "This field is required.")
            if sb is None:
                self.add_error("real_sample_size_b", "This field is required.")
            if cb is None:
                self.add_error("real_conversions_b", "This field is required.")

            if sa is not None and ca is not None:
                if ca > sa:
                    self.add_error("real_conversions_a", "Conversions cannot exceed users.")
            if sb is not None and cb is not None:
                if cb > sb:
                    self.add_error("real_conversions_b", "Conversions cannot exceed users.")
        else:
            baseline = cleaned_data.get("baseline_conversion_rate")
            lift = cleaned_data.get("expected_lift")
            beta = cleaned_data.get("beta")
            rounds = cleaned_data.get("bandit_rounds")

            if baseline is None:
                self.add_error("baseline_conversion_rate", "This field is required.")
            if lift is None:
                self.add_error("expected_lift", "This field is required.")
            if beta is None:
                self.add_error("beta", "This field is required.")
            if rounds is None:
                self.add_error("bandit_rounds", "This field is required.")

            if baseline is not None and lift is not None:
                baseline_dec = float(baseline) / 100.0
                lift_dec = float(lift) / 100.0
                treatment_rate = baseline_dec * (1.0 + lift_dec)
                if not 0.0 <= treatment_rate <= 1.0:
                    self.add_error(
                        "expected_lift",
                        "Baseline CVR and lift produce a treatment CVR outside [0%, 100%].",
                    )

        return cleaned_data
