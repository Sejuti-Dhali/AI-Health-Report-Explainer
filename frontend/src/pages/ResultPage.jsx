import { useLocation, useNavigate } from "react-router-dom"
import ResultCard from "../components/ResultCard"
import UrgentBanner from "../components/UrgentBanner"
import ChatBox from "../components/ChatBox"

export default function ResultPage() {
  const { state } = useLocation()
  const navigate = useNavigate()

  if (!state?.data) {
    navigate("/")
    return null
  }

  const { data, language } = state

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-gray-900">Your Report Results</h1>
          <button
            onClick={() => navigate("/")}
            className="text-sm text-blue-600 hover:underline"
          >
            ← Upload Another
          </button>
        </div>

        {/* Urgent Banner */}
        <UrgentBanner show={data.see_doctor_urgently} />

        {/* Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <h2 className="font-semibold text-blue-900 mb-1">Summary</h2>
          <p className="text-blue-800 text-sm">{data.summary}</p>
        </div>

        {/* Result Cards */}
        <div className="mb-6">
          <h2 className="font-semibold text-gray-700 mb-3">Test Results</h2>
          {data.results.map((r, i) => (
            <ResultCard key={i} {...r} />
          ))}
        </div>

        {/* Chat */}
        <ChatBox
          reportContext={data.summary + " " + data.results.map(r =>
            `${r.test}: ${r.value} ${r.unit} (${r.status})`
          ).join(", ")}
          language={language}
        />

        {/* Disclaimer */}
        <p className="text-xs text-gray-400 text-center mt-6 pb-6">
          {data.disclaimer}
        </p>
      </div>
    </div>
  )
}
