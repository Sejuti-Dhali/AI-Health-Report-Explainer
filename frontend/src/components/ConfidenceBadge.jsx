export default function ConfidenceBadge({ band, score }) {
  const normalized = (band || "low").toLowerCase();
  const color =
    normalized === "high"
      ? "bg-green-100 text-green-800 border-green-200"
      : normalized === "moderate"
      ? "bg-yellow-100 text-yellow-800 border-yellow-200"
      : "bg-red-100 text-red-800 border-red-200";

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${color}`}>
      Confidence: {band || "low"} {typeof score === "number" ? `(${score.toFixed(2)})` : ""}
    </span>
  );
}
