import { useState } from 'react';
import { comparePolicies } from '../api';
import SourceCitations from './SourceCitations';

export default function ComparePanel({ selected, policies }) {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const selectedPolicies = policies.filter((p) => selected.includes(p.policy_id));

  async function submit(e) {
    e.preventDefault();
    if (!question.trim() || selected.length < 2) return;
    setLoading(true);
    setError('');
    try {
      const res = await comparePolicies(question.trim(), selected);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      {selected.length < 2 && (
        <p className="empty-hint">Select at least 2 policies in the sidebar to compare them.</p>
      )}

      <form className="composer" onSubmit={submit}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Which policy covers dental treatment better?"
          disabled={selected.length < 2}
        />
        <button type="submit" disabled={selected.length < 2 || loading}>Compare</button>
      </form>

      {error && <p className="error-text">{error}</p>}
      {loading && <p className="empty-hint">Comparing {selectedPolicies.length} policies…</p>}

      {result && (
        <div className="compare-result">
          <p className="compare-summary">{result.summary}</p>
          <div className="compare-table">
            {result.rows.map((row) => (
              <div key={row.policy_id} className="compare-row">
                <div className="compare-row-header">{row.filename}</div>
                <p className="compare-finding">{row.finding}</p>
                <SourceCitations sources={row.sources} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
