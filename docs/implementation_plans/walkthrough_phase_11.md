# Walkthrough: Phase 11 - Bleeding Edge RAG 🩸

## Overview

We have successfully implemented the "Bleeding Edge" RAG roadmap (v4.0 features) as a non-breaking enhancement to the AI Code Orchestrator. This phase introduces state-of-the-art retrieval techniques to improve code understanding and context relevance.

## 🎯 Features Implemented

### 1. Re-ranking Module (`rag/reranker.py`)

- **What it does:** Uses a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to re-score the top 50 vector search results.
- **Benefit:** Drastically improves precision for complex queries by analyzing the full interaction between query and document.
- **Usage:**
  ```python
  results = vector_store.search(query="...", use_reranking=True)
  ```

### 2. Knowledge Graph (`core/graph/`)

- **What it does:** Builds a structural map of the codebase (Files, Classes, Functions, Imports).
- **Ingester:** Uses `ast` (Python) and `regex` (C#/TS) to parse code without heavy dependencies.
- **Retriever:** Fetches 1-hop neighbors (e.g., "What does this function call?", "Where is this class defined?").

### 3. Retrieval Agent (`core/agent/retrieval_agent.py`)

- **What it does:** Orchestrates the entire pipeline.
- **Workflow:**
  1.  **Search:** Hybrid Vector Search + Re-ranking.
  2.  **Identify:** Maps search results to Graph Nodes.
  3.  **Expand:** Pulls structural context from the Knowledge Graph.
  4.  **Synthesize:** Generates a context-rich report for the LLM.

## 🧪 Verification

We verified each component with dedicated scripts:

| Component        | Script                            | Result                                                         |
| :--------------- | :-------------------------------- | :------------------------------------------------------------- |
| **Re-ranking**   | `scripts/demo_reranking.py`       | ✅ Correctly re-ordered "distractor" docs vs. true code logic. |
| **Integration**  | `scripts/demo_rag_integration.py` | ✅ Verified end-to-end `VectorStore` integration.              |
| **Graph Ingest** | `scripts/demo_graph_ingest.py`    | ✅ Parsed Python code into Nodes (Class/Func) and Edges.       |
| **Graph RAG**    | `scripts/demo_graph_rag.py`       | ✅ Retrieved structural neighbors for a target function.       |
| **Agent**        | `scripts/demo_retrieval_agent.py` | ✅ Orchestrated Search -> Graph -> Report loop.                |

## 🚀 Next Steps

This framework is now ready for v4.0.

- **Backend:** Fully operational modules in `core/graph` and `rag/reranker.py`.
- **Frontend:** Visualization of the Knowledge Graph can be added to the Admin Panel in future sprints.
