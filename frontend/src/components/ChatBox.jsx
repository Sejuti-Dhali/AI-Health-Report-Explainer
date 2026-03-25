import { useState } from "react"
import axios from "axios"

export default function ChatBox({ reportContext, language }) {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const ask = async () => {
    if (!question.trim()) return
    const userMsg = { role: "user", text: question }
    setMessages(prev => [...prev, userMsg])
    setQuestion("")
    setLoading(true)

    try {
      const res = await axios.post("http://localhost:8000/api/chat", {
        question,
        report_context: reportContext,
        language
      })
      setMessages(prev => [...prev, { role: "ai", text: res.data.answer }])
    } catch {
      setMessages(prev => [...prev, { role: "ai", text: "Something went wrong. Please try again." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-6 border rounded-xl p-4 bg-white">
      <h2 className="font-semibold text-gray-800 mb-3">Ask a follow-up question</h2>
      <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm p-3 rounded-lg ${
            m.role === "user"
              ? "bg-blue-50 text-blue-900 ml-8"
              : "bg-gray-50 text-gray-800 mr-8"
          }`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="text-sm text-gray-400 italic">Thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === "Enter" && ask()}
          placeholder="e.g. Is my HbA1c serious?"
          className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <button
          onClick={ask}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  )
}