import re
from typing import List
from ..base import BaseChunker, Chunk

class CodeChunker(BaseChunker):
    """
    Chunks code based on logical boundaries (classes, functions).
    Primarily supports .ts and .tsx (TypeScript/React). 
    Also compatible with .py, .cs, .js, .jsx for ingestion.
    """
    
    def split(self, content: str, chunk_size: int = 1000, overlap: int = 100) -> List[Chunk]:
        # Safety check for overlap
        if overlap >= chunk_size:
            overlap = chunk_size // 10
            
        # Simple regex-based splitting for now, focused on classes and functions
        # In a real enterprise app, we might use tree-sitter or AST
        
        # Pattern for Python/JS/C#/TS functions and classes
        # Matches: class Name, async function name(), public void Name()
        boundary_pattern = r'\n(?=(?:(?:public|private|protected|internal|static|async|virtual|override|class|def|function|interface|enum|type)\s+))'
        
        parts = re.split(boundary_pattern, content)
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if len(current_chunk) + len(part) <= chunk_size:
                current_chunk += part
            else:
                if current_chunk:
                    chunks.append(Chunk(content=current_chunk.strip(), metadata={"type": "code_block"}))
                
                # If a single part is larger than chunk_size, we must split it by characters
                if len(part) > chunk_size:
                    for i in range(0, len(part), chunk_size - overlap):
                        sub_chunk = part[i:i + chunk_size]
                        chunks.append(Chunk(content=sub_chunk.strip(), metadata={"type": "code_sub_block"}))
                    current_chunk = ""
                else:
                    current_chunk = part
        
        if current_chunk:
            chunks.append(Chunk(content=current_chunk.strip(), metadata={"type": "code_block"}))
            
        return chunks
