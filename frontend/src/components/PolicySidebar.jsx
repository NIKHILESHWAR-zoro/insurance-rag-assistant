import { useRef, useState } from 'react';
import { uploadPolicy, deletePolicy } from '../api';

export default function PolicySidebar({ policies, setPolicies, selected, setSelected }) {
  const fileInput = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  async function handleFiles(files) {
    setError('');
    for (const file of files) {
      setUploading(true);
      try {
        const res = await uploadPolicy(file);
        setPolicies((prev) => [...prev, res.policy]);
        setSelected((prev) => [...prev, res.policy.policy_id]);
      } catch (e) {
        setError(e.message);
      } finally {
        setUploading(false);
      }
    }
  }

  function toggle(policyId) {
    setSelected((prev) =>
      prev.includes(policyId) ? prev.filter((id) => id !== policyId) : [...prev, policyId]
    );
  }

  async function handleDelete(policyId) {
    await deletePolicy(policyId);
    setPolicies((prev) => prev.filter((p) => p.policy_id !== policyId));
    setSelected((prev) => prev.filter((id) => id !== policyId));
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>Policy Reader</h1>
        <p>Upload policy PDFs, then ask questions grounded in the actual fine print.</p>
      </div>

      <div
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFiles(Array.from(e.dataTransfer.files).filter((f) => f.type === 'application/pdf'));
        }}
        onClick={() => fileInput.current.click()}
      >
        <input
          ref={fileInput}
          type="file"
          accept="application/pdf"
          multiple
          hidden
          onChange={(e) => handleFiles(Array.from(e.target.files))}
        />
        <span className="dropzone-label">{uploading ? 'Indexing…' : 'Drop a policy PDF, or click to browse'}</span>
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="policy-list">
        {policies.length === 0 && <p className="empty-hint">No policies uploaded yet.</p>}
        {policies.map((p) => (
          <label key={p.policy_id} className="policy-item">
            <input
              type="checkbox"
              checked={selected.includes(p.policy_id)}
              onChange={() => toggle(p.policy_id)}
            />
            <div className="policy-meta">
              <span className="policy-name">{p.filename}</span>
              <span className="policy-chunks">{p.num_chunks} clauses indexed</span>
            </div>
            <button
              className="policy-remove"
              onClick={(e) => {
                e.preventDefault();
                handleDelete(p.policy_id);
              }}
              aria-label={`Remove ${p.filename}`}
            >
              ×
            </button>
          </label>
        ))}
      </div>
    </aside>
  );
}
