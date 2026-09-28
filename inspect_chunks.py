import questions as qs
from store import search
import config

def main():
    items = qs.answered()
    for item in items:
        q = item["question"]
        print(f"\n====================\nQUESTION: {q}\n====================")
        results = search(q, top_k=config.TOP_K, corpus=config.CORPUS, variant="default")
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} (Source: {r.source}, Distance: {r.distance:.4f}) ---")
            print(r.text)

if __name__ == "__main__":
    main()