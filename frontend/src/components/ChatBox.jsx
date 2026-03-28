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

      setMessages(prev => [
        ...prev,
        { role: "ai", text: res.data.answer }
      ])
    } catch (err) {
      console.error(err)
      setMessages(prev => [
        ...prev,
        { role: "ai", text: "Something went wrong. Please try again." }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-10 rounded-3xl border border-slate-200 dark:border-slate-800 
    bg-white/80 dark:bg-slate-900/80 backdrop-blur shadow-sm p-5">

      <h2 className="font-semibold text-slate-900 dark:text-white mb-4 text-lg">
        Ask follow-up questions
      </h2>

      {/* Chat messages */}
      <div className="space-y-3 mb-4 max-h-72 overflow-y-auto pr-1">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-sm p-3 rounded-2xl max-w-[80%] ${
              m.role === "user"
                ? "ml-auto bg-blue-600 text-white"
                : "mr-auto bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
            }`}
          >
            {m.text}
          </div>
        ))}

        {loading && (
          <div className="text-sm text-slate-400 italic">
            AI is thinking...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === "Enter" && ask()}
          placeholder="Ask anything about your report..."
          className="flex-1 rounded-xl px-4 py-2 text-sm 
          bg-slate-100 dark:bg-slate-800 
          text-slate-900 dark:text-white
          placeholder:text-slate-500 dark:placeholder:text-slate-400
          border border-slate-200 dark:border-slate-700
          focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={ask}
          disabled={loading}
          className="px-4 py-2 rounded-xl text-sm font-medium 
          bg-blue-600 text-white 
          hover:bg-blue-700 active:scale-95 
          disabled:opacity-50 transition"
        >
          Ask
        </button>
      </div>
    </div>
  )
}