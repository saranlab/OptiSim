"use client";

import React from "react";
import {
  Activity,
  Cpu,
  FileText,
  Sliders,
  ShieldCheck,
  Download,
} from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isBackendConnected: boolean;
  onExportPDF: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isBackendConnected,
  onExportPDF,
}) => {
  const tabs = [
    { id: "inference", label: "Inference & Sequential CS", icon: Activity },
    { id: "hte_guardrails", label: "Subgroups & Guardrails", icon: ShieldCheck },
    { id: "or_knapsack", label: "0-1 Knapsack Lab", icon: Cpu },
    { id: "bandits", label: "Adaptive Routing", icon: Sliders },
    { id: "memo", label: "Executive Board Memo", icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#09090b]/95 backdrop-blur-xl">
      {/* Top Brand Bar - No Borders */}
      <div className="mx-auto flex max-w-[1550px] items-center justify-between px-8 py-3.5">
        {/* Brand */}
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            <span className="text-zinc-400">saranlab</span>
            <span className="text-zinc-600">/</span>
            <span className="font-semibold text-white tracking-tight">OptiSim</span>
          </div>

          <span className="rounded-full bg-white/[0.05] px-2.5 py-0.5 text-[10px] text-zinc-400 font-mono">
            checkout-flow-v2
          </span>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onExportPDF}
            className="flex items-center space-x-2 rounded-full bg-white/[0.06] hover:bg-white/[0.1] px-3.5 py-1.5 text-xs font-mono font-medium text-white transition-all active:scale-[0.98]"
          >
            <Download className="h-3.5 w-3.5 text-blue-400" />
            <span>Export Board Memo (PDF)</span>
          </button>

          <div className="flex items-center space-x-2 rounded-full bg-white/[0.03] px-3 py-1 text-[11px] font-mono text-zinc-400">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isBackendConnected ? "bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" : "bg-zinc-600"
              }`}
            />
            <span>{isBackendConnected ? "Engine Online" : "Local Mode"}</span>
          </div>
        </div>
      </div>

      {/* Modern Minimal Navigation Bar - Zero Borders */}
      <div className="mx-auto max-w-[1550px] px-8 pb-2">
        <nav className="flex space-x-1 overflow-x-auto scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 rounded-lg px-3.5 py-2 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-white/[0.08] text-white shadow-sm"
                    : "text-zinc-400 hover:text-white hover:bg-white/[0.03]"
                }`}
              >
                <Icon
                  className={`h-3.5 w-3.5 ${
                    isActive ? "text-blue-400" : "text-zinc-500"
                  }`}
                />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
