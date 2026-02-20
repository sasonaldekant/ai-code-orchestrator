"""
DynUI Documentation Ingestion Script

Ingests RAG-ready DynUI documentation into Tier 2 (Design Tokens) and Tier 3 (Component Catalog)
with semantic chunking and proper metadata enrichment.

Usage:
    python scripts/ingest_dynui_docs_tier.py
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.chunking_strategies import MarkdownChunker, Chunk
from rag.vector_store import SimplePersistentVectorStore, Document
from rag.embeddings_provider import create_embeddings_provider
from core.settings import get_dynui_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DynUI Docs Location
DYNUI_DOCS_PATH = get_dynui_path() / "docs" / "rag-ready"

# Tier Mapping (from Phase 4 plan)
TIER_MAPPING = {
    "00-INDEX.md": {"tier": 1, "category": "documentation", "priority": "critical"},
    "01-QUICK_START.md": {"tier": 1, "category": "documentation", "priority": "high"},
    "02-DESIGN_TOKENS.md": {"tier": 2, "category": "design_token", "priority": "high"},
    "03-COMPONENT_CATALOG.md": {"tier": 3, "category": "ui_component", "priority": "high"},
    "04-STYLING_GUIDE.md": {"tier": 2, "category": "design_token", "priority": "medium"},
    "05-CODE_EXAMPLES.md": {"tier": 3, "category": "ui_component", "priority": "high"},
    "RAG_GUIDELINES.md": {"tier": 1, "category": "documentation", "priority": "medium"}
}


def extract_section_name(chunk_text: str) -> str:
    """Extract section name from chunk (first H2 or H3 heading)."""
    lines = chunk_text.split('\n')
    for line in lines:
        header_match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if header_match:
            return header_match.group(2).strip()
    return "Unknown Section"


def enrich_metadata(base_metadata: Dict[str, Any], chunk: Chunk, chunk_index: int) -> Dict[str, Any]:
    """Enrich chunk metadata with tier info, keywords, and section details."""
    # Extract section from chunk metadata or text
    section = chunk.metadata.get('header') or extract_section_name(chunk.text)
    
    # Extract keywords from section and first lines
    keywords = []
    if section:
        keywords.extend(section.lower().split())
    
    # Add keywords from chunk content
    first_lines = '\n'.join(chunk.text.split('\n')[:5]).lower()
    if 'var(--dyn-' in first_lines:
        keywords.append('tokens')
    if 'import' in first_lines and 'dyn' in first_lines:
        keywords.append('component')
    
    return {
        **base_metadata,
        "chunk_id": f"{base_metadata['document_id']}-chunk-{chunk_index:03d}",
        "section": section,
        "keywords": list(set(keywords)),
        "char_start": chunk.start_char,
        "char_end": chunk.end_char
    }


def ingest_dynui_documentation():
    """Main ingestion function."""
    logger.info("Starting DynUI documentation ingestion...")
    
    # Verify path
    if not DYNUI_DOCS_PATH.exists():
        logger.error(f"DynUI docs path not found: {DYNUI_DOCS_PATH}")
        return False
    
    # Initialize embedding provider
    logger.info("Initializing embeddings provider...")
    embedding_provider = create_embeddings_provider(
        provider_type="huggingface",
        model="all-MiniLM-L6-v2",
        use_cache=True
    )
    
    # Initialize vector store
    logger.info("Initializing vector store...")
    store = SimplePersistentVectorStore(
        collection_name="code_docs",
        persist_directory="rag/store_data",
        embedding_function=embedding_provider.embed_texts
    )
    
    # Initialize markdown chunker (500-1000 tokens per chunk)
    chunker = MarkdownChunker(chunk_size=1000, chunk_overlap=150)
    
    total_docs = 0
    total_chunks = 0
    
    # Process each document
    for file_name, tier_info in TIER_MAPPING.items():
        file_path = DYNUI_DOCS_PATH / file_name
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
        
        logger.info(f"Processing {file_name} (Tier {tier_info['tier']})...")
        
        # Read file
        content = file_path.read_text(encoding="utf-8")
        
        # Prepare base metadata
        base_metadata = {
            "source": file_name,
            "document_id": file_path.stem,
            "tier": tier_info["tier"],
            "type": tier_info["category"],
            "priority": tier_info["priority"],
            "project": "DynUI"
        }
        
        # Chunk document
        chunks = chunker.chunk_text(content, base_metadata)
        logger.info(f"  Created {len(chunks)} chunks from {file_name}")
        
        # Convert to Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            enriched_meta = enrich_metadata(base_metadata, chunk, i)
            doc_id = enriched_meta["chunk_id"]  # Use chunk_id as document ID
            doc = Document(
                id=doc_id,
                text=chunk.text,
                metadata=enriched_meta
            )
            documents.append(doc)
        
        # Add to vector store
        store.add_documents(documents)
        logger.info(f"  Added {len(documents)} chunks to vector store")
        
        total_docs += 1
        total_chunks += len(documents)
    
    logger.info(f"\n✅ Ingestion complete!")
    logger.info(f"  Total documents processed: {total_docs}")
    logger.info(f"  Total chunks created: {total_chunks}")
    
    # Display stats
    stats = store.get_collection_stats()
    logger.info(f"  Vector store total documents: {stats.get('count', 'unknown')}")
    
    return True


def verify_ingestion():
    """Verify that ingestion worked correctly."""
    logger.info("\nVerifying ingestion...")
    
    # Initialize components
    embedding_provider = create_embeddings_provider(
        provider_type="huggingface",
        model="all-MiniLM-L6-v2",
        use_cache=True
    )
    
    store = SimplePersistentVectorStore(
        collection_name="code_docs",
        persist_directory="rag/store_data",
        embedding_function=embedding_provider.embed_texts
    )
    
    # Test Tier 2 (Design Tokens)
    logger.info("\nTest 1: Tier 2 (Design Tokens) retrieval")
    results = store.search(
        query="primary color token",
        top_k=3,
        filter_metadata={"tier": 2}
    )
    
    logger.info(f"  Found {len(results)} results")
    for i, result in enumerate(results):
        logger.info(f"  [{i+1}] Source: {result.document.metadata.get('source')}")
        logger.info(f"      Section: {result.document.metadata.get('section')}")
        logger.info(f"      Tier: {result.document.metadata.get('tier')}")
        logger.info(f"      Preview: {result.document.text[:100]}...")
    
    # Test Tier 3 (Components)
    logger.info("\nTest 2: Tier 3 (Components) retrieval")
    results = store.search(
        query="DynButton component props",
        top_k=3,
        filter_metadata={"tier": 3}
    )
    
    logger.info(f"  Found {len(results)} results")
    for i, result in enumerate(results):
        logger.info(f"  [{i+1}] Source: {result.document.metadata.get('source')}")
        logger.info(f"      Section: {result.document.metadata.get('section')}")
        logger.info(f"      Tier: {result.document.metadata.get('tier')}")
        logger.info(f"      Preview: {result.document.text[:100]}...")
    
    logger.info("\n✅ Verification complete!")


if __name__ == "__main__":
    success = ingest_dynui_documentation()
    
    if success:
        verify_ingestion()
    else:
        logger.error("Ingestion failed!")
        sys.exit(1)
