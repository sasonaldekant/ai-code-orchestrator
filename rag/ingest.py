from pathlib import Path
from .embeddings_store import EmbeddingStore

def ingest_dir(src_dir: str, store_path: str):
    src = Path(src_dir)
    store = EmbeddingStore(Path(store_path))
    for p in src.rglob("*.md"):
        store.add(id=p.stem, text=p.read_text(encoding="utf-8"))
    store.save()

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="directory with .md files")
    ap.add_argument("--store", required=True, help="output store path (json)")
    args = ap.parse_args()
    ingest_dir(args.src, args.store)
    print("Ingest done.")
