import React, { useState } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000/api/chat';

interface Message {
  role: string;
  content: string;
}

function App() {
  const [prompt, setPrompt] = useState('');
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError('');
    
    // Store the prompt and clear the input immediately
    const currentPrompt = prompt;
    setPrompt('');
    
    // Add user message to chat history
    const userMessage: Message = { role: 'user', content: currentPrompt };
    setChatHistory(prev => [...prev, userMessage]);
    
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: currentPrompt,
          chat_history: chatHistory
        }),
      });
      
      if (res.status === 403) {
        const data = await res.json();
        setError(data.detail || 'Jailbreak attempt detected');
      } else if (!res.ok) {
        setError('Server error');
      } else {
        const data = await res.json();
        // Add assistant response to chat history
        const assistantMessage: Message = { role: 'assistant', content: data.response };
        setChatHistory(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-container">
        <header className="chat-header">
          <h1>LLM Security Demo</h1>
          <p className="subtitle">AI Jailbreak Detection System</p>
        </header>

        <div className="chat-messages">
          {chatHistory.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-header">
                  <span className={`${message.role}-badge`}>
                    {message.role === 'user' ? 'You' : 'AI Assistant'}
                  </span>
                </div>
                <div className="message-text">{message.content}</div>
              </div>
            </div>
          ))}
          {error && (
            <div className="message error">
              <div className="message-content">
                <div className="message-header">
                  <span className="error-badge">Security Alert</span>
                </div>
                <div className="message-text">{error}</div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-wrapper">
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (prompt.trim()) {
                    handleSubmit(e);
                  }
                }
              }}
              placeholder="Type your message here..."
              className="chat-input"
              required
            />
            <button 
              type="submit" 
              disabled={loading} 
              className={`send-button ${loading ? 'loading' : ''}`}
            >
              {loading ? (
                <span className="loading-spinner"></span>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" className="send-icon">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/>
                </svg>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
