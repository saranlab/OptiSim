"use client";

import React from "react";
import { Sliders, X, Play } from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  mode: "simulation" | "real";
  setMode: (mode: "simulation" | "real") => void;
  preset: string;
  setPreset: (p: string) => void;
  confidence: string;
  setConfidence: (c: string) => void;
  power: string;
  setPower: (p: string) => void;
  baselineCvr: number;
  setBaselineCvr: (v: number) => void;
  expectedLift: number;
  setExpectedLift: (v: number) => void;
  revPerConv: number;
  setRevPerConv: (v: number) => void;
  setupCost: number;
  setSetupCost: (v: number) => void;
  annualTraffic: number;
  setAnnualTraffic: (v: number) => void;
  onApplyPreset: (presetName: string) => void;
  onRunComputation: () => void;
  isComputing: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  mode,
  setMode,
  preset,
  setPreset,
  confidence,
  setConfidence,
  power,
  setPower,
  baselineCvr,
  setBaselineCvr,
  expectedLift,
  setExpectedLift,
  revPerConv,
  setRevPerConv,
  setupCost,
  setSetupCost,
  annualTraffic,
  setAnnualTraffic,
  onApplyPreset,
  onRunComputation,
  isComputing,
}) => {
  if (!isOpen) return null;

  const presets = ["E-Commerce", "B2B SaaS", "Media", "Custom"];

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Surface - Pure Monochrome, Zero Borders */}
      <div className="relative w-full max-w-sm bg-[#0e0e11] p-6 shadow-2xl overflow-y-auto flex flex-col justify-between text-zinc-300 z-10 animate-in slide-in-from-right duration-200">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-2">
            <div className="flex items-center space-x-2">
              <Sliders className="h-4 w-4 text-white" />
              <h2 className="text-sm font-semibold text-white font-mono uppercase tracking-wider">
                Experiment Levers
              </h2>
            </div>
            <button
              onClick={onClose}
              className="rounded-full bg-white/[0.06] hover:bg-white/[0.12] p-1.5 text-zinc-400 hover:text-white transition-all"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Mode Segmented Control */}
          <div className="space-y-2">
            <label className="text-[11px] font-medium text-zinc-400 block font-mono">
              Data Mode
            </label>
            <div className="grid grid-cols-2 gap-1 rounded-lg bg-white/[0.04] p-1 text-xs font-mono">
              <button
                onClick={() => setMode("simulation")}
                className={`py-1.5 rounded-md text-center transition-all ${
                  mode === "simulation"
                    ? "bg-white text-black font-semibold shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Simulation
              </button>
              <button
                onClick={() => setMode("real")}
                className={`py-1.5 rounded-md text-center transition-all ${
                  mode === "real"
                    ? "bg-white text-black font-semibold shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Observed
              </button>
            </div>
          </div>

          {/* Archetypes */}
          <div className="space-y-2">
            <label className="text-[11px] font-medium text-zinc-400 block font-mono">
              Preset Archetypes
            </label>
            <div className="grid grid-cols-2 gap-1 text-xs font-mono">
              {presets.map((p) => (
                <button
                  key={p}
                  onClick={() => onApplyPreset(p)}
                  className={`px-3 py-1.5 rounded-md text-left transition-all ${
                    preset === p
                      ? "bg-white text-black font-semibold"
                      : "bg-white/[0.03] text-zinc-400 hover:text-white hover:bg-white/[0.06]"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Statistical Levers */}
          <div className="space-y-3 pt-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-zinc-500 font-mono">
              Statistical Calibration
            </div>

            {/* Confidence */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-zinc-400">Confidence (1 - &alpha;)</span>
                <span className="text-white font-bold">{confidence}</span>
              </div>
              <div className="grid grid-cols-3 gap-1 text-xs font-mono">
                {["95%", "99%", "90%"].map((c) => (
                  <button
                    key={c}
                    onClick={() => setConfidence(c)}
                    className={`py-1 rounded-md transition-all ${
                      confidence === c
                        ? "bg-white text-black font-semibold shadow-sm"
                        : "bg-white/[0.03] text-zinc-400 hover:text-white hover:bg-white/[0.06]"
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            {/* Power */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-zinc-400">Power (1 - &beta;)</span>
                <span className="text-white font-bold">{power}</span>
              </div>
              <div className="grid grid-cols-2 gap-1 text-xs font-mono">
                {["80%", "90%"].map((p) => (
                  <button
                    key={p}
                    onClick={() => setPower(p)}
                    className={`py-1 rounded-md transition-all ${
                      power === p
                        ? "bg-white text-black font-semibold shadow-sm"
                        : "bg-white/[0.03] text-zinc-400 hover:text-white hover:bg-white/[0.06]"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Inputs */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block">Baseline CVR (%)</label>
                <input
                  type="number"
                  min="0.1"
                  max="90"
                  step="0.5"
                  value={baselineCvr}
                  onChange={(e) => {
                    setBaselineCvr(parseFloat(e.target.value) || 0);
                    setPreset("Custom");
                  }}
                  className="w-full rounded-md bg-white/[0.05] px-2.5 py-1.5 text-white focus:bg-white/[0.10] focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block">Target Lift (%)</label>
                <input
                  type="number"
                  min="-50"
                  max="100"
                  step="0.5"
                  value={expectedLift}
                  onChange={(e) => {
                    setExpectedLift(parseFloat(e.target.value) || 0);
                    setPreset("Custom");
                  }}
                  className="w-full rounded-md bg-white/[0.05] px-2.5 py-1.5 text-white focus:bg-white/[0.10] focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Commercial Levers */}
          <div className="space-y-3 pt-2 text-xs font-mono">
            <div className="text-[10px] font-bold uppercase tracking-wider text-zinc-500 font-mono">
              Commercial Scale
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px]">
                <span className="text-zinc-400">Rev / Conv:</span>
                <span className="text-white font-bold">${revPerConv}</span>
              </div>
              <input
                type="range"
                min="1"
                max="250"
                step="5"
                value={revPerConv}
                onChange={(e) => setRevPerConv(parseFloat(e.target.value) || 0)}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px]">
                <span className="text-zinc-400">Sunk Cost:</span>
                <span className="text-white font-bold">${setupCost.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="0"
                max="15000"
                step="500"
                value={setupCost}
                onChange={(e) => setSetupCost(parseFloat(e.target.value) || 0)}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px]">
                <span className="text-zinc-400">Annual Traffic:</span>
                <span className="text-white font-bold">{(annualTraffic / 1000).toFixed(0)}k</span>
              </div>
              <input
                type="range"
                min="10000"
                max="1000000"
                step="50000"
                value={annualTraffic}
                onChange={(e) => setAnnualTraffic(parseInt(e.target.value, 10) || 0)}
                className="w-full h-1 cursor-pointer appearance-none rounded-lg bg-white/[0.12] accent-white"
              />
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-6">
          <button
            onClick={() => {
              onRunComputation();
              onClose();
            }}
            disabled={isComputing}
            className="w-full rounded-lg bg-white hover:bg-zinc-200 text-black py-2.5 text-xs font-mono font-semibold tracking-tight flex items-center justify-center gap-2 shadow-sm transition-all active:scale-[0.98] disabled:opacity-50"
          >
            <Play className="h-3.5 w-3.5 fill-black text-black" />
            <span>{isComputing ? "Recomputing..." : "Apply & Recalculate"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
