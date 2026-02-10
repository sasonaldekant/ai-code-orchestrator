from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Chunk:
    """Represents a single chunk of content."""
    content: str
    metadata: dict

class BaseChunker:
    """Base class for all chunking strategies."""
    def split(self, content: str, **kwargs) -> List[Chunk]:
        raise NotImplementedError
