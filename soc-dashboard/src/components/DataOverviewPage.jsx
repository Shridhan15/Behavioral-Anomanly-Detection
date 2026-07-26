import { useState, useEffect } from "react";
import { BarChart3, ShieldAlert, Database, Info } from "lucide-react";
import { fetchDatasetStats } from "../services/api";

const DATA_TYPE_DEFINITIONS = {
  normal: {
    title: "Normal Baseline Activity",
    desc: "Represents standard, authenticated user workflows during normal working hours. Used by the models to establish a baseline behavioral profile.",
  },
  brute_force: {
    title: "Brute Force Attack",
    desc: "Characterized by rapid, repeated failed authentication attempts from a single source IP. Often targets administrative endpoints to guess passwords.",
  },
  credential_stuffing: {
    title: "Credential Stuffing",
    desc: "Involves automated scripts injecting leaked username and password pairs across multiple accounts. Identified by high request frequency and distinct payload structures.",
  },
  device_spoofing: {
    title: "Device Spoofing",
    desc: "Occurs when a session utilizes mismatched or heavily altered user-agent signatures and device fingerprints to bypass endpoint controls.",
  },
  impossible_travel: {
    title: "Impossible Travel",
    desc: "Triggered when an entity authenticates successfully from two geographically distant locations in an unrealistically short time window.",
  },
  insider_drift: {
    title: "Insider Drift",
    desc: "Gradual behavioral deviation where a legitimate user slowly starts accessing unauthorized or out-of-department resources over time.",
  },
  lateral_movement: {
    title: "Lateral Movement",
    desc: "Tactics used by an attacker to systematically pivot across internal systems, databases, and secondary nodes after initial compromise.",
  },
  low_and_slow: {
    title: "Low and Slow Attack",
    desc: "Stealthy malicious activity spread out over long time intervals with minimal requests per hour to evade traditional rate-limiting and signature thresholds.",
  },
};

export default function DataOverviewPage() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDatasetStats()
      .then((data) => setStats(data))
      .catch((err) => console.error("Failed to load stats:", err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 animate-pulse">
        Loading dataset distribution metrics...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <Database className="text-blue-500" size={24} />
          <h2 className="text-xl font-bold text-white">
            Dataset Distribution Overview
          </h2>
        </div>
        <p className="text-sm text-slate-400">
          Real-time metrics tracking the volume of sequences and categorical
          distribution used to train the Bidirectional LSTM and One-Class SVM
          models.
        </p>
        <div className="mt-4 inline-flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg border border-slate-700">
          <BarChart3 size={18} className="text-emerald-400" />
          <span className="text-sm text-slate-300">
            Total Processed Sequences:
          </span>
          <span className="font-bold text-white">
            {stats?.total_sequences?.toLocaleString() || 0}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {stats &&
          Object.entries(stats.class_distribution).map(([className, count]) => {
            const percentage = ((count / stats.total_sequences) * 100).toFixed(
              1,
            );
            const meta = DATA_TYPE_DEFINITIONS[className] || {
              title: className.replace("_", " "),
              desc: "Custom behavioral telemetry category evaluated by the engine.",
            };

            return (
              <div
                key={className}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-white capitalize flex items-center gap-2">
                      {className !== "normal" ? (
                        <ShieldAlert size={16} className="text-red-400" />
                      ) : (
                        <div className="w-2 h-2 rounded-full bg-emerald-400" />
                      )}
                      {meta.title}
                    </h3>
                    <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {count.toLocaleString()} rows ({percentage}%)
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4">
                    {meta.desc}
                  </p>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-800 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${className === "normal" ? "bg-emerald-500" : "bg-red-500"}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}
