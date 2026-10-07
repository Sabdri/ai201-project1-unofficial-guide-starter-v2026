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

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — produced by: `chunker.py::split_documents`

```
Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_phys_130_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#1` — produced by: `chunker.py::split_documents`

```
Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#1` — produced by: `chunker.py::split_documents`

```
The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

## Sample Answer

**Question:** How are juniors and seniors ordered in the housing lottery?

**Answer:**

```
Juniors and seniors are ordered by accumulated credit hours first, with ties broken randomly. 

Source: admin_housing_lottery.txt
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
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 |MET|
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 |MET|
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 |MET|
| 4. Complete thought chunks | 4 of 5 | 3/5 | 3/5 | 3/5 |MISSED|
| 5. Answer matches expected keywords | 4 of 5 | 3/5 | 3/5 | 3/5 |MISSED|

Criteria 1, 3 and 4 measure retrieval and chunking, which are deterministic —
best distances and retrieved source lists were byte-identical across all three
runs, so each of those criteria has one number that goes in all three columns.
Criteria 2 and 5 depend on generated text and were read run by run.

### Real output

**Criterion 2 — every answer names a source.** From `run_eval.py::main`,
generation by `generate.py::answer_from_chunks`, question 1 run 2:

Juniors and seniors are ordered by accumulated credit hours first, with ties broken randomly. 

Source: admin_housing_lottery.txt


**Criterion 3 — the gate.** From `run_eval.py::check_out_of_scope`, cutoff 0.6:

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.799 | refused |
| How do I change the oil in a diesel engine? | 0.850 | refused |
| Who won the 1994 World Cup? | 0.780 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.824 | refused |
| How do I write a for loop in Rust? | 0.831 | refused |

**Criterion 5 — expected keywords.** Question 4 run 3, `generate.py::answer_from_chunks`:

Dropping a class can be done through the end of week six, but dropping after week two will show as a "W" on your transcript (admin_add_drop_deadline.txt and admin_withdrawal_deadline.txt).


## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | **MET** | Inspected chunks confirm the top retrieved result for all 5 questions explicitly contains the required answer text. |
| 2 | Every answer names a source | **MET** | Checked across all runs; every generated response explicitly cites its source file name. |
| 3 | Gate stops out-of-corpus questions | **MET** | All 5 out-of-scope questions generated distances between 0.780 and 0.850, successfully triggering the 0.60 threshold refusal. |
| 4 | Complete thought chunks | **MISSED** | A question passes if none of its top-3 chunks is a fragment (no sentence-ending punctuation). Both housing questions got the title-only chunk "On the housing lottery" at #2, so 3/5. 98 of 271 chunks were title-only. |
| 5 | Answer matches expected keywords | **MISSED** | Case-insensitive substring match against `expects`. "randomly drawn" missed in all 3 runs (model said "drawn at random") and "shows as a W" missed in all 3 (model said "will show as a W"), so 3/5. |


## Diagnoses

**Criterion 4 — stage 2, chunking (`chunker.py::split_documents`).** Splitting on `\n\n` made every document's title line ("On the housing lottery") its own chunk. A title has no sentence in it, but it embeds very close to questions about that topic (distance 0.32), so it takes a top-3 slot from real content.

**Criterion 5 — stage 5, generation (`generate.py::answer_from_chunks`).** The model paraphrases the policy instead of using the document's wording: "will show as a W" instead of "shows as a W". The answer is correct, but the exact phrase is gone. The "randomly drawn" miss is a measurement problem, not a pipeline one. That phrase appears nowhere in the corpus (see the revision in criteria.md).


## The Improvement

**What I changed:**  
In `chunker.py::split_documents`, any paragraph that doesn't end in sentence punctuation (a title line) is now attached to the paragraph below it instead of becoming its own chunk. Indexed as variant `merged`: 271 chunks → 183.

**Why I picked it:**  
It targets the criterion 4 miss directly. The diagnosed failure was title-only chunks taking top-3 slots for both housing questions.


### Run Log — After

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Complete thought chunks | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answer matches expected keywords | 4 of 5 | 3/5 | 3/5 | 3/5 | MISSED |


**Did it help?**  
Yes, for the criterion it targeted. Criterion 4 went from 3/5 to 5/5 in all three runs — "On the housing lottery" no longer appears in either housing question's top 3. Criteria 1–3 stayed at 5/5. Criterion 5 stayed at 3/5 (4/5 under the revised wording) — expected, since that miss is in generation and this change was in chunking.


## What's Still Broken

Criterion 5 is still MISSED on the original wording: the model writes "will show as a W" instead of "shows as a W" in all three runs. That's stage 5, generation, and the chunking fix didn't touch it.


## What I'd Do Differently

Knowing what I know now, I would write stricter keyword criteria or automated assertions in `scorer.py` to enforce uniform citation formatting across all generation runs.

