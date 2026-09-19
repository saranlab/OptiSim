"""
OptiSim // Enterprise Causal Inference & A/B Experimentation Studio
A production-grade, mathematically rigorous experimentation platform.
Built with Streamlit, Plotly, NumPy, and SciPy.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root relative path is always prioritized in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
import streamlit as st

from ab_testing_platform import (
    CUPEDEngine,
    DeltaMethodEngine,
    StatsEngine,
)
from ab_testing_platform.models import CandidateFeature, OptimizationResult
from ab_testing_platform.optimizer import PortfolioOptimizer
from dashboard.services import ExperimentDashboardService

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OptiSim // Experimentation Studio",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Strict 60-30-10 Design System & Typographic Scale Injection
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* =========================================================================
       DESIGN TOKENS (60-30-10 Rule & WCAG AAA High Contrast)
       ========================================================================= */
    :root {
        --canvas-bg: #F8FAFC;
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --card-border-hover: #CBD5E1;
        --text-display: #0F172A;
        --text-body: #334155;
        --text-secondary: #475569;
        --text-muted: #64748B;
        --brand-blue: #2563EB;
        --brand-blue-subtle: #EFF6FF;
        --brand-blue-border: #BFDBFE;
        --status-win-bg: #F0FDF4;
        --status-win-border: #BBF7D0;
        --status-win-accent: #10B981;
        --status-win-title: #14532D;
        --status-win-body: #166534;
        --status-win-badge: #DCFCE7;
        --status-warn-bg: #FFFBEB;
        --status-warn-border: #FDE68A;
        --status-warn-accent: #F59E0B;
        --status-warn-title: #78350F;
        --status-warn-body: #92400E;
        --status-warn-badge: #FEF3C7;
        --status-danger-bg: #FEF2F2;
        --status-danger-border: #FECACA;
        --status-danger-accent: #EF4444;
        --status-danger-title: #7F1D1D;
        --status-danger-body: #991B1B;
        --status-danger-badge: #FEE2E2;
    }

    /* 60% Canvas & Root Typography */
    html, body, .stApp {
        background-color: var(--canvas-bg) !important;
        color: var(--text-body) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Force all base text elements to dark readable colors */
    p, span, label, div {
        color: var(--text-body);
    }

    /* Page Header */
    .page-header {
        margin-bottom: 22px;
    }
    .page-title {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        color: var(--text-display) !important;
        margin: 0 0 6px 0 !important;
        line-height: 1.25 !important;
    }
    .page-subtitle {
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        color: var(--text-secondary) !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }

    h1, h2, h3, h4 {
        color: var(--text-display) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        margin-top: 0 !important;
    }

    /* 30% Structural Cards (Metrics) */
    div[data-testid="stMetric"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        min-height: 100px !important;
    }
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 4px !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.3 !important;
    }
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p,
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] div {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-display) !important;
        font-size: 1.20rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.015em !important;
        font-variant-numeric: tabular-nums !important;
        line-height: 1.25 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        margin-top: 4px !important;
    }

    /* Native Container Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 14px !important;
        padding: 20px 22px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }

    /* Executive Verdict Banners */
    .verdict-banner {
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        border: 1px solid transparent;
        border-left-width: 5px;
    }
    .verdict-success {
        background-color: var(--status-win-bg);
        border-color: var(--status-win-border);
        border-left-color: var(--status-win-accent);
    }
    .verdict-warning {
        background-color: var(--status-warn-bg);
        border-color: var(--status-warn-border);
        border-left-color: var(--status-warn-accent);
    }
    .verdict-danger {
        background-color: var(--status-danger-bg);
        border-color: var(--status-danger-border);
        border-left-color: var(--status-danger-accent);
    }
    .verdict-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .badge-success {
        background-color: var(--status-win-badge);
        color: var(--status-win-title);
    }
    .badge-warning {
        background-color: var(--status-warn-badge);
        color: var(--status-warn-title);
    }
    .badge-danger {
        background-color: var(--status-danger-badge);
        color: var(--status-danger-title);
    }
    .verdict-title {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin: 0 0 8px 0 !important;
        line-height: 1.3 !important;
    }
    .verdict-success .verdict-title { color: var(--status-win-title) !important; }
    .verdict-warning .verdict-title { color: var(--status-warn-title) !important; }
    .verdict-danger .verdict-title { color: var(--status-danger-title) !important; }
    
    .verdict-message {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        margin: 0 !important;
    }
    .verdict-success .verdict-message { color: var(--status-win-body) !important; }
    .verdict-warning .verdict-message { color: var(--status-warn-body) !important; }
    .verdict-danger .verdict-message { color: var(--status-danger-body) !important; }

    /* Callout Box */
    .callout-box {
        background-color: var(--brand-blue-subtle);
        border: 1px solid var(--brand-blue-border);
        border-left: 4px solid var(--brand-blue);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .callout-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 6px;
    }
    .callout-text {
        font-size: 0.88rem;
        line-height: 1.55;
        color: #1E40AF;
        margin: 0;
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        border-bottom: 2px solid var(--card-border) !important;
        gap: 6px !important;
        margin-bottom: 22px !important;
    }
    button[data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-size: 0.90rem !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        border-radius: 8px 8px 0 0 !important;
        border: none !important;
    }
    button[data-baseweb="tab"]:hover {
        color: var(--text-display) !important;
        background-color: #F1F5F9 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--brand-blue) !important;
        border-bottom: 2px solid var(--brand-blue) !important;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: #F1F5F9 !important;
        border-right: 1px solid var(--card-border) !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text-display) !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: var(--text-body) !important;
        font-weight: 500 !important;
    }

    /* Q&A Block */
    .qa-card {
        border-left: 3px solid var(--brand-blue);
        padding: 12px 18px;
        margin-bottom: 14px;
        border-radius: 0 8px 8px 0;
        background-color: #F8FAFC;
    }
    .qa-q {
        font-weight: 700;
        color: var(--text-display);
        margin-bottom: 4px;
        font-size: 0.95rem;
    }
    .qa-a {
        color: var(--text-body);
        font-size: 0.88rem;
        line-height: 1.6;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. Standardized Plotly Theme Helper
# -----------------------------------------------------------------------------
def format_chart(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=24, r=24, t=20, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color="#334155",
            size=12,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#CBD5E1",
            tickcolor="#CBD5E1",
            tickfont=dict(color="#64748B", size=11),
            title_font=dict(color="#1E293B", size=12, weight=600),
            automargin=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#CBD5E1",
            tickcolor="#CBD5E1",
            tickfont=dict(color="#64748B", size=11),
            title_font=dict(color="#1E293B", size=12, weight=600),
            automargin=True,
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_color="#F8FAFC",
            font_size=12,
            font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        ),
    )
    return fig


# -----------------------------------------------------------------------------
# 4. Sidebar Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## **OptiSim Studio**")
    st.caption("Causal Inference & Experimentation Architecture")
    st.markdown("---")

    mode_label = st.radio(
        "Experiment Mode",
        options=[
            "Plan & Simulate (Monte Carlo)",
            "Upload CSV Dataset (Raw User Logs)",
            "Analyze Real Data (Observed Counts)",
        ],
        index=0,
        help="Simulate with synthetic Monte Carlo sample paths, upload user-level experiment logs, or analyze observed counts.",
    )
    is_simulation = ("Plan & Simulate" in mode_label)
    is_csv = ("Upload CSV Dataset" in mode_label)

    st.markdown("### Statistical Design")
    st.caption("Configure parameters directly or choose an industry archetype.")

    PRESET_ARCHETYPES = {
        "SaaS B2B": {
            "cvr": 10.0,
            "lift": 12.0,
            "conf": "95%",
            "power": "80%",
            "rev": 50.0,
            "cost": 1000.0,
            "traffic": 100000,
        },
        "E-Commerce": {
            "cvr": 3.5,
            "lift": 8.0,
            "conf": "95%",
            "power": "80%",
            "rev": 25.0,
            "cost": 2500.0,
            "traffic": 250000,
        },
        "Ad Tech": {
            "cvr": 1.5,
            "lift": 4.0,
            "conf": "99%",
            "power": "90%",
            "rev": 5.0,
            "cost": 500.0,
            "traffic": 1000000,
        },
    }

    # Initialize state keys if not already present
    if "preset_archetype" not in st.session_state:
        st.session_state["preset_archetype"] = "Custom"
    if "num_cvr" not in st.session_state:
        st.session_state["num_cvr"] = 10.0
    if "num_lift" not in st.session_state:
        st.session_state["num_lift"] = 12.0
    if "seg_conf" not in st.session_state:
        st.session_state["seg_conf"] = "95%"
    if "seg_power" not in st.session_state:
        st.session_state["seg_power"] = "80%"
    if "num_rev" not in st.session_state:
        st.session_state["num_rev"] = 10.0
    if "num_cost" not in st.session_state:
        st.session_state["num_cost"] = 500.0
    if "num_traffic" not in st.session_state:
        st.session_state["num_traffic"] = 100000

    def on_preset_change():
        choice = st.session_state.get("preset_archetype")
        if choice in PRESET_ARCHETYPES:
            p = PRESET_ARCHETYPES[choice]
            st.session_state["num_cvr"] = float(p["cvr"])
            st.session_state["num_lift"] = float(p["lift"])
            st.session_state["seg_conf"] = p["conf"]
            st.session_state["seg_power"] = p["power"]
            st.session_state["num_rev"] = float(p["rev"])
            st.session_state["num_cost"] = float(p["cost"])
            st.session_state["num_traffic"] = int(p["traffic"])

    def set_custom_preset():
        if st.session_state.get("preset_archetype") != "Custom":
            st.session_state["preset_archetype"] = "Custom"

    if is_simulation:
        st.markdown("**Industry Benchmark Archetype**")
        st.pills(
            "Industry Archetype",
            options=["Custom", "SaaS B2B", "E-Commerce", "Ad Tech"],
            key="preset_archetype",
            on_change=on_preset_change,
            label_visibility="collapsed",
        )

    # 1. Confidence Level (Alpha)
    st.markdown("**Confidence Level (1 - α)**")
    conf_choice = st.segmented_control(
        "Confidence Level (1 - α)",
        options=["95%", "99%", "90%", "Custom"],
        key="seg_conf",
        label_visibility="collapsed",
        help="Type I error rate (α = 1 - Confidence). 95% (α=0.05) is the industry standard for anytime-valid confidence sequences.",
    )
    if conf_choice == "95%":
        alpha = 0.05
    elif conf_choice == "99%":
        alpha = 0.01
    elif conf_choice == "90%":
        alpha = 0.10
    else:
        alpha = st.number_input(
            "Custom α (Type I Error)",
            min_value=0.001,
            max_value=0.200,
            value=0.050,
            step=0.005,
            format="%.3f",
            on_change=set_custom_preset,
            help="Significance level α.",
        )

    if is_simulation:
        # 2. Power (1 - Beta)
        st.markdown("**Statistical Power (1 - β)**")
        power_choice = st.segmented_control(
            "Statistical Power (1 - β)",
            options=["80%", "90%", "Custom"],
            key="seg_power",
            label_visibility="collapsed",
            help="Target statistical power. 80% is standard; 90% minimizes false negatives.",
        )
        if power_choice == "80%":
            beta = 0.20
        elif power_choice == "90%":
            beta = 0.10
        else:
            custom_p = st.number_input(
                "Custom Power (1 - β)",
                min_value=0.50,
                max_value=0.99,
                value=0.85,
                step=0.05,
                format="%.2f",
                on_change=set_custom_preset,
            )
            beta = 1.0 - custom_p

        st.caption(f"Significance: **α = {alpha:.3f}** | Target Power: **{(1.0 - beta)*100:.0f}%**")

        st.markdown("**Conversion Rates & Effect Size**")
        col_cvr, col_lift = st.columns(2)
        with col_cvr:
            baseline_cvr = st.number_input(
                "Baseline CVR (%)",
                min_value=0.1,
                max_value=90.0,
                step=0.5,
                format="%.2f",
                key="num_cvr",
                on_change=set_custom_preset,
                help="Control conversion rate baseline (Group A).",
            )
        with col_lift:
            expected_lift = st.number_input(
                "Target Lift (%)",
                min_value=-50.0,
                max_value=100.0,
                step=0.5,
                format="%.1f",
                key="num_lift",
                on_change=set_custom_preset,
                help="Minimum Detectable Effect (MDE) relative lift.",
            )

        treatment_cvr = baseline_cvr * (1.0 + expected_lift / 100.0)
        st.caption(f"Target Treatment CVR: **{treatment_cvr:.2f}%** ({expected_lift:+.1f}% vs baseline)")

        bandit_rounds = st.number_input(
            "Bandit Simulation Steps",
            min_value=5_000,
            max_value=100_000,
            value=20_000,
            step=5_000,
            help="Rounds for Thompson Sampling & LinUCB simulation.",
        )
        posterior_samples = 100_000
        real_sample_size_a = real_sample_size_b = None
        real_conversions_a = real_conversions_b = None

    elif is_csv:
        st.markdown("#### Experiment Log Ingestion")
        uploaded_csv = st.file_uploader(
            "Upload User-Level CSV",
            type=["csv"],
            help="Upload raw logs with columns: user_id, variant, converted, pre_spend, sessions",
        )
        if st.button("Load Sample Dataset", help="Load pre-built 10,000 user checkout experiment dataset", width="stretch"):
            sample_path = PROJECT_ROOT / "sample_experiment_data.csv"
            if sample_path.exists():
                st.session_state["raw_df"] = pd.read_csv(sample_path)
                st.session_state["raw_df_name"] = "Sample Checkout Experiment (N=10,000)"

        if uploaded_csv is not None:
            st.session_state["raw_df"] = pd.read_csv(uploaded_csv)
            st.session_state["raw_df_name"] = uploaded_csv.name

        df_loaded = st.session_state.get("raw_df")
        if df_loaded is None:
            sample_path = PROJECT_ROOT / "sample_experiment_data.csv"
            if sample_path.exists():
                df_loaded = pd.read_csv(sample_path)
                st.session_state["raw_df"] = df_loaded
                st.session_state["raw_df_name"] = "Sample Checkout Experiment (N=10,000)"

        if df_loaded is not None:
            v_cols = [c for c in df_loaded.columns if c.lower() in ["variant", "group", "arm", "treatment", "variation"]]
            v_col = v_cols[0] if v_cols else df_loaded.columns[1]
            y_cols = [c for c in df_loaded.columns if c.lower() in ["converted", "conversion", "is_converted", "y", "target"]]
            y_col = y_cols[0] if y_cols else df_loaded.columns[2]

            groups = list(df_loaded[v_col].unique())
            g_a = df_loaded[df_loaded[v_col] == groups[0]]
            g_b = df_loaded[df_loaded[v_col] == groups[1]] if len(groups) > 1 else df_loaded[df_loaded[v_col] == groups[0]]

            real_sample_size_a = len(g_a)
            real_conversions_a = int(pd.to_numeric(g_a[y_col], errors="coerce").fillna(0).sum())
            real_sample_size_b = len(g_b)
            real_conversions_b = int(pd.to_numeric(g_b[y_col], errors="coerce").fillna(0).sum())

            cvr_obs_a = (real_conversions_a / real_sample_size_a * 100.0) if real_sample_size_a > 0 else 0.0
            cvr_obs_b = (real_conversions_b / real_sample_size_b * 100.0) if real_sample_size_b > 0 else 0.0

            # SRM (Sample Ratio Mismatch)
            expected_n = (real_sample_size_a + real_sample_size_b) / 2.0
            chi2_stat = ((real_sample_size_a - expected_n) ** 2 / expected_n) + ((real_sample_size_b - expected_n) ** 2 / expected_n)
            srm_p = 1.0 - stats.chi2.cdf(chi2_stat, df=1)

            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px; margin-top: 6px; font-size: 0.80rem;">
                    <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">{st.session_state.get('raw_df_name', 'Dataset')}</div>
                    <div><strong>A:</strong> {real_sample_size_a:,} users | {real_conversions_a:,} conv ({cvr_obs_a:.2f}%)</div>
                    <div><strong>B:</strong> {real_sample_size_b:,} users | {real_conversions_b:,} conv ({cvr_obs_b:.2f}%)</div>
                    <div style="margin-top: 4px; color: {'#166534' if srm_p >= 0.001 else '#991B1B'}; font-weight: 600;">
                        SRM: {'PASS (p=' + f'{srm_p:.3f}' + ')' if srm_p >= 0.001 else 'FAIL (Mismatch)'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            expected_lift = float(st.number_input("Planned Target Lift / MDE (%)", 0.1, 100.0, 12.0, 0.5))
            baseline_cvr = cvr_obs_a if cvr_obs_a > 0 else 10.0
            beta = 0.20
            posterior_samples = 100_000
            bandit_rounds = 20_000
        else:
            real_sample_size_a = 1000
            real_conversions_a = 100
            real_sample_size_b = 1000
            real_conversions_b = 120
            expected_lift = 12.0
            baseline_cvr = 10.0
            beta = 0.20
            posterior_samples = 100_000
            bandit_rounds = 20_000

    else:
        st.markdown("#### Observed Conversions")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            real_sample_size_a = st.number_input("Sample Size A", 10, 1_000_000, 1_000, 100)
            real_conversions_a = st.number_input("Conversions A", 0, real_sample_size_a, 100, 10)
        with col_s2:
            real_sample_size_b = st.number_input("Sample Size B", 10, 1_000_000, 1_000, 100)
            real_conversions_b = st.number_input("Conversions B", 0, real_sample_size_b, 120, 10)

        cvr_obs_a = (real_conversions_a / real_sample_size_a * 100.0) if real_sample_size_a > 0 else 0.0
        cvr_obs_b = (real_conversions_b / real_sample_size_b * 100.0) if real_sample_size_b > 0 else 0.0
        st.caption(f"Observed: **A: {cvr_obs_a:.2f}%** | **B: {cvr_obs_b:.2f}%**")

        expected_lift = st.number_input("Planned Target Lift / MDE (%)", 0.1, 100.0, 12.0, 0.5)
        baseline_cvr = cvr_obs_a if cvr_obs_a > 0 else 10.0
        beta = 0.20
        posterior_samples = 100_000
        bandit_rounds = 20_000

    st.markdown("---")
    st.markdown("### Commercial Levers & Audience Scale")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        rev_per_conv = st.number_input(
            "Rev / Conv ($)",
            min_value=1.0,
            max_value=10_000.0,
            step=1.0,
            format="%.1f",
            key="num_rev",
            on_change=set_custom_preset,
            help="Monetary revenue generated per conversion event.",
        )
    with col_r2:
        impl_cost = st.number_input(
            "Setup Cost ($)",
            min_value=0.0,
            max_value=500_000.0,
            step=100.0,
            format="%.0f",
            key="num_cost",
            on_change=set_custom_preset,
            help="Fixed engineering and setup deployment cost.",
        )
    traffic = st.number_input(
        "Projected Annual Traffic",
        min_value=1_000,
        max_value=100_000_000,
        step=10_000,
        format="%d",
        key="num_traffic",
        on_change=set_custom_preset,
        help="Estimated annual visitor traffic exposed to experiment.",
    )
    st.caption(f"Estimated Annual Audience: **{traffic:,.0f}** users")

# -----------------------------------------------------------------------------
# 5. Execute Experiment Analysis Service (Cached for Low Latency)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Computing causal inference metrics...", ttl=300)
def get_cached_analysis(
    b_cvr, exp_lift, a_val, b_val, post_samples, b_rounds,
    rss_a, rconv_a, rss_b, rconv_b,
    exp_mode, r_per_c, i_cost, proj_traffic
):
    return ExperimentDashboardService.run(
        baseline_conversion_rate=b_cvr,
        expected_lift=exp_lift,
        alpha=a_val,
        beta=b_val,
        posterior_samples=post_samples,
        bandit_rounds=b_rounds,
        real_sample_size_a=rss_a,
        real_conversions_a=rconv_a,
        real_sample_size_b=rss_b,
        real_conversions_b=rconv_b,
        mode=exp_mode,
        revenue_per_conversion=r_per_c,
        implementation_cost=i_cost,
        projected_traffic=proj_traffic,
    )


@st.cache_data(show_spinner="Computing CUPED adjustment...", ttl=300)
def get_cached_cuped(n_c, n_t, base_cvr, lift, corr, alpha_val):
    return ExperimentDashboardService.run_cuped_analysis(
        n_control=n_c,
        n_treatment=n_t,
        baseline_cvr=base_cvr,
        true_lift=lift,
        correlation=corr,
        alpha=alpha_val,
    )


@st.cache_data(show_spinner="Computing Delta Method ratio test...", ttl=300)
def get_cached_delta_method(n_users_c, n_users_t, base_ctr, lift, mean_sessions, alpha_val):
    return ExperimentDashboardService.run_delta_method_analysis(
        num_users_control=n_users_c,
        num_users_treatment=n_users_t,
        base_ctr=base_ctr,
        true_lift=lift,
        mean_sessions=mean_sessions,
        alpha=alpha_val,
    )


@st.cache_data(show_spinner="Simulating LinUCB Contextual Bandit...", ttl=300)
def get_cached_contextual_bandit(rounds, context_dim, alpha_val):
    return ExperimentDashboardService.run_contextual_bandit_simulation(
        n_rounds=rounds,
        context_dim=context_dim,
        alpha=alpha_val,
    )


analysis = get_cached_analysis(
    baseline_cvr,
    expected_lift,
    alpha,
    beta,
    posterior_samples,
    bandit_rounds,
    real_sample_size_a,
    real_conversions_a,
    real_sample_size_b,
    real_conversions_b,
    "simulation" if is_simulation else "real",
    rev_per_conv,
    impl_cost,
    traffic,
)

exp = analysis.experiment
freq = analysis.frequentist
seq = analysis.sequential
bayes = analysis.bayesian
rec = analysis.recommendation
fin = analysis.financials

p_pool = (exp["conversions_a"] + exp["conversions_b"]) / max(1, exp["sample_size_a"] + exp["sample_size_b"])
se_pool = np.sqrt(p_pool * (1.0 - p_pool) * (1.0 / max(1, exp["sample_size_a"]) + 1.0 / max(1, exp["sample_size_b"])))

point_gross = fin["gross_uplift"]
point_net = fin["net_benefit"]
point_roi = fin["roi"]

defensible_gross = traffic * seq["ci_lower"] * rev_per_conv
defensible_net = defensible_gross - impl_cost
defensible_roi = (defensible_net / impl_cost * 100.0) if impl_cost > 0 else 0.0

daily_gain = fin["gross_uplift"] / 365.0
breakeven_str = f"{int(np.ceil(impl_cost / daily_gain))} days" if daily_gain > 0 and impl_cost > 0 else ("0 days (no setup cost)" if impl_cost == 0 else "Indefinite")

seq_rel_lower = seq["ci_lower"] / max(1e-9, exp["conversion_rate_a"])
seq_rel_upper = seq["ci_upper"] / max(1e-9, exp["conversion_rate_a"])

# -----------------------------------------------------------------------------
# 6. Main Dashboard View
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="page-header">
        <h1 class="page-title">OptiSim // A/B Experimentation & Decision Studio</h1>
        <p class="page-subtitle">
            Enterprise causal inference with <strong>Anytime-Valid Confidence Sequences</strong>, 
            Bayesian Expected Loss, and <strong>Winner's Curse</strong> adjusted financial projections.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# High-Contrast Executive Verdict Banner
status_key = rec["status"]
if status_key == "success":
    badge_title = "CONVINCING WINNER"
    verdict_cls = "verdict-success"
    badge_cls = "badge-success"
elif status_key == "warning":
    badge_title = "INCONCLUSIVE EVIDENCE"
    verdict_cls = "verdict-warning"
    badge_cls = "badge-warning"
else:
    badge_title = "UNDERPERFORMING VARIANT"
    verdict_cls = "verdict-danger"
    badge_cls = "badge-danger"

st.markdown(
    f"""
    <div class="verdict-banner {verdict_cls}">
        <span class="verdict-badge {badge_cls}">{badge_title}</span>
        <h2 class="verdict-title">{rec['title']}</h2>
        <p class="verdict-message">{rec['message']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Executive Decision Memo & Institutional Governance Export
# -----------------------------------------------------------------------------
memo_markdown = f"""# OptiSim // Executive Experimentation Decision Memo

**Evaluation Timestamp:** Production Session Audit
**Target Metric:** Primary Conversion Rate (Bernoulli Unit Experiment)
**Total Sample Size:** {exp['sample_size_a'] + exp['sample_size_b']:,} observations (Control A: {exp['sample_size_a']:,} | Treatment B: {exp['sample_size_b']:,})

---

### 1. Executive Verdict & Operational Mandate
- **Classification:** **{badge_title}** — {rec['title']}
- **Core Directive:** {rec['message']}
- **Continuous Monitoring Audit:** Time-uniform confidence sequence (Waudby-Smith & Ramdas 2021) is **{'CONFIRMED CONCLUSIVE' if seq['is_conclusive'] else 'INCONCLUSIVE / ACCUMULATING EVIDENCE'}**. False positive rate is strictly bounded at $\\alpha = {alpha:.3f}$ under continuous peeking.

---

### 2. Multi-Engine Inferential Synthesis
| Metric / Parameter | Control (A) | Treatment (B) | Delta / Effect Size | Methodological Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Empirical CVR** | {exp['conversion_rate_a']:.2%} ({exp['conversions_a']:,} conv) | {exp['conversion_rate_b']:.2%} ({exp['conversions_b']:,} conv) | {freq['relative_lift']:+.2%} relative | Pooled SE: {se_pool:.5f} |
| **Fixed Horizon Z-Test** | — | — | Z = {freq['z_statistic']:.3f} | p = {freq['p_value']:.4e} ({'Significant' if freq['is_significant'] else 'Not Significant'} at $\\alpha={alpha:.2f}$) |
| **Anytime Confidence Sequence** | — | — | [{seq['ci_lower']*100:+.2f} pp, {seq['ci_upper']*100:+.2f} pp] | Rel Lift CS: [{seq_rel_lower:+.2%}, {seq_rel_upper:+.2%}] |
| **Bayesian Posterior** | — | — | P(B > A) = {bayes['probability_b_better']:.1%} | Expected Loss: {bayes['expected_loss_choose_b']:.5f} |

---

### 3. Commercial Impact & Winner's Curse Protection
- **Annual Traffic Projection:** {traffic:,} users
- **Contribution Margin:** ${rev_per_conv:,.2f} per conversion
- **Implementation Sunk Cost:** ${impl_cost:,.2f}
- **Observed Point Projection:** **${point_net:,.2f}** net return ({point_roi:.1f}% ROI) — *Subject to upward selection bias (Winner's Curse).*
- **Conservative Defensible Floor:** **${defensible_net:,.2f}** net return ({defensible_roi:.1f}% Defensible ROI) — *Guaranteed lower bound for fiscal accountability.*
- **Breakeven Horizon:** {breakeven_str}

---

### 4. Enterprise Governance & Sign-Off Checklist
- [ ] **Data Science Lead:** Sample ratio mismatch (SRM) verified, peeking penalty applied, SUTVA hold validated.
- [ ] **Platform / Infrastructure Architect:** Latency SLA impact (<35ms), edge cache invalidation, and kill-switch deployed.
- [ ] **Product VP / Commercial Sponsor:** Sign-off based on Conservative Defensible Floor (${defensible_net:,.2f}).
"""

with st.expander("Executive Decision Memo & Institutional Governance Export", expanded=False):
    st.markdown(
        """
        <div style="font-size: 0.88rem; color: #475569; margin-bottom: 10px;">
            Institutional-grade decision memo synthesizing causal inference, financial floor, and governance sign-off criteria for leadership and PRDs.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        label="Download Executive Decision Memo (.md)",
        data=memo_markdown,
        file_name="executive_decision_memo.md",
        mime="text/markdown",
    )
    st.markdown(memo_markdown)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Statistical Inference & Monitoring",
    "Financial Impact & Projections",
    "Adaptive Optimization & Bandits",
    "Methodology & Mathematical Foundations",
    "Decision Optimization & OR Lab",
])

# -----------------------------------------------------------------------------
# TAB 1: Statistical Inference & Monitoring
# -----------------------------------------------------------------------------
with tab1:
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(
            label="Control (A) CVR",
            value=f"{exp['conversion_rate_a']:.2%}",
            help=f"{exp['conversions_a']:,} conv / {exp['sample_size_a']:,} users",
        )
    with col_m2:
        st.metric(
            label="Treatment (B) CVR",
            value=f"{exp['conversion_rate_b']:.2%}",
            delta=f"{freq['relative_lift']:+.1%} vs A",
            help=f"{exp['conversions_b']:,} conv / {exp['sample_size_b']:,} users",
        )
    with col_m3:
        seq_status = "Peeking-Proof" if seq["is_conclusive"] else "Inconclusive"
        st.metric(
            label="Anytime Sequence",
            value=f"{seq['ci_lower']:+.2%} to {seq['ci_upper']:+.2%}",
            delta=seq_status,
            delta_color="normal" if seq["is_conclusive"] else "off",
            help="Waudby-Smith & Ramdas (2023) asymptotic confidence sequence. Continuous monitoring is valid.",
        )
    with col_m4:
        st.metric(
            label="Bayesian P(B > A)",
            value=f"{bayes['probability_b_better']:.1%}",
            delta=f"Loss: {bayes['expected_loss_choose_b']:.4f} pp",
            delta_color="inverse" if bayes['expected_loss_choose_b'] > 0.005 else "normal",
            help="Probability that B is better and the expected loss in conversion rate if B is mistakenly chosen.",
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Interval Width: Fixed vs. Anytime Sequence</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">The anytime sequence guarantees exact 95% coverage under continuous peeking.</div>
                <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                    <span><span style="color: #2563EB; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Confidence Sequence (Always-Valid)</span>
                    <span><span style="color: #94A3B8; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Fixed Wald CI (1 Look)</span>
                    <span><span style="color: #0F172A; font-weight: 900;">◆</span> Point Lift</span>
                    <span><span style="color: #DC2626; font-weight: 900;">┆</span> Null Line (0%)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            fig_ci = go.Figure()
            fig_ci.add_trace(go.Scatter(
                x=[freq["ci_lower"] * 100, freq["ci_upper"] * 100],
                y=["Fixed Wald CI (1 Look)", "Fixed Wald CI (1 Look)"],
                mode="lines+markers",
                name="Fixed Wald CI (1 Look)",
                line=dict(color="#94A3B8", width=5),
                marker=dict(size=12, symbol="line-ns", line_width=4),
                showlegend=False,
            ))
            fig_ci.add_trace(go.Scatter(
                x=[seq["ci_lower"] * 100, seq["ci_upper"] * 100],
                y=["Anytime Sequence (All Looks)", "Anytime Sequence (All Looks)"],
                mode="lines+markers",
                name="Confidence Sequence (Always-Valid)",
                line=dict(color="#2563EB", width=6),
                marker=dict(size=14, symbol="line-ns", line_width=5),
                showlegend=False,
            ))
            fig_ci.add_vline(
                x=0.0,
                line_dash="dash",
                line_color="#DC2626",
                line_width=1.5,
                annotation_text=" Null (0%) ",
                annotation_position="bottom right",
                annotation=dict(
                    bgcolor="#FEF2F2",
                    bordercolor="#FECACA",
                    borderwidth=1,
                    font=dict(color="#B91C1C", size=10, weight=600),
                    yshift=-2,
                ),
            )
            fig_ci.add_trace(go.Scatter(
                x=[freq["absolute_lift"] * 100],
                y=["Fixed Wald CI (1 Look)"],
                mode="markers",
                name="Point Lift",
                showlegend=False,
                marker=dict(size=11, color="#0F172A", symbol="diamond"),
            ))
            fig_ci.add_trace(go.Scatter(
                x=[freq["absolute_lift"] * 100],
                y=["Anytime Sequence (All Looks)"],
                mode="markers",
                name="Point Lift",
                showlegend=False,
                marker=dict(size=11, color="#0F172A", symbol="diamond"),
            ))
            fig_ci.update_layout(
                xaxis=dict(
                    title=dict(text="Absolute Conversion Rate Lift (percentage points)", standoff=12),
                    automargin=True,
                ),
                yaxis=dict(
                    range=[-0.5, 1.5],
                    tickfont=dict(color="#0F172A", size=11, weight=600),
                    automargin=True,
                ),
            )
            st.plotly_chart(format_chart(fig_ci, height=270), use_container_width=True)

    with col_g2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Bayesian Posterior Distributions</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Beta-Binomial conjugate posterior densities for Control (A) and Treatment (B).</div>
                <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                    <span><span style="display:inline-block; width:12px; height:12px; background:rgba(100, 116, 139, 0.4); border:1.5px solid #64748B; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Control (A) Posterior</span>
                    <span><span style="display:inline-block; width:12px; height:12px; background:rgba(37, 99, 235, 0.4); border:1.5px solid #2563EB; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Treatment (B) Posterior</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            alpha_a = 1.0 + exp["conversions_a"]
            beta_a = 1.0 + (exp["sample_size_a"] - exp["conversions_a"])
            alpha_b = 1.0 + exp["conversions_b"]
            beta_b = 1.0 + (exp["sample_size_b"] - exp["conversions_b"])

            x_min = max(0.0, min(exp["conversion_rate_a"], exp["conversion_rate_b"]) - 0.05)
            x_max = min(1.0, max(exp["conversion_rate_a"], exp["conversion_rate_b"]) + 0.05)
            x_grid = np.linspace(x_min, x_max, 300)

            pdf_a = stats.beta.pdf(x_grid, alpha_a, beta_a)
            pdf_b = stats.beta.pdf(x_grid, alpha_b, beta_b)
            max_pdf = max(float(np.max(pdf_a)), float(np.max(pdf_b)))

            fig_bayes = go.Figure()
            fig_bayes.add_trace(go.Scatter(
                x=x_grid * 100, y=pdf_a,
                mode="lines", name="Control (A)",
                line=dict(color="#64748B", width=2),
                fill="tozeroy", fillcolor="rgba(100, 116, 139, 0.08)",
                showlegend=False,
            ))
            fig_bayes.add_trace(go.Scatter(
                x=x_grid * 100, y=pdf_b,
                mode="lines", name="Treatment (B)",
                line=dict(color="#2563EB", width=2.5),
                fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.12)",
                showlegend=False,
            ))
            fig_bayes.update_layout(
                xaxis=dict(
                    title=dict(text="Conversion Rate (%)", standoff=12),
                    automargin=True,
                ),
                yaxis=dict(
                    title=dict(text="Probability Density", standoff=12),
                    range=[0, max_pdf * 1.20],
                    automargin=True,
                ),
            )
            st.plotly_chart(format_chart(fig_bayes, height=270), use_container_width=True)

    # 3. Sequential Monitoring Trajectory
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Anytime-Valid Sequential Trajectory Over Sample Size</div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Time-uniform confidence sequence envelope [Lₙ, Uₙ] narrowing as sample observations accumulate. Continuous monitoring is mathematically valid; early stopping occurs when Lₙ > 0%.</div>
            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                <span><span style="color: #2563EB; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Running Treatment Lift</span>
                <span><span style="color: #93C5FD; font-weight: 900; font-size: 1.1rem; line-height: 0;">┆</span> Confidence Sequence Envelope [Lₙ, Uₙ]</span>
                <span><span style="color: #DC2626; font-weight: 900;">┆</span> Null Horizon (0%)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if analysis.chart_data and analysis.chart_data.get("convergence"):
            conv_pts = analysis.chart_data["convergence"]
            x_n = [pt["sample_size"] for pt in conv_pts]
            y_lift = [pt.get("lift", (pt["cvr_b"] - pt["cvr_a"])) * 100.0 for pt in conv_pts]
            y_cs_low = [pt.get("cs_lower", 0.0) * 100.0 for pt in conv_pts]
            y_cs_high = [pt.get("cs_upper", 0.0) * 100.0 for pt in conv_pts]

            fig_seq_traj = go.Figure()
            fig_seq_traj.add_trace(go.Scatter(
                x=x_n, y=y_cs_high,
                mode="lines",
                line=dict(color="#93C5FD", width=1.5, dash="dash"),
                name="CS Upper (U_n)",
                showlegend=False,
            ))
            fig_seq_traj.add_trace(go.Scatter(
                x=x_n, y=y_cs_low,
                mode="lines",
                line=dict(color="#93C5FD", width=1.5, dash="dash"),
                fill="tonexty",
                fillcolor="rgba(37, 99, 235, 0.08)",
                name="CS Lower (L_n)",
                showlegend=False,
            ))
            fig_seq_traj.add_trace(go.Scatter(
                x=x_n, y=y_lift,
                mode="lines+markers",
                line=dict(color="#1D4ED8", width=2.5),
                marker=dict(size=4, color="#1D4ED8"),
                name="Running Lift",
                showlegend=False,
            ))
            fig_seq_traj.add_hline(
                y=0.0,
                line_dash="dash",
                line_color="#DC2626",
                line_width=1.5,
                annotation_text=" Null (0%) ",
                annotation_position="bottom right",
                annotation=dict(bgcolor="#FEF2F2", bordercolor="#FECACA", borderwidth=1, font=dict(color="#B91C1C", size=10, weight=600)),
            )
            fig_seq_traj.update_layout(
                xaxis=dict(title=dict(text="Evaluated Sample Size (Users)", standoff=12), automargin=True),
                yaxis=dict(title=dict(text="Absolute Lift (percentage points)", standoff=12), automargin=True),
            )
            st.plotly_chart(format_chart(fig_seq_traj, height=270), use_container_width=True)

    # 4. Statistical Diagnostics & Audit Table
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Statistical Diagnostics & Methodological Audit Table</div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">Detailed audit parameters across Frequentist, Sequential, and Bayesian decision frameworks.</div>
            """,
            unsafe_allow_html=True,
        )
        p_pool = (exp["conversions_a"] + exp["conversions_b"]) / max(1, exp["sample_size_a"] + exp["sample_size_b"])
        se_pool = np.sqrt(p_pool * (1.0 - p_pool) * (1.0 / max(1, exp["sample_size_a"]) + 1.0 / max(1, exp["sample_size_b"])))

        audit_data = {
            "Statistical Metric": [
                "Evaluated Sample Size (N)",
                "Observed Conversions (C)",
                "Empirical Conversion Rate (CVR)",
                "Absolute Effect Size (ATE)",
                "Relative Lift (%)",
                "Pooled Standard Error (SE)",
                "Test Statistic (Z-Score)",
                "Two-Tailed P-Value",
                "95% Fixed Wald CI (1 Look)",
                "95% Anytime Confidence Sequence",
                "Bayesian P(Treatment > Control)",
                "Bayesian Expected Loss (Risk)",
                "Required Sample Size per Arm (n*)",
                "Design Significance Level (α)",
                "Design Statistical Power (1 - β)",
            ],
            "Control (A)": [
                f"{exp['sample_size_a']:,}",
                f"{exp['conversions_a']:,}",
                f"{exp['conversion_rate_a']:.2%}",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
                f"{analysis.required_sample_size:,}" if analysis.required_sample_size > 0 else "N/A",
                f"{alpha:.3f}",
                f"{(1.0 - beta)*100:.0f}%",
            ],
            "Treatment (B)": [
                f"{exp['sample_size_b']:,}",
                f"{exp['conversions_b']:,}",
                f"{exp['conversion_rate_b']:.2%}",
                f"{freq['absolute_lift']*100:+.2f} pp",
                f"{freq['relative_lift']:+.2%}",
                f"{se_pool:.5f}",
                f"z = {freq['z_statistic']:.3f}",
                f"p = {freq['p_value']:.4e}",
                f"[{freq['ci_lower']*100:+.2f}%, {freq['ci_upper']*100:+.2f}%]",
                f"[{seq['ci_lower']*100:+.2f}%, {seq['ci_upper']*100:+.2f}%]",
                f"{bayes['probability_b_better']:.2%}",
                f"{bayes['expected_loss_choose_b']:.5f} pp",
                f"{analysis.required_sample_size:,}" if analysis.required_sample_size > 0 else "N/A",
                f"{alpha:.3f}",
                f"{(1.0 - beta)*100:.0f}%",
            ],
            "Methodological Engine": [
                "Empirical Observations",
                "Bernoulli Success Count",
                "Maximum Likelihood Estimator",
                "Point Difference (p̂_B - p̂_A)",
                "Relative Uplift Rate",
                "Pooled Variance Normal Approximation",
                "Two-Proportion Z-Test",
                "Standard Normal Cumulative Tail",
                "Fixed Horizon (Invalid under peeking)",
                "Waudby-Smith & Ramdas (2023) Time-Uniform",
                "Beta-Binomial Conjugate Posterior",
                "Bayesian Decision Theory (Stucchio 2015)",
                "Lehr (1992) Power Sizing Formula",
                "Type I Error Budget",
                "Type II Error Complement",
            ]
        }
        df_audit = pd.DataFrame(audit_data)
        st.dataframe(df_audit, hide_index=True, use_container_width=True)

    # 5. Statistical Power & MDE Sensitivity Sizing Curve
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Statistical Power & Minimum Detectable Effect (MDE) Sizing Curve</div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Required sample size per variation across detectable effect sizes (MDE). Smaller effects require exponentially larger audiences.</div>
            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                <span><span style="color: #2563EB; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Required Sample Size Curve (n*)</span>
                <span><span style="color: #0F172A; font-weight: 900;">◆</span> Current Planned MDE</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        base_rate = max(0.005, exp["conversion_rate_a"])
        mde_grid = np.linspace(0.02, 0.25, 30)
        req_grid = [
            StatsEngine.required_sample_size_per_variation(
                baseline_conversion_rate=base_rate,
                minimum_detectable_effect=float(m),
                alpha=alpha,
                beta=beta,
            )
            for m in mde_grid
        ]
        curr_mde = abs(float(expected_lift)) / 100.0 if expected_lift is not None and abs(expected_lift) > 0.01 else 0.12
        curr_req = StatsEngine.required_sample_size_per_variation(
            baseline_conversion_rate=base_rate,
            minimum_detectable_effect=curr_mde,
            alpha=alpha,
            beta=beta,
        )

        fig_pwr = go.Figure()
        fig_pwr.add_trace(go.Scatter(
            x=mde_grid * 100.0,
            y=req_grid,
            mode="lines",
            line=dict(color="#2563EB", width=2.5),
            name="Required Sample Size",
            showlegend=False,
        ))
        fig_pwr.add_trace(go.Scatter(
            x=[curr_mde * 100.0],
            y=[curr_req],
            mode="markers",
            marker=dict(size=12, color="#0F172A", symbol="diamond"),
            name="Current Plan",
            showlegend=False,
        ))
        fig_pwr.update_layout(
            xaxis=dict(title=dict(text="Minimum Detectable Effect (Relative Lift %)", standoff=12), automargin=True),
            yaxis=dict(title=dict(text="Required Sample Size per Variation", standoff=12), automargin=True),
        )
        st.plotly_chart(format_chart(fig_pwr, height=270), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: Financial Impact & Winner's Curse Studio
# -----------------------------------------------------------------------------
with tab2:
    st.markdown(
        """
        <div class="callout-box">
            <div class="callout-title">Decision Risk: The Winner's Curse in Experiment Selection</div>
            <p class="callout-text">
                When an experiment is selected for roll-out <strong>because</strong> it achieved statistical significance (p &lt; 0.05), 
                the observed point-estimate lift is <strong>systematically biased upwards</strong>. Favorable random variation helped it cross the bar. 
                Relying on observed point estimates leads to missed revenue targets. OptiSim calculates the 
                <strong>Conservative Defensible Floor</strong> using the anytime sequence lower bound.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    point_gross = fin["gross_uplift"]
    point_net = fin["net_benefit"]
    point_roi = fin["roi"]

    defensible_gross = traffic * seq["ci_lower"] * rev_per_conv
    defensible_net = defensible_gross - impl_cost
    defensible_roi = (defensible_net / impl_cost * 100.0) if impl_cost > 0 else 0.0

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric(
            label="Observed Point Net Return",
            value=f"${point_net:,.2f}",
            delta=f"{point_roi:.1f}% ROI",
            help="Based on observed sample mean difference. Highly vulnerable to Winner's Curse.",
        )
    with col_f2:
        st.metric(
            label="Defensible Floor (Net)",
            value=f"${defensible_net:,.2f}",
            delta=f"{defensible_roi:.1f}% Defensible ROI",
            delta_color="normal" if defensible_net > 0 else "inverse",
            help="Anchored to the lower bound of the confidence sequence. Insulates against Winner's Curse.",
        )
    with col_f3:
        st.metric(
            label="Setup Cost",
            value=f"${impl_cost:,.2f}",
            delta=f"{traffic:,} Annual Traffic",
            delta_color="off",
            help="One-off engineering setup cost required to deploy Variant B.",
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Financial Viability: Point Estimate vs. Defensible Floor</div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Comparison of annual revenue projections under naive point estimates vs. conservative lower-bound adjustments.</div>
            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                <span><span style="display:inline-block; width:12px; height:12px; background:#3B82F6; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Gross Uplift ($)</span>
                <span><span style="display:inline-block; width:12px; height:12px; background:#10B981; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Net Benefit ($)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_fin = go.Figure()
        fig_fin.add_trace(go.Bar(
            name="Gross Uplift ($)",
            x=["Observed Point<br>Estimate", "Conservative Defensible<br>Floor (CI Lower)"],
            y=[point_gross, max(0.0, defensible_gross)],
            marker_color=["#93C5FD", "#3B82F6"],
            showlegend=False,
        ))
        fig_fin.add_trace(go.Bar(
            name="Net Benefit ($)",
            x=["Observed Point<br>Estimate", "Conservative Defensible<br>Floor (CI Lower)"],
            y=[point_net, defensible_net],
            marker_color=["#10B981" if point_net > 0 else "#EF4444", "#059669" if defensible_net > 0 else "#DC2626"],
            showlegend=False,
        ))
        fig_fin.add_hline(y=0.0, line_dash="dash", line_color="#64748B")
        fig_fin.update_layout(
            barmode="group",
            yaxis=dict(title=dict(text="Annual Financial Impact ($)", standoff=12), automargin=True),
            xaxis=dict(tickfont=dict(size=12, color="#0F172A", weight=600), automargin=True),
        )
        st.plotly_chart(format_chart(fig_fin, height=330), use_container_width=True)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# TAB 3: Bandits & Personalization Lab
# -----------------------------------------------------------------------------
with tab3:
    algo_mode = st.radio(
        "Optimization Framework",
        options=["Bernoulli Thompson Sampling (MAB)", "LinUCB Contextual Bandit (Personalized)"],
        horizontal=True,
        help="Compare classical multi-armed exploration vs user-context-aware ridge regression personalization.",
    )

    if algo_mode == "Bernoulli Thompson Sampling (MAB)":
        if is_simulation and analysis.bandit is not None:
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                st.metric("Total Bandit Rounds", f"{bandit_rounds:,}")
            with col_b2:
                st.metric("Conversions Earned", f"{analysis.bandit['cumulative_reward']:,}")
            with col_b3:
                st.metric(
                    "Cumulative Regret",
                    f"{analysis.bandit['regret']:.1f} missed",
                    help="The opportunity cost of serving sub-optimal variants during dynamic exploration.",
                )

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            col_s1, col_s2 = st.columns(2)
            chart_data = analysis.chart_data
            with col_s1:
                with st.container(border=True):
                    st.markdown(
                        """
                        <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Monte Carlo Convergence Path</div>
                        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Empirical conversion rates fluctuating and stabilizing toward truth as sample size grows.</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                            <span><span style="color: #64748B; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Group A Convergence</span>
                            <span><span style="color: #2563EB; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Group B Convergence</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if chart_data and chart_data.get("convergence"):
                        conv_data = chart_data["convergence"]
                        s_sizes = [pt["sample_size"] for pt in conv_data]
                        cvr_as = [pt["cvr_a"] * 100 for pt in conv_data]
                        cvr_bs = [pt["cvr_b"] * 100 for pt in conv_data]

                        fig_conv = go.Figure()
                        fig_conv.add_trace(go.Scatter(x=s_sizes, y=cvr_as, mode="lines", name="Group A Convergence", line=dict(color="#64748B", width=2), showlegend=False))
                        fig_conv.add_trace(go.Scatter(x=s_sizes, y=cvr_bs, mode="lines", name="Group B Convergence", line=dict(color="#2563EB", width=2.5), showlegend=False))
                        fig_conv.update_layout(
                            xaxis=dict(title=dict(text="Evaluated Sample Size", standoff=12), automargin=True),
                            yaxis=dict(title=dict(text="Empirical CVR (%)", standoff=12), automargin=True),
                        )
                        st.plotly_chart(format_chart(fig_conv, height=270), use_container_width=True)

            with col_s2:
                with st.container(border=True):
                    st.markdown(
                        """
                        <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Thompson Sampling Cumulative Regret</div>
                        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Sub-linear regret growth as Thompson Sampling dynamically routes traffic to the winning arm.</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                            <span><span style="color: #D97706; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Thompson Sampling Cumulative Regret</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if chart_data and chart_data.get("bandit"):
                        b_data = chart_data["bandit"]
                        rounds = [pt["round"] for pt in b_data]
                        regrets = [pt["regret"] for pt in b_data]

                        fig_regret = go.Figure()
                        fig_regret.add_trace(go.Scatter(
                            x=rounds, y=regrets,
                            mode="lines", name="Thompson Sampling Regret",
                            line=dict(color="#D97706", width=2.5),
                            fill="tozeroy", fillcolor="rgba(217, 119, 6, 0.08)",
                            showlegend=False,
                        ))
                        fig_regret.update_layout(
                            xaxis=dict(title=dict(text="Customer Arrival Round", standoff=12), automargin=True),
                            yaxis=dict(title=dict(text="Cumulative Regret (Missed Conversions)", standoff=12), automargin=True),
                        )
                        st.plotly_chart(format_chart(fig_regret, height=270), use_container_width=True)
        else:
            st.info("Switch to **Plan & Simulate Mode** in the sidebar to simulate live Monte Carlo convergence paths and multi-armed bandit regret curves.")

    else:
        # LinUCB Contextual Bandit Mode
        ctx_res = get_cached_contextual_bandit(rounds=max(1000, bandit_rounds), context_dim=3, alpha_val=1.0)
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.metric("Contextual Rounds", f"{ctx_res.rounds:,}")
        with col_c2:
            st.metric("Active Personalization Arms", f"{ctx_res.num_arms} Variants")
        with col_c3:
            st.metric("Conversions Earned", f"{int(ctx_res.cumulative_reward):,}")
        with col_c4:
            st.metric(
                "Cumulative Regret",
                f"{ctx_res.cumulative_regret:.1f} missed",
                help="Regret minimized by conditioning arm selection on user context (mobile, intent, tier).",
            )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        col_c_g1, col_c_g2 = st.columns(2)
        with col_c_g1:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">LinUCB Dynamic Regret Curve</div>
                    <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Sub-linear regret as ridge regression learns personalized context weights.</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                        <span><span style="color: #7C3AED; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Contextual LinUCB Regret</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                fig_ctx_reg = go.Figure()
                fig_ctx_reg.add_trace(go.Scatter(
                    x=ctx_res.history_rounds,
                    y=ctx_res.history_regrets,
                    mode="lines",
                    name="LinUCB Regret",
                    line=dict(color="#7C3AED", width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(124, 58, 237, 0.08)",
                    showlegend=False,
                ))
                fig_ctx_reg.update_layout(
                    xaxis=dict(title=dict(text="Arrival Round", standoff=12), automargin=True),
                    yaxis=dict(title=dict(text="Cumulative Regret", standoff=12), automargin=True),
                )
                st.plotly_chart(format_chart(fig_ctx_reg, height=270), use_container_width=True)

        with col_c_g2:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Personalized Arm Allocation</div>
                    <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;">Traffic distribution routed by contextual user segment affinity.</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                        <span><span style="display:inline-block; width:12px; height:12px; background:#6366F1; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> User Pulls</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                fig_ctx_pulls = go.Figure()
                arms_list = list(ctx_res.arm_pull_counts.keys())
                pulls_list = [ctx_res.arm_pull_counts[a] for a in arms_list]
                display_arms = [a.replace("_", " ").title() for a in arms_list]

                fig_ctx_pulls.add_trace(go.Bar(
                    x=display_arms,
                    y=pulls_list,
                    marker_color=["#6366F1", "#3B82F6", "#06B6D4"],
                    showlegend=False,
                ))
                fig_ctx_pulls.update_layout(
                    xaxis=dict(tickfont=dict(size=12, color="#0F172A", weight=600), automargin=True),
                    yaxis=dict(title=dict(text="Total User Allocations", standoff=12), automargin=True),
                )
                st.plotly_chart(format_chart(fig_ctx_pulls, height=270), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: Advanced Methodology & Rigor
# -----------------------------------------------------------------------------
with tab4:
    # 1. Interactive CUPED Variance Reduction Studio
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">CUPED Studio: Variance Reduction via Pre-Experiment Covariates</div>
            <div style="font-size: 0.85rem; color: #475569; margin-bottom: 12px;">
                CUPED (Deng et al., 2013) utilizes historical pre-experiment data (e.g. past user spend or baseline activity) 
                to strip away pre-existing variation: <strong>Y<sub>adj</sub> = Y - θ(X - E[X])</strong>. 
                Variance is reduced by <strong>(1 - ρ²)</strong>, reducing required traffic by 30% to 50% without altering the unbiased treatment effect.
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_loaded = st.session_state.get("raw_df")
        has_csv_cov = (
            df_loaded is not None 
            and any(c.lower() in ["pre_spend", "pre_metric", "covariate"] for c in df_loaded.columns)
            and any(c.lower() in ["variant", "group", "arm", "treatment"] for c in df_loaded.columns)
        )

        col_cuped_ctrl1, col_cuped_ctrl2 = st.columns([3, 2])
        with col_cuped_ctrl1:
            cuped_preset = st.segmented_control(
                "Covariate Correlation (ρ)",
                options=["0.30 (Weak)", "0.60 (Typical)", "0.80 (Strong)", "Custom"],
                default="0.60 (Typical)",
                help="Pre-experiment correlation ρ with the primary metric. Higher correlation yields larger variance reduction.",
            )
            if cuped_preset == "0.30 (Weak)":
                cuped_rho = 0.30
            elif cuped_preset == "0.60 (Typical)":
                cuped_rho = 0.60
            elif cuped_preset == "0.80 (Strong)":
                cuped_rho = 0.80
            else:
                cuped_rho = st.number_input("Custom Correlation (ρ)", 0.00, 0.95, 0.60, 0.05, format="%.2f")
        with col_cuped_ctrl2:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            if has_csv_cov:
                st.caption("Active Mode: Utilizing uploaded dataset pre-experiment spend column.")
            else:
                st.caption(f"Theoretical Sample Size Savings: **{cuped_rho**2 * 100:.1f}%** (Noise reduction: 1 - ρ²)")

        if has_csv_cov:
            v_col = [c for c in df_loaded.columns if c.lower() in ["variant", "group", "arm", "treatment"]][0]
            x_col = [c for c in df_loaded.columns if c.lower() in ["pre_spend", "pre_metric", "covariate"]][0]
            y_col = [c for c in df_loaded.columns if c.lower() in ["converted", "conversion", "is_converted", "y", "target"]][0]
            groups = list(df_loaded[v_col].unique())
            y_c = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[0]][y_col], errors="coerce").fillna(0).values
            y_t = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[1]][y_col], errors="coerce").fillna(0).values
            x_c = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[0]][x_col], errors="coerce").fillna(0).values
            x_t = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[1]][x_col], errors="coerce").fillna(0).values
            cuped_result = CUPEDEngine.compute(y_c, y_t, x_c, x_t, alpha=alpha)
        else:
            cuped_result, _ = get_cached_cuped(
                n_c=5000,
                n_t=5000,
                base_cvr=exp["conversion_rate_a"],
                lift=freq["absolute_lift"],
                corr=cuped_rho,
                alpha_val=alpha,
            )

        col_cp1, col_cp2, col_cp3, col_cp4 = st.columns(4)
        with col_cp1:
            st.metric("Empirical Corr (ρ)", f"{cuped_result.correlation:.2f}")
        with col_cp2:
            st.metric("Variance Reduction", f"{cuped_result.variance_reduction_pct:.1f}%", delta="Noise Removed", delta_color="normal")
        with col_cp3:
            st.metric("Sample Size Savings", f"{cuped_result.sample_size_savings_pct:.1f}%", delta="Faster Experiments", delta_color="normal")
        with col_cp4:
            st.metric("Adjusted P-Value", f"{cuped_result.p_value:.4f}", delta="CUPED Inference", delta_color="normal" if cuped_result.is_significant else "off")

        # Visualizing Raw vs CUPED Interval
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 6px;">
                <span><span style="color: #94A3B8; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> Raw Unadjusted Confidence Interval</span>
                <span><span style="color: #059669; font-weight: 900; font-size: 1.1rem; line-height: 0;">━</span> CUPED Variance-Reduced Confidence Interval</span>
                <span><span style="color: #0F172A; font-weight: 900;">◆</span> Point Lift</span>
                <span><span style="color: #DC2626; font-weight: 900;">┆</span> Null Line (0%)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        z_crit = stats.norm.ppf(1.0 - alpha / 2.0)
        raw_se = np.sqrt(cuped_result.raw_variance)
        raw_ci_low = (cuped_result.raw_lift - z_crit * raw_se) * 100.0
        raw_ci_high = (cuped_result.raw_lift + z_crit * raw_se) * 100.0

        adj_ci_low = cuped_result.ci_lower * 100.0
        adj_ci_high = cuped_result.ci_upper * 100.0

        fig_cuped = go.Figure()
        fig_cuped.add_trace(go.Scatter(
            x=[raw_ci_low, raw_ci_high],
            y=["Raw Unadjusted", "Raw Unadjusted"],
            mode="lines+markers",
            line=dict(color="#94A3B8", width=5),
            marker=dict(size=12, symbol="line-ns", line_width=4),
            showlegend=False,
        ))
        fig_cuped.add_trace(go.Scatter(
            x=[adj_ci_low, adj_ci_high],
            y=["CUPED Adjusted", "CUPED Adjusted"],
            mode="lines+markers",
            line=dict(color="#059669", width=6),
            marker=dict(size=14, symbol="line-ns", line_width=5),
            showlegend=False,
        ))
        fig_cuped.add_vline(
            x=0.0,
            line_dash="dash",
            line_color="#DC2626",
            line_width=1.5,
            annotation_text=" Null (0%) ",
            annotation_position="bottom right",
            annotation=dict(bgcolor="#FEF2F2", bordercolor="#FECACA", borderwidth=1, font=dict(color="#B91C1C", size=10, weight=600)),
        )
        fig_cuped.add_trace(go.Scatter(
            x=[cuped_result.raw_lift * 100.0],
            y=["Raw Unadjusted"],
            mode="markers",
            marker=dict(size=11, color="#0F172A", symbol="diamond"),
            showlegend=False,
        ))
        fig_cuped.add_trace(go.Scatter(
            x=[cuped_result.adjusted_lift * 100.0],
            y=["CUPED Adjusted"],
            mode="markers",
            marker=dict(size=11, color="#0F172A", symbol="diamond"),
            showlegend=False,
        ))
        fig_cuped.update_layout(
            xaxis=dict(title=dict(text="Treatment Effect Lift (percentage points)", standoff=12), automargin=True),
            yaxis=dict(range=[-0.5, 1.5], tickfont=dict(color="#0F172A", size=11, weight=600), automargin=True),
        )
        st.plotly_chart(format_chart(fig_cuped, height=230), use_container_width=True)

    # 2. Interactive Delta Method Clustered Ratio Studio
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">Delta Method: Clustered Ratio Metrics</div>
            <div style="font-size: 0.85rem; color: #475569; margin-bottom: 12px;">
                Online experiments frequently evaluate ratio metrics (e.g. CTR = Total Clicks / Total Sessions). 
                Because the unit of randomization is the user but metrics occur across multiple sessions per user, observations are clustered. 
                Treating sessions as independent violates i.i.d. assumptions and severely underestimates standard errors. 
                The <strong>Delta Method (Deng et al., 2018)</strong> uses a Taylor series expansion to produce honest, cluster-robust standard errors.
            </div>
            """,
            unsafe_allow_html=True,
        )

        has_csv_cluster = (
            df_loaded is not None
            and any(c.lower() in ["sessions", "visits"] for c in df_loaded.columns)
            and any(c.lower() in ["clicks", "events"] for c in df_loaded.columns)
            and any(c.lower() in ["variant", "group", "arm", "treatment"] for c in df_loaded.columns)
        )

        col_delta_ctrl1, col_delta_ctrl2 = st.columns([3, 2])
        with col_delta_ctrl1:
            delta_preset = st.segmented_control(
                "Sessions per User (Cluster Intensity)",
                options=["2.0 (Low)", "5.0 (Moderate)", "8.0 (High)", "Custom"],
                default="5.0 (Moderate)",
                help="Average sessions per user. Higher values induce stronger clustering variance.",
            )
            if delta_preset == "2.0 (Low)":
                mean_sessions = 2.0
            elif delta_preset == "5.0 (Moderate)":
                mean_sessions = 5.0
            elif delta_preset == "8.0 (High)":
                mean_sessions = 8.0
            else:
                mean_sessions = st.number_input("Custom Mean Sessions", 1.0, 20.0, 5.0, 0.5, format="%.1f")
        with col_delta_ctrl2:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            if has_csv_cluster:
                st.caption("Active Mode: Utilizing uploaded dataset user session clusters.")
            else:
                st.caption("Unit of Randomization: User | Metric Unit: Session")

        if has_csv_cluster:
            v_col = [c for c in df_loaded.columns if c.lower() in ["variant", "group", "arm", "treatment"]][0]
            s_col = [c for c in df_loaded.columns if c.lower() in ["sessions", "visits"]][0]
            c_col = [c for c in df_loaded.columns if c.lower() in ["clicks", "events"]][0]
            groups = list(df_loaded[v_col].unique())
            c_c = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[0]][c_col], errors="coerce").fillna(0).values
            n_c = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[0]][s_col], errors="coerce").fillna(1).values
            c_t = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[1]][c_col], errors="coerce").fillna(0).values
            n_t = pd.to_numeric(df_loaded[df_loaded[v_col] == groups[1]][s_col], errors="coerce").fillna(1).values
            delta_res = DeltaMethodEngine.compute(c_c, n_c, c_t, n_t, alpha=alpha)
            sum_c_c, sum_n_c = float(np.sum(c_c)), float(np.sum(n_c))
            sum_c_t, sum_n_t = float(np.sum(c_t)), float(np.sum(n_t))
            p_c = sum_c_c / sum_n_c if sum_n_c > 0 else 0.0
            p_t = sum_c_t / sum_n_t if sum_n_t > 0 else 0.0
            naive_se = np.sqrt(p_c * (1.0 - p_c) / sum_n_c + p_t * (1.0 - p_t) / sum_n_t)
            delta_comp = {
                "naive_se": float(naive_se),
                "robust_se": float(delta_res.se_difference),
                "variance_inflation_factor": float(delta_res.se_difference / naive_se) if naive_se > 0 else 1.0,
            }
        else:
            delta_res, delta_comp = get_cached_delta_method(
                n_users_c=1000,
                n_users_t=1000,
                base_ctr=0.08,
                lift=0.015,
                mean_sessions=mean_sessions,
                alpha_val=alpha,
            )

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Naive Pooled SE", f"{delta_comp['naive_se']:.5f}", help="Underestimates variance by assuming sessions are independent.")
        with col_d2:
            st.metric("Delta Method Robust SE", f"{delta_comp['robust_se']:.5f}", help="Honest asymptotic standard error with user clustering.")
        with col_d3:
            vif = delta_comp['variance_inflation_factor']
            st.metric("Variance Inflation Factor", f"{vif:.2f}x", delta=f"+{(vif - 1.0)*100:.0f}% SE penalty", delta_color="inverse")

    # 3. Mathematical Foundations & Complete Theoretical Compendium
    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">Complete Mathematical Compendium & Asymptotic Guarantees</div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 2px;">
                        Rigorous formulations, parameter dictionaries, and theoretical proofs across all 7 causal inference and optimization engines in OptiSim.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        MATH_TOPICS = [
            "1. Sequential Confidence Sequences",
            "2. CUPED Variance Reduction",
            "3. Clustered Delta Method",
            "4. Bayesian Decision Theory",
            "5. Contextual LinUCB Bandits",
            "6. Frequentist Hypothesis & Power",
            "7. Commercial Value & ROI",
        ]

        if "math_topic" not in st.session_state or st.session_state["math_topic"] not in MATH_TOPICS:
            st.session_state["math_topic"] = MATH_TOPICS[0]

        def go_prev_topic():
            cur = MATH_TOPICS.index(st.session_state["math_topic"])
            st.session_state["math_topic"] = MATH_TOPICS[(cur - 1) % len(MATH_TOPICS)]

        def go_next_topic():
            cur = MATH_TOPICS.index(st.session_state["math_topic"])
            st.session_state["math_topic"] = MATH_TOPICS[(cur + 1) % len(MATH_TOPICS)]

        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">Complete Mathematical Compendium</span>
                    <span style="background: #2563EB; color: #FFFFFF; font-size: 0.76rem; font-weight: 700; padding: 2px 10px; border-radius: 9999px;">
                        7 Core Modules (1 to 7)
                    </span>
                </div>
                <div style="font-size: 0.82rem; color: #64748B;">
                    Select any module below or use Previous / Next to inspect formulations
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.pills(
            "Mathematical Engine",
            options=MATH_TOPICS,
            key="math_topic",
            label_visibility="collapsed",
        )

        curr_idx = MATH_TOPICS.index(st.session_state["math_topic"])

        # Visual progress dots and stepper bar
        dots_html = "".join([
            f'<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background-color:{"#2563EB" if i == curr_idx else "#CBD5E1"}; margin: 0 4px; transition: background-color 0.2s;"></span>'
            for i in range(len(MATH_TOPICS))
        ])

        col_nav_l, col_nav_c, col_nav_r = st.columns([1, 2, 1])
        with col_nav_l:
            prev_num = (curr_idx - 1) % len(MATH_TOPICS) + 1
            st.button(f"Previous ({prev_num}/7)", on_click=go_prev_topic, key="btn_prev_math", width="stretch")
        with col_nav_c:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 2px 0;">
                    <div style="margin-bottom: 3px;">{dots_html}</div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #475569;">
                        Module <strong>{curr_idx + 1} of 7</strong>: <span style="color: #0F172A; font-weight: 700;">{MATH_TOPICS[curr_idx].split('. ', 1)[1]}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_nav_r:
            next_num = (curr_idx + 1) % len(MATH_TOPICS) + 1
            st.button(f"Next ({next_num}/7)", on_click=go_next_topic, key="btn_next_math", width="stretch")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        if curr_idx == 0:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Anytime-Valid Confidence Sequences (Waudby-Smith & Ramdas, 2023)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"Estimating means of bounded random variables by the time-uniform Chernoff bound"</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **Confidence Sequence Envelope Formulation:**

                $$\text{CS}_n = \left[ \hat{\delta}_n \pm W_n \right]$$

                $$W_n = \sigma \sqrt{\frac{2(n\rho^2 + 1)}{n^2 \rho^2} \log\left(\frac{\sqrt{n\rho^2 + 1}}{\alpha}\right)}$$

                **Time-Uniform Guarantee (Ville's Martingale Inequality):**

                $$\mathbb{P}\left(\exists n \ge 1: \; \delta^* \notin \text{CS}_n\right) \le \alpha \iff \mathbb{P}\left(\forall n \ge 1: \; \delta^* \in \text{CS}_n\right) \ge 1 - \alpha$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $\hat{\delta}_n$ | Empirical Lift | Point estimate $\hat{p}_{B,n} - \hat{p}_{A,n}$ observed at arbitrary sample size $n$. |
                | $\delta^*$ | True Population Lift | Unobserved ground-truth average treatment effect (ATE). |
                | $W_n$ | Half-Width Radius | Time-uniform confidence envelope shrinking at optimal rate $\mathcal{O}\left(\sqrt{\frac{\log n}{n}}\right)$. |
                | $\sigma$ | Sub-Gaussian Proxy | Sub-Gaussian parameter proxy: $\sqrt{p(1-p)}$ for Bernoulli conversion trials. |
                | $\rho$ | Intrinsic Tuning Horizon | Tuning scalar calibrated for minimal boundary width around target sample size $N^*$. |
                | $\alpha$ | Family-Wise Error Rate | Type I error probability guaranteed across continuous monitoring (e.g. $\alpha = 0.05$). |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        In standard fixed-horizon A/B testing, checking the dashboard daily ("peeking") inflates false positive discovery rates from 5% to over 30%. Non-negative supermartingales guarantee that practitioners can monitor dashboards continuously and stop as soon as 0 ∉ CSₙ without invalidating statistical error guarantees.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif curr_idx == 1:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    CUPED: Controlled-Experiment Using Pre-Experiment Data (Deng et al., 2013)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data" (Microsoft Research)</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **De-Noised Metric & Optimal Covariate Weight:**

                $$Y_{\text{adj}} = Y - \theta^*(X - \mathbb{E}[X])$$

                $$\theta^* = \frac{\text{Cov}(Y, X)}{\text{Var}(X)} = \rho_{XY} \frac{\sigma_Y}{\sigma_X}$$

                **Variance Reduction Theorem & Traffic Savings:**

                $$\text{Var}(Y_{\text{adj}}) = \text{Var}(Y) \cdot (1 - \rho_{XY}^2)$$

                $$N_{\text{CUPED}} = N_{\text{raw}} \cdot (1 - \rho_{XY}^2) \implies \text{Traffic Savings} = \rho_{XY}^2 \times 100\%$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $Y$ | Primary Outcome Metric | Post-treatment metric per user (e.g. conversions or revenue during test window). |
                | $X$ | Pre-Experiment Covariate | Pre-existing baseline metric measured *before* test exposure (e.g. past 14-day spend). |
                | $\theta^*$ | Optimal OLS Scalar | Linear regression slope coefficient that strictly minimizes $\text{Var}(Y_{\text{adj}})$. |
                | $\rho_{XY}$ | Covariate Correlation | Pearson correlation between pre-experiment baseline $X$ and test outcome $Y$. |
                | $Y_{\text{adj}}$ | De-Noised Estimator | Adjusted metric with identical expectation ($\mathbb{E}[Y_{\text{adj}}] = \mathbb{E}[Y]$) but lower variance. |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        Natural user variance (e.g. whale spenders vs casual users) creates massive random noise. CUPED partials out baseline pre-experiment variance. At ρ = 0.60, required sample size drops by 36%—allowing teams to ship decisions in 9 days instead of 14 days with zero risk of bias.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif curr_idx == 2:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Clustered Delta Method for Ratio Metrics (Deng et al., 2018)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"Applying the Delta Method in Metric Analytics: A Practical Guide with Novel Applications" (KDD 2018)</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **Clustered Ratio Metric Estimator:**

                $$\hat{R} = \frac{\sum_{i=1}^m Y_i}{\sum_{i=1}^m N_i} = \frac{\bar{Y}}{\bar{N}} \quad \left(\text{e.g. CTR} = \frac{\text{Total Clicks}}{\text{Total Sessions}}, \quad \text{RPM} = \frac{\text{Total Revenue}}{\text{Total Pageviews}}\right)$$

                **Multivariate First-Order Taylor Expansion (Cluster-Robust Variance):**

                $$\widehat{\text{Var}}(\hat{R}) \approx \frac{1}{m \bar{N}^2} \left[ s_Y^2 - 2 \hat{R} s_{YN} + \hat{R}^2 s_N^2 \right]$$

                *User-Cluster Sample Variances & Covariances:*

                $$s_Y^2 = \frac{1}{m-1} \sum_{i=1}^m (Y_i - \bar{Y})^2, \quad s_N^2 = \frac{1}{m-1} \sum_{i=1}^m (N_i - \bar{N})^2, \quad s_{YN} = \frac{1}{m-1} \sum_{i=1}^m (Y_i - \bar{Y})(N_i - \bar{N})$$

                **Variance Inflation Factor (Clustering Penalty):**

                $$\text{VIF} = \frac{\text{SE}_{\text{cluster}}}{\text{SE}_{\text{naive}}} \ge 1, \quad \text{where } \text{SE}_{\text{naive}} = \sqrt{\frac{\hat{R}(1 - \hat{R})}{\sum N_i}}$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $m$ | Cluster Count | Number of independent randomized units (unique users). |
                | $Y_i$ | User Numerator Sum | Total conversions/clicks generated by user $i$ across all sessions. |
                | $N_i$ | User Denominator Sum | Total sessions/pageviews generated by user $i$. |
                | $\bar{N}$ | Mean Sessions per User | Average cluster intensity ($\frac{1}{m} \sum N_i$). |
                | $s_{YN}$ | Cross-Covariance | User-level covariance between session frequency and event occurrence. |
                | $\text{VIF}$ | Variance Inflation | Degree to which naive standard errors underestimate true sampling variability. |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        Randomizing at the user level while measuring at the session level creates intra-user correlation. Naive pooled t-tests assume every session is an independent user, underestimating error bars by up to 3x and flooding platforms with false positive winner claims. The Delta Method produces honest, cluster-robust confidence intervals.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif curr_idx == 3:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Bayesian Decision Theory & Expected Loss (Stucchio, 2015)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"Bayesian A/B Testing at VWO" (Visual Website Optimizer Methodology)</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **Conjugate Beta-Binomial Posterior Density:**

                $$\theta_i \mid k_i, n_i \sim \text{Beta}(\alpha_0 + k_i, \; \beta_0 + n_i - k_i), \quad \text{with uninformative prior } \text{Beta}(1, 1)$$

                **Probability of Superiority & Expected Downside Risk:**

                $$\mathbb{P}(\theta_B > \theta_A \mid \mathcal{D}) = \int_0^1 \int_{\theta_A}^1 p(\theta_A \mid \mathcal{D}) \, p(\theta_B \mid \mathcal{D}) \, d\theta_B \, d\theta_A$$

                $$\mathbb{E}[\text{Loss} \mid \text{Deploy } B] = \int_0^1 \int_0^1 \max(0, \theta_A - \theta_B) \, p(\theta_A \mid \mathcal{D}) \, p(\theta_B \mid \mathcal{D}) \, d\theta_A \, d\theta_B$$

                **Optimal Economic Stopping Rule:**

                $$\text{Deploy Variant } B \iff \mathbb{E}[\text{Loss} \mid \text{Deploy } B] < \varepsilon \quad (\varepsilon = \text{business risk tolerance, e.g. } 0.001)$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $\theta_A, \theta_B$ | True Conversion Rates | Latent true conversion rate probability densities of Control and Treatment. |
                | $k_i, n_i$ | Successes & Trials | Observed conversions ($k$) out of total visitor exposures ($n$). |
                | $\mathbb{P}(\theta_B > \theta_A)$ | Directional Probability | Bayesian probability that treatment conversion rate strictly exceeds control. |
                | $\mathbb{E}[\text{Loss}]$ | Downside Risk | Expected conversion rate surrender if the shipped decision turns out to be wrong. |
                | $\varepsilon$ | Risk Tolerance | Maximum permissible conversion point downside threshold before taking action. |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        P-values fail to answer the primary commercial question: "What is the expected dollar loss if this release is a mistake?" Bayesian Expected Loss quantifies exact downside risk in conversion points, allowing automated ship/no-ship thresholds.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif curr_idx == 4:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Multi-Armed Bandits & LinUCB Contextual Optimization (Li et al., 2010)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"A Contextual-Bandit Approach to Personalized News Article Recommendation" (WWW 2010)</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **A. Beta-Bernoulli Thompson Sampling (Probability Matching):**

                $$\tilde{\theta}_k \sim \text{Beta}(\alpha_k, \; \beta_k), \quad a_t = \arg\max_{k \in \mathcal{K}} \tilde{\theta}_k, \quad \alpha_{a_t} \leftarrow \alpha_{a_t} + r_t, \quad \beta_{a_t} \leftarrow \beta_{a_t} + (1 - r_t)$$

                **B. LinUCB with Disjoint Linear Models (Contextual Personalization):**

                $$\mathbb{E}[r_{t, a} \mid x_t] = x_t^T \theta_a^* \quad \implies \quad \hat{\theta}_a = A_a^{-1} b_a$$

                $$\text{where } A_a = I_d + \sum_{\tau: a_\tau = a} x_\tau x_\tau^T, \quad b_a = \sum_{\tau: a_\tau = a} r_\tau x_\tau$$

                **Upper Confidence Bound Arm Decision Rule:**

                $$a_t = \arg\max_{a \in \mathcal{A}} \left[ x_t^T \hat{\theta}_a + \alpha_{\text{UCB}} \sqrt{x_t^T A_a^{-1} x_t} \right]$$

                **Asymptotic Sub-Linear Regret:**

                $$\text{Regret}(T) = \sum_{t=1}^T \left( r_t^* - r_{t, a_t} \right) \le \mathcal{O}\left(d \sqrt{T \log(T)}\right) \implies \lim_{T \to \infty} \frac{\text{Regret}(T)}{T} = 0$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $x_t \in \mathbb{R}^d$ | User Context Vector | Feature representation of incoming visitor (device, traffic channel, intent). |
                | $\hat{\theta}_a \in \mathbb{R}^d$ | Arm Parameter Estimate | Online ridge regression weight vector capturing variant preference for arm $a$. |
                | $A_a \in \mathbb{R}^{d \times d}$ | Covariance Precision | Gram matrix accumulating context feature outer products allocated to arm $a$. |
                | $\alpha_{\text{UCB}}$ | Exploration Radius | Confidence multiplier governing the exploration-exploitation tradeoff. |
                | $\text{Regret}(T)$ | Cumulative Regret | Total loss in conversions compared to an oracle always choosing the optimal arm. |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        Traditional 50/50 A/B testing wastes 50% of traffic on inferior variants during weeks of experimentation. LinUCB shifts traffic in real time toward the winning experience while personalizing based on user context attributes.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif curr_idx == 5:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Frequentist Hypothesis Testing & Power Sizing (Lehr, 1992)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"Sixteen S-squared over D-squared: A relation for crude sample size estimates"</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **Two-Proportion Pooled Z-Test Statistic:**

                $$Z = \frac{\hat{p}_B - \hat{p}_A}{\text{SE}_{\text{pool}}}, \quad \text{SE}_{\text{pool}} = \sqrt{\hat{p}_{\text{pool}}(1 - \hat{p}_{\text{pool}}) \left( \frac{1}{n_A} + \frac{1}{n_B} \right)}, \quad \hat{p}_{\text{pool}} = \frac{k_A + k_B}{n_A + n_B}$$

                **P-Value & Wald Confidence Interval:**

                $$p\text{-value} = 2 \cdot \left[1 - \Phi(|Z|)\right], \quad \text{CI}_{1-\alpha} = (\hat{p}_B - \hat{p}_A) \pm z_{1 - \alpha/2} \sqrt{\frac{\hat{p}_A(1 - \hat{p}_A)}{n_A} + \frac{\hat{p}_B(1 - \hat{p}_B)}{n_B}}$$

                **Sample Size per Arm (Fixed-Horizon Power Equation):**

                $$n^* = \frac{2 \left( z_{1 - \alpha/2} + z_{1 - \beta} \right)^2 \bar{p}(1 - \bar{p})}{\left(p_B - p_A\right)^2} = \frac{2 \left( z_{1 - \alpha/2} + z_{1 - \beta} \right)^2}{\text{CVR}_A \cdot \text{Lift}_{\text{rel}}^2} (1 - \bar{p})$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $\hat{p}_A, \hat{p}_B$ | Sample Conversion Rates | Observed proportions $\frac{k_A}{n_A}$ and $\frac{k_B}{n_B}$. |
                | $z_{1 - \alpha/2}$ | Critical Significance Value | Normal quantile for Type I error rate ($\alpha=0.05 \implies z_{0.975} = 1.960$). |
                | $z_{1 - \beta}$ | Critical Power Quantile | Normal quantile for Statistical Power ($1-\beta=0.80 \implies z_{0.80} = 0.842$). |
                | $\text{Lift}_{\text{rel}}$ | Minimum Detectable Effect | Target relative percentage lift $\frac{p_B - p_A}{p_A}$ the experiment is sized to detect. |
                | $n^*$ | Required Sample per Arm | Minimum sample threshold required before evaluating the fixed-horizon Z-statistic. |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        Fixed-horizon tests represent a binding contract: evaluate only after collecting n* observations per arm. Stopping early invalidates the Type I error guarantee.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif curr_idx == 6:
            st.markdown(
                r"""
                <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Commercial ROI & Financial Breakeven Modeling (Kohavi et al., 2020)
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 12px;">
                    Published in: <em>"Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing" (Cambridge University Press)</em>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                r"""
                **Annualized Commercial Impact Formulas:**

                $$\Delta \text{Conversions} = \text{Annual Traffic} \times \left( \hat{p}_B - \hat{p}_A \right)$$

                $$\Delta \text{Revenue} = \Delta \text{Conversions} \times \text{RevenuePerConversion}$$

                **Net Commercial Payoff & Breakeven Horizon:**

                $$\text{Net Payoff} = \Delta \text{Revenue} - \text{Cost}_{\text{setup}}$$

                $$T_{\text{breakeven}} = \frac{\text{Cost}_{\text{setup}}}{\Delta \text{Revenue} / 365} \quad (\text{days until cumulative revenue exceeds setup cost})$$

                | Symbol | Parameter Name | Mathematical Role in Inference |
                | :--- | :--- | :--- |
                | $\text{Annual Traffic}$ | Total Population Scale | Projected visitor volume exposed to the feature over a 365-day fiscal cycle. |
                | $\text{RevPerConv}$ | Gross Margin per Unit | Dollar contribution margin yielded by a single completed conversion. |
                | $\text{Cost}_{\text{setup}}$ | Engineering Expenditure | Fixed upfront cost for development, QA, and infrastructure deployment. |
                | $T_{\text{breakeven}}$ | Breakeven Horizon | Payback period in days to recoup setup investment. |

                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Executive Decision Takeaway</div>
                    <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                        Statistical significance is a necessary condition, not a sufficient one. An experiment showing statistically significant lift that requires 5 years to recover engineering costs is commercially negative-ROI and should not be rolled out.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# -----------------------------------------------------------------------------
# TAB 5: Decision Optimization & OR Lab
# -----------------------------------------------------------------------------
with tab5:
    st.markdown(
        """
        <div class="callout-box">
            <div class="callout-title">Prescriptive Decision Science: 0-1 Multi-Dimensional Knapsack MILP Portfolio Optimizer</div>
            <p class="callout-text">
                Moving beyond isolated inference (<em>"Does variant B beat variant A?"</em>) to enterprise-scale capital allocation 
                (<em>"Which subset of winning experiments should we deploy given finite capital, engineering bandwidth, and latency budgets?"</em>). 
                OptiSim formulates the deployment decision as a <strong>Multi-Dimensional 0-1 Knapsack Mixed-Integer Linear Program (MILP)</strong> 
                and solves it to provable global optimality using SciPy's HiGHS branch-and-cut solver.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">
                Portfolio Resource Constraints & Risk Preferences
            </div>
            <div style="font-size: 0.84rem; color: #64748B; margin-bottom: 16px;">
                Configure the organizational ceiling across development sprints, infrastructure latency SLAs, and capital budgets.
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_or1, col_or2, col_or3, col_or4 = st.columns(4)
        with col_or1:
            or_budget = st.number_input(
                "Max Deployment Budget ($)",
                min_value=5000.0,
                max_value=250000.0,
                value=25000.0,
                step=2500.0,
                help="Total allowable upfront implementation & licensing cost across all selected features.",
                key="or_budget",
            )
        with col_or2:
            or_latency = st.number_input(
                "Max Latency SLA Overhead (ms)",
                min_value=10.0,
                max_value=200.0,
                value=35.0,
                step=5.0,
                help="Maximum allowable cumulative p95 client page load or API latency degradation.",
                key="or_latency",
            )
        with col_or3:
            or_effort = st.number_input(
                "Max Engineering Sprint Capacity (Pts)",
                min_value=10.0,
                max_value=150.0,
                value=40.0,
                step=5.0,
                help="Maximum engineering capacity (story points) allocated for deployment across squads.",
                key="or_effort",
            )
        with col_or4:
            or_risk = st.slider(
                "Risk Penalty Weight (lambda)",
                min_value=0.0,
                max_value=1.0,
                value=0.10,
                step=0.05,
                help="Risk penalty factor subtracted from expected annual value per unit of operational risk.",
                key="or_risk",
            )

    # Candidate Feature Pool
    candidate_pool = PortfolioOptimizer.get_default_candidate_pool(
        current_experiment_value=max(0.0, defensible_net),
        current_experiment_cost=impl_cost,
    )

    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 0.98rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">
                Candidate Feature Pool (A/B Test Pipeline)
            </div>
            <div style="font-size: 0.84rem; color: #64748B; margin-bottom: 12px;">
                Pipeline of validated experiments and platform capabilities competing for production roll-out.
            </div>
            """,
            unsafe_allow_html=True,
        )
        pool_df = pd.DataFrame([
            {
                "Feature ID": f.feature_id,
                "Feature Name": f.name,
                "Category": f.category,
                "Expected Value ($/yr)": f"${f.expected_value:,.0f}",
                "Setup Cost ($)": f"${f.cost:,.0f}",
                "Latency (ms)": f"{f.latency_ms:.1f} ms",
                "Effort (Pts)": f"{f.effort_points:.0f} pts",
                "Risk Score": f"{f.risk_score:.1f}",
                "Conflict Group": f.conflict_group or "None",
            }
            for f in candidate_pool
        ])
        st.dataframe(pool_df, use_container_width=True, hide_index=True)

    # Run MILP optimization
    opt_result = ExperimentDashboardService.run_portfolio_optimization(
        features=candidate_pool,
        max_budget=or_budget,
        max_latency_ms=or_latency,
        max_effort_points=or_effort,
        risk_aversion=or_risk,
        enforce_conflicts=True,
        current_experiment_value=max(0.0, defensible_net),
        current_experiment_cost=impl_cost,
    )

    # Executive KPI Metric Cards
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        net_portfolio_gain = opt_result.total_value - opt_result.total_cost
        st.metric(
            label="Portfolio Value",
            value=f"${opt_result.total_value:,.0f}",
            delta=f"+${net_portfolio_gain:,.0f} Net Gain" if net_portfolio_gain > 0 else f"${net_portfolio_gain:,.0f}",
            help="Total expected annual commercial value generated by the optimal selection.",
        )
    with col_kpi2:
        st.metric(
            label="Budget Utilization",
            value=f"{opt_result.budget_utilization_pct:.1f}%",
            delta=f"${opt_result.total_cost:,.0f} of ${or_budget:,.0f} Cap",
            delta_color="off",
            help="Total implementation expenditure vs available budget ceiling.",
        )
    with col_kpi3:
        st.metric(
            label="Latency Overhead",
            value=f"{opt_result.total_latency_ms:.1f} ms",
            delta=f"{opt_result.latency_utilization_pct:.1f}% of {or_latency:.0f}ms Cap",
            delta_color="off",
            help="Cumulative client-side latency overhead consumed vs budget.",
        )
    with col_kpi4:
        st.metric(
            label="Engineering Capacity",
            value=f"{opt_result.total_effort_points:.0f} Pts",
            delta=f"{opt_result.effort_utilization_pct:.1f}% of {or_effort:.0f} Pts Cap",
            delta_color="off",
            help="Engineering story points allocated across sprints.",
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Selected vs Deferred Features
    col_sel, col_rej = st.columns(2)
    with col_sel:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 0.95rem; font-weight: 700; color: #14532D;">Approved for Deployment ({len(opt_result.selected_features)})</span>
                    <span class="verdict-badge badge-success" style="font-size: 0.72rem;">MILP OPTIMAL</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if opt_result.selected_features:
                for feat in opt_result.selected_features:
                    st.markdown(
                        f"""
                        <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 8px;">
                                <span style="font-weight: 700; font-size: 0.88rem; color: #14532D; line-height: 1.35;">{feat.name}</span>
                                <span style="font-size: 0.72rem; font-weight: 600; color: #166534; background: #DCFCE7; border: 1px solid #BBF7D0; padding: 2px 8px; border-radius: 4px; white-space: nowrap; flex-shrink: 0;">{feat.category}</span>
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; color: #166534;">
                                <span>Value: <strong>${feat.expected_value:,.0f}</strong></span>
                                <span>Cost: <strong>${feat.cost:,.0f}</strong></span>
                                <span>Latency: <strong>{feat.latency_ms:+.1f}ms</strong></span>
                                <span>Effort: <strong>{feat.effort_points:.0f}pts</strong></span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No features selected under current constraints. Expand budget or latency limits.")

    with col_rej:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 0.95rem; font-weight: 700; color: #475569;">Deferred / Excluded ({len(opt_result.rejected_features)})</span>
                    <span class="verdict-badge badge-warning" style="font-size: 0.72rem;">CONSTRAINED</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if opt_result.rejected_features:
                for feat in opt_result.rejected_features:
                    conflict_selected = [s for s in opt_result.selected_features if feat.conflict_group and s.conflict_group == feat.conflict_group]
                    if conflict_selected:
                        reason = f"Mutually exclusive with '{conflict_selected[0].name}'"
                    elif opt_result.total_cost + feat.cost > or_budget:
                        reason = f"Exceeds remaining budget (${or_budget - opt_result.total_cost:,.0f} left vs ${feat.cost:,.0f} needed)"
                    elif opt_result.total_latency_ms + feat.latency_ms > or_latency:
                        reason = f"Exceeds latency limit ({or_latency - opt_result.total_latency_ms:.1f}ms left vs {feat.latency_ms:.1f}ms needed)"
                    elif opt_result.total_effort_points + feat.effort_points > or_effort:
                        reason = f"Exceeds sprint capacity ({or_effort - opt_result.total_effort_points:.0f} pts left vs {feat.effort_points:.0f} pts needed)"
                    else:
                        reason = "Sub-optimal risk-adjusted ROI vs. selected portfolio"

                    st.markdown(
                        f"""
                        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 6px;">
                                <span style="font-weight: 700; font-size: 0.88rem; color: #334155; line-height: 1.35;">{feat.name}</span>
                                <span style="font-size: 0.72rem; font-weight: 600; color: #475569; background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 4px; white-space: nowrap; flex-shrink: 0;">{feat.category}</span>
                            </div>
                            <div style="margin-bottom: 8px;">
                                <span style="display: inline-block; font-size: 0.73rem; font-weight: 500; color: #92400E; background: #FEF3C7; border: 1px solid #FDE68A; padding: 2px 8px; border-radius: 4px; line-height: 1.3;">{reason}</span>
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; color: #64748B;">
                                <span>Value: <strong>${feat.expected_value:,.0f}</strong></span>
                                <span>Cost: <strong>${feat.cost:,.0f}</strong></span>
                                <span>Latency: <strong>{feat.latency_ms:+.1f}ms</strong></span>
                                <span>Effort: <strong>{feat.effort_points:.0f}pts</strong></span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("All candidate features were successfully selected.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Plotly Visualizations: Efficient Frontier & Resource Saturation
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 0.92rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Capital-Value Efficient Frontier
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 8px;">
                    Pareto-optimal envelope showing maximum achievable commercial value across budget steps.
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                    <span><span style="display:inline-block; width:12px; height:12px; background:#2563EB; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Optimal Frontier</span>
                    <span><span style="display:inline-block; width:12px; height:12px; background:#10B981; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Operating Point</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            frontier = opt_result.efficient_frontier
            if frontier:
                f_budgets = [pt["budget"] for pt in frontier]
                f_values = [pt["value"] for pt in frontier]
                fig_ef = go.Figure()
                fig_ef.add_trace(go.Scatter(
                    x=f_budgets,
                    y=f_values,
                    mode="lines+markers",
                    line=dict(color="#2563EB", width=2.5),
                    marker=dict(size=7, color="#2563EB"),
                    name="Optimal Frontier",
                    hovertemplate="Budget: $%{x:,.0f}<br>Value: $%{y:,.0f}<extra></extra>",
                ))
                fig_ef.add_trace(go.Scatter(
                    x=[opt_result.total_cost],
                    y=[opt_result.total_value],
                    mode="markers",
                    marker=dict(size=14, color="#10B981", symbol="diamond", line=dict(color="#065F46", width=2)),
                    name="Operating Point",
                    hovertemplate="Current Operating Point<br>Cost: $%{x:,.0f}<br>Value: $%{y:,.0f}<extra></extra>",
                ))
                fig_ef.update_layout(
                    xaxis=dict(title="Deployment Budget ($)", automargin=True),
                    yaxis=dict(title="Max Portfolio Value ($)", automargin=True),
                    showlegend=False,
                )
                st.plotly_chart(format_chart(fig_ef, height=300), use_container_width=True)
            else:
                st.info("Frontier calculation unavailable.")

    with col_g2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 0.92rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;">
                    Multi-Dimensional Capacity Saturation
                </div>
                <div style="font-size: 0.80rem; color: #64748B; margin-bottom: 8px;">
                    Resource consumption percentage across capital, latency SLA, and developer story points.
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; font-weight: 600; color: #475569; padding: 6px 12px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 8px;">
                    <span><span style="display:inline-block; width:12px; height:12px; background:#10B981; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Safe (&lt;85%)</span>
                    <span><span style="display:inline-block; width:12px; height:12px; background:#F59E0B; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Near Cap (85-100%)</span>
                    <span><span style="display:inline-block; width:12px; height:12px; background:#EF4444; border-radius:2px; vertical-align:middle; margin-right:4px;"></span> Exceeded (&gt;100%)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            res_names = ["Budget ($)", "Latency (ms)", "Dev Effort (Pts)"]
            res_pcts = [
                opt_result.budget_utilization_pct,
                opt_result.latency_utilization_pct,
                opt_result.effort_utilization_pct,
            ]
            colors = ["#10B981" if p < 85 else "#F59E0B" if p <= 100 else "#EF4444" for p in res_pcts]
            fig_res = go.Figure(go.Bar(
                x=res_pcts,
                y=res_names,
                orientation="h",
                marker_color=colors,
                text=[f"{p:.1f}%" for p in res_pcts],
                textposition="outside",
            ))
            fig_res.add_vline(x=100.0, line_dash="dash", line_color="#EF4444", annotation_text="100% SLA Limit", annotation_position="top right")
            fig_res.update_layout(
                xaxis=dict(title="Capacity Consumed (%)", range=[0, max(120, max(res_pcts) + 20)], automargin=True),
                yaxis=dict(automargin=True),
                showlegend=False,
            )
            st.plotly_chart(format_chart(fig_res, height=300), use_container_width=True)

    # Mathematical Foundations & Dual Prices
    with st.container(border=True):
        st.markdown(
            r"""
            <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">
                Operations Research Formulation: Multi-Dimensional 0-1 Knapsack MILP
            </div>
            <div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
                Let $x_i \in \{0, 1\}$ denote the binary deployment indicator for candidate feature $i \in \{1, \dots, n\}$. 
                The optimization program is formulated as:
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            r"""
            $$\max_{\mathbf{x} \in \{0, 1\}^n} \quad \sum_{i=1}^n \left( v_i - \lambda r_i \right) x_i$$

            $$\text{subject to} \quad \sum_{i=1}^n c_i x_i \le B \quad \text{(Deployment Capital Budget)}$$

            $$\sum_{i=1}^n \ell_i x_i \le L \quad \text{(Latency SLA Degradation Limit)}$$

            $$\sum_{i=1}^n e_i x_i \le E \quad \text{(Engineering Sprint Capacity)}$$

            $$\sum_{j \in \mathcal{C}_k} x_j \le 1 \quad \forall k \quad \text{(Mutually Exclusive Feature Groups)}$$

            | Mathematical Symbol | Practical Operational Role |
            | :--- | :--- |
            | $v_i - \lambda r_i$ | Risk-adjusted expected annual commercial return of feature $i$. |
            | $c_i, B$ | Feature implementation cost ($) and total quarterly capital budget ($B$). |
            | $\ell_i, L$ | Client-side/API latency impact (ms) and max allowable SLA latency budget ($L$). |
            | $e_i, E$ | Engineering effort (story points) and total sprint engineering bandwidth ($E$). |
            | $\mathcal{C}_k$ | Mutually exclusive candidate sets (e.g. variants competing for the exact same UI surface). |

            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 6px; padding: 12px 16px; margin-top: 14px;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #1E3A8A; margin-bottom: 4px;">Algorithmic Guarantee</div>
                <div style="font-size: 0.84rem; color: #1E40AF; line-height: 1.5;">
                    Unlike heuristic greedy sorting (which fails under multiple knapsack dimensions and conflict sets), SciPy's HiGHS branch-and-cut MILP solver guarantees finding the exact global optimum, proving zero regret across all combinatorial allocation subsets.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# 7. Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "OptiSim // Enterprise Causal Inference & A/B Experimentation Studio. "
    "Designed with the 60-30-10 UI/UX rule and high-contrast typography hierarchy."
)
