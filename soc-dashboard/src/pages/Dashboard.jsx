import { useState } from "react";
import LogInputForm from "../components/LogInputForm";
import AlertCard from "../components/AlertCard";
import SequenceAlertCard from "../components/SequenceAlertCard";
import DataOverviewPage from "../components/DataOverviewPage";
import { evaluateSingleLog, evaluateSequenceLogs } from "../services/api";
import { Shield, Layers, Activity, BarChart2, Terminal } from "lucide-react";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("analysis"); // 'analysis' or 'overview'
  const [mode, setMode] = useState("single"); // 'single' or 'sequence'
  const [singleResult, setSingleResult] = useState(null);
  const [sequenceResult, setSequenceResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogSubmission = async (parsedData) => {
    setIsLoading(true);
    try {
      if (mode === "single") {
        const response = await evaluateSingleLog(parsedData);
        setSingleResult(response);
      } else {
        const response = await evaluateSequenceLogs(parsedData);
        setSequenceResult(response);
      }
    } catch (error) {
      console.error("API Error:", error);
      alert(
        "Failed to evaluate log payload. Check console and API connection.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Permanent Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between hidden md:flex">
        <div>
          {/* Sidebar Header */}
          <div className="p-6 border-b border-slate-800 flex items-center gap-3">
            <Activity className="text-blue-500" size={28} />
            <div>
              <h1 className="font-bold text-white text-base">SOC Engine</h1>
              <p className="text-xs text-slate-400">AI Threat Sentinel</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-2">
            <button
              onClick={() => setActiveTab("analysis")}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                activeTab === "analysis"
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <Terminal size={18} /> Threat Analysis
            </button>

            <button
              onClick={() => setActiveTab("overview")}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                activeTab === "overview"
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <BarChart2 size={18} /> Data Overview
            </button>
          </nav>
        </div>

        {/* Sidebar Footer info */}
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
          Engine Status:{" "}
          <span className="text-emerald-400 font-semibold">Active</span>
        </div>
      </aside>

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-h-screen overflow-y-auto">
        {/* Top Header bar for mobile or quick mode shifts */}
        <header className="bg-slate-900/50 backdrop-blur border-b border-slate-800 px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3 md:hidden">
            <Activity className="text-blue-500" size={24} />
            <span className="font-bold text-white">
              SOC Intelligence Engine
            </span>
          </div>

          <div className="text-sm font-medium text-slate-400 capitalize">
            Current View:{" "}
            <span className="text-white">
              {activeTab === "analysis"
                ? "Threat Analysis Console"
                : "Data Distribution Overview"}
            </span>
          </div>

          {/* If on Analysis tab, show mode switcher in header */}
          {activeTab === "analysis" && (
            <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => setMode("single")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  mode === "single"
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Shield size={14} /> Single Event
              </button>
              <button
                onClick={() => setMode("sequence")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  mode === "sequence"
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Layers size={14} /> Sequence
              </button>
            </div>
          )}
        </header>

        {/* Dynamic Workspace Container */}
        <main className="p-8 flex-1">
          {activeTab === "overview" ? (
            <DataOverviewPage />
          ) : (
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 h-full">
              {/* Left Side */}
              <div className="xl:col-span-5">
                <LogInputForm
                  onSubmit={handleLogSubmission}
                  isLoading={isLoading}
                  placeholder={
                    mode === "single"
                      ? "Paste single log JSON object..."
                      : 'Paste sequence JSON object with "logs": [...]'
                  }
                />
              </div>

              {/* Right Side */}
              <div className="xl:col-span-7">
                {mode === "single" ? (
                  <AlertCard result={singleResult} />
                ) : (
                  <SequenceAlertCard result={sequenceResult} />
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
