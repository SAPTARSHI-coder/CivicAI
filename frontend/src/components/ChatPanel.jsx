import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'

export default function ChatPanel({ sessionId, provider, currentLanguage }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  
  const speakText = (text) => {
    if (!('speechSynthesis' in window)) return
    
    window.speechSynthesis.cancel()
    
    const utterance = new SpeechSynthesisUtterance(text)
    const langMap = {
      'English': 'en-US',
      'Hindi': 'hi-IN',
      'Bengali': 'bn-IN',
      'Odia': 'or-IN'
    }
    utterance.lang = langMap[currentLanguage] || 'en-US'
    window.speechSynthesis.speak(utterance)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ session_id: sessionId, message: userMsg, provider: provider })
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        const errorMsg = errData?.error?.message || errData?.detail || 'Chat request failed'
        throw new Error(errorMsg)
      }
      const data = await res.json()
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (err) {
      console.error(err)
      setMessages(prev => [...prev, { role: 'system', content: `Error: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.1rem' }}>Ask a follow-up question</h3>

      <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', minHeight: '200px', maxHeight: '400px', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {messages.length === 0 ? (
          <p style={{ color: '#64748b', fontStyle: 'italic', fontSize: '0.9rem' }}>No messages yet. Ask something about the document!</p>
        ) : (
          <AnimatePresence>
            {messages.map((m, idx) => (
              <motion.div 
                key={idx} 
                layout
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={m.role === 'user' ? 'chat-bubble-user' : (m.role === 'assistant' ? 'chat-bubble-assistant' : 'chat-bubble-system')}
                style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  padding: '0.75rem 1rem',
                  borderRadius: '12px',
                  maxWidth: '85%',
                  position: 'relative'
                }}
              >
                {m.role === 'assistant' ? (
                  <div className="markdown-body">
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  </div>
                ) : (
                  m.content
                )}
                
                {/* TTS Listen Button for assistant replies */}
                {m.role === 'assistant' && ('speechSynthesis' in window) && (
                  <button 
                    onClick={() => speakText(m.content)}
                    title="Listen aloud"
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer', padding: '4px',
                      position: 'absolute', right: '-30px', top: '50%', transform: 'translateY(-50%)',
                      opacity: 0.6
                    }}
                  >
                    🔊
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        )}
        
        {loading && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="chat-bubble-system"
            style={{ alignSelf: 'flex-start', padding: '0.75rem 1rem', borderRadius: '12px' }}
          >
            <span className="typing-indicator" aria-hidden="true">
               <span className="dot"></span>
               <span className="dot"></span>
               <span className="dot"></span>
            </span>
          </motion.div>
        )}
      </div>

      <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <input 
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question..."
          style={{ flex: 1, padding: '0.75rem', borderRadius: '24px', border: '1px solid #cbd5e1' }}
          disabled={loading}
        />

        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          type="submit" 
          disabled={loading || !input.trim()}
          className="chat-btn-send"
          style={{ padding: '0.75rem 1.25rem', borderRadius: '24px', cursor: 'pointer' }}
        >
          Send
        </motion.button>
      </form>
    </div>
  )
}
