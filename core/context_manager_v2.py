"""
Enhanced Context Manager with RAG integration.
Updated to support hybrid retrieval as per ADVANCED_RAG_Source.md.
"""

from __future__ import annotations

import logging
import json
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.retriever_v2 import EnhancedRAGRetriever, RetrievalResult

logger = logging.getLogger(__name__)

@dataclass
class EnrichedContext:
    phase: str
    specialty: Optional[str]
    retrieved_docs: List[RetrievalResult] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_prompt_context(self, max_docs: int = 3) -> str:
        parts = []
        
        # 1. Retrieved Knowledge
        if self.retrieved_docs:
            parts.append("## Relevant Domain Knowledge:")
            for i, doc in enumerate(self.retrieved_docs[:max_docs]):
                source = doc.metadata.get("source", "unknown")
                parts.append(f"Source {i+1} ({source}):\n```\n{doc.content.strip()}\n```\n")
        
        # 2. Phase Rules
        if self.rules:
             parts.append(f"## {self.phase.capitalize()} Rules:\n{yaml.dump(self.rules)}")

        return "\n".join(parts)

class EnhancedContextManager:
    def __init__(self, enable_rag: bool = True):
        self.enable_rag = enable_rag
        self.retriever = None
        
        if enable_rag:
            try:
                self.retriever = EnhancedRAGRetriever()
            except ImportError:
                logger.warning("ChromaDB not installed, RAG disabled.")
                self.enable_rag = False

    def build_context(
        self,
        phase: str,
        user_query: str,
        specialty: Optional[str] = None,
        schema_path: Optional[str] = None,
        rules_path: Optional[str] = None,
        top_k_docs: int = 5
    ) -> EnrichedContext:
        """
        Build enriched context combining RAG retrieval and static configs.
        """
        # Load static
        rules = {}
        if rules_path:
             try:
                 with open(rules_path, 'r') as f:
                     rules = yaml.safe_load(f)
             except Exception as e:
                 logger.error(f"Failed to load rules: {e}")

        schema = {}
        if schema_path:
             try:
                 with open(schema_path, 'r') as f:
                     schema = json.load(f)
             except Exception as e:
                 logger.error(f"Failed to load schema: {e}")

        # RAG Retrieval
        docs = []
        if self.enable_rag and self.retriever and user_query:
            # Construct a hybrid query
            context_query = f"{phase} {specialty or ''} {user_query}"
            docs = self.retriever.hybrid_retrieve(
                query=context_query,
                top_k=top_k_docs,
                semantic_weight=0.7 # Default balance
            )
        
        return EnrichedContext(
            phase=phase,
            specialty=specialty,
            retrieved_docs=docs,
            rules=rules,
            schema=schema
        )

    def add_domain_knowledge(self, content: str, metadata: Dict[str, Any], doc_id: str):
        if self.enable_rag and self.retriever:
            self.retriever.add_document(content, metadata, doc_id=doc_id)
