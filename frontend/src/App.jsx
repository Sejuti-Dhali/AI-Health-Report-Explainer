import { BrowserRouter, Routes, Route } from "react-router-dom"
import { useState, useEffect } from "react"
import UploadPage from "./pages/UploadPage"
import ResultPage from "./pages/ResultPage"

export default function App() {
  const [dark, setDark] = useState(false)

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [dark])

  return (
    <>
      <button
        onClick={() => setDark(!dark)}
        className="fixed top-4 right-4 z-50 px-4 py-2 rounded-xl bg-slate-800 text-white dark:bg-yellow-400 dark:text-slate-900 shadow"
      >
        {dark ? "☀️ Light" : "🌙 Dark"}
      </button>

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/result" element={<ResultPage />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}
