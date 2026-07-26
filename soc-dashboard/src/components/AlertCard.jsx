import { ShieldAlert, ShieldCheck } from "lucide-react";

export default function AlertCard({ result }) {
  if (!result) return null;

  const isAnomaly = result.is_anomaly;
  const cardStyles = isAnomaly
    ? "bg-red-900/20 border-red-500/50"
    : "bg-green-900/20 border-green-500/50";

  const textStyles = isAnomaly ? "text-red-400" : "text-green-400";
  const Icon = isAnomaly ? ShieldAlert : ShieldCheck;

  return (
    <div className={`mt-6 p-6 rounded-lg shadow-lg border ${cardStyles}`}>
      <div className="flex items-center gap-3 mb-4">
        <Icon className={textStyles} size={28} />
        <h2 className={`text-2xl font-bold ${textStyles}`}>{result.status}</h2>
      </div>

      <div className="space-y-4 text-slate-300">
        <div>
          <p className="text-sm text-slate-400 uppercase tracking-wider mb-1">
            Classification
          </p>
          <p className="font-medium">{result.explanation.alert_type}</p>
        </div>

        <div>
          <p className="text-sm text-slate-400 uppercase tracking-wider mb-1">
            Primary Triggers
          </p>
          <ul className="list-disc list-inside space-y-1">
            {result.explanation.primary_triggers.map((trigger, idx) => (
              <li key={idx} className="text-sm">
                {trigger}
              </li>
            ))}
          </ul>
        </div>

        <div className="pt-4 border-t border-slate-700/50">
          <p className="text-sm text-slate-400 uppercase tracking-wider mb-1">
            Recommended Action
          </p>
          <p className="font-semibold text-white">
            {result.explanation.recommended_action}
          </p>
        </div>
      </div>
    </div>
  );
}
