export default function SourceCitations({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="citations">
      <span className="citations-label">Grounded in</span>
      <div className="citations-list">
        {sources.map((s, i) => (
          <details key={i} className="citation">
            <summary>
              {s.filename}{s.page ? ` · p.${s.page}` : ''}
            </summary>
            <p>{s.chunk_text}</p>
          </details>
        ))}
      </div>
    </div>
  );
}
