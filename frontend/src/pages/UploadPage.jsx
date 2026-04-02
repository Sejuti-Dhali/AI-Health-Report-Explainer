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
      const status = err.response?.status
      const detail = err.response?.data?.detail

      if (detail) {
        setError(detail)
      } else if (status === 502 || status === 503 || status === 504) {
        setError("The backend is waking up or temporarily unavailable. Please wait a moment and try again.")
      } else {
        setError("Upload failed. Please check your file and try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 
    bg-gradient-to-br from-slate-100 to-slate-200 
    dark:from-slate-950 dark:to-slate-900 transition-colors">

      <div className="w-full max-w-md">
        
        {/* Card */}
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur 
        rounded-3xl shadow-xl p-8 border border-white/20 dark:border-slate-800">

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              MediScan AI
            </h1>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-2">
              Smart medical report analyzer
            </p>
          </div>

          {/* Upload Box */}
          <label className="block border-2 border-dashed 
          border-slate-300 dark:border-slate-700 
          rounded-2xl p-10 text-center cursor-pointer 
          hover:border-blue-500 hover:bg-blue-50/40 
          dark:hover:bg-slate-800 transition-all mb-5">

            <input
              type="file"
              className="hidden"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => setFile(e.target.files[0])}
            />

            {file ? (
              <div>
                <p className="text-green-600 font-medium truncate">
                  ✔ {file.name}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Click to change file
                </p>
              </div>
            ) : (
              <div>
                <p className="text-5xl mb-3">📄</p>
                <p className="text-slate-700 dark:text-slate-300 text-sm">
                  Upload your report
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  PDF, PNG, JPG supported
                </p>
              </div>
            )}
          </label>

          {/* Error */}
          {error && (
            <p className="text-red-500 text-sm mb-3 text-center">
              {error}
            </p>
          )}

          {/* Button */}
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full py-3 rounded-2xl font-medium 
            bg-gradient-to-r from-blue-600 to-indigo-600 
            text-white shadow-md hover:shadow-lg 
            hover:scale-[1.02] active:scale-95 
            disabled:opacity-50 disabled:cursor-not-allowed 
            transition-all"
          >
            {loading ? "Analyzing..." : "Analyze Report"}
          </button>

          <p className="text-xs text-amber-700 dark:text-amber-300 text-center mt-4">
            On free hosting, the first analysis after inactivity can take 30-60 seconds while the backend wakes up.
          </p>

          {/* Footer */}
          <p className="text-xs text-slate-400 text-center mt-5">
            This tool assists interpretation — not a medical diagnosis.
          </p>
        </div>
      </div>
    </div>
  )
}
