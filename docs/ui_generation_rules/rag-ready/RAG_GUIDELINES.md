---
title: RAG Implementation Guidelines
type: meta
category: integration
version: 1.0.0
last_updated: 2026-02-13
---

# RAG Implementation Guidelines for DynUI Documentation

> **How to optimize DynUI docs for RAG systems and AI agents**

## 🎯 Overview

This documentation structure is **specifically designed for RAG (Retrieval-Augmented Generation)** systems and AI code generation agents.

### Key Characteristics

- **Factual Focus**: Only current, actionable information
- **No Historical Data**: No changelogs, audit trails, or version history
- **Structured Format**: Consistent markdown with YAML frontmatter
- **Token-First**: All values reference design tokens
- **Examples-Rich**: Real-world code samples
- **Cross-Referenced**: Clear document relationships

## 📚 Documentation Architecture

### Tier 1: Foundation Documents (High Priority)

**Index for every query:**

1. **00-INDEX.md** - Navigation hub
2. **01-QUICK_START.md** - Core concepts and patterns
3. **02-DESIGN_TOKENS.md** - Complete token reference

**Index for specific needs:**

4. **03-COMPONENT_CATALOG.md** - Component API reference
5. **04-STYLING_GUIDE.md** - Customization patterns
6. **05-CODE_EXAMPLES.md** - Implementation patterns

### Tier 2: Component-Specific Documents

**Location**: `components/[ComponentName].md`

**When to index**: When user asks about specific component

**Structure**:
```markdown
# DynButton

## Purpose
[One-sentence description]

## Props
[Complete prop table]

## Examples
[3-5 real examples]

## Styling
[Token overrides]
```

## 🔍 Indexing Strategy

### Recommended Approach: **Semantic Chunking**

#### Chunk Size
- **Optimal**: 500-1000 tokens per chunk
- **Max**: 1500 tokens
- **Min**: 200 tokens

#### Chunk Boundaries

**Split on:**
- `##` (h2) headers - Each major section
- `###` (h3) headers - For long sections
- Code blocks - Keep examples intact

**Never split:**
- Tables mid-row
- Code examples
- Lists
- Token definitions

#### Example Chunking Strategy

**02-DESIGN_TOKENS.md** could be chunked:

1. Chunk 1: Overview + 3-Layer Architecture (lines 1-80)
2. Chunk 2: Color Tokens - Primitives (lines 81-150)
3. Chunk 3: Color Tokens - Brand/Status (lines 151-250)
4. Chunk 4: Spacing Tokens (lines 251-300)
5. Chunk 5: Typography Tokens (lines 301-350)
6. Etc.

### Metadata for Each Chunk

```json
{
  "document_id": "02-DESIGN_TOKENS",
  "chunk_id": "02-DESIGN_TOKENS-chunk-002",
  "section": "Color Tokens - Brand",
  "category": "foundation",
  "type": "reference",
  "keywords": ["color", "primary", "success", "brand", "tokens"],
  "related_docs": ["01-QUICK_START", "04-STYLING_GUIDE"],
  "priority": "high"
}
```

## 🎯 Query Routing Strategy

### Query Type Detection

| User Query Pattern | Index These Docs | Example |
|-------------------|------------------|----------|
| "How to [X]" | 01, 05 | "How to create a form" |
| "What is [X]" | 01, 03 | "What is DynBox" |
| "[Component] props" | 03, components/[X] | "DynButton props" |
| "Style/customize [X]" | 02, 04 | "Customize button color" |
| "Example of [X]" | 05, components/[X] | "Example of modal" |
| "Token for [X]" | 02 | "Token for spacing" |
| "All components" | 03 | "List all components" |

### Multi-Doc Queries

**Query**: "Create a login form with primary button"

**Retrieve**:
1. 01-QUICK_START.md (Pattern: Simple Form)
2. 05-CODE_EXAMPLES.md (Example 1: Login Form)
3. 03-COMPONENT_CATALOG.md (DynButton, DynInput, DynFieldContainer)

**Query**: "What color token for primary button"

**Retrieve**:
1. 02-DESIGN_TOKENS.md (Color Tokens - Brand)
2. 04-STYLING_GUIDE.md (Token-First Approach)

## 🔑 Critical Extraction Rules

### For Code Generation

**ALWAYS extract:**

1. **Import statements** from examples
2. **Token references** (all `--dyn-*` variables)
3. **Prop patterns** (size, color, variant)
4. **Default values** from Quick Start
5. **3-level fallback** pattern from tokens

**NEVER generate:**

1. Hardcoded colors (`#2563eb` → use `var(--dyn-color-primary)`)
2. Hardcoded spacing (`16px` → use `var(--dyn-spacing-md)`)
3. Hardcoded sizes (`40px` → use `var(--dyn-size-height-md)`)

### For Question Answering

**Priority order:**

