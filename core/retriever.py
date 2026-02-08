"""
RAG retriever for enrichment of LLM prompts.

The retriever loads documents from JSON files in the configured index
directory.  Documents must contain at least `content` and `source` fields.
Retrieval is a simple keyword match and rank on small datasets; for
production usage you can swap the indexer with a vector database like
Chroma, Faiss or Weaviate【270526541516335†L469-L480】.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Load and query a document store for relevant context."""

    def __init__(self, index_dir: str = "rag/domain_indices") -> None:
        self.index_dir = Path(index_dir)
        self.documents: List[Dict[str, Any]] = []
        self._load_indices()

    def _load_indices(self) -> None:
        if not self.index_dir.exists():
            return
        for index_file in self.index_dir.glob("*.json"):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                    if isinstance(docs, list):
                        self.documents.extend(docs)
            except Exception as exc:
                logger.warning(f"Failed to load index {index_file}: {exc}")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve the top‑k most relevant documents based on keyword overlap.

        Parameters
        ----------
        query : str
            The user question or requirement.
        top_k : int
            Number of results to return.

        Returns
        -------
        List[dict]
            A list of document dictionaries with keys `content` and `source`.
        """
        if not query or not self.documents:
            return []
        q_terms = {t.lower() for t in query.split()}
        scored: List[tuple[int, Dict[str, Any]]] = []
        for doc in self.documents:
            content = doc.get("content", "").lower()
            score = sum(1 for term in q_terms if term in content)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]
