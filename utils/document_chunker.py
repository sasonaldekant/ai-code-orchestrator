"""
Document chunking utilities for RAG system.

Provides smart chunking strategies for code and documentation,
preserving context and metadata across chunks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Literal
import tiktoken
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk with metadata."""
    
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    start_index: int
    end_index: int
    token_count: int


class DocumentChunker:
    """
    Smart document chunker that preserves semantic boundaries.
    
    Supports multiple chunking strategies optimized for different content types:
    - code: Preserves function/class boundaries
    - markdown: Preserves section structure
    - text: Sentence-aware splitting
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ) -> None:
        """
        Initialize the chunker.
        
        Parameters
        ----------
        chunk_size : int
            Target chunk size in tokens.
        chunk_overlap : int
            Number of overlapping tokens between chunks.
        encoding_name : str
            Tiktoken encoding to use for token counting.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            logger.warning(
                "chunk_overlap (%s) must be smaller than chunk_size (%s); "
                "clamping overlap to %s",
                chunk_overlap,
                chunk_size,
                chunk_size - 1,
            )
            chunk_overlap = max(chunk_size - 1, 0)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def chunk_document(
        self,
        content: str,
        metadata: Dict[str, Any] | None = None,
        strategy: Literal["code", "markdown", "text"] = "text",
    ) -> List[Chunk]:
        """
        Chunk a document using the specified strategy.
        
        Parameters
        ----------
        content : str
            The document content to chunk.
        metadata : dict, optional
            Metadata to attach to all chunks.
        strategy : str
            Chunking strategy: 'code', 'markdown', or 'text'.
            
        Returns
        -------
        List[Chunk]
            List of document chunks with metadata.
        """
        if metadata is None:
            metadata = {}

        if strategy == "code":
            return self._chunk_code(content, metadata)
        elif strategy == "markdown":
            return self._chunk_markdown(content, metadata)
        else:
            return self._chunk_text(content, metadata)

    def _chunk_code(self, content: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Chunk code preserving function and class boundaries.
        
        Tries to keep functions/classes together. Falls back to sliding window
        for large functions.
        """
        chunks: List[Chunk] = []
        
        # Regex patterns for common code structures
        # Match function definitions (Python, JavaScript, TypeScript, C#, etc.)
        function_pattern = r'((?:async\s+)?(?:public|private|protected|static|async)?\s*(?:function|def|class|interface|enum)\s+\w+[^{]*\{[^}]*\}|(?:async\s+)?(?:public|private|protected|static|async)?\s*(?:function|def|class)\s+\w+.*?(?=\n(?:def|class|function|$)))'
        
        matches = list(re.finditer(function_pattern, content, re.MULTILINE | re.DOTALL))
        
        if not matches:
            # No clear code structure, fall back to text chunking
            return self._chunk_text(content, metadata)
        
        current_pos = 0
        chunk_buffer = []
        buffer_tokens = 0
        
        for match in matches:
            block = match.group(0)
            block_tokens = self.count_tokens(block)
            
            # If single block exceeds chunk size, split it
            if block_tokens > self.chunk_size:
                # Flush current buffer first
                if chunk_buffer:
                    chunk_text = "\n\n".join(chunk_buffer)
                    chunks.append(self._create_chunk(
                        chunk_text, metadata, len(chunks), current_pos, match.start()
                    ))
                    chunk_buffer = []
                    buffer_tokens = 0
                
                # Split large block into smaller chunks
                chunks.extend(self._chunk_text(block, metadata, start_offset=match.start()))
                current_pos = match.end()
            elif buffer_tokens + block_tokens > self.chunk_size:
                # Flush buffer and start new chunk
                if chunk_buffer:
                    chunk_text = "\n\n".join(chunk_buffer)
                    chunks.append(self._create_chunk(
                        chunk_text, metadata, len(chunks), current_pos, match.start()
                    ))
                
                chunk_buffer = [block]
                buffer_tokens = block_tokens
                current_pos = match.start()
            else:
                # Add to current buffer
                chunk_buffer.append(block)
                buffer_tokens += block_tokens
        
        # Flush remaining buffer
        if chunk_buffer:
            chunk_text = "\n\n".join(chunk_buffer)
            chunks.append(self._create_chunk(
                chunk_text, metadata, len(chunks), current_pos, len(content)
            ))
        
        return chunks

    def _chunk_markdown(self, content: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Chunk markdown preserving section structure.
        
        Tries to keep sections together based on headers.
        """
        chunks: List[Chunk] = []
        
        # Split by markdown headers
        sections = re.split(r'(^#{1,6}\s+.+$)', content, flags=re.MULTILINE)
        
        chunk_buffer = []
        buffer_tokens = 0
        current_pos = 0
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
                
            section_tokens = self.count_tokens(section)
            
            if section_tokens > self.chunk_size:
                # Flush buffer
                if chunk_buffer:
                    chunk_text = "".join(chunk_buffer)
                    chunks.append(self._create_chunk(
                        chunk_text, metadata, len(chunks), current_pos, current_pos + len(chunk_text)
                    ))
                    chunk_buffer = []
                    buffer_tokens = 0
                
                # Split large section
                chunks.extend(self._chunk_text(section, metadata, start_offset=current_pos))
                current_pos += len(section)
            elif buffer_tokens + section_tokens > self.chunk_size:
                # Flush and start new
                if chunk_buffer:
                    chunk_text = "".join(chunk_buffer)
                    chunks.append(self._create_chunk(
                        chunk_text, metadata, len(chunks), current_pos, current_pos + len(chunk_text)
                    ))
                
                chunk_buffer = [section]
                buffer_tokens = section_tokens
                current_pos += len("".join(sections[:i]))
            else:
                chunk_buffer.append(section)
                buffer_tokens += section_tokens
        
        # Flush remaining
        if chunk_buffer:
            chunk_text = "".join(chunk_buffer)
            chunks.append(self._create_chunk(
                chunk_text, metadata, len(chunks), current_pos, len(content)
            ))
        
        return chunks

    def _chunk_text(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        start_offset: int = 0
    ) -> List[Chunk]:
        """
        Chunk text with sentence-aware splitting and overlap.
        
        Uses sliding window with overlap for better context preservation.
        """
        chunks: List[Chunk] = []
        tokens = self.encoding.encode(content)
        
        start_idx = 0
        chunk_id = 0
        
        while start_idx < len(tokens):
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Try to end at sentence boundary
            if end_idx < len(tokens):
                # Look for sentence endings near the boundary
                last_sentences = re.finditer(r'[.!?]\s+', chunk_text)
                sentence_ends = [m.end() for m in last_sentences]
                
                if sentence_ends:
                    # Use the last sentence ending
                    cut_point = sentence_ends[-1]
                    chunk_text = chunk_text[:cut_point]
                    # Recalculate actual token count
                    chunk_tokens = self.encoding.encode(chunk_text)
            
            chunk = Chunk(
                content=chunk_text.strip(),
                metadata=metadata.copy(),
                chunk_id=f"chunk_{chunk_id}",
                start_index=start_offset + start_idx,
                end_index=start_offset + start_idx + len(chunk_tokens),
                token_count=len(chunk_tokens),
            )
            chunks.append(chunk)
            
            # Move window with overlap
            step = max(self.chunk_size - self.chunk_overlap, 1)
            start_idx += step
            chunk_id += 1
        
        return chunks

    def _create_chunk(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_id: int,
        start_index: int,
        end_index: int,
    ) -> Chunk:
        """Helper to create a Chunk object."""
        return Chunk(
            content=content.strip(),
            metadata=metadata.copy(),
            chunk_id=f"chunk_{chunk_id}",
            start_index=start_index,
            end_index=end_index,
            token_count=self.count_tokens(content),
        )
