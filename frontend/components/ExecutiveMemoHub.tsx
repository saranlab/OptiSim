"use client";

import React, { useState } from "react";
import {
  FileText,
  Download,
  Copy,
  Check,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import { MemoResponse } from "../lib/types";

interface ExecutiveMemoHubProps {
  memoData: MemoResponse;
  onRegenerate: () => void;
}

export const ExecutiveMemoHub: React.FC<ExecutiveMemoHubProps> = ({
  memoData,
  onRegenerate,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(memoData.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([memoData.markdown], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `optisim-decision-memo-${Date.now()}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const isShip = memoData.executive_verdict.includes("SHIP");
  const isAbort = memoData.executive_verdict.includes("DO NOT SHIP");

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md border border-cyan-500/40 bg-cyan-950/40 text-cyan-400">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold tracking-tight text-white font-mono">
                Executive Decision Memo Hub
              </h3>
              <span
                className={`rounded px-2 py-0.5 text-[11px] font-mono font-bold uppercase tracking-wider ${
                  isShip
                    ? "bg-emerald-950/60 text-emerald-400 border border-emerald-500/40"
                    : isAbort
                    ? "bg-rose-950/60 text-rose-400 border border-rose-500/40"
                    : "bg-amber-950/60 text-amber-400 border border-amber-500/40"
                }`}
              >
                {memoData.executive_verdict}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 font-mono">
              Generated: {memoData.timestamp} | Causal & OR Governance Brief
            </p>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 rounded-md border border-slate-700 bg-slate-800 hover:bg-slate-700 px-3 py-1.5 text-xs font-mono font-medium text-slate-200 transition-all"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copied ? "Copied" : "Copy Markdown"}</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center space-x-1.5 rounded-md border border-cyan-500/40 bg-cyan-950/60 hover:bg-cyan-900/60 px-3 py-1.5 text-xs font-mono font-bold text-cyan-400 transition-all shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download .md</span>
          </button>
        </div>
      </div>

      {/* Memo Reader Document */}
      <div className="rounded-lg border border-slate-800 bg-slate-900/90 p-8 shadow-md">
        <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed font-sans">
          <pre className="p-6 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap leading-6">
            {memoData.markdown}
          </pre>
        </div>
      </div>
    </div>
  );
};
