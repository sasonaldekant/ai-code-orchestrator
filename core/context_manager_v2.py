"""
Enhanced context manager with RAG integration.

Provides dynamic context enrichment using the RAG retriever,
combining static schemas/rules with retrieved knowledge.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import yaml

from core.retriever_v2 import EnhancedRAGRetriever, RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class EnrichedContext:
    """Context enriched with RAG-retrieved knowledge."""
    
    phase: str
    specialty: str | None
    rules: Dict[str, Any]
    schema: Dict[str, Any]
    retrieved_docs: List[RetrievalResult]
    extra: Dict[str, Any]
    
    def to_prompt_context(self, max_docs: int = 3) -> str:
        """
        Format context for LLM prompt.
        
        Parameters
        ----------
        max_docs : int
            Maximum number of retrieved documents to include.
            
        Returns
        -------
        str
            Formatted context string for prompt.
        """
        parts = []
        
        # Phase and specialty
        parts.append(f"Phase: {self.phase}")
        if self.specialty:
            parts.append(f"Specialty: {self.specialty}")
        
        # Rules
        if self.rules:
            parts.append("\nRules:")
            parts.append(yaml.dump(self.rules, default_flow_style=False))
        
        # Schema (truncated if too large)
        if self.schema:
            parts.append("\nSchema:")
            schema_str = json.dumps(self.schema, indent=2)
            if len(schema_str) > 2000:
                schema_str = schema_str[:2000] + "\n... (truncated)"
            parts.append(schema_str)
        
        # Retrieved knowledge
        if self.retrieved_docs:
            parts.append("\nRelevant Knowledge:")
            for idx, doc in enumerate(self.retrieved_docs[:max_docs], 1):
                parts.append(f"\n[{idx}] (score: {doc.score:.3f})")
                if "source" in doc.metadata:
                    parts.append(f"Source: {doc.metadata['source']}")
                parts.append(doc.content)
                parts.append("-" * 40)
        
        return "\n".join(parts)


class EnhancedContextManager:
    """
    Context manager with RAG integration.
    
    Combines static configuration (rules, schemas) with dynamic
    knowledge retrieval for enriched context.
    """

    def __init__(
        self,
        retriever: EnhancedRAGRetriever | None = None,
        enable_rag: bool = True,
    ) -> None:
        """
        Initialize the context manager.
        
        Parameters
        ----------
        retriever : EnhancedRAGRetriever, optional
            RAG retriever instance. If None and enable_rag is True,
            a default retriever will be created.
        enable_rag : bool
            Whether to enable RAG enrichment.
        """
        self.enable_rag = enable_rag
        
        if enable_rag:
            if retriever is None:
                self.retriever = EnhancedRAGRetriever()
            else:
                self.retriever = retriever
        else:
            self.retriever = None
        
        logger.info(
            f"Initialized EnhancedContextManager (RAG {'enabled' if enable_rag else 'disabled'})"
        )

    def build_context(
        self,
        phase: str,
        specialty: str | None = None,
        schema_path: Path | None = None,
        rules_path: Path | None = None,
        user_query: str | None = None,
        top_k_docs: int = 3,
        filter_metadata: Dict[str, Any] | None = None,
    ) -> EnrichedContext:
        """
        Build enriched context for a phase.
        
        Parameters
        ----------
        phase : str
            Current phase (e.g., 'planning', 'implementation').
        specialty : str, optional
            Agent specialty (e.g., 'backend', 'frontend').
        schema_path : Path, optional
            Path to schema JSON file.
        rules_path : Path, optional
            Path to rules YAML file.
        user_query : str, optional
            User query or requirement for RAG retrieval.
        top_k_docs : int
            Number of documents to retrieve from RAG.
        filter_metadata : dict, optional
            Metadata filters for RAG retrieval.
            
        Returns
        -------
        EnrichedContext
            Context enriched with retrieved knowledge.
        """
        # Load static configuration
        rules = self._load_yaml(rules_path) if rules_path and rules_path.exists() else {}
        schema = self._load_json(schema_path) if schema_path and schema_path.exists() else {}
        
        # Retrieve relevant documents if RAG is enabled
        retrieved_docs: List[RetrievalResult] = []
        
        if self.enable_rag and self.retriever and user_query:
            try:
                # Build retrieval query
                query_parts = [user_query]
                if phase:
                    query_parts.append(f"phase:{phase}")
                if specialty:
                    query_parts.append(f"specialty:{specialty}")
                
                query = " ".join(query_parts)
                
                # Retrieve documents using hybrid search
                retrieved_docs = self.retriever.hybrid_retrieve(
                    query=query,
                    top_k=top_k_docs,
                    filter_metadata=filter_metadata,
                )
                
                logger.info(
                    f"Retrieved {len(retrieved_docs)} documents for query: {user_query[:50]}..."
                )
            except Exception as exc:
                logger.error(f"RAG retrieval failed: {exc}")
        
        return EnrichedContext(
            phase=phase,
            specialty=specialty,
            rules=rules,
            schema=schema,
            retrieved_docs=retrieved_docs,
            extra={},
        )

    def add_domain_knowledge(
        self,
        content: str,
        metadata: Dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> int:
        """
        Add domain knowledge to the RAG system.
        
        Parameters
        ----------
        content : str
            Knowledge content to add.
        metadata : dict, optional
            Metadata tags for filtering.
        doc_id : str, optional
            Unique document ID.
            
        Returns
        -------
        int
            Number of chunks created.
        """
        if not self.enable_rag or not self.retriever:
            logger.warning("RAG is disabled, cannot add knowledge")
            return 0
        
        # Determine chunking strategy from metadata
        strategy = "text"
        if metadata and "type" in metadata:
            strategy = metadata["type"]
        
        return self.retriever.add_document(
            content=content,
            metadata=metadata,
            doc_id=doc_id,
            chunking_strategy=strategy,
        )

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as exc:
            logger.error(f"Failed to load YAML from {path}: {exc}")
            return {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"Failed to load JSON from {path}: {exc}")
            return {}

    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        if not self.enable_rag or not self.retriever:
            return {"enabled": False}
        
        stats = self.retriever.get_collection_stats()
        stats["enabled"] = True
        return stats
