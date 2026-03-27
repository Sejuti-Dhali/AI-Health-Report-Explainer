import React from "react";

const getStatusStyles = (status) => {
  const s = String(status || "").toLowerCase();

  if (s === "high" || s === "low" || s === "abnormal") {
    return {
      border: "border-amber-300 dark:border-amber-500",
      badge:
        "bg-amber-100 text-amber-700 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/30",
      dot: "bg-amber-500",
      accent: "border-l-4 border-amber-400 dark:border-amber-500",
    };
  }

  if (s === "normal") {
    return {
      border: "border-emerald-300 dark:border-emerald-500",
      badge:
        "bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:border-emerald-500/30",
      dot: "bg-emerald-500",
      accent: "border-l-4 border-emerald-400 dark:border-emerald-500",
    };
  }

  return {
    border: "border-slate-300 dark:border-slate-700",
    badge:
      "bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700",
    dot: "bg-slate-400",
    accent: "border-l-4 border-slate-300 dark:border-slate-700",
  };
};

export default function ResultCard({ result }) {
  const status = result?.status || "uncertain";
  const styles = getStatusStyles(status);

  return (
    <div
      className={`rounded-3xl bg-white dark:bg-slate-900 shadow-sm ${styles.border} ${styles.accent} border p-6 transition hover:shadow-md`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className={`mt-2 h-3 w-3 rounded-full ${styles.dot}`} />
          <div>
            <h3 className="text-2xl font-semibold text-slate-900 dark:text-white">
              {result?.test || "Unknown test"}
            </h3>
            <p className="mt-2 text-lg text-slate-700 dark:text-slate-300">
              {result?.value || "N/A"}{" "}
              <span className="text-slate-500 dark:text-slate-400">
                {result?.unit || ""}
              </span>
            </p>
          </div>
        </div>

        <span
          className={`rounded-full px-4 py-1 text-sm font-medium ${styles.badge}`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      <div className="mt-5 space-y-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Reference
          </p>
          <p className="mt-1 text-base text-slate-800 dark:text-slate-200">
            {result?.reference || "Not available"}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Interpretation
          </p>
          <p className="mt-1 text-base leading-7 text-slate-800 dark:text-slate-200">
            {result?.explanation || "No explanation available."}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Reference basis
          </p>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            {result?.reference ? "Standard lab reference interval" : "Not available"}
          </p>

          {result?.source && (
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Source: {result.source}
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {result?.reference && (
          <span className="rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-3 py-1 text-xs">
            Benchmark-guided
          </span>
        )}
        <span className="rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-3 py-1 text-xs">
          AI-assisted
        </span>
      </div>
    </div>
  );
}