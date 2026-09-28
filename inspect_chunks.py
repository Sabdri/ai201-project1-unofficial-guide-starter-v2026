#!/usr/bin/env python3
"""
Print the chunks retrieval actually returns, in full, for every test question.

`app.py retrieve` shows a 52-character preview, which is enough to see where a
distance landed and not enough to judge criteria 1 and 4:

  - criterion 1 asks whether a retrieved chunk *contains the answer*
  - criterion 4 asks whether the chunks are *complete thoughts*

Both need the whole chunk text. This prints it. No model calls — retrieval and
the gate are deterministic, so one pass is the whole measurement.

    python inspect_chunks.py > chunks_before.txt
"""

import config
import gate
import questions as qs
from store import search


def show(question: str, top_k: int, threshold: float) -> None:
    results = search(question, top_k=top_k)
    decision = gate.check(results, threshold=threshold)

    print(f"\n{'=' * 78}")
    print(f"Q: {question}")
    print(f"Gate: {decision.explanation}")
    print("=" * 78)

    for rank, r in enumerate(results, 1):
        print(f"\n[{rank}] {r.label}  distance {r.distance:.4f}  "
              f"({len(r.text)} chars, produced by {r.produced_by})")
        print("-" * 78)
        print(r.text)


def main() -> None:
    top_k = config.TOP_K
    threshold = config.THRESHOLD

    print("# Retrieved chunks, in full")
    print(f"\n- Produced by: `inspect_chunks.py::main`")
    print(f"- Retrieval: `store.py::search`, chunks from `chunker.py::split_documents`")
    print(f"- Corpus: `{config.CORPUS}` · top-k: {top_k} · cutoff: {threshold}")

    print(f"\n\n{'#' * 78}\n# TEST QUESTIONS\n{'#' * 78}")
    for item in qs.answered():
        show(item["question"], top_k, threshold)
        print(f"\nexpects: {item.get('expects', '')!r}")

    print(f"\n\n{'#' * 78}\n# OUT OF SCOPE (the gate should refuse all five)\n{'#' * 78}")
    for question in qs.OUT_OF_SCOPE:
        results = search(question, top_k=top_k)
        decision = gate.check(results, threshold=threshold)
        verdict = "refused" if not decision.passed else "LET THROUGH"
        nearest = results[0].label if results else "none"
        print(f"{verdict:<12} best distance {decision.best_distance:.4f}  "
              f"nearest {nearest:<34} {question}")


if __name__ == "__main__":
    main()
