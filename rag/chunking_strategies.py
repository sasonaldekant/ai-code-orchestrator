"""Advanced chunking strategies for document processing.

Provides multiple chunking strategies optimized for different content types:
- SemanticChunker: Split on natural language boundaries (paragraphs, sentences)
- CodeChunker: Language-aware code splitting (functions, classes, methods)
- RecursiveChunker: Hierarchical splitting with multiple separators
- MarkdownChunker: Preserve markdown structure (headers, code blocks)

All chunkers support:
- Configurable chunk size and overlap
- Metadata preservation
- Adaptive sizing based on content
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    metadata: Dict[str, Any]
    start_char: int
    end_char: int


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split text into chunks."""
        pass


class SemanticChunker(ChunkingStrategy):
    """
    Semantic chunking that respects natural language boundaries.
    
    Splits on:
    1. Paragraph breaks (\n\n)
    2. Sentence boundaries (. ! ?)
    3. Character limits as fallback
    
    Best for: Documentation, articles, requirements
    """

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split text on semantic boundaries."""
        chunks = []
        
        # Split into paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        current_start = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > self.chunk_size:
                chunks.append(Chunk(
                    text=current_chunk,
                    metadata=metadata.copy(),
                    start_char=current_start,
                    end_char=current_start + len(current_chunk)
                ))
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + "\n\n" + para if overlap_text else para
                current_start += len(current_chunk) - len(overlap_text)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add final chunk
        if current_chunk:
            chunks.append(Chunk(
                text=current_chunk,
                metadata=metadata.copy(),
                start_char=current_start,
                end_char=current_start + len(current_chunk)
            ))
        
        logger.debug(f"SemanticChunker created {len(chunks)} chunks")
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        """Get overlap text from end of chunk."""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Try to split on sentence boundary
        sentences = re.split(r'[.!?]\s+', text)
        overlap = ""
        for sent in reversed(sentences):
            if len(overlap) + len(sent) <= self.chunk_overlap:
                overlap = sent + ". " + overlap
            else:
                break
        
        return overlap.strip() if overlap else text[-self.chunk_overlap:]


class CodeChunker(ChunkingStrategy):
    """
    Language-aware code chunking.
    
    Splits on:
    1. Function/method definitions
    2. Class definitions
    3. Top-level statements
    4. Comment blocks
    
    Best for: Python, C#, JavaScript, TypeScript source code
    """

    LANGUAGE_PATTERNS = {
        'python': {
            'function': r'^(async )?def \w+\(',
            'class': r'^class \w+',
            'comment': r'^#.*$'
        },
        'csharp': {
            'function': r'(public|private|protected|internal)\s+\w+\s+\w+\s*\(',
            'class': r'(public|private|protected|internal)?\s*class\s+\w+',
            'comment': r'^//.*$|^/\*.*\*/$'
        },
        'javascript': {
            'function': r'(async )?function\s+\w+\(|const\s+\w+\s*=\s*\(',
            'class': r'class\s+\w+',
            'comment': r'^//.*$|^/\*.*\*/$'
        },
        'typescript': {
            'function': r'(async )?function\s+\w+\(|const\s+\w+\s*=\s*\(',
            'class': r'(export )?class\s+\w+',
            'comment': r'^//.*$|^/\*.*\*/$'
        }
    }

    def __init__(
        self,
        chunk_size: int = 1200,  # Larger for code
        chunk_overlap: int = 200,
        language: str = 'python'
    ) -> None:
        super().__init__(chunk_size, chunk_overlap)
        self.language = language.lower()
        self.patterns = self.LANGUAGE_PATTERNS.get(self.language, self.LANGUAGE_PATTERNS['python'])

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split code on function/class boundaries."""
        chunks = []
        lines = text.split('\n')
        
        current_chunk_lines = []
        current_start_line = 0
        current_char_pos = 0
        
        for i, line in enumerate(lines):
            # Check if line starts a new function or class
            is_boundary = any(
                re.match(pattern, line.strip(), re.MULTILINE)
                for pattern in self.patterns.values()
            )
            
            current_text = '\n'.join(current_chunk_lines)
            
            # If we hit a boundary and chunk is large enough, save it
            if is_boundary and current_chunk_lines and len(current_text) >= self.chunk_size // 2:
                chunks.append(Chunk(
                    text=current_text,
                    metadata={**metadata, 'start_line': current_start_line, 'end_line': i},
                    start_char=current_char_pos,
                    end_char=current_char_pos + len(current_text)
                ))
                
                # Start new chunk with overlap
                overlap_lines = self._get_overlap_lines(current_chunk_lines)
                current_chunk_lines = overlap_lines + [line]
                current_start_line = i - len(overlap_lines)
                current_char_pos += len(current_text) - len('\n'.join(overlap_lines))
            else:
                current_chunk_lines.append(line)
            
            # Force split if chunk too large
            if len(current_text) > self.chunk_size * 1.5:
                chunks.append(Chunk(
                    text=current_text,
                    metadata={**metadata, 'start_line': current_start_line, 'end_line': i},
                    start_char=current_char_pos,
                    end_char=current_char_pos + len(current_text)
                ))
                current_chunk_lines = [line]
                current_start_line = i
                current_char_pos += len(current_text)
        
        # Add final chunk
        if current_chunk_lines:
            final_text = '\n'.join(current_chunk_lines)
            chunks.append(Chunk(
                text=final_text,
                metadata={**metadata, 'start_line': current_start_line, 'end_line': len(lines)},
                start_char=current_char_pos,
                end_char=current_char_pos + len(final_text)
            ))
        
        logger.debug(f"CodeChunker ({self.language}) created {len(chunks)} chunks")
        return chunks
    
    def _get_overlap_lines(self, lines: List[str]) -> List[str]:
        """Get overlap lines from end of chunk."""
        overlap_text = ''
        overlap_lines = []
        
        for line in reversed(lines):
            if len(overlap_text) + len(line) <= self.chunk_overlap:
                overlap_lines.insert(0, line)
                overlap_text += line + '\n'
            else:
                break
        
        return overlap_lines


