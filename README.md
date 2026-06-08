# The Unofficial Guide 🐻

A Retrieval-Augmented Generation (RAG) system that makes **student-generated knowledge about UC Berkeley
CS/EECS professors searchable and answerable**. Ask a plain-language question — *"Which professor should I
take for CS61A?"* — and get a grounded, **cited** answer drawn from real student reviews, not the model's
general knowledge.

> Berkeley CS students rely heavily on word-of-mouth to decide *who* to take for a given course — the same
> class can be a great experience or a demoralizing one depending entirely on the instructor. That knowledge
> is real but scattered across hundreds of individual reviews. The official catalog tells you a course exists;
> it never tells you a professor "made the final unreasonably hard and refused to release the distribution."
> This system aggregates that diffuse, contradictory signal and answers questions with citations.

---

## Status

| Milestone | Status |
|---|---|
| 1 — Choose domain & collect documents | ✅ Done |
| 2 — Chunking strategy | ⬜ Not started |
| 3 — Vector store & semantic search | ⬜ Not started |
| 4 — Grounded response generation | ⬜ Not started |
| 5 — Query interface | ⬜ Not started |
| 6 — Evaluation report | ⬜ Not started |

---

## The corpus (Milestone 1)

**11 documents**, each a UC Berkeley professor's Rate My Professors page, chosen for **contrast** — beloved,
disliked, and divisive instructors across CS10 / CS61A / CS61B / CS164 / CS170 / CS182 / CS184 / CS188 /
CS189 / DATA8 / DATA144. See [`data/sources.md`](data/sources.md) for the full manifest, URLs, and honesty
caveats (sampling, truncation, single-source). Raw text lives in [`data/raw/`](data/raw/).

### Ingestion (collection) process
1. Identified 11 professor pages spanning many courses and the full rating spectrum (1.3/5 → 4.9/5).
2. Fetched each page and extracted student reviews verbatim with their metadata (course, quality, difficulty,
   grade, date, tags).
3. Saved each as a structured raw markdown file under `data/raw/` with a metadata header carrying the source
   URL, professor, courses, and overall ratings — so every future chunk can cite its origin.

_Cleaning/preprocessing and chunking are implemented in Milestone 2._

---

## Setup

```bash
# from the repo root
python -m venv .venv
source .venv/bin/activate            # Mac/Linux
pip install -r requirements.txt

cp .env.example .env                 # then add your free Groq key from console.groq.com
```

## Stack

| Component | Tool | Notes |
|---|---|---|
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | local, no API key — _confirmed in M3_ |
| Vector store | ChromaDB | local, no account |
| LLM | Groq (`llama-3.3-70b-versatile`) | free tier |

> **Embedding model choice & production tradeoffs** will be documented here in Milestone 3
> (cost, context length, multilingual support, local vs. API).

---

## Evaluation
_Milestone 6: 5 test questions with ground-truth answers, retrieval + response accuracy, and at least one
documented failure case. The seed questions are in [`planning.md`](planning.md)._
