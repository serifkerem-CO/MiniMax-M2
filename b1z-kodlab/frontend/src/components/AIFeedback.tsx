import { useState } from 'react'
import axios from 'axios'

export default function AIFeedback() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([
    {
      role: 'assistant',
      content: '👋 Merhaba! Ben B1Z KODLAB AI Mentor\'un. Kodlama hakkında her türlü soruyu sorabilirsin!'
    }
  ])
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async () => {
    if (!message.trim()) return

    const userMessage = message
    setMessage('')
    setChatHistory([...chatHistory, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await axios.post('/api/ai/chat', null, {
        params: {
          message: userMessage,
          context: 'B1Z KODLAB AI Mentor conversation'
        }
      })

      setChatHistory(prev => [
        ...prev,
        { role: 'assistant', content: response.data.response }
      ])
    } catch (error: any) {
      setChatHistory(prev => [
        ...prev,
        { role: 'assistant', content: `❌ Hata: ${error.response?.data?.detail || error.message}` }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[500px]">
      {/* Chat History */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 bg-b1z-gray-900 rounded-lg p-4 border-2 border-b1z-gray-700">
        {chatHistory.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-b1z-accent text-b1z-black'
                  : 'bg-b1z-gray-800 text-b1z-white border-2 border-b1z-gray-700'
              }`}
            >
              <p className="text-xs font-bold mb-1">
                {msg.role === 'user' ? '👤 Sen' : '🤖 AI Mentor (MiniMax-M2)'}
              </p>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-b1z-gray-800 p-3 rounded-lg border-2 border-b1z-gray-700">
              <p className="text-sm text-b1z-accent animate-pulse">
                🤖 Düşünüyorum...
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Kodlama hakkında bir şey sor..."
          className="flex-1 input-b1z"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !message.trim()}
          className="btn-b1z"
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </div>

      {/* Quick Actions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={() => setMessage('Python ile liste nasıl oluşturulur?')}
          className="text-xs px-3 py-1 bg-b1z-gray-800 hover:bg-b1z-gray-700 rounded border border-b1z-gray-600"
        >
          💡 Python listesi
        </button>
        <button
          onClick={() => setMessage('Async/await nedir?')}
          className="text-xs px-3 py-1 bg-b1z-gray-800 hover:bg-b1z-gray-700 rounded border border-b1z-gray-600"
        >
          💡 Async/await
        </button>
        <button
          onClick={() => setMessage('Rust ownership nasıl çalışır?')}
          className="text-xs px-3 py-1 bg-b1z-gray-800 hover:bg-b1z-gray-700 rounded border border-b1z-gray-600"
        >
          💡 Rust ownership
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 p-3 bg-b1z-gray-900 border-2 border-b1z-accent rounded-lg">
        <p className="text-xs text-b1z-gray-500 text-center">
          🧠 <span className="text-b1z-accent font-bold">11 Akıl Harmanları</span> ile
          desteklenen AI mentorluğu
        </p>
      </div>
    </div>
  )
}
