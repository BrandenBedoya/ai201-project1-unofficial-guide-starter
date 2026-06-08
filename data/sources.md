# Source Manifest — The Unofficial Guide

**Domain:** Student reviews of UC Berkeley Computer Science / EECS professors and courses.
**Source used:** Rate My Professors (publicly visible student reviews).
**Collected:** 2026-06-08 via automated page fetch; raw text saved under `data/raw/`.

These 11 professor pages were chosen for **coverage and contrast**, not just volume —
they span beloved instructors, widely-disliked ones, and genuinely divisive cases, across
many core CS/EECS courses (CS10, CS61A, CS61B, CS164, CS170, CS182, CS184, CS188, CS189, DATA8, DATA144).
That spread is what lets the system answer comparison questions ("who should I take for 61A?")
rather than just look up one professor.

| # | Professor | Courses | Overall | Would take again | Raw file | URL |
|---|-----------|---------|---------|------------------|----------|-----|
| 1 | John DeNero | CS61A, DATA8 | 4.4/5 | 85% | `data/raw/rmp_denero.md` | https://www.ratemyprofessors.com/professor/1621181 |
| 2 | Jonathan Shewchuk | CS61B, CS189, CS274 | 4.7/5 | 98% | `data/raw/rmp_shewchuk.md` | https://www.ratemyprofessors.com/professor/246561 |
| 3 | John Wright | CS170 | 4.6/5 | 90% | `data/raw/rmp_wright.md` | https://www.ratemyprofessors.com/professor/2903387 |
| 4 | Daniel Klein | CS188 | 4.7/5 | 100% | `data/raw/rmp_klein.md` | https://www.ratemyprofessors.com/professor/814582 |
| 5 | John Canny | CS188, CS182, CS194, CS160 | 1.3/5 | 20% | `data/raw/rmp_canny.md` | https://www.ratemyprofessors.com/professor/597026 |
| 6 | Zachary Pardos | DATA144 | 1.6/5 | 16% | `data/raw/rmp_pardos.md` | https://www.ratemyprofessors.com/professor/2971156 |
| 7 | Sarah Chasins | CS164 | 2.7/5 | 29% | `data/raw/rmp_chasins.md` | https://www.ratemyprofessors.com/professor/2907404 |
| 8 | Dan Garcia | CS61A, CS10 | 3.7/5 | 66% | `data/raw/rmp_garcia.md` | https://www.ratemyprofessors.com/professor/142865 |
| 9 | James O'Brien | CS184 | 3.9/5 | 100% | `data/raw/rmp_obrien.md` | https://www.ratemyprofessors.com/professor/558845 |
| 10 | Pamela Fox | CS61A | 4.2/5 | 73% | `data/raw/rmp_fox.md` | https://www.ratemyprofessors.com/professor/2701686 |
| 11 | Peyrin Kao | CS61B, CS161, CS188 | 4.9/5 | 98% | `data/raw/rmp_kao.md` | https://www.ratemyprofessors.com/professor/2804069 |

## Collection notes & honesty caveats
- **Sampling:** Each raw file holds a sample of recent reviews (~5 per professor), not the full
  rating history. The page fetcher returns the most recent/visible reviews. This is enough for a
  demo corpus but means the system reflects a *slice* of opinion, not a statistically complete one.
- **Truncation:** A few longer comments (notably John Canny's) were shortened by the fetch step.
  Flagged here so it can be revisited in the Milestone 2 ingestion pipeline.
- **Single source type:** All documents are Rate My Professors reviews. Reddit (r/berkeley) was the
  intended second source for long-form threads, but it is not fetchable in this environment.
  Adding long-form Reddit/forum threads is logged as a future expansion in `planning.md`.
- **Ethics:** Public, student-authored reviews collected in small volume for an educational class
  project. No login-gated or private content was accessed.
