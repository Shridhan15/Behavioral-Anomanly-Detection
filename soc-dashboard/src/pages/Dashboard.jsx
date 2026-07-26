import { useState } from "react";
import LogInputForm from "../components/LogInputForm";
import AlertCard from "../components/AlertCard";
import SequenceAlertCard from "../components/SequenceAlertCard";
import { evaluateSingleLog, evaluateSequenceLogs } from "../services/api";
import { Shield, Layers, Activity } from "lucide-react";

export default function Dashboard() {
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
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="p-8 max-w-5xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8 pb-4 border-b border-slate-700">
          {/* ... rest of your code ... */}
          <div className="flex items-center gap-3">
            <Activity className="text-blue-500" size={32} />
            <div>
              <h1 className="text-3xl font-bold text-white">
                SOC Intelligence Engine
              </h1>
              <p className="text-sm text-slate-400">
                Real-Time Anomaly Detection & Threat Explainability
              </p>
            </div>
          </div>

          {/* Mode Selector Tabs */}
          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700">
            <button
              onClick={() => setMode("single")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === "single"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Shield size={16} /> Single Event (SVM)
            </button>
            <button
              onClick={() => setMode("sequence")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === "sequence"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Layers size={16} /> Sequence Timeline (LSTM)
            </button>
          </div>
        </header>
      </div>

      {/* Main Content */}
      <main className="grid grid-cols-1 gap-6">
        <LogInputForm
          onSubmit={handleLogSubmission}
          isLoading={isLoading}
          placeholder={
            mode === "single"
              ? "Paste single log JSON object..."
              : 'Paste sequence JSON object with "logs": [...]'
          }
        />

        {mode === "single" ? (
          <AlertCard result={singleResult} />
        ) : (
          <SequenceAlertCard result={sequenceResult} />
        )}
      </main>
    </div>
  );
}
