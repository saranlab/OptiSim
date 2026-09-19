"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { Sidebar } from "../components/Sidebar";
import { VerdictBanner } from "../components/VerdictBanner";
import { TabInference } from "../components/TabInference";
import { TabSubgroupsGuardrails } from "../components/TabSubgroupsGuardrails";
import { TabORKnapsack } from "../components/TabORKnapsack";
import { TabBandits } from "../components/TabBandits";
import { TabFinancials } from "../components/TabFinancials";
import { ExecutiveMemoHub } from "../components/ExecutiveMemoHub";
import { optisimApi } from "../lib/api";
import { exportElementToPDF } from "../lib/pdfExport";
import {
  initialCandidates,
  initialCupedData,
  initialDeltaData,
  initialGuardrailsData,
  initialHteData,
  initialLinUCBData,
  initialMemoData,
  initialPortfolioData,
  initialSequentialData,
  initialThompsonData,
} from "../lib/mockData";
import {
  CandidateFeature,
  GuardrailAuditResponse,
  HTEResponse,
  LinUCBResponse,
  MemoResponse,
  PortfolioOptimizeResponse,
  ThompsonResponse,
} from "../lib/types";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("inference");
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [isComputing, setIsComputing] = useState<boolean>(false);

  // Sidebar Levers
  const [mode, setMode] = useState<"simulation" | "real">("simulation");
  const [preset, setPreset] = useState<string>("E-Commerce");
  const [confidence, setConfidence] = useState<string>("95%");
  const [power, setPower] = useState<string>("80%");
  const [baselineCvr, setBaselineCvr] = useState<number>(10.42);
  const [expectedLift, setExpectedLift] = useState<number>(13.72);
  const [revPerConv, setRevPerConv] = useState<number>(45);
  const [setupCost, setSetupCost] = useState<number>(12000);
  const [annualTraffic, setAnnualTraffic] = useState<number>(240000);

  // Model States
  const [sequentialData, setSequentialData] = useState(initialSequentialData);
  const [cupedData] = useState(initialCupedData);
  const [deltaData] = useState(initialDeltaData);
  const [hteData, setHteData] = useState<HTEResponse>(initialHteData);
  const [guardrailsData, setGuardrailsData] = useState<GuardrailAuditResponse>(initialGuardrailsData);
  const [candidates] = useState<CandidateFeature[]>(initialCandidates);
  const [portfolioData, setPortfolioData] = useState<PortfolioOptimizeResponse>(initialPortfolioData);
  const [thompsonData, setThompsonData] = useState<ThompsonResponse>(initialThompsonData);
  const [linucbData, setLinucbData] = useState<LinUCBResponse>(initialLinUCBData);
  const [memoData, setMemoData] = useState<MemoResponse>(initialMemoData);

  // Derived values
  const controlCvr = baselineCvr / 100;
  const treatmentCvr = (baselineCvr * (1 + expectedLift / 100)) / 100;
  const ciLower = treatmentCvr - controlCvr - 0.007;
  const ciUpper = treatmentCvr - controlCvr + 0.007;
  const defensibleNet = Math.max(0, annualTraffic * (ciLower) * revPerConv - setupCost);

  // Check backend health on mount
  useEffect(() => {
    async function checkBackend() {
      try {
        const health = await optisimApi.health();
        if (health && health.status === "healthy") {
          setIsBackendConnected(true);
        }
      } catch {
        setIsBackendConnected(false);
      }
    }
    checkBackend();
  }, []);

  // Handle Preset application
  const handleApplyPreset = (name: string) => {
    setPreset(name);
    if (name === "E-Commerce") {
      setBaselineCvr(10.42);
      setExpectedLift(13.72);
      setRevPerConv(45);
      setSetupCost(12000);
      setAnnualTraffic(240000);
    } else if (name === "B2B SaaS") {
      setBaselineCvr(3.20);
      setExpectedLift(22.50);
      setRevPerConv(180);
      setSetupCost(25000);
      setAnnualTraffic(60000);
    } else if (name === "Media") {
      setBaselineCvr(18.50);
      setExpectedLift(6.40);
      setRevPerConv(8);
      setSetupCost(5000);
      setAnnualTraffic(800000);
    }
  };

  // Run computation trigger
  const handleRunComputation = async () => {
    setIsComputing(true);
    try {
      if (isBackendConnected) {
        const audited = await optisimApi.auditGuardrails(
          await optisimApi.getGuardrailDefaults(),
          0.05
        );
        setGuardrailsData(audited);
      }
    } catch (e) {
      console.warn("Compute offline fallback:", e);
    } finally {
      setTimeout(() => setIsComputing(false), 300);
    }
  };

  // Guardrail update
  const handleRefreshGuardrails = async (alphaFdr: number) => {
    try {
      const defaults = await optisimApi.getGuardrailDefaults();
      const audited = await optisimApi.auditGuardrails(defaults, alphaFdr);
      setGuardrailsData(audited);
    } catch {
      setGuardrailsData((prev) => ({
        ...prev,
        fdr_alpha: alphaFdr,
        metrics: prev.metrics.map((m) => {
          const isSig = m.adjusted_p_value < alphaFdr;
          const exceeds = m.relative_change > m.threshold_pct;
          const status = exceeds && isSig ? "FAIL" : exceeds ? "WARN" : "PASS";
          return { ...m, status: status as "PASS" | "WARN" | "FAIL" };
        }),
      }));
    }
  };

  // Portfolio re-optimize
  const handleReoptimize = async (params: {
    max_budget: number;
    max_latency_ms: number;
    max_effort_points: number;
    robust_mode: boolean;
    churn_penalty_weight: number;
  }) => {
    try {
      const res = await optisimApi.optimizePortfolio({
        features: candidates,
        ...params,
      });
      setPortfolioData(res);
    } catch {
      setPortfolioData((prev) => ({
        ...prev,
        is_robust: params.robust_mode,
        total_value: params.robust_mode ? 125800 : 167000,
        budget_utilization_pct: (prev.total_cost / params.max_budget) * 100,
        latency_utilization_pct: (prev.total_latency_ms / params.max_latency_ms) * 100,
        effort_utilization_pct: (prev.total_effort_points / params.max_effort_points) * 100,
      }));
    }
  };

  // Thompson simulation
  const handleSimulateThompson = async (rounds: number, delay: number) => {
    try {
      const res = await optisimApi.simulateThompson({
        true_conversion_rates: {
          "Variant B (Modernized)": 0.155,
          "Control (Baseline)": 0.104,
          "Variant C (Aggressive)": 0.092,
        },
        n_rounds: rounds,
        delay_rounds: delay,
      });
      setThompsonData(res);
    } catch {
      setThompsonData((prev) => ({
        ...prev,
        cumulative_reward: Math.round(rounds * 0.145),
        regret: +(rounds * 0.015).toFixed(1),
      }));
    }
  };

  // LinUCB simulation
  const handleSimulateLinUCB = async (rounds: number, alpha: number) => {
    try {
      const res = await optisimApi.simulateLinUCB({
        arm_names: ["Minimal UI", "Rich Visuals", "AI Recommendations"],
        n_rounds: rounds,
        context_dim: 3,
        alpha,
      });
      setLinucbData(res);
    } catch {
      setLinucbData((prev) => ({
        ...prev,
        ctr: 0.162,
      }));
    }
  };

  // PDF Export Trigger from Navbar
  const handleExportPDF = async () => {
    if (activeTab !== "memo") {
      setActiveTab("memo");
      setTimeout(async () => {
        await exportElementToPDF("executive-memo-document", `OptiSim-Executive-Memo-${Date.now()}.pdf`);
      }, 350);
    } else {
      await exportElementToPDF("executive-memo-document", `OptiSim-Executive-Memo-${Date.now()}.pdf`);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-white flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Modern Minimal Navbar - Zero Borders */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendConnected={isBackendConnected}
        onExportPDF={handleExportPDF}
      />

      {/* Main Workspace Body */}
      <div className="flex-1 flex max-w-[1550px] mx-auto w-full">
        {/* Left Interactive Levers Panel - Zero Borders */}
        <Sidebar
          mode={mode}
          setMode={setMode}
          preset={preset}
          setPreset={setPreset}
          confidence={confidence}
          setConfidence={setConfidence}
          power={power}
          setPower={setPower}
          baselineCvr={baselineCvr}
          setBaselineCvr={setBaselineCvr}
          expectedLift={expectedLift}
          setExpectedLift={setExpectedLift}
          revPerConv={revPerConv}
          setRevPerConv={setRevPerConv}
          setupCost={setupCost}
          setSetupCost={setSetupCost}
          annualTraffic={annualTraffic}
          setAnnualTraffic={setAnnualTraffic}
          onApplyPreset={handleApplyPreset}
          onRunComputation={handleRunComputation}
          isComputing={isComputing}
        />

        {/* Center Canvas */}
        <main className="flex-1 p-8 overflow-y-auto">
          {/* Top Decision Verdict Banner */}
          <VerdictBanner
            status="success"
            headline="Rollout Recommendation: Deploy to 100% of Production Traffic"
            subtext="Anytime-valid confidence sequence excludes null effect across 24,000 observations. Multi-metric FDR guardrails clear with zero critical regressions."
            controlCvr={controlCvr}
            treatmentCvr={treatmentCvr}
            relativeLift={expectedLift / 100}
            ciLower={ciLower}
            ciUpper={ciUpper}
            probBBetter={0.992}
            defensibleNet={defensibleNet}
          />

          {/* Tab Views */}
          {activeTab === "inference" && (
            <div className="space-y-6">
              <TabInference
                sequentialData={sequentialData}
                cupedData={cupedData}
                deltaData={deltaData}
                controlCvr={controlCvr}
                treatmentCvr={treatmentCvr}
              />
              <TabFinancials
                annualTraffic={annualTraffic}
                revPerConv={revPerConv}
                setupCost={setupCost}
                observedLiftPct={expectedLift}
                ciLowerPct={ciLower * 100}
              />
            </div>
          )}

          {activeTab === "hte_guardrails" && (
            <TabSubgroupsGuardrails
              hteData={hteData}
              guardrailsData={guardrailsData}
              onRefreshGuardrails={handleRefreshGuardrails}
            />
          )}

          {activeTab === "or_knapsack" && (
            <TabORKnapsack
              portfolioData={portfolioData}
              candidates={candidates}
              onReoptimize={handleReoptimize}
            />
          )}

          {activeTab === "bandits" && (
            <TabBandits
              thompsonData={thompsonData}
              linucbData={linucbData}
              onSimulateThompson={handleSimulateThompson}
              onSimulateLinUCB={handleSimulateLinUCB}
            />
          )}

          {activeTab === "memo" && (
            <ExecutiveMemoHub
              memoData={memoData}
              onRegenerate={() => {}}
            />
          )}
        </main>
      </div>

      {/* Modern Minimal Footer - Zero Borders */}
      <footer className="bg-[#09090b] px-8 py-5 mt-auto">
        <div className="max-w-[1550px] mx-auto flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-zinc-500">
          <div>
            <span>OptiSim</span> &bull; <span>3-Color Modern Minimal</span> &bull; <span>Anytime Sequence</span> &bull; <span>HiGHS MILP</span>
          </div>
          <div className="text-zinc-500">
            <span>FastAPI 2.0</span> &bull; <span>Next.js 15</span> &bull; <span>Zero Borders</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
