from app import vectorstore
from app.gemini_client import generate
from app.config import settings

SYSTEM_INSTRUCTION = """You are an insurance policy assistant. You answer ONLY using the
provided policy excerpts (context). Rules:
1. Never use outside knowledge about insurance in general — only what's in the context.
2. If the context does not contain the answer, clearly say the policy documents don't
   specify this, rather than guessing.
3. Always mention which policy/document your answer is based on.
4. Be precise about exclusions, waiting periods, and conditions — these matter a lot to users.
5. Keep answers concise and in plain, everyday language (avoid legal jargon where possible),
   but do not lose important conditions or numbers.
"""


def _format_context(chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks):
        blocks.append(
            f"[Source {i+1} | Policy: {c['filename']} | Page: {c.get('page', '?')}]\n{c['text']}"
        )
    return "\n\n".join(blocks)


def answer_question(question: str, policy_ids: list[str] | None) -> dict:
    chunks = vectorstore.query(question, top_k=settings.top_k, policy_ids=policy_ids)
    if not chunks:
        return {
            "answer": "I couldn't find any uploaded policy content to answer this. "
                      "Please upload a policy PDF first.",
            "sources": [],
        }

    context = _format_context(chunks)
    prompt = f"""Context (excerpts from insurance policy documents):
{context}

Question: {question}

Answer using ONLY the context above. Cite which policy each part of your answer comes from."""

    answer_text = generate(prompt, system_instruction=SYSTEM_INSTRUCTION)

    sources = [
        {
            "policy_id": c["policy_id"],
            "filename": c["filename"],
            "chunk_text": c["text"][:500],
            "page": c.get("page"),
            "score": c.get("distance"),
        }
        for c in chunks
    ]
    return {"answer": answer_text, "sources": sources}


def compare_policies(question: str, policy_ids: list[str]) -> dict:
    rows = []
    per_policy_chunks = {}

    for pid in policy_ids:
        chunks = vectorstore.query(question, top_k=settings.top_k, policy_ids=[pid])
        per_policy_chunks[pid] = chunks
        filename = chunks[0]["filename"] if chunks else pid

        if not chunks:
            rows.append({
                "policy_id": pid,
                "filename": filename,
                "finding": "No relevant content found in this policy for this question.",
                "sources": [],
            })
            continue

        context = _format_context(chunks)
        prompt = f"""Context (excerpts from ONE insurance policy document, "{filename}"):
{context}

Question: {question}

In 2-3 sentences, answer specifically for THIS policy only, using only the context above."""
        finding = generate(prompt, system_instruction=SYSTEM_INSTRUCTION)

        rows.append({
            "policy_id": pid,
            "filename": filename,
            "finding": finding,
            "sources": [
                {
                    "policy_id": c["policy_id"],
                    "filename": c["filename"],
                    "chunk_text": c["text"][:500],
                    "page": c.get("page"),
                    "score": c.get("distance"),
                }
                for c in chunks
            ],
        })

    # Synthesis: compare across the per-policy findings
    findings_block = "\n\n".join(
        f"{r['filename']}: {r['finding']}" for r in rows
    )
    summary_prompt = f"""Here are per-policy findings for the question: "{question}"

{findings_block}

Write a short (3-5 sentence) side-by-side comparison summary highlighting the key
differences between these policies for this question. Be specific and factual."""
    summary = generate(summary_prompt, system_instruction=SYSTEM_INSTRUCTION)

    return {"summary": summary, "rows": rows}
