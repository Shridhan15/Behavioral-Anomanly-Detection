import { useState } from "react";
import { Terminal } from "lucide-react";

export default function LogInputForm({ onSubmit, isLoading }) {
  const [jsonInput, setJsonInput] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    try {
      const parsedData = JSON.parse(jsonInput);
      onSubmit(parsedData);
    } catch (err) {
      setError("Invalid JSON format. Please check your syntax.");
    }
  };

  return (
    <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <Terminal className="text-blue-400" size={20} />
        <h2 className="text-lg font-semibold">Manual Log Injection</h2>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <textarea
          className="w-full h-48 bg-slate-900 text-green-400 p-4 rounded font-mono text-sm border border-slate-700 focus:border-blue-500 focus:outline-none resize-none"
          placeholder="Paste JSON log payload here..."
          value={jsonInput}
          onChange={(e) => setJsonInput(e.target.value)}
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={isLoading || !jsonInput}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium py-2 px-4 rounded transition-colors"
        >
          {isLoading ? "Analyzing..." : "Evaluate Payload"}
        </button>
      </form>
    </div>
  );
}
