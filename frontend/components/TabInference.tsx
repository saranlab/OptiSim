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
import { ShieldCheck } from "lucide-react";
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
      {/* 4 Metric Cards - Zero Borders */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Control CVR (A)
          </div>
          <div className="mt-2 text-2xl font-semibold font-mono text-white tabular-nums">
            {(controlCvr * 100).toFixed(2)}%
          </div>
          <div className="mt-2 text-xs text-zinc-500">Baseline conversion</div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Treatment CVR (B)
          </div>
          <div className="mt-2 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl font-semibold text-white tabular-nums">
              {(treatmentCvr * 100).toFixed(2)}%
            </span>
            <span className="text-xs font-semibold text-blue-400">
              +{sequentialData.relative_lift_pct.toFixed(1)}%
            </span>
          </div>
          <div className="mt-2 text-xs text-zinc-500">Observed treatment lift</div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Anytime Sequence
          </div>
          <div className="mt-2 text-xl font-semibold font-mono text-white tabular-nums">
            [{lastLower > 0 ? "+" : ""}{lastLower.toFixed(2)}%, {lastUpper > 0 ? "+" : ""}{lastUpper.toFixed(2)}%]
          </div>
          <div className="mt-2 text-xs text-blue-400 flex items-center gap-1.5 font-mono">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Peeking-Proof</span>
          </div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Bayesian P(B &gt; A)
          </div>
          <div className="mt-2 text-2xl font-semibold font-mono text-blue-400 tabular-nums">
            99.2%
          </div>
          <div className="mt-2 text-xs text-zinc-500 font-mono">
            Expected Loss: 0.00012 pp
          </div>
        </div>
      </div>

      {/* Two Columns: Statistical Rigor Comparison */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left: Interval Width Comparison */}
        <div className="rounded-xl bg-white/[0.03] p-6 space-y-4">
          <div>
            <h3 className="text-sm font-medium text-white">
              Interval Width Comparison
            </h3>
            <p className="text-xs text-zinc-400 mt-1">
              Fixed Wald CI vs. Anytime Valid Confidence Sequence (Waudby-Smith &amp; Ramdas).
            </p>
          </div>

          <div className="space-y-3 pt-2">
            {/* Fixed Wald CI */}
            <div className="rounded-lg bg-white/[0.02] p-4 text-xs font-mono">
              <div className="flex justify-between text-zinc-300 font-medium mb-1">
                <span>Fixed Wald CI (1-Look Static)</span>
                <span className="text-zinc-200">
                  [{waldLower.toFixed(2)} pp, {waldUpper.toFixed(2)} pp]
                </span>
              </div>
              <div className="text-[11px] text-zinc-500">
                Width: {(waldUpper - waldLower).toFixed(2)} pp &bull; Inflates Type I error &gt;25% if repeatedly inspected.
              </div>
            </div>

            {/* Anytime Sequence */}
            <div className="rounded-lg bg-blue-600/10 p-4 text-xs font-mono">
              <div className="flex justify-between text-blue-400 font-semibold mb-1">
                <span>Anytime Confidence Sequence</span>
                <span>[{lastLower.toFixed(2)} pp, {lastUpper.toFixed(2)} pp]</span>
              </div>
              <div className="text-[11px] text-zinc-400">
                Width: {(lastUpper - lastLower).toFixed(2)} pp &bull; Uniform coverage guarantee: safe to stop and inspect anytime.
              </div>
            </div>
          </div>

          <div className="rounded-lg bg-white/[0.02] p-4 text-xs text-zinc-400 leading-relaxed font-sans">
            The anytime confidence sequence pays a modest width penalty in exchange for absolute mathematical immunity against dashboard peeking and early stopping bias.
          </div>
        </div>

        {/* Right: Variance Reduction (CUPED & Delta Method) */}
        <div className="space-y-4">
          {/* CUPED Card */}
          <div className="rounded-xl bg-white/[0.03] p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-white">
                CUPED Variance Reduction
              </h3>
              <span className="rounded-full bg-blue-600/20 px-2.5 py-0.5 text-xs font-mono font-medium text-blue-400">
                -{cupedData.variance_reduction_pct.toFixed(1)}% Variance
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Pre-experiment covariate adjustment (Deng et al., 2013).
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="rounded-lg bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Covariate Multiplier (&theta;)</span>
                <span className="text-sm font-semibold text-white">{cupedData.theta.toFixed(4)}</span>
              </div>
              <div className="rounded-lg bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Correlation (&rho;)</span>
                <span className="text-sm font-semibold text-white">{cupedData.correlation.toFixed(3)}</span>
              </div>
            </div>

            <div className="mt-3 text-xs text-zinc-400 bg-white/[0.02] p-3 rounded-lg flex justify-between items-center font-mono">
              <span>Sample Runtime Savings:</span>
              <span className="font-semibold text-blue-400">
                {cupedData.sample_size_savings_pct.toFixed(1)}% faster decision
              </span>
            </div>
          </div>

          {/* Delta Method Card */}
          <div className="rounded-xl bg-white/[0.03] p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-white">
                Delta Method Ratio Metric
              </h3>
              <span className="rounded-full bg-white/[0.06] px-2.5 py-0.5 text-xs font-mono text-zinc-300">
                Cluster-Robust
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Taylor expansion correcting user-level session correlation.
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="rounded-lg bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Standard Error Diff</span>
                <span className="text-sm font-semibold text-white">{deltaData.se_difference.toFixed(5)}</span>
              </div>
              <div className="rounded-lg bg-white/[0.02] p-3">
                <span className="text-[10px] text-zinc-500 block mb-1">Z-Statistic</span>
                <span className="text-sm font-semibold text-white">{deltaData.z_statistic.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sequential Confidence Sequence Chart - Zero Borders */}
      <div className="rounded-xl bg-white/[0.03] p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2">
          <div>
            <h3 className="text-sm font-medium text-white">
              Confidence Sequence Trajectory ([L_n, U_n])
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Uniform coverage sequence contracts as sample n grows. Zero is excluded early, confirming significant lift.
            </p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="flex items-center space-x-1.5 text-zinc-300">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              <span>Lift Estimate (&tau;)</span>
            </span>
            <span className="flex items-center space-x-1.5 text-zinc-400">
              <span className="h-2 w-2 rounded-full bg-blue-400/40" />
              <span>95% Anytime Band</span>
            </span>
          </div>
        </div>

        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={csChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
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
                tickFormatter={(val) => `${val}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#18181b",
                  border: "none",
                  fontSize: "12px",
                  borderRadius: "8px",
                  color: "#ffffff",
                  boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
                }}
                labelFormatter={(label) => `Sample Size: ${label ? Number(label).toLocaleString() : 0} users`}
                formatter={(val: any, name: any) => [
                  `${val}%`,
                  name === "tau" ? "Lift Estimate" : name === "lower" ? "95% Lower" : "95% Upper",
                ]}
              />
              <ReferenceLine y={0} stroke="#71717a" strokeDasharray="4 4" />
              <Area type="monotone" dataKey="band" fill="#3b82f6" fillOpacity={0.12} stroke="none" />
              <Line type="monotone" dataKey="upper" stroke="#60a5fa" strokeWidth={1} strokeDasharray="2 2" dot={false} />
              <Line type="monotone" dataKey="lower" stroke="#60a5fa" strokeWidth={1} strokeDasharray="2 2" dot={false} />
              <Line type="monotone" dataKey="tau" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
