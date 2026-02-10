"""Embeddings provider with support for multiple models.

Supports:
- OpenAI embeddings (text-embedding-3-small, text-embedding-3-large)
- HuggingFace models for local inference (no API calls)
- Cached embeddings to reduce API costs
- Batch processing for efficiency

Default: text-embedding-3-small for best cost/performance ratio
($0.02 per 1M tokens vs $0.13 for large model)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging
import hashlib
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingsProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass


class OpenAIEmbeddings(EmbeddingsProvider):
    """
    OpenAI embeddings provider.
    
    Models:
    - text-embedding-3-small: $0.02/1M tokens, 1536 dims (default)
    - text-embedding-3-large: $0.13/1M tokens, 3072 dims
    - text-embedding-ada-002: $0.10/1M tokens, 1536 dims (legacy)
    """

    DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536
    }

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        batch_size: int = 100
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI not installed. Install with: pip install openai"
            )

        self.model = model
        self.batch_size = batch_size
        self._dimension = self.DIMENSIONS.get(model, 1536)
        
        # Initialize client
        import os
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        logger.info(f"Initialized OpenAI embeddings (model={model})")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(
                    f"Generated {len(batch_embeddings)} embeddings "
                    f"(batch {i // self.batch_size + 1})"
                )
            except Exception as e:
                logger.error(f"OpenAI embedding error: {e}")
                # Return zero vectors on error
                all_embeddings.extend([[0.0] * self._dimension] * len(batch))
        
        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        return self._dimension


class HuggingFaceEmbeddings(EmbeddingsProvider):
    """
    HuggingFace embeddings for local inference.
    
    No API calls, runs locally on CPU.
    Popular models:
    - sentence-transformers/all-MiniLM-L6-v2: 384 dims, fast
    - sentence-transformers/all-mpnet-base-v2: 768 dims, accurate
    - BAAI/bge-small-en-v1.5: 384 dims, good quality
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu"
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.device = device
        
        # Load model
        logger.info(f"Loading HuggingFace model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self._dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(
            f"Initialized HuggingFace embeddings "
            f"(model={model_name}, dim={self._dimension})"
        )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"HuggingFace embedding error: {e}")
            return [[0.0] * self._dimension] * len(texts)

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        return self._dimension


class CachedEmbeddings(EmbeddingsProvider):
    """
    Wrapper that caches embeddings to reduce API costs.
    
    Uses SHA-256 hash of text as cache key.
    Stores embeddings in JSON file.
    """

    def __init__(
        self,
        provider: EmbeddingsProvider,
        cache_path: str = "rag/embeddings_cache.json"
    ) -> None:
        self.provider = provider
        self.cache_path = Path(cache_path)
        self.cache: Dict[str, List[float]] = {}
        self._load_cache()
        
        logger.info(f"Initialized cached embeddings (cache_path={cache_path})")

    def _load_cache(self) -> None:
        """Load cache from disk."""
        if self.cache_path.exists():
            try:
                self.cache = json.loads(self.cache_path.read_text())
                logger.info(f"Loaded {len(self.cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.cache = {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache))
            logger.debug(f"Saved {len(self.cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with caching."""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                embeddings.append(self.cache[cache_key])
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            logger.debug(f"Generating {len(uncached_texts)} new embeddings")
            new_embeddings = self.provider.embed_texts(uncached_texts)
            
            # Update cache and results
            for text, embedding, idx in zip(
                uncached_texts, new_embeddings, uncached_indices
            ):
                cache_key = self._get_cache_key(text)
                self.cache[cache_key] = embedding
                embeddings[idx] = embedding
            
            # Save cache
            self._save_cache()
        else:
            logger.debug(f"All {len(texts)} embeddings from cache")
        
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        return self.provider.dimension


def create_embeddings_provider(
    provider_type: str = "openai",
    model: Optional[str] = None,
    use_cache: bool = True,
    **kwargs
) -> EmbeddingsProvider:
    """
    Factory function to create embeddings provider.
    
    Parameters
    ----------
    provider_type : str
        One of: 'openai', 'huggingface'
    model : str, optional
        Model name. Defaults:
        - openai: text-embedding-3-small
        - huggingface: sentence-transformers/all-MiniLM-L6-v2
    use_cache : bool
        Whether to cache embeddings (default: True)
    **kwargs
        Additional provider-specific arguments
    
    Returns
    -------
    EmbeddingsProvider
        Configured embeddings provider
    """

    if provider_type == "openai":
        try:
            model = model or "text-embedding-3-small"
            provider = OpenAIEmbeddings(model=model, **kwargs)
        except ImportError:
            logger.warning("OpenAI not available. Using MockEmbeddingsProvider.")
            from rag.mock_embeddings import MockEmbeddingsProvider
            provider = MockEmbeddingsProvider(model_name="mock-fallback")

    elif provider_type == "huggingface":
        model = model or "sentence-transformers/all-MiniLM-L6-v2"
        try:
            provider = HuggingFaceEmbeddings(model_name=model, **kwargs)
        except Exception as e:
            logger.warning(f"HuggingFace embeddings not available ({e}). Falling back to MockEmbeddingsProvider.")
            from rag.mock_embeddings import MockEmbeddingsProvider
            provider = MockEmbeddingsProvider(model_name=model)
            
    elif provider_type == "mock":
        from rag.mock_embeddings import MockEmbeddingsProvider
        provider = MockEmbeddingsProvider(model_name=model or "mock-model")
        
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    # Wrap with cache if enabled
    if use_cache:
        cache_path = kwargs.get("cache_path", "rag/embeddings_cache.json")
        provider = CachedEmbeddings(provider, cache_path)
    
    return provider
