# Advanced RAG (Retrieval-Augmented Generation)

Enhanced RAG system with vector database integration for semantic code and documentation search.

## Overview

The Advanced RAG feature provides intelligent knowledge retrieval to enrich LLM context with relevant code, documentation, and domain knowledge. It uses:

- **ChromaDB** - Persistent vector database
- **Sentence Transformers** - State-of-the-art embeddings
- **Strategic Auto-Chunking (Phase 10)** - Logic-aware document splitting (Functions/Classes)
- **Optimization Advisor** - Proactive token-saving recommendations
- **Re-ranking (Phase 11)** - Cross-Encoder refinement for high precision
- **Document Management** - Fine-grained retrieval and deletion
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
│ Re-ranker       │ ← Cross-Encoder (Optional)
│ (Phase 11)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context         │
│ Manager         │ ← Enriched context for LLM
└─────────────────┘
```

## Components

### 1. Chunking Engine (`core/chunking/engine.py`) [NEW in v3.0 Phase 10]

The enterprise-grade replacement for legacy chunkers. It provides strategic, logic-aware splitting.

**Code Strategy (`CodeChunker`):**

- **Logic-Aware**: Identifies function and class boundaries using regex patterns.
- **Self-Contained**: Ensures chunks are logically meaningful, reducing hallucination.
- **Multi-Language**: Supports Python, C#, TypeScript, JavaScript, and more.

**Text Strategy (`TextChunker`):**

- **Recursive Splitting**: Smart paragraph and sentence-level splitting.
- **Configurable**: Fine-tuned control over `chunk_size` and `overlap`.

**Optimization Advisor:**
Built-in logic to analyze content and suggest optimal parameters:

- Detects generated files (e.g., `.g.cs`) and suggests exclusion.
- Recommends size-specific chunking strategies.

**Usage:**

```python
from core.chunking.engine import ChunkingEngine

engine = ChunkingEngine()
chunks = engine.chunk_content(
    content=code_content,
    file_path="src/service.cs",
    chunk_size=1000,
    overlap=120
)

# Get proactive advice
recommendations = engine.get_recommendations(code_content, "src/service.cs")
for rec in recommendations:
    print(f"Advice: {rec}")
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

### 3. Re-ranking Module (`rag/reranker.py`) [NEW in v4.0 Phase 11]

Implements a second-stage retrieval process using Cross-Encoders to improve precision.

**Why Re-ranking?**
Standard vector search (Cosine Similarity) finds "semantically similar" text, but often misses subtle nuances. Cross-Encoders compare the query and document _together_, achieving much higher accuracy at the cost of speed.

**Usage:**

```python
# Enable re-ranking in search
results = store.search(
    query="How to handle auth errors?",
    top_k=5,
    use_reranking=True  # Automatically triggers Cross-Encoder
)
```

**Best Practices:**

- Use for complex "How-to" queries.
- Keep `top_k` small (5-10) to minimize latency.
- Do NOT use for simple ID or filename lookups.

### 4. RAG Management API [NEW Phase 10 Extension]

Exposes fine-grained control over the vector store.

**Endpoints:**

- `GET /admin/collections/{name}/documents`: Browse documents with pagination.
- `DELETE /admin/collections/{name}/documents/{doc_id}`: Remove specific stale or invalid chunks.

### 5. Agentic Retrieval ("Deep Search") [NEW in Phase 15]

Moving beyond static vector search, v4.0 introduces the **Retrieval Agent**.

**Concept:**
Instead of a single query, the agent performs a simplified ReAct loop:

1.  **Thought:** "I need to find the `AuthMiddleware` class."
2.  **Action:** `search_code("class AuthMiddleware")`
3.  **Observation:** Found in `src/middleware/auth.ts`.
4.  **Thought:** "Now I need to see how it handles tokens."
5.  **Action:** `read_file("src/middleware/auth.ts")`

**Components:**

- `RetrievalAgent` (`agents/specialist_agents/retrieval_agent.py`)
- Tools: `search_code`, `read_file`, `list_dir`

### 6. Experience Retrieval (Self-Correction) [NEW in Phase 17]

The system now indexes its own execution history.

**Mechanism:**

- **Source:** `experience.db` (SQLite) containing `(error_embedding, fix_strategy)`.
- **Query:** When an error occurs, the `RepairAgent` embeds the error traceback.
- **Retrieval:** Finds the top-k most similar past errors and retrieves their successful fixes.

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

... (Rest of the guide remains similar)
