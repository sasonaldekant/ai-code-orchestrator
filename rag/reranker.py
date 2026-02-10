"""
Reranker Module for AI Code Orchestrator v4.0

This module implements a Cross-Encoder reranking strategy to improve retrieval precision.
It re-scores the initial candidates from the vector store using a more accurate model.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Lazy load to avoid crashes on incompatible environments
HAS_SENTENCE_TRANSFORMERS = True

@dataclass
class RerankedResult:
    """A document that has been rescored by the re-ranker."""
    document_id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    original_score: Optional[float] = None

class CrossEncoderReranker:
    """
    Reranks retrieval results using a Cross-Encoder model.
    
    Cross-Encoders process (Query, Document) pairs together, allowing for full
    self-attention between the query and the document, resulting in higher accuracy
    than bi-encoder vector similarity.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Lazy loading to avoid startup overhead if not used
                from sentence_transformers import CrossEncoder 
                self.model = CrossEncoder(model_name, device=device)
                logger.info(f"Loaded Cross-Encoder model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load Cross-Encoder model (likely environment issue): {e}")
                self.model = None
        
    def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[RerankedResult]:
        """
        Rerank a list of documents based on their relevance to the query.
        
        Args:
            query: The search query.
            documents: List of dicts with 'id', 'text', 'metadata', and optional 'score'.
            top_k: Number of top results to return.
            
        Returns:
            List of RerankedResult objects sorted by score (descending).
        """
        if not documents:
            return []
            
        if not self.model:
            logger.warning("Reranker model not active. Returning original order.")
            # Fallback: just return as RerankedResult
            results = [
                RerankedResult(
                    document_id=doc.get("id"),
                    text=doc.get("text", ""),
                    metadata=doc.get("metadata", {}),
                    score=doc.get("score", 0.0),
                    original_score=doc.get("score")
                ) for doc in documents
            ]
            return results[:top_k]
            
        # Prepare pairs for the model: [(query, doc_text), ...]
        doc_texts = [doc.get("text", "") for doc in documents]
        pairs = [[query, doc_text] for doc_text in doc_texts]
        
        try:
            # Predict scores
            scores = self.model.predict(pairs)
            
            # Combine results
            ranked_results = []
            for i, doc in enumerate(documents):
                ranked_results.append(RerankedResult(
                    document_id=doc.get("id"),
                    text=doc.get("text", ""),
                    metadata=doc.get("metadata", {}),
                    score=float(scores[i]),
                    original_score=doc.get("score")
                ))
            
            # Sort by score descending
            ranked_results.sort(key=lambda x: x.score, reverse=True)
            
            # Return top_k
            return ranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return [
                RerankedResult(
                    document_id=doc.get("id"),
                    text=doc.get("text", ""),
                    metadata=doc.get("metadata", {}),
                    score=doc.get("score", 0.0)
                ) for doc in documents
            ][:top_k]
