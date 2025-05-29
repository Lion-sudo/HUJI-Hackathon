import React, { useState } from 'react';

const API_URL = 'http://localhost:8000/api/chat';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      if (res.status === 403) {
        const data = await res.json();
        setError(data.detail || 'Jailbreak attempt detected');
      } else if (!res.ok) {
        setError('Server error');
      } else {
        const data = await res.json();
        setResponse(data.response);
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', padding: 20, fontFamily: 'sans-serif' }}>
      <h2>LLM Chat</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          rows={4}
          placeholder="Type your prompt here..."
          style={{ fontSize: 16, padding: 8 }}
          required
        />
        <button type="submit" disabled={loading} style={{ fontSize: 16, padding: 8 }}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      {response && (
        <div style={{ marginTop: 24, background: '#f6f6f6', padding: 16, borderRadius: 8 }}>
          <strong>LLM Response:</strong>
          <div>{response}</div>
        </div>
      )}
      {error && (
        <div style={{ marginTop: 24, color: 'red' }}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

export default App;
