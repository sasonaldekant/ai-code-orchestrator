from pathlib import Path
from .embeddings_store import EmbeddingStore

def ask(store_path: str, question: str, k: int = 3):
    store = EmbeddingStore(Path(store_path))
    return store.query(question, k=k)

if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--q", required=True)
    ap.add_argument("--k", type=int, default=3)
    args = ap.parse_args()
    res = ask(args.store, args.q, k=args.k)
    print(json.dumps(res, indent=2, ensure_ascii=False))
