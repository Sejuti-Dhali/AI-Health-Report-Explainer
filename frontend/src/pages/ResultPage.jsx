import { useMemo, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import ResultCard from "../components/ResultCard"
import UrgentBanner from "../components/UrgentBanner"
import ChatBox from "../components/ChatBox"

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

  const data = location.state?.data

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4 transition-colors">
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-200 dark:border-slate-800 p-8 max-w-lg w-full text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            No result found
          </h1>
          <p className="text-gray-600 dark:text-slate-400 mb-6">
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

  const results = data.results || []

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

  const reportContext =
    (data.summary || "") +
    " " +
    results
      .map(
        (item) =>
          `${item.test}: ${item.value}${item.unit ? ` ${item.unit}` : ""} (${item.status || "unknown"})`
      )
      .join(", ")

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 md:p-6 transition-colors">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-200 dark:border-slate-800 p-6 mb-5">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400 mb-2">
                MediScan AI
              </p>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Report Analysis
              </h1>
              <p className="text-slate-500 dark:text-slate-400 mt-2">
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

        <div className="mb-6 bg-blue-50 dark:bg-slate-900/60 border border-blue-200 dark:border-slate-700 rounded-2xl p-4">
          <p className="text-sm text-blue-900 dark:text-slate-200 font-medium">
            Benchmark-guided interpretation
          </p>
          <p className="text-xs text-blue-800 dark:text-slate-400 mt-1">
            Interpretations are benchmark-guided using standard lab reference intervals. Exact source labels are shown only where available.
          </p>
        </div>

        {results.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-200 dark:border-slate-800 p-8 text-center">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No measurable lab parameters found
            </h3>
            <p className="text-gray-600 dark:text-slate-400 text-sm">
              This file may not be a numeric lab report, or the report text could not be extracted clearly.
              Clean PDF lab reports usually work best.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {abnormal.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                  Needs attention
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {abnormal.map((item, idx) => (
                    <ResultCard key={`abnormal-${idx}`} result={item} />
                  ))}
                </div>
              </section>
            )}

            {normal.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                  Within expected range
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {normal.map((item, idx) => (
                    <ResultCard key={`normal-${idx}`} result={item} />
                  ))}
                </div>
              </section>
            )}

            {unknown.length > 0 && (
              <section>
                <div className="flex items-center justify-between gap-4 mb-4 flex-wrap">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Could not be confidently interpreted
                  </h3>

                  <button
                    onClick={() => setShowUnknown((prev) => !prev)}
                    className="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 text-sm font-medium"
                  >
                    {showUnknown ? "Hide uncertain results" : `Show uncertain results (${unknown.length})`}
                  </button>
                </div>

                {showUnknown && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {unknown.map((item, idx) => (
                      <ResultCard key={`unknown-${idx}`} result={item} />
                    ))}
                  </div>
                )}
              </section>
            )}
          </div>
        )}

        <ChatBox reportContext={reportContext} language="english" />

        <div className="mt-6 bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-200 dark:border-slate-800 p-4">
          <p className="text-xs text-gray-500 dark:text-slate-400">
            {data.disclaimer || "This analysis is AI-generated and does not replace a doctor."}
          </p>
        </div>
      </div>
    </div>
  )
}