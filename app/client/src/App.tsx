import React, { useState } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000/api/chat';

interface Message {
  role: string;
  content: string;
}

interface ErrorResponse {
  detail: {
    message: string;
    verdict: string;
  };
}

function App() {
  const [prompt, setPrompt] = useState('');
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [error, setError] = useState<ErrorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError(null);
    
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
        setError({
          detail: {
            message: 'Request rejected.',
            verdict: data.detail.verdict
          }
        });
      } else if (!res.ok) {
        setError({
          detail: {
            message: 'Server error',
            verdict: 'An unexpected error occurred. Please try again.'
          }
        });
      } else {
        const data = await res.json();
        // Add assistant response to chat history
        const assistantMessage: Message = { role: 'assistant', content: data.response };
        setChatHistory(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      setError({
        detail: {
          message: 'Network error',
          verdict: 'Unable to connect to the server. Please check your internet connection.'
        }
      });
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
                  <span className="error-badge">
                    {error.detail.message}
                    <button 
                      className="explanation-button"
                      onClick={() => setShowExplanation(!showExplanation)}
                      title="Click for explanation"
                    >
                      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                      </svg>
                    </button>
                  </span>
                </div>
                {showExplanation && (
                  <div className="explanation-text">{error.detail.verdict}</div>
                )}
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
