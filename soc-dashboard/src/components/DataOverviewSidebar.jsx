import { useState, useEffect } from "react";
import { X, PieChart, BarChart3, AlertTriangle } from "lucide-react";
// Assuming you add a fetchStats function to your api.js
import { fetchDatasetStats } from "../services/api";

export default function DataOverviewSidebar({ isOpen, onClose }) {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isOpen && !stats) {
      loadStats();
    }
  }, [isOpen]);

  const loadStats = async () => {
    setIsLoading(true);
    try {
      const data = await fetchDatasetStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to load distribution stats:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Backdrop for mobile/smaller screens */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 transition-opacity xl:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-80 bg-slate-900 border-l border-slate-700 z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center gap-2 text-white font-semibold">
            <PieChart size={20} className="text-blue-500" />
            <h2>Data Distribution</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-4 flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-40 text-slate-400 animate-pulse">
              Loading real-time stats...
            </div>
          ) : stats ? (
            <div className="space-y-6">
              {/* Total Volume */}
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <h3 className="text-sm text-slate-400 mb-1 flex items-center gap-2">
                  <BarChart3 size={16} /> Total Training Sequences
                </h3>
                <p className="text-2xl font-bold text-white">
                  {stats.total_sequences.toLocaleString()}
                </p>
              </div>

              {/* Anomaly Breakdown */}
              <div>
                <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                  <AlertTriangle size={16} className="text-yellow-500" />
                  Class Breakdown
                </h3>
                <div className="space-y-2">
                  {Object.entries(stats.class_distribution).map(
                    ([className, count]) => (
                      <div key={className} className="flex flex-col gap-1">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-400 capitalize">
                            {className.replace("_", " ")}
                          </span>
                          <span className="text-white font-medium">
                            {count.toLocaleString()}
                          </span>
                        </div>
                        {/* Simple progress bar representation */}
                        <div className="w-full bg-slate-800 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${className === "normal" ? "bg-emerald-500" : "bg-red-500"}`}
                            style={{
                              width: `${(count / stats.total_sequences) * 100}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-red-400 text-sm text-center mt-10">
              Failed to load dataset statistics.
            </div>
          )}
        </div>
      </div>
    </>
  );
}
