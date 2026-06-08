"""Document ingestion + chunking for The Unofficial Guide.

Implements the strategy specified in planning.md:
  - one review = one chunk (NOT a fixed character window)
  - overlap = 0 (reviews are independent records; overlap would blend opinions)
  - each chunk is "enriched" with professor/course/rating so it is self-describing,
    and carries the same fields as structured metadata for citation + filtering.

Run directly to load, chunk, count, and inspect:
    python chunker.py
"""
from __future__ import annotations

import html
import random
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

from config import RAW_DIR


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class Chunk:
    id: str                       # e.g. "rmp_garcia.md::2"
    text: str                     # enriched, self-describing chunk text (what gets embedded)
    metadata: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Cleaning
# --------------------------------------------------------------------------- #
_TAG_RE = re.compile(r"<[^>]+>")
_BOILERPLATE_RE = re.compile(
    r"(read more|share this|report (this )?rating|helpful\?|\d+ comments?)",
    re.IGNORECASE,
)
_WS_RE = re.compile(r"[ \t]+")


def clean_text(text: str) -> str:
    """Strip HTML tags/entities, common review-site boilerplate, and normalize whitespace.

    Our raw files are already fairly clean (fetched as text, not HTML), so this is
    mostly defensive — but it is the stage that would catch <div>, &amp;, "Read more",
    etc. if a future source is messier. After cleaning we verify by printing a document.
    """
    text = html.unescape(text)          # &amp; -> &, &#39; -> '
    text = _TAG_RE.sub("", text)        # drop any stray HTML tags
    text = _BOILERPLATE_RE.sub("", text)
    text = _WS_RE.sub(" ", text)        # collapse runs of spaces/tabs
    return text.strip()


# --------------------------------------------------------------------------- #
# Parsing a raw professor file
# --------------------------------------------------------------------------- #
def _parse_header(header_lines: list[str]) -> dict:
    """Turn the `key: value` block at the top of a raw file into a dict."""
    meta = {}
    for line in header_lines:
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta


_NUM_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")


def _parse_rating_line(line: str) -> dict:
    """Parse a review's pipe-delimited first line, e.g.:
    'CS61A | Jun 7, 2026 | Quality 1.0 | Difficulty 5.0 | Grade B+'
    """
    parts = [p.strip() for p in line.split("|")]
    out = {"course": parts[0] if parts else "", "date": "", "quality": -1.0,
           "difficulty": -1.0, "grade": ""}
    if len(parts) > 1:
        out["date"] = parts[1]
    for p in parts[2:]:
        low = p.lower()
        if low.startswith("quality"):
            m = _NUM_RE.search(p)
            if m:
                out["quality"] = float(m.group(1))
        elif low.startswith("difficulty"):
            m = _NUM_RE.search(p)
            if m:
                out["difficulty"] = float(m.group(1))
        elif low.startswith("grade"):
            out["grade"] = p[len("grade"):].strip()
        elif low.startswith("audit"):
            out["grade"] = "Audit/No Grade"
    return out


def _is_rating_line(line: str) -> bool:
    """A review block starts with a line like 'COURSE | date | Quality ...'."""
    return "|" in line and bool(re.match(r"^[A-Za-z]+\s?\d", line.strip()))


def load_and_chunk(raw_dir: Path = RAW_DIR) -> list[Chunk]:
    """Load every raw file, clean it, and split into one chunk per review."""
    chunks: list[Chunk] = []
    files = sorted(raw_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No raw .md files found in {raw_dir}")

    for path in files:
        raw = path.read_text(encoding="utf-8")

        # Split off the `key: value` header (everything before the first '# ' heading).
        header_lines, body_start = [], 0
        lines = raw.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("# "):
                body_start = i + 1
                break
            header_lines.append(line)
        header = _parse_header(header_lines)
        body = "\n".join(lines[body_start:])

        # Reviews are separated by blank lines.
        blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
        review_idx = 0
        for block in blocks:
            block_lines = block.splitlines()
            if not _is_rating_line(block_lines[0]):
                continue  # skip any stray non-review block

            rating = _parse_rating_line(block_lines[0])

            # Everything after the rating line is the comment, plus optional Advice/Tags.
            comment_parts, advice, tags = [], "", ""
            for ln in block_lines[1:]:
                low = ln.lower().strip()
                if low.startswith("advice:"):
                    advice = ln.split(":", 1)[1].strip()
                elif low.startswith("tags:"):
                    tags = ln.split(":", 1)[1].strip()
                else:
                    comment_parts.append(ln.strip())
            comment = clean_text(" ".join(comment_parts))
            if not comment:
                continue  # skip empty reviews (Checkpoint: no empty chunks)

            professor = header.get("professor", "Unknown")
            course = rating["course"]

            # --- Enriched, self-describing chunk text (what gets embedded) ---
            q = rating["quality"]
            d = rating["difficulty"]
            head = f'Review of Professor {professor} (UC Berkeley, {course})'
            bits = []
            if q >= 0:
                bits.append(f"Quality {q}/5")
            if d >= 0:
                bits.append(f"Difficulty {d}/5")
            if rating["grade"]:
                bits.append(f"Grade {rating['grade']}")
            if rating["date"]:
                bits.append(rating["date"])
            if bits:
                head += " — " + ", ".join(bits)
            text = f'{head}:\n"{comment}"'
            if advice:
                text += f"\nAdvice: {advice}"
            if tags:
                text += f"\nTags: {tags}"

            # --- Structured metadata (citation + filtering); all values scalar for Chroma ---
            metadata = {
                "professor": professor,
                "course": course,
                "quality": float(q),
                "difficulty": float(d),
                "grade": rating["grade"] or "N/A",
                "date": rating["date"] or "N/A",
                "tags": tags or "N/A",
                "source_file": path.name,
                "source_url": header.get("source_url", ""),
                "source_type": header.get("source_type", "Rate My Professors"),
                "overall_quality": header.get("overall_quality", "N/A"),
                "would_take_again": header.get("would_take_again", "N/A"),
                "chunk_index": review_idx,  # position of this review within its document
            }
            chunks.append(Chunk(id=f"{path.name}::{review_idx}", text=text, metadata=metadata))
            review_idx += 1

    return chunks


# --------------------------------------------------------------------------- #
# Inspection (Milestone 3 checkpoint)
# --------------------------------------------------------------------------- #
def _inspect(n: int = 5, seed: int = 7) -> None:
    chunks = load_and_chunk()
    docs = sorted({c.metadata["source_file"] for c in chunks})
    lengths = [len(c.text) for c in chunks]

    print(f"Loaded {len(docs)} documents -> {len(chunks)} chunks "
          f"(one chunk per review, overlap 0).")
    print(f"Chunk length chars: min={min(lengths)}, "
          f"mean={sum(lengths)//len(lengths)}, max={max(lengths)}")
    if len(chunks) < 50:
        print("WARNING: <50 chunks — chunks may be too large.")
    elif len(chunks) > 2000:
        print("WARNING: >2000 chunks — chunks may be too small.")
    else:
        print("Chunk count is in the healthy 50–2000 range. ✓")

    print(f"\n--- {n} random chunks (seed={seed}) ---")
    for c in random.Random(seed).sample(chunks, k=min(n, len(chunks))):
        print(f"\n[{c.id}]  course={c.metadata['course']}  "
              f"quality={c.metadata['quality']}  src={c.metadata['source_file']}")
        print(c.text)


if __name__ == "__main__":
    _inspect()
