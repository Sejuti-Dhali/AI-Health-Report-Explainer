import React from "react";

export default function UrgentBanner({ show }) {
  if (!show) return null;

  return (
    <div className="mb-8 rounded-3xl border border-red-300 dark:border-red-500/40 
    bg-gradient-to-r from-red-50 to-red-100 
    dark:from-red-500/10 dark:to-red-500/5 
    p-6 shadow-sm">

      <div className="flex items-start gap-4">
        <div className="text-3xl">⚠️</div>

        <div>
          <h2 className="text-xl md:text-2xl font-semibold text-red-700 dark:text-red-400">
            Higher-risk result detected
          </h2>

          <p className="mt-2 text-sm md:text-base text-red-700 dark:text-red-300">
            A medical review is recommended, especially if symptoms are present.
          </p>

          <p className="mt-2 text-xs text-red-600 dark:text-red-400">
            This is not a diagnosis. Please consult a qualified doctor.
          </p>
        </div>
      </div>
    </div>
  );
}