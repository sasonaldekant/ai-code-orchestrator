"""Base Ingester class.

All domain knowledge ingesters inherit from this.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path


class Document:
    """Structured document for RAG indexing."""
    
    def __init__(
        self,
        id: str,
        type: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        self.id = id
        self.type = type
        self.content = content
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for vector store."""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        return f"Document(id='{self.id}', type='{self.type}', content_length={len(self.content)})"


class BaseIngester(ABC):
    """Abstract base class for all ingesters."""
    
    def __init__(self, source_config: 'KnowledgeSource'):
        self.source_config = source_config
        self.documents: List[Document] = []
    
    @abstractmethod
    def ingest(self) -> List[Document]:
        """Main ingestion method.
        
        Returns:
            List of Document objects ready for indexing
        """
        pass
    
    def _create_document(
        self,
        id: str,
        type: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Document:
        """Helper to create a Document."""
        return Document(id=id, type=type, content=content, metadata=metadata)
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve file path (handles URLs by cloning)."""
        if path.startswith('http'):
            # TODO: Implement git clone logic
            raise NotImplementedError("URL cloning not yet implemented")
        return Path(path).resolve()
