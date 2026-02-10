
"""
Demo for Retrieval Agent (Investigator Mode)
"""
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.vector_store import InMemoryVectorStore, Document
from core.graph.schema import KnowledgeGraph
from core.graph.ingester import GraphIngester
from core.graph.retriever import GraphRetriever
from core.agent.retrieval_agent import RetrievalAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Data
CODE_FILE = "src/auth.py"
CODE_CONTENT = """
class AuthProvider:
    def login(self, user, password):
        self.validate(user)
        print("Logging in...")

    def validate(self, user):
        return True

def logout(user):
    print("Logging out...")
"""

def main():
    print("--- 🚀 Demo: Retrieval Agent (Investigator) ---")
    
    # 1. Setup Keyword/Vector Search
    print("Initializing Vector Store...")
    vector_store = InMemoryVectorStore() 
    # Mocking embedding function for InMemoryStore interaction (if needed) or just relies on loose matching?
    # Actually InMemoryStore needs an embedding function to work. 
    # Let's use a dummy one for the demo to avoid dependency load, 
    # OR we can just mock the search method if we want to test the Agent logic only.
    
    # Let's populate it properly with a dummy embedding function
    def dummy_embedding_fn(texts):
        return [[0.1] * 384 for _ in texts] # Mock 384-dim embeddings
        
    vector_store.embedding_function = dummy_embedding_fn
    
    vector_store.add_documents([
        Document(
            id="doc1", 
            text=CODE_CONTENT, 
            metadata={"source": CODE_FILE, "file_path": CODE_FILE}
        )
    ])
    
    # 2. Setup Knowledge Graph
    print("Initializing Knowledge Graph...")
    graph = KnowledgeGraph()
    ingester = GraphIngester(graph)
    ingester.process_file(CODE_FILE, CODE_CONTENT)
    graph_retriever = GraphRetriever(graph)
    
    # 3. Setup Agent
    print("Initializing Agent...")
    agent = RetrievalAgent(vector_store, graph_retriever)
    
    # 4. Run Investigation
    query = "How does login work?"
    print(f"\n🕵️ Investigating: '{query}'")
    
    # We mock the vector search return to ensure we get our document despite dummy embeddings
    # In a real scenario, the embedding model handles this.
    # For this demo, let's rely on the fact that we only have 1 doc, so it will be returned.
    
    report = agent.investigate(query)
    
    print("\n--- 📄 Investigation Report ---")
    print(f"Query: {report['query']}")
    print(f"Entry Points Found: {report['entry_points']}")
    
    print("\n--- Graph Context ---")
    print(report['graph_context'])
    
    print("\n--- Final Constructed Prompt (Snippet) ---")
    prompt = agent.format_final_prompt(report)
    print(prompt[:500] + "...")
    
    print("\nDone.")

if __name__ == "__main__":
    main()
