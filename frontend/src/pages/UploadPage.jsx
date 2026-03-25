import { useState } from "react"
import axios from "axios"
import { useNavigate } from "react-router-dom"

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
      const res = await axios.post("http://localhost:8000/api/upload", formData)
      navigate("/result", { state: { data: res.data, language: "english" } })
    } catch (err) {
      setError("Upload failed. Please check your file and try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">MediScan AI</h1>
          <p className="text-gray-500 text-sm mt-1">Upload your lab report for instant explanation</p>
        </div>
        <label className="block border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition-colors mb-4">
          <input
            type="file"
            className="hidden"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={e => setFile(e.target.files[0])}
          />
          {file ? (
            <div>
              <p className="text-green-600 font-medium">checkmark {file.name}</p>
              <p className="text-gray-400 text-xs mt-1">Click to change file</p>
            </div>
          ) : (
            <div>
              <p className="text-4xl mb-2">doc</p>
              <p className="text-gray-600 text-sm">Click to upload PDF or image</p>
              <p className="text-gray-400 text-xs mt-1">PDF, PNG, JPG supported</p>
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
        <p className="text-xs text-gray-400 text-center mt-4">
          This tool explains reports. It does not replace a doctor.
        </p>
      </div>
    </div>
  )
}
