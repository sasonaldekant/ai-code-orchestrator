# Advanced RAG (Retrieval-Augmented Generation)

Enhanced RAG system with vector database integration for semantic code and documentation search.

## Overview

The Advanced RAG feature provides intelligent knowledge retrieval to enrich LLM context with relevant code, documentation, and domain knowledge. It uses:

- **ChromaDB** - Persistent vector database
- **Sentence Transformers** - State-of-the-art embeddings
- **Smart Chunking** - Context-aware document splitting
- **Hybrid Search** - Combines semantic + keyword matching

## Architecture

```
┌─────────────────┐
│  Documents      │
│  (code, docs)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document        │
│ Chunker         │ ← Smart splitting (code/markdown/text)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ChromaDB        │
│ Vector Store    │ ← Sentence-Transformers embeddings
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hybrid Search   │ ← Semantic + Keyword fusion
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context         │
│ Manager         │ ← Enriched context for LLM
└─────────────────┘
```

## Components

### 1. Document Chunker (`utils/document_chunker.py`)

Smart chunking with multiple strategies:

**Code Strategy:**
- Preserves function/class boundaries
- Respects syntactic structure
- Falls back to sliding window for large blocks

**Markdown Strategy:**
- Preserves section structure
- Keeps headers with content
- Maintains hierarchical context

**Text Strategy:**
- Sentence-aware splitting
- Configurable overlap
- Token-based sizing

**Usage:**
```python
from utils.document_chunker import DocumentChunker

chunker = DocumentChunker(
    chunk_size=512,      # tokens
    chunk_overlap=50,    # tokens
)

chunks = chunker.chunk_document(
    content=code_content,
    metadata={"source": "main.py", "language": "python"},
    strategy="code",
)
```

### 2. Enhanced RAG Retriever (`core/retriever_v2.py`)

Vector database-backed retrieval with ChromaDB:

**Features:**
- Semantic search using sentence transformers
- Keyword-based exact matching
- Hybrid search with configurable weights
- Metadata filtering
- Reciprocal rank fusion for result combination

**Usage:**
```python
from core.retriever_v2 import EnhancedRAGRetriever

retriever = EnhancedRAGRetriever(
    collection_name="code_docs",
    persist_directory="./chroma_db",
    embedding_model="all-MiniLM-L6-v2",
)

# Add documents
retriever.add_document(
    content=document_text,
    metadata={"source": "docs.md", "topic": "api"},
    doc_id="doc_001",
    chunking_strategy="markdown",
)

# Semantic search
results = retriever.retrieve(
    query="How to implement authentication?",
    top_k=5,
)

# Hybrid search (recommended)
results = retriever.hybrid_retrieve(
    query="authentication implementation",
    top_k=5,
    semantic_weight=0.7,  # 70% semantic, 30% keyword
)

# With metadata filtering
results = retriever.retrieve(
    query="database migrations",
    top_k=3,
    filter_metadata={"topic": "database"},
)
```

### 3. Enhanced Context Manager (`core/context_manager_v2.py`)

Combines static configuration with dynamic RAG retrieval:

**Features:**
- Automatic knowledge retrieval based on query
- Static schema/rules loading
- Context formatting for LLM prompts
- RAG statistics tracking

**Usage:**
```python
from core.context_manager_v2 import EnhancedContextManager
from pathlib import Path

context_mgr = EnhancedContextManager(
    enable_rag=True,
)

# Build enriched context
context = context_mgr.build_context(
    phase="implementation",
    specialty="backend",
    schema_path=Path("schemas/api_schema.json"),
    rules_path=Path("config/backend_rules.yaml"),
    user_query="Create REST API for user management",
    top_k_docs=3,
)

# Format for LLM prompt
prompt_context = context.to_prompt_context(max_docs=3)

# Add domain knowledge
context_mgr.add_domain_knowledge(
    content=api_documentation,
    metadata={"type": "api_docs", "version": "v1"},
    doc_id="api_v1_docs",
)
```

### 4. Build RAG Index Script (`scripts/build_rag_index.py`)

CLI tool for populating the vector database:

