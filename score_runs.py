#!/usr/bin/env python3
"""
Score a run log against all five criteria in criteria.md, one number per run.

    python score_runs.py results/run_..._before.md
    python score_runs.py results/run_..._after.md --variant merged

Criteria 2 and 5 are read from the answers in the log. Criteria 1 and 4 come
from retrieval, re-run live against the index the log was made from (retrieval
is deterministic, so this reproduces what the run saw). Criterion 3 is read
from the gate table in the log.
"""

import argparse
import re
from pathlib import Path

import questions as qs
import scorer

TOP_K_FOR_C4 = 3


def parse_log(path: Path):
    text = path.read_text(encoding="utf-8")
    answers = {}  # (question, run) -> answer
    for m in re.finditer(r"^### (.+?) — run (\d+)\n.*?```\n(.*?)\n```", text, re.S | re.M):
        answers[(m.group(1), int(m.group(2)))] = m.group(3)
    refused = len(re.findall(r"\| refused \|", text))
    gate_total = len(re.findall(r"\| (?:refused|\*\*let through\*\*) \|", text))
    return answers, refused, gate_total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--variant", default="default")
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()

    from store import search

    answers, refused, gate_total = parse_log(Path(args.log))
    items = qs.answered()
    runs = sorted({r for (_, r) in answers})
    n = len(items)

    c1 = c4 = 0
    for item in items:
        results = search(item["question"], top_k=args.top_k, variant=args.variant)
        fact = item.get("expects_revised", item["expects"])
        hit = any(scorer.contains(r.text, fact) for r in results)
        frags = [r.text for r in results[:TOP_K_FOR_C4] if scorer.is_fragment(r.text)]
        c1 += hit
        c4 += not frags
        print(f"- {item['question']}\n    C1 answer in top-{args.top_k}: {hit}"
              f"   C4 fragments in top-{TOP_K_FOR_C4}: {frags or 'none'}")

    rows = {k: [] for k in ("c1", "c2", "c3", "c4", "c5", "c5r")}
    for run in runs:
        got = [answers.get((i["question"], run), "") for i in items]
        rows["c1"].append(c1)
        rows["c2"].append(sum(scorer.names_source(a) for a in got))
        rows["c3"].append(refused)
        rows["c4"].append(c4)
        rows["c5"].append(sum(scorer.contains(a, i["expects"]) for a, i in zip(got, items)))
        rows["c5r"].append(sum(scorer.contains(a, i.get("expects_revised", i["expects"]))
                               for a, i in zip(got, items)))
        for a, i in zip(got, items):
            if not scorer.contains(a, i["expects"]):
                print(f"    run {run} C5 miss ({i['expects']!r}): {a[:90]!r}")

    names = {
        "c1": "1. Retrieved chunk contains the answer",
        "c2": "2. Every answer names a source",
        "c3": "3. Gate stops out-of-corpus questions",
        "c4": "4. Complete thought chunks",
        "c5": "5. Answer matches expected keywords (original)",
        "c5r": "5. Answer matches expected keywords (revised)",
    }
    print(f"\n| Criterion | {' | '.join(f'Run {r}' for r in runs)} |")
    for k, label in names.items():
        total = gate_total if k == "c3" else n
        print(f"| {label} | {' | '.join(f'{v}/{total}' for v in rows[k])} |")


if __name__ == "__main__":
    main()
