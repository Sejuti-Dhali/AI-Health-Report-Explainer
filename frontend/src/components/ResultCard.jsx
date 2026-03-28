import React from "react";

const getStatusStyles = (status) => {
  const s = String(status || "").toLowerCase();

  if (s === "high" || s === "low" || s === "abnormal") {
    return {
      border: "border-amber-300 dark:border-amber-500",
      badge:
        "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300",
      dot: "bg-amber-500",
    };
  }

  if (s === "normal") {
    return {
      border: "border-emerald-300 dark:border-emerald-500",
      badge:
        "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300",
      dot: "bg-emerald-500",
    };
  }

  return {
    border: "border-slate-300 dark:border-slate-700",
    badge:
      "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
    dot: "bg-slate-400",
  };
};

export default function ResultCard({ result }) {
  const status = result?.status || "uncertain";
  const styles = getStatusStyles(status);

  return (
    <div
      className={`rounded-3xl bg-white/80 dark:bg-slate-900/80 backdrop-blur 
      border ${styles.border} p-6 shadow-sm hover:shadow-lg transition`}
    >
      {/* Top */}
      <div className="flex justify-between items-start gap-4">
        <div className="flex gap-3">
          <span className={`mt-2 h-3 w-3 rounded-full ${styles.dot}`} />

          <div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
              {result?.test || "Unknown test"}
            </h3>

            <p className="mt-1 text-lg text-slate-700 dark:text-slate-300">
              {result?.value || "N/A"}{" "}
              <span className="text-sm text-slate-500">
                {result?.unit || ""}
              </span>
            </p>
          </div>
        </div>

        <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles.badge}`}>
          {status}
        </span>
      </div>

      {/* Content */}
      <div className="mt-5 space-y-4 text-sm">
        <div>
          <p className="text-xs text-slate-400 uppercase">Reference</p>
          <p className="text-slate-700 dark:text-slate-300 mt-1">
            {result?.reference || "Not available"}
          </p>
        </div>

        <div>
          <p className="text-xs text-slate-400 uppercase">Interpretation</p>
          <p className="text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">
            {result?.explanation || "No explanation available."}
          </p>
        </div>

        {result?.source && (
          <p className="text-xs text-slate-400">
            Source: {result.source}
          </p>
        )}
      </div>

      {/* Tags */}
      <div className="mt-4 flex gap-2 flex-wrap">
        <span className="px-3 py-1 text-xs rounded-full bg-slate-100 dark:bg-slate-800">
          AI-assisted
        </span>

        {result?.reference && (
          <span className="px-3 py-1 text-xs rounded-full bg-slate-100 dark:bg-slate-800">
            Benchmark-based
          </span>
        )}
      </div>
    </div>
  );
}