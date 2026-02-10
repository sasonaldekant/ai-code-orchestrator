from typing import List, Dict, Any, Callable, Awaitable
from .chunking.engine import ChunkingEngine, Chunk
import asyncio

class AgentHelper:
    """
    Utilities for specialist agents to handle complexity and scale.
    """
    
    def __init__(self):
        self.chunker = ChunkingEngine()

    async def process_large_content(
        self, 
        content: str, 
        file_path: str,
        process_fn: Callable[[str], Awaitable[Any]],
        chunk_size: int = 4000,
        overlap: int = 200
    ) -> List[Any]:
        """
        Splits large content and processes each chunk using the provided function.
        Useful for agents dealing with massive files.
        """
        chunks = self.chunker.chunk_content(
            content, 
            file_path=file_path, 
            chunk_size=chunk_size, 
            overlap=overlap
        )
        
        results = []
        for chunk in chunks:
            result = await process_fn(chunk.content)
            results.append(result)
            
        return results
