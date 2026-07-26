import { ShieldAlert, ShieldCheck, Activity } from "lucide-react";

export default function SequenceAlertCard({ result }) {
  if (!result) return null;

  const isAnomaly = result.status === "ANOMALY DETECTED";
  const cardStyles = isAnomaly
    ? "bg-red-900/20 border-red-500/50"
    : "bg-green-900/20 border-green-500/50";

  const textStyles = isAnomaly ? "text-red-400" : "text-green-400";
  const Icon = isAnomaly ? ShieldAlert : ShieldCheck;

  // Convert confidence to percentage
  const confidencePct = (result.confidence_score * 100).toFixed(2);

  return (
    <div className={`p-6 rounded-lg shadow-lg border ${cardStyles}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Icon className={textStyles} size={32} />
          <div>
            <h2 className={`text-2xl font-bold ${textStyles}`}>
              {result.status}
            </h2>
            <p className="text-sm text-slate-400">
              LSTM Temporal Sequence Analysis
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs uppercase tracking-wider text-slate-400">
            Confidence
          </span>
          <p className="text-2xl font-mono font-bold text-white">
            {confidencePct}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-slate-300">
        {/* Left Column: Triggers and Actions */}
        <div className="space-y-4">
          <div>
            <p className="text-sm text-slate-400 uppercase tracking-wider mb-1">
              Predicted Vector
            </p>
            <p className="text-lg font-semibold text-white capitalize">
              {result.predicted_attack_type.replace("_", " ")}
            </p>
          </div>

          <div>
            <p className="text-sm text-slate-400 uppercase tracking-wider mb-1">
              Primary Triggers
            </p>
            <ul className="list-disc list-inside space-y-1">
              {result.explanation.primary_triggers.map((trigger, idx) => (
                <li key={idx} className="text-sm text-slate-300">
                  {trigger}
                </li>
              ))}
            </ul>
          </div>

          <div className="pt-2 border-t border-slate-700/50">
            <p className="text-sm text-slate-400 uppercase tracking-wider mb-1">
              Recommended Action
            </p>
            <p className="font-semibold text-white">
              {result.explanation.recommended_action}
            </p>
          </div>
        </div>

        {/* Right Column: Softmax Class Probabilities */}
        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700/50">
          <div className="flex items-center gap-2 mb-3">
            <Activity size={16} className="text-blue-400" />
            <p className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Softmax Probability Distribution
            </p>
          </div>

          <div className="space-y-2">
            {Object.entries(result.all_probabilities).map(
              ([attackClass, prob]) => {
                const percentage = (prob * 100).toFixed(1);
                const isSelected = attackClass === result.predicted_attack_type;

                return (
                  <div key={attackClass} className="text-xs">
                    <div className="flex justify-between mb-1">
                      <span
                        className={
                          isSelected
                            ? "font-bold text-white capitalize"
                            : "text-slate-400 capitalize"
                        }
                      >
                        {attackClass.replace("_", " ")}
                      </span>
                      <span className="font-mono text-slate-400">
                        {percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${isSelected ? (isAnomaly ? "bg-red-500" : "bg-green-500") : "bg-slate-600"}`}
                        style={{ width: `${Math.max(percentage, 1)}%` }}
                      />
                    </div>
                  </div>
                );
              },
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
