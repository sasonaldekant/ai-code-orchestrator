"""
Domain-aware RAG retriever optimized for local CPU usage.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import logging

from rag.vector_store import ChromaVectorStore, SearchResult
from rag.embeddings_provider import create_embeddings_provider

logger = logging.getLogger(__name__)

@dataclass
class DomainContext:
    database_entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    components: List[Dict[str, Any]] = field(default_factory=list)
    design_tokens: List[str] = field(default_factory=list)
    query_patterns: List[str] = field(default_factory=list)

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
        components_collection: str = "pos_component_library",
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_dir: str = "rag/chroma_db",
        use_cache: bool = True
    ):
        # Initialize embeddings
        self.embedding_provider = create_embeddings_provider(
             provider_type="huggingface", # Local first
             model=embedding_model,
             use_cache=use_cache
        )
        
        # Initialize vector stores
        self.db_store = ChromaVectorStore(
            collection_name=database_collection,
            persist_directory=persist_dir,
            embedding_function=self.embedding_provider.embed_texts
        )
        self.components_store = ChromaVectorStore(
            collection_name=components_collection,
            persist_directory=persist_dir,
            embedding_function=self.embedding_provider.embed_texts
        )
        
        self._context_cache: Dict[str, DomainContext] = {}

    def retrieve_domain_context(
        self, 
        user_requirement: str, 
        top_k_entities: int = 5, 
        top_k_components: int = 8
    ) -> DomainContext:
        """
        Retrieve structured domain context based on user requirement.
        """
        cache_key = f"{user_requirement[:50]}_{top_k_entities}_{top_k_components}"
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]

        # 1. Retrieve database entities
        # Note: 'type' filter matches metadata set in ingesters
        db_results = self.db_store.search(
            query=user_requirement, 
            top_k=top_k_entities, 
            filter_metadata={"type": "database_schema"}
        )

        # 2. Retrieve React components
        component_results = self.components_store.search(
            query=user_requirement, 
            top_k=top_k_components, 
            filter_metadata={"type": "react_component"}
        )

        # 3. Extract relationships for found entities
        relevant_entities = [r.document.metadata.get("entity") for r in db_results if r.document.metadata.get("entity")]
        relationships = self._get_relationships(relevant_entities)

        # 4. Extract design tokens from found components
        design_tokens = self._extract_design_tokens(component_results)

        # 5. Get query patterns (optional/future)
        query_patterns: List[str] = [] 

        context = DomainContext(
            database_entities=[
                {
                    "name": r.document.metadata.get("entity"),
                    "properties": json.loads(r.document.metadata.get("schema_info", "{}")).get("properties", []),
                    "relationships": json.loads(r.document.metadata.get("schema_info", "{}")).get("navigation_properties", []),
                }
                for r in db_results
            ],
            relationships=relationships,
            components=[
                {
                    "name": r.document.metadata.get("component"),
                    "props": json.loads(r.document.metadata.get("component_info", "{}")).get("props", []),
                    "examples": json.loads(r.document.metadata.get("component_info", "{}")).get("examples", []),
                }
                for r in component_results
            ],
            design_tokens=design_tokens,
            query_patterns=query_patterns,
        )

        self._context_cache[cache_key] = context
        return context

    def _get_relationships(self, entity_names: List[str]) -> List[Dict[str, Any]]:
        relationships: List[Dict[str, Any]] = []
        if not entity_names:
            return []
            
        for entity in entity_names:
            # This is a bit naive; ideally we query for specific relationship documents
            # or lookup in the entity metadata directly if we indexed full graphs.
            # Here we search for "relationships involving X"
            results = self.db_store.search(
                query=f"relationships involving {entity}", 
                top_k=3, 
                filter_metadata={"type": "database_relationship"}
            )
            for r in results:
                rel = r.document.metadata
                # Filter to ensure it actually involves our entities
                if rel.get("from") in entity_names or rel.get("to") in entity_names:
                     # Avoid duplicates
                     if rel not in relationships:
                        relationships.append(rel)
        return relationships

    def _extract_design_tokens(self, component_results: List[SearchResult]) -> List[str]:
        tokens = set()
        for result in component_results:
            info = json.loads(result.document.metadata.get("component_info", "{}"))
            tokens.update(info.get("design_tokens", []))
        return sorted(list(tokens))

    def format_context_for_prompt(self, context: DomainContext) -> str:
        """
        Format the structured context into compact JSON for a prompt.
        """
        context_json = {
            "db": {
                "e": [
                    {
                        "name": e["name"],
                        "props": [f"{p['name']}:{p['type']}" for p in e.get("properties", [])[:10]],
                        "rels": [f"{r['property_name']}->{r['related_entity']}" for r in e.get("relationships", [])[:5]],
                    }
                    for e in context.database_entities
                ],
                "r": [f"{r['from']}->{r['to']} ({r.get('type','?')})" for r in context.relationships[:10]],
            },
            "ui": {
                "c": [
                    {
                        "name": c["name"],
                        "props": [f"{p['name']}:{p['type']}" for p in c.get("props", [])[:8]],
                    }
                    for c in context.components
                ],
                "t": context.design_tokens[:15],
            },
        }
        return json.dumps(context_json, separators=(",", ":"))

    def optimize_domain_context(self, domain_context: DomainContext, max_tokens: int = 2000) -> str:
        """
        Compress the domain context into a minimal representation.
        """
        entities_compact = [
            f"{e['name']}({','.join([p['name'] for p in e.get('properties', [])[:5]])})"
            for e in domain_context.database_entities
        ]
        rels_compact = [f"{r['from']}->{r['to']}" for r in domain_context.relationships]
        components_compact = [
            f"{c['name']}({','.join([p['name'] for p in c.get('props', [])[:5]])})"
            for c in domain_context.components
        ]
        
        context = {
            "db": {"e": entities_compact, "r": rels_compact},
            "ui": {"c": components_compact, "t": domain_context.design_tokens[:10]},
        }
        
        compact_json = json.dumps(context, separators=(",", ":"))
        
        # Rough token estimate: number of words * 1.3
        # Using a simple heuristic here to avoid dependency on tokenizer for this check
        token_count = len(compact_json.split()) * 1.3
        
        if token_count > max_tokens:
            # Truncate lists if too large
            context["db"]["e"] = context["db"]["e"][:3]
            context["ui"]["c"] = context["ui"]["c"][:5]
            compact_json = json.dumps(context, separators=(",", ":"))
            
        return compact_json

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Compatibility method for OrchestratorV2.
        Returns a flat list of retrieved documents (DB entities + components).
        """
        context = self.retrieve_domain_context(query, top_k_entities=top_k, top_k_components=top_k)
        
        # Flatten results for generic use
        results = []
        for entity in context.database_entities:
            results.append({
                "content": f"Entity: {entity['name']}",
                "metadata": {"type": "database_entity", "name": entity["name"]},
                "score": 1.0 # Mock score
            })
        for component in context.components:
             results.append({
                "content": f"Component: {component['name']}",
                "metadata": {"type": "react_component", "name": component["name"]},
                "score": 1.0
            })
        return results
