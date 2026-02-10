"""Vector store implementations for RAG retrieval.

Provides pluggable vector database backends:
- ChromaDB (default, best for local deployment)
- Faiss (high performance, CPU-friendly)
- InMemory (testing, small datasets)

All stores support:
- Embedding generation and indexing
- Similarity search with metadata filtering
- Collection management
- Persistent storage
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import json
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document representation for vector store."""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Search result with score and metadata."""
    document: Document
    score: float
    rank: int


class VectorStore(ABC):
    """Abstract base class for vector store implementations."""

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Delete a single document by ID."""
        pass

    @abstractmethod
    def get_documents(self, limit: int = 10, offset: int = 0) -> List[Document]:
        """Retrieve a list of documents from the store."""
        pass

    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        pass


class ChromaVectorStore(VectorStore):
    """
    ChromaDB vector store implementation.
    
    Best choice for local deployment:
    - No GPU required
    - Persistent storage
    - Good performance for < 1M documents
    - Built-in metadata filtering
    """

    def __init__(
        self,
        collection_name: str = "code_docs",
        persist_directory: str = "rag/chroma_db",
        embedding_function: Optional[Any] = None
    ) -> None:
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "ChromaDB not installed. Install with: pip install chromadb"
            )

        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client with persistent storage (modern API)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

        self.embedding_function = embedding_function
        logger.info(
            f"Initialized ChromaDB collection '{collection_name}' "
            f"at {persist_directory}"
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Chroma collection."""
        if not documents:
            return

        ids = [doc.id for doc in documents]
        texts = [doc.text for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Generate embeddings if not provided
        embeddings = None
        if documents[0].embedding is not None:
            embeddings = [doc.embedding for doc in documents]
        elif self.embedding_function is not None:
            embeddings = self.embedding_function(texts)

        # Add to collection
        if embeddings:
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            # Chroma will use default embedding function
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )

        logger.info(f"Added {len(documents)} documents to Chroma collection")

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents in Chroma."""
        # Build where clause for metadata filtering
        where = filter_metadata if filter_metadata else None

        # Query collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )

        # Convert to SearchResult objects
        search_results = []
        if results['ids'] and results['ids'][0]:
            for rank, (doc_id, text, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                document = Document(
                    id=doc_id,
                    text=text,
                    metadata=metadata or {}
                )
                # Convert distance to similarity score (1 - cosine_distance)
                score = 1.0 - distance if distance is not None else 0.0
                search_results.append(SearchResult(
                    document=document,
                    score=score,
                    rank=rank + 1
                ))

        return search_results

    def delete_collection(self) -> None:
        """Delete the Chroma collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted Chroma collection '{self.collection_name}'")

    def delete_document(self, document_id: str) -> None:
        """Delete a single document by ID from Chroma."""
        self.collection.delete(ids=[document_id])
        logger.info(f"Deleted document '{document_id}' from Chroma collection '{self.collection_name}'")

    def get_documents(self, limit: int = 10, offset: int = 0) -> List[Document]:
        """Retrieve a list of documents from Chroma."""
        results = self.collection.get(
            limit=limit,
            offset=offset,
            include=['documents', 'metadatas']
        )
        
        documents = []
        if results['ids']:
            for doc_id, text, metadata in zip(results['ids'], results['documents'], results['metadatas']):
                documents.append(Document(
                    id=doc_id,
                    text=text,
                    metadata=metadata or {}
                ))
        return documents

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get Chroma collection statistics."""
        count = self.collection.count()
        return {
            "name": self.collection_name,
            "count": count,
            "persist_directory": str(self.persist_directory)
        }


class FaissVectorStore(VectorStore):
    """
    Faiss vector store implementation.
    
    High-performance option:
    - Extremely fast similarity search
    - CPU-friendly (no GPU required for small datasets)
    - Manual persistence required
    - Best for > 100K documents
    """

    def __init__(
        self,
        dimension: int = 1536,  # OpenAI embedding dimension
        index_type: str = "Flat",  # Flat, IVF, HNSW
        persist_path: Optional[str] = "rag/faiss_index",
        embedding_function: Optional[Any] = None
    ) -> None:
        try:
            import faiss
        except ImportError:
            raise ImportError(
                "Faiss not installed. Install with: pip install faiss-cpu"
            )

        self.dimension = dimension
        self.persist_path = Path(persist_path) if persist_path else None
        self.embedding_function = embedding_function
        self.documents: List[Document] = []
        self.doc_id_to_idx: Dict[str, int] = {}

        # Create Faiss index
        if index_type == "Flat":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "IVF":
            # For larger datasets
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        elif index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(dimension, 32)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Load existing index if available
        if self.persist_path and self.persist_path.exists():
            self._load_index()

        logger.info(f"Initialized Faiss index (type={index_type}, dim={dimension})")

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Faiss index."""
        if not documents:
            return

        # Generate embeddings if not provided
        embeddings = []
        for doc in documents:
            if doc.embedding:
                embeddings.append(doc.embedding)
            elif self.embedding_function:
                emb = self.embedding_function([doc.text])[0]
                embeddings.append(emb)
            else:
                raise ValueError("No embeddings provided and no embedding function")

        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Add to index
        start_idx = len(self.documents)
        self.index.add(embeddings_array)

        # Store documents and mapping
        for i, doc in enumerate(documents):
            self.documents.append(doc)
            self.doc_id_to_idx[doc.id] = start_idx + i

        logger.info(f"Added {len(documents)} documents to Faiss index")

        # Persist if configured
        if self.persist_path:
            self._save_index()

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents in Faiss index."""
        if not self.embedding_function:
            raise ValueError("Embedding function required for search")

        # Generate query embedding
        query_embedding = np.array(
            self.embedding_function([query]),
            dtype=np.float32
        )

        # Search index
        distances, indices = self.index.search(query_embedding, top_k)

        # Convert to SearchResult objects
        search_results = []
        for rank, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx < len(self.documents):
                doc = self.documents[idx]

                # Apply metadata filter if provided
                if filter_metadata:
                    match = all(
                        doc.metadata.get(k) == v
                        for k, v in filter_metadata.items()
                    )
                    if not match:
                        continue

                # Convert L2 distance to similarity score
                score = 1.0 / (1.0 + float(distance))
                search_results.append(SearchResult(
                    document=doc,
                    score=score,
                    rank=rank + 1
                ))

        return search_results

    def delete_collection(self) -> None:
        """Clear Faiss index and documents."""
        self.index.reset()
        self.documents.clear()
        self.doc_id_to_idx.clear()
        if self.persist_path and self.persist_path.exists():
            self.persist_path.unlink()
        logger.info("Deleted Faiss index")

    def delete_document(self, document_id: str) -> None:
        """Delete document from Faiss (requires rebuild, simulating for now)."""
        logger.warning("Deleting individual documents from Faiss requires index rebuild. Not yet fully optimized.")
        if document_id in self.doc_id_to_idx:
            idx = self.doc_id_to_idx.pop(document_id)
            # In a real app, we'd rebuild or use IndexIDMap. 
            # For now, we just remove from our tracking.
            self.documents[idx] = None 
            if self.persist_path:
                self._save_index()

    def get_documents(self, limit: int = 10, offset: int = 0) -> List[Document]:
        """Simple document retrieval for Faiss."""
        valid_docs = [d for d in self.documents if d is not None]
        return valid_docs[offset:offset + limit]

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get Faiss index statistics."""
        return {
            "count": self.index.ntotal,
            "dimension": self.dimension,
            "persist_path": str(self.persist_path) if self.persist_path else None
        }

    def _save_index(self) -> None:
        """Save Faiss index and documents to disk."""
        import faiss
        if self.persist_path:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            # Save index
            index_file = self.persist_path.with_suffix(".index")
            faiss.write_index(self.index, str(index_file))
            # Save documents
            docs_file = self.persist_path.with_suffix(".docs.json")
            docs_data = [
                {
                    "id": doc.id,
                    "text": doc.text,
                    "metadata": doc.metadata
                }
                for doc in self.documents
            ]
            docs_file.write_text(json.dumps(docs_data), encoding="utf-8")
            logger.info(f"Saved Faiss index to {self.persist_path}")

    def _load_index(self) -> None:
        """Load Faiss index and documents from disk."""
        import faiss
        index_file = self.persist_path.with_suffix(".index")
        docs_file = self.persist_path.with_suffix(".docs.json")
        
        if index_file.exists() and docs_file.exists():
            # Load index
            self.index = faiss.read_index(str(index_file))
            # Load documents
            docs_data = json.loads(docs_file.read_text(encoding="utf-8"))
            self.documents = [
                Document(
                    id=d["id"],
                    text=d["text"],
                    metadata=d["metadata"]
                )
                for d in docs_data
            ]
            self.doc_id_to_idx = {doc.id: i for i, doc in enumerate(self.documents)}
            logger.info(f"Loaded Faiss index from {self.persist_path}")


class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store for testing.
    
    Uses numpy for similarity computation.
    No persistence, suitable for small datasets only.
    """

    def __init__(self, embedding_function: Optional[Any] = None) -> None:
        self.documents: List[Document] = []
        self.embedding_function = embedding_function
        logger.info("Initialized in-memory vector store")

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to in-memory store."""
        if not documents:
            return

        # Generate embeddings if needed
        for doc in documents:
            if not doc.embedding and self.embedding_function:
                doc.embedding = self.embedding_function([doc.text])[0]
            self.documents.append(doc)

        logger.info(f"Added {len(documents)} documents to in-memory store")

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search using cosine similarity."""
        if not self.embedding_function:
            raise ValueError("Embedding function required for search")

        # Generate query embedding
        query_embedding = np.array(self.embedding_function([query])[0])

        # Compute similarities
        similarities = []
        for doc in self.documents:
            # Apply metadata filter
            if filter_metadata:
                match = all(
                    doc.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue

            if doc.embedding:
                doc_embedding = np.array(doc.embedding)
                # Cosine similarity
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.lin