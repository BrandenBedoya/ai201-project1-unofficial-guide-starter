# planning.md — The Unofficial Guide

> Spec-first working document. Each milestone updates this before code is written.

---

## Domain (Milestone 1)

**Domain:** Student reviews of UC Berkeley Computer Science / EECS professors and courses.

**2–3 sentence summary (for README too):**
> Berkeley CS students rely heavily on word-of-mouth to decide *who* to take for a given course —
> the same class can be a great experience or a demoralizing one depending entirely on the instructor.
> That knowledge is real but scattered across hundreds of individual Rate My Professors reviews, semester
> by semester, with no way to ask a plain-language question like "who should I take for 61A?" and get a
> grounded, side-by-side answer. The Unofficial Guide makes that diffuse, contradictory, student-generated
> knowledge searchable and answerable, with citations back to the reviews it drew from.

**Why this knowledge is hard to find otherwise:** The official course catalog tells you a course *exists*;
it never tells you the professor "made the final unreasonably hard and refused to release the distribution,"
or that one instructor is "the GOAT" while another teaching the same number is "not prepared for teaching at all."
That signal only lives in informal student reviews, and it's buried — you'd have to read dozens of reviews
across multiple professor pages and mentally aggregate them. This project does that aggregation.

### 5 questions the system should be able to answer
A domain that can't produce 5 concrete questions is too vague. These also seed the Milestone 6 eval set.
1. *"I'm taking CS61A next semester — which professor should I pick?"* (comparison: DeNero vs. Garcia vs. Fox — and they conflict)
2. *"Are John Canny's classes worth taking?"* (single professor, strongly negative consensus)
3. *"Which professor gives good feedback / is helpful in office hours?"* (cross-cutting, tag-driven: O'Brien)
4. *"Is CS61B hard, and who teaches it well?"* (course difficulty + instructor: Shewchuk, Kao)
5. *"Which professors or classes should I avoid?"* (synthesis across the low-rated set: Canny, Pardos, Chasins)

> Question 1 is deliberately a near-miss trap: the reviews **disagree** about Garcia (same professor, same
> course, ratings of both 1.0 and 4.0). A good answer must surface that disagreement rather than pick one side.
> This is the likely failure case to document in Milestone 6.

---

## Document structure observations (from skimming the corpus)

What I noticed reading the raw reviews, which directly drives chunking (Milestone 2):
- **Each review is short and self-contained** — typically 1–3 sentences, one opinion, one course, one date.
  The key fact is concentrated, not spread across paragraphs. This is the opposite of a long-form guide.
- **Reviews carry structured metadata** — course code, quality, difficulty, grade, date, tags — that is as
  important for answering as the prose ("difficulty 5.0, grade F" matters).
- **Reviews within one professor's page contradict each other** — retrieval must be able to pull *multiple*
  reviews for the same professor so the generator can weigh them, not just the single most similar one.
- **The professor name is the join key** but often appears only in the file header, not in every review line —
  so chunking must keep professor/course identity attached to every chunk (metadata, not just text).

**Initial chunking hypothesis (to finalize in Milestone 2):** one chunk ≈ one review, with the professor +
course + rating metadata attached to each chunk, rather than a fixed character window. Fixed 500-char splitting
would cut across review boundaries and strand a rating from its comment. Small, review-sized chunks fit this
corpus. Overlap is likely unnecessary (reviews are independent), unlike long-form guides where overlap matters.

---

## Sources (Milestone 1)
See [`data/sources.md`](data/sources.md) for the full manifest (11 documents, URLs, ratings, caveats).

---

## Chunking strategy (Milestone 2) — TODO
_Finalize chunk size, overlap, and rationale here before writing the chunker._

## Embedding & vector store (Milestone 3) — TODO
_Record embedding model choice and production tradeoffs here._

## Retrieval + grounded generation (Milestones 4–5) — TODO

## Evaluation design (Milestone 6) — TODO
_5 questions above become the eval set with ground-truth answers._

---

## Stretch feature log
> Update this section *before* starting any stretch feature.

- [ ] Hybrid search (semantic + BM25) — candidate, well-suited since reviews contain exact tokens like course codes ("CS61A") and professor names.
- [ ] Chunking strategy comparison (review-per-chunk vs. fixed-window) — candidate.
- [ ] Metadata filtering (by course, rating, or date) — candidate; metadata is already structured per review.
- [ ] Conversational memory — candidate.
- [ ] **Future source expansion:** add long-form r/berkeley threads / forum posts to contrast short reviews with long-form text (Reddit was not fetchable in the build environment; revisit).
