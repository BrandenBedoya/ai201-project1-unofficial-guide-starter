"""Central configuration for The Unofficial Guide RAG pipeline.

Keeping paths and the decisions from planning.md in one place means the chunker,
the vector store, generation, and evaluation all agree on the same numbers.
"""
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
CHROMA_DIR = BASE_DIR / "chroma_db"          # gitignored; rebuilt by vector_store.py

# --- Embedding + vector store (planning.md: Retrieval Approach) ---
EMBED_MODEL = "all-MiniLM-L6-v2"             # local, 384-dim, no API key
COLLECTION_NAME = "berkeley_cs_reviews"
DISTANCE_METRIC = "cosine"                    # cosine distance -> good matches well under 0.5

# --- Retrieval (planning.md: top-k decision) ---
TOP_K = 5
