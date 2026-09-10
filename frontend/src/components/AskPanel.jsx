import { useState } from 'react';
import { askQuestion } from '../api';
import SourceCitations from './SourceCitations';

const SUGGESTIONS = [
  'Does this cover maternity expenses?',
  'What is the waiting period for pre-existing conditions?',
  'Why might a claim under this policy get rejected?',
];

export default function AskPanel({ selected, policies }) {
  const [question, setQuestion] = useState('');
  const [thread, setThread] = useState([]);
  const [loading, setLoading] = useState(false);

  async function submit(q) {
    const text = (q ?? question).trim();
    if (!text || loading) return;
    setQuestion('');
    setThread((prev) => [...prev, { role: 'user', text }]);
    setLoading(true);
    try {
      const res = await askQuestion(text, selected);
      setThread((prev) => [...prev, { role: 'assistant', text: res.answer, sources: res.sources }]);
    } catch (e) {
      setThread((prev) => [...prev, { role: 'assistant', text: `Error: ${e.message}`, sources: [] }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      {thread.length === 0 && (
        <div className="empty-state">
          <p>Ask anything about {policies.length ? 'your uploaded policies' : 'a policy — upload one to begin'}.</p>
          <div className="suggestions">
            {SUGGESTIONS.map((s) => (
              <button key={s} onClick={() => submit(s)} disabled={!policies.length}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="thread">
        {thread.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            <p>{msg.text}</p>
            {msg.role === 'assistant' && <SourceCitations sources={msg.sources} />}
          </div>
        ))}
        {loading && <div className="message message-assistant message-loading">Reading the policy…</div>}
      </div>

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Am I covered for a knee surgery?"
          disabled={!policies.length}
        />
        <button type="submit" disabled={!policies.length || loading}>Ask</button>
      </form>
    </div>
  );
}