class RecursiveChunker(ChunkingStrategy):
    """
    Hierarchical recursive chunking.
    
    Tries multiple separators in order:
    1. Double newline (paragraphs)
    2. Single newline (lines)
    3. Sentence boundaries
    4. Word boundaries
    5. Character splitting
    
    Best for: Mixed content, general text
    """

    SEPARATORS = [
        "\n\n",  # Paragraphs
        "\n",    # Lines
        ". ",    # Sentences
        " ",     # Words
        ""       # Characters
    ]

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Recursively split text using multiple separators."""
        return self._recursive_split(text, metadata, 0, 0, self.SEPARATORS)
    
    def _recursive_split(
        self,
        text: str,
        metadata: Dict[str, Any],
        start_char: int,
        depth: int,
        separators: List[str]
    ) -> List[Chunk]:
        """Recursively split text."""
        if len(text) <= self.chunk_size:
            return [Chunk(
                text=text,
                metadata=metadata.copy(),
                start_char=start_char,
                end_char=start_char + len(text)
            )]
        
        # Try each separator
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                chunks = []
                current_chunk = ""
                current_pos = start_char
                
                for part in parts:
                    if len(current_chunk) + len(part) + len(sep) <= self.chunk_size:
                        current_chunk += part + sep
                    else:
                        if current_chunk:
                            chunks.append(Chunk(
                                text=current_chunk.rstrip(sep),
                                metadata=metadata.copy(),
                                start_char=current_pos,
                                end_char=current_pos + len(current_chunk)
                            ))
                            current_pos += len(current_chunk)
                        current_chunk = part + sep
                
                if current_chunk:
                    chunks.append(Chunk(
                        text=current_chunk.rstrip(sep),
                        metadata=metadata.copy(),
                        start_char=current_pos,
                        end_char=current_pos + len(current_chunk)
                    ))
                
                return chunks
        
        # Fallback: character split
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            chunks.append(Chunk(
                text=chunk_text,
                metadata=metadata.copy(),
                start_char=start_char + i,
                end_char=start_char + i + len(chunk_text)
            ))
        
        return chunks


class MarkdownChunker(ChunkingStrategy):
    """
    Markdown-aware chunking that preserves structure.
    
    Splits on:
    1. Headers (# ## ###)
    2. Code blocks (```)
    3. Horizontal rules (---)
    4. Paragraph breaks
    
    Preserves markdown formatting and hierarchy.
    Best for: Documentation, README files, technical specs
    """

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split markdown preserving structure."""
        chunks = []
        lines = text.split('\n')
        
        current_section = []
        current_header = None
        current_start = 0
        in_code_block = False
        
        for i, line in enumerate(lines):
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            
            # Check for headers (only outside code blocks)
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match and not in_code_block:
                # Save previous section
                if current_section:
                    section_text = '\n'.join(current_section)
                    if len(section_text.strip()) > 0:
                        chunks.append(Chunk(
                            text=section_text,
                            metadata={
                                **metadata,
                                'header': current_header,
                                'section_start': current_start
                            },
                            start_char=current_start,
                            end_char=current_start + len(section_text)
                        ))
                        current_start += len(section_text)
                
                # Start new section
                current_header = header_match.group(2)
                current_section = [line]
            else:
                current_section.append(line)
            
            # Force split if section too large
            section_text = '\n'.join(current_section)
            if len(section_text) > self.chunk_size and not in_code_block:
                chunks.append(Chunk(
                    text=section_text,
                    metadata={
                        **metadata,
                        'header': current_header,
                        'section_start': current_start
                    },
                    start_char=current_start,
                    end_char=current_start + len(section_text)
                ))
                current_section = []
                current_start += len(section_text)
        
        # Add final section
        if current_section:
            section_text = '\n'.join(current_section)
            if len(section_text.strip()) > 0:
                chunks.append(Chunk(
                    text=section_text,
                    metadata={
                        **metadata,
                        'header': current_header,
                        'section_start': current_start
                    },
                    start_char=current_start,
                    end_char=current_start + len(section_text)
                ))
        
        logger.debug(f"MarkdownChunker created {len(chunks)} chunks")
        return chunks


def create_chunker(
    content_type: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    language: Optional[str] = None
) -> ChunkingStrategy:
    """Factory function to create appropriate chunker."""
    if content_type in ['py', 'python', 'cs', 'csharp', 'js', 'javascript', 'ts', 'typescript']:
        lang = language or content_type
        return CodeChunker(chunk_size, chunk_overlap, lang)
    elif content_type in ['md', 'markdown']:
        return MarkdownChunker(chunk_size, chunk_overlap)
    elif content_type in ['txt', 'text', 'doc']:
        return SemanticChunker(chunk_size, chunk_overlap)
    else:
        return RecursiveChunker(chunk_size, chunk_overlap)
