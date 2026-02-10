import os
from typing import List
from .base import Chunk
from .strategies.code_chunker import CodeChunker
from .strategies.text_chunker import TextChunker

class ChunkingEngine:
    """
    Orchestrates different chunking strategies based on file content.
    """
    
    CODE_EXTENSIONS = {'.py', '.cs', '.ts', '.tsx', '.js', '.jsx', '.java', '.go', '.cpp', '.h'}
    
    def __init__(self):
        self.code_chunker = CodeChunker()
        self.text_chunker = TextChunker()
        
    def get_recommendations(self, content: str, file_path: str) -> List[str]:
        """
        Analyzes content and provides optimization recommendations.
        """
        recs = []
        size = len(content)
        extension = os.path.splitext(file_path)[1].lower() if file_path else ""
        
        # 1. Size-based recommendations
        if size > 50000:
            recs.append(f"Very large file detected ({size} chars). Consider breaking into smaller modules.")
        
        # 2. File type based recommendations
        if ".g.cs" in file_path.lower() or "generated" in file_path.lower():
            recs.append("Generated file detected. Consider filtering this from ingestion to save tokens.")
            
        # 3. Parameter optimization
        if size < 2000:
            recs.append("File is small. Using a single chunk is optimal.")
        elif extension in self.CODE_EXTENSIONS:
            recs.append("Logical code chunking is active (Phase 10). Chunk size ~1000 is optimal for semantic integrity.")
        else:
            recs.append("Consider reducing overlap to 100 for ~10% token savings in large text documents.")
            
        return recs

    def chunk_content(self, content: str, file_path: str = None, chunk_size: int = 1000, overlap: int = 100) -> List[Chunk]:
        """
        Main entry point for chunking.
        """
        if not content:
            return []
            
        extension = os.path.splitext(file_path)[1].lower() if file_path else None
        
        if extension in self.CODE_EXTENSIONS:
            return self.code_chunker.split(content, chunk_size=chunk_size, overlap=overlap)
        else:
            return self.text_chunker.split(content, chunk_size=chunk_size, overlap=overlap)
