"""
PDF parsing + clause-aware chunking for insurance policy documents.

Insurance PDFs are usually numbered/sectioned ("4.2 Exclusions", "Clause 7: ...").
We first try to split on clause-like patterns, then fall back to a sliding
window over sentences so no chunk is too large or too small.
"""
import re
import fitz  # PyMuPDF
from app.config import settings

CLAUSE_PATTERN = re.compile(
    r"(?m)^(?:\s*)(\d{1,2}(?:\.\d{1,2})*\.?\s+[A-Z][A-Za-z /&\-]{3,60}|"
    r"Clause\s+\d+[:.]?|Section\s+\d+[:.]?|Exclusions?:|Definitions?:)"
)


def extract_pages(file_bytes: bytes) -> list[dict]:
    """Returns list of {page_number, text}."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        pages.append({"page_number": i + 1, "text": text.strip()})
    doc.close()
    return pages


def _sliding_window_chunks(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(size - overlap, 1)
    for start in range(0, len(words), step):
        chunk_words = words[start:start + size]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + size >= len(words):
            break
    return chunks


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Returns list of {text, page} chunks.
    Tries clause-based splitting per page first; if a page has no clause
    markers or a clause segment is too long, falls back to sliding window.
    """
    all_chunks = []
    size_words = settings.chunk_size // 5  # rough words-per-chunk from char target
    overlap_words = settings.chunk_overlap // 5
    size_words = max(size_words, 80)
    overlap_words = max(overlap_words, 15)

    for page in pages:
        text = page["text"]
        if not text:
            continue

        splits = CLAUSE_PATTERN.split(text)
        if len(splits) <= 1:
            for c in _sliding_window_chunks(text, size_words, overlap_words):
                all_chunks.append({"text": c, "page": page["page_number"]})
            continue

        # re-attach clause headers to their following text
        segments = []
        buf = splits[0]
        i = 1
        while i < len(splits):
            header = splits[i]
            body = splits[i + 1] if i + 1 < len(splits) else ""
            segments.append((header + " " + body).strip())
            i += 2
        if buf.strip():
            segments.insert(0, buf.strip())

        for seg in segments:
            word_count = len(seg.split())
            if word_count <= size_words * 1.4:
                if seg.strip():
                    all_chunks.append({"text": seg.strip(), "page": page["page_number"]})
            else:
                for c in _sliding_window_chunks(seg, size_words, overlap_words):
                    all_chunks.append({"text": c, "page": page["page_number"]})

    return [c for c in all_chunks if len(c["text"]) > 20]
