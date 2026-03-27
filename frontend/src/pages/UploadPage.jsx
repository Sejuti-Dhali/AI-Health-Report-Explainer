import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { uploadReport } from "../utils/api"

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError("")

    const formData = new FormData()
    formData.append("file", file)
    formData.append("language", "english")

    try {
      const data = await uploadReport(formData)
      navigate("/result", {
        state: {
          data,
          language: "english",
        },
      })
    } catch (err) {
      console.error("FULL ERROR:", err.response?.data || err)
      setError("Upload failed. Please check your file and try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 flex items-center justify-center p-4 transition-colors">
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg p-8 w-full max-w-md border border-gray-200 dark:border-slate-800">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MediScan AI</h1>
          <p className="text-gray-500 dark:text-slate-400 text-sm mt-1">
            Upload your lab report for instant explanation
          </p>
          <p className="text-gray-400 dark:text-slate-500 text-xs mt-3">
            Supports PDF and images (PNG, JPG, JPEG). Clean PDF reports give the best results.
          </p>
        </div>

        <label className="block border-2 border-dashed border-gray-300 dark:border-slate-700 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition-colors mb-4">
          <input
            type="file"
            className="hidden"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(e) => setFile(e.target.files[0])}
          />

          {file ? (
            <div>
              <p className="text-green-600 font-medium">? {file.name}</p>
              <p className="text-gray-400 text-xs mt-1">
                Click to change file
              </p>
            </div>
          ) : (
            <div>
              <p className="text-4xl mb-2">??</p>
              <p className="text-gray-600 dark:text-slate-300 text-sm">
                Click to upload PDF or image
              </p>
              <p className="text-gray-400 dark:text-slate-500 text-xs mt-1">
                PDF, PNG, JPG supported
              </p>
            </div>
          )}
        </label>

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="w-full bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Analyzing..." : "Analyze Report"}
        </button>

        <p className="text-xs text-gray-400 dark:text-slate-500 text-center mt-4">
          This tool explains reports. It does not replace a doctor.
        </p>
      </div>
    </div>
  )
}
