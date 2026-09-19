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
import { Play } from "lucide-react";
import { LinUCBResponse, ThompsonResponse } from "../lib/types";

interface TabBanditsProps {
  thompsonData: ThompsonResponse;
  linucbData: LinUCBResponse;
  onSimulateThompson: (rounds: number, delay: number) => void;
  onSimulateLinUCB: (rounds: number, alpha: number) => void;
}

export const TabBandits: React.FC<TabBanditsProps> = ({
  thompsonData,
  linucbData,
  onSimulateThompson,
  onSimulateLinUCB,
}) => {
  const [nRounds, setNRounds] = useState<number>(1000);
  const [delayRounds, setDelayRounds] = useState<number>(5);
  const [linucbRounds, setLinucbRounds] = useState<number>(500);
  const [linucbAlpha, setLinucbAlpha] = useState<number>(1.0);

  const thompsonChartData = Object.keys(thompsonData.pulls).map((arm) => ({
    name: arm,
    allocationPct: +((thompsonData.allocation_rates[arm] || 0) * 100).toFixed(1),
    pulls: thompsonData.pulls[arm] || 0,
    cvr: +((thompsonData.conversion_rates[arm] || 0) * 100).toFixed(2),
  }));

  // Pure monochrome grayscale shades
  const SHADES = ["#ffffff", "rgba(255, 255, 255, 0.65)", "rgba(255, 255, 255, 0.35)"];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Module 1: Thompson Sampling */}
        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-1">
            <div>
              <h3 className="text-sm font-medium text-white">Thompson Sampling Routing</h3>
              <p className="text-xs text-zinc-400">Bayesian dynamic exploration vs. exploitation</p>
            </div>
            <span className="rounded-full bg-white/[0.08] px-2.5 py-0.5 text-[10px] font-mono text-white font-medium w-fit">
              Beta-Binomial
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
            <div className="space-y-1.5 rounded-xl bg-white/[0.02] p-3">
              <div className="flex justify-between text-zinc-400">
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
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>

            <div className="space-y-1.5 rounded-xl bg-white/[0.02] p-3">
              <div className="flex justify-between text-zinc-400">
                <span>Delay:</span>
                <span className="text-white font-bold">{delayRounds} rounds</span>
              </div>
              <input
                type="range"
                min="0"
                max="25"
                step="1"
                value={delayRounds}
                onChange={(e) => setDelayRounds(parseInt(e.target.value, 10))}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>
          </div>

          <button
            onClick={() => onSimulateThompson(nRounds, delayRounds)}
            className="w-full rounded-xl bg-white hover:bg-zinc-200 text-black py-2.5 text-xs font-mono font-semibold flex items-center justify-center gap-2 shadow-sm transition-all active:scale-[0.98]"
          >
            <Play className="h-3 w-3 fill-black text-black" />
            <span>Simulate Allocation</span>
          </button>

          <div className="h-56 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={thompsonChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="name" stroke="#71717a" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#71717a" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#18181b",
                    border: "none",
                    fontSize: "12px",
                    borderRadius: "8px",
                    color: "#ffffff",
                    boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
                  }}
                  formatter={(v: any) => [`${v}%`, "Traffic Share"]}
                />
                <Bar dataKey="allocationPct" radius={[4, 4, 0, 0]}>
                  {thompsonChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={SHADES[index % SHADES.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 text-xs font-mono">
            <div className="rounded-xl bg-white/[0.02] p-3">
              <span className="text-[10px] text-zinc-500 block mb-1">Cumulative Rewards</span>
              <span className="text-base sm:text-lg font-semibold text-white">
                {thompsonData.cumulative_reward.toLocaleString()}
              </span>
            </div>
            <div className="rounded-xl bg-white/[0.02] p-3">
              <span className="text-[10px] text-zinc-500 block mb-1">Cumulative Regret</span>
              <span className="text-base sm:text-lg font-semibold text-zinc-400">
                {thompsonData.regret.toFixed(1)} conv
              </span>
            </div>
          </div>
        </div>

        {/* Module 2: LinUCB Contextual Bandit */}
        <div className="rounded-2xl bg-white/[0.03] p-5 sm:p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-1">
            <div>
              <h3 className="text-sm font-medium text-white">LinUCB Contextual Personalization</h3>
              <p className="text-xs text-zinc-400">Disjoint Ridge Regression over 3D context vectors</p>
            </div>
            <span className="rounded-full bg-white/[0.06] px-2.5 py-0.5 text-[10px] font-mono text-zinc-400 w-fit">
              Li et al.
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
            <div className="space-y-1.5 rounded-xl bg-white/[0.02] p-3">
              <div className="flex justify-between text-zinc-400">
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
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>

            <div className="space-y-1.5 rounded-xl bg-white/[0.02] p-3">
              <div className="flex justify-between text-zinc-400">
                <span>Exploration &alpha;:</span>
                <span className="text-white font-bold">{linucbAlpha.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="3.0"
                step="0.1"
                value={linucbAlpha}
                onChange={(e) => setLinucbAlpha(parseFloat(e.target.value))}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>
          </div>

          <button
            onClick={() => onSimulateLinUCB(linucbRounds, linucbAlpha)}
            className="w-full rounded-xl bg-white/[0.08] hover:bg-white/[0.14] text-white py-2.5 text-xs font-mono font-semibold flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
          >
            <Play className="h-3 w-3 fill-white" />
            <span>Simulate LinUCB Routing</span>
          </button>

          <div className="space-y-2.5 pt-2">
            <span className="text-xs font-medium text-zinc-400 block font-mono">Personalized Allocation</span>
            {Object.keys(linucbData.arm_pulls).map((arm) => {
              const pulls = linucbData.arm_pulls[arm] || 0;
              const totalPulls = Object.values(linucbData.arm_pulls).reduce((a, b) => a + b, 0) || 1;
              const pct = (pulls / totalPulls) * 100;
              const rew = linucbData.arm_rewards[arm] || 0;
              const armCtr = pulls > 0 ? (rew / pulls) * 100 : 0;

              return (
                <div key={arm} className="rounded-xl bg-white/[0.02] p-3 text-xs font-mono">
                  <div className="flex flex-wrap justify-between text-zinc-300 mb-1.5 gap-1">
                    <span className="font-medium text-white">{arm}</span>
                    <span className="text-zinc-400 text-[11px]">
                      {pulls.toLocaleString()} pulls ({pct.toFixed(1)}%) | CTR:{" "}
                      <span className="text-white font-semibold">{armCtr.toFixed(1)}%</span>
                    </span>
                  </div>
                  <div className="h-1 w-full rounded-full bg-white/[0.06] overflow-hidden">
                    <div className="h-full bg-white transition-all duration-300" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-2 flex items-center justify-between text-xs font-mono">
            <span className="text-zinc-400">Achieved Empirical CTR:</span>
            <span className="text-white font-bold text-sm">
              {(linucbData.ctr * 100).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
