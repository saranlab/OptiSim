"use client";

import React, { useState } from "react";
import {
  FileText,
  Download,
  Copy,
  Check,
  Printer,
} from "lucide-react";
import { MemoResponse } from "../lib/types";
import { exportElementToPDF } from "../lib/pdfExport";

interface ExecutiveMemoHubProps {
  memoData: MemoResponse;
  onRegenerate: () => void;
}

export const ExecutiveMemoHub: React.FC<ExecutiveMemoHubProps> = ({
  memoData,
}) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isExportingPDF, setIsExportingPDF] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(memoData.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadMd = () => {
    const blob = new Blob([memoData.markdown], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `OptiSim-Decision-Memo-${Date.now()}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportPDF = async () => {
    setIsExportingPDF(true);
    try {
      await exportElementToPDF("executive-memo-document", `OptiSim-Executive-Board-Memo-${Date.now()}.pdf`);
    } catch (err) {
      console.error("PDF export failed:", err);
      window.print();
    } finally {
      setIsExportingPDF(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Responsive Action Header - Pure Monochrome, Zero Borders */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl bg-white/[0.03] p-5 sm:p-6">
        <div className="flex items-center space-x-3.5">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/[0.06] text-white">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm sm:text-base font-semibold text-white font-mono">
                Executive Decision Memo Hub
              </h3>
              <span className="rounded-full bg-white text-black px-2.5 py-0.5 text-[10px] sm:text-[11px] font-mono font-semibold uppercase tracking-wider">
                {memoData.executive_verdict}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5 font-mono">
              Causal &amp; OR Governance Brief for Investment Committee
            </p>
          </div>
        </div>

        {/* Action Buttons - Responsive Wrapping */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleExportPDF}
            disabled={isExportingPDF}
            className="flex items-center space-x-1.5 rounded-xl bg-white hover:bg-zinc-200 px-4 py-2 text-xs font-mono font-semibold text-black transition-all active:scale-[0.98] disabled:opacity-50 shadow-sm"
          >
            <Download className="h-3.5 w-3.5 text-black" />
            <span>{isExportingPDF ? "Generating PDF..." : "Export Board PDF"}</span>
          </button>

          <button
            onClick={() => window.print()}
            className="flex items-center space-x-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] px-3.5 py-2 text-xs font-mono text-zinc-200 transition-all active:scale-[0.98]"
          >
            <Printer className="h-3.5 w-3.5 text-zinc-400" />
            <span className="hidden sm:inline">Print Vector PDF</span>
            <span className="sm:hidden">Print</span>
          </button>

          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] px-3.5 py-2 text-xs font-mono text-zinc-200 transition-all active:scale-[0.98]"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-white" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>

          <button
            onClick={handleDownloadMd}
            className="flex items-center space-x-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] px-3.5 py-2 text-xs font-mono text-zinc-200 transition-all active:scale-[0.98]"
          >
            <Download className="h-3.5 w-3.5" />
            <span>.md</span>
          </button>
        </div>
      </div>

      {/* Printable Board Memo Surface - Responsive Paper Layout */}
      <div
        id="executive-memo-document"
        className="rounded-2xl bg-white/[0.03] p-6 sm:p-10 print-surface text-zinc-200"
      >
        {/* Memo Header Letterhead */}
        <div className="pb-8 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-3">
            <div>
              <div className="text-[11px] font-mono text-zinc-400 font-semibold uppercase tracking-wider">
                OPTISIM PLATFORM &bull; BOARD MEMORANDUM
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-1">
                Executive Decision Memo: Checkout Flow Modernization
              </h1>
            </div>
            <div className="sm:text-right font-mono text-xs text-zinc-500">
              <div>Ref: MEMO-2026-0919</div>
              <div>Classification: Strict Confidential</div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 pt-4 text-xs font-mono">
            <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
              <span className="text-zinc-500 text-[10px] block">Recommendation</span>
              <span className="text-sm font-semibold text-white">SHIP TO 100% TRAFFIC</span>
            </div>
            <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
              <span className="text-zinc-500 text-[10px] block">Defensible ARR Floor</span>
              <span className="text-sm font-semibold text-white">$125,800 / year</span>
            </div>
            <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
              <span className="text-zinc-500 text-[10px] block">Methodology</span>
              <span className="text-sm font-semibold text-zinc-300">Anytime Valid CS (95%)</span>
            </div>
            <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
              <span className="text-zinc-500 text-[10px] block">Guardrails Status</span>
              <span className="text-sm font-semibold text-white">0 Critical Violations</span>
            </div>
          </div>
        </div>

        {/* Formatted Memo Content */}
        <div className="pt-6 font-mono text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap bg-white/[0.02] p-4 sm:p-6 rounded-xl overflow-x-auto">
          {memoData.markdown}
        </div>

        {/* Institutional Sign-off Block */}
        <div className="pt-8 mt-6 grid grid-cols-1 sm:grid-cols-3 gap-6 font-mono text-xs text-zinc-400">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Principal Experimentation Lead</div>
            <div className="mt-1 font-semibold text-white">Data Science &amp; Causal Inference</div>
          </div>
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Head of Operations Research</div>
            <div className="mt-1 font-semibold text-white">Mathematical Programming &amp; MILP</div>
          </div>
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">VP of Engineering &amp; Product</div>
            <div className="mt-1 font-semibold text-white">Platform Governance &amp; SRE</div>
          </div>
        </div>
      </div>
    </div>
  );
};
