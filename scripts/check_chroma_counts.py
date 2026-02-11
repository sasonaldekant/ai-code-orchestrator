import chromadb
from pathlib import Path

def check_counts():
    persist_dir = "rag/chroma_db"
    client = chromadb.PersistentClient(path=persist_dir)
    
    collections = client.list_collections()
    print(f"Found {len(collections)} collections:")
    for col in collections:
        count = col.count()
        print(f" - {col.name}: {count} documents")
        if col.name == "pos_component_library":
            # Peek at some documents to see what's in there
            results = col.get(limit=100)
            seen_components = set()
            for meta in results.get("metadatas", []):
                if meta and "component" in meta:
                    seen_components.add(meta["component"])
            print(f"   Unique components found in first 100 docs: {len(seen_components)}")
            print(f"   Names: {sorted(list(seen_components))}")

if __name__ == "__main__":
    check_counts()
