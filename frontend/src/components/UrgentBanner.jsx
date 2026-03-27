import React from "react";

export default function UrgentBanner({ show }) {
  if (!show) return null;

  return (
    <div className="mb-8 rounded-3xl border border-red-200 bg-red-50 p-6 shadow-sm">
      <div className="flex items-start gap-4">
        <div className="mt-1 text-2xl">⚠️</div>
        <div>
          <h2 className="text-2xl font-semibold text-red-700">
            Higher-risk result summary
          </h2>
          <p className="mt-2 text-base leading-7 text-red-700">
            Medical review is recommended, especially if symptoms are present.
          </p>
          <p className="mt-2 text-sm text-red-600">
            This is not a diagnosis. A qualified clinician should confirm the result.
          </p>
        </div>
      </div>
    </div>
  );
}