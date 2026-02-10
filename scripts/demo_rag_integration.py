
"""
Demo script for RAG Integration with Re-ranking
"""
import sys
import os
import shutil
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.vector_store import ChromaVectorStore, Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_DB_DIR = "rag/test_chroma_rerank"

def main():
    print("--- 🚀 Demo: RAG Integration (Chroma + Cross-Encoder) ---")
    
    # 0. Cleanup previous test run
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)

    # 1. Initialize Vector Store
    # Note: We rely on default embeddings (SentenceTransformer/all-MiniLM-L6-v2) handled by Chroma/Utils
    store = ChromaVectorStore(
        collection_name="test_reranking",
        persist_directory=TEST_DB_DIR
    )
    
    # 2. Add Documents (Mix of relevant and keyword-heavy distractors)
    docs = [
        Document(id="1", text="Python uses 'def' to define functions.", metadata={"topic": "python"}),
        Document(id="2", text="In Python, indentation is significant and determines scope.", metadata={"topic": "python"}),
        Document(id="3", text="The 'definition' of a good function is clarity.", metadata={"topic": "general"}), # Keyword match "definition" -> "def"
        Document(id="4", text="To define a variable in Java, use 'int x = 10;'", metadata={"topic": "java"}),   # Keyword match "define"
        Document(id="5", text="Functions are first-class citizens in Python.", metadata={"topic": "python"}),
    ]
    
    print(f"\nAdding {len(docs)} documents...")
    store.add_documents(docs)
    
    query = "How to define a function in Python?"
    print(f"\nQUERY: '{query}'")
    
    # 3. Search WITHOUT Re-ranking
    print("\n--- 1. Standard Search (Cosine Similarity) ---")
    results_std = store.search(query, top_k=3, use_reranking=False)
    for res in results_std:
        print(f"[{res.score:.4f}] {res.document.text}")
        
    # 4. Search WITH Re-ranking
    print("\n--- 2. Advanced Search (Re-ranking) ---")
    results_rerank = store.search(query, top_k=3, use_reranking=True)
    for res in results_rerank:
        print(f"[{res.score:.4f}] {res.document.text}")
        
    # 5. Cleanup
    # store.delete_collection()
    # shutil.rmtree(TEST_DB_DIR)
    print("\nDone.")

if __name__ == "__main__":
    main()
