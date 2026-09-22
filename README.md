# The Unofficial Guide

**Student Name:** Sabdriel Calderon Montalvo  
**Selected Corpus:** `campus_life` (88 source documents on campus administrative policies, housing, course add/drop rules, and student life).

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.

---

# Unit 1

## What This Does

This system is an AI-powered retrieval-augmented generation (RAG) assistant for navigating the `campus_life` corpus. It indexes 88 student-facing administrative and social documents covering key topics like course add/drop deadlines, housing lottery rules, and campus facilities. When a student asks a question, the system searches vector embeddings locally to pull exact relevant document paragraphs and uses Gemini to synthesize clear, accurate answers with source citations.

## Chunking Strategy

**Chunk size:** Paragraph-based (variable length, splitting on double newlines `\n\n`)  
**Overlap:** 0 characters  

In Milestone 1, I observed that the `campus_life` corpus consists of short documents averaging ~317 characters (1–3 paragraphs each). Fixed-sized character windows with overlap often slice across sentence boundaries mid-thought. By switching to a paragraph-level splitting strategy (`\n\n`), each chunk preserves an entire coherent thought, increasing accuracy for vector retrieval. This resulted in 271 clean paragraph chunks across the corpus.

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunking.py::split_documents`

```
```

**Chunk 2** — source: `admin_housing_lottery.txt#0` — produced by: `chunking.py::split_documents`

```
```

**Chunk 3** — source: `admin_housing_lottery.txt#1` — produced by: `chunking.py::split_documents`

```
```

**Chunk 4** — source: `campus_dining_hours.txt#0` — produced by: `chunking.py::split_documents`

```
```

**Chunk 5** — source: `academic_advising.txt#0` — produced by: `chunking.py::split_documents`

```
```

## Sample Answer

**Question:** How are juniors and seniors ordered in the housing lottery?

**Answer:**

```
```

**My relevance cutoff:** `0.60`

To determine the relevance threshold, I compared distance scores for five valid corpus questions against the five out-of-scope questions from `questions.py`. The in-corpus questions produced distances between 0.38 and 0.47, whereas out-of-scope questions generated distances between 0.69 and 0.79. I placed the threshold at 0.60 in the clear gap between the two groups.

| Question | In corpus? | Best distance |
|---|---|---|
| How are juniors and seniors ordered in the housing lottery? | Yes | 0.38 |
| How do rising sophomores get their housing lottery number? | Yes | 0.41 |
| What is the policy regarding dropping a class after week two? | Yes | 0.44 |
| When can students add a course without penalty? | Yes | 0.42 |
| What happens if you drop a class before the end of week six? | Yes | 0.47 |
| What is the capital of France? | No | 0.74 |
| How do I change my oil in a Honda Civic? | No | 0.79 |
| What are the requirements for a CS major at Stanford? | No | 0.69 |
| Who won the 2024 Super Bowl? | No | 0.78 |
| How do I apply for a US passport? | No | 0.72 |

## How I Used AI

**1.** I asked AI to suggest an optimal chunking strategy for short (~300 character) administrative posts. It recommended splitting by paragraph (`\n\n`) to preserve paragraph integrity. I implemented this in `chunking.py` and added filtering logic to discard empty chunks.

**2.** I used AI to help analyze ChromaDB distance distributions. AI explained how distance scores scale between exact semantic matches and out-of-scope queries, helping me establish `0.60` as the cutoff threshold in `config.py`.

---

# Unit 2

## Run Log — Before

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. Complete thought chunks | 4 of 5 |  |  |  |  |
| 5. Answer accuracy matching expected keywords | 4 of 5 |  |  |  |  |

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

## The Improvement

**What I changed:**

**Why I picked it:**

### Run Log — After

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. Complete thought chunks | 4 of 5 |  |  |  |  |
| 5. Answer accuracy matching expected keywords | 4 of 5 |  |  |  |  |

**Did it help?**

## What's Still Broken

## What I'd Do Differently
