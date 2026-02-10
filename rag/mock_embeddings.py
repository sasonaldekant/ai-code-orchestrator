import numpy as np
from typing import List, Union

class MockEmbeddingsProvider:
    """
    A mock embeddings provider for testing and development environments
    where heavy ML libraries (sentence-transformers) are not available or compatible.
    Generates deterministic random-like embeddings based on input text length/hash.
    """
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
        self.embedding_dim = 384  # Standard MiniLM dimension

    def encode(self, sentences: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        if isinstance(sentences, str):
            sentences = [sentences]
            
        embeddings = []
        for text in sentences:
            # Create a deterministic seed from the text
            seed = sum(ord(c) for c in text) % 2**32
            rng = np.random.RandomState(seed)
            # Generate random vector
            vector = rng.standard_normal(self.embedding_dim)
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            embeddings.append(vector.tolist())
            
        if len(embeddings) == 1 and isinstance(sentences, str):
            return embeddings[0]
        return embeddings
