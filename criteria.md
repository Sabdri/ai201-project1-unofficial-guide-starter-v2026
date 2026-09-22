# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
The `campus_life` corpus contains very focused, single-topic documents (~317 characters on average). Because topics rarely span multiple files, vector similarity should easily retrieve the single matching post for at least 4 out of 5 questions, leaving a 1-question margin for semantic phrasing differences.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Every query in this pipeline is explicitly grounded using prompt instructions that mandate citing source filenames (e.g., `admin_housing_lottery.txt`). Since Gemini receives the document names directly in the retrieved context block, failing to name a source would indicate a complete failure of prompt instruction-following.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

**Why this target:**
With a vector distance cutoff set around 0.60, out-of-scope questions (such as inquiries about unrelated universities or topics not in `campus_life`) typically produce distances above 0.68–0.79, creating a distinct margin between valid context matches and irrelevancies.

---

## 4. Complete thought chunks without sentence fragmentation

For at least 4 of my 5 test questions, the top retrieved chunks represent complete, coherent paragraphs without sentences being cut off mid-thought.

**Why this target:**
Because `campus_life` documents consist of short 1-to-3 paragraph posts, fixed-size character chunking often slices right through mid-sentence boundaries. Setting this target ensures that our custom chunker in Milestone 3 successfully aligns chunk boundaries with natural paragraph endings (`\n\n`).

---

## 5. Answer accuracy matching expected keywords

For at least 4 of my 5 test questions, the final generated answer explicitly includes the key factual detail defined in the test suite's `expects` field (e.g., "credit hours", "shows as a W").

**Why this target:**
Retrieving the correct document is only half the job; the language model must also accurately extract the exact policy detail in its final text rather than summarizing vaguely.

---
<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
