"""
OptiSim // Enterprise Causal Inference & A/B Experimentation Studio
A production-grade, mathematically rigorous experimentation platform.
Built with Streamlit, Plotly, NumPy, and SciPy.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from scipy import stats
import streamlit as st

from dashboard.services import ExperimentDashboardService

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OptiSim // Experimentation Studio",
    page_icon="⚖️",
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
    st.markdown("## ⚖️ **OptiSim Studio**")
    st.caption("Causal Inference & Experimentation Architecture")
    st.markdown("---")

    mode_label = st.radio(
        "Experiment Mode",
        options=["Plan & Simulate (Monte Carlo)", "Analyze Real Data (Observed)"],
        index=0,
        help="Simulate with synthetic Monte Carlo sample paths, or analyze observed counts.",
    )
    is_simulation = ("Plan & Simulate" in mode_label)

    st.markdown("### ⚙️ Statistical Design")
    alpha = st.slider(
        "Significance Level (α)",
        min_value=0.01,
        max_value=0.10,
        value=0.05,
        step=0.01,
        help="Type I error rate. 0.05 corresponds to 95% anytime-valid confidence.",
    )

    if is_simulation:
        baseline_cvr = st.slider("Baseline CVR (Group A %)", 1.0, 50.0, 10.0, 0.5)
        expected_lift = st.slider("Target Relative Lift (%)", -50.0, 50.0, 12.0, 1.0)
        power_beta = st.slider("Statistical Power (1 - β)", 0.70, 0.95, 0.80, 0.05)
        beta = 1.0 - power_beta
        posterior_samples = 100_000
        bandit_rounds = st.number_input("Bandit Simulation Rounds", 5_000, 100_000, 20_000, 5_000)
        real_sample_size_a = real_sample_size_b = None
        real_conversions_a = real_conversions_b = None
    else:
        st.markdown("#### Observed Conversions")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            real_sample_size_a = st.number_input("Sample Size A", 10, 1_000_000, 1_000, 100)
            real_conversions_a = st.number_input("Conversions A", 0, real_sample_size_a, 100, 10)
        with col_s2:
            real_sample_size_b = st.number_input("Sample Size B", 10, 1_000_000, 1_000, 100)
            real_conversions_b = st.number_input("Conversions B", 0, real_sample_size_b, 120, 10)

        expected_lift = st.number_input("Planned Target Lift / MDE (%)", 0.1, 100.0, 12.0, 0.5)
        baseline_cvr = (real_conversions_a / real_sample_size_a * 100.0) if real_sample_size_a > 0 else 10.0
        beta = 0.20
        posterior_samples = 100_000
        bandit_rounds = 20_000

    st.markdown("### 💰 Commercial Levers")
    rev_per_conv = st.number_input("Revenue Per Conversion ($)", 1.0, 10_000.0, 10.0, 1.0)
    impl_cost = st.number_input("Implementation Setup Cost ($)", 0.0, 500_000.0, 500.0, 100.0)
    traffic = st.number_input("Projected Annual Traffic", 1_000, 100_000_000, 100_000, 10_000)

# -----------------------------------------------------------------------------
# 5. Execute Experiment Analysis Service
# -----------------------------------------------------------------------------
analysis = ExperimentDashboardService.run(
    baseline_conversion_rate=baseline_cvr,
    expected_lift=expected_lift,
    alpha=alpha,
    beta=beta,
    posterior_samples=posterior_samples,
    bandit_rounds=bandit_rounds,
    real_sample_size_a=real_sample_size_a,
    real_conversions_a=real_conversions_a,
    real_sample_size_b=real_sample_size_b,
    real_conversions_b=real_conversions_b,
    mode="simulation" if is_simulation else "real",
    revenue_per_conversion=rev_per_conv,
    implementation_cost=impl_cost,
    projected_traffic=traffic,
)

exp = analysis.experiment
freq = analysis.frequentist
seq = analysis.sequential
bayes = analysis.bayesian
rec = analysis.recommendation
fin = analysis.financials

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

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Diagnostic & Inference",
    "💰 Financial & Winner's Curse",
    "🧪 Bandits & Simulation",
    "📐 Statistical Rigor",
])

# -----------------------------------------------------------------------------
# TAB 1: Diagnostic & Anytime Inference
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

# -----------------------------------------------------------------------------
# TAB 2: Financial Impact & Winner's Curse Studio
# -----------------------------------------------------------------------------
with tab2:
    st.markdown(
        """
        <div class="callout-box">
            <div class="callout-title">⚠️ What is the Winner's Curse in A/B Testing?</div>
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
# TAB 3: Simulation & Bandit Lab
# -----------------------------------------------------------------------------
with tab3:
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

# -----------------------------------------------------------------------------
# TAB 4: Statistical Rigor & Methodology Reference
# -----------------------------------------------------------------------------
with tab4:
    with st.container(border=True):
        st.markdown(
            """<div style="font-size: 1.02rem; font-weight: 700; color: #0F172A; margin-bottom: 12px;">Mathematical Formulations & Time-Uniform Guarantees</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            r"""
            #### A. Anytime-Valid Confidence Sequences (Waudby-Smith & Ramdas, 2023)
            For an empirical difference $\hat{\delta}_n$ with pooled variance $\sigma^2$ at effective sample size $n$:
            $$\hat{\delta}_n \pm \sigma \sqrt{\frac{2(n\rho^2 + 1)}{n^2 \rho^2} \log\left(\frac{\sqrt{n\rho^2 + 1}}{\alpha}\right)}$$
            where $\rho$ is a pre-experiment tuning parameter anchored to the planned sample size $N^*$:
            $$\rho = \sqrt{\frac{-2\log(\alpha) + \log(-2\log(\alpha) + 1)}{N^*}}$$
            *Mathematical Guarantee*: $\mathbb{P}\left(\forall n \ge 1, \; \delta^* \in \text{CS}_n\right) \ge 1 - \alpha$. Continuous peeking never inflates Type I error.

            #### B. Bayesian Beta-Binomial Posterior Update & Expected Loss
            Given flat prior $\text{Beta}(1, 1)$, after observing $k_i$ conversions out of $n_i$ trials:
            $$\theta_i \mid \text{data} \sim \text{Beta}(1 + k_i, \; 1 + n_i - k_i)$$
            The **Expected Loss** of deploying Variant $B$ over Control $A$ is:
            $$\mathbb{E}[\text{Loss} \mid \text{choose } B] = \int_0^1 \int_0^1 \max(0, \theta_A - \theta_B) \, p(\theta_A) p(\theta_B) \, d\theta_A d\theta_B$$
            """
        )

# -----------------------------------------------------------------------------
# 7. Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "OptiSim // Enterprise Causal Inference & A/B Experimentation Studio. "
    "Designed with the 60-30-10 UI/UX rule and high-contrast typography hierarchy."
)
