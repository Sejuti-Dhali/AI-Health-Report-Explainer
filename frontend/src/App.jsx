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
    <div className="transition-colors duration-300">
      {/* Toggle */}
      <button
        onClick={() => setDark(!dark)}
        className="fixed top-4 right-4 z-50 px-4 py-2 rounded-full 
        bg-white/80 dark:bg-slate-800/80 backdrop-blur 
        text-slate-800 dark:text-white 
        shadow-md hover:scale-105 active:scale-95 transition"
      >
        {dark ? "☀️" : "🌙"}
      </button>

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/result" element={<ResultPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}