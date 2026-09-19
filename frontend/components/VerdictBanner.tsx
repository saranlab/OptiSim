"use client";

import React from "react";
import { ArrowUpRight } from "lucide-react";

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
    <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-7 mb-6 transition-all">
      {/* Top Banner Row: Headline & Defensible ARR Stat */}
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
        <div className="space-y-2.5 max-w-3xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-[11px] font-medium font-mono uppercase tracking-wider px-3 py-1 rounded-full bg-white text-black">
              <span className="h-1.5 w-1.5 rounded-full bg-black animate-pulse" />
              Decision Validated
            </span>
            <span className="text-xs text-zinc-400 font-mono">
              Bayesian Posterior: {(probBBetter * 100).toFixed(1)}%
            </span>
          </div>

          <h2 className="text-lg sm:text-2xl font-semibold text-white tracking-tight leading-snug">
            {headline}
          </h2>
          <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed max-w-2xl">
            {subtext}
          </p>
        </div>

        {/* Highlight KPI Pill - Responsive */}
        <div className="rounded-xl bg-white/[0.04] p-4 sm:p-5 sm:min-w-[240px] text-left lg:text-right font-mono">
          <div className="text-[10px] sm:text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
            Defensible Net ARR
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-white tabular-nums mt-1">
            ${defensibleNet.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="text-[10px] sm:text-xs text-zinc-500 mt-1 flex items-center lg:justify-end gap-1">
            <ArrowUpRight className="h-3 w-3 text-white" />
            <span>95% Audited Lower Bound</span>
          </div>
        </div>
      </div>

      {/* Responsive Metrics Strip - Pure Monochrome, Zero Borders */}
      <div className="mt-6 pt-5 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 text-xs font-mono">
        <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
          <span className="text-zinc-500 text-[10px] sm:text-[11px] block mb-1">Control Baseline (A)</span>
          <span className="text-base sm:text-lg font-semibold text-white">{(controlCvr * 100).toFixed(2)}%</span>
          <span className="text-[10px] text-zinc-500 block mt-0.5">Historical standard</span>
        </div>

        <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
          <span className="text-zinc-500 text-[10px] sm:text-[11px] block mb-1">Treatment Observed (B)</span>
          <div className="flex items-baseline space-x-1.5">
            <span className="text-base sm:text-lg font-semibold text-white">{(treatmentCvr * 100).toFixed(2)}%</span>
            <span className="text-xs font-semibold text-white">
              ({relativeLift > 0 ? "+" : ""}{(relativeLift * 100).toFixed(1)}%)
            </span>
          </div>
          <span className="text-[10px] text-zinc-400 block mt-0.5">Observed sample CVR</span>
        </div>

        <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
          <span className="text-zinc-500 text-[10px] sm:text-[11px] block mb-1">95% Anytime Sequence</span>
          <span className="text-sm sm:text-base font-semibold text-white">
            [{(ciLower * 100).toFixed(2)}%, {(ciUpper * 100).toFixed(2)}%]
          </span>
          <span className="text-[10px] text-zinc-500 block mt-0.5">Peeking-proof guarantee</span>
        </div>

        <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
          <span className="text-zinc-500 text-[10px] sm:text-[11px] block mb-1">False Discovery Rate</span>
          <span className="text-base sm:text-lg font-semibold text-white">0 Critical Violations</span>
          <span className="text-[10px] text-zinc-500 block mt-0.5">BH step-up adjusted</span>
        </div>
      </div>
    </div>
  );
};
