import { useState, useRef, useEffect } from 'react'
import { Navbar } from '../components/Navbar'
import { ragAPIClient } from '../utils/api'
import { Send, Loader, AlertCircle } from 'lucide-react'

export const ChatPage = () => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    setError('')
    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await ragAPIClient.query(userMessage)
      const data = response.data
      console.log('[Chat] API Response:', data)

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
        },
      ])
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to get response. Please try again.'
      setError(errorMsg)
      setMessages((prev) =>
        prev.slice(0, -1).concat({
          role: 'error',
          content: errorMsg,
        })
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-dark">
      <Navbar />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">💬</div>
              <h2 className="text-2xl font-bold text-white mb-2">Start a Conversation</h2>
              <p className="text-gray-400">Ask questions about your uploaded documents</p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in`}
          >
            <div
              className={`max-w-md px-4 py-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.role === 'error'
                  ? 'bg-red-900/20 border border-red-700 text-red-400'
                  : 'bg-gray-800 text-gray-100'
              }`}
            >
              <p className="text-sm md:text-base whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-600 text-xs text-gray-300">
                  <p className="font-semibold mb-1">Sources:</p>
                  <ul className="space-y-1">
                    {msg.sources.map((source, i) => (
                      <li key={i}>• {source}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start fade-in">
            <div className="bg-gray-800 px-4 py-3 rounded-lg flex items-center gap-2">
              <Loader size={18} className="animate-spin text-blue-500" />
              <p className="text-gray-300 text-sm">Thinking...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-800 p-4 bg-darker">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-900/20 border border-red-700 rounded-lg mb-4">
            <AlertCircle size={18} className="text-red-500" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something about your documents..."
            disabled={loading}
            className="flex-1 px-4 py-3 bg-dark border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <Loader size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}
