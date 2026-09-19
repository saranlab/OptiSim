"use client";

import React from "react";
import {
  Activity,
  Cpu,
  FileText,
  Download,
  Settings2,
} from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  preset: string;
  onApplyPreset: (p: string) => void;
  onToggleDrawer: () => void;
  isBackendConnected: boolean;
  onExportPDF: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  preset,
  onApplyPreset,
  onToggleDrawer,
  isBackendConnected,
  onExportPDF,
}) => {
  const tabs = [
    { id: "causal_risk", label: "Causal Evidence & Risk", icon: Activity },
    { id: "allocation", label: "Capital & Routing Lab", icon: Cpu },
    { id: "memo", label: "Decision Memo", icon: FileText },
  ];

  const presets = ["E-Commerce", "B2B SaaS", "Media", "Custom"];

  return (
    <header className="sticky top-0 z-40 w-full bg-[#09090b]/95 backdrop-blur-xl">
      {/* Top Utility Bar - Zero Borders */}
      <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-3.5">
        {/* Brand & Context */}
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-white" />
            <span className="text-zinc-400">saranlab</span>
            <span className="text-zinc-600">/</span>
            <span className="font-semibold text-white tracking-tight">OptiSim</span>
          </div>
          <span className="rounded-full bg-white/[0.05] px-2.5 py-0.5 text-[10px] text-zinc-400 font-mono">
            v2.0
          </span>
        </div>

        {/* Center Archetype Presets - Tremor Filter Pills */}
        <div className="hidden md:flex items-center space-x-1 rounded-full bg-white/[0.04] p-1 text-xs font-mono">
          {presets.map((p) => {
            const isSelected = preset === p;
            return (
              <button
                key={p}
                onClick={() => onApplyPreset(p)}
                className={`px-3 py-1 rounded-full transition-all ${
                  isSelected
                    ? "bg-white text-black font-semibold shadow-sm"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                {p}
              </button>
            );
          })}
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleDrawer}
            className="flex items-center space-x-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.1] px-3.5 py-1.5 text-xs font-mono font-medium text-zinc-200 transition-all active:scale-[0.98]"
            title="Configure Experiment Levers"
          >
            <Settings2 className="h-3.5 w-3.5 text-zinc-400" />
            <span>Levers</span>
          </button>

          <button
            onClick={onExportPDF}
            className="flex items-center space-x-2 rounded-full bg-white text-black hover:bg-zinc-200 px-4 py-1.5 text-xs font-mono font-semibold transition-all active:scale-[0.98] shadow-sm"
          >
            <Download className="h-3.5 w-3.5 text-black" />
            <span>Export PDF</span>
          </button>

          <div className="hidden lg:flex items-center space-x-2 rounded-full bg-white/[0.03] px-3 py-1 text-[11px] font-mono text-zinc-400">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isBackendConnected ? "bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]" : "bg-zinc-600"
              }`}
            />
            <span>{isBackendConnected ? "Engine" : "Offline"}</span>
          </div>
        </div>
      </div>

      {/* Modern Minimal Navigation Bar - Zero Borders */}
      <div className="mx-auto max-w-7xl px-8 pb-3">
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
                    ? "bg-white/[0.10] text-white font-medium shadow-sm"
                    : "text-zinc-400 hover:text-white hover:bg-white/[0.03]"
                }`}
              >
                <Icon
                  className={`h-3.5 w-3.5 ${
                    isActive ? "text-white" : "text-zinc-500"
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
