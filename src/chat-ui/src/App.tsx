import { useState, useEffect, useRef } from 'react'
import './App.css'

interface Message {
  id: string
  text: string
  sender: 'user' | 'agent'
  timestamp: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080/ws'

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket(WS_URL)
    
    ws.onopen = () => {
      console.log('Connected to supervisor agent')
      setIsConnected(true)
      addMessage('System', 'Connected to AI Observability Agent', 'agent')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      addMessage(data.id || Date.now().toString(), data.text || data.message, 'agent')
      setIsLoading(false)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }

    ws.onclose = () => {
      console.log('Disconnected from supervisor agent')
      setIsConnected(false)
    }

    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [WS_URL])

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (id: string, text: string, sender: 'user' | 'agent') => {
    setMessages(prev => [...prev, {
      id,
      text,
      sender,
      timestamp: new Date()
    }])
  }

  const sendMessage = async () => {
    if (!input.trim() || !isConnected) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message
    addMessage(Date.now().toString(), userMessage, 'user')

    // Send via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        query: userMessage,
        timestamp: new Date().toISOString()
      }))
    } else {
      // Fallback to HTTP if WebSocket not available
      try {
        const response = await fetch(`${API_URL}/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userMessage })
        })
        const data = await response.json()
        addMessage(Date.now().toString(), data.response || data.message, 'agent')
      } catch (error) {
        addMessage(Date.now().toString(), 'Error: Could not connect to agent', 'agent')
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 AI Observability Chat</h1>
        <div className="status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message agent">
              <div className="message-content">
                <div className="message-text">
                  <span className="loading">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about metrics, logs, or pod health..."
            disabled={!isConnected}
            rows={2}
          />
          <button 
            onClick={sendMessage} 
            disabled={!isConnected || !input.trim() || isLoading}
          >
            Send
          </button>
        </div>

        <div className="examples">
          <p>Try asking:</p>
          <button onClick={() => setInput("Show CPU usage for backend pods")}>
            Show CPU usage for backend pods
          </button>
          <button onClick={() => setInput("Check pod health in namespace nilabja-haldar-dev")}>
            Check pod health
          </button>
          <button onClick={() => setInput("Show error logs from last hour")}>
            Show error logs
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

// Made with Bob
