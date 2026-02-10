
"""
Demo for Graph-Enhanced Retrieval
"""
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.graph.schema import KnowledgeGraph
from core.graph.ingester import GraphIngester
from core.graph.retriever import GraphRetriever

logging.basicConfig(level=logging.ERROR)

SAMPLE_CODE = """
class DataService:
    def connect(self):
        print("Connecting to DB...")

    def fetch_data(self):
        self.connect()
        return {"data": 123}

class ReportGenerator:
    def generate(self, service):
        data = service.fetch_data()
        print(f"Generating report with {data}")
"""

def main():
    print("--- 🚀 Demo: Graph-Enhanced Retrieval ---")
    
    # 1. Build Graph from sample code
    print("Building Knowledge Graph...")
    graph = KnowledgeGraph()
    ingester = GraphIngester(graph)
    ingester.process_file("src/data_service.py", SAMPLE_CODE)
    
    retriever = GraphRetriever(graph)

    # 2. Simulate Retrieval of a specific function
    # Suppose Vector Search found "generate" function in ReportGenerator
    target_node_id = "func:generate:src/data_service.py"
    
    print(f"\nTarget Search Result: {target_node_id}")
    
    # 3. Expand Context (Graph RAG)
    print("\nExpanding Context (1-Hop)...")
    # For this demo, we manually add edges because AST parsing of the string above won't catch dynamic typing like 'service.fetch_data()' 
    # unless we have sophisticated type inference. 
    # BUT, the ingester DOES catch 'defines'.
    # Let's inspect what we have.
    
    # Let's verify what nodes we have first
    # for n in graph.nodes: print(n)

    # AST Ingester will parse:
    # - class DataService
    # - func connect
    # - func fetch_data
    # - class ReportGenerator
    # - func generate
    
    # It won't catch "ReportGenerator calls DataService" easily without type hints or detailed analysis.
    # However, let's look for "defines" edges from the file.
    
    context_nodes = retriever.expand_context([target_node_id])
    
    print(f"Found {len(context_nodes)} related nodes.")
    for node in context_nodes:
        print(f" - [{node.type.value}] {node.name} ({node.id})")
        
    print("\n--- Formatted Context for LLM ---")
    print(retriever.format_context(context_nodes))
    
    print("\nDone.")

if __name__ == "__main__":
    main()
