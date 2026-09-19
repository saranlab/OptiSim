"use client";

import React, { useState } from "react";
import { Info } from "lucide-react";
import { GuardrailAuditResponse, HTEResponse } from "../lib/types";

interface TabSubgroupsGuardrailsProps {
  hteData: HTEResponse;
  guardrailsData: GuardrailAuditResponse;
  onRefreshGuardrails: (alphaFdr: number) => void;
}

export const TabSubgroupsGuardrails: React.FC<TabSubgroupsGuardrailsProps> = ({
  hteData,
  guardrailsData,
  onRefreshGuardrails,
}) => {
  const [fdrAlpha, setFdrAlpha] = useState<number>(0.05);

  return (
    <div className="space-y-6">
      {/* Subgroup Heterogeneity (HTE CATE Analysis) */}
      <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm font-medium text-white">
                Heterogeneous Treatment Effects (HTE) Subgroup Slicing
              </h3>
              <span className="rounded-full bg-white/[0.08] px-2.5 py-0.5 text-[10px] font-mono text-white font-medium uppercase tracking-wider">
                {hteData.has_heterogeneity ? "Heterogeneity Detected" : "Homogeneous"}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Conditional Average Treatment Effect (CATE) across segmented user cohorts. Cochran&apos;s Q interaction test distinguishes true variation from noise.
            </p>
          </div>
          <div className="text-xs font-mono text-zinc-400">
            Top Performing Cohort: <span className="text-white font-semibold">{hteData.top_performing_segment}</span>
          </div>
        </div>

        {/* Marketing Research Strategic Directive */}
        <div className="rounded-xl bg-white/[0.02] p-3.5 flex items-start gap-2.5 text-xs text-zinc-300 font-sans">
          <Info className="h-4 w-4 shrink-0 text-white mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-white">Marketing Research Directive: </span>
            {hteData.has_heterogeneity
              ? `Significant cohort divergence identified. Top lift occurs in "${hteData.top_performing_segment}". Recommend concentrating variant deployment and ad creative personalization on this high-sensitivity segment.`
              : "No significant interaction detected across cohorts. Treatment exhibits uniform lift across platforms, supporting universal 100% rollout."}
          </div>
        </div>

        {/* Forest Subgroups Table - Strict Header/Data Alignment */}
        <div className="overflow-x-auto w-full scrollbar-none">
          <table className="w-full text-xs font-mono min-w-[700px]">
            <thead>
              <tr className="text-zinc-500">
                <th className="py-3 px-3 font-normal text-left">Cohort / Segment</th>
                <th className="py-3 px-3 font-normal text-right">Sample (A / B)</th>
                <th className="py-3 px-3 font-normal text-right">CVR (A &rarr; B)</th>
                <th className="py-3 px-3 font-normal text-right">Relative Lift</th>
                <th className="py-3 px-3 font-normal text-center">Interaction Test</th>
                <th className="py-3 px-3 font-normal text-right">Segment Verdict</th>
              </tr>
            </thead>
            <tbody>
              {hteData.subgroups.map((sub) => (
                <tr key={sub.segment_name} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-3 font-medium text-white text-left">{sub.segment_name}</td>
                  <td className="py-3 px-3 text-zinc-400 text-right tabular-nums">
                    {sub.sample_size_a.toLocaleString()} / {sub.sample_size_b.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-zinc-300 text-right tabular-nums">
                    {(sub.cvr_a * 100).toFixed(2)}% &rarr; {(sub.cvr_b * 100).toFixed(2)}%
                  </td>
                  <td className="py-3 px-3 text-right tabular-nums">
                    <span className={sub.relative_lift > 0 ? "text-white font-semibold" : "text-zinc-500"}>
                      {sub.relative_lift > 0 ? "+" : ""}
                      {(sub.relative_lift * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    {sub.interaction_significant ? (
                      <span className="text-white font-medium">Significant</span>
                    ) : (
                      <span className="text-zinc-600">Neutral</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider ${
                        sub.is_significant && sub.relative_lift > 0
                          ? "bg-white text-black font-semibold"
                          : "bg-white/[0.04] text-zinc-400"
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

      {/* Multi-Metric Guardrails Matrix - Software Engineering & Reliability SRE Focus */}
      <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm font-medium text-white">
                Operational Guardrails Matrix (SRE &amp; Reliability SLAs)
              </h3>
              <span className="rounded-full bg-white/[0.06] px-2.5 py-0.5 text-[10px] font-mono text-zinc-400">
                Benjamini-Hochberg FDR Adjusted
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Guarantees conversion uplift does not inadvertently degrade latency SLAs, error rates, or downstream retention.
            </p>
          </div>

          {/* FDR Alpha Slider */}
          <div className="flex items-center space-x-3 text-xs">
            <span className="text-zinc-400 font-mono">FDR (&alpha;):</span>
            <span className="font-mono text-white font-bold tabular-nums">{fdrAlpha.toFixed(2)}</span>
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
              className="h-1 w-24 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
            />
          </div>
        </div>

        {/* Guardrail Metric Cards Grid */}
        <div className="grid grid-cols-1 gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {guardrailsData.metrics.map((metric) => {
            const isPass = metric.status === "PASS";

            return (
              <div
                key={metric.metric_name}
                className="rounded-xl bg-white/[0.02] p-4 transition-all hover:bg-white/[0.04] flex flex-col justify-between"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-white">{metric.metric_name}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-mono font-medium uppercase tracking-wider ${
                      isPass
                        ? "bg-white/[0.08] text-white"
                        : "bg-white text-black font-semibold"
                    }`}
                  >
                    {metric.status}
                  </span>
                </div>

                <div className="mt-3 flex items-baseline justify-between text-xs font-mono">
                  <span className="text-zinc-500">Baseline: {metric.control_value}</span>
                  <span className="text-white font-medium tabular-nums">Observed: {metric.treatment_value}</span>
                </div>

                <div className="mt-2 text-xs font-mono">
                  <span className="text-zinc-400">Relative Delta: </span>
                  <span className={metric.status === "FAIL" ? "text-white font-bold underline tabular-nums" : "text-white font-medium tabular-nums"}>
                    {metric.relative_change > 0 ? "+" : ""}
                    {metric.relative_change.toFixed(2)}%
                  </span>
                  <span className="text-zinc-500 text-[10px] block mt-0.5">
                    Tolerance Ceiling: &le; {metric.threshold_pct}%
                  </span>
                </div>

                <div className="mt-3 pt-2 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                  <span className="tabular-nums">Raw p: {metric.raw_p_value.toFixed(3)}</span>
                  <span className="text-zinc-300 tabular-nums">FDR q: {metric.adjusted_p_value.toFixed(3)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
