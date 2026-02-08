"""
Tests for enhanced RAG retriever.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from core.retriever_v2 import EnhancedRAGRetriever, RetrievalResult


@pytest.fixture
def temp_db_dir():
    """Create temporary directory for ChromaDB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def retriever(temp_db_dir):
    """Create retriever instance with temporary database."""
    return EnhancedRAGRetriever(
        collection_name="test_collection",
        persist_directory=temp_db_dir,
        chunk_size=128,
        chunk_overlap=20,
    )


def test_initialization(retriever, temp_db_dir):
    """Test retriever initialization."""
    assert retriever.collection_name == "test_collection"
    assert retriever.persist_directory == Path(temp_db_dir)
    assert retriever.collection is not None


def test_add_single_document(retriever):
    """Test adding a single document."""
    content = """
    This is a test document about Python programming.
    Python is a high-level programming language.
    It is widely used for web development and data science.
    """
    
    metadata = {"source": "test.txt", "topic": "python"}
    chunks_count = retriever.add_document(
        content=content,
        metadata=metadata,
        doc_id="test_doc_1",
        chunking_strategy="text",
    )
    
    assert chunks_count > 0
    
    stats = retriever.get_collection_stats()
    assert stats["document_count"] == chunks_count


def test_add_code_document(retriever):
    """Test adding code with code chunking strategy."""
    code = """
    def calculate_sum(a, b):
        return a + b
    
    def calculate_product(a, b):
        return a * b
    
    class Calculator:
        def add(self, x, y):
            return x + y
        
        def subtract(self, x, y):
            return x - y
    """
    
    chunks_count = retriever.add_document(
        content=code,
        metadata={"language": "python", "type": "code"},
        doc_id="code_doc_1",
        chunking_strategy="code",
    )
    
    assert chunks_count > 0


def test_semantic_retrieval(retriever):
    """Test semantic search retrieval."""
    # Add multiple documents
    docs = [
        {
            "content": "Python is great for machine learning and AI.",
            "metadata": {"topic": "python"},
            "id": "doc1",
        },
        {
            "content": "JavaScript is the language of the web.",
            "metadata": {"topic": "javascript"},
            "id": "doc2",
        },
        {
            "content": "Deep learning uses neural networks for AI.",
            "metadata": {"topic": "ai"},
            "id": "doc3",
        },
    ]
    
    retriever.add_documents_batch(docs)
    
    # Search for AI-related content
    results = retriever.retrieve(query="artificial intelligence", top_k=2)
    
    assert len(results) <= 2
    assert all(isinstance(r, RetrievalResult) for r in results)
    assert all(r.score > 0 for r in results)


def test_hybrid_retrieval(retriever):
    """Test hybrid search (semantic + keyword)."""
    # Add documents
    docs = [
        {
            "content": "Python programming language is versatile.",
            "metadata": {"lang": "python"},
            "id": "doc1",
        },
        {
            "content": "Machine learning with Python is powerful.",
            "metadata": {"lang": "python"},
            "id": "doc2",
        },
        {
            "content": "Web development using JavaScript frameworks.",
            "metadata": {"lang": "javascript"},
            "id": "doc3",
        },
    ]
    
    retriever.add_documents_batch(docs)
    
    # Hybrid search
    results = retriever.hybrid_retrieve(
        query="Python machine learning",
        top_k=2,
        semantic_weight=0.7,
    )
    
    assert len(results) <= 2
    assert all(isinstance(r, RetrievalResult) for r in results)


def test_metadata_filtering(retriever):
    """Test retrieval with metadata filters."""
    # Add documents with different metadata
    docs = [
        {
            "content": "Backend development with Python.",
            "metadata": {"category": "backend", "language": "python"},
            "id": "doc1",
        },
        {
            "content": "Frontend development with React.",
            "metadata": {"category": "frontend", "language": "javascript"},
            "id": "doc2",
        },
        {
            "content": "Backend APIs with Node.js.",
            "metadata": {"category": "backend", "language": "javascript"},
            "id": "doc3",
        },
    ]
    
    retriever.add_documents_batch(docs)
    
    # Filter for backend only
    results = retriever.retrieve(
        query="development",
        top_k=5,
        filter_metadata={"category": "backend"},
    )
    
    assert len(results) > 0
    assert all(r.metadata["category"] == "backend" for r in results)


def test_collection_reset(retriever):
    """Test collection reset."""
    # Add some documents
    retriever.add_document(
        content="Test content",
        metadata={"test": True},
        doc_id="test_doc",
    )
    
    initial_count = retriever.get_collection_stats()["document_count"]
    assert initial_count > 0
    
    # Reset collection
    retriever.reset_collection()
    
    # Check it's empty
    stats = retriever.get_collection_stats()
    assert stats["document_count"] == 0


def test_markdown_chunking(retriever):
    """Test markdown chunking strategy."""
    markdown = """
    # Introduction
    
    This is the introduction section.
    
    ## Background
    
    Some background information here.
    
    ## Methodology
    
    Details about the methodology.
    
    ### Data Collection
    
    How we collected the data.
    
    ### Analysis
    
    How we analyzed the data.
    
    ## Results
    
    The results of our study.
    """
    
    chunks_count = retriever.add_document(
        content=markdown,
        metadata={"type": "documentation"},
        doc_id="md_doc",
        chunking_strategy="markdown",
    )
    
    assert chunks_count > 0


def test_empty_query(retriever):
    """Test retrieval with empty query."""
    retriever.add_document(
        content="Some content",
        metadata={},
        doc_id="doc1",
    )
    
    results = retriever.retrieve(query="", top_k=5)
    
    # Should return empty or handle gracefully
    assert isinstance(results, list)
