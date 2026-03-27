export default function ResultCard({ item }) {
  const status = (item.status || "unknown").toLowerCase()

  const statusStyles = {
    high: {
      badge: "bg-red-100 text-red-700 border-red-200",
      card: "border-red-200 bg-red-50/40",
      dot: "bg-red-500",
      label: "High",
      icon: "↑",
    },
    low: {
      badge: "bg-amber-100 text-amber-700 border-amber-200",
      card: "border-amber-200 bg-amber-50/40",
      dot: "bg-amber-500",
      label: "Low",
      icon: "↓",
    },
    normal: {
      badge: "bg-green-100 text-green-700 border-green-200",
      card: "border-green-200 bg-green-50/40",
      dot: "bg-green-500",
      label: "Normal",
      icon: "✓",
    },
    unknown: {
      badge: "bg-gray-100 text-gray-700 border-gray-200",
      card: "border-gray-200 bg-white",
      dot: "bg-gray-400",
      label: "Unknown",
      icon: "?",
    },
  }

  const ui = statusStyles[status] || statusStyles.unknown

  return (
    <div className={`rounded-2xl border shadow-sm p-5 transition-all hover:shadow-md ${ui.card}`}>
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`w-2.5 h-2.5 rounded-full ${ui.dot}`}></span>
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {ui.icon} {item.test || "Unknown test"}
            </h3>
          </div>

          <p className="text-sm text-gray-600">
            {item.value || "N/A"} {item.unit || ""}
          </p>
        </div>

        <span className={`px-3 py-1 rounded-full text-xs font-semibold border whitespace-nowrap ${ui.badge}`}>
          {ui.label}
        </span>
      </div>

      <div className="space-y-3 text-sm">
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">Reference</p>
          <p className="text-gray-800">{item.reference || "Not available"}</p>
        </div>

        <div>
          <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">Interpretation</p>
          <p className="text-gray-800 leading-6">
            {item.explanation || "No explanation available."}
          </p>
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">
            Source: {item.source_label || "Unknown"}
          </span>

          <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">
            Confidence: {item.confidence || "unknown"}
          </span>

          <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">
            {item.interpretation_mode || "unknown"}
          </span>
        </div>
      </div>
    </div>
  )
}