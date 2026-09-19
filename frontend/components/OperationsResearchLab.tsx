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
import {
  Cpu,
  ShieldCheck,
  ShieldAlert,
  Sliders,
  TrendingUp,
  Clock,
  DollarSign,
  Briefcase,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import { CandidateFeature, PortfolioOptimizeResponse } from "../lib/types";

interface OperationsResearchLabProps {
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

export const OperationsResearchLab: React.FC<OperationsResearchLabProps> = ({
  portfolioData,
  candidates,
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
      {/* Top Banner KPI Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {/* Metric 1: Total Value */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Unlocked Annual Value (ARR)
          </div>
          <div className="mt-1 flex items-baseline space-x-2">
            <span className="text-2xl font-bold tracking-tight text-white font-mono tabular-nums">
              ${portfolioData.total_value.toLocaleString()}
            </span>
            <span
              className={`rounded px-1.5 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider ${
                portfolioData.is_robust
                  ? "bg-cyan-950/60 text-cyan-400 border border-cyan-500/30"
                  : "bg-slate-800 text-slate-300"
              }`}
            >
              {portfolioData.is_robust ? "Robust Floor" : "Point Estimate"}
            </span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            {portfolioData.churn_penalty_deducted > 0 ? (
              <span className="text-amber-400 font-mono">
                -${portfolioData.churn_penalty_deducted.toLocaleString()} churn penalty deducted
              </span>
            ) : (
              "Zero churn deduction applied"
            )}
          </div>
        </div>

        {/* Metric 2: Capital Budget SLA */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Capital Budget Utilization
          </div>
          <div className="mt-1 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl font-bold tracking-tight text-slate-200 tabular-nums">
              ${portfolioData.total_cost.toLocaleString()}
            </span>
            <span className="text-xs text-slate-400">/ ${maxBudget.toLocaleString()}</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-cyan-400 transition-all duration-300"
                style={{ width: `${Math.min(100, portfolioData.budget_utilization_pct)}%` }}
              />
            </div>
            <span className="text-xs font-mono text-slate-400">
              {portfolioData.budget_utilization_pct.toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Metric 3: Latency SLA */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Latency Overhead SLA
          </div>
          <div className="mt-1 flex items-baseline space-x-2 font-mono">
            <span
              className={`text-2xl font-bold tracking-tight tabular-nums ${
                portfolioData.total_latency_ms < 0 ? "text-emerald-400" : "text-slate-200"
              }`}
            >
              {portfolioData.total_latency_ms > 0 ? "+" : ""}
              {portfolioData.total_latency_ms.toFixed(1)} ms
            </span>
            <span className="text-xs text-slate-400">/ {maxLatency} ms</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-emerald-400 transition-all duration-300"
                style={{
                  width: `${Math.max(0, Math.min(100, portfolioData.latency_utilization_pct))}%`,
                }}
              />
            </div>
            <span className="text-xs font-mono text-slate-400">
              {portfolioData.latency_utilization_pct.toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Metric 4: Sprint Capacity */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Sprint Engineering Capacity
          </div>
          <div className="mt-1 flex items-baseline space-x-2 font-mono">
            <span className="text-2xl font-bold tracking-tight text-slate-200 tabular-nums">
              {portfolioData.total_effort_points.toFixed(0)} pts
            </span>
            <span className="text-xs text-slate-400">/ {maxEffort} pts</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-indigo-400 transition-all duration-300"
                style={{ width: `${Math.min(100, portfolioData.effort_utilization_pct)}%` }}
              />
            </div>
            <span className="text-xs font-mono text-slate-400">
              {portfolioData.effort_utilization_pct.toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Interactive Controls & Efficient Frontier Chart */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Controls Panel (1 Col) */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm space-y-5">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              <Sliders className="h-4 w-4 text-cyan-400" />
              <span>MILP Resource & Risk Constraints</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              HiGHS Branch-and-Cut Mixed-Integer Linear Program
            </p>
          </div>

          {/* Optimization Mode Toggle */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">
              Optimization Objective Mode
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => {
                  setRobustMode(true);
                  handleParamChange(maxBudget, maxLatency, maxEffort, true, churnWeight);
                }}
                className={`flex flex-col items-start p-2.5 rounded-md border text-left transition-all ${
                  robustMode
                    ? "border-cyan-500/40 bg-cyan-950/40 text-white"
                    : "border-slate-800 bg-slate-950/40 text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className="text-xs font-bold font-mono">Robust Mode</span>
                <span className="text-[10px] text-slate-400 mt-0.5">95% Defensible Floor</span>
              </button>

              <button
                onClick={() => {
                  setRobustMode(false);
                  handleParamChange(maxBudget, maxLatency, maxEffort, false, churnWeight);
                }}
                className={`flex flex-col items-start p-2.5 rounded-md border text-left transition-all ${
                  !robustMode
                    ? "border-cyan-500/40 bg-cyan-950/40 text-white"
                    : "border-slate-800 bg-slate-950/40 text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className="text-xs font-bold font-mono">Deterministic</span>
                <span className="text-[10px] text-slate-400 mt-0.5">Expected Point Value</span>
              </button>
            </div>
          </div>

          {/* Slider 1: Capital Budget */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Capital Budget SLA:</span>
              <span className="font-mono text-white font-bold">${maxBudget.toLocaleString()}</span>
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
              className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
          </div>

          {/* Slider 2: Latency SLA */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Latency Overhead SLA:</span>
              <span className="font-mono text-white font-bold">{maxLatency} ms</span>
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
              className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
          </div>

          {/* Slider 3: Sprint Effort */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Sprint Capacity:</span>
              <span className="font-mono text-white font-bold">{maxEffort} story points</span>
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
              className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
          </div>

          {/* Slider 4: Churn Penalty */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Retention Churn Penalty Weight:</span>
              <span className="font-mono text-white font-bold">{churnWeight.toFixed(1)}x</span>
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
              className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
          </div>
        </div>

        {/* Efficient Frontier Curve (2 Cols) */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm lg:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                <span>The Efficient Frontier (Pareto Optimal Tradeoff)</span>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-300 border border-slate-700">
                  Unlocked ARR vs. Capital Budget
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Shows maximal value achievable under varying budget envelopes. Dot highlights current selected operating point.
              </p>
            </div>
            <div className="text-xs font-mono text-slate-400">
              Operating Point: <span className="text-cyan-400 font-bold">${portfolioData.total_value.toLocaleString()}</span>
            </div>
          </div>

          {/* Chart Container */}
          <div className="mt-4 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={frontierPoints} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="budget"
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                  domain={["auto", "auto"]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    fontSize: "12px",
                    borderRadius: "6px",
                  }}
                  labelFormatter={(b) => `Budget: $${b ? Number(b).toLocaleString() : 0}`}
                  formatter={(v: any) => [`$${Number(v).toLocaleString()}`, "Max Unlocked ARR"]}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#38bdf8"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: "#38bdf8" }}
                  activeDot={{ r: 6, fill: "#06b6d4" }}
                />
                <ReferenceDot
                  x={portfolioData.total_cost}
                  y={portfolioData.total_value}
                  r={6}
                  fill="#10b981"
                  stroke="#ffffff"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Diminishing marginal returns visible beyond $12k budget</span>
            <span>Green Marker: Active Portfolio</span>
          </div>
        </div>
      </div>

      {/* Candidate Features Portfolio Table */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              <span>Candidate Feature Allocation Roster</span>
              <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-cyan-400 border border-slate-700">
                {portfolioData.selected_features.length} Selected / {portfolioData.rejected_features.length} Deferred
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Features prioritized via 0-1 knapsack formulation under latency SLAs, engineering capacity, and churn risk penalties.
            </p>
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2 font-semibold">Status</th>
                <th className="pb-2 font-semibold">Feature Name</th>
                <th className="pb-2 font-semibold">Category</th>
                <th className="pb-2 font-semibold">Expected / Floor Value</th>
                <th className="pb-2 font-semibold">Cost ($)</th>
                <th className="pb-2 font-semibold">Latency Impact</th>
                <th className="pb-2 font-semibold">Effort</th>
                <th className="pb-2 font-semibold text-right">Downstream Churn Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {/* Selected Features */}
              {portfolioData.selected_features.map((feat) => (
                <tr key={feat.feature_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5">
                    <span className="inline-flex items-center gap-1 rounded bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                      <CheckCircle className="h-3 w-3" /> Selected
                    </span>
                  </td>
                  <td className="py-2.5 font-bold text-white">{feat.name}</td>
                  <td className="py-2.5 text-slate-400">{feat.category}</td>
                  <td className="py-2.5">
                    <div className="text-slate-200 font-bold">${feat.expected_value.toLocaleString()}</div>
                    {feat.defensible_floor_value !== undefined && feat.defensible_floor_value !== null && (
                      <div className="text-[10px] text-cyan-400">
                        Floor: ${feat.defensible_floor_value.toLocaleString()}
                      </div>
                    )}
                  </td>
                  <td className="py-2.5 text-slate-300">${feat.cost.toLocaleString()}</td>
                  <td className="py-2.5">
                    <span className={feat.latency_ms < 0 ? "text-emerald-400 font-bold" : "text-slate-300"}>
                      {feat.latency_ms > 0 ? "+" : ""}
                      {feat.latency_ms} ms
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-300">{feat.effort_points} pts</td>
                  <td className="py-2.5 text-right">
                    {feat.downstream_churn_risk > 0 ? (
                      <span className="text-amber-400 font-bold">
                        ${feat.downstream_churn_risk.toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-slate-500">None</span>
                    )}
                  </td>
                </tr>
              ))}

              {/* Deferred Features */}
              {portfolioData.rejected_features.map((feat) => (
                <tr key={feat.feature_id} className="opacity-60 hover:opacity-100 hover:bg-slate-800/20 transition-all">
                  <td className="py-2.5">
                    <span className="inline-flex items-center gap-1 rounded bg-slate-800 border border-slate-700 px-2 py-0.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Deferred
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-300">{feat.name}</td>
                  <td className="py-2.5 text-slate-500">{feat.category}</td>
                  <td className="py-2.5 text-slate-400">
                    <div>${feat.expected_value.toLocaleString()}</div>
                    {feat.defensible_floor_value !== undefined && feat.defensible_floor_value !== null && (
                      <div className="text-[10px] text-slate-500">
                        Floor: ${feat.defensible_floor_value.toLocaleString()}
                      </div>
                    )}
                  </td>
                  <td className="py-2.5 text-slate-400">${feat.cost.toLocaleString()}</td>
                  <td className="py-2.5 text-slate-400">
                    {feat.latency_ms > 0 ? "+" : ""}
                    {feat.latency_ms} ms
                  </td>
                  <td className="py-2.5 text-slate-400">{feat.effort_points} pts</td>
                  <td className="py-2.5 text-right text-slate-500">
                    {feat.downstream_churn_risk > 0 ? `$${feat.downstream_churn_risk.toLocaleString()}` : "None"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
