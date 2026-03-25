import { BrowserRouter, Routes, Route } from "react-router-dom"
import UploadPage from "./pages/UploadPage.jsx"
import ResultPage from "./pages/ResultPage.jsx"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </BrowserRouter>
  )
}