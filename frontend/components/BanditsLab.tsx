"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import {
  Sliders,
  Play,
  RotateCcw,
  Zap,
  TrendingUp,
  Cpu,
  Layers,
  Sparkles,
} from "lucide-react";
import { LinUCBResponse, ThompsonResponse } from "../lib/types";

interface BanditsLabProps {
  thompsonData: ThompsonResponse;
  linucbData: LinUCBResponse;
  onSimulateThompson: (rounds: number, delay: number) => void;
  onSimulateLinUCB: (rounds: number, alpha: number) => void;
}

export const BanditsLab: React.FC<BanditsLabProps> = ({
  thompsonData,
  linucbData,
  onSimulateThompson,
  onSimulateLinUCB,
}) => {
  const [nRounds, setNRounds] = useState<number>(1000);
  const [delayRounds, setDelayRounds] = useState<number>(5);
  const [linucbRounds, setLinucbRounds] = useState<number>(500);
  const [linucbAlpha, setLinucbAlpha] = useState<number>(1.0);

  // Prepare Thompson arm chart data
  const thompsonChartData = Object.keys(thompsonData.pulls).map((arm) => ({
    name: arm,
    allocationPct: +((thompsonData.allocation_rates[arm] || 0) * 100).toFixed(1),
    pulls: thompsonData.pulls[arm] || 0,
    cvr: +((thompsonData.conversion_rates[arm] || 0) * 100).toFixed(2),
  }));

  const COLORS = ["#06b6d4", "#3b82f6", "#10b981", "#8b5cf6"];

  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
              <Zap className="h-4 w-4 text-cyan-400" />
              <span>Adaptive Personalization & Multi-Armed Bandits</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Dynamic traffic allocation minimizing regret under delayed enterprise feedback (Chapelle & Li 2011) and personalized contextual routing (Li et al. 2010).
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Module 1: Thompson Sampling with Delayed Feedback */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm space-y-5">
          <div className="border-b border-slate-800 pb-3 flex justify-between items-center">
            <div>
              <h4 className="text-sm font-bold text-white font-mono">Thompson Sampling Simulation</h4>
              <p className="text-xs text-slate-400">Bayesian dynamic exploration vs. exploitation</p>
            </div>
            <span className="rounded bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 text-[10px] font-mono text-cyan-400">
              Beta-Binomial
            </span>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-2 gap-4 text-xs font-mono">
            <div className="space-y-1">
              <div className="flex justify-between text-slate-400">
                <span>Arrivals:</span>
                <span className="text-white font-bold">{nRounds.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="200"
                max="3000"
                step="100"
                value={nRounds}
                onChange={(e) => setNRounds(parseInt(e.target.value, 10))}
                className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
              />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-slate-400">
                <span>Feedback Delay:</span>
                <span className="text-cyan-400 font-bold">{delayRounds} rounds</span>
              </div>
              <input
                type="range"
                min="0"
                max="25"
                step="1"
                value={delayRounds}
                onChange={(e) => setDelayRounds(parseInt(e.target.value, 10))}
                className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
              />
            </div>
          </div>

          <button
            onClick={() => onSimulateThompson(nRounds, delayRounds)}
            className="w-full rounded-md border border-cyan-500/30 bg-cyan-950/50 hover:bg-cyan-900/50 text-cyan-400 py-2 text-xs font-mono font-bold flex items-center justify-center gap-2 transition-all shadow-sm"
          >
            <Play className="h-3.5 w-3.5" />
            <span>Run Thompson Allocation Simulation</span>
          </button>

          {/* Allocation Bar Chart */}
          <div className="h-56 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={thompsonChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} tickFormatter={(v) => `${v}%`} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    fontSize: "12px",
                    borderRadius: "6px",
                  }}
                  formatter={(v: any) => [`${v}%`, "Traffic Share"]}
                />
                <Bar dataKey="allocationPct" radius={[4, 4, 0, 0]}>
                  {thompsonChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800 text-xs font-mono">
            <div className="rounded border border-slate-800 bg-slate-950/40 p-2.5">
              <span className="text-[10px] text-slate-500 block">Total Reward Conversions</span>
              <span className="text-base font-bold text-emerald-400">
                {thompsonData.cumulative_reward.toLocaleString()}
              </span>
            </div>
            <div className="rounded border border-slate-800 bg-slate-950/40 p-2.5">
              <span className="text-[10px] text-slate-500 block">Cumulative Regret</span>
              <span className="text-base font-bold text-slate-300">
                {thompsonData.regret.toFixed(1)} conversions
              </span>
            </div>
          </div>
        </div>

        {/* Module 2: Contextual Bandit (LinUCB) */}
        <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-sm space-y-5">
          <div className="border-b border-slate-800 pb-3 flex justify-between items-center">
            <div>
              <h4 className="text-sm font-bold text-white font-mono">LinUCB Contextual Personalization</h4>
              <p className="text-xs text-slate-400">Disjoint Ridge Regression over 3D context vectors</p>
            </div>
            <span className="rounded bg-indigo-950/60 border border-indigo-500/30 px-2 py-0.5 text-[10px] font-mono text-indigo-400">
              Li et al. (WSDM)
            </span>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-2 gap-4 text-xs font-mono">
            <div className="space-y-1">
              <div className="flex justify-between text-slate-400">
                <span>Rounds:</span>
                <span className="text-white font-bold">{linucbRounds}</span>
              </div>
              <input
                type="range"
                min="100"
                max="2000"
                step="50"
                value={linucbRounds}
                onChange={(e) => setLinucbRounds(parseInt(e.target.value, 10))}
                className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-indigo-400"
              />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-slate-400">
                <span>Exploration &alpha;:</span>
                <span className="text-indigo-400 font-bold">{linucbAlpha.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="3.0"
                step="0.1"
                value={linucbAlpha}
                onChange={(e) => setLinucbAlpha(parseFloat(e.target.value))}
                className="w-full h-1.5 cursor-pointer appearance-none rounded-lg bg-slate-800 accent-indigo-400"
              />
            </div>
          </div>

          <button
            onClick={() => onSimulateLinUCB(linucbRounds, linucbAlpha)}
            className="w-full rounded-md border border-indigo-500/30 bg-indigo-950/50 hover:bg-indigo-900/50 text-indigo-400 py-2 text-xs font-mono font-bold flex items-center justify-center gap-2 transition-all shadow-sm"
          >
            <Play className="h-3.5 w-3.5" />
            <span>Simulate LinUCB Contextual Routing</span>
          </button>

          {/* LinUCB Arm Routing Summary */}
          <div className="space-y-2.5 pt-2">
            <span className="text-xs font-semibold text-slate-300 block">Personalized Variant Allocation</span>
            {Object.keys(linucbData.arm_pulls).map((arm) => {
              const pulls = linucbData.arm_pulls[arm] || 0;
              const totalPulls = Object.values(linucbData.arm_pulls).reduce((a, b) => a + b, 0) || 1;
              const pct = (pulls / totalPulls) * 100;
              const rew = linucbData.arm_rewards[arm] || 0;
              const armCtr = pulls > 0 ? (rew / pulls) * 100 : 0;

              return (
                <div key={arm} className="rounded border border-slate-800 bg-slate-950/40 p-2.5 text-xs font-mono">
                  <div className="flex justify-between text-slate-300 mb-1">
                    <span className="font-bold text-white">{arm}</span>
                    <span className="text-slate-400">
                      {pulls.toLocaleString()} pulls ({pct.toFixed(1)}%) | CTR:{" "}
                      <span className="text-emerald-400 font-bold">{armCtr.toFixed(1)}%</span>
                    </span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full bg-indigo-400 transition-all duration-300" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* LinUCB CTR Summary */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Achieved Empirical CTR:</span>
            <span className="text-emerald-400 font-bold text-sm">
              {(linucbData.ctr * 100).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
