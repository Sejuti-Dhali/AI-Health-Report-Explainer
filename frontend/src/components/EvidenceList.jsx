export default function EvidenceList({ evidence = [] }) {
  if (!evidence?.length) return null;

  return (
    <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="mb-2 text-sm font-semibold text-slate-700">Evidence</p>
      <div className="space-y-2">
        {evidence.map((item, idx) => (
          <div key={idx} className="rounded-lg border border-slate-200 bg-white p-2">
            <div className="text-xs font-medium text-slate-700">
              {item.title || "Untitled"} · {item.source || "unknown"}
            </div>
            <div className="mt-1 text-xs text-slate-600">
              {item.snippet || ""}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
