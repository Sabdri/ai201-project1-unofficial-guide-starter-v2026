"""
Decides whether one answer is correct, for run_eval.py's per-question table.

This is criterion 5 under its ORIGINAL wording in criteria.md: the answer has
to contain the question's `expects` string, case-insensitive substring match.
No fuzzy matching — "show as a W" does not count for "shows as a W". The point
is that the number is the same every time someone scores it.

score_runs.py uses the same helpers to score all five criteria from a run log.
"""

import re

HEADING_END = re.compile(r"[.!?:;)\"'”’]\s*$")


def contains(text: str, phrase: str) -> bool:
    return bool(phrase) and phrase.lower() in text.lower()


def names_source(answer: str) -> bool:
    """Criterion 2: the answer names at least one document filename."""
    return ".txt" in answer


def is_fragment(chunk_text: str) -> bool:
    """Criterion 4: a chunk with no sentence-ending punctuation is a heading
    or a cut-off line, not a complete thought."""
    return not HEADING_END.search(chunk_text.strip())


def judge(question, expects, answer, results) -> bool:
    return contains(answer, expects)
