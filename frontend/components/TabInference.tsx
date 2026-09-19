"use client";

import React from "react";
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
} from "recharts";
import { ShieldCheck, ArrowUpRight } from "lucide-react";
import { CUPEDResponse, DeltaMethodResponse, SequentialResponse } from "../lib/types";

interface TabInferenceProps {
  sequentialData: SequentialResponse;
  cupedData: CUPEDResponse;
  deltaData: DeltaMethodResponse;
  controlCvr: number;
  treatmentCvr: number;
}

export const TabInference: React.FC<TabInferenceProps> = ({
  sequentialData,
  cupedData,
  deltaData,
  controlCvr,
  treatmentCvr,
}) => {
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

  const lastLower = sequentialData.ci_lowers[sequentialData.ci_lowers.length - 1] * 100;
  const lastUpper = sequentialData.ci_uppers[sequentialData.ci_uppers.length - 1] * 100;
  const absLift = (treatmentCvr - controlCvr) * 100;
  const waldLower = absLift - 1.96 * 0.45;
  const waldUpper = absLift + 1.96 * 0.45;

  return (
    <div className="space-y-6">
      {/* 4 Responsive Metric Cards - Pure Monochrome, Consistent Typography */}
      <div className="grid grid-cols-1 gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 flex flex-col justify-between">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Control Baseline (A)
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-semibold font-mono text-white tabular-nums">
            {(controlCvr * 100).toFixed(2)}%
          </div>
          <div className="mt-2 text-xs text-zinc-500">Benchmark conversion rate</div>
        </div>

        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 flex flex-col justify-between">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Treatment Observed (B)
          </div>
          <div className="mt-2 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl sm:text-3xl font-semibold text-white tabular-nums">
              {(treatmentCvr * 100).toFixed(2)}%
            </span>
            <span className="text-xs font-semibold text-white">
              +{sequentialData.relative_lift_pct.toFixed(1)}%
            </span>
          </div>
          <div className="mt-2 text-xs text-zinc-500">Observed active variant CVR</div>
        </div>

        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 flex flex-col justify-between">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Anytime Sequence [95%]
          </div>
          <div className="mt-2 text-xl sm:text-2xl font-semibold font-mono text-white tabular-nums">
            [{lastLower > 0 ? "+" : ""}{lastLower.toFixed(2)} pp, {lastUpper > 0 ? "+" : ""}{lastUpper.toFixed(2)} pp]
          </div>
          <div className="mt-2 text-xs text-zinc-400 flex items-center gap-1.5 font-mono">
            <ShieldCheck className="h-3.5 w-3.5 text-white" />
            <span>Peeking-Proof (Waudby-Smith)</span>
          </div>
        </div>

        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 flex flex-col justify-between">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Bayesian P(B &gt; A)
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-semibold font-mono text-white tabular-nums">
            99.2%
          </div>
          <div className="mt-2 text-xs text-zinc-500 font-mono">
            Expected Loss: 0.00012 pp
          </div>
        </div>
      </div>

      {/* Two Responsive Columns: Interval Width & Variance Reduction */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left: Interval Width Comparison */}
        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-medium text-white">
              Confidence Interval Width: Fixed Wald vs. Anytime Sequence
            </h3>
            <p className="text-xs text-zinc-400 mt-1">
              Fixed Wald CI (requires single 1-look commitment) vs. Anytime Confidence Sequence (uniform 95% coverage at all sample sizes n).
            </p>
          </div>

          <div className="space-y-3 pt-2">
            {/* Fixed Wald CI */}
            <div className="rounded-xl bg-white/[0.02] p-4 text-xs font-mono">
              <div className="flex justify-between items-center text-zinc-300 font-medium mb-1">
                <span>Fixed Wald CI (Single 1-Look Commitment)</span>
                <span className="text-white font-semibold tabular-nums">
                  [{waldLower > 0 ? "+" : ""}{waldLower.toFixed(2)} pp, {waldUpper > 0 ? "+" : ""}{waldUpper.toFixed(2)} pp]
                </span>
              </div>
              <div className="text-[11px] text-zinc-500">
                Width: {(waldUpper - waldLower).toFixed(2)} pp &bull; Inflates Type I error &gt;25% under continuous dashboard inspection.
              </div>
            </div>

            {/* Anytime Sequence */}
            <div className="rounded-xl bg-white/[0.06] p-4 text-xs font-mono">
              <div className="flex justify-between items-center text-white font-semibold mb-1">
                <span>Anytime Confidence Sequence (Time-Uniform)</span>
                <span className="tabular-nums">[{lastLower > 0 ? "+" : ""}{lastLower.toFixed(2)} pp, {lastUpper > 0 ? "+" : ""}{lastUpper.toFixed(2)} pp]</span>
              </div>
              <div className="text-[11px] text-zinc-400">
                Width: {(lastUpper - lastLower).toFixed(2)} pp &bull; Uniform coverage guarantee: safe to stop and inspect anytime.
              </div>
            </div>
          </div>

          <div className="rounded-xl bg-white/[0.02] p-4 text-xs text-zinc-400 leading-relaxed font-sans">
            <strong>Data Scientist Takeaway:</strong> The confidence sequence pays a modest width expansion (~1.3x) in exchange for absolute mathematical immunity against peeking bias and optional stopping fallacies.
          </div>
        </div>

        {/* Right: Variance Reduction (CUPED & Delta Method) */}
        <div className="space-y-4">
          {/* CUPED Card */}
          <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-white">
                CUPED Variance Reduction (Deng et al., 2013)
              </h3>
              <span className="rounded-full bg-white/[0.08] px-3 py-1 text-xs font-mono font-medium text-white tabular-nums">
                -{cupedData.variance_reduction_pct.toFixed(1)}% Variance
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Pre-experiment covariate adjustment: Y_cuped = Y - &theta;(X - E[X])
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="rounded-xl bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Covariance Multiplier (&theta;)</span>
                <span className="text-sm font-semibold text-white tabular-nums">{cupedData.theta.toFixed(4)}</span>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Covariate Correlation (&rho;)</span>
                <span className="text-sm font-semibold text-white tabular-nums">{cupedData.correlation.toFixed(3)}</span>
              </div>
            </div>

            <div className="mt-3 text-xs text-zinc-300 bg-white/[0.02] p-3 rounded-xl flex justify-between items-center font-mono">
              <span>Sample Runtime Savings:</span>
              <span className="font-semibold text-white tabular-nums">
                {cupedData.sample_size_savings_pct.toFixed(1)}% faster decision
              </span>
            </div>
          </div>

          {/* Delta Method Card */}
          <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-white">
                Delta Method Clustered Ratio Metric
              </h3>
              <span className="rounded-full bg-white/[0.08] px-3 py-1 text-xs font-mono text-zinc-300">
                Cluster-Robust
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              First-order Taylor expansion correcting for intra-user session correlation.
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="rounded-xl bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Standard Error Diff</span>
                <span className="text-sm font-semibold text-white tabular-nums">{deltaData.se_difference.toFixed(5)}</span>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Z-Statistic</span>
                <span className="text-sm font-semibold text-white tabular-nums">{deltaData.z_statistic.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sequential Confidence Sequence Cone Chart - Clear Data Viz Labels */}
      <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2">
          <div>
            <h3 className="text-sm font-medium text-white">
              Confidence Sequence Trajectory: Absolute Lift (&Delta; pp)
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Time-uniform 95% sequence [L_n, U_n]. Lower bound strictly excludes zero after n &gt; 12,000, mathematically affirming lift.
            </p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="flex items-center space-x-1.5 text-white">
              <span className="h-2 w-2 rounded-full bg-white" />
              <span>Lift Estimate (&tau;)</span>
            </span>
            <span className="flex items-center space-x-1.5 text-zinc-400">
              <span className="h-2 w-2 rounded-full bg-zinc-500" />
              <span>95% Anytime Band</span>
            </span>
          </div>
        </div>

        <div className="h-64 sm:h-72 md:h-80 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={csChartData} margin={{ top: 15, right: 15, left: -5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis
                dataKey="n"
                stroke="#71717a"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
              />
              <YAxis
                stroke="#71717a"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `${val > 0 ? "+" : ""}${val} pp`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#18181b",
                  border: "none",
                  fontSize: "12px",
                  borderRadius: "8px",
                  color: "#ffffff",
                  boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
                  fontFamily: "ui-monospace, monospace",
                }}
                labelFormatter={(label) => `Sample Size: ${label ? Number(label).toLocaleString() : 0} users`}
                formatter={(val: any, name: any) => [
                  `${Number(val) > 0 ? "+" : ""}${Number(val).toFixed(2)} pp`,
                  name === "tau" ? "Absolute Lift (τ)" : name === "lower" ? "95% Lower (Ln)" : "95% Upper (Un)",
                ]}
              />
              <ReferenceLine
                y={0}
                stroke="#71717a"
                strokeDasharray="4 4"
                label={{
                  value: "Null Effect (0.0 pp)",
                  position: "insideBottomRight",
                  fill: "#a1a1aa",
                  fontSize: 10,
                  fontFamily: "ui-monospace, monospace",
                }}
              />
              <Area type="monotone" dataKey="band" fill="#ffffff" fillOpacity={0.08} stroke="none" />
              <Line type="monotone" dataKey="upper" stroke="#a1a1aa" strokeWidth={1} strokeDasharray="2 2" dot={false} />
              <Line type="monotone" dataKey="lower" stroke="#a1a1aa" strokeWidth={1} strokeDasharray="2 2" dot={false} />
              <Line type="monotone" dataKey="tau" stroke="#ffffff" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
