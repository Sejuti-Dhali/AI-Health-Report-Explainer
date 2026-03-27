export default function UrgentBanner({ show, riskLevel }) {
  if (!show && !riskLevel) return null

  const level = (riskLevel || "").toLowerCase()

  const styles =
    level === "high"
      ? "bg-red-50 border-red-200 text-red-800"
      : level === "moderate"
      ? "bg-amber-50 border-amber-200 text-amber-800"
      : "bg-blue-50 border-blue-200 text-blue-800"

  const title =
    level === "high"
      ? "Higher-risk result summary"
      : level === "moderate"
      ? "Moderate-risk result summary"
      : "Result summary"

  return (
    <div className={`border rounded-3xl p-5 mb-5 shadow-sm ${styles}`}>
      <div className="font-semibold mb-1 text-base">{title}</div>
      <div className="text-sm leading-6">
        {show
          ? "Medical review is recommended, especially if symptoms are present."
          : "No urgent flag was triggered by the current benchmarked interpretation."}
      </div>
    </div>
  )
}
