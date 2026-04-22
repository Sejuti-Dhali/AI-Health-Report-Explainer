export default function WarningChip({ show, text = "Low evidence support" }) {
  if (!show) return null;
  return (
    <span className="inline-flex items-center rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700">
      {text}
    </span>
  );
}
