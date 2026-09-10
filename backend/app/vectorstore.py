import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.gemini_client import embed_text, embed_batch

_client = chromadb.PersistentClient(
    path=settings.chroma_persist_dir,
    settings=ChromaSettings(anonymized_telemetry=False),
)
_collection = _client.get_or_create_collection(name="insurance_policies")


def add_policy_chunks(policy_id: str, filename: str, chunks: list[dict]) -> int:
    """chunks: list of {text, page}. Returns number of chunks added."""
    if not chunks:
        return 0
    texts = [c["text"] for c in chunks]
    embeddings = embed_batch(texts, task_type="retrieval_document")
    ids = [f"{policy_id}::{uuid.uuid4().hex[:8]}" for _ in chunks]
    metadatas = [
        {"policy_id": policy_id, "filename": filename, "page": c.get("page", 0)}
        for c in chunks
    ]
    _collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(chunks)


def query(question: str, top_k: int, policy_ids: list[str] | None = None) -> list[dict]:
    q_embedding = embed_text(question, task_type="retrieval_query")
    where = {"policy_id": {"$in": policy_ids}} if policy_ids else None
    result = _collection.query(
        query_embeddings=[q_embedding],
        n_results=top_k,
        where=where,
    )
    out = []
    if not result["ids"] or not result["ids"][0]:
        return out
    for i in range(len(result["ids"][0])):
        out.append({
            "text": result["documents"][0][i],
            "policy_id": result["metadatas"][0][i]["policy_id"],
            "filename": result["metadatas"][0][i]["filename"],
            "page": result["metadatas"][0][i].get("page"),
            "distance": result["distances"][0][i] if "distances" in result else None,
        })
    return out


def list_policies() -> list[dict]:
    all_data = _collection.get(include=["metadatas"])
    seen = {}
    for meta in all_data["metadatas"]:
        pid = meta["policy_id"]
        if pid not in seen:
            seen[pid] = {"policy_id": pid, "filename": meta["filename"], "num_chunks": 0}
        seen[pid]["num_chunks"] += 1
    return list(seen.values())


def delete_policy(policy_id: str) -> None:
    _collection.delete(where={"policy_id": policy_id})
