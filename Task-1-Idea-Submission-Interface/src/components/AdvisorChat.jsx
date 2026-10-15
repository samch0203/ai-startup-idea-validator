import { useState } from "react";
import { askAdvisor } from "../api/ideaApi.js";

// Conversational startup advisor. The backend's reply is read from reply / answer / message.
const pickReply = (data) => data?.reply ?? data?.answer ?? data?.message ?? JSON.stringify(data);

export default function AdvisorChat({ ideaId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const data = await askAdvisor(text, ideaId);
      setMessages((m) => [...m, { role: "advisor", text: pickReply(data) }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "error", text: err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="chat-log" aria-live="polite">
        {messages.length === 0 && (
          <p className="muted">Ask a follow-up question about your idea or the results above.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="bubble advisor muted">Thinking...</div>}
      </div>
      <form className="chat-form" onSubmit={send}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question"
          aria-label="Your question"
          disabled={loading}
        />
        <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
