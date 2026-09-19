"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  BarChart,
  Bar,
  ErrorBar,
} from "recharts";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  Sparkles,
  Layers,
  Filter,
  Info,
} from "lucide-react";
import {
  CUPEDResponse,
  DeltaMethodResponse,
  GuardrailAuditResponse,
  HTEResponse,
  SequentialResponse,
} from "../lib/types";

interface ExperimentStudioProps {
  sequentialData: SequentialResponse;
  cupedData: CUPEDResponse;
  deltaData: DeltaMethodResponse;
  hteData: HTEResponse;
  guardrailsData: GuardrailAuditResponse;
  onRefreshGuardrails: (alphaFdr: number) => void;
}

export const ExperimentStudio: React.FC<ExperimentStudioProps> = ({
  sequentialData,
  cupedData,
  deltaData,
  hteData,
  guardrailsData,
  onRefreshGuardrails,
}) => {
  const [fdrAlpha, setFdrAlpha] = useState<number>(0.05);

  // Format confidence sequence chart data
  const csChartData = sequentialData.sample_sizes.map((size, idx) => ({
    n: size,
    tau: +(sequentialData.tau_estimates[idx] * 100).toFixed(3),
    lower: +(sequentialData.ci_lowers[idx] * 100).toFixed(3),
    upper: +(sequentialData.ci_uppers[idx] * 100).toFixed(3),
    band: [
      +(sequentialData.ci_lowers[idx] * 100).toFixed(3),
      +(sequentialData.ci_uppers[idx] * 100).toFixed(3),
    ],
  }));

  // Format HTE Forest plot data
  const forestData = hteData.subgroups.map((sub) => ({
    name: sub.segment_name,
    liftPct: +(sub.relative_lift * 100).toFixed(2),
    lowerPct: +(sub.ci_lower / (sub.cvr_a || 0.1) * 100).toFixed(2),
    upperPct: +(sub.ci_upper / (sub.cvr_a || 0.1) * 100).toFixed(2),
    zScore: +sub.z_score.toFixed(2),
    isSignificant: sub.is_significant,
    isInteractionSig: sub.interaction_significant,
  }));

  return (
    <div className="space-y-6">
      {/* Top Banner KPI Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {/* Metric 1 */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Primary Target Metric
          </div>
          <div className="mt-1 flex items-baseline justify-between">
            <div className="text-xl font-bold tracking-tight text-white font-mono">
              Checkout CVR
            </div>
            <span className="rounded bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 text-[11px] font-mono text-cyan-400">
              Variant B
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
            <span>Control: <span className="text-slate-200 tabular-nums font-mono">10.42%</span></span>
            <span>Treatment: <span className="text-slate-200 tabular-nums font-mono">11.85%</span></span>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Relative Treatment Effect
          </div>
          <div className="mt-1 flex items-baseline space-x-2">
            <span className="text-2xl font-bold tracking-tight text-emerald-400 font-mono tabular-nums">
              +{sequentialData.relative_lift_pct.toFixed(2)}%
            </span>
            <span className="text-xs font-medium text-slate-400">Relative</span>
          </div>
          <div className="mt-2 text-xs text-slate-400 font-mono tabular-nums">
            95% CS: [{(sequentialData.ci_lowers[sequentialData.ci_lowers.length - 1] * 100).toFixed(2)}%,{" "}
            {(sequentialData.ci_uppers[sequentialData.ci_uppers.length - 1] * 100).toFixed(2)}%]
          </div>
        </div>

        {/* Metric 3 */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Sequential Peeking Immunity
          </div>
          <div className="mt-1 flex items-center space-x-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            <span className="text-sm font-semibold text-white">
              {sequentialData.stopped_early ? "Decision Confirmed" : "Monitoring Active"}
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Waudby-Smith & Ramdas (2021) Asymptotic CS
          </div>
        </div>

        {/* Metric 4 */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Multi-Metric Guardrails
          </div>
          <div className="mt-1 flex items-center space-x-2">
            {guardrailsData.has_critical_violations ? (
              <>
                <AlertTriangle className="h-5 w-5 text-rose-400" />
                <span className="text-sm font-semibold text-rose-400">Violation Detected</span>
              </>
            ) : (
              <>
                <ShieldCheck className="h-5 w-5 text-emerald-400" />
                <span className="text-sm font-semibold text-emerald-400">All Passed (FDR 5%)</span>
              </>
            )}
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Benjamini-Hochberg Multiplicity Control
          </div>
        </div>
      </div>

      {/* Main Section: Confidence Sequence Cone & Causal Adjustments */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Confidence Sequence Trajectory (2 Cols) */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm lg:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                <span>Anytime-Valid Confidence Sequence Trajectory</span>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-cyan-400 border border-slate-700">
                  Time-Uniform Central Limit Theorem
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Evaluated continuously at every visitor arrival. Guarantees Type I error rate &le; 5% under infinite continuous looks.
              </p>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="flex items-center space-x-1.5 text-slate-300">
                <span className="h-2 w-2 rounded-full bg-cyan-400" />
                <span>&tau; Point Estimate</span>
              </span>
              <span className="flex items-center space-x-1.5 text-slate-400">
                <span className="h-2 w-2 rounded bg-cyan-500/20 border border-cyan-500/40" />
                <span>95% Anytime Band</span>
              </span>
            </div>
          </div>

          {/* Chart Container */}
          <div className="mt-4 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={csChartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="n"
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
                />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `${val}%`}
                  domain={["auto", "auto"]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    fontSize: "12px",
                    borderRadius: "6px",
                  }}
                  labelFormatter={(label) => `Sample Size: ${label ? Number(label).toLocaleString() : 0} users`}
                  formatter={(val: any, name: any) => [
                    `${val}%`,
                    name === "tau" ? "Absolute Lift (pp)" : name === "lower" ? "95% Lower" : "95% Upper",
                  ]}
                />
                <ReferenceLine y={0} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: "Null 0%", fill: "#f43f5e", fontSize: 10, position: "insideBottomRight" }} />
                <Area type="monotone" dataKey="band" fill="#06b6d4" fillOpacity={0.12} stroke="none" />
                <Line type="monotone" dataKey="upper" stroke="#06b6d4" strokeWidth={1} strokeDasharray="2 2" dot={false} />
                <Line type="monotone" dataKey="lower" stroke="#06b6d4" strokeWidth={1} strokeDasharray="2 2" dot={false} />
                <Line type="monotone" dataKey="tau" stroke="#38bdf8" strokeWidth={2} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
            <span>Left boundary: High early uncertainty</span>
            <span>Right boundary: Asymptotic contraction around true effect</span>
          </div>
        </div>

        {/* Causal Adjustments Side Panel (1 Col) */}
        <div className="space-y-4">
          {/* CUPED Card */}
          <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                CUPED Variance Reduction
              </span>
              <span className="rounded bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-mono text-emerald-400 font-bold">
                -{cupedData.variance_reduction_pct.toFixed(1)}% Variance
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Pre-experiment covariate conditioning (Deng et al., 2013).
            </p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="rounded border border-slate-800 bg-slate-950/60 p-2">
                <span className="text-[10px] text-slate-500 block">Covariate &theta;</span>
                <span className="font-bold text-slate-200">{cupedData.theta.toFixed(4)}</span>
              </div>
              <div className="rounded border border-slate-800 bg-slate-950/60 p-2">
                <span className="text-[10px] text-slate-500 block">Correlation &rho;</span>
                <span className="font-bold text-slate-200">{cupedData.correlation.toFixed(3)}</span>
              </div>
            </div>
            <div className="mt-3 rounded border border-slate-800/80 bg-slate-950/40 p-2 text-xs flex justify-between items-center">
              <span className="text-slate-400">Sample Size Savings:</span>
              <span className="text-emerald-400 font-mono font-bold">
                {cupedData.sample_size_savings_pct.toFixed(1)}% equivalent runtime
              </span>
            </div>
          </div>

          {/* Delta Method Card */}
          <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Delta Method Ratio Metric
              </span>
              <span className="rounded bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 text-[10px] font-mono text-cyan-400">
                Cluster-Robust
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Taylor series expansion correcting user session correlation.
            </p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="rounded border border-slate-800 bg-slate-950/60 p-2">
                <span className="text-[10px] text-slate-500 block">Cluster SE Diff</span>
                <span className="font-bold text-slate-200">{deltaData.se_difference.toFixed(5)}</span>
              </div>
              <div className="rounded border border-slate-800 bg-slate-950/60 p-2">
                <span className="text-[10px] text-slate-500 block">Delta Z-Statistic</span>
                <span className="font-bold text-slate-200">{deltaData.z_statistic.toFixed(2)}</span>
              </div>
            </div>
            <div className="mt-3 rounded border border-slate-800/80 bg-slate-950/40 p-2 text-xs flex justify-between items-center">
              <span className="text-slate-400">Ratio Lift p-value:</span>
              <span className="text-cyan-400 font-mono font-bold">
                {deltaData.p_value < 0.001 ? "< 0.001" : deltaData.p_value.toFixed(4)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Subgroup Heterogeneity (HTE CATE Forest Plot) */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              <span>Heterogeneous Treatment Effects (HTE) Forest Analysis</span>
              <span
                className={`rounded px-2 py-0.5 text-[10px] font-mono font-semibold border ${
                  hteData.has_heterogeneity
                    ? "bg-amber-950/60 border-amber-500/30 text-amber-400"
                    : "bg-slate-800 border-slate-700 text-slate-300"
                }`}
              >
                Cochran's Q Test: {hteData.has_heterogeneity ? "Heterogeneity Detected" : "Homogeneous"}
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Conditional Average Treatment Effect (CATE) across segmented user cohorts. Statistical interaction z-tests identify segment winners & losers.
            </p>
          </div>
          <div className="text-xs font-mono text-slate-400">
            Top Segment: <span className="text-emerald-400 font-bold">{hteData.top_performing_segment}</span>
          </div>
        </div>

        {/* Forest Subgroups Table & Visual Bars */}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2 font-semibold">Cohort / Segment</th>
                <th className="pb-2 font-semibold">Sample (A / B)</th>
                <th className="pb-2 font-semibold">CVR (A &rarr; B)</th>
                <th className="pb-2 font-semibold">Relative Lift</th>
                <th className="pb-2 font-semibold">Interaction Test</th>
                <th className="pb-2 font-semibold text-right">Segment Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {hteData.subgroups.map((sub) => (
                <tr key={sub.segment_name} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 font-bold text-white">{sub.segment_name}</td>
                  <td className="py-2.5 text-slate-400">
                    {sub.sample_size_a.toLocaleString()} / {sub.sample_size_b.toLocaleString()}
                  </td>
                  <td className="py-2.5 text-slate-300">
                    {(sub.cvr_a * 100).toFixed(2)}% &rarr; {(sub.cvr_b * 100).toFixed(2)}%
                  </td>
                  <td className="py-2.5">
                    <span
                      className={`font-bold ${
                        sub.relative_lift > 0 ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {sub.relative_lift > 0 ? "+" : ""}
                      {(sub.relative_lift * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-400">
                    {sub.interaction_significant ? (
                      <span className="text-amber-400 font-semibold">
                        Significant (&Delta; effect)
                      </span>
                    ) : (
                      <span className="text-slate-500">Neutral</span>
                    )}
                  </td>
                  <td className="py-2.5 text-right">
                    <span
                      className={`inline-block rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                        sub.is_significant && sub.relative_lift > 0
                          ? "bg-emerald-950/60 text-emerald-400 border border-emerald-500/30"
                          : sub.relative_lift < 0
                          ? "bg-rose-950/60 text-rose-400 border border-rose-500/30"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {sub.is_significant && sub.relative_lift > 0
                        ? "Outperformer"
                        : sub.relative_lift < 0
                        ? "Underperformer"
                        : "Inconclusive"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Multi-Metric Guardrails Matrix */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              <span>Operational Risk & Multi-Metric Guardrails Matrix</span>
              <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-300 border border-slate-700">
                Benjamini-Hochberg FDR Adjusted
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Tracks secondary business metrics to ensure conversion uplift does not harm infrastructure, reliability, or retention.
            </p>
          </div>
          {/* FDR Alpha Slider */}
          <div className="flex items-center space-x-3 text-xs">
            <span className="text-slate-400">Target FDR (&alpha;):</span>
            <span className="font-mono text-slate-200 font-bold">{fdrAlpha.toFixed(2)}</span>
            <input
              type="range"
              min="0.01"
              max="0.20"
              step="0.01"
              value={fdrAlpha}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setFdrAlpha(val);
                onRefreshGuardrails(val);
              }}
              className="h-1.5 w-24 cursor-pointer appearance-none rounded-lg bg-slate-700 accent-cyan-400"
            />
          </div>
        </div>

        {/* Guardrail Metric Cards Grid */}
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {guardrailsData.metrics.map((metric) => {
            const isFail = metric.status === "FAIL";
            const isWarn = metric.status === "WARN";
            const isPass = metric.status === "PASS";

            return (
              <div
                key={metric.metric_name}
                className={`rounded-lg border p-4 transition-all ${
                  isFail
                    ? "border-rose-500/40 bg-rose-950/20"
                    : isWarn
                    ? "border-amber-500/40 bg-amber-950/20"
                    : "border-slate-800 bg-slate-950/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-white">{metric.metric_name}</span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider ${
                      isFail
                        ? "bg-rose-900/60 text-rose-300 border border-rose-500/40"
                        : isWarn
                        ? "bg-amber-900/60 text-amber-300 border border-amber-500/40"
                        : "bg-emerald-950/60 text-emerald-400 border border-emerald-500/30"
                    }`}
                  >
                    {metric.status}
                  </span>
                </div>

                <div className="mt-3 flex items-baseline justify-between text-xs font-mono">
                  <span className="text-slate-400">Baseline: {metric.control_value}</span>
                  <span className="text-slate-200 font-bold">Observed: {metric.treatment_value}</span>
                </div>

                <div className="mt-2 text-xs font-mono">
                  <span className="text-slate-400">Relative Delta: </span>
                  <span
                    className={`font-bold ${
                      metric.relative_change > 0 && metric.direction_favorable === "lower"
                        ? "text-rose-400"
                        : "text-slate-200"
                    }`}
                  >
                    {metric.relative_change > 0 ? "+" : ""}
                    {metric.relative_change.toFixed(2)}%
                  </span>
                  <span className="text-slate-500 text-[10px] block">
                    Threshold: &le; {metric.threshold_pct}%
                  </span>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>Raw p: {metric.raw_p_value.toFixed(3)}</span>
                  <span className="text-slate-300">FDR p: {metric.adjusted_p_value.toFixed(3)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
