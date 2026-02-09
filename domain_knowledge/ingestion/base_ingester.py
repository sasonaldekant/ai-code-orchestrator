"""Base class for domain knowledge ingesters."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Ingester(ABC):
    """Abstract base class for all domain knowledge ingesters."""

    @abstractmethod
    def ingest(self) -> List['Document']:
        """
        Ingest domain knowledge and return a list of documents.
        
        Returns:
            List[Document]: A list of documents ready for embedding.
        """
        pass
