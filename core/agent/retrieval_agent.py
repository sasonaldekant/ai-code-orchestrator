
import logging
from typing import List, Dict, Any, Optional

from rag.vector_store import VectorStore, SearchResult
from core.graph.retriever import GraphRetriever, GraphNode
from core.graph.schema import NodeType

logger = logging.getLogger(__name__)

class RetrievalAgent:
    """
    Investigator Agent that orchestrates Vector Search, Re-ranking, and Graph Retrieval
    to answer complex questions about the codebase.
    """

    def __init__(self, vector_store: VectorStore, graph_retriever: GraphRetriever, llm_client=None):
        self.vector_store = vector_store
        self.graph_retriever = graph_retriever
        self.llm_client = llm_client # Optional: for future "Plan -> Act" loop using LLM

    def investigate(self, query: str, top_k: int = 5, hops: int = 1) -> Dict[str, Any]:
        """
        Perform a multi-hop investigation.
        
        Process:
        1. Hybrid Search (Vector + Keyword) with Re-ranking (if available).
        2. Extract key entities (File/Class/Function) from search results.
        3. Expand context using Knowledge Graph (1-hop neighbors).
        4. Fuse results into a coherent context package.
        """
        logger.info(f"🕵️ Investigating: '{query}'")
        
        # Step 1: High-Precision Search
        # We enable re-ranking by default for the agent as accuracy > speed here.
        search_results = self.vector_store.search(
            query=query, 
            top_k=top_k, 
            use_reranking=True 
        )
        
        # Step 2: Identify Graph Entry Points from Search Results
        # We assume VectorStore docs have 'id' metadata matching GraphNode ids,
        # OR we construct IDs from metadata (e.g. file_path).
        # Our GraphIngester uses ids like "file:path", "class:name:path", "func:name:path".
        # Our VectorStore docs likely have "source" or standard IDs.
        # For this MVP, let's assume we can map VectorStore ID -> Graph ID or use file paths.
        
        entry_point_ids = []
        for res in search_results:
            # Attempt to map to Graph IDs
            # Strategy A: Use file path from metadata
            file_path = res.document.metadata.get("source") or res.document.metadata.get("file_path")
            if file_path:
                # Add File Node
                entry_point_ids.append(f"file:{file_path}")
                
            # Strategy B: If chunk is a function/class, try to construct likely ID
            # In a real system, VectorStore docs should share exact IDs with Graph. 
            # For now, we rely on file-level expansion which is robust.
            
        # Step 3: Graph Expansion
        graph_context = []
        if entry_point_ids:
            # Deduplicate
            entry_point_ids = list(set(entry_point_ids))
            logger.info(f"Expanding graph context for {len(entry_point_ids)} entry points...")
            
            graph_nodes = self.graph_retriever.expand_context(entry_point_ids, hops=hops)
            graph_context = self.graph_retriever.format_context(graph_nodes)
        
        # Step 4: Synthesize Report
        return {
            "query": query,
            "vector_results": search_results,
            "graph_context": graph_context,
            "entry_points": entry_point_ids
        }

    def format_final_prompt(self, investigation: Dict[str, Any]) -> str:
        """
        Create a prompt for the LLM using the gathered intelligence.
        """
        lines = [f"User Query: {investigation['query']}\n"]
        
        lines.append("### Retrieved Code Snippets (Vector Search)\n")
        for i, res in enumerate(investigation['vector_results']):
            lines.append(f"Source: {res.document.metadata.get('source', 'unknown')}")
            lines.append(f"Relevance: {res.score:.4f}")
            lines.append(f"```\n{res.document.text[:500]}...\n```\n")
            
        if investigation['graph_context']:
            lines.append(investigation['graph_context'])
            
        return "\n".join(lines)
