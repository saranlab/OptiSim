"use client";

import React from "react";
import { AlertCircle } from "lucide-react";

interface TabFinancialsProps {
  annualTraffic: number;
  revPerConv: number;
  setupCost: number;
  observedLiftPct: number;
  ciLowerPct: number;
}

export const TabFinancials: React.FC<TabFinancialsProps> = ({
  annualTraffic,
  revPerConv,
  setupCost,
  observedLiftPct,
  ciLowerPct,
}) => {
  // Financial computations
  const pointGross = annualTraffic * (observedLiftPct / 100) * 0.10 * revPerConv;
  const pointNet = pointGross - setupCost;

  const defensibleGross = Math.max(0, annualTraffic * (ciLowerPct / 100) * 0.10 * revPerConv);
  const defensibleNet = defensibleGross - setupCost;

  const dailyGain = pointGross / 365;
  const breakevenDays = dailyGain > 0 && setupCost > 0 ? Math.ceil(setupCost / dailyGain) : 0;

  return (
    <div className="space-y-6">
      {/* 4 KPI Cards - Zero Borders */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Point Estimate Net ARR
          </div>
          <div className="mt-2 text-2xl font-semibold font-mono text-white tabular-nums">
            ${pointNet.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="mt-2 text-xs text-zinc-500 flex items-center gap-1 font-mono">
            <AlertCircle className="h-3.5 w-3.5 shrink-0 text-blue-400" />
            <span>Vulnerable to Winner's Curse</span>
          </div>
        </div>

        <div className="rounded-xl bg-blue-600/10 p-5">
          <div className="text-[11px] font-medium text-blue-400 uppercase tracking-wider font-mono">
            Defensible Net ARR
          </div>
          <div className="mt-2 text-2xl font-semibold font-mono text-white tabular-nums">
            ${defensibleNet.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="mt-2 text-xs text-blue-400 font-mono">
            95% Confidence Lower Bound
          </div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Implementation Sunk Cost
          </div>
          <div className="mt-2 text-2xl font-semibold font-mono text-white tabular-nums">
            ${setupCost.toLocaleString()}
          </div>
          <div className="mt-2 text-xs text-zinc-500 font-mono">Fixed engineering capital</div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Breakeven Horizon
          </div>
          <div className="mt-2 text-2xl font-semibold font-mono text-blue-400 tabular-nums">
            {breakevenDays > 0 ? `${breakevenDays} Days` : "Immediate"}
          </div>
          <div className="mt-2 text-xs text-zinc-500 font-mono">Capital recovery timeline</div>
        </div>
      </div>

      {/* Comparison Table - Zero Borders */}
      <div className="rounded-xl bg-white/[0.03] p-6 space-y-4">
        <div>
          <h3 className="text-sm font-medium text-white">
            Capital Defensibility Audit: Winner's Curse Protection
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Statistical selection bias artificially inflates observed effects. Only the confidence lower bound is fiscally defensible.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="text-zinc-500">
                <th className="py-3 px-3 font-normal">Methodology</th>
                <th className="py-3 px-3 font-normal">Assumed Lift</th>
                <th className="py-3 px-3 font-normal">Gross Lift</th>
                <th className="py-3 px-3 font-normal">Net Annual ARR</th>
                <th className="py-3 px-3 font-normal text-right">Audit Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="hover:bg-white/[0.02] transition-colors">
                <td className="py-3 px-3 font-medium text-zinc-400">
                  Naive Observed Point Estimate
                </td>
                <td className="py-3 px-3 text-zinc-400">+{observedLiftPct.toFixed(1)}%</td>
                <td className="py-3 px-3 text-zinc-400">
                  ${pointGross.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </td>
                <td className="py-3 px-3 text-zinc-300">
                  ${pointNet.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </td>
                <td className="py-3 px-3 text-right">
                  <span className="rounded-full bg-white/[0.04] text-zinc-400 px-2.5 py-0.5 text-[10px] font-medium uppercase">
                    Unadjusted
                  </span>
                </td>
              </tr>
              <tr className="bg-white/[0.02] hover:bg-white/[0.04] transition-colors">
                <td className="py-3 px-3 font-semibold text-white">
                  Conservative Defensible Floor
                </td>
                <td className="py-3 px-3 text-blue-400">+{ciLowerPct.toFixed(2)}%</td>
                <td className="py-3 px-3 text-zinc-200">
                  ${defensibleGross.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </td>
                <td className="py-3 px-3 font-semibold text-white">
                  ${defensibleNet.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </td>
                <td className="py-3 px-3 text-right">
                  <span className="rounded-full bg-blue-600/20 text-blue-400 px-2.5 py-0.5 text-[10px] font-medium uppercase">
                    Audited Floor
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
