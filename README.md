# OptiSim // A/B Testing & Simulation Studio

OptiSim is a production-grade, Django-powered web application and modular Python suite designed for binary conversion experiments. The platform empowers developers and data scientists to design, simulate, analyze, and estimate the financial return of A/B tests.

Deployed live at: [opti-sim.vercel.app](https://opti-sim.vercel.app)

---

## Key Features

1. **Plan & Simulate Mode**: Runs Monte Carlo simulations to model variant performance and calculate target sample sizes required to meet statistical power goals.
2. **Analyze Real Data Mode**: Perform two-proportion Z-tests with Wald Confidence Intervals on observed conversion data.
3. **Bayesian Beta-Binomial Inference**: Computes MCMC posterior draws, credible intervals, the probability of B being superior to A, and expected risk (loss) curves.
4. **Thompson Sampling Bandits**: Simulates dynamic traffic allocation to show how multi-armed bandit routing minimizes regret over customer arrivals.
5. **Financial Impact Studio**: Combines setup costs, traffic volume, and value-per-conversion to project gross/net ROI and overall business benefits.
6. **Interactive Visualizations**: High-performance SVG curves representing convergence, posterior probability density functions, and multi-armed bandit allocations.
7. **Mathematical Rigor Reports**: Generates print-optimized reports detailing the rigorous mathematical formulas behind the calculations.

---

## Project Structure

```text
ab_testing_platform/       # Core mathematical and statistical engine
  bandits.py               # Thompson Sampling multi-armed bandit models
  bayesian.py              # Bayesian Beta-Binomial conjugate prior engine
  frequentist.py           # Wald Z-test & power calculations
  simulation.py            # Monte Carlo simulation utilities
  models.py                # Core dataclasses and value objects
dashboard/                 # Django application for the web interface
  services.py              # Business logic orchestrating simulation/analytics
  views.py                 # Views for web UI and math rigor reports
  forms.py                 # Form inputs and validations
config/                    # Django project configuration settings
static/                    # Dashboard UI styles (CSS) and graphics
templates/                 # HTML templates for responsive rendering
examples/                  # Python-only quickstart script
tests/                     # Comprehensive unittest suite
```

---

## Requirements

The core statistical engine relies on `numpy` to avoid heavy MCMC frameworks:

- Python 3.12+
- Django
- NumPy

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Local Development Setup

To run the OptiSim web application on your local machine:

1. Install dependencies from the virtual environment:
   ```bash
   pip install -r requirements.txt
   ```
2. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
3. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
4. Access the studio at: `http://127.0.0.1:8000/`

---

## running CLI / Tests

To run the Python-only quickstart example:

```bash
python examples/usage_example.py
```

To run the suite of automated statistical tests:

```bash
python -m unittest discover tests
```

---

## Vercel Deployment

OptiSim is configured to run on **Vercel** as serverless functions with zero configuration, serving static assets via the Vercel CDN. The settings file defines:
- `ALLOWED_HOSTS` covering Vercel production and staging domains.
- `STATIC_ROOT` configured for automatic `collectstatic` execution during Vercel builds.
