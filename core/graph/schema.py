
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class NodeType(Enum):
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    MODULE = "module"

class EdgeType(Enum):
    IMPORTS = "imports"          # A imports B
    DEFINES = "defines"          # File A defines Class B
    INHERITS = "inherits"        # Class A inherits Class B
    CALLS = "calls"              # Function A calls Function B
    INSTANTIATES = "instantiates" # Function A creates instance of Class B

@dataclass
class GraphNode:
    id: str                 # Unique ID (e.g., "file:src/main.py", "class:UserService")
    type: NodeType
    name: str               # Human readable name
    file_path: str          # Where it is defined
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "file_path": self.file_path,
            "metadata": self.metadata
        }

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, GraphNode):
            return False
        return self.id == other.id

@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    type: EdgeType
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.type.value,
            "metadata": self.metadata
        }

class KnowledgeGraph:
    """
    In-memory representation of the code knowledge graph.
    Can be serialized to JSON/GEXF or pushed to Neo4j.
    """
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adjacency: Dict[str, Set[str]] = {} # source -> set of targets

    def add_node(self, node: GraphNode):
        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self.adjacency[node.id] = set()

    def add_edge(self, edge: GraphEdge):
        if edge.source_id not in self.nodes:
            logger.warning(f"Accessing unknown source node: {edge.source_id}")
            # Auto-create phantom node? For now, skip.
            return
        
        # We allow edges to unknown targets (e.g. external libraries)
        # But for internal consistency, better to only link known nodes.
        if edge.target_id not in self.nodes:
            # Create a "External" placeholder node if needed?
            pass

        self.edges.append(edge)
        self.adjacency[edge.source_id].add(edge.target_id)

    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphNode]:
        """Get connected nodes."""
        if node_id not in self.adjacency:
            return []
        
        target_ids = self.adjacency[node_id]
        if edge_type:
            # Filter by edge type
            filtered_targets = {
                e.target_id for e in self.edges 
                if e.source_id == node_id and e.type == edge_type
            }
            target_ids = target_ids.intersection(filtered_targets)
            
        return [self.nodes[tid] for tid in target_ids if tid in self.nodes]

    def to_json(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'KnowledgeGraph':
        kg = cls()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for n_data in data['nodes']:
            kg.add_node(GraphNode(
                id=n_data['id'],
                type=NodeType(n_data['type']),
                name=n_data['name'],
                file_path=n_data['file_path'],
                metadata=n_data['metadata']
            ))
            
        for e_data in data['edges']:
            kg.add_edge(GraphEdge(
                source_id=e_data['source'],
                target_id=e_data['target'],
                type=EdgeType(e_data['type']),
                metadata=e_data['metadata']
            ))
        return kg
