
"""
Demo script for GraphRAG Ingestion (AST/Regex)
"""
import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.graph.schema import KnowledgeGraph
from core.graph.ingester import GraphIngester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Python code to parse
SAMPLE_CODE = """
import os
from typing import List

class UserManager:
    def __init__(self, db_conn):
        self.db = db_conn

    def create_user(self, username: str):
        print(f"Creating user {username}")
        self.validate_user(username)

    def validate_user(self, username):
        return True

def standalone_function():
    pass
"""

def main():
    print("--- 🚀 Demo: Knowledge Graph Ingestion ---")
    
    # 1. Setup
    graph = KnowledgeGraph()
    ingester = GraphIngester(graph)
    
    # 2. Process mock file
    file_path = "src/users.py"
    print(f"\nProcessing virtual file: {file_path}")
    ingester.process_file(file_path, SAMPLE_CODE)
    
    # 3. Inspect Graph
    print("\n--- Nodes ---")
    for node_id, node in graph.nodes.items():
        print(f"[{node.type.value.upper()}] {node.name} ({node.id})")
        
    print("\n--- Edges ---")
    for edge in graph.edges:
        print(f"{edge.source_id} --[{edge.type.value}]--> {edge.target_id}")
        
    # 4. JSON Export
    print("\n--- JSON Export (Snippet) ---")
    json_output = graph.to_json()
    print(json.dumps(json_output, indent=2)[:500] + "\n...")

    print("\nDone.")

if __name__ == "__main__":
    main()
