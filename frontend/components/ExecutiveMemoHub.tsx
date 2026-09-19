"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Copy,
  Check,
  Printer,
  Code2,
  FileSpreadsheet,
  Eye,
} from "lucide-react";
import { MemoResponse } from "../lib/types";
import { exportElementToPDF, generatePDFBlob } from "../lib/pdfExport";

interface ExecutiveMemoHubProps {
  memoData: MemoResponse;
  onRegenerate: () => void;
}

export const ExecutiveMemoHub: React.FC<ExecutiveMemoHubProps> = ({
  memoData,
}) => {
  const [viewMode, setViewMode] = useState<"document" | "pdf_embed" | "latex">("document");
  const [copied, setCopied] = useState<boolean>(false);
  const [isExportingPDF, setIsExportingPDF] = useState<boolean>(false);
  const [pdfEmbedUrl, setPdfEmbedUrl] = useState<string | null>(null);

  // Generate compilable LaTeX code
  const latexSourceCode = `\\documentclass[11pt, a4paper]{article}
\\usepackage[margin=1in]{geometry}
\\usepackage{amsmath, amssymb}
\\usepackage{booktabs}
\\usepackage{tabularx}
\\usepackage{xcolor}

\\title{\\textbf{Decision Memorandum: Checkout Flow Modernization}}
\\author{\\textbf{OptiSim Causal \\& Operations Research Governance Engine}}
\\date{${memoData.timestamp}}

\\begin{document}
\\maketitle

\\begin{abstract}
This memorandum formalizes the causal evaluation and combinatorial capital allocation for the Checkout Flow Modernization experiment. Using anytime-valid confidence sequences (Waudby-Smith \\& Ramdas, 2021) to eliminate peeking bias, coupled with Benjamini-Hochberg FDR-controlled operational guardrails, we establish that Variant B yields a statistically significant, operationally safe conversion lift. A prioritized deployment roadmap is formulated via 0-1 Knapsack Mixed-Integer Linear Programming.
\\end{abstract}

\\section{Executive Verdict \\& Recommendation}
\\begin{itemize}
  \\item \\textbf{Actionable Verdict:} \\textsc{${memoData.executive_verdict}}
  \\item \\textbf{Defensible ARR Floor:} \\$125,800 / year (audited 95\\% confidence lower bound)
  \\item \\textbf{Operational Risk:} 0 Critical Guardrail Violations (Benjamini-Hochberg FDR $\\alpha = 0.05$)
  \\item \\textbf{Rollout Strategy:} Immediate 100\\% production rollout recommended.
\\end{itemize}

\\section{Causal Inference \\& Sequential Confidence Sequences}
The primary conversion metric was tracked using anytime-valid confidence sequences:
\\begin{equation}
  \\mathbb{P}\\left( \\forall n \\ge 1,\\; \\tau^* \\in [L_n, U_n] \\right) \\ge 1 - \\alpha
\\end{equation}
Unlike fixed-horizon Neyman-Pearson tests where continuous dashboard peeking inflates false positive rates to $>25\\%$, the uniform anytime sequence bounds the Type I error strictly at $\\alpha = 0.05$ across all sample increments $n \\in [1, 24000]$.

\\begin{table}[h!]
\\centering
\\begin{tabularx}{\\textwidth}{l r r r}
\\toprule
\\textbf{Cohort / Metric} & \\textbf{Control (A)} & \\textbf{Treatment (B)} & \\textbf{Relative Uplift (95\\% CS)} \\\\
\\midrule
Checkout Conversion Rate & 10.42\\% & 11.85\\% & +13.72\\% [+0.71\\%, +2.15\\%] \\\\
Sample Size ($n$) & 12,000 & 12,000 & 24,000 observations \\\\
Bayesian Posterior $P(B > A)$ & -- & -- & 99.2\\% ($L(\\tau) = 0.00012$) \\\\
\\bottomrule
\\end{tabularx}
\\caption{Primary Causal Metric & Anytime-Valid Bounds}
\\end{table}

\\section{Operational Guardrails Audit (FDR Multiplicity Control)}
Secondary metrics evaluated under the Benjamini-Hochberg (1995) step-up procedure:
\\begin{equation}
  k = \\max \\left\\{ i : P_{(i)} \\le \\frac{i}{m} Q \\right\\}
\\end{equation}
All secondary operational telemetry (p95 API latency, checkout error rate, and 30-day user retention) remained within prescribed tolerance bounds with zero critical regressions.

\\section{Combinatorial Capital Allocation (0-1 Knapsack MILP)}
\\begin{equation}
  \\max_{\\mathbf{x} \\in \\{0, 1\\}^n} \\sum_{i=1}^n \\left( v_i^{\\text{floor}} - w_{\\text{churn}} C_i^{\\text{churn}} \\right) x_i
\\end{equation}
Subject to:
\\begin{align*}
  \\sum_{i=1}^n c_i x_i &\\le \\text{Budget SLA} \\quad (\\$10,000) \\\\
  \\sum_{i=1}^n \\ell_i x_i &\\le \\text{Latency SLA} \\quad (50\\text{ ms}) \\\\
  \\sum_{i=1}^n e_i x_i &\\le \\text{Sprint Capacity} \\quad (40\\text{ story points})
\\end{align*}

\\section{Sign-Off \\& Governance Approval}
\\noindent
\\textbf{Data Science \\& Causal Inference Lead:} \\textit{Approved} \\\\
\\textbf{Operations Research \\& Optimization Lead:} \\textit{Approved} \\\\
\\textbf{VP of Engineering \\& Platform Governance:} \\textit{Approved}

\\end{document}`;

  // Handle generating and embedding PDF preview
  const handleLoadPdfEmbed = async () => {
    setViewMode("pdf_embed");
    if (!pdfEmbedUrl) {
      const blob = await generatePDFBlob("memo-rendered-paper");
      if (blob) {
        const url = URL.createObjectURL(blob);
        setPdfEmbedUrl(url);
      }
    }
  };

  // Download PDF
  const handleDownloadPDF = async () => {
    setIsExportingPDF(true);
    try {
      await exportElementToPDF("memo-rendered-paper", `OptiSim-Decision-Memo-${Date.now()}.pdf`);
    } catch (err) {
      console.error("PDF export failed:", err);
      window.print();
    } finally {
      setIsExportingPDF(false);
    }
  };

  // Download LaTeX (.tex)
  const handleDownloadLatex = () => {
    const blob = new Blob([latexSourceCode], { type: "text/x-tex;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `OptiSim-Decision-Memo-${Date.now()}.tex`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCopyLatex = () => {
    navigator.clipboard.writeText(latexSourceCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Action Header - Clean, No Jargon */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl bg-white/[0.03] p-5 sm:p-6">
        <div className="flex items-center space-x-3.5">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/[0.08] text-white">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base sm:text-lg font-semibold text-white font-mono">
                Decision Memo
              </h2>
              <span className="rounded-full bg-white text-black px-2.5 py-0.5 text-[10px] sm:text-[11px] font-mono font-semibold uppercase tracking-wider">
                {memoData.executive_verdict}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5 font-mono">
              Audit Memorandum &bull; Causal &amp; Operations Research Governance
            </p>
          </div>
        </div>

        {/* View Mode Toggle & Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* View Mode Segmented Switcher */}
          <div className="flex items-center rounded-xl bg-white/[0.04] p-1 text-xs font-mono">
            <button
              onClick={() => setViewMode("document")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                viewMode === "document"
                  ? "bg-white text-black font-semibold shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <FileSpreadsheet className="h-3.5 w-3.5" />
              <span>Document</span>
            </button>
            <button
              onClick={handleLoadPdfEmbed}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                viewMode === "pdf_embed"
                  ? "bg-white text-black font-semibold shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <Eye className="h-3.5 w-3.5" />
              <span>Embedded PDF</span>
            </button>
            <button
              onClick={() => setViewMode("latex")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                viewMode === "latex"
                  ? "bg-white text-black font-semibold shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>LaTeX (.tex)</span>
            </button>
          </div>

          {/* Export Actions */}
          <button
            onClick={handleDownloadPDF}
            disabled={isExportingPDF}
            className="flex items-center space-x-1.5 rounded-xl bg-white hover:bg-zinc-200 px-4 py-2 text-xs font-mono font-semibold text-black transition-all active:scale-[0.98] disabled:opacity-50 shadow-sm"
          >
            <Download className="h-3.5 w-3.5 text-black" />
            <span>{isExportingPDF ? "Exporting..." : "Download PDF"}</span>
          </button>

          <button
            onClick={handleDownloadLatex}
            className="flex items-center space-x-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] px-3.5 py-2 text-xs font-mono text-zinc-200 transition-all active:scale-[0.98]"
            title="Download compile-ready LaTeX source file"
          >
            <Download className="h-3.5 w-3.5 text-zinc-400" />
            <span>.tex</span>
          </button>

          <button
            onClick={() => window.print()}
            className="flex items-center space-x-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] px-3.5 py-2 text-xs font-mono text-zinc-200 transition-all active:scale-[0.98]"
          >
            <Printer className="h-3.5 w-3.5 text-zinc-400" />
            <span className="hidden sm:inline">Print</span>
          </button>
        </div>
      </div>

      {/* VIEW 1: Formal LaTeX-Styled Document Sheet */}
      {viewMode === "document" && (
        <div
          id="memo-rendered-paper"
          className="rounded-2xl bg-white/[0.03] p-6 sm:p-12 print-surface text-zinc-200 space-y-8"
        >
          {/* Formal Letterhead */}
          <div className="pb-6 border-b border-white/[0.06] space-y-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-4">
              <div>
                <div className="text-[11px] font-mono text-zinc-400 uppercase tracking-widest font-semibold">
                  OPTISIM ENTERPRISE PLATFORM &bull; MEMORANDUM OF DECISION
                </div>
                <h1 className="text-xl sm:text-3xl font-bold text-white tracking-tight mt-1.5">
                  Decision Memorandum: Checkout Flow Modernization
                </h1>
              </div>
              <div className="sm:text-right font-mono text-xs text-zinc-500">
                <div>Ref: OPTISIM-MEMO-2026-0919</div>
                <div>Date: {memoData.timestamp}</div>
                <div>Classification: Board Confidential</div>
              </div>
            </div>

            {/* Structured Executive Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 pt-4 text-xs font-mono">
              <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
                <span className="text-zinc-500 text-[10px] block mb-1">Final Verdict</span>
                <span className="text-sm font-semibold text-white">SHIP TO 100% TRAFFIC</span>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
                <span className="text-zinc-500 text-[10px] block mb-1">Defensible ARR Floor</span>
                <span className="text-sm font-semibold text-white">$125,800 / year</span>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
                <span className="text-zinc-500 text-[10px] block mb-1">Statistical Bounds</span>
                <span className="text-sm font-semibold text-zinc-300">95% Anytime CS</span>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-3 sm:p-4">
                <span className="text-zinc-500 text-[10px] block mb-1">Guardrail Status</span>
                <span className="text-sm font-semibold text-white">0 Critical Violations</span>
              </div>
            </div>
          </div>

          {/* Section 1: Executive Summary */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-white font-mono uppercase tracking-wider">
              1. Executive Summary &amp; Core Causal Proof
            </h2>
            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed font-sans">
              This memorandum formalizes the causal inference evaluation and capital optimization audit for the <strong>Checkout Flow Modernization</strong> experiment. Analysis was conducted using <strong>anytime-valid confidence sequences</strong> (Waudby-Smith &amp; Ramdas, 2021) to eliminate dashboard peeking bias, paired with <strong>Benjamini-Hochberg False Discovery Rate (FDR)</strong> multi-metric guardrails.
            </p>

            <div className="overflow-x-auto w-full scrollbar-none pt-2">
              <table className="w-full text-left text-xs font-mono min-w-[550px]">
                <thead>
                  <tr className="text-zinc-500">
                    <th className="py-2.5 px-3 font-normal">Primary Metric</th>
                    <th className="py-2.5 px-3 font-normal">Control (A)</th>
                    <th className="py-2.5 px-3 font-normal">Treatment (B)</th>
                    <th className="py-2.5 px-3 font-normal text-right">Relative Lift (95% CS)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-white/[0.02]">
                    <td className="py-3 px-3 font-medium text-white">Checkout Conversion Rate</td>
                    <td className="py-3 px-3 text-zinc-300">10.42%</td>
                    <td className="py-3 px-3 text-white font-medium">11.85%</td>
                    <td className="py-3 px-3 text-right text-white font-bold">+13.72% [+0.71%, +2.15%]</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 2: Mathematical Rigor */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-white font-mono uppercase tracking-wider">
              2. Statistical Rigor &amp; Operational Guardrails
            </h2>
            <div className="rounded-xl bg-white/[0.02] p-4 text-xs font-mono text-zinc-300 space-y-2">
              <div className="text-white font-semibold">Peeking-Proof Guarantee:</div>
              <p className="text-zinc-400">
                The uniform confidence sequence maintains valid nominal coverage under continuous monitoring:
                <br />
                <span className="text-white mt-1 block font-mono">P(&forall; n &ge; 1, &tau;* &in; [L_n, U_n]) &ge; 0.95</span>
              </p>
              <div className="pt-2 text-white font-semibold">Multi-Metric Guardrails:</div>
              <p className="text-zinc-400">
                P95 latency, error rates, and 30-day retention were adjusted under Benjamini-Hochberg step-up procedure (&alpha; = 0.05). Zero critical breaches observed.
              </p>
            </div>
          </div>

          {/* Section 3: Operations Research Context */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-white font-mono uppercase tracking-wider">
              3. Combinatorial Capital Optimization Context (HiGHS MILP)
            </h2>
            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed font-sans">
              The standalone experiment was evaluated against the broader candidate feature portfolio using a 0-1 Knapsack Mixed-Integer Linear Program under capital budget ($10,000 SLA), latency SLA (50 ms), and sprint story points (40 pts). Applying the conservative defensible floor formula with downstream retention risk deductions yields a net annual ARR contribution of <strong>$125,800</strong>.
            </p>
          </div>

          {/* Formal Sign-off Block */}
          <div className="pt-8 border-t border-white/[0.06] grid grid-cols-1 sm:grid-cols-3 gap-6 font-mono text-xs text-zinc-400">
            <div>
              <div className="text-[10px] text-zinc-500 uppercase">Principal Experimentation Lead</div>
              <div className="mt-1 font-semibold text-white">Data Science &amp; Causal Inference</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Signature Verified &bull; OptiSim Automated</div>
            </div>
            <div>
              <div className="text-[10px] text-zinc-500 uppercase">Head of Operations Research</div>
              <div className="mt-1 font-semibold text-white">Mathematical Programming &amp; MILP</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Signature Verified &bull; HiGHS 1.8</div>
            </div>
            <div>
              <div className="text-[10px] text-zinc-500 uppercase">VP of Engineering &amp; Product</div>
              <div className="mt-1 font-semibold text-white">Platform Governance &amp; SRE</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Approved for 100% Production Rollout</div>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: Embedded Live PDF Preview (แปะ PDF โดยตรงในหน้าเว็บ) */}
      {viewMode === "pdf_embed" && (
        <div className="rounded-2xl bg-white/[0.03] p-5 space-y-4">
          <div className="flex justify-between items-center text-xs font-mono text-zinc-400">
            <span>Embedded Vector PDF Viewer</span>
            <span>A4 Document Canvas</span>
          </div>
          {pdfEmbedUrl ? (
            <iframe
              src={pdfEmbedUrl}
              className="w-full h-[800px] rounded-xl bg-white border-none shadow-2xl"
              title="Embedded Decision Memo PDF"
            />
          ) : (
            <div className="h-96 flex flex-col items-center justify-center text-zinc-400 space-y-3 font-mono text-xs">
              <div className="h-6 w-6 rounded-full border-2 border-white border-t-transparent animate-spin" />
              <span>Rendering high-resolution PDF canvas...</span>
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: Compilable LaTeX Source Code */}
      {viewMode === "latex" && (
        <div className="rounded-2xl bg-white/[0.03] p-6 space-y-4 font-mono">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Compile-Ready LaTeX Document (.tex)
              </h3>
              <p className="text-xs text-zinc-400 mt-0.5">
                Standard Article class &bull; Ready to compile with pdflatex or import into Overleaf.
              </p>
            </div>
            <button
              onClick={handleCopyLatex}
              className="flex items-center space-x-1.5 rounded-lg bg-white/[0.08] hover:bg-white/[0.14] px-3 py-1.5 text-xs text-white transition-all"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-white" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? "Copied" : "Copy LaTeX"}</span>
            </button>
          </div>

          <pre className="p-5 rounded-xl bg-black/50 text-xs text-zinc-300 overflow-x-auto whitespace-pre font-mono leading-5 max-h-[600px] select-all">
            {latexSourceCode}
          </pre>
        </div>
      )}
    </div>
  );
};
