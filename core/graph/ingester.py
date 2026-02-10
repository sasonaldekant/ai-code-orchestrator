
import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional

from .schema import KnowledgeGraph, GraphNode, GraphEdge, NodeType, EdgeType

logger = logging.getLogger(__name__)

class GraphIngester:
    """
    Parses code files to extract a Knowledge Graph.
    Uses 'ast' for Python and Regex for other languages (C#, TS).
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def process_file(self, file_path: str, content: str):
        """
        Analyze a file and populate the graph.
        """
        path = Path(file_path)
        file_id = f"file:{file_path}"
        
        # 1. Add File Node
        self.graph.add_node(GraphNode(
            id=file_id,
            type=NodeType.FILE,
            name=path.name,
            file_path=file_path,
            metadata={"extension": path.suffix}
        ))

        # 2. Parse based on extension
        if path.suffix == ".py":
            self._process_python(file_id, file_path, content)
        elif path.suffix in [".cs", ".ts", ".js"]:
            self._process_regex(file_id, file_path, content, path.suffix)
        else:
            logger.info(f"Skipping graph analysis for unsupported type: {path.suffix}")

    def _process_python(self, file_id: str, file_path: str, content: str):
        try:
            tree = ast.parse(content)
            
            # Walk the AST
            for node in ast.walk(tree):
                # Class Def
                if isinstance(node, ast.ClassDef):
                    class_id = f"class:{node.name}:{file_path}"
                    self.graph.add_node(GraphNode(
                        id=class_id,
                        type=NodeType.CLASS,
                        name=node.name,
                        file_path=file_path,
                        metadata={"lineno": node.lineno}
                    ))
                    # Edge: File defines Class
                    self.graph.add_edge(GraphEdge(
                        source_id=file_id,
                        target_id=class_id,
                        type=EdgeType.DEFINES
                    ))
                    
                    # Inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            # We assume the base class is in the graph or will be.
                            # Since we don't know the file of the base class yet, 
                            # we face a linking challenge. 
                            # For MVP, we'll store the edge target as "fuzzy" and resolve later?
                            # Or just create a placeholder semantic node.
                            base_id_fuzzy = f"class:{base.id}:?" 
                            # Actually, for visualization, just linking to the name is often enough for top-level view
                            # or we leave it for now.
                            pass

                # Function Def
                elif isinstance(node, ast.FunctionDef):
                    func_id = f"func:{node.name}:{file_path}"
                    self.graph.add_node(GraphNode(
                        id=func_id,
                        type=NodeType.FUNCTION,
                        name=node.name,
                        file_path=file_path,
                        metadata={"lineno": node.lineno}
                    ))
                    # Edge: File defines Function
                    self.graph.add_edge(GraphEdge(
                        source_id=file_id,
                        target_id=func_id,
                        type=EdgeType.DEFINES
                    ))
                    
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        # Edge: File imports Module
                        module_name = alias.name
                        # Create pseudo-node for external module
                        mod_id = f"module:{module_name}" 
                        self.graph.add_node(GraphNode(
                            id=mod_id,
                            type=NodeType.MODULE,
                            name=module_name,
                            file_path="",
                            metadata={"external": True}
                        ))
                        self.graph.add_edge(GraphEdge(
                            source_id=file_id,
                            target_id=mod_id,
                            type=EdgeType.IMPORTS
                        ))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod_id = f"module:{node.module}"
                        self.graph.add_node(GraphNode(
                            id=mod_id,
                            type=NodeType.MODULE,
                            name=node.module,
                            file_path="",
                            metadata={"external": True}
                        ))
                        self.graph.add_edge(GraphEdge(
                            source_id=file_id,
                            target_id=mod_id,
                            type=EdgeType.IMPORTS
                        ))

        except SyntaxError:
            logger.warning(f"Failed to parse Python file: {file_path}")

    def _process_regex(self, file_id: str, file_path: str, content: str, suffix: str):
        # Basic regex for Classes and Functions
        # C#:  public class Foo
        # TS:  export class Foo
        
        class_pattern = r"(?:class|interface)\s+(\w+)"
        func_pattern = r"(?:void|int|string|bool|public|private|protected)\s+(\w+)\s*\("
        
        if suffix in [".ts", ".js"]:
             func_pattern = r"function\s+(\w+)\s*\("

        # Find Classes
        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            class_id = f"class:{name}:{file_path}"
            self.graph.add_node(GraphNode(
                id=class_id,
                type=NodeType.CLASS,
                name=name,
                file_path=file_path
            ))
            self.graph.add_edge(GraphEdge(
                source_id=file_id,
                target_id=class_id,
                type=EdgeType.DEFINES
            ))

        # Find Functions
        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            # Skip common keywords if regex is too loose (e.g. 'if', 'for')
            if name in ["if", "for", "while", "switch", "catch"]:
                continue
                
            func_id = f"func:{name}:{file_path}"
            self.graph.add_node(GraphNode(
                id=func_id,
                type=NodeType.FUNCTION,
                name=name,
                file_path=file_path
            ))
            self.graph.add_edge(GraphEdge(
                source_id=file_id,
                target_id=func_id,
                type=EdgeType.DEFINES
            ))
