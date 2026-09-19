"use client";

import React from "react";
import { Activity, Cpu, Layers, FileText, BarChart3, Sliders, ShieldCheck } from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isBackendConnected: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isBackendConnected,
}) => {
  const navItems = [
    {
      id: "experiment",
      label: "Experiment Studio",
      icon: Activity,
      badge: "Causal & Sequential",
    },
    {
      id: "portfolio",
      label: "OR Knapsack Lab",
      icon: Cpu,
      badge: "MILP HiGHS",
    },
    {
      id: "bandits",
      label: "Adaptive Personalization",
      icon: Sliders,
      badge: "Thompson / LinUCB",
    },
    {
      id: "memo",
      label: "Executive Memo Hub",
      icon: FileText,
      badge: "Governance Brief",
    },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/90 backdrop-blur-md px-6 py-3.5">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center space-x-3.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md border border-cyan-500/40 bg-cyan-950/40 text-cyan-400 shadow-sm shadow-cyan-900/30">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-base font-bold tracking-tight text-white">
                OptiSim
              </span>
              <span className="rounded border border-slate-700 bg-slate-900 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                v2.0 Enterprise
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Causal Inference & Operations Research Optimization
            </p>
          </div>
        </div>

        {/* Primary View Switcher */}
        <nav className="flex items-center space-x-1 rounded-lg border border-slate-800 bg-slate-900/90 p-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 rounded-md px-3.5 py-1.5 text-xs font-semibold transition-all ${
                  isActive
                    ? "border border-cyan-500/30 bg-slate-800 text-white shadow-sm"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-cyan-400" : "text-slate-500"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Engine status indicator */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 rounded-md border border-slate-800 bg-slate-900/80 px-2.5 py-1 text-xs">
            <span
              className={`h-2 w-2 rounded-full ${
                isBackendConnected
                  ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)] animate-pulse"
                  : "bg-amber-400"
              }`}
            />
            <span className="font-mono text-[11px] text-slate-300">
              {isBackendConnected ? "REST Engine Online" : "Demo Mode (Mock)"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
