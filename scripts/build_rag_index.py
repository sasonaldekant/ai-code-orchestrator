"""
Script to ingest generic files into the RAG vector store.
Matches the CLI described in ADVANCED_RAG_Source.md.
"""

import argparse
import logging
from pathlib import Path
from typing import List
import json

from core.retriever_v2 import EnhancedRAGRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Build RAG Index from Files")
    parser.add_argument("--directory", help="Directory to index")
    parser.add_argument("--file", help="Single file to index")
    parser.add_argument("--json", help="JSON file with documents to index")
    parser.add_argument("--pattern", default="**/*", help="Glob pattern for directory scan")
    parser.add_argument("--collection", default="generic_knowledge", help="Vector store collection name")
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    parser.add_argument("--reset", action="store_true", help="Reset collection before indexing")
    
    args = parser.parse_args()
    
    retriever = EnhancedRAGRetriever(
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    if args.reset:
        logger.warning(f"Resetting collection '{args.collection}'...")
        retriever.client.delete_collection(args.collection)
        retriever = EnhancedRAGRetriever(
            collection_name=args.collection,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )

    count = 0

    # 1. Directory
    if args.directory:
        path = Path(args.directory)
        if not path.exists():
            print(f"Directory not found: {path}")
            return
            
        files = list(path.glob(args.pattern))
        print(f"Found {len(files)} files matching '{args.pattern}' in {path}")
        
        for f in files:
            if f.is_file():
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    strategy = "code" if f.suffix in [".py", ".ts", ".tsx", ".js", ".cs"] else "markdown" if f.suffix == ".md" else "text"
                    
                    chunks = retriever.add_document(
                        content=content,
                        metadata={"source": str(f), "filename": f.name},
                        chunking_strategy=strategy
                    )
                    count += chunks
                    print(f"Indexed {f.name}: {chunks} chunks")
                except Exception as e:
                    logger.error(f"Failed to process {f}: {e}")

    # 2. Single File
    if args.file:
        f = Path(args.file)
        if f.exists():
             content = f.read_text(encoding="utf-8")
             strategy = "code" if f.suffix in [".py", ".ts", ".tsx", ".js", ".cs"] else "markdown" if f.suffix == ".md" else "text"
             chunks = retriever.add_document(content, {"source": str(f)}, chunking_strategy=strategy)
             count += chunks
             print(f"Indexed {f.name}: {chunks} chunks")

    # 3. JSON dump
    if args.json:
        f = Path(args.json)
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                 for item in data:
                     retriever.add_document(
                         content=item.get("content", ""),
                         metadata=item.get("metadata", {}),
                         doc_id=item.get("id"),
                         chunking_strategy="text"
                     )
                 print(f"Indexed {len(data)} documents from JSON")

    print(f"\nIndexing complete. Total chunks added: {count}")

if __name__ == "__main__":
    main()
