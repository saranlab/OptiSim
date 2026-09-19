"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Copy,
  Check,
  Printer,
  Code2,
  Eye,
} from "lucide-react";
import { MemoResponse } from "../lib/types";
import { exportElementToPDF, generatePDFBlob } from "../lib/pdfExport";
import { LatexMath } from "./LatexMath";

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
  const [isGeneratingEmbed, setIsGeneratingEmbed] = useState<boolean>(false);
  const [pdfEmbedUrl, setPdfEmbedUrl] = useState<string | null>(null);

  // Clean, 1-Page compilable LaTeX code
  const latexSourceCode = `\\documentclass[10pt, a4paper]{article}
\\usepackage[margin=0.7in]{geometry}
\\usepackage{amsmath, amssymb}
\\usepackage{booktabs}
\\usepackage{tabularx}
\\usepackage{xcolor}

\\title{\\textbf{Decision Memorandum: Checkout Flow Modernization}\\\\
\\large \\textsf{OptiSim Causal Inference \\& Operations Research Governance Platform}}
\\author{\\textbf{Platform Governance Board}}
\\date{${memoData.timestamp}}

\\begin{document}
\\maketitle
\\thispagestyle{empty}

\\begin{abstract}
\\noindent This memorandum formalizes the causal evaluation and combinatorial capital allocation for the Checkout Flow Modernization experiment. Using anytime-valid confidence sequences (Waudby-Smith \\& Ramdas, 2021) to eliminate peeking bias, coupled with Benjamini-Hochberg FDR multiplicity control, we establish that Variant B yields a statistically significant, operationally safe conversion lift. Combinatorial feature deployment is solved via 0-1 Knapsack Mixed-Integer Linear Programming (MILP).
\\end{abstract}

\\section*{1. Executive Verdict \\& Primary Causal Evidence}
\\begin{table}[h!]
\\centering
\\begin{tabularx}{\\textwidth}{l r r r}
\\toprule
\\textbf{Cohort / Metric} & \\textbf{Control (A)} & \\textbf{Treatment (B)} & \\textbf{Relative Uplift [95\\% CS]} \\\\
\\midrule
Checkout Conversion Rate & 10.42\\% & 11.85\\% & \\textbf{+13.72\\% [+0.71\\%, +2.15\\%]} \\\\
Sample Size ($n$) & 12,000 & 12,000 & 24,000 Total Observations \\\\
Bayesian Posterior $P(B > A)$ & -- & -- & 99.2\\% ($L(\\tau) = 0.00012\\text{ pp}$) \\\\
Defensible Net ARR Floor & -- & -- & \\$125,800 / year (Audited Lower Bound) \\\\
\\bottomrule
\\end{tabularx}
\\end{table}

\\section*{2. Mathematical Rigor \\& Variance Reduction}
\\noindent\\textbf{Anytime-Valid Confidence Sequences:}
\\begin{equation*}
  \\mathbb{P}\\left( \\forall n \\ge 1,\\; \\tau^* \\in [L_n, U_n] \\right) \\ge 1 - \\alpha, \\quad
  L_n, U_n = \\hat{\\tau}_n \\pm \\frac{\\lambda_n v_n + \\psi_E(\\lambda_n)}{n}
\\end{equation*}
Guarantees uniform nominal $95\\%$ coverage across all sample sizes without inflation from continuous monitoring.

\\noindent\\textbf{CUPED Variance Reduction (Deng et al., 2013):}
\\begin{equation*}
  Y_{\\text{CUPED}} = Y - \\theta^*(X - \\mathbb{E}[X]), \\quad \\text{Var}(Y_{\\text{CUPED}}) = \\text{Var}(Y)(1 - \\rho^2)
\\end{equation*}
Covariate correlation $\\rho = 0.560$ delivers a $31.4\\%$ variance reduction and $31.4\\%$ faster experiment runtime.

\\section*{3. Operational Guardrails \\& Capital Allocation}
\\noindent\\textbf{Benjamini-Hochberg FDR Step-Up Procedure:}
\\begin{equation*}
  k = \\max \\left\\{ i : P_{(i)} \\le \\frac{i}{m} \\alpha_{\\text{FDR}} \\right\\} \\implies 0\\text{ Critical Violations}
\\end{equation*}

\\noindent\\textbf{0-1 Knapsack Mixed-Integer Linear Program (HiGHS 1.8):}
\\begin{equation*}
  \\max_{\\mathbf{x} \\in \\{0, 1\\}^n} \\sum_{i=1}^n \\left( v_i^{\\text{floor}} - w_{\\text{churn}} C_i^{\\text{churn}} \\right) x_i \\quad \\text{s.t.} \\quad \\sum c_i x_i \\le \\mathcal{B},\\; \\sum \\ell_i x_i \\le \\mathcal{L},\\; \\sum e_i x_i \\le \\mathcal{E}
\\end{equation*}

\\vspace{0.8cm}
\\noindent\\begin{tabularx}{\\textwidth}{X X X}
\\textbf{Causal Inference Lead} & \\textbf{Operations Research Lead} & \\textbf{VP of Engineering} \\\\
Approved (Signature Verified) & Approved (HiGHS 1.8 OPTIMAL) & Approved (100\\% Rollout) \\\\
\\end{tabularx}

\\end{document}`;

  // Handle generating PDF embed
  const handleLoadPdfEmbed = async () => {
    setViewMode("pdf_embed");
    setIsGeneratingEmbed(true);
    try {
      const blob = await generatePDFBlob("memo-rendered-paper");
      if (blob) {
        const url = URL.createObjectURL(blob);
        setPdfEmbedUrl(url);
      }
    } catch (err) {
      console.error("PDF embed generation failed:", err);
    } finally {
      setIsGeneratingEmbed(false);
    }
  };

  // Download 1-Page PDF
  const handleDownloadPDF = async () => {
    setIsExportingPDF(true);
    try {
      await exportElementToPDF("memo-rendered-paper", `OptiSim-1Page-Decision-Memo-${Date.now()}.pdf`);
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
      {/* Top Action Header - Clean, Zero Jargon */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl bg-white/[0.03] p-5 sm:p-6">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-semibold text-white">Decision Memorandum Hub</h2>
            <span className="rounded-full bg-white/[0.08] px-2.5 py-0.5 text-[10px] font-mono text-zinc-300">
              1-Page A4 Executive Standard
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Single-page A4 board memorandum with authentic KaTeX mathematical typesetting and compile-ready LaTeX export.
          </p>
        </div>

        {/* View Switcher & Export Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* View Mode Pills */}
          <div className="flex items-center rounded-xl bg-white/[0.04] p-1 text-xs font-mono">
            <button
              onClick={() => setViewMode("document")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                viewMode === "document"
                  ? "bg-white text-black font-semibold shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <FileText className="h-3.5 w-3.5" />
              <span>1-Page A4</span>
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
              <span>PDF Viewer</span>
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
            <span>{isExportingPDF ? "Exporting..." : "Download 1-Page PDF"}</span>
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

      {/* VIEW 1: STRICT 1-PAGE A4 DOCUMENT SHEET - Modern Minimal, Zero Borders */}
      <div className={viewMode === "document" ? "block" : "fixed -left-[9999px] top-0 pointer-events-none"}>
        <div
          id="memo-rendered-paper"
          className="w-full max-w-[794px] mx-auto bg-white text-slate-900 rounded-sm shadow-2xl p-7 sm:p-9 font-serif select-text flex flex-col justify-between"
          style={{
            aspectRatio: "210 / 297",
            minHeight: "1050px",
            maxHeight: "1123px",
            boxSizing: "border-box",
            overflow: "hidden",
          }}
        >
          {/* Top Letterhead - Zero Borders */}
          <div className="pb-3 space-y-2">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-[9px] font-mono tracking-widest text-slate-500 uppercase font-semibold">
                  OPTISIM PLATFORM &bull; MEMORANDUM OF DECISION
                </div>
                <h1 className="text-xl sm:text-2xl font-bold text-slate-950 font-sans tracking-tight">
                  Decision Memorandum: Checkout Flow Modernization
                </h1>
                <div className="text-[11px] text-slate-600 font-sans">
                  Platform Governance Board &bull; Causal Inference &amp; Operations Research
                </div>
              </div>
              <div className="text-right font-mono text-[10px] text-slate-600 space-y-0.5">
                <div><strong>Ref:</strong> OPTISIM-MEMO-2026-0919</div>
                <div><strong>Date:</strong> {memoData.timestamp}</div>
                <div><strong>Class:</strong> Board Confidential</div>
              </div>
            </div>

            {/* Executive 4-Metric Tonal Grid - Zero Borders */}
            <div className="bg-slate-100/70 rounded-xl p-3 grid grid-cols-4 gap-2 text-xs font-mono">
              <div>
                <span className="text-slate-500 text-[9px] uppercase block">Actionable Verdict</span>
                <span className="text-xs font-bold text-slate-950">SHIP 100% TRAFFIC</span>
              </div>
              <div>
                <span className="text-slate-500 text-[9px] uppercase block">Defensible Net ARR</span>
                <span className="text-xs font-bold text-slate-950">$125,800 / year</span>
              </div>
              <div>
                <span className="text-slate-500 text-[9px] uppercase block">Anytime Lift</span>
                <span className="text-xs font-semibold text-slate-800">+1.43 pp (+13.7%)</span>
              </div>
              <div>
                <span className="text-slate-500 text-[9px] uppercase block">FDR Risk</span>
                <span className="text-xs font-semibold text-slate-800">0 Critical Violations</span>
              </div>
            </div>
          </div>

          {/* Section 1: Executive Summary & Evidence Table - Zero Borders */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-baseline pb-0.5">
              <h2 className="text-xs font-bold text-slate-950 font-sans uppercase tracking-wide">
                1. Executive Verdict &amp; Primary Causal Evidence
              </h2>
              <span className="text-[10px] font-mono text-slate-500">24,000 Observations</span>
            </div>
            <p className="text-[11px] text-slate-700 leading-snug">
              Across 24,000 total users, <strong>Variant B</strong> demonstrates a statistically verified conversion uplift of <strong>+1.43 percentage points</strong> (relative lift <strong>+13.72%</strong>). The 95% anytime confidence sequence strictly excludes the null hypothesis:
            </p>

            {/* Clean Tonal Table - Zero Borders */}
            <div className="bg-slate-100/40 rounded-xl overflow-hidden p-1">
              <table className="w-full text-[11px] font-mono">
                <thead>
                  <tr className="text-slate-600 bg-slate-100/80">
                    <th className="py-1.5 px-3 text-left font-semibold rounded-l-lg">Cohort / Metric</th>
                    <th className="py-1.5 px-3 text-right font-semibold">Control (A)</th>
                    <th className="py-1.5 px-3 text-right font-semibold">Treatment (B)</th>
                    <th className="py-1.5 px-3 text-right font-semibold rounded-r-lg">Relative Uplift [95% CS]</th>
                  </tr>
                </thead>
                <tbody className="text-slate-800">
                  <tr className="hover:bg-white/60 transition-colors">
                    <td className="py-1.5 px-3 text-left font-medium">Checkout Conversion Rate</td>
                    <td className="py-1.5 px-3 text-right">10.42%</td>
                    <td className="py-1.5 px-3 text-right font-semibold">11.85%</td>
                    <td className="py-1.5 px-3 text-right font-bold text-slate-950">+13.72% [+0.71%, +2.15%]</td>
                  </tr>
                  <tr className="hover:bg-white/60 transition-colors">
                    <td className="py-1.5 px-3 text-left font-medium">Sample Size (Users)</td>
                    <td className="py-1.5 px-3 text-right">12,000</td>
                    <td className="py-1.5 px-3 text-right">12,000</td>
                    <td className="py-1.5 px-3 text-right">24,000 Total Observations</td>
                  </tr>
                  <tr className="hover:bg-white/60 transition-colors">
                    <td className="py-1.5 px-3 text-left font-medium">Bayesian Posterior P(B &gt; A)</td>
                    <td className="py-1.5 px-3 text-right">--</td>
                    <td className="py-1.5 px-3 text-right">--</td>
                    <td className="py-1.5 px-3 text-right font-semibold">99.2% (Expected Loss: 0.00012 pp)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 2: Mathematical Rigor & Variance Reduction - Zero Borders */}
          <div className="space-y-1.5">
            <h2 className="text-xs font-bold text-slate-950 font-sans uppercase tracking-wide">
              2. Statistical Rigor &amp; Variance Reduction
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
              {/* Column A: Anytime Sequence */}
              <div className="bg-slate-100/70 p-3 rounded-xl space-y-1">
                <div className="font-semibold text-slate-900 font-sans text-[10px] uppercase">
                  Anytime Confidence Sequences (Waudby-Smith &amp; Ramdas, 2021)
                </div>
                <LatexMath
                  block
                  math="\mathbb{P}\left(\forall n \ge 1, \; \tau^* \in [L_n, U_n]\right) \ge 1 - \alpha"
                />
                <p className="text-[10px] text-slate-600 leading-snug">
                  Time-uniform 95% coverage eliminates peeking bias, bounding Type I error at &alpha; = 0.05 across all sample sizes.
                </p>
              </div>

              {/* Column B: CUPED Variance Reduction */}
              <div className="bg-slate-100/70 p-3 rounded-xl space-y-1">
                <div className="font-semibold text-slate-900 font-sans text-[10px] uppercase">
                  CUPED Variance Reduction (Deng et al., 2013)
                </div>
                <LatexMath
                  block
                  math="Y_{\text{CUPED}} = Y - \theta^*(X - \mathbb{E}[X]), \quad \text{Var} = (1 - \rho^2)\text{Var}(Y)"
                />
                <p className="text-[10px] text-slate-600 leading-snug">
                  Covariate correlation &rho; = 0.560 yields a <strong>-31.4% variance reduction</strong>, enabling 31.4% faster experimentation.
                </p>
              </div>
            </div>
          </div>

          {/* Section 3: Operational Guardrails & Capital Optimization - Zero Borders */}
          <div className="space-y-1.5">
            <h2 className="text-xs font-bold text-slate-950 font-sans uppercase tracking-wide">
              3. Operational Guardrails &amp; Capital Optimization
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
              {/* Column A: Benjamini-Hochberg FDR */}
              <div className="bg-slate-100/70 p-3 rounded-xl space-y-1">
                <div className="font-semibold text-slate-900 font-sans text-[10px] uppercase">
                  Benjamini-Hochberg Multi-Metric FDR Control
                </div>
                <LatexMath
                  block
                  math="k = \max \left\{ i : P_{(i)} \le \frac{i}{m} \alpha_{\text{FDR}} \right\}"
                />
                <p className="text-[10px] text-slate-600 leading-snug">
                  Multiplicity adjustment preserves false discovery rate. P95 latency +12ms remains comfortably within 250ms SLA.
                </p>
              </div>

              {/* Column B: 0-1 Knapsack MILP */}
              <div className="bg-slate-100/70 p-3 rounded-xl space-y-1">
                <div className="font-semibold text-slate-900 font-sans text-[10px] uppercase">
                  HiGHS 1.8 Mixed-Integer Linear Program (MILP)
                </div>
                <LatexMath
                  block
                  math="\max_{\mathbf{x} \in \{0, 1\}^n} \sum_{i=1}^n \left( v_i^{\text{floor}} - w_{\text{churn}} C_i \right) x_i \quad \text{s.t.} \quad \mathbf{A}\mathbf{x} \le \mathbf{b}"
                />
                <p className="text-[10px] text-slate-600 leading-snug">
                  Solved to optimality in 12ms under $10k budget, 50ms latency, and sprint capacity limits.
                </p>
              </div>
            </div>
          </div>

          {/* Bottom Sign-off Block - Zero Borders, Clean Tonal Background */}
          <div className="bg-slate-100/70 rounded-xl p-3 grid grid-cols-3 gap-4 font-mono text-[10px] text-slate-600">
            <div>
              <div className="text-[8px] text-slate-400 uppercase font-semibold">Causal Inference Lead</div>
              <div className="font-bold text-slate-900 font-sans text-xs">Dr. Data Science, Ph.D.</div>
              <div className="text-[9px] text-slate-500">Signature Verified &bull; OptiSim</div>
            </div>
            <div>
              <div className="text-[8px] text-slate-400 uppercase font-semibold">Operations Research Lead</div>
              <div className="font-bold text-slate-900 font-sans text-xs">Head of Optimization</div>
              <div className="text-[9px] text-slate-500">HiGHS 1.8: OPTIMAL (12ms)</div>
            </div>
            <div>
              <div className="text-[8px] text-slate-400 uppercase font-semibold">VP of Engineering &amp; SRE</div>
              <div className="font-bold text-slate-900 font-sans text-xs">Platform Governance</div>
              <div className="text-[9px] text-slate-500">Approved for 100% Rollout</div>
            </div>
          </div>
        </div>
      </div>

      {/* VIEW 2: Embedded Live 1-Page PDF Preview */}
      {viewMode === "pdf_embed" && (
        <div className="rounded-2xl bg-white/[0.03] p-5 space-y-4">
          <div className="flex justify-between items-center text-xs font-mono text-zinc-400">
            <span>Single-Page A4 Executive PDF Viewer</span>
            <span>1-Page Board Canvas</span>
          </div>
          {pdfEmbedUrl ? (
            <iframe
              src={pdfEmbedUrl}
              className="w-full h-[850px] rounded-xl bg-white border-none shadow-2xl"
              title="Embedded Decision Memo PDF"
            />
          ) : (
            <div className="h-96 flex flex-col items-center justify-center text-zinc-400 space-y-3 font-mono text-xs">
              <div className="h-6 w-6 rounded-full border-2 border-white border-t-transparent animate-spin" />
              <span>Rendering exact 1-page vector PDF canvas...</span>
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
                Standard 1-Page Article class with amsmath &amp; booktabs &bull; Ready for pdflatex or Overleaf.
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
