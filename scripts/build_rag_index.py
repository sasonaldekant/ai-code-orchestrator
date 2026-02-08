#!/usr/bin/env python3
"""
CLI tool for building RAG index from various sources.

Supports indexing from:
- Local files and directories
- Git repositories
- Documentation URLs
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.retriever_v2 import EnhancedRAGRetriever

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def index_file(
    retriever: EnhancedRAGRetriever,
    file_path: Path,
    metadata: Dict[str, Any] | None = None,
) -> int:
    """
    Index a single file.
    
    Parameters
    ----------
    retriever : EnhancedRAGRetriever
        The retriever instance.
    file_path : Path
        Path to the file to index.
    metadata : dict, optional
        Additional metadata to attach.
        
    Returns
    -------
    int
        Number of chunks created.
    """
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return 0
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error(f"Failed to read {file_path}: {exc}")
        return 0
    
    # Determine chunking strategy from file extension
    suffix = file_path.suffix.lower()
    if suffix in {".py", ".js", ".ts", ".java", ".cs", ".cpp", ".c", ".go", ".rs"}:
        strategy = "code"
    elif suffix in {".md", ".markdown"}:
        strategy = "markdown"
    else:
        strategy = "text"
    
    # Prepare metadata
    file_metadata = {
        "source": str(file_path),
        "filename": file_path.name,
        "extension": suffix,
        "type": strategy,
    }
    if metadata:
        file_metadata.update(metadata)
    
    # Index the file
    chunks_count = retriever.add_document(
        content=content,
        metadata=file_metadata,
        doc_id=str(file_path),
        chunking_strategy=strategy,
    )
    
    logger.info(f"Indexed {file_path} -> {chunks_count} chunks")
    return chunks_count


def index_directory(
    retriever: EnhancedRAGRetriever,
    directory: Path,
    pattern: str = "**/*",
    exclude: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> int:
    """
    Index all files in a directory.
    
    Parameters
    ----------
    retriever : EnhancedRAGRetriever
        The retriever instance.
    directory : Path
        Directory to index.
    pattern : str
        Glob pattern for file matching.
    exclude : List[str], optional
        Patterns to exclude.
    metadata : dict, optional
        Additional metadata to attach.
        
    Returns
    -------
    int
        Total number of chunks created.
    """
    if not directory.is_dir():
        logger.warning(f"Directory not found: {directory}")
        return 0
    
    exclude = exclude or []
    exclude_patterns = {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
    }
    exclude_patterns.update(exclude)
    
    total_chunks = 0
    total_files = 0
    
    for file_path in directory.glob(pattern):
        if not file_path.is_file():
            continue
        
        # Check exclusions
        if any(excl in str(file_path) for excl in exclude_patterns):
            continue
        
        chunks_count = index_file(retriever, file_path, metadata)
        total_chunks += chunks_count
        total_files += 1
    
    logger.info(
        f"Indexed directory {directory} -> {total_files} files, {total_chunks} chunks"
    )
    return total_chunks


def index_json_documents(
    retriever: EnhancedRAGRetriever,
    json_file: Path,
) -> int:
    """
    Index documents from a JSON file.
    
    Expected format:
    [
        {
            "content": "...",
            "metadata": {...},
            "id": "..."
        },
        ...
    ]
    
    Parameters
    ----------
    retriever : EnhancedRAGRetriever
        The retriever instance.
    json_file : Path
        Path to JSON file.
        
    Returns
    -------
    int
        Number of chunks created.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load JSON file {json_file}: {exc}")
        return 0
    
    if not isinstance(documents, list):
        logger.error(f"JSON file must contain a list of documents")
        return 0
    
    # Determine chunking strategy from metadata if available
    strategy = "text"
    if documents and documents[0].get("metadata", {}).get("type"):
        strategy = documents[0]["metadata"]["type"]
    
    chunks_count = retriever.add_documents_batch(
        documents=documents,
        chunking_strategy=strategy,
    )
    
    logger.info(f"Indexed {len(documents)} documents from {json_file} -> {chunks_count} chunks")
    return chunks_count


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build RAG index from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index a single file
  python scripts/build_rag_index.py --file path/to/document.md
  
  # Index a directory
  python scripts/build_rag_index.py --directory path/to/codebase
  
  # Index from JSON
  python scripts/build_rag_index.py --json path/to/documents.json
  
  # Reset and rebuild index
  python scripts/build_rag_index.py --directory path/to/docs --reset
        """,
    )
    
    parser.add_argument(
        "--file",
        type=Path,
        help="Index a single file",
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Index all files in a directory",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Index documents from JSON file",
    )
    parser.add_argument(
        "--pattern",
        default="**/*",
        help="Glob pattern for directory indexing (default: **/*)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="Patterns to exclude from indexing",
    )
    parser.add_argument(
        "--collection",
        default="code_docs",
        help="ChromaDB collection name (default: code_docs)",
    )
    parser.add_argument(
        "--persist-dir",
        default="./chroma_db",
        help="Directory to persist ChromaDB (default: ./chroma_db)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Chunk size in tokens (default: 512)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Chunk overlap in tokens (default: 50)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the collection before indexing",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show collection statistics",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    # Initialize retriever
    retriever = EnhancedRAGRetriever(
        collection_name=args.collection,
        persist_directory=args.persist_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    
    # Reset if requested
    if args.reset:
        logger.info("Resetting collection...")
        retriever.reset_collection()
    
    # Show stats if requested
    if args.stats:
        stats = retriever.get_collection_stats()
        print("\nCollection Statistics:")
        print(f"  Name: {stats['collection_name']}")
        print(f"  Documents: {stats['document_count']}")
        print(f"  Location: {stats['persist_directory']}")
        return
    
    # Index based on source type
    total_chunks = 0
    
    if args.file:
        total_chunks = index_file(retriever, args.file)
    elif args.directory:
        total_chunks = index_directory(
            retriever,
            args.directory,
            pattern=args.pattern,
            exclude=args.exclude,
        )
    elif args.json:
        total_chunks = index_json_documents(retriever, args.json)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Final stats
    stats = retriever.get_collection_stats()
    print("\n✓ Indexing complete!")
    print(f"  Total chunks created: {total_chunks}")
    print(f"  Total documents in collection: {stats['document_count']}")


if __name__ == "__main__":
    main()
