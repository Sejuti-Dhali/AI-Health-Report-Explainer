export default function ManualReviewBadge({ show }) {
  if (!show) return null;
  return (
    <span className="inline-flex items-center rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700">
      Manual review recommended
    </span>
  );
}
