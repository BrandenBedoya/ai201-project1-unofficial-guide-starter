"""Grounded answer generation for The Unofficial Guide.

The engineering challenge here is GROUNDING: the LLM must answer from the retrieved
student reviews only, never from its own training knowledge, and it must refuse when
the reviews don't cover the question.

Two layers enforce this (belt and suspenders):
  1. A strict system prompt with hard rules (answer only from context, refuse otherwise,
     report disagreement, cite the [Professor, Course] labels).
  2. Programmatic source attribution: the `sources` returned to the UI are built from the
     ACTUAL retrieved chunks' metadata, not parsed out of the LLM's text. So citations are
     guaranteed even if the model forgets to add them.

A relevance gate also short-circuits to a refusal when nothing retrieved is close enough,
so clearly out-of-domain questions never even reach the LLM.

Run directly to test end-to-end on a few queries + an out-of-scope query:
    python generate.py
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from config import TOP_K
from vector_store import search

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

# If even the best retrieved chunk is farther than this (cosine distance), treat the
# question as out-of-domain and refuse without calling the LLM. Tuned against the
# observed in-domain range (~0.2-0.5) and out-of-domain queries (~0.8+).
RELEVANCE_GATE = 0.75

REFUSAL = "I don't have enough information on that."

SYSTEM_PROMPT = f"""You are The Unofficial Guide, answering questions about UC Berkeley \
Computer Science professors and courses using ONLY the student reviews provided to you.

Rules — follow them exactly:
1. Use ONLY the information in the provided reviews. Never use outside or prior knowledge \
about any professor, course, or university.
2. If the provided reviews do not contain enough information to answer, reply with exactly: \
"{REFUSAL}" and nothing else.
3. When reviews about the same professor disagree, say so explicitly and summarize BOTH \
sides — do not flatten a divisive professor into a single verdict.
4. Cite your evidence inline using the bracketed source labels shown with each review, \
e.g. [Dan Garcia, CS61A]. Attribute each claim to the review(s) it came from.
5. Be concise and concrete. Quote or paraphrase what students actually said \
(ratings, specific complaints/praise). Do not invent details not present in the reviews."""


def _format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as a numbered, source-labeled context block."""
    lines = []
    for i, c in enumerate(chunks, 1):
        label = f"[{c['professor']}, {c['course']}]"
        lines.append(f"Review {i} {label}:\n{c['text']}")
    return "\n\n".join(lines)


def _format_source(c: dict) -> str:
    prof, course, url = c["professor"], c["course"], c["source_url"]
    return f"{prof} — Rate My Professors ({url})" if url else f"{prof} ({course})"


def _sources_for_answer(chunks: list[dict], answer_text: str) -> list[str]:
    """Build the citation list programmatically from retrieved chunk metadata.

    Top-k retrieval (k=5) often pulls in off-topic professors on broad queries, so we cite
    only the retrieved professors the answer actually discusses (matched by name in the
    answer text). This keeps attribution programmatic — we never trust the LLM to format
    citations — while avoiding over-attribution. Falls back to all retrieved sources if no
    professor name is found in the answer.
    """
    text = answer_text.lower()
    seen, used = set(), []
    for c in chunks:
        if c["professor"].lower() in text and c["source_url"] not in seen:
            seen.add(c["source_url"])
            used.append(_format_source(c))
    if used:
        return used
    # Fallback: cite everything retrieved (deduped).
    for c in chunks:
        if c["source_url"] not in seen:
            seen.add(c["source_url"])
            used.append(_format_source(c))
    return used


def answer(question: str, k: int = TOP_K) -> dict:
    """End-to-end grounded answer.

    Returns {answer, sources, contexts, refused, top_distance}.
    """
    chunks = search(question, k=k)
    top_distance = chunks[0]["distance"] if chunks else 1.0

    # Relevance gate: nothing close enough -> refuse without calling the LLM.
    if not chunks or top_distance > RELEVANCE_GATE:
        return {
            "answer": REFUSAL,
            "sources": [],
            "contexts": chunks,
            "refused": True,
            "top_distance": top_distance,
        }

    context = _format_context(chunks)
    user_prompt = (
        f"Student reviews:\n\n{context}\n\n"
        f"---\nQuestion: {question}\n\n"
        f"Answer using only the reviews above, following all the rules."
    )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,  # deterministic, grounded
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = resp.choices[0].message.content.strip()
    refused = REFUSAL.lower() in text.lower() and len(text) < len(REFUSAL) + 20

    return {
        "answer": text,
        "sources": [] if refused else _sources_for_answer(chunks, text),
        "contexts": chunks,
        "refused": refused,
        "top_distance": top_distance,
    }


# --------------------------------------------------------------------------- #
# End-to-end test (Milestone 5 checkpoint)
# --------------------------------------------------------------------------- #
_TEST_QUERIES = [
    "What do students say about Dan Garcia for CS61A?",        # divisive
    "Are John Canny's classes worth taking?",                  # negative consensus
    "Which professor gives good feedback and is patient in office hours?",  # sparse signal
    "What's the best dorm for freshmen at Berkeley?",          # OUT OF SCOPE -> refuse
]


def _demo() -> None:
    for q in _TEST_QUERIES:
        print("=" * 90)
        print(f"Q: {q}")
        r = answer(q)
        tag = "  [REFUSED]" if r["refused"] else ""
        print(f"(top_distance={r['top_distance']}){tag}\n")
        print(r["answer"])
        if r["sources"]:
            print("\nSources:")
            for s in r["sources"]:
                print(f"  • {s}")
        print()


if __name__ == "__main__":
    _demo()
