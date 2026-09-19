"use client";

import React from "react";

interface VerdictBannerProps {
  status: "success" | "warning" | "danger";
  headline: string;
  subtext: string;
  controlCvr: number;
  treatmentCvr: number;
  relativeLift: number;
  ciLower: number;
  ciUpper: number;
  probBBetter: number;
  defensibleNet: number;
}

export const VerdictBanner: React.FC<VerdictBannerProps> = ({
  headline,
  subtext,
  controlCvr,
  treatmentCvr,
  relativeLift,
  ciLower,
  ciUpper,
  probBBetter,
  defensibleNet,
}) => {
  return (
    <div className="rounded-xl bg-white/[0.03] p-6 mb-6">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div className="space-y-2 max-w-3xl">
          <div className="flex items-center space-x-2.5">
            <span className="inline-flex items-center gap-1.5 text-[11px] font-medium font-mono uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-blue-600/20 text-blue-400">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
              Decision Validated
            </span>
            <span className="text-xs text-zinc-500 font-mono">
              Bayesian Confidence: {(probBBetter * 100).toFixed(1)}%
            </span>
          </div>

          <h2 className="text-xl font-medium text-white tracking-tight">{headline}</h2>
          <p className="text-xs text-zinc-400 leading-relaxed max-w-2xl">{subtext}</p>
        </div>

        {/* Defensible Floor Stat Box - No Borders */}
        <div className="rounded-xl bg-white/[0.03] p-4 min-w-[220px] text-right font-mono">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">
            Defensible Net ARR
          </div>
          <div className="text-2xl font-bold text-white tabular-nums mt-0.5">
            ${defensibleNet.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="text-[10px] text-zinc-500 mt-1">
            95% Conservative Floor
          </div>
        </div>
      </div>

      {/* Metric Items Strip - Borderless Minimal */}
      <div className="mt-6 pt-4 grid grid-cols-2 gap-4 sm:grid-cols-4 text-xs font-mono">
        <div className="rounded-lg bg-white/[0.02] p-3">
          <span className="text-zinc-500 text-[10px] block mb-1">Control Baseline (A)</span>
          <span className="text-sm font-semibold text-white">{(controlCvr * 100).toFixed(2)}%</span>
        </div>
        <div className="rounded-lg bg-white/[0.02] p-3">
          <span className="text-zinc-500 text-[10px] block mb-1">Treatment Observed (B)</span>
          <span className="text-sm font-semibold text-blue-400">
            {(treatmentCvr * 100).toFixed(2)}% ({relativeLift > 0 ? "+" : ""}{(relativeLift * 100).toFixed(1)}%)
          </span>
        </div>
        <div className="rounded-lg bg-white/[0.02] p-3">
          <span className="text-zinc-500 text-[10px] block mb-1">Anytime Sequence [95%]</span>
          <span className="text-sm font-semibold text-zinc-200">
            [{(ciLower * 100).toFixed(2)}%, {(ciUpper * 100).toFixed(2)}%]
          </span>
        </div>
        <div className="rounded-lg bg-white/[0.02] p-3">
          <span className="text-zinc-500 text-[10px] block mb-1">P(B &gt; A) Probability</span>
          <span className="text-sm font-semibold text-blue-400">
            {(probBBetter * 100).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
};
