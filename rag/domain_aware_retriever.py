"""
Domain-aware RAG retriever optimized for local CPU usage.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import logging

from rag.vector_store import SimplePersistentVectorStore, SearchResult
from rag.embeddings_provider import create_embeddings_provider
from core.settings import resolve_path

logger = logging.getLogger(__name__)

@dataclass
class DomainContext:
    database_entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    components: List[Dict[str, Any]] = field(default_factory=list)
    design_tokens: List[Dict[str, Any]] = field(default_factory=list) # Changed to list of dicts for details
    documentation: List[Dict[str, Any]] = field(default_factory=list) # New field
    query_patterns: List[str] = field(default_factory=list)
    total_db_count: int = 0
    total_ui_count: int = 0
    all_component_names: List[str] = field(default_factory=list)

class DomainAwareRetriever:
    """
    Retriever optimized for domain-specific knowledge.
    
    Key features:
    1. Multi-collection retrieval (database + components)
    2. Structured output (JSON)
    3. Caching of frequent contexts
    4. CPU-friendly embeddings
    """

    def __init__(
        self,
        database_collection: str = "pos_database_schema",
        components_collection: str = "code_docs", # Pointing to the main collection we used in ingestion
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_dir: str = "rag/store_data", # JSON store directory
        use_cache: bool = True
    ):
        # Initialize embeddings
        self.embedding_provider = create_embeddings_provider(
             provider_type="huggingface", # Local first
             model=embedding_model,
             use_cache=use_cache
        )
        
        # Load Hybrid Config
        from pathlib import Path
        import yaml
        self.config = {}
        config_path = Path("config/rag_hybrid_config.yaml")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        
        # Initialize vector stores
        self.db_store = SimplePersistentVectorStore(
            collection_name=database_collection,
            persist_directory=persist_dir,
            embedding_function=self.embedding_provider.embed_texts
        )
        self.code_store = SimplePersistentVectorStore(
            collection_name=components_collection,
            persist_directory=persist_dir,
            embedding_function=self.embedding_provider.embed_texts
        )
        
        self._context_cache: Dict[str, DomainContext] = {}

    def retrieve_tier(self, tier_id: int, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        [Task 3.2] Retrieve documents specifically for a given tier.
        T1: Rules/Docs, T2: Tokens, T3: Components, T4: Backend
        """
        # Map tier ID to internal categories
        tier_map = {
            1: "documentation",
            2: "design_token",
            3: "ui_component",
            4: "database_schema"
        }
        category = tier_map.get(tier_id, "documentation")
        store = self.db_store if tier_id == 4 else self.code_store
        
        try:
            results = store.search(
                query=query,
                top_k=top_k,
                filter_metadata={"type": category}
            )
            return [
                {
                    "content": r.document.text,
                    "source": resolve_path(r.document.metadata.get("full_path") or r.document.metadata.get("path") or r.document.metadata.get("source")),
                    "metadata": r.document.metadata,
                    "tier": tier_id
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Tier {tier_id} retrieval failed: {e}")
            return []

    def retrieve_domain_context(
        self, 
        user_requirement: str, 
        top_k_entities: int = 5, 
        top_k_components: int = 8,
        top_k_tokens: int = 5,
        top_k_docs: int = 2
    ) -> DomainContext:
        """
        Retrieve structured domain context based on user requirement.
        """
        cache_key = f"{user_requirement[:50]}_{top_k_entities}_{top_k_components}_{top_k_tokens}"
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]

        db_results = []
        component_results = []
        token_results = []
        doc_results = []

        # 1. Retrieve database entities (if relevant)
        try:
            db_results = self.db_store.search(
                query=user_requirement, 
                top_k=top_k_entities, 
                filter_metadata={"type": "database_schema"}
            )
        except Exception as e:
            logger.warning(f"Database search failed: {e}")

        # 2. Retrieve UI Components (using new 'ui_component' type from ingestion)
        try:
            component_results = self.code_store.search(
                query=user_requirement, 
                top_k=top_k_components, 
                filter_metadata={"type": "ui_component"}
            )
            # Fallback/Additional: Try 'react_component' if using legacy data
            if not component_results:
                 component_results = self.code_store.search(
                    query=user_requirement, 
                    top_k=top_k_components, 
                    filter_metadata={"type": "react_component"}
                )
        except Exception as e:
            logger.warning(f"Component search failed: {e}")

        # 3. Retrieve Design Tokens
        try:
             token_results = self.code_store.search(
                query=user_requirement, 
                top_k=top_k_tokens, 
                filter_metadata={"type": "design_token"}
            )
        except Exception as e:
            logger.warning(f"Token search failed: {e}")

        # 4. Retrieve Documentation
        try:
             doc_results = self.code_store.search(
                query=user_requirement, 
                top_k=top_k_docs, 
                filter_metadata={"type": "documentation"}
            )
        except Exception as e:
            logger.warning(f"Doc search failed: {e}")

        # 5. Extract relationships for found entities
        relevant_entities = [r.document.metadata.get("entity") for r in db_results if r.document.metadata.get("entity")]
        relationships = self._get_relationships(relevant_entities)

        # 6. Global Stats
        total_db = 0
        total_ui = 0
        all_names = []
        try:
            total_db = self.db_store.get_collection_stats().get("count", 0)
            ui_stats = self.code_store.get_collection_stats()
            total_ui = ui_stats.get("count", 0)
        except Exception as e:
            pass

        context = DomainContext(
            database_entities=[
                {
                    "name": r.document.metadata.get("entity") or r.document.metadata.get("name"),
                    "properties": json.loads(r.document.metadata.get("schema_info", "{}")).get("properties", []),
                    "relationships": json.loads(r.document.metadata.get("schema_info", "{}")).get("navigation_properties", []),
                }
                for r in db_results
            ],
            relationships=relationships,
            components=[
                {
                    "name": r.document.metadata.get("name"),
                    "content": r.document.text, # Include full text content now!
                    "path": resolve_path(r.document.metadata.get("full_path") or r.document.metadata.get("path")),
                }
                for r in component_results
            ],
            design_tokens=[
                {
                    "name": r.document.metadata.get("name"),
                    "content": r.document.text,
                    "category": r.document.metadata.get("category"),
                }
                for r in token_results
            ],
            documentation=[
                {
                    "name": r.document.metadata.get("name"),
                    "content": r.document.text,
                }
                for r in doc_results
            ],
            total_db_count=total_db,
            total_ui_count=total_ui,
            all_component_names=all_names
        )

        self._context_cache[cache_key] = context
        return context

    def _get_relationships(self, entity_names: List[str]) -> List[Dict[str, Any]]:
        relationships: List[Dict[str, Any]] = []
        if not entity_names:
            return []
            
        for entity in entity_names:
            results = self.db_store.search(
                query=f"relationships involving {entity}", 
                top_k=3, 
                filter_metadata={"type": "database_relationship"}
            )
            for r in results:
                rel = r.document.metadata
                if rel.get("from") in entity_names or rel.get("to") in entity_names:
                     if rel not in relationships:
                        relationships.append(rel)
        return relationships

    def format_context_for_prompt(self, context: DomainContext) -> str:
        """
        Format the structured context into compact JSON for a prompt.
        """
        context_json = {
            "db": {
                "entities": [e["name"] for e in context.database_entities],
            },
            "ui": {
                "components": [
                    {
                        "name": c["name"],
                        # Truncate content for prompt to avoid overflow. 
                        # We try to keep signatures and first part of docs.
                        "snippet": c["content"][:2000] # Increased limit significantly as we want real code
                    }
                    for c in context.components
                ],
                "tokens": [t["content"][:300] for t in context.design_tokens],
                "docs": [d["content"][:1000] for d in context.documentation]
            },
        }
        return json.dumps(context_json, indent=2)

    def optimize_domain_context(self, domain_context: DomainContext, max_tokens: int = 4000) -> str:
        """
        Compress the domain context into a minimal representation.
        """
        return self.format_context_for_prompt(domain_context)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Compatibility method for OrchestratorV2.
        """
        context = self.retrieve_domain_context(query, top_k_entities=top_k, top_k_components=top_k)
        
        results = []
        for component in context.components:
             results.append({
                "content": component["content"][:500] + "...",
                "metadata": {"type": "ui_component", "name": component["name"]},
                "score": 1.0
            })
        return results
