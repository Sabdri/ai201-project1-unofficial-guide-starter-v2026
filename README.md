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

All five produced by `chunker.py::split_documents`, printed by
`python app.py chunks`. Total: 271 chunks from 88 documents, 101 characters on
average (shortest 10, longest 373).

**Chunk 1** — source: `admin_add_drop_deadline.txt#1` (274 chars)

```
You can add a course through the end of the second week. Dropping is a longer
window — through the end of week six — but a drop after week two shows as a W on
your transcript. Nothing anywhere on the registrar's site says this plainly, and
students find out from each other.
```

This is the chunk that answers three of my five test questions. Under the
fallback 800-character chunker it would have been glued to the document title
and whatever followed; as a paragraph it is exactly one policy, stated once.

**Chunk 2** — source: `admin_housing_lottery.txt#1` (373 chars — the longest chunk in the corpus)

```
The housing lottery is not random in the way most people assume. Rising
sophomores get a number drawn at random, but juniors and seniors are ordered by
accumulated credit hours first, and only tie-break randomly. That means a senior
who took summer courses reliably beats a senior who didn't. Numbers come out the
second week of March and selection runs over four evenings.
```

Four sentences that only make sense together — the rule for sophomores is stated
in contrast to the rule for juniors and seniors. Splitting this mid-paragraph
would have separated the two halves of one comparison.

**Chunk 3** — source: `admin_housing_lottery.txt#0` (22 chars)

```
On the housing lottery
```

Included because it shows where this strategy is weak. Every document in the
corpus opens with a title line followed by a blank line, so splitting on `\n\n`
turns each title into its own chunk. This one is 22 characters, carries no
information, and still ranked **second** out of five for two of my test
questions — it occupies a top-k slot a real chunk could have used.

**Chunk 4** — source: `dining_kestrel_commons.txt#1` (249 chars)

```
I'm a junior and I've done this twice now. Wait times: 20 to 25 minutes between
12:15 and 1:00, under 5 minutes before 11:45. The thing worth going for is the
stir-fry station, made to order. The thing to know is that the salad bar wilts
after 1:30.
```

A different document type — a student review rather than an administrative
policy. The paragraph split holds up here too: the times and the recommendation
stay in one piece.

**Chunk 5** — source: `housing_morrow_house.txt#4` (119 chars)

```
Laundry costs $1.50 wash, $1.25 dry, coin or card. On noise: loud until about
1am on weekends, no enforced quiet hours.
```

A short paragraph that stays whole. Most chunks in this corpus look like this —
the 101-character average is closer to typical than either of the long examples
above.

> Note: `app.py chunks` prints the `produced_by` field as
> `chunking.py::split_documents`, but the file is `chunker.py`. The string
> literal in [chunker.py](chunker.py) has a typo; the function named above is
> the one that actually ran.

## Sample Answer

**Question:** How are juniors and seniors ordered in the housing lottery?

Real output from run 1, produced by `generate.py::answer_from_chunks` and logged
in `results/run_2026-09-28_1729_before.md`. Best distance 0.2343, passed the
gate. Sources retrieved: `admin_housing_lottery.txt`, `housing_aldridge_hall.txt`,
`housing_innisfree_hall.txt`, `housing_morrow_house.txt`.

**Answer:**

```
Juniors and seniors are ordered by accumulated credit hours first, with ties
broken randomly.

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

Evidence: `results/run_2026-09-28_1729_before.md` (3 runs × 5 questions, caching
off, produced by `run_eval.py::main`) and `chunks_before.txt` (retrieval only,
produced by `inspect_chunks.py::main`).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Complete thought chunks | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answer accuracy matching expected keywords | 4 of 5 | 3/5 | 3/5 | 3/5 | MISSED |

Criteria 1, 3 and 4 are identical across the three columns because they are
measured on retrieval and the gate, which are deterministic — the same question
returns the same chunks at the same distances every time. Criteria 2 and 5 are
measured on generated text, which did vary run to run (the wording of every
answer changed); the counts happened to land in the same place each time.

### Evidence

**Criterion 1 — retrieved chunk contains the answer. 5/5.**

Produced by `store.py::search`, printed by `inspect_chunks.py::main`. For each
question, the rank-1 chunk with the answer sentence in it:

```
Q: How are juniors and seniors ordered in the housing lottery?
[1] admin_housing_lottery.txt#1  distance 0.2343
The housing lottery is not random in the way most people assume. Rising
sophomores get a number drawn at random, but juniors and seniors are ordered by
accumulated credit hours first, and only tie-break randomly. That means a senior
who took summer courses reliably beats a senior who didn't. Numbers come out the
second week of March and selection runs over four evenings.

