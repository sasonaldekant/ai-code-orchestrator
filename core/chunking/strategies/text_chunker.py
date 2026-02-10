from typing import List
from ..base import BaseChunker, Chunk

class TextChunker(BaseChunker):
    """
    Standard recursive character splitting for text/markdown.
    """
    
    def split(self, content: str, chunk_size: int = 800, overlap: int = 120) -> List[Chunk]:
        # Safety check for overlap
        if overlap >= chunk_size:
            overlap = chunk_size // 10
            
        chunks = []
        if len(content) <= chunk_size:
            return [Chunk(content=content, metadata={"type": "full_text"})]
            
        for i in range(0, len(content), chunk_size - overlap):
            chunk_content = content[i:i + chunk_size]
            chunks.append(Chunk(
                content=chunk_content, 
                metadata={
                    "type": "text_chunk",
                    "index": i // (chunk_size - overlap)
                }
            ))
        return chunks
