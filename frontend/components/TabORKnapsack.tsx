"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
} from "recharts";
import { Sliders, Check } from "lucide-react";
import { CandidateFeature, PortfolioOptimizeResponse } from "../lib/types";

interface TabORKnapsackProps {
  portfolioData: PortfolioOptimizeResponse;
  candidates: CandidateFeature[];
  onReoptimize: (params: {
    max_budget: number;
    max_latency_ms: number;
    max_effort_points: number;
    robust_mode: boolean;
    churn_penalty_weight: number;
  }) => void;
}

export const TabORKnapsack: React.FC<TabORKnapsackProps> = ({
  portfolioData,
  onReoptimize,
}) => {
  const [maxBudget, setMaxBudget] = useState<number>(10000);
  const [maxLatency, setMaxLatency] = useState<number>(50);
  const [maxEffort, setMaxEffort] = useState<number>(40);
  const [robustMode, setRobustMode] = useState<boolean>(true);
  const [churnWeight, setChurnWeight] = useState<number>(1.0);

  const handleParamChange = (
    newBudget = maxBudget,
    newLatency = maxLatency,
    newEffort = maxEffort,
    newRobust = robustMode,
    newChurn = churnWeight
  ) => {
    onReoptimize({
      max_budget: newBudget,
      max_latency_ms: newLatency,
      max_effort_points: newEffort,
      robust_mode: newRobust,
      churn_penalty_weight: newChurn,
    });
  };

  const frontierPoints = portfolioData.efficient_frontier || [];

  return (
    <div className="space-y-6">
      {/* 4 Metric Cards - Zero Borders */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Unlocked ARR
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-semibold font-mono text-white tabular-nums">
              ${portfolioData.total_value.toLocaleString()}
            </span>
            <span className="rounded-full bg-blue-600/20 px-2 py-0.5 text-[10px] font-mono text-blue-400 font-medium">
              {portfolioData.is_robust ? "Robust Floor" : "Point Value"}
            </span>
          </div>
          <div className="mt-2 text-xs text-zinc-500 font-mono">
            {portfolioData.churn_penalty_deducted > 0
              ? `-$${portfolioData.churn_penalty_deducted.toLocaleString()} churn risk deducted`
              : "Zero churn deduction"}
          </div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Capital Budget Consumed
          </div>
          <div className="mt-2 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl font-semibold text-white tabular-nums">
              ${portfolioData.total_cost.toLocaleString()}
            </span>
            <span className="text-xs text-zinc-500">/ ${maxBudget.toLocaleString()}</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className="h-1 w-full rounded-full bg-white/[0.06] overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${Math.min(100, portfolioData.budget_utilization_pct)}%` }}
              />
            </div>
            <span className="text-xs font-mono text-zinc-400">
              {portfolioData.budget_utilization_pct.toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Latency Overhead SLA
          </div>
          <div className="mt-2 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl font-semibold text-white tabular-nums">
              {portfolioData.total_latency_ms > 0 ? "+" : ""}
              {portfolioData.total_latency_ms.toFixed(1)} ms
            </span>
            <span className="text-xs text-zinc-500">/ {maxLatency} ms</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className="h-1 w-full rounded-full bg-white/[0.06] overflow-hidden">
              <div
                className="h-full bg-white transition-all duration-300"
                style={{
                  width: `${Math.max(0, Math.min(100, portfolioData.latency_utilization_pct))}%`,
                }}
              />
            </div>
            <span className="text-xs font-mono text-zinc-400">
              {portfolioData.latency_utilization_pct.toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="rounded-xl bg-white/[0.03] p-5">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider font-mono">
            Sprint Capacity
          </div>
          <div className="mt-2 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl font-semibold text-white tabular-nums">
              {portfolioData.total_effort_points.toFixed(0)} pts
            </span>
            <span className="text-xs text-zinc-500">/ {maxEffort} pts</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className="h-1 w-full rounded-full bg-white/[0.06] overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${Math.min(100, portfolioData.effort_utilization_pct)}%` }}
              />
            </div>
            <span className="text-xs font-mono text-zinc-400">
              {portfolioData.effort_utilization_pct.toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Controls & Efficient Frontier Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Controls Column */}
        <div className="rounded-xl bg-white/[0.03] p-6 space-y-5">
          <div>
            <h3 className="text-sm font-medium text-white flex items-center gap-2 font-mono">
              <Sliders className="h-3.5 w-3.5 text-blue-400" />
              <span>MILP Constraints</span>
            </h3>
            <p className="text-xs text-zinc-400 mt-1">
              Solved via HiGHS Branch-and-Cut MILP engine.
            </p>
          </div>

          {/* Mode Switcher - Zero Borders */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-zinc-400 block font-mono">Objective</label>
            <div className="grid grid-cols-2 gap-1 rounded-lg bg-white/[0.03] p-1 text-xs font-mono">
              <button
                onClick={() => {
                  setRobustMode(true);
                  handleParamChange(maxBudget, maxLatency, maxEffort, true, churnWeight);
                }}
                className={`py-1.5 px-2 rounded-md text-left transition-all ${
                  robustMode
                    ? "bg-blue-600 text-white font-medium"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <div>Robust Floor</div>
                <div className="text-[10px] opacity-70">95% Bound</div>
              </button>

              <button
                onClick={() => {
                  setRobustMode(false);
                  handleParamChange(maxBudget, maxLatency, maxEffort, false, churnWeight);
                }}
                className={`py-1.5 px-2 rounded-md text-left transition-all ${
                  !robustMode
                    ? "bg-blue-600 text-white font-medium"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <div>Expected</div>
                <div className="text-[10px] opacity-70">Point Mean</div>
              </button>
            </div>
          </div>

          {/* Sliders */}
          <div className="space-y-4 pt-1 text-xs font-mono">
            <div className="space-y-1.5">
              <div className="flex justify-between">
                <span className="text-zinc-400">Budget Limit:</span>
                <span className="text-white font-bold">${maxBudget.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="2000"
                max="25000"
                step="500"
                value={maxBudget}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  setMaxBudget(val);
                  handleParamChange(val, maxLatency, maxEffort, robustMode, churnWeight);
                }}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.08] accent-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between">
                <span className="text-zinc-400">Max Latency:</span>
                <span className="text-white font-bold">{maxLatency} ms</span>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={maxLatency}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  setMaxLatency(val);
                  handleParamChange(maxBudget, val, maxEffort, robustMode, churnWeight);
                }}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.08] accent-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between">
                <span className="text-zinc-400">Sprint Capacity:</span>
                <span className="text-white font-bold">{maxEffort} pts</span>
              </div>
              <input
                type="range"
                min="15"
                max="80"
                step="5"
                value={maxEffort}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  setMaxEffort(val);
                  handleParamChange(maxBudget, maxLatency, val, robustMode, churnWeight);
                }}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.08] accent-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between">
                <span className="text-zinc-400">Churn Penalty:</span>
                <span className="text-white font-bold">{churnWeight.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="3.0"
                step="0.5"
                value={churnWeight}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setChurnWeight(val);
                  handleParamChange(maxBudget, maxLatency, maxEffort, robustMode, val);
                }}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.08] accent-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Efficient Frontier Chart - Zero Borders */}
        <div className="rounded-xl bg-white/[0.03] p-6 lg:col-span-2 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2">
            <div>
              <h3 className="text-sm font-medium text-white">
                Efficient Frontier Curve
              </h3>
              <p className="text-xs text-zinc-400 mt-0.5">
                Maximal commercial ARR unlocked across varying budget envelopes.
              </p>
            </div>
            <div className="text-xs font-mono text-zinc-400">
              Optimal ARR: <span className="text-blue-400 font-bold">${portfolioData.total_value.toLocaleString()}</span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={frontierPoints} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis
                  dataKey="budget"
                  stroke="#71717a"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <YAxis
                  stroke="#71717a"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
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
                  labelFormatter={(b) => `Budget: $${b ? Number(b).toLocaleString() : 0}`}
                  formatter={(v: any) => [`$${Number(v).toLocaleString()}`, "Max ARR"]}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 2.5, fill: "#3b82f6" }}
                />
                <ReferenceDot
                  x={portfolioData.total_cost}
                  y={portfolioData.total_value}
                  r={5}
                  fill="#ffffff"
                  stroke="#3b82f6"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Candidate Feature Allocation Roster - Zero Borders */}
      <div className="rounded-xl bg-white/[0.03] p-6 space-y-4">
        <div className="flex items-center justify-between pb-2">
          <div>
            <h3 className="text-sm font-medium text-white">
              Knapsack Feature Allocation Roster
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              MILP solver optimization across latency SLAs, capacity, and churn penalty.
            </p>
          </div>
          <span className="rounded-full bg-white/[0.05] px-3 py-1 text-xs font-mono text-zinc-300">
            {portfolioData.selected_features.length} Selected / {portfolioData.rejected_features.length} Deferred
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="text-zinc-500">
                <th className="py-3 px-3 font-normal">Status</th>
                <th className="py-3 px-3 font-normal">Feature</th>
                <th className="py-3 px-3 font-normal">Category</th>
                <th className="py-3 px-3 font-normal">Value (ARR)</th>
                <th className="py-3 px-3 font-normal">Cost</th>
                <th className="py-3 px-3 font-normal">Latency</th>
                <th className="py-3 px-3 font-normal">Effort</th>
                <th className="py-3 px-3 font-normal text-right">Churn Risk</th>
              </tr>
            </thead>
            <tbody>
              {portfolioData.selected_features.map((feat) => (
                <tr key={feat.feature_id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-3">
                    <span className="inline-flex items-center gap-1 rounded-full bg-blue-600/20 px-2.5 py-0.5 text-[10px] font-medium text-blue-400 uppercase">
                      <Check className="h-3 w-3" /> Selected
                    </span>
                  </td>
                  <td className="py-3 px-3 font-medium text-white">{feat.name}</td>
                  <td className="py-3 px-3 text-zinc-500">{feat.category}</td>
                  <td className="py-3 px-3">
                    <div className="font-semibold text-white">${feat.expected_value.toLocaleString()}</div>
                    {feat.defensible_floor_value !== undefined && feat.defensible_floor_value !== null && (
                      <div className="text-[10px] text-blue-400">
                        Floor: ${feat.defensible_floor_value.toLocaleString()}
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-3 text-zinc-300">${feat.cost.toLocaleString()}</td>
                  <td className="py-3 px-3 text-zinc-300">
                    {feat.latency_ms > 0 ? "+" : ""}
                    {feat.latency_ms} ms
                  </td>
                  <td className="py-3 px-3 text-zinc-300">{feat.effort_points} pts</td>
                  <td className="py-3 px-3 text-right">
                    {feat.downstream_churn_risk > 0 ? (
                      <span className="text-zinc-300">
                        ${feat.downstream_churn_risk.toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-zinc-600">None</span>
                    )}
                  </td>
                </tr>
              ))}

              {portfolioData.rejected_features.map((feat) => (
                <tr key={feat.feature_id} className="opacity-40 hover:opacity-80 transition-all">
                  <td className="py-3 px-3">
                    <span className="inline-block rounded-full bg-white/[0.04] px-2.5 py-0.5 text-[10px] font-medium text-zinc-400 uppercase">
                      Deferred
                    </span>
                  </td>
                  <td className="py-3 px-3 text-zinc-400">{feat.name}</td>
                  <td className="py-3 px-3 text-zinc-600">{feat.category}</td>
                  <td className="py-3 px-3 text-zinc-400">${feat.expected_value.toLocaleString()}</td>
                  <td className="py-3 px-3 text-zinc-400">${feat.cost.toLocaleString()}</td>
                  <td className="py-3 px-3 text-zinc-400">{feat.latency_ms > 0 ? "+" : ""}{feat.latency_ms} ms</td>
                  <td className="py-3 px-3 text-zinc-400">{feat.effort_points} pts</td>
                  <td className="py-3 px-3 text-right text-zinc-600">
                    {feat.downstream_churn_risk > 0 ? `$${feat.downstream_churn_risk.toLocaleString()}` : "None"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Clean Operations Research Formulation block */}
      <div className="rounded-xl bg-white/[0.03] p-6 space-y-3">
        <h3 className="text-sm font-medium text-white">
          Formulation: Multi-Dimensional 0-1 Knapsack MILP
        </h3>
        <p className="text-xs text-zinc-400 leading-relaxed">
          Let <span className="font-mono bg-white/[0.06] px-1.5 py-0.5 rounded text-white">x_i ∈ &#123;0, 1&#125;</span> denote the binary deployment indicator for candidate feature <span className="font-mono bg-white/[0.06] px-1.5 py-0.5 rounded text-white">i ∈ &#123;1, ..., n&#125;</span>.
        </p>

        <div className="rounded-lg bg-white/[0.02] p-4 font-mono text-xs text-zinc-300 space-y-2">
          <div className="font-semibold text-blue-400">
            maximize: &Sigma; [ v_i(floor) - w_churn &times; ChurnRisk_i ] &times; x_i
          </div>
          <div className="text-zinc-400 pl-4 space-y-1">
            <div>subject to:</div>
            <div>&bull; &Sigma; (Cost_i &times; x_i) &le; Budget_SLA</div>
            <div>&bull; &Sigma; (Latency_i &times; x_i) &le; Latency_SLA</div>
            <div>&bull; &Sigma; (Effort_i &times; x_i) &le; Sprint_Capacity</div>
            <div>&bull; &Sigma; (x_j) &le; 1 for j in ConflictGroup_k</div>
          </div>
        </div>
      </div>
    </div>
  );
};
