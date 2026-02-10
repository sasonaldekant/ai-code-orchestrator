
"""
Demo script for Cross-Encoder Reranking
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.reranker import CrossEncoderReranker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("--- 🚀 Demo: Cross-Encoder Reranking ---")
    
    # 1. Initialize Reranker
    reranker = CrossEncoderReranker()
    
    if not reranker.model:
        print("⚠️  Model not loaded (sentence-transformers missing?). Demo will use fallback.")
    
    # 2. Mock Data
    query = "How to handle database connection errors?"
    
    # Simulating retrieval results (mixed relevance)
    # Notice: Document 3 has keywords "database" and "error" but is about syntax, 
    # while Document 1 is semantically perfect. Document 2 is somewhat related.
    documents = [
        {
            "id": "doc1", 
            "text": "Implement a retry logic with exponential backoff when the database pool is exhausted.", 
            "score": 0.85 # Artificial vector score
        },
        {
            "id": "doc2", 
            "text": "Check your connection string credentials in config.yaml.", 
            "score": 0.82
        },
        {
            "id": "doc3", 
            "text": "Syntax errors in SQL queries will cause the database driver to throw an exception.", 
            "score": 0.80
        },
        {
            "id": "doc4", 
            "text": "The frontend UI displays an error banner when the API returns 500.", 
            "score": 0.75
        }
    ]
    
    print(f"\nQUERY: {query}")
    print("\n--- Original Order (Vector Similarity / Mock) ---")
    for doc in documents:
        print(f"[{doc['score']}] {doc['text'][:60]}...")
        
    # 3. Rerank
    print("\n... Re-ranking ...")
    reranked = reranker.rerank(query, documents, top_k=3)
    
    print("\n--- Reranked Order (Cross-Encoder) ---")
    for i, res in enumerate(reranked):
        score_diff = f"({res.score - (res.original_score or 0):+.4f})" if res.original_score else ""
        print(f"{i+1}. [{res.score:.4f}] {score_diff} {res.text[:80]}...")
        
    print("\nDone.")

if __name__ == "__main__":
    main()
