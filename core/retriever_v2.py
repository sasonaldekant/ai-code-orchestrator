"""
Enhanced RAG retriever with vector database integration.

Provides semantic search using ChromaDB with sentence transformers,
hybrid search combining keyword and semantic retrieval, and
advanced filtering capabilities.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

from utils.document_chunker import DocumentChunker, Chunk

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from retrieval operation."""
    
    content: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str


class EnhancedRAGRetriever:
    """
    Advanced RAG retriever with vector database and hybrid search.
    
    Features:
    - Semantic search using sentence transformers
    - Keyword-based search for exact matches
    - Hybrid search combining both approaches
    - Metadata filtering
    - Configurable chunking strategies
    """

    def __init__(
        self,
        collection_name: str = "code_docs",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ) -> None:
        """
        Initialize the enhanced retriever.
        
        Parameters
        ----------
        collection_name : str
            Name of the ChromaDB collection.
        persist_directory : str
            Directory to persist the vector database.
        embedding_model : str
            Sentence transformer model for embeddings.
        chunk_size : int
            Target chunk size in tokens.
        chunk_overlap : int
            Overlap between chunks in tokens.
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        
        # Initialize chunker
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
        logger.info(
            f"Initialized EnhancedRAGRetriever with collection '{collection_name}' "
            f"at {persist_directory}"
        )

    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any] | None = None,
        doc_id: str | None = None,
        chunking_strategy: Literal["code", "markdown", "text"] = "text",
    ) -> int:
        """
        Add a document to the vector database.
        
        Parameters
        ----------
        content : str
            Document content to add.
        metadata : dict, optional
            Metadata to attach to the document.
        doc_id : str, optional
            Unique identifier for the document.
        chunking_strategy : str
            Strategy to use for chunking: 'code', 'markdown', or 'text'.
            
        Returns
        -------
        int
            Number of chunks created from the document.
        """
        if metadata is None:
            metadata = {}
        
        if doc_id is None:
            doc_id = f"doc_{uuid4().hex}"
        metadata["doc_id"] = doc_id
        
        # Chunk the document
        chunks = self.chunker.chunk_document(
            content=content,
            metadata=metadata,
            strategy=chunking_strategy,
        )
        
        if not chunks:
            logger.warning("No chunks created from document")
            return 0
        
        # Prepare data for ChromaDB
        ids = [f"{doc_id}_{chunk.chunk_id}" for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        
        logger.info(f"Added document with {len(chunks)} chunks to collection")
        return len(chunks)

    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]],
        chunking_strategy: Literal["code", "markdown", "text"] = "text",
    ) -> int:
        """
        Add multiple documents in batch.
        
        Parameters
        ----------
        documents : List[dict]
            List of documents, each with 'content', 'metadata', and optional 'id'.
        chunking_strategy : str
            Chunking strategy to use.
            
        Returns
        -------
        int
            Total number of chunks created.
        """
        total_chunks = 0
        
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            doc_id = doc.get("id")
            
            chunks_count = self.add_document(
                content=content,
                metadata=metadata,
                doc_id=doc_id,
                chunking_strategy=chunking_strategy,
            )
            total_chunks += chunks_count
        
        return total_chunks

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] | None = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents using semantic search.
        
        Parameters
        ----------
        query : str
            Search query.
        top_k : int
            Number of results to return.
        filter_metadata : dict, optional
            Metadata filters to apply.
            
        Returns
        -------
        List[RetrievalResult]
            Retrieved documents with scores.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata,
        )
        
        return self._format_results(results)

    def hybrid_retrieve(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        filter_metadata: Dict[str, Any] | None = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve using hybrid search (semantic + keyword).
        
        Combines semantic similarity with keyword matching for better results.
        
        Parameters
        ----------
        query : str
            Search query.
        top_k : int
            Number of results to return.
        semantic_weight : float
            Weight for semantic search (0-1). Keyword weight is (1 - semantic_weight).
        filter_metadata : dict, optional
            Metadata filters to apply.
            
        Returns
        -------
        List[RetrievalResult]
            Retrieved documents with combined scores.
        """
        # Get semantic results
        semantic_results = self.retrieve(
            query=query,
            top_k=top_k * 2,  # Get more for fusion
            filter_metadata=filter_metadata,
        )
        
        # Get keyword results (simple keyword matching)
        keyword_results = self._keyword_search(
            query=query,
            top_k=top_k * 2,
            filter_metadata=filter_metadata,
        )
        
        # Combine and re-rank
        combined = self._reciprocal_rank_fusion(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            semantic_weight=semantic_weight,
        )
        
        return combined[:top_k]

    def _keyword_search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] | None = None,
    ) -> List[RetrievalResult]:
        """
        Simple keyword-based search.
        
        Scores documents based on keyword overlap.
        """
        # Get all documents (or filtered subset)
        all_docs = self.collection.get(
            where=filter_metadata,
            include=["documents", "metadatas"],
        )
        
        if not all_docs["documents"]:
            return []
        
        # Calculate keyword overlap scores
        query_terms = {term.lower() for term in query.split()}
        scored_results = []
        
        for idx, doc in enumerate(all_docs["documents"]):
            doc_terms = {term.lower() for term in doc.split()}
            overlap = len(query_terms.intersection(doc_terms))
            
            if overlap > 0:
                score = overlap / len(query_terms)  # Normalized by query length
                scored_results.append((
                    doc,
                    all_docs["metadatas"][idx],
                    score,
                    all_docs["ids"][idx],
                ))
        
        # Sort by score
        scored_results.sort(key=lambda x: x[2], reverse=True)
        
        # Convert to RetrievalResult objects
        return [
            RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                chunk_id=chunk_id,
            )
            for content, metadata, score, chunk_id in scored_results[:top_k]
        ]

    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        semantic_weight: float = 0.7,
        k: int = 60,
    ) -> List[RetrievalResult]:
        """
        Combine results using reciprocal rank fusion.
        
        RRF is a simple and effective ranking fusion method.
        """
        # Create score dictionaries
        scores: Dict[str, float] = {}
        content_map: Dict[str, RetrievalResult] = {}
        
        # Add semantic scores
        for rank, result in enumerate(semantic_results, start=1):
            rrf_score = semantic_weight / (k + rank)
            scores[result.chunk_id] = scores.get(result.chunk_id, 0) + rrf_score
            content_map[result.chunk_id] = result
        
        # Add keyword scores
        keyword_weight = 1 - semantic_weight
        for rank, result in enumerate(keyword_results, start=1):
            rrf_score = keyword_weight / (k + rank)
            scores[result.chunk_id] = scores.get(result.chunk_id, 0) + rrf_score
            if result.chunk_id not in content_map:
                content_map[result.chunk_id] = result
        
        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Return results with updated scores
        return [
            RetrievalResult(
                content=content_map[chunk_id].content,
                metadata=content_map[chunk_id].metadata,
                score=scores[chunk_id],
                chunk_id=chunk_id,
            )
            for chunk_id in sorted_ids
        ]

    def _format_results(self, results: Dict[str, Any]) -> List[RetrievalResult]:
        """Format ChromaDB query results into RetrievalResult objects."""
        if not results["documents"] or not results["documents"][0]:
            return []
        
        formatted = []
        for idx, content in enumerate(results["documents"][0]):
            formatted.append(
                RetrievalResult(
                    content=content,
                    metadata=results["metadatas"][0][idx],
                    score=1 - results["distances"][0][idx],  # Convert distance to similarity
                    chunk_id=results["ids"][0][idx],
                )
            )
        
        return formatted

    def delete_collection(self) -> None:
        """Delete the current collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection '{self.collection_name}'")

    def reset_collection(self) -> None:
        """Reset the collection (delete and recreate)."""
        self.delete_collection()
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Reset collection '{self.collection_name}'")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": str(self.persist_directory),
        }
