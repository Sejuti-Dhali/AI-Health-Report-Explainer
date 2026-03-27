import axios from "axios"

const API_BASE = "http://localhost:8000/api"

export async function uploadReport(formData) {
  const res = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return res.data
}

export async function askReportQuestion(payload) {
  const res = await axios.post(`${API_BASE}/chat`, payload, {
    headers: { "Content-Type": "application/json" },
  })
  return res.data
}
