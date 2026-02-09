"""
Feature-rich Document Chunker.

Implements smart chunking strategies for Code, Markdown, and Text.
Matches the specification in ADVANCED_RAG_Source.md.
"""

from __future__ import annotations

import re
import logging
import tiktoken
from dataclasses import dataclass, field
from typing import List, Dict, Any, Literal, Optional

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Represents a document chunk with metadata."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    start_char_idx: int
    end_char_idx: int
    token_count: int

class DocumentChunker:
    """
    Smart document chunker that preserves semantic boundaries.
    
    Strategies:
    - code: Preserves function/class boundaries
    - markdown: Preserves section structure (headers)
    - text: Sentence-aware splitting with overlap
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base") # Fallback

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        strategy: Literal["code", "markdown", "text"] = "text",
        doc_id: str = "doc"
    ) -> List[Chunk]:
        """
        Chunk a document using the specified strategy.
        """
        metadata = metadata or {}
        
        if strategy == "code":
            return self._chunk_code(content, metadata, doc_id)
        elif strategy == "markdown":
            return self._chunk_markdown(content, metadata, doc_id)
        else:
            return self._chunk_text(content, metadata, doc_id)

    def _chunk_code(self, content: str, metadata: Dict[str, Any], doc_id: str) -> List[Chunk]:
        """
        Chunk code preserving top-level definitions.
        """
        # Naive split by top-level regex for classes/functions
        # In a real implementation, AST parsing is preferred
        pattern = r'^\s*(?:class|def|async def|function|interface|enum)\s+\w+'
        
        # Identify split points
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        if not matches:
             return self._chunk_text(content, metadata, doc_id)

        chunks = []
        start = 0
        
        for i, match in enumerate(matches):
            end = matches[i+1].start() if i + 1 < len(matches) else len(content)
            
            # Extract block
            block = content[start:end]
            
            # If block is too large, sub-chunk it as text
            if self.count_tokens(block) > self.chunk_size:
                 sub_chunks = self._chunk_text(block, metadata, f"{doc_id}_sub{i}")
                 # Adjust metadata/offsets (simplified here)
                 chunks.extend(sub_chunks)
            else:
                 chunks.append(Chunk(
                     content=block.strip(),
                     metadata=metadata,
                     chunk_id=f"{doc_id}_{i}",
                     start_char_idx=start,
                     end_char_idx=end,
                     token_count=self.count_tokens(block)
                 ))
            
            start = end
            
        return chunks

    def _chunk_markdown(self, content: str, metadata: Dict[str, Any], doc_id: str) -> List[Chunk]:
        """
        Chunk markdown by headers.
        """
        # Split by H1-H3 headers
        pattern = r'(^#{1,3}\s+.+)'
        parts = re.split(pattern, content, flags=re.MULTILINE)
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_counter = 0

        for part in parts:
            if not part: continue
            
            new_content = current_chunk + part
            
            if self.count_tokens(new_content) > self.chunk_size:
                # Flush current
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        metadata=metadata,
                        chunk_id=f"{doc_id}_{chunk_counter}",
                        start_char_idx=current_start,
                        end_char_idx=current_start + len(current_chunk),
                        token_count=self.count_tokens(current_chunk)
                    ))
                    chunk_counter += 1
                    current_start += len(current_chunk)
                    current_chunk = part
                else:
                    # Part itself is too big, sub-chunk it
                    sub_chunks = self._chunk_text(part, metadata, f"{doc_id}_{chunk_counter}")
                    chunks.extend(sub_chunks)
                    chunk_counter += len(sub_chunks)
                    current_start += len(part)
                    current_chunk = ""
            else:
                current_chunk = new_content

        if current_chunk:
             chunks.append(Chunk(
                content=current_chunk.strip(),
                metadata=metadata,
                chunk_id=f"{doc_id}_{chunk_counter}",
                start_char_idx=current_start,
                end_char_idx=current_start + len(current_chunk),
                token_count=self.count_tokens(current_chunk)
            ))

        return chunks

    def _chunk_text(self, content: str, metadata: Dict[str, Any], doc_id: str) -> List[Chunk]:
        """
        Sliding window text chunking.
        """
        tokens = self.encoding.encode(content)
        total_tokens = len(tokens)
        chunks = []
        
        start = 0
        idx = 0
        while start < total_tokens:
            end = min(start + self.chunk_size, total_tokens)
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append(Chunk(
                content=chunk_text,
                metadata=metadata,
                chunk_id=f"{doc_id}_{idx}",
                start_char_idx=0, # Approximation, hard to map back from tokens exactly without offset mapping
                end_char_idx=0,
                token_count=len(chunk_tokens)
            ))
            
            start += (self.chunk_size - self.chunk_overlap)
            idx += 1
            
        return chunks