**Features:**
- Index from files, directories, or JSON
- Auto-detect chunking strategy from file type
- Pattern-based file filtering
- Collection management (reset, stats)

**Usage:**

```bash
# Index a single file
python scripts/build_rag_index.py --file path/to/document.md

# Index entire directory
python scripts/build_rag_index.py --directory ./codebase \
    --pattern "**/*.py" \
    --exclude "tests" "__pycache__"

# Index from JSON
python scripts/build_rag_index.py --json documents.json

# Reset and rebuild
python scripts/build_rag_index.py --directory ./docs --reset

# Show statistics
python scripts/build_rag_index.py --stats

# Custom configuration
python scripts/build_rag_index.py \
    --directory ./src \
    --collection "my_project" \
    --persist-dir "./vector_db" \
    --chunk-size 1024 \
    --chunk-overlap 100 \
    --verbose
```

## Installation

### Dependencies

Added to `pyproject.toml`:

```toml
dependencies = [
  # ... existing dependencies ...
  "chromadb>=0.4.22",
  "sentence-transformers>=2.3.0",
  "tiktoken>=0.5.2",
]
```

Install:

```bash
pip install -e .
```

### First-time Setup

```bash
# Download sentence transformer model (happens automatically on first use)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## Quick Start

### 1. Index Your Codebase

```bash
# Index all Python files
python scripts/build_rag_index.py \
    --directory ./my_project \
    --pattern "**/*.py" \
    --collection "my_project_code"

# Index documentation
python scripts/build_rag_index.py \
    --directory ./docs \
    --pattern "**/*.md" \
    --collection "my_project_docs"
```

### 2. Use in Your Pipeline

```python
from core.context_manager_v2 import EnhancedContextManager
from core.retriever_v2 import EnhancedRAGRetriever

# Initialize
retriever = EnhancedRAGRetriever(
    collection_name="my_project_code",
)

context_mgr = EnhancedContextManager(
    retriever=retriever,
    enable_rag=True,
)

# Get enriched context
context = context_mgr.build_context(
    phase="implementation",
    user_query="Add caching to the API endpoint",
    top_k_docs=5,
)

# Use in LLM prompt
from core.llm_client_v2 import EnhancedLLMClient

client = EnhancedLLMClient()
response = client.complete(
    prompt=f"""
    {context.to_prompt_context()}
    
    Task: {user_query}
    
    Generate implementation following the retrieved patterns and rules.
    """,
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
)
```

## Performance

### Chunking Strategies Performance

| Strategy | Speed | Context Quality | Best For |
|----------|-------|-----------------|----------|
| **Text** | Fast | Good | Documentation, READMEs |
| **Markdown** | Medium | Excellent | Structured docs |
| **Code** | Medium | Excellent | Source code |

### Embedding Model Options

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|--------|
| `all-MiniLM-L6-v2` | 384 | Fast | Good |
| `all-mpnet-base-v2` | 768 | Medium | Better |
| `instructor-large` | 768 | Slow | Best |

Default: `all-MiniLM-L6-v2` (good balance)

### Search Strategy Comparison

**Semantic Only:**
- Best for: Conceptual queries
- Example: "How to handle authentication?"

**Keyword Only:**
- Best for: Exact matches
- Example: "UserController.login method"

**Hybrid (Recommended):**
- Best for: General queries
- Combines strengths of both
- Configurable weight (default: 70% semantic, 30% keyword)

## Configuration

### Chunking Parameters

```python
chunker = DocumentChunker(
    chunk_size=512,        # Target tokens per chunk
    chunk_overlap=50,      # Overlap between chunks
    encoding_name="cl100k_base",  # Tiktoken encoding
)
```

**Guidelines:**
- **Small chunks (256-512)**: Better precision, more chunks
- **Large chunks (1024-2048)**: More context, fewer chunks
- **Overlap (10-20%)**: Prevents context loss at boundaries

### Retrieval Parameters

```python
results = retriever.hybrid_retrieve(
    query="user query",
    top_k=5,                  # Number of results
    semantic_weight=0.7,       # Semantic vs keyword balance
    filter_metadata={...},     # Optional filters
)
```

**Guidelines:**
- **top_k**: 3-5 for focused context, 10-15 for comprehensive
- **semantic_weight**: 0.7-0.8 for general queries, 0.5-0.6 for code search

## Testing

Run tests:

```bash
# All RAG tests
pytest tests/test_retriever_v2.py -v

