# A/B Testing & Statistical Simulation Platform

Production-grade, modular Python utilities for binary conversion experiments.
The platform includes Monte Carlo simulation, frequentist inference, Bayesian
Beta-Binomial inference, and Thompson Sampling traffic allocation.

## Project Structure

```text
ab_testing_platform/
  __init__.py
  bandits.py
  bayesian.py
  formatting.py
  frequentist.py
  math_utils.py
  models.py
  simulation.py
  validation.py
examples/
  usage_example.py
tests/
  test_*.py
```

## Requirements

```bash
pip install -r requirements.txt
```

Only `numpy` is required. The platform avoids heavy MCMC libraries and does not
require SciPy.

## Quick Start

```python
from ab_testing_platform import (
    BayesianEngine,
    ExperimentSimulator,
    StatsEngine,
    ThompsonSamplingBandit,
)

required_n = StatsEngine.required_sample_size_per_variation(
    baseline_conversion_rate=0.10,
    minimum_detectable_effect=0.12,
)

experiment = ExperimentSimulator(random_seed=42).simulate_ab_test(
    sample_size_per_group=required_n,
    baseline_conversion_rate=0.10,
    expected_lift=0.12,
)

frequentist = StatsEngine.two_proportion_z_test(
    conversions_a=experiment.conversions_a,
    sample_size_a=experiment.sample_size_a,
    conversions_b=experiment.conversions_b,
    sample_size_b=experiment.sample_size_b,
)

bayesian = BayesianEngine(random_seed=42).analyze(
    conversions_a=experiment.conversions_a,
    sample_size_a=experiment.sample_size_a,
    conversions_b=experiment.conversions_b,
    sample_size_b=experiment.sample_size_b,
)

bandit = ThompsonSamplingBandit({"A": 0.10, "B": 0.112}, random_seed=42)
summary = bandit.run(n_rounds=20_000)
```

Run the full example:

```bash
python examples/usage_example.py
```

Run tests with the standard library:

```bash
python -m unittest discover tests
```