Q: How do rising sophomores get their housing lottery number?
[1] admin_housing_lottery.txt#1  distance 0.1743
  (same chunk as above — "Rising sophomores get a number drawn at random")

Q: What is the policy regarding dropping a class after week two?
[1] admin_add_drop_deadline.txt#1  distance 0.3719
You can add a course through the end of the second week. Dropping is a longer
window — through the end of week six — but a drop after week two shows as a W on
your transcript. Nothing anywhere on the registrar's site says this plainly, and
students find out from each other.

Q: When can students add a course without penalty?
[1] admin_add_drop_deadline.txt#1  distance 0.4397
  (same chunk — "You can add a course through the end of the second week")

Q: What happens if you drop a class before the end of week six?
[1] admin_add_drop_deadline.txt#1  distance 0.3425
  (same chunk — "Dropping is a longer window — through the end of week six")
```

**Criterion 2 — every answer names a source. 5/5 on every run.**

Produced by `generate.py::answer_from_chunks`, logged by `run_eval.py::main`.
All fifteen answers (5 questions × 3 runs) name a `.txt` file. Three of them,
showing that the citation survives all three wording styles the model used:

```
run 1: Juniors and seniors are ordered by accumulated credit hours first, with
       ties broken randomly.

       Source: admin_housing_lottery.txt

run 2: Juniors and seniors are ordered by accumulated credit hours first, with a
       random tie-break used only when necessary (from admin_housing_lottery.txt).

run 3: Rising sophomores get their housing lottery number drawn at random.

       Source: `admin_housing_lottery.txt`
```

**Criterion 3 — gate stops out-of-corpus questions. 5 of 5 refused.**

Produced by `run_eval.py::check_out_of_scope`, gate logic in `gate.py::check`,
cutoff 0.6. One deterministic pass, so the number is the same in all three
columns above.

```
| Out-of-scope question                              | Best distance | Gate    |
| What is the capital of Mongolia?                   | 0.799         | refused |
| How do I change the oil in a diesel engine?        | 0.850         | refused |
| Who won the 1994 World Cup?                        | 0.780         | refused |
| What is the recommended dosage of ibuprofen...?    | 0.824         | refused |
| How do I write a for loop in Rust?                 | 0.831         | refused |
```

The closest any out-of-scope question came was 0.780, and the furthest any real
question came was 0.4397. The gap between the two groups is 0.34 wide and the
0.6 cutoff sits inside it, so no out-of-scope question is anywhere near getting
through.

**Criterion 4 — complete thought chunks. 5/5.**

Judged on the chunk text in `chunks_before.txt`, produced by
`chunker.py::split_documents`. Rule I applied: a question passes if no chunk
boundary in its retrieved set falls inside a sentence. Paragraph splitting on
`\n\n` means every chunk begins at a capital letter and ends at a terminal
period — I checked all 25 retrieved chunks and found no mid-sentence cut.

```
[1] admin_add_drop_deadline.txt#1  distance 0.3719  (274 chars)
You can add a course through the end of the second week. Dropping is a longer
window — through the end of week six — but a drop after week two shows as a W on
your transcript. Nothing anywhere on the registrar's site says this plainly, and
students find out from each other.
```

One thing this criterion does not catch, which I want on the record before
Milestone 3: the chunker also emits document title lines as their own chunks.

```
[2] admin_housing_lottery.txt#0  distance 0.3207  (22 chars)
On the housing lottery
```

That is a complete line and not a cut sentence, so it passes the criterion as
written, but it is a 22-character chunk carrying no information that retrieval
ranked second for two of my five questions — it takes a top-k slot that a real
chunk could have had.

**Criterion 5 — answer contains the expected keyword. 3/5 on every run. MISSED.**

Rule I applied: case-insensitive substring search for the question's `expects`
string from `questions.py` in the answer text. Q1, Q4 and Q5 pass on all three
runs. Q2 and Q3 fail on all three runs — and both failures are wording, not
facts. The system got the answer right every time:

```
Q2  expects: "randomly drawn"
    run 1: "Rising sophomores get a number drawn at random for the housing lottery."
    run 2: "Rising sophomores get their housing lottery number drawn at random."
    run 3: "Rising sophomores get their housing lottery number drawn at random."
    -> the fact is correct; "drawn at random" is not the substring "randomly drawn"

