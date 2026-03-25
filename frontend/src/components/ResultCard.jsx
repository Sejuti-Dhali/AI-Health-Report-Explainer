const STATUS = {
  NORMAL: {
    bg: "bg-green-50", border: "border-green-300",
    badge: "bg-green-100 text-green-800", label: "Normal", icon: "✓"
  },
  BORDERLINE: {
    bg: "bg-yellow-50", border: "border-yellow-300",
    badge: "bg-yellow-100 text-yellow-800", label: "Borderline", icon: "!"
  },
  ABNORMAL: {
    bg: "bg-red-50", border: "border-red-300",
    badge: "bg-red-100 text-red-800", label: "Needs Attention", icon: "⚠"
  }
}

export default function ResultCard({ test, value, unit, status, explanation, advice }) {
  const s = STATUS[status] || STATUS.NORMAL
  return (
    <div className={`rounded-xl border-2 p-4 mb-3 ${s.bg} ${s.border}`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-800 text-base">{test}</h3>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ml-2 shrink-0 ${s.badge}`}>
          {s.icon} {s.label}
        </span>
      </div>
      <p className="text-2xl font-bold text-gray-900 mb-1">
        {value}{" "}
        <span className="text-sm font-normal text-gray-500">{unit}</span>
      </p>
      <p className="text-sm text-gray-700 mb-2">{explanation}</p>
      <p className="text-xs text-gray-500 italic">{advice}</p>
    </div>
  )
}