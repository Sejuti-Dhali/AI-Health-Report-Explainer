import { normalizeResultForUi } from "../utils/ragUi";
import WarningChip from "../components/WarningChip";
import EvidenceList from "../components/EvidenceList";
import ManualReviewBadge from "../components/ManualReviewBadge";
import ConfidenceBadge from "../components/ConfidenceBadge";
import { useMemo, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import ResultCard from "../components/ResultCard"
import UrgentBanner from "../components/UrgentBanner"

const EMPTY_RESULTS = []

function confidenceScore(confidence) {
  const c = (confidence || "").toLowerCase()
  if (c === "high") return 2
  if (c === "medium") return 1
  return 0
}

function statusPriority(status) {
  const s = (status || "").toLowerCase()
  if (s === "high" || s === "low") return 0
  if (s === "normal") return 1
  return 2
}

function sortResults(items) {
  return [...items].sort((a, b) => {
    const aStatus = statusPriority(a.status)
    const bStatus = statusPriority(b.status)

    if (aStatus !== bStatus) return aStatus - bStatus

    const aConf = confidenceScore(a.confidence)
    const bConf = confidenceScore(b.confidence)

    if (aConf !== bConf) return bConf - aConf

    return (a.test || "").localeCompare(b.test || "")
  })
}

export default function ResultPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const [showUnknown, setShowUnknown] = useState(false)

  const data = location.state?.data ?? null
  const results = data?.results ?? EMPTY_RESULTS

  const abnormal = useMemo(
    () =>
      sortResults(
        results.filter((item) => ["high", "low"].includes((item.status || "").toLowerCase()))
      ),
    [results]
  )

  const normal = useMemo(
    () =>
      sortResults(
        results.filter((item) => (item.status || "").toLowerCase() === "normal")
      ),
    [results]
  )

  const unknown = useMemo(
    () =>
      sortResults(
        results.filter((item) => (item.status || "").toLowerCase() === "unknown")
      ),
    [results]
  )

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-8 max-w-lg w-full text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-3">No result found</h1>
          <p className="text-gray-600 mb-6">
            No analysis data was found for this page. Please upload a report again.
          </p>
          <button
            onClick={() => navigate("/")}
            className="bg-slate-900 text-white px-5 py-3 rounded-2xl hover:bg-black"
          >
            Go back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-6 mb-5">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">
                MediScan AI
              </p>
              <h1 className="text-3xl font-bold text-slate-900">Report Analysis</h1>
              <p className="text-slate-500 mt-2">
                Grounded interpretation using benchmark rules and extracted report values
              </p>
            </div>

            <button
              onClick={() => navigate("/")}
              className="bg-slate-900 text-white px-5 py-3 rounded-2xl hover:bg-black"
            >
              Analyze another report
            </button>
          </div>
        </div>

        <UrgentBanner
          show={data.see_doctor_urgently}
          riskLevel={data.risk_level}
        />

        <div className="bg-gradient-to-r from-slate-900 to-slate-700 text-white rounded-3xl shadow-sm p-6 mb-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300 mb-2">Overall Summary</p>
              <h2 className="text-xl font-semibold mb-2">
                {data.risk_level || "Unknown"} risk interpretation
              </h2>
              <p className="text-slate-100 max-w-3xl">
                {data.summary || "No summary available."}
              </p>
            </div>

            <div className="flex gap-3 flex-wrap">
              <div className="bg-white/10 rounded-2xl px-4 py-3 min-w-[120px]">
                <div className="text-xs text-slate-300 mb-1">Abnormal</div>
                <div className="text-2xl font-bold">{abnormal.length}</div>
              </div>

              <div className="bg-white/10 rounded-2xl px-4 py-3 min-w-[120px]">
                <div className="text-xs text-slate-300 mb-1">Normal</div>
                <div className="text-2xl font-bold">{normal.length}</div>
              </div>

              <div className="bg-white/10 rounded-2xl px-4 py-3 min-w-[120px]">
                <div className="text-xs text-slate-300 mb-1">Uncertain</div>
                <div className="text-2xl font-bold">{unknown.length}</div>
              </div>
            </div>
          </div>
        </div>

        {results.length === 0 ? (
          <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-8 text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No measurable lab parameters found</h3>
            <p className="text-gray-600 text-sm">
              This file may not be a numeric lab report, or the report text could not be extracted clearly.
              Clean PDF lab reports usually work best.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {abnormal.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Needs attention</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {abnormal.map((item, idx) => (
                    <ResultCard key={`abnormal-${idx}`} item={item} />
                  ))}
                </div>
              </section>
            )}

            {normal.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Within expected range</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {normal.map((item, idx) => (
                    <ResultCard key={`normal-${idx}`} item={item} />
                  ))}
                </div>
              </section>
            )}

            {unknown.length > 0 && (
              <section>
                <div className="flex items-center justify-between gap-4 mb-4 flex-wrap">
                  <h3 className="text-lg font-semibold text-slate-900">
                    Could not be confidently interpreted
                  </h3>

                  <button
                    onClick={() => setShowUnknown((prev) => !prev)}
                    className="px-4 py-2 rounded-xl border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 text-sm font-medium"
                  >
                    {showUnknown ? "Hide uncertain results" : `Show uncertain results (${unknown.length})`}
                  </button>
                </div>

                {showUnknown && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {unknown.map((item, idx) => (
                      <ResultCard key={`unknown-${idx}`} item={item} />
                    ))}
                  </div>
                )}
              </section>
            )}
          </div>
        )}

        <div className="mt-6 bg-white rounded-3xl shadow-sm border border-gray-200 p-4">
          <p className="text-xs text-gray-500">
            {data.disclaimer || "This analysis is AI-generated and does not replace a doctor."}
          </p>
        </div>
      </div>
    </div>
  )
}


{/* RAG_SAFETY_UI_BLOCK */}
{/* Place this block inside each rendered test-result card and replace `item` with your row variable if needed */}
{(() => {
  const r = normalizeResultForUi(item);
  return (
    <div className="mt-3">
      <div className="flex flex-wrap gap-2">
        <ConfidenceBadge band={r.confidence_band} score={r.confidence_score} />
        <ManualReviewBadge show={r.needs_manual_review} />
        <WarningChip show={r.hallucination_flag || !r.evidence_support} text="Low evidence support" />
      </div>

      {(r.needs_manual_review || r.hallucination_flag || !r.evidence_support) ? (
        <div className="mt-2 rounded-lg border border-amber-200 bg-amber-50 p-2 text-xs text-amber-800">
          Interpretation uncertainty is elevated. Review with a clinician is recommended.
        </div>
      ) : null}

      <EvidenceList evidence={r.retrieved_evidence || []} />
    </div>
  );
})()}
