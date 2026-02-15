---
title: RAG-Ready Documentation
version: 1.0.0
last_updated: 2026-02-13
status: Production Ready
---

# DynUI RAG-Ready Documentation

> **Optimized documentation for AI agents, code generators, and RAG systems**

## 🎯 Purpose

This folder contains **production-ready documentation** specifically designed for:

- 🤖 **AI Code Generation Agents**
- 🔍 **RAG (Retrieval-Augmented Generation) Systems**
- ⚡ **LLM-Powered Development Tools**
- 📚 **Vector Database Indexing**

### What Makes This "RAG-Ready"?

✅ **Factual Only** - No historical data, no changelogs
✅ **Token-First** - All values reference design tokens
✅ **Structured** - Consistent markdown + YAML frontmatter
✅ **Example-Rich** - Real-world code patterns
✅ **Cross-Referenced** - Clear document relationships
✅ **Chunking-Friendly** - Optimized for semantic splitting

## 📚 Quick Start

### For AI Agents

**Start here**: [00-INDEX.md](00-INDEX.md)

**Then read**:
1. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cheat sheet
2. [01-QUICK_START.md](01-QUICK_START.md) - Core concepts
3. [02-DESIGN_TOKENS.md](02-DESIGN_TOKENS.md) - Token reference
4. [05-CODE_EXAMPLES.md](05-CODE_EXAMPLES.md) - Patterns

### For RAG Implementers

**Start here**: [RAG_GUIDELINES.md](RAG_GUIDELINES.md)

**Then check**:
- [METADATA.json](METADATA.json) - Document metadata
- Indexing strategy recommendations
- Query routing patterns
- Embedding optimization tips

## 📝 Document Structure

### Foundation Documents (Tier 1)

| File | Purpose | Priority | Tokens | Index When |
|------|---------|----------|--------|------------|
| **[00-INDEX.md](00-INDEX.md)** | Navigation hub | Critical | ~800 | Always |
| **[01-QUICK_START.md](01-QUICK_START.md)** | Core concepts | High | ~3200 | Always |
| **[02-DESIGN_TOKENS.md](02-DESIGN_TOKENS.md)** | Token reference | High | ~5500 | Always |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Cheat sheet | High | ~800 | Quick queries |

### Reference Documents (Tier 1)

| File | Purpose | Priority | Tokens | Index When |
|------|---------|----------|--------|------------|
| **[03-COMPONENT_CATALOG.md](03-COMPONENT_CATALOG.md)** | All components | High | ~4000 | Component queries |
| **[04-STYLING_GUIDE.md](04-STYLING_GUIDE.md)** | Styling patterns | Medium | ~2800 | Style/theme queries |
| **[05-CODE_EXAMPLES.md](05-CODE_EXAMPLES.md)** | Implementation | High | ~3500 | Pattern queries |

### Meta Documents

| File | Purpose | Audience |
|------|---------|----------|
| **[RAG_GUIDELINES.md](RAG_GUIDELINES.md)** | Implementation guide | RAG implementers |
| **[METADATA.json](METADATA.json)** | Document metadata | Vector databases |
| **[README.md](README.md)** | This file | Everyone |

## 🛠️ Implementation Guide

### Step 1: Index Documents

```python
# Recommended chunking
chunk_size = 800  # tokens
strategy = "semantic"  # Split on h2/h3 headers

# Priority order
priority_docs = [
    "00-INDEX.md",
    "01-QUICK_START.md",
    "02-DESIGN_TOKENS.md",
    "QUICK_REFERENCE.md"
]
```

### Step 2: Configure Embeddings

```python
# Recommended models
model = "text-embedding-3-large"  # OpenAI
# OR
model = "embed-multilingual-v3.0"  # Cohere
# OR
model = "all-mpnet-base-v2"  # Local

dimensions = 1536  # Optimal balance
```

### Step 3: Set Up Query Routing

```python
query_patterns = {
    "how_to": ["01-QUICK_START", "05-CODE_EXAMPLES"],
    "what_is": ["01-QUICK_START", "03-COMPONENT_CATALOG"],
    "token_for": ["02-DESIGN_TOKENS"],
    "style": ["04-STYLING_GUIDE", "02-DESIGN_TOKENS"],
    "example": ["05-CODE_EXAMPLES"]
}
```

### Step 4: Add Quality Rules

```python
validation_rules = [
    "No hardcoded colors",
    "No hardcoded spacing",
    "Always use var(--dyn-*) tokens",
    "Import from '@dyn-ui/react'",
    "Default size: md",
    "Default spacing: sm"
]
```

## 📊 Statistics

```json
{
  "total_documents": 8,
  "total_tokens": "~23,000",
  "components_documented": 45,
  "code_examples": 35,
  "design_tokens": 85,
  "indexing_time": "< 5 minutes",
  "avg_query_time": "< 200ms"
}
```

## ⚡ Performance Tips

### 1. Cache Common Queries

```python
cache_forever = [
    "02-DESIGN_TOKENS.md",  # Rarely changes
    "QUICK_REFERENCE.md"     # Static reference
]

cache_1hour = [
    "Recent component queries",
    "User-specific patterns"
]
```

### 2. Fast-Path Queries

Some queries don't need RAG:

```python
fast_paths = {
    "import DynButton": "import { DynButton } from '@dyn-ui/react'",
    "primary color": "--dyn-color-primary",
    "default spacing": "--dyn-spacing-sm (8px)"
}
```

### 3. Hybrid Search

```python
scores = {
    "semantic_similarity": 0.70,
    "keyword_match": 0.20,
    "metadata_filter": 0.10
}
```