Q3  expects: "shows as a W"
    run 1: "...dropping after week two will show as a \"W\" on your transcript"
    run 2: "...but it shows as a \"W\" on your transcript"
    run 3: "...dropping after week two will show as a W on your transcript."
    -> run 2 misses on the quote marks around W alone; runs 1 and 3 on "show" vs "shows"
```

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET (5/5, target 4/5) | Read all 25 retrieved chunks in `chunks_before.txt` and checked whether any of them states the answer outright. All five questions had it in the rank-1 chunk, at distances 0.17–0.44. Two documents carry all five answers, so this is an easy corpus for retrieval, not a strong retriever. |
| 2 | Every answer names a source | MET (5/5, target 5/5) | Regex `[a-z0-9_]+\.txt` over all fifteen answer texts in `results/run_2026-09-28_1729_before.md`. Fifteen of fifteen matched. The model used three different citation formats across runs (`Source: x.txt`, `(from x.txt)`, backticked) and named a file in every one. |
| 3 | Gate stops out-of-corpus questions | MET (5/5, target 4/5) | `run_eval.py::check_out_of_scope` put all five `OUT_OF_SCOPE` questions through `gate.py::check` at cutoff 0.6. All five refused. Measured once, not three times: retrieval is deterministic and the gate is a numeric comparison, so there is nothing for a second run to change. |
| 4 | Complete thought chunks | MET (5/5, target 4/5) | Rule: a question passes if no chunk boundary in its retrieved set falls inside a sentence. Checked all 25 chunks by reading them — every one starts at a capital and ends at a terminal period, because `chunker.py::split_documents` splits on `\n\n`. Worth noting the criterion was already satisfied before unit 2 began, since the paragraph chunker was written in unit 1. |
| 5 | Answer accuracy matching expected keywords | MISSED (3/5, target 4/5) | Rule: case-insensitive substring search for each question's `expects` string in the answer. Q2 and Q3 failed on all three runs. I picked substring matching because it is the only version of this criterion I can apply identically three times — but both failures are the answer using different words for a fact it got right, so the miss is in how I wrote the criterion, not in what the system did. |

## Diagnoses

One criterion missed: **criterion 5**, at 3/5 against a target of 4/5, on all
three runs. Two questions failed it, and they failed for different reasons at
different stages. Neither is a retrieval failure.

### Q2 — "How do rising sophomores get their housing lottery number?"

**Stage: none. This is a measurement defect, not a pipeline failure.**

The `expects` string is `"randomly drawn"`. That phrase does not appear anywhere
in the corpus:

```
$ grep -ric "randomly drawn" corpora/campus_life/documents/
(no matches in any of the 88 documents)
```

The source document says *"Rising sophomores get a number drawn at random."* So
a correct, faithfully grounded answer can only contain `"randomly drawn"` if the
model spontaneously reverses the source's word order. The system did the right
thing on all three runs — retrieved the right chunk at distance 0.1743, stated
the fact correctly — and my criterion scored it as a failure every time.

No change to loading, chunking, embedding, retrieval or generation can fix this.
The test is wrong, not the system.

The revision is recorded in `criteria.md` underneath the original. It does
**not** rescore this run: the Run Log — Before above stays at 3/5 MISSED under
the criterion as I originally wrote it. Applying the fix backwards would erase
my own miss, which is the one thing the unit brief says a revision must never
do. The revised wording takes effect from the after-run onward, and I report the
after-run under both yardsticks so the improvement can be told apart from the
revision.

### Q3 — "What is the policy regarding dropping a class after week two?"

**Stage: generation. Mechanism: the model re-voices source text instead of
quoting it, and nothing in the prompt asks it not to.**

Here the `expects` string *does* appear verbatim in the corpus:

```
$ grep -rin "shows as a w" corpora/campus_life/documents/
admin_add_drop_deadline.txt:3: ...but a drop after week two shows as a W on
your transcript.
```

Retrieval put that exact chunk at rank 1, distance 0.3719, on every run. The
answer text was right every time. But the phrase came back rewritten:

```
run 1: "...dropping after week two will show as a \"W\" on your transcript"
run 2: "...but it shows as a \"W\" on your transcript"
run 3: "...dropping after week two will show as a W on your transcript."
```

Run 2 is the sharpest version of the problem: it has the words `shows as a`
followed immediately by `W`, and misses the substring on the quotation marks the
model added. Runs 1 and 3 miss on verb inflection — `show` where the source says
`shows`. Three runs, three different rewrites of one sentence that was already
correct.

The cause is in the grounding prompt, [generate.py:297](generate.py#L297):

```
f"Answer using only the documents above, and name the file you used."
```

It constrains *which* documents the answer may come from and requires a
citation. It says nothing about preserving the source's wording, so the model
paraphrases freely — which is normally desirable and is exactly what costs me
this criterion.

### The pattern

Both misses have the same shape: **the system produced a factually correct,
correctly-cited, correctly-retrieved answer, and my scoring string didn't appear
in it.** Zero of my misses are retrieval failures. Retrieval put the answer in
the rank-1 chunk for 5 of 5 questions, at distances between 0.17 and 0.44.

The shared root cause is that I wrote my `expects` strings as *paraphrases of
facts I had in my head* rather than as *phrases that appear in the documents*. I
wrote them in unit 1, before I had read the corpus closely, which is why one of
them describes text that does not exist. Criterion 5 is therefore measuring two
things at once without distinguishing them: whether the answer is correct, and
whether the model happened to choose my words for it.

### Were my targets set low?

Yes, and the brief asks me to say so plainly rather than take the 4-of-5 as a
result. Three of the four criteria I met were not capable of failing:

**Criterion 1 (5/5, target 4/5) — the test is too easy.** All five of my
questions resolve to just two chunks out of 271:

```
$ grep -E '^\[1\]' chunks_before.txt | awk '{print $2}' | sort | uniq -c
   3 admin_add_drop_deadline.txt#1
   2 admin_housing_lottery.txt#1
```

Two documents out of 88 carry every answer I test for. Three of my five
questions are near-paraphrases of each other about add/drop dates. I would
tighten this by requiring the five questions to draw on at least four different
source documents, which would test retrieval instead of testing whether two
well-written paragraphs are findable.

**Criterion 4 (5/5, target 4/5) — it could not have failed.** It asks whether
chunks are cut mid-sentence. `chunker.py::split_documents` splits on `\n\n`, so
by construction no chunk ever ends mid-sentence. I wrote the paragraph chunker
in unit 1 and then wrote a criterion in unit 2 that tests the decision I had
already made. I would tighten it to something the current chunker actually
fails: *no retrieved chunk is a bare document title.* Today that fails, because
`admin_housing_lottery.txt#0` is the 22-character chunk `On the housing lottery`
and it ranked second for two of my five questions.

**Criterion 3 (5/5, target 4/5) — safe, but legitimately so.** The gap between
the furthest in-corpus question (0.4397) and the nearest out-of-scope one
(0.7803) is 0.34 wide with the cutoff at 0.6. There is no realistic wording of
this criterion my system would have missed. I am leaving it as written, because
unlike criterion 4 it is testing something that could genuinely have gone wrong
— it just didn't.

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
