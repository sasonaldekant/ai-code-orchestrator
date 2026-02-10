"""
Mock Retriever for Simulation Mode.
"""
from typing import List, Dict, Any

class MockRetriever:
    """Simulates RAG retrieval without embeddings or vector DB."""
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return dummy documents."""
        return [
            {
                "content": f"Mock document relevant to: {query}",
                "metadata": {"source": "simulation", "type": "knowledge_base"},
                "score": 0.95
            }
        ]
        
    def retrieve_domain_context(self, *args, **kwargs):
        """Return dummy domain context object."""
        # We need a dummy object that has the attributes expected by ContextManager
        class DummyContext:
            database_entities = []
            relationships = []
            components = []
            design_tokens = []
            
            
        return DummyContext()
        
    def format_context_for_prompt(self, context) -> str:
        """Return dummy string context."""
        return '{"mock": "context"}'