# Specific test
pytest tests/test_retriever_v2.py::test_hybrid_retrieval -v

# With coverage
pytest tests/test_retriever_v2.py --cov=core.retriever_v2 --cov-report=html
```

## Examples

### Example 1: Index Project Documentation

```python
from core.retriever_v2 import EnhancedRAGRetriever
from pathlib import Path

retriever = EnhancedRAGRetriever()

# Index all markdown files
for md_file in Path("docs").glob("**/*.md"):
    content = md_file.read_text()
    retriever.add_document(
        content=content,
        metadata={
            "source": str(md_file),
            "type": "documentation",
        },
        doc_id=str(md_file),
        chunking_strategy="markdown",
    )

print(retriever.get_collection_stats())
```

### Example 2: Code Search with Filtering

```python
# Search for authentication code in backend
results = retriever.hybrid_retrieve(
    query="JWT token authentication implementation",
    top_k=5,
    filter_metadata={
        "category": "backend",
        "language": "python",
    },
)

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Source: {result.metadata['source']}")
    print(f"Content: {result.content[:200]}...")
    print("-" * 50)
```

### Example 3: Batch Indexing from JSON

```json
// documents.json
[
  {
    "content": "API endpoint documentation...",
    "metadata": {
      "type": "api",
      "version": "v1",
      "category": "backend"
    },
    "id": "api_v1_users"
  },
  {
    "content": "Database schema description...",
    "metadata": {
      "type": "schema",
      "database": "postgresql"
    },
    "id": "schema_users"
  }
]
```

```python
import json

with open("documents.json") as f:
    documents = json.load(f)

retriever.add_documents_batch(documents, chunking_strategy="text")
```

## Troubleshooting

### Issue: ChromaDB persistence errors

**Solution:** Ensure directory permissions:
```bash
chmod 755 ./chroma_db
```

### Issue: Out of memory with large files

**Solution:** Reduce chunk size:
```python
retriever = EnhancedRAGRetriever(
    chunk_size=256,  # Smaller chunks
    chunk_overlap=25,
)
```

### Issue: Slow retrieval

**Solution:** Use smaller embedding model or limit top_k:
```python
retriever = EnhancedRAGRetriever(
    embedding_model="all-MiniLM-L6-v2",  # Fastest
)

results = retriever.retrieve(query, top_k=3)  # Fewer results
```

### Issue: Poor retrieval quality

**Solutions:**
1. Use hybrid search instead of semantic-only
2. Increase semantic_weight for conceptual queries
3. Add more specific metadata for filtering
4. Use better embedding model (all-mpnet-base-v2)

## Migration from v1

Old retriever (`core/retriever.py`):
```python
from core.retriever import RAGRetriever

retriever = RAGRetriever(index_dir="rag/domain_indices")
results = retriever.retrieve(query, top_k=3)
```

New retriever (`core/retriever_v2.py`):
```python
from core.retriever_v2 import EnhancedRAGRetriever

retriever = EnhancedRAGRetriever(
    collection_name="code_docs",
    persist_directory="./chroma_db",
)
results = retriever.hybrid_retrieve(query, top_k=3)
```

**Key Differences:**
- Vector database instead of JSON files
- Semantic search instead of keyword-only
- Hybrid search capability
- Metadata filtering
- Better chunking strategies

## Future Enhancements

- [ ] Multi-modal embeddings (code + docs)
- [ ] Query expansion and reformulation
- [ ] Relevance feedback loop
- [ ] Distributed vector database (Qdrant/Weaviate)
- [ ] Custom fine-tuned embeddings
- [ ] Automatic index updates on file changes
- [ ] Graph-based knowledge retrieval

## Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Tiktoken](https://github.com/openai/tiktoken)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
