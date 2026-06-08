"""Embedding + vector store + retrieval for The Unofficial Guide.

planning.md (Retrieval Approach):
  - embed chunks with all-MiniLM-L6-v2 (local, 384-dim)
  - store in ChromaDB with full metadata for citation
  - cosine distance, so good matches land well below 0.5
  - retrieve top-k = 5

Run directly to (re)build the index and smoke-test retrieval on 3 eval queries:
    python vector_store.py
"""
from __future__ import annotations

import logging

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ChromaDB 0.5.x ships a posthog telemetry call that errors noisily; silence it.
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

from chunker import Chunk, load_and_chunk
from config import CHROMA_DIR, COLLECTION_NAME, DISTANCE_METRIC, EMBED_MODEL, TOP_K

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _client() -> chromadb.api.ClientAPI:
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def build_index(chunks: list[Chunk] | None = None) -> int:
    """Embed all chunks and (re)write them to a fresh ChromaDB collection.

    Drops any existing collection first so re-running never duplicates chunks.
    Returns the number of chunks indexed.
    """
    if chunks is None:
        chunks = load_and_chunk()

    client = _client()
    # Fresh collection every build -> idempotent.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": DISTANCE_METRIC},  # cosine distance
    )

    model = get_model()
    texts = [c.text for c in chunks]
    embeddings = model.encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    ).tolist()

    collection.add(
        ids=[c.id for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[c.metadata for c in chunks],
    )
    return len(chunks)


def search(query: str, k: int = TOP_K) -> list[dict]:
    """Return the top-k most similar chunks to `query`.

    Each result: {id, text, distance (cosine), professor, course, source_url, metadata}.
    """
    collection = _client().get_collection(COLLECTION_NAME)
    q_emb = get_model().encode(
        [query], normalize_embeddings=True, show_progress_bar=False
    ).tolist()
    res = collection.query(query_embeddings=q_emb, n_results=k)

    out = []
    for cid, doc, dist, meta in zip(
        res["ids"][0], res["documents"][0], res["distances"][0], res["metadatas"][0]
    ):
        out.append({
            "id": cid,
            "text": doc,
            "distance": round(float(dist), 3),
            "professor": meta.get("professor", ""),
            "course": meta.get("course", ""),
            "source_url": meta.get("source_url", ""),
            "metadata": meta,
        })
    return out


# --------------------------------------------------------------------------- #
# Smoke test (Milestone 4 checkpoint)
# --------------------------------------------------------------------------- #
_SMOKE_QUERIES = [
    "I'm choosing a CS61A professor — what do students say about Dan Garcia?",
    "Are John Canny's classes worth taking?",
    "Which CS professor is known for giving good feedback and being patient in office hours?",
]


def _smoke_test() -> None:
    n = build_index()
    print(f"Indexed {n} chunks into ChromaDB collection '{COLLECTION_NAME}' "
          f"({DISTANCE_METRIC} distance).\n")

    for q in _SMOKE_QUERIES:
        print("=" * 90)
        print(f"QUERY: {q}")
        results = search(q, k=TOP_K)
        best = results[0]["distance"]
        flag = "✓ strong" if best < 0.5 else "⚠ weak (>0.5)"
        print(f"top result distance = {best}  [{flag}]\n")
        for i, r in enumerate(results, 1):
            first_line = r["text"].splitlines()[0]
            print(f" {i}. dist={r['distance']:<5}  {r['professor']} ({r['course']})  "
                  f"[{r['id']}]")
            print(f"      {first_line}")
        print()


if __name__ == "__main__":
    _smoke_test()
