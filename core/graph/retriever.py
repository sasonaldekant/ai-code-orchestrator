
import logging
from typing import List, Dict, Any, Optional

from .schema import KnowledgeGraph, GraphNode, NodeType, EdgeType

logger = logging.getLogger(__name__)

class GraphRetriever:
    """
    Retrieves structural context from the Knowledge Graph.
    Used to augment vector search results with neighbor nodes.
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def expand_context(self, node_ids: List[str], hops: int = 1) -> List[GraphNode]:
        """
        Get 1-hop neighbors for a list of nodes to provide structural context.
        useful for answering "What does this class inherit from?" or "What does this function call?"
        """
        all_nodes = set()
        
        # 1. Add original nodes
        for nid in node_ids:
            if nid in self.graph.nodes:
                all_nodes.add(self.graph.nodes[nid])
            else:
                logger.warning(f"Node ID {nid} not found in graph")

        # 2. Expand neighbors
        if hops > 0:
            for nid in node_ids:
                neighbors = self.graph.get_neighbors(nid)
                for neighbor in neighbors:
                    all_nodes.add(neighbor)
        
        return list(all_nodes)

    def format_context(self, nodes: List[GraphNode]) -> str:
        """
        Format graph nodes into a string for the LLM prompt.
        """
        if not nodes:
            return ""

        lines = ["\n### Structural Context (Knowledge Graph):"]
        
        # Group by File
        nodes_by_file = {}
        for node in nodes:
            if node.type == NodeType.FILE:
                continue # Skip file nodes themselves in listing, or maybe include?
            
            # Simple grouping
            fpath = node.file_path or "External"
            if fpath not in nodes_by_file:
                nodes_by_file[fpath] = []
            nodes_by_file[fpath].append(node)

        for fpath, file_nodes in nodes_by_file.items():
            lines.append(f"- File: `{fpath}`")
            for node in file_nodes:
                lines.append(f"  - [{node.type.value.upper()}] {node.name} (Line: {node.metadata.get('lineno', '?')})")
        
        return "\n".join(lines)