## 🎯 Quality Metrics

### Target KPIs

- ✅ **Retrieval Accuracy**: >95%
- ✅ **Token Usage**: 100% (no hardcoded values)
- ✅ **Pattern Matching**: >90%
- ✅ **Compilation Rate**: >98%
- ✅ **Import Correctness**: 100%

### How to Measure

```python
# Sample validation
def validate_generated_code(code: str) -> dict:
    checks = {
        "has_imports": "from '@dyn-ui/react'" in code,
        "uses_tokens": "var(--dyn-" in code,
        "no_hardcoded": not re.search(r'#[0-9a-f]{6}', code),
        "proper_sizes": any(s in code for s in ['sm', 'md', 'lg'])
    }
    return checks
```

## 📖 Example Queries

### Query 1: "Create a login form"

**Retrieved docs**:
- 05-CODE_EXAMPLES.md (Example 1: Login Form)
- 01-QUICK_START.md (Pattern 1: Simple Form)
- 03-COMPONENT_CATALOG.md (DynInput, DynButton, DynFieldContainer)

**Generated code**:
```tsx
import { DynBox, DynInput, DynButton, DynFieldContainer } from '@dyn-ui/react';

function LoginForm() {
  return (
    <DynBox gap="md" direction="vertical">
      <DynFieldContainer label="Email" required>
        <DynInput type="email" size="md" />
      </DynFieldContainer>
      <DynButton color="primary" size="md" type="submit">
        Sign In
      </DynButton>
    </DynBox>
  );
}
```

### Query 2: "What token for button background?"

**Retrieved docs**:
- 02-DESIGN_TOKENS.md (Color Tokens - Brand)
- 04-STYLING_GUIDE.md (Method 1: CSS Variables)

**Answer**:
```
Use: --dyn-color-primary for primary buttons
Value: #2563eb (light mode), #3b82f6 (dark mode)

Implementation:
style={{ backgroundColor: 'var(--dyn-color-primary)' }}
```

### Query 3: "How to make card with shadow?"

**Retrieved docs**:
- 04-STYLING_GUIDE.md (Pattern 1: Card with Shadow)
- 01-QUICK_START.md (Pattern 2: Card Layout)

**Generated code**:
```tsx
<DynBox
  padding="md"
  style={{
    backgroundColor: 'var(--dyn-color-surface)',
    borderRadius: 'var(--dyn-border-radius-md)',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid var(--dyn-color-border)'
  }}
>
  Card content
</DynBox>
```

## 🔗 Integration Examples

### Pinecone

```python
import pinecone
from openai import OpenAI

pinecone.init(api_key="...", environment="...")
index = pinecone.Index("dynui-docs")

# Index document
def index_doc(content, metadata):
    embedding = OpenAI().embeddings.create(
        model="text-embedding-3-large",
        input=f"passage: {content}"
    ).data[0].embedding
    
    index.upsert([{
        "id": metadata["id"],
        "values": embedding,
        "metadata": metadata
    }])
```

### Weaviate

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Create schema
client.schema.create({
    "class": "DynUIDoc",
    "vectorizer": "text2vec-openai",
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "title", "dataType": ["string"]},
        {"name": "category", "dataType": ["string"]},
        {"name": "priority", "dataType": ["string"]}
    ]
})
```

### Chroma

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection(
    name="dynui_docs",
    metadata={"description": "DynUI RAG-ready documentation"}
)

# Add documents
collection.add(
    documents=[doc_content],
    metadatas=[doc_metadata],
    ids=[doc_id]
)
```

## ❓ FAQ

**Q: Why separate from main docs?**
A: RAG needs focused, factual content. Main docs include historical context, migration guides, and development notes that confuse AI agents.

**Q: How often to re-index?**
A: Foundation docs (tokens, patterns) rarely change. Re-index when components are added/modified (~monthly).

**Q: What embedding model?**
A: OpenAI `text-embedding-3-large` (best), Cohere `embed-multilingual-v3.0` (multi-lang), or local `all-mpnet-base-v2` (privacy).

**Q: Chunking strategy?**
A: Semantic chunking on h2/h3 headers. Target 800 tokens/chunk. Never split code examples.

**Q: How to validate generated code?**
A: Check for token usage (no hardcoded values), correct imports, proper prop patterns, compilable syntax.

## 📦 Package Contents

```
rag-ready/
├── 00-INDEX.md                 # Master navigation
├── 01-QUICK_START.md           # Getting started guide
├── 02-DESIGN_TOKENS.md         # Complete token reference
├── 03-COMPONENT_CATALOG.md    # All 45 components
├── 04-STYLING_GUIDE.md         # Customization patterns
├── 05-CODE_EXAMPLES.md         # Real-world patterns
├── QUICK_REFERENCE.md          # One-page cheat sheet
├── RAG_GUIDELINES.md           # Implementation guide
├── METADATA.json               # Document metadata
└── README.md                   # This file
```

## 🚀 Next Steps

1. **Read**: [RAG_GUIDELINES.md](RAG_GUIDELINES.md) for detailed implementation
2. **Check**: [METADATA.json](METADATA.json) for document structure
3. **Start**: Index foundation docs first
4. **Test**: Validate with sample queries
5. **Monitor**: Track quality metrics

---

**Ready to build?** Start with [00-INDEX.md](00-INDEX.md)

**Need help?** Check [RAG_GUIDELINES.md](RAG_GUIDELINES.md)

**Version**: 1.0.0 | **Status**: Production Ready | **Updated**: 2026-02-13