1. Code examples (05-CODE_EXAMPLES.md)
2. Quick patterns (01-QUICK_START.md)
3. API reference (03-COMPONENT_CATALOG.md)
4. Token definitions (02-DESIGN_TOKENS.md)
5. Styling techniques (04-STYLING_GUIDE.md)

## 📊 Embedding Strategy

### Model Recommendations

**Option 1: OpenAI** `text-embedding-3-large`
- Dimension: 3072 (or 1536 for cost savings)
- Best for: General code understanding

**Option 2: Cohere** `embed-multilingual-v3.0`
- Dimension: 1024
- Best for: Multi-language support (English/Serbian)

**Option 3: Local** `sentence-transformers/all-mpnet-base-v2`
- Dimension: 768
- Best for: Privacy-sensitive deployments

### Embedding Optimization

**Prefix technique**:
```
passage: [chunk content]
query: [user question]
```

**Metadata enrichment**:
- Add document title to chunk
- Add section path (e.g., "Design Tokens > Color Tokens > Brand")
- Add component name if applicable

## 🔍 Search Strategy

### Hybrid Search (Recommended)

**Combine:**
1. **Semantic search** (70% weight) - Embedding similarity
2. **Keyword search** (20% weight) - BM25 on token names
3. **Metadata filtering** (10% weight) - Document type, category

### Re-ranking

After initial retrieval, re-rank by:

1. **Document priority** (Foundation docs > Component docs)
2. **Recency** of examples (prefer pattern matches)
3. **Code presence** (chunks with code examples rank higher)

## 🛠️ Implementation Guide

### Vector Database Setup

#### Pinecone Example

```python
import pinecone
from openai import OpenAI

# Initialize
pinecone.init(api_key="...", environment="...")
index = pinecone.Index("dynui-docs")
openai_client = OpenAI()

# Index document
def index_document(doc_id, content, metadata):
    # Create embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=f"passage: {content}"
    )
    embedding = response.data[0].embedding
    
    # Upsert to Pinecone
    index.upsert([
        {
            "id": doc_id,
            "values": embedding,
            "metadata": metadata
        }
    ])

# Query
def search_docs(query, top_k=5):
    # Create query embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=f"query: {query}"
    )
    query_embedding = response.data[0].embedding
    
    # Search
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    return results.matches
```

### Prompt Engineering

**System prompt template**:

```
You are a DynUI code generation expert. Use ONLY information from the provided documentation.

RULES:
1. NEVER hardcode colors, spacing, or sizes
2. ALWAYS use design tokens: var(--dyn-*)
3. Follow 3-level fallback pattern for component tokens
4. Import components from '@dyn-ui/react'
5. Default sizes: md (medium)
6. Default spacing: sm (8px)
7. Form components: 100% width by default

Documentation context:
{retrieved_docs}

User query: {user_query}
```

## ⚡ Performance Optimization

### Caching Strategy

**Cache these permanently** (rarely change):
- 02-DESIGN_TOKENS.md (all chunks)
- 01-QUICK_START.md (core patterns)
- Common component queries (DynButton, DynInput, DynBox)

**Cache with TTL** (1 hour):
- Recent user queries
- Component combinations

### Query Optimization

**Fast path queries** (no RAG needed):
- "Import DynButton" → Direct: `import { DynButton } from '@dyn-ui/react'`
- "Primary color token" → Direct: `--dyn-color-primary`
- "Default spacing" → Direct: `--dyn-spacing-sm` (8px)

## 📝 Quality Metrics

### Track These

1. **Retrieval accuracy**: % of queries returning relevant docs
2. **Token usage**: % of generated code using tokens vs hardcoded
3. **Pattern matching**: % following documented patterns
4. **Import correctness**: % of valid imports
5. **Compilation rate**: % of generated code that compiles

### Success Criteria

- ✅ **>95%** retrieval accuracy
- ✅ **100%** token usage (no hardcoded values)
- ✅ **>90%** pattern matching
- ✅ **100%** import correctness
- ✅ **>98%** compilation rate

## 🔗 Integration Checklist

- [ ] Vector database configured
- [ ] All docs indexed with metadata
- [ ] Semantic chunking implemented
- [ ] Hybrid search enabled
- [ ] Re-ranking configured
- [ ] Prompt template validated
- [ ] Caching strategy deployed
- [ ] Quality metrics tracking
- [ ] Token validation in post-processing

## 💡 Tips for Best Results

1. **Always start with 01-QUICK_START.md** for context
2. **Prefer 05-CODE_EXAMPLES.md** for patterns over synthesizing new ones
3. **Check 02-DESIGN_TOKENS.md** for every color/spacing/size
4. **Validate generated code** against token usage rules
5. **Use component-specific docs** for detailed prop info

---

**This documentation is RAG-ready. Follow these guidelines for optimal results.**
